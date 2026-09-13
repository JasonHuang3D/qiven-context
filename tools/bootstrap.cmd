@echo off
setlocal
cd /d "%~dp0.."
py -3.14 -m venv .venv || exit /b 1
.venv\Scripts\python.exe -m pip install --upgrade pip || exit /b 1
.venv\Scripts\python.exe -m pip install -r tools\requirements.txt || exit /b 1
