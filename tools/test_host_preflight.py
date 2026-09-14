from pathlib import Path
import io
import unittest
from unittest import mock
from contextlib import redirect_stderr

import host_preflight


class HostPreflightTests(unittest.TestCase):
    def test_environment_forces_noninteractive_authentication(self):
        env = host_preflight.environment()
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
        self.assertEqual(env["GCM_INTERACTIVE"], "Never")
        self.assertEqual(env["GH_PROMPT_DISABLED"], "1")

    def test_canonical_paths_are_absolute(self):
        for path in (
            host_preflight.PYTHON, host_preflight.CMAKE, host_preflight.NINJA,
            host_preflight.VSWHERE, host_preflight.GIT, host_preflight.GH,
            host_preflight.SSH, host_preflight.KNOWN_HOSTS,
        ):
            self.assertTrue(Path(path).is_absolute(), path)

    def test_report_command_rejects_unexpected_exit(self):
        result = mock.Mock(returncode=2, stdout="", stderr="prompt required")
        report = host_preflight.Report()
        with mock.patch.object(host_preflight, "run", return_value=result):
            with redirect_stderr(io.StringIO()):
                report.command("auth", ["tool"], r"authenticated")
        self.assertEqual(report.failures, ["auth"])

    def test_effective_ssh_normalizes_keys(self):
        result = mock.Mock(stdout="HostName ssh.github.com\nBatchMode yes\n", stderr="")
        self.assertEqual(
            host_preflight.effective_ssh(result),
            {"hostname": "ssh.github.com", "batchmode": "yes"},
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
