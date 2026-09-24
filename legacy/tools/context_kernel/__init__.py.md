# [SEALED] tools/context_kernel/__init__.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/context_kernel/__init__.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
"""K1 reference kernel; importing is never an authority cutover."""
from .model import KernelObject, MemoryStore, ProjectId, RecordId
from .import_git import ImportedSnapshot, import_git_snapshot

__all__ = ["KernelObject", "MemoryStore", "ProjectId", "RecordId", "ImportedSnapshot", "import_git_snapshot"]

````
