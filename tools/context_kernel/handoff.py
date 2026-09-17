"""K4 self-describing artifact handoff over one canonical Context export.

The archival package remains semantic truth. The continuity projection is a
strictly derived, digest-bound LLM transport view and may never diverge from it.
"""
from dataclasses import dataclass
from hashlib import sha256
import base64
import json

from context_snapshot import safe_path
from .archive import CanonicalExport, encode as archive_encode, restore_export
from .reads import KernelReadSnapshot
from .serialization import _check, _pairs

FORMAT = 'qiven-context-handoff'
VERSION = 1
PROJECTION_VERSION = 1
CONSUMER_PROFILE = 'qiven-k4-artifact-continuity-v1'
MAX_HANDOFF_BYTES = 640 * 1024 * 1024
PREFIX = b'qiven.context.handoff\0v1\0'


def encode(value):
    _check(value)
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                     allow_nan=False).encode('utf-8')
    if len(raw) > MAX_HANDOFF_BYTES:
        raise ValueError('handoff exceeds byte limit')
    return raw


def parse(raw):
    if type(raw) is not bytes or len(raw) > MAX_HANDOFF_BYTES:
        raise ValueError('invalid handoff bytes or size')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs)
    except (UnicodeError, RecursionError, json.JSONDecodeError) as exc:
        raise ValueError('invalid handoff encoding') from exc
    if encode(value) != raw:
        raise ValueError('noncanonical handoff encoding')
    return value


def digest(domain, value):
    return 'sha256:' + sha256(PREFIX + domain.encode('ascii') + b'\0' + encode(value)).hexdigest()


def _consumer_profile():
    return {
        'id': CONSUMER_PROFILE,
        'project_continuity_path': 'collaboration/project-continuity-acceptance.md',
        'handoff_contract_path': 'collaboration/context-handoff-contract.md',
        'projection_semantics': 'continuity_projection.files are exact source bytes derived from canonical_export',
        'phase_a': 'artifact_only_no_remote_qiven_context',
        'phase_b': 'live_verification_only_after_phase_a_sealed',
    }


def _text_or_base64(raw):
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        return 'base64', base64.b64encode(raw).decode('ascii')
    if any(ord(ch) < 32 and ch not in '\t\n\r' for ch in text):
        return 'base64', base64.b64encode(raw).decode('ascii')
    return 'utf-8', text


def _decode_entry(entry):
    if not isinstance(entry, dict) or set(entry) != {'path', 'digest', 'size', 'encoding', 'content'}:
        raise ValueError('invalid handoff projection entry')
    try:
        path = safe_path(entry['path'])
    except Exception as exc:
        raise ValueError('invalid handoff projection path') from exc
    if path != entry['path']:
        raise ValueError('noncanonical handoff projection path')
    if entry['encoding'] == 'utf-8':
        if not isinstance(entry['content'], str):
            raise ValueError('invalid utf-8 projection content')
        raw = entry['content'].encode('utf-8')
    elif entry['encoding'] == 'base64':
        if not isinstance(entry['content'], str):
            raise ValueError('invalid base64 projection content')
        try:
            raw = base64.b64decode(entry['content'], validate=True)
        except Exception as exc:
            raise ValueError('invalid base64 projection content') from exc
        if base64.b64encode(raw).decode('ascii') != entry['content']:
            raise ValueError('noncanonical base64 projection content')
    else:
        raise ValueError('unknown handoff projection encoding')
    expected = 'sha256:' + sha256(raw).hexdigest()
    if type(entry['size']) is not int or entry['size'] < 0 or len(raw) != entry['size'] or entry['digest'] != expected:
        raise ValueError('handoff projection content integrity mismatch')
    return raw


def _projection(read):
    files = []
    for path, raw in sorted(read.source.files.items()):
        encoding, content = _text_or_base64(raw)
        files.append({'path': path, 'digest': 'sha256:' + sha256(raw).hexdigest(),
                      'size': len(raw), 'encoding': encoding, 'content': content})
    body = {'version': PROJECTION_VERSION, 'source_snapshot_id': read.source.id,
            'files': files}
    return {**body, 'projection_digest': digest('projection', body)}


def _source_identity(restored):
    snapshot = restored.store.get(restored.snapshot)
    if snapshot.kind != 'ProjectSnapshot':
        raise ValueError('K4 handoff requires an exact imported Git ProjectSnapshot')
    source = snapshot.payload.get('source')
    if not isinstance(source, dict):
        raise ValueError('missing handoff source identity')
    result = {key: source.get(key) for key in ('repository', 'commit', 'tree')}
    if any(not isinstance(value, str) or not value for value in result.values()):
        raise ValueError('incomplete handoff source identity')
    return result


@dataclass(frozen=True)
class CanonicalHandoff:
    encoded: bytes

    @property
    def value(self):
        return parse(self.encoded)


@dataclass(frozen=True)
class VerifiedHandoff:
    value: dict
    restored: object
    read: KernelReadSnapshot

    @property
    def files(self):
        return self.read.source.files

    @property
    def handoff_digest(self):
        return self.value['handoff_digest']


def build_handoff(archive):
    if not isinstance(archive, CanonicalExport):
        raise TypeError('handoff requires CanonicalExport')
    restored = restore_export(archive.encoded)
    if not restored.report['complete']:
        raise ValueError('K4 handoff requires complete canonical recovery')
    read = KernelReadSnapshot.capture(restored.store.get, restored.store.blob, restored.snapshot)
    package = archive.value
    content = {
        'format': FORMAT,
        'version': VERSION,
        'consumer_profile': _consumer_profile(),
        'source': _source_identity(restored),
        'snapshot': restored.snapshot,
        'manifest_digest': package['manifest_digest'],
        'package_digest': package['package_digest'],
        'recovery': restored.report,
        'authorization': 'not_granted',
        'writes_enabled': False,
        'canonical_export': package,
        'continuity_projection': _projection(read),
    }
    return CanonicalHandoff(encode({**content, 'handoff_digest': digest('handoff', content)}))


def verify_handoff(raw):
    value = parse(raw)
    required = {'format', 'version', 'consumer_profile', 'source', 'snapshot',
                'manifest_digest', 'package_digest', 'recovery', 'authorization',
                'writes_enabled', 'canonical_export', 'continuity_projection',
                'handoff_digest'}
    if set(value) != required or value.get('format') != FORMAT or type(value.get('version')) is not int or value['version'] != VERSION:
        raise ValueError('unsupported handoff envelope')
    content = {key: item for key, item in value.items() if key != 'handoff_digest'}
    if digest('handoff', content) != value['handoff_digest']:
        raise ValueError('handoff digest mismatch')
    if value['consumer_profile'] != _consumer_profile():
        raise ValueError('unsupported handoff consumer profile')
    if value['authorization'] != 'not_granted' or value['writes_enabled'] is not False:
        raise ValueError('handoff cannot grant authority')

    package_raw = archive_encode(value['canonical_export'])
    restored = restore_export(package_raw)
    if not restored.report['complete']:
        raise ValueError('handoff canonical recovery is incomplete')
    package = value['canonical_export']
    if (value['snapshot'] != restored.snapshot
            or value['manifest_digest'] != package['manifest_digest']
            or value['package_digest'] != package['package_digest']
            or value['recovery'] != restored.report):
        raise ValueError('handoff archive identity mismatch')
    if value['source'] != _source_identity(restored):
        raise ValueError('handoff source identity mismatch')

    projection = value['continuity_projection']
    if not isinstance(projection, dict) or set(projection) != {'version', 'source_snapshot_id', 'files', 'projection_digest'}:
        raise ValueError('invalid handoff projection')
    body = {key: projection[key] for key in ('version', 'source_snapshot_id', 'files')}
    if type(body['version']) is not int or body['version'] != PROJECTION_VERSION or digest('projection', body) != projection['projection_digest']:
        raise ValueError('handoff projection digest mismatch')
    if not isinstance(body['files'], list):
        raise ValueError('invalid handoff projection files')
    seen = set()
    for entry in body['files']:
        if not isinstance(entry, dict):
            raise ValueError('invalid handoff projection entry')
        if entry.get('path') in seen:
            raise ValueError('duplicate handoff projection path')
        seen.add(entry.get('path'))
        _decode_entry(entry)

    read = KernelReadSnapshot.capture(restored.store.get, restored.store.blob, restored.snapshot)
    expected = _projection(read)
    if projection != expected:
        raise ValueError('handoff projection differs from canonical export')
    return VerifiedHandoff(value, restored, read)


def summary(verified):
    if not isinstance(verified, VerifiedHandoff):
        raise TypeError('verified handoff required')
    projection = verified.value['continuity_projection']
    return {
        'format': FORMAT,
        'version': VERSION,
        'consumer_profile': verified.value['consumer_profile']['id'],
        'handoff_digest': verified.value['handoff_digest'],
        'projection_digest': projection['projection_digest'],
        'source_repository': verified.value['source']['repository'],
        'source_commit': verified.value['source']['commit'],
        'source_tree': verified.value['source']['tree'],
        'snapshot': verified.value['snapshot'],
        'manifest_digest': verified.value['manifest_digest'],
        'package_digest': verified.value['package_digest'],
        'projection_files': len(projection['files']),
        'complete': verified.restored.report['complete'],
        'authorization': verified.value['authorization'],
        'writes_enabled': verified.value['writes_enabled'],
    }
