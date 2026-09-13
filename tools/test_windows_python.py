from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESOLVER = ROOT / "tools" / "resolve-python.cmd"
BOOTSTRAP = ROOT / "tools" / "bootstrap.cmd"
CMD = Path(os.environ.get("ComSpec", r"C:\Windows\System32\cmd.exe"))
SYSTEM32 = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"


class WindowsPythonResolutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.temp, ignore_errors=True)

    def mock(self, directory, name, valid=True, version="3.11.0", reported=None):
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        selected = str(reported or path)
        script = f"""@echo off
if not "{1 if valid else 0}"=="1" exit /b 1
echo %* | %SystemRoot%\\System32\\findstr.exe /l /c:"sys.executable" >nul
if not errorlevel 1 echo {selected}
echo %* | %SystemRoot%\\System32\\findstr.exe /l /c:"sys.version_info[:3]" >nul
if not errorlevel 1 echo {version}
exit /b 0
"""
        path.write_text(script, encoding="ascii")
        return path, {}

    def run_resolver(self, path_dirs, extra=None):
        env = os.environ.copy()
        env.update(extra or {})
        commands = self.temp / "commands"
        commands.mkdir(exist_ok=True)
        candidates = [p / "python.cmd" for p in path_dirs if (p / "python.cmd").exists()]
        where_lines = ["@echo off", *[f"echo {candidate}" for candidate in candidates]]
        if not candidates:
            where_lines.append("exit /b 1")
        (commands / "where.cmd").write_text("\n".join(where_lines) + "\n", encoding="ascii")
        env["PATH"] = os.pathsep.join([str(commands), *(str(p) for p in path_dirs), str(SYSTEM32)])
        env["PATHEXT"] = ".CMD;.EXE"
        return subprocess.run(
            [str(CMD), "/d", "/c", str(RESOLVER)],
            text=True,
            capture_output=True,
            env=env,
            cwd=ROOT,
        )

    def assert_selected(self, result, expected):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"Qiven Python:\n{expected}\n", result.stdout.replace("\r\n", "\n"))

    def test_qiven_python_valid(self):
        candidate, env = self.mock(self.temp / "explicit", "chosen.cmd")
        env["QIVEN_PYTHON"] = str(candidate)
        self.assert_selected(self.run_resolver([], env), candidate)

    def test_qiven_python_invalid_does_not_fallback(self):
        fallback, env = self.mock(self.temp / "fallback", "python.cmd")
        env["QIVEN_PYTHON"] = str(self.temp / "missing python.exe")
        result = self.run_resolver([fallback.parent], env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("QIVEN_PYTHON", result.stderr)
        self.assertNotIn(str(fallback), result.stdout)

    def test_qiven_python_old_does_not_fallback(self):
        old, env = self.mock(self.temp / "old", "old python.cmd", valid=False, version="3.10.9")
        fallback, _ = self.mock(self.temp / "fallback", "python.cmd")
        env["QIVEN_PYTHON"] = str(old)
        result = self.run_resolver([fallback.parent], env)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(str(fallback), result.stdout)

    def test_broken_python_then_valid_python(self):
        broken, _ = self.mock(self.temp / "first", "python.cmd", valid=False)
        valid, env = self.mock(self.temp / "second", "python.cmd")
        self.assert_selected(self.run_resolver([broken.parent, valid.parent], env), valid)

    def test_valid_python_ignores_broken_py(self):
        python, env = self.mock(self.temp / "python", "python.cmd")
        py, _ = self.mock(self.temp / "py", "py.cmd", valid=False)
        self.assert_selected(self.run_resolver([python.parent, py.parent], env), python)

    def test_py_fallback(self):
        python, _ = self.mock(self.temp / "python", "python.cmd", valid=False)
        py, env = self.mock(self.temp / "py", "py.cmd")
        self.assert_selected(self.run_resolver([python.parent, py.parent], env), py)

    def test_no_valid_interpreter(self):
        python, env = self.mock(self.temp / "python", "python.cmd", valid=False)
        py, _ = self.mock(self.temp / "py", "py.cmd", valid=False)
        result = self.run_resolver([python.parent, py.parent], env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Python 3.11 or newer is required", result.stderr)
        self.assertIn("where python", result.stderr)
        self.assertIn("fallback", result.stderr)

    def test_space_containing_path(self):
        candidate, env = self.mock(self.temp / "path with spaces", "python.cmd")
        env["QIVEN_PYTHON"] = str(candidate)
        self.assert_selected(self.run_resolver([], env), candidate)

    def fixture_repo(self):
        repo = self.temp / "repo"
        (repo / "tools").mkdir(parents=True)
        shutil.copy2(BOOTSTRAP, repo / "tools" / "bootstrap.cmd")
        shutil.copy2(RESOLVER, repo / "tools" / "resolve-python.cmd")
        (repo / "tools" / "requirements.txt").write_text("", encoding="ascii")
        return repo

    def test_existing_valid_venv_is_reused(self):
        repo = self.fixture_repo()
        subprocess.run([sys.executable, "-m", "venv", str(repo / ".venv")], check=True)
        executable = repo / ".venv" / "Scripts" / "python.exe"
        before = executable.stat().st_mtime_ns
        env = os.environ.copy()
        env.update({"PIP_NO_INDEX": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1", "QIVEN_PYTHON": str(self.temp / "must not be used.exe")})
        result = subprocess.run([str(CMD), "/d", "/c", str(repo / "tools" / "bootstrap.cmd")], cwd=repo, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(executable.stat().st_mtime_ns, before)

    def test_bootstrap_creates_venv_with_resolved_interpreter(self):
        repo = self.fixture_repo()
        env = os.environ.copy()
        env.update({"PIP_NO_INDEX": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1", "QIVEN_PYTHON": sys.executable})
        result = subprocess.run([str(CMD), "/d", "/c", str(repo / "tools" / "bootstrap.cmd")], cwd=repo, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        created = repo / ".venv" / "Scripts" / "python.exe"
        self.assertTrue(created.exists())
        probe = subprocess.run([str(created), "-c", "import sys; raise SystemExit(sys.version_info < (3,11))"])
        self.assertEqual(probe.returncode, 0)

    def test_existing_broken_venv_is_rejected(self):
        repo = self.fixture_repo()
        executable = repo / ".venv" / "Scripts" / "python.exe"
        executable.parent.mkdir(parents=True)
        # Use a real Windows PE that is deliberately not Python. A zero-byte
        # .exe makes Windows raise a GUI "This app can't run on your PC" dialog
        # outside captured stdio, which is hostile to unattended test runs.
        shutil.copy2(SYSTEM32 / "where.exe", executable)
        result = subprocess.run([str(CMD), "/d", "/c", str(repo / "tools" / "bootstrap.cmd")], cwd=repo, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Existing .venv is invalid", result.stderr)
        self.assertTrue(executable.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
