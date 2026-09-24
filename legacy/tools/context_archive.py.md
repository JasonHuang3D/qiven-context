# [SEALED] tools/context_archive.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/context_archive.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
"""Export, restore, or build/verify one K4 canonical Context handoff."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

from context_kernel import import_git_snapshot
from context_kernel.archive import export_snapshot, restore_export, MAX_PACKAGE_BYTES
from context_kernel.handoff import build_handoff, verify_handoff, summary, MAX_HANDOFF_BYTES
from context_kernel.reads import KernelReadSnapshot
from context_kernel.sqlite_reference import SQLiteReference


def _stamp():
    return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')


def _export(root, commit, project, repository):
    imported=import_git_snapshot(root,commit,project_id=project,
                                 repository=repository,actor_assertion='archive-cli-unverified')
    return export_snapshot(imported.store.get,imported.store.blob,imported.snapshot_digest,
        access_policy='owner-authorized-context-recovery',observed_at=_stamp())


def _write_new(path, raw):
    owned=False
    try:
        with path.open('xb') as stream:
            owned=True
            stream.write(raw)
    except BaseException:
        if owned:path.unlink(missing_ok=True)
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    export=commands.add_parser('export-git')
    export.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    export.add_argument('--commit',required=True)
    export.add_argument('--project',default='qiven-context')
    export.add_argument('--repository',required=True)
    export.add_argument('--output',type=Path,required=True)
    handoff=commands.add_parser('handoff-git')
    handoff.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    handoff.add_argument('--commit',required=True)
    handoff.add_argument('--project',default='qiven-context')
    handoff.add_argument('--repository',required=True)
    handoff.add_argument('--output',type=Path,required=True)
    verify=commands.add_parser('handoff-verify')
    verify.add_argument('--input',type=Path,required=True)
    restore=commands.add_parser('restore')
    restore.add_argument('--input',type=Path,required=True)
    restore.add_argument('--database',type=Path,required=True)
    restore.add_argument('--sources',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='export-git':
        archive=_export(args.root,args.commit,args.project,args.repository)
        _write_new(args.output,archive.encoded)
        print(json.dumps({'manifest_digest':archive.value['manifest_digest'],
                          'package_digest':archive.value['package_digest'],'source_commit':args.commit}))
    elif args.command=='handoff-git':
        archive=_export(args.root,args.commit,args.project,args.repository)
        artifact=build_handoff(archive)
        _write_new(args.output,artifact.encoded)
        try:
            raw=args.output.read_bytes();verified=verify_handoff(raw)
        except BaseException:
            args.output.unlink(missing_ok=True);raise
        print(json.dumps({**summary(verified),'handoff_bytes':len(raw)},sort_keys=True))
    elif args.command=='handoff-verify':
        if args.input.stat().st_size > MAX_HANDOFF_BYTES:
            raise ValueError('handoff exceeds transport limit')
        raw=args.input.read_bytes();verified=verify_handoff(raw)
        print(json.dumps({**summary(verified),'handoff_bytes':len(raw)},sort_keys=True))
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

````
