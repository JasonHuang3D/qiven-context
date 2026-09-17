"""Immutable, versioned K1 objects and a non-authoritative memory reference store."""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from types import MappingProxyType
from jsonschema import Draft202012Validator, FormatChecker
from context_snapshot import safe_path
from .registry import REGISTRY
from .serialization import canonical_bytes, parse_canonical, semantic_digest

_SCHEMA = json.loads((Path(__file__).resolve().parents[2] / "schema/context-kernel-object.schema.json").read_text())
_VALIDATOR = Draft202012Validator(_SCHEMA)
_RECORD_VALIDATORS = {}
for _kind, (_, _name, _expected) in REGISTRY.items():
    _raw = (Path(__file__).resolve().parents[2] / f"schema/{_name}.schema.json").read_bytes()
    if sha256(_raw).hexdigest() != _expected:
        raise ValueError("kernel source schema registry requires a versioned migration")
    _RECORD_VALIDATORS[_kind] = Draft202012Validator(json.loads(_raw), format_checker=FormatChecker())


@dataclass(frozen=True)
class ProjectId:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str) or not re.fullmatch(r"[a-z][a-z0-9.-]{0,127}", self.value):
            raise ValueError("invalid ProjectId")


@dataclass(frozen=True)
class RecordId:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str) or not re.fullmatch(r"ADR-[0-9]{4}|(?:MEM|OBL)-[0-9]{8}T[0-9]{6}Z-[A-F0-9]{6}", self.value):
            raise ValueError("unregistered RecordId")


@dataclass(frozen=True)
class KernelObject:
    encoded: bytes

    def __post_init__(self):
        value = parse_canonical(self.encoded)
        errors = list(_VALIDATOR.iter_errors(value))
        if errors:
            raise ValueError("invalid kernel object: " + errors[0].message)
        p = value["payload"]
        if value["kind"] == "RecordRevision":
            kind = p["record_kind"]
            _RECORD_VALIDATORS[kind].validate(p["metadata"])
            if p["record_schema"] != "sha256:" + REGISTRY[kind][2] or p["record_id"] != p["metadata"]["id"]:
                raise ValueError("revision identity/schema mismatch")
        elif value["kind"] == "SourceDocument":
            if safe_path(p["path"]) != p["path"]:
                raise ValueError("noncanonical source document path")
        elif value["kind"] == "ProjectSnapshot":
            for field, key in (("records", "record_id"), ("documents", "path")):
                keys = [item[key] for item in p[field]]
                if keys != sorted(set(keys)):
                    raise ValueError("snapshot manifest must be sorted and unique")

    @classmethod
    def create(cls, kind, payload):
        return cls(canonical_bytes({"serialization_version": 1, "kind": kind, "payload": payload}))

    @property
    def digest(self):
        return semantic_digest(self.encoded)

    @property
    def kind(self):
        return self.value["kind"]

    @property
    def value(self):
        # Every access is detached: callers cannot mutate stored nested values.
        return parse_canonical(self.encoded)

    @property
    def payload(self):
        return self.value["payload"]


class MemoryStore:
    """Immutable objects only. No canonical head, durable commit or permission API.

    Single-owner K1 reference adapter; concurrent publication belongs to K2.
    Snapshot installation is performed only after importer closure validation.
    """
    def __init__(self):
        self._objects = {}
        self._blobs = {}

    @property
    def objects(self):
        return MappingProxyType(self._objects)

    def put(self, obj):
        checked = KernelObject(obj.encoded)
        old = self._objects.get(checked.digest)
        if old is not None and old.encoded != checked.encoded:
            raise ValueError("semantic digest collision")
        self._objects[checked.digest] = checked
        return checked.digest

    def get(self, digest):
        return self._objects[digest]

    def put_blob(self, raw):
        if type(raw) is not bytes:
            raise ValueError("raw source must be immutable bytes")
        digest = "sha256:" + sha256(raw).hexdigest()
        if digest in self._blobs and self._blobs[digest] != raw:
            raise ValueError("raw digest collision")
        self._blobs[digest] = raw
        return digest

    def blob(self, digest):
        return self._blobs[digest]
