"""Immutable source materialization for one Context read transaction.

Git inputs are read from a single commit. Non-Git directories are explicitly
non-authoritative exports/fixtures and must be quiescent during capture.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
from types import MappingProxyType
from typing import Mapping

SOURCE_ROOTS = ("README.md", "BOOTSTRAP.md", "MEMORY-CONSTITUTION.md", "governance",
                "collaboration", "schema", "state", "views", "sessions", "projects",
                "memory", "decisions", "obligations", "ledger", "evidence")
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_SOURCE_BYTES = 128 * 1024 * 1024


def canonical_json(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def safe_path(path: str) -> str:
    value = PurePosixPath(path)
    if not path or value.is_absolute() or ".." in value.parts or "\\" in path or ":" in path:
        raise ValueError(f"unsafe Context source path: {path!r}")
    return value.as_posix()


def source_path(path: str) -> bool:
    return path.split("/", 1)[0] in SOURCE_ROOTS


def digest_files(files: Mapping[str, bytes]) -> dict[str, str]:
    return {p: sha256(b).hexdigest() for p, b in sorted(files.items())}


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "--no-replace-objects", "-C", str(root), *args], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise ValueError(f"Git snapshot failed: {result.stderr.decode('utf-8', errors='replace').strip()}")
    return result.stdout


def _directory_files(root: Path) -> dict[str, bytes]:
    files = {}
    total = 0
    for entry in SOURCE_ROOTS:
        path = root / entry
        targets = [path] if path.is_file() else sorted(path.rglob("*")) if path.is_dir() else []
        for target in targets:
            if target.is_symlink():
                raise ValueError(f"snapshot does not follow symbolic links: {target}")
            if target.is_file():
                if target.stat().st_size > MAX_FILE_BYTES:
                    raise ValueError("Context source exceeds per-file byte limit")
                content = target.read_bytes()
                total += len(content)
                if total > MAX_SOURCE_BYTES:
                    raise ValueError("Context snapshot exceeds total byte limit")
                files[target.relative_to(root).as_posix()] = content
    return files


def git_source_files(root: Path, commit: str) -> dict[str, bytes]:
    # Read raw blobs: archive export-ignore/export-subst attributes are not source.
    entries = _git(root, "ls-tree", "-r", "-z", commit).split(b"\0")
    selected = []
    for entry in entries:
        if not entry:
            continue
        header, raw_path = entry.split(b"\t", 1)
        path = raw_path.decode("utf-8")
        if not source_path(path):
            continue
        mode, kind, oid = header.split()
        if kind != b"blob" or mode not in (b"100644", b"100755"):
            raise ValueError(f"unsupported snapshot source mode: {path}")
        selected.append((safe_path(path), oid))
    if not selected:
        raise ValueError("Git snapshot has no Context sources")
    files = {}
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(["git", "--no-replace-objects", "-C", str(root),
                                    "cat-file", "--batch"], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=errors)
        try:
            total = 0
            for path, oid in selected:
                process.stdin.write(oid + b"\n")
                process.stdin.flush()
                returned, kind, raw_size = process.stdout.readline().split()
                size = int(raw_size)
                total += size
                if (returned != oid or kind != b"blob" or size < 0
                        or size > MAX_FILE_BYTES or total > MAX_SOURCE_BYTES):
                    raise ValueError(f"unsupported or oversized snapshot source: {path}")
                content = process.stdout.read(size)
                if len(content) != size or process.stdout.read(1) != b"\n":
                    raise ValueError("truncated Git blob stream")
                files[path] = content
            process.stdin.close()
            if process.wait(timeout=30):
                raise ValueError("Git snapshot blob read failed")
        finally:
            if not process.stdin.closed:
                process.stdin.close()
            process.stdout.close()
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    return files


@dataclass(frozen=True)
class SourceSnapshot:
    origin: str
    kind: str
    commit: str | None
    tree: str | None
    files: Mapping[str, bytes]
    hashes: Mapping[str, str]
    id: str

    @classmethod
    def capture(cls, root: Path, *, ref: str | None = None) -> "SourceSnapshot":
        root = Path(root).resolve()
        is_git = (root / ".git").exists()
        commit = tree = None
        if is_git:
            # Always resolve a ref once, then only address immutable Git objects.
            commit = _git(root, "rev-parse", "--verify", (ref or "HEAD") + "^{commit}").decode().strip()
            tree = _git(root, "rev-parse", commit + "^{tree}").decode().strip()
            if ref is None and _git(root, "status", "--porcelain", "--untracked-files=all", "--", *SOURCE_ROOTS):
                raise ValueError("Context sources differ from HEAD; commit them or explicitly select a published ref")
            files = git_source_files(root, commit)
            kind = "git-commit"
        else:
            if ref is not None:
                raise ValueError("Git ref requires a Git repository")
            files = _directory_files(root)
            if digest_files(files) != digest_files(_directory_files(root)):
                raise ValueError("source directory changed during capture")
            kind = "quiescent-directory"
        if sum(map(len, files.values())) > MAX_SOURCE_BYTES:
            raise ValueError("Context snapshot exceeds total byte limit")
        hashes = digest_files(files)
        identity = sha256(canonical_json(hashes)).hexdigest()
        return cls(str(root), kind, commit, tree, MappingProxyType(files), MappingProxyType(hashes), identity)

    def manifest(self) -> dict:
        return {"id": self.id, "kind": self.kind, "git_commit": self.commit,
                "git_tree": self.tree, "files": dict(self.hashes)}

    def text(self, path: str) -> str:
        path = safe_path(path)
        if path not in self.files:
            raise FileNotFoundError(f"missing Context snapshot source: {path}")
        return self.files[path].decode("utf-8")

    def evidence(self, path: str) -> dict:
        return {"path": path, "snapshot_id": self.id, "sha256": self.hashes[path],
                "content": self.text(path)}

    @contextmanager
    def materialize(self):
        # Private, bounded, disposable read materialization; no working-tree reads
        # occur after capture. This is not a JasonPC clone or authority boundary.
        with tempfile.TemporaryDirectory(prefix="qiven-context-read-") as temporary:
            root = Path(temporary)
            for path, content in self.files.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            yield root


def as_snapshot(root) -> SourceSnapshot:
    return root if isinstance(root, SourceSnapshot) else SourceSnapshot.capture(root)


def verify_evidence(manifest: Mapping, sources: Mapping[str, Mapping]) -> None:
    if sha256(canonical_json(manifest["files"])).hexdigest() != manifest["id"]:
        raise ValueError("snapshot manifest digest mismatch")
    for path, source in sources.items():
        if (source.get("path") != path or source.get("snapshot_id") != manifest["id"]
                or source.get("sha256") != manifest["files"].get(path)
                or sha256(source["content"].encode("utf-8")).hexdigest() != source.get("sha256")):
            raise ValueError(f"snapshot evidence mismatch: {path}")


def bind_snapshot(root, component=None) -> SourceSnapshot:
    existing = getattr(component, "snapshot", None)
    if existing is None:
        return as_snapshot(root)
    if isinstance(root, SourceSnapshot):
        if existing.id != root.id:
            raise ValueError("components use different Context snapshots")
    elif Path(root).resolve() != Path(existing.origin):
        raise ValueError("component snapshot belongs to a different source root")
    return existing
