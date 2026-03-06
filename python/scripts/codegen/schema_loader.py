"""Load, validate, and resolve pyjvlink record schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_DIR = Path(__file__).resolve().parents[1] / ".." / "src" / "pyjvlink" / "_internal" / "protocol" / "schema"
SCHEMA_DIR = SCHEMA_DIR.resolve()

SEMANTIC_TYPES = frozenset(
    {
        "str",
        "int",
        "float",
        "date_yyyymmdd",
        "date_mmdd",
        "time_hhmm",
        "datetime_mmddhhmm",
        "duration_ss_s",
        "duration_mss_s",
        "duration_mss_ss",
        "duration_ss_ss",
        "money_100yen",
        "flag",
        "reserved",
        "array:int",
        "array:str",
        "array:float",
        "array:money_100yen",
        "array:duration_ss_s",
        "array:object",
    }
)

WIRE_TYPES = frozenset({"string", "array"})

REQUIRED_SCHEMA_KEYS = {"record_type", "title", "record_length", "key_fields", "fields"}
REQUIRED_FIELD_KEYS = {"name", "item_number", "wire_type", "semantic_type", "byte_position", "byte_size"}
REQUIRED_ELEMENT_KEYS = {"name", "wire_type", "semantic_type", "byte_offset", "byte_size"}


class SchemaError(Exception):
    """Raised when a schema is invalid."""

    def __init__(self, record_type: str, message: str) -> None:
        super().__init__(f"[{record_type}] {message}")
        self.record_type = record_type


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_common_fields() -> list[dict[str, Any]]:
    """Load the shared common race fields."""
    common_path = SCHEMA_DIR / "_common_race_fields.json"
    data = _load_json(common_path)
    return data["fields"]


def load_common_header_fields() -> list[dict[str, Any]]:
    """Load the shared header-only fields (data_code, data_creation_date)."""
    header_path = SCHEMA_DIR / "_common_header_fields.json"
    data = _load_json(header_path)
    return data["fields"]


def load_schema(record_type: str) -> dict[str, Any]:
    """Load a single record schema by type (e.g. 'ra', 'RA')."""
    path = SCHEMA_DIR / "records" / f"{record_type.lower()}.json"
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    return _load_json(path)


def load_all_schemas() -> dict[str, dict[str, Any]]:
    """Load all record schemas from the records/ directory."""
    records_dir = SCHEMA_DIR / "records"
    schemas = {}
    for path in sorted(records_dir.glob("*.json")):
        schema = _load_json(path)
        rt = schema.get("record_type", path.stem.upper())
        schemas[rt] = schema
    return schemas


def resolve_fields(schema: dict[str, Any]) -> list[dict[str, Any]]:
    """Return full field list: common fields (if referenced) + record-specific fields."""
    fields: list[dict[str, Any]] = []
    if schema.get("common_fields_ref"):
        fields.extend(load_common_fields())
    elif schema.get("common_header_fields_ref"):
        fields.extend(load_common_header_fields())
    fields.extend(schema.get("fields", []))
    return fields


def validate_schema(schema: dict[str, Any]) -> list[str]:
    """Validate a record schema. Returns list of error messages (empty if valid)."""
    errors: list[str] = []
    rt = schema.get("record_type", "UNKNOWN")

    # Check required top-level keys
    missing_keys = REQUIRED_SCHEMA_KEYS - set(schema.keys())
    if missing_keys:
        errors.append(f"[{rt}] Missing required keys: {missing_keys}")
        return errors  # Can't proceed without required keys

    # Check key_fields reference existing field names
    all_fields = resolve_fields(schema)
    field_names = {f["name"] for f in all_fields}
    for key_field in schema["key_fields"]:
        if key_field not in field_names:
            errors.append(f"[{rt}] key_field '{key_field}' not found in fields")

    # Validate each field (including common fields)
    seen_names: set[str] = set()
    for field in all_fields:
        errors.extend(_validate_field(rt, field, seen_names))

    return errors


def _validate_field(rt: str, field: dict[str, Any], seen_names: set[str]) -> list[str]:
    """Validate a single field definition."""
    errors: list[str] = []
    name = field.get("name", "<unnamed>")

    # Check required keys
    missing = REQUIRED_FIELD_KEYS - set(field.keys())
    if missing:
        errors.append(f"[{rt}] Field '{name}' missing required keys: {missing}")
        return errors

    # Check unique name
    if name in seen_names:
        errors.append(f"[{rt}] Duplicate field name: '{name}'")
    seen_names.add(name)

    # Check wire_type
    if field["wire_type"] not in WIRE_TYPES:
        errors.append(f"[{rt}] Field '{name}' has invalid wire_type: '{field['wire_type']}'")

    # Check semantic_type
    st = field["semantic_type"]
    if st not in SEMANTIC_TYPES and not st.startswith("enum:"):
        errors.append(f"[{rt}] Field '{name}' has invalid semantic_type: '{st}'")

    # Check array:object requires element_fields
    if st == "array:object":
        if "element_fields" not in field:
            errors.append(f"[{rt}] Field '{name}' is array:object but missing element_fields")
        elif "array_info" not in field:
            errors.append(f"[{rt}] Field '{name}' is array:object but missing array_info")
        else:
            for ef in field["element_fields"]:
                ef_missing = REQUIRED_ELEMENT_KEYS - set(ef.keys())
                if ef_missing:
                    ef_name = ef.get("name", "<unnamed>")
                    errors.append(f"[{rt}] Element field '{name}.{ef_name}' missing keys: {ef_missing}")

    # Check array types have array_info
    if st.startswith("array:") and "array_info" not in field:
        errors.append(f"[{rt}] Field '{name}' is '{st}' but missing array_info")

    return errors


def validate_all() -> list[str]:
    """Validate all schemas and return all errors."""
    errors: list[str] = []
    for _rt, schema in load_all_schemas().items():
        errors.extend(validate_schema(schema))
    return errors
