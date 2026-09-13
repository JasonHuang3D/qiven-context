@echo off
setlocal
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe (
  echo ERROR: run tools\bootstrap.cmd first.
  exit /b 2
)
.venv\Scripts\python.exe tools\validate_context.py
exit /b %errorlevel%
