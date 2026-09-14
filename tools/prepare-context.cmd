@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe (
  echo ERROR: run tools\bootstrap.cmd first. 1>&2
  exit /b 2
)
.venv\Scripts\python.exe tools\prepare_context.py %*
set "QIVEN_EXIT_CODE=%errorlevel%"
exit /b %QIVEN_EXIT_CODE%
