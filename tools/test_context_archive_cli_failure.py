"""K4 CLI failure-path proof for restore output cleanup."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from context_kernel import import_git_snapshot
from context_kernel.archive import export_snapshot
from test_context_transactions import STAMP

ROOT=Path(__file__).resolve().parents[1]


class ArchiveCliFailureTests(unittest.TestCase):
    def test_source_target_failure_does_not_publish_database(self):
        with tempfile.TemporaryDirectory(prefix='context-k4-cli-failure-') as temporary:
            root=Path(temporary)
            head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
            imported=import_git_snapshot(ROOT,head,project_id='qiven-context',
                repository='asserted:k4-cli-failure-fixture',actor_assertion='fixture')
            archive=export_snapshot(imported.store.get,imported.store.blob,imported.snapshot_digest,
                access_policy='fixture:canonical-continuity',observed_at=STAMP)
            package=root/'package.json';package.write_bytes(archive.encoded)
            blocker=root/'not-a-directory';blocker.write_text('fixture',encoding='utf-8')
            database=root/'restore.db';sources=blocker/'sources'
            result=subprocess.run([sys.executable,str(ROOT/'tools/context_archive.py'),'restore',
                '--input',str(package),'--database',str(database),'--sources',str(sources)],
                capture_output=True,timeout=60)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(database.exists(),result.stderr.decode())


if __name__=='__main__':unittest.main(verbosity=2)
