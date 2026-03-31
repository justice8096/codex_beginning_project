from __future__ import annotations

from collections.abc import Mapping


def compact_metadata(raw: Mapping[str, str], *, max_items: int = 24) -> dict[str, str]:
    """
    Sanitize metadata for IFC property export.
    Keeps deterministic ordering and trims very large key sets.
    """
    items = sorted((str(k), str(v)) for k, v in raw.items() if k and v is not None)
    compact: dict[str, str] = {}
    for idx, (key, value) in enumerate(items):
        if idx >= max_items:
            compact["bambu2ifc.metadata_truncated"] = "true"
            break
        compact[key[:128]] = value[:2048]
    return compact
