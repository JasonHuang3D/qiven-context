#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
  echo "ERROR: Python 3.11 or newer is required." >&2
  exit 1
fi
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r tools/requirements.txt
