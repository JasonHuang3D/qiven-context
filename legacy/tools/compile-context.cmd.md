# [SEALED] tools/compile-context.cmd

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/compile-context.cmd`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````cmd
@echo off
setlocal
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe (
  echo ERROR: run tools\bootstrap.cmd first.
  exit /b 2
)
.venv\Scripts\python.exe tools\compile_context.py %*
exit /b %errorlevel%

````
