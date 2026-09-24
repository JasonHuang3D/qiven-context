# [SEALED] tools/compile-context.sh

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/compile-context.sh`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````bash
#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then echo "ERROR: run tools/bootstrap.sh first." >&2; exit 2; fi
exec .venv/bin/python tools/compile_context.py "$@"

````
