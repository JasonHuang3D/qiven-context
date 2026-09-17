"""Kernel canonical serialization v1. See collaboration/context-kernel-k1.md."""
from hashlib import sha256
import json

PREFIX = b"qiven.context.kernel\x00v1\x00"
MAX_INTEGER = 2**53 - 1
MAX_BYTES = 16 * 1024 * 1024


def _check(value, depth=0):
    if depth > 64:
        raise ValueError("canonical value exceeds depth 64")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_INTEGER:
            raise ValueError("canonical integer exceeds exact interoperable range")
        return
    if type(value) is str:
        value.encode("utf-8", errors="strict")
        return
    if type(value) is list:
        for item in value:
            _check(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("canonical object keys must be strings")
            _check(key, depth + 1)
            _check(item, depth + 1)
        return
    raise ValueError(f"unsupported canonical type: {type(value).__name__}")


def canonical_bytes(value):
    _check(value)
    result = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                        allow_nan=False).encode("utf-8")
    if len(result) > MAX_BYTES:
        raise ValueError("canonical object exceeds byte limit")
    return result


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_canonical(raw):
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        raise ValueError("invalid serialized object size/type")
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
        if canonical_bytes(result) != raw:
            raise ValueError("noncanonical serialized bytes")
        return result
    except (UnicodeError, RecursionError) as exc:
        raise ValueError("invalid canonical encoding") from exc


def semantic_digest(raw):
    return "sha256:" + sha256(PREFIX + raw).hexdigest()
