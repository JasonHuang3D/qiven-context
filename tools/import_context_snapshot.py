"""Inspect a K1 quarantine import; the memory store expires with this process."""
import argparse
import json
from pathlib import Path
from context_kernel import import_git_snapshot


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--commit',required=True,help='Full exact Git commit ID')
    parser.add_argument('--project',required=True)
    parser.add_argument('--repository',required=True,help='Asserted source repository identity')
    parser.add_argument('--actor',required=True,help='Unverified import actor assertion')
    args=parser.parse_args()
    result=import_git_snapshot(args.root,args.commit,project_id=args.project,
                               repository=args.repository,actor_assertion=args.actor)
    print(json.dumps({'snapshot':result.snapshot_digest,'receipt':result.receipt_digest,
                      'records':len(result.snapshot.payload['records']),
                      'documents':len(result.snapshot.payload['documents']),
                      'instance_state':'quarantined','authorization':'not_granted'},indent=2))


if __name__=='__main__': main()
