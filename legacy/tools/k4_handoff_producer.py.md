# [SEALED] tools/k4_handoff_producer.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/k4_handoff_producer.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
"""Human Manual Mode producer for the exact remote K4 handoff candidate."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

from context_kernel import import_git_snapshot
from context_kernel.archive import export_snapshot
from context_kernel.handoff import build_handoff, verify_handoff, summary

ROOT=Path(__file__).resolve().parents[1]
REMOTE='origin'
BRANCH='refs/heads/jason-brother/context-k4'
REPOSITORY='JasonHuang3D/qiven-context'


def git(*args):
    result=subprocess.run(['git','--no-replace-objects','-C',str(ROOT),*args],
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8',errors='replace').strip() or 'git command failed')
    return result.stdout.decode('utf-8').strip()


def main(argv=None):
    import os, sys
    # Branch is parameterizable so the producer can materialize any exact
    # published candidate (v4 activation trial, 2026-09-20); default keeps
    # the K4 reference acceptance branch.
    branch = (argv or sys.argv[1:])[0] if (argv or sys.argv[1:]) else os.environ.get('QIVEN_K4_BRANCH', BRANCH)
    head=git('rev-parse','--verify','HEAD^{commit}')
    tree=git('rev-parse','--verify',head+'^{tree}')
    if git('status','--porcelain','--untracked-files=all'):
        raise RuntimeError('K4 producer requires a clean working tree')
    remote=git('ls-remote','--exit-code',REMOTE,branch).split()
    if len(remote)<2 or remote[0]!=head or remote[1]!=branch:
        raise RuntimeError(f'local HEAD {head} is not exact remote {branch}')

    observed=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    imported=import_git_snapshot(ROOT,head,project_id='qiven-context',repository=REPOSITORY,
                                 actor_assertion='jasonpc-k4-handoff-producer')
    if imported.snapshot.payload['source']['tree']!=tree:
        raise RuntimeError('imported tree differs from exact local Git tree')
    archive=export_snapshot(imported.store.get,imported.store.blob,imported.snapshot_digest,
                            access_policy='owner-authorized-k4-handoff',observed_at=observed)
    artifact=build_handoff(archive)
    verified=verify_handoff(artifact.encoded)
    result=summary(verified)
    if result['source_commit']!=head or result['source_tree']!=tree or not result['complete']:
        raise RuntimeError('verified handoff identity differs from producer candidate')

    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder=ROOT/'generated'/'k4-handoff';folder.mkdir(parents=True,exist_ok=True)
    output=folder/f'k4-{head}-{stamp}.json'
    owned=False
    try:
        with output.open('xb') as stream:
            owned=True
            stream.write(artifact.encoded)
        persisted=verify_handoff(output.read_bytes())
        if persisted.handoff_digest!=result['handoff_digest']:
            raise RuntimeError('persisted handoff verification mismatch')
    except BaseException:
        if owned:output.unlink(missing_ok=True)
        raise

    print(json.dumps({
        'status':'PASS','role':'k4_handoff_producer','remote_ref':branch,
        'artifact':str(output.relative_to(ROOT)),'handoff_bytes':len(artifact.encoded),
        'python':sys.version.split()[0],'platform':platform.platform(),**result
    },ensure_ascii=False,sort_keys=True))
    return 0


if __name__=='__main__':raise SystemExit(main())

````
