@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0.."

if exist .venv\Scripts\python.exe goto :check_venv
if exist .venv (
  echo ERROR: Existing .venv is invalid; remove .venv and rerun bootstrap. 1>&2
  exit /b 1
)
call tools\resolve-python.cmd || exit /b 1
"%QIVEN_RESOLVED_PYTHON%" -m venv .venv || exit /b 1
goto :install

:check_venv
.venv\Scripts\python.exe -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1
if errorlevel 1 (
  echo ERROR: Existing .venv is invalid; remove .venv and rerun bootstrap. 1>&2
  exit /b 1
)

:install
.venv\Scripts\python.exe -m pip install --upgrade pip || exit /b 1
.venv\Scripts\python.exe -m pip install -r tools\requirements.txt || exit /b 1
