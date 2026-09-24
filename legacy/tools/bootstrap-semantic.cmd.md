# [SEALED] tools/bootstrap-semantic.cmd

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/bootstrap-semantic.cmd`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````cmd
@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe (
  echo ERROR: run tools\bootstrap.cmd first. 1>&2
  exit /b 2
)
echo [ RUN] installing optional semantic retrieval dependencies
.venv\Scripts\python.exe -m pip install -r tools\requirements-semantic.txt || exit /b 1
echo [ OK ] semantic retrieval dependencies installed

````
