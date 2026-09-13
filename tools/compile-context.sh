#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then echo "ERROR: run tools/bootstrap.sh first." >&2; exit 2; fi
exec .venv/bin/python tools/compile_context.py "$@"
