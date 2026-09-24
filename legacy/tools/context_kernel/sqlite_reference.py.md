# [SEALED] tools/context_kernel/sqlite_reference.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/context_kernel/sqlite_reference.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
"""Restart-capable K2 conformance adapter, NOT a production storage selection.

All heads are quarantined reference namespaces. SQLite serializes writers with
BEGIN IMMEDIATE; objects, result, receipt and head CAS share one transaction.
Persistent reservations bind keys before execution. No network/Host/Git writes.
"""
from contextlib import contextmanager
from hashlib import sha256
import sqlite3
from .model import KernelObject


class SQLiteReference:
    def __init__(self, path, timeout=5.0):
        self.path = str(path)
        self.timeout = timeout
        if self.path == ':memory:':
            raise ValueError('restart reference requires an explicit file')
        with self.connect() as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript('''
                CREATE TABLE IF NOT EXISTS objects(digest TEXT PRIMARY KEY, encoded BLOB NOT NULL);
                CREATE TABLE IF NOT EXISTS blobs(digest TEXT PRIMARY KEY, body BLOB NOT NULL);
                CREATE TABLE IF NOT EXISTS projects(project TEXT PRIMARY KEY, head TEXT NOT NULL,
                    mode TEXT NOT NULL CHECK(mode='quarantined'));
                CREATE TABLE IF NOT EXISTS write_blocks(project TEXT PRIMARY KEY, reason TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS attempts(
                    project TEXT NOT NULL, principal TEXT NOT NULL, key TEXT NOT NULL,
                    request TEXT NOT NULL, transaction_id TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('pending','committed','not_committed')),
                    receipt TEXT, reason TEXT NOT NULL,
                    PRIMARY KEY(project, principal, key), UNIQUE(project, transaction_id));
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=self.timeout, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA synchronous=FULL')
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def get(db, digest):
        row = db.execute('SELECT encoded FROM objects WHERE digest=?', (digest,)).fetchone()
        if row is None:
            raise KeyError(digest)
        result = KernelObject(bytes(row['encoded']))
        if result.digest != digest:
            raise ValueError('stored object integrity failure')
        return result

    @staticmethod
    def put(db, value):
        row = db.execute('SELECT encoded FROM objects WHERE digest=?', (value.digest,)).fetchone()
        if row is not None and bytes(row['encoded']) != value.encoded:
            raise ValueError('immutable object collision')
        db.execute('INSERT OR IGNORE INTO objects VALUES (?,?)', (value.digest, value.encoded))

    @staticmethod
    def blob(db, digest):
        row = db.execute('SELECT body FROM blobs WHERE digest=?', (digest,)).fetchone()
        if row is None:
            raise KeyError(digest)
        raw = bytes(row['body'])
        if 'sha256:' + sha256(raw).hexdigest() != digest:
            raise ValueError('stored raw evidence integrity failure')
        return raw

    @staticmethod
    def put_blob(db, digest, raw):
        if 'sha256:' + sha256(raw).hexdigest() != digest:
            raise ValueError('raw evidence digest mismatch')
        db.execute('INSERT OR IGNORE INTO blobs VALUES (?,?)', (digest, raw))
        if SQLiteReference.blob(db, digest) != raw:
            raise ValueError('immutable raw evidence collision')

    def head(self, db, project):
        row = db.execute('SELECT head,mode FROM projects WHERE project=?', (project,)).fetchone()
        if row is None or row['mode'] != 'quarantined':
            raise ValueError('missing quarantined reference project')
        return row['head']

    def bootstrap_quarantine(self, imported, policy):
        """Explicit fixture initialization. Never translates Git governance grants."""
        imported.verify()
        origin = imported.snapshot.payload
        governance = KernelObject.create('ReferenceGovernance', policy)
        if policy['project_id'] != origin['project_id']:
            raise ValueError('bootstrap project mismatch')
        # Git source records/indices/governance remain in import_origin as evidence.
        # They are not conflicting active representations beside native revisions.
        record_paths = {imported.store.get(imported.store.get(r['revision']).payload['source_document']).payload['path']
                        for r in origin['records']}
        historical = record_paths | {'memory/index.yaml', 'decisions/index.yaml', 'obligations/index.yaml',
                                     'governance/authority.yaml'}
        snapshot = KernelObject.create('SandboxSnapshot', {
            'project_id': origin['project_id'], 'base_snapshot': imported.snapshot_digest,
            'import_origin': imported.snapshot_digest, 'governance': governance.digest,
            'creating_transaction': None, 'records': origin['records'],
            'documents': [d for d in origin['documents'] if d['path'] not in historical],
            'evidence': sorted(o.digest for o in imported.store.objects.values() if o.kind == 'EvidenceObject'),
            'instance_state': 'quarantined'})
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                for value in imported.store.objects.values():
                    self.put(db, value)
                    if value.kind == 'EvidenceObject':
                        digest = value.payload['content_digest']
                        self.put_blob(db, digest, imported.store.blob(digest))
                self.put(db, governance)
                self.put(db, snapshot)
                db.execute('INSERT INTO projects VALUES (?,?,?)', (origin['project_id'], snapshot.digest, 'quarantined'))
                db.commit()
            except BaseException:
                db.rollback()
                raise
        return snapshot.digest

    @staticmethod
    def begin_read(db):
        db.execute("BEGIN")

    @staticmethod
    def begin(db):
        db.execute('BEGIN IMMEDIATE')

    @staticmethod
    def lookup(db, project, principal, key):
        row = db.execute('SELECT * FROM attempts WHERE project=? AND principal=? AND key=?',
                         (project, principal, key)).fetchone()
        return dict(row) if row else None

    def reserve(self, db, request):
        p = request.payload
        row = self.lookup(db, p['project_id'], p['principal'], p['idempotency_key'])
        if row:
            return 'ok' if row['request'] == request.digest else 'idempotency_conflict'
        block = db.execute('SELECT reason FROM write_blocks WHERE project=?', (p['project_id'],)).fetchone()
        if block:
            return block['reason']
        existing = db.execute('SELECT request FROM attempts WHERE project=? AND transaction_id=?',
                              (p['project_id'], p['transaction_id'])).fetchone()
        if existing:
            return 'transaction_id_conflict'
        self.put(db, request)
        db.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?)',
                   (p['project_id'], p['principal'], p['idempotency_key'], request.digest,
                    p['transaction_id'], 'pending', None, 'reserved'))
        return 'ok'

    @staticmethod
    def dependency_committed(db, project, transaction_id):
        row = db.execute('SELECT status FROM attempts WHERE project=? AND transaction_id=?',
                         (project, transaction_id)).fetchone()
        return row is not None and row['status'] == 'committed'

    @staticmethod
    def reject(db, p, reason):
        db.execute("UPDATE attempts SET status='not_committed',reason=? WHERE project=? AND principal=? AND key=? AND status='pending'",
                   (reason, p['project_id'], p['principal'], p['idempotency_key']))

    def publish(self, db, request, snapshot, receipt, objects, blobs):
        p = request.payload
        for obj in objects:
            self.put(db, obj)
        for digest, raw in blobs.items():
            self.put_blob(db, digest, raw)
        self.put(db, snapshot)
        self.put(db, receipt)
        changed = db.execute('UPDATE projects SET head=? WHERE project=? AND head=? AND mode=?',
                             (snapshot.digest, p['project_id'], p['base_snapshot'], 'quarantined')).rowcount
        if changed != 1:
            raise ValueError('head compare-and-swap failed')
        updated = db.execute("UPDATE attempts SET status='committed',receipt=?,reason='committed' WHERE project=? AND principal=? AND key=? AND request=? AND status='pending'",
                             (receipt.digest, p['project_id'], p['principal'], p['idempotency_key'], request.digest)).rowcount
        if updated != 1:
            raise ValueError('result publication conflict')

````
