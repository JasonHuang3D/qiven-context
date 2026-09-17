"""Export one exact Git snapshot or restore a read-only quarantine for inspection."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

from context_kernel import import_git_snapshot
from context_kernel.archive import export_snapshot, restore_export, MAX_PACKAGE_BYTES
from context_kernel.reads import KernelReadSnapshot
from context_kernel.sqlite_reference import SQLiteReference


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    export=commands.add_parser('export-git')
    export.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    export.add_argument('--commit',required=True)
    export.add_argument('--project',default='qiven-context')
    export.add_argument('--repository',required=True)
    export.add_argument('--output',type=Path,required=True)
    restore=commands.add_parser('restore')
    restore.add_argument('--input',type=Path,required=True)
    restore.add_argument('--database',type=Path,required=True)
    restore.add_argument('--sources',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='export-git':
        imported=import_git_snapshot(args.root,args.commit,project_id=args.project,
                                     repository=args.repository,actor_assertion='archive-cli-unverified')
        archive=export_snapshot(imported.store.get,imported.store.blob,imported.snapshot_digest,
            access_policy='owner-authorized-context-recovery',
            observed_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
        with args.output.open('xb') as stream:stream.write(archive.encoded)
        print(json.dumps({'manifest_digest':archive.value['manifest_digest'],
                          'package_digest':archive.value['package_digest'],'source_commit':args.commit}))
    else:
        if args.database.exists() or args.sources.exists():
            raise ValueError('restore targets must not exist')
        if args.input.stat().st_size > MAX_PACKAGE_BYTES:
            raise ValueError('package exceeds transport limit')
        restored=restore_export(args.input.read_bytes())
        if not restored.report['complete']:
            print(json.dumps(restored.report));return 2
        read=KernelReadSnapshot.capture(restored.store.get,restored.store.blob,restored.snapshot)
        sources_owned=False
        database_owned=False
        try:
            # Materialize reviewable sources before publishing the runnable reference
            # adapter. Both targets are claimed exclusively and removed on ordinary
            # failure; K4 deliberately does not claim power-loss atomicity.
            args.sources.mkdir()
            sources_owned=True
            for path,raw in read.source.files.items():
                target=args.sources/path;target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as stream:stream.write(raw)
            with args.database.open('xb'):
                pass
            database_owned=True
            restored.to_sqlite(SQLiteReference(args.database))
        except BaseException:
            if database_owned:
                for suffix in ('','-wal','-shm'):
                    Path(str(args.database)+suffix).unlink(missing_ok=True)
            if sources_owned:
                shutil.rmtree(args.sources,ignore_errors=True)
            raise
        print(json.dumps({'snapshot':restored.snapshot,'manifest_digest':restored.manifest_digest,**restored.report}))
    return 0


if __name__=='__main__':raise SystemExit(main())
