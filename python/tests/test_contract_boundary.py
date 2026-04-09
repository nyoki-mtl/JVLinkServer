"""Contract boundary tests.

These tests verify that the three layers (schema, decoder, C++ parser)
maintain consistent field naming. They serve as CI gates to prevent
contract drift.
"""

from __future__ import annotations

import ast
import re
import sys
from functools import lru_cache
from pathlib import Path

import pytest

# Add scripts to path for schema loader
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import codegen.schema_loader as schema_loader_module
from codegen.schema_loader import load_all_schemas, resolve_fields, validate_all, validate_schema

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DECODER_FILE = PROJECT_ROOT / "python" / "src" / "pyjvlink" / "_internal" / "codecs" / "record_decoder.py"
CPP_RECORDS_DIR = PROJECT_ROOT / "src" / "data" / "records"

# Common race fields handled by _build_context / _context_kwargs in the decoder
_CONTEXT_FIELDS = frozenset(
    {
        "meet_year",
        "meet_date",
        "racecourse_code",
        "meet_round",
        "meet_day",
        "race_number",
        "data_code",
        "data_creation_date",
    }
)


def _all_record_types() -> list[str]:
    schemas = load_all_schemas()
    return sorted(schemas.keys())


def _schema_top_level_field_names(record_type: str) -> set[str]:
    """Return top-level (non-reserved) field names from schema."""
    schemas = load_all_schemas()
    fields = resolve_fields(schemas[record_type])
    return {f["name"] for f in fields if f.get("semantic_type") != "reserved"}


def _schema_all_field_names(record_type: str, *, include_reserved: bool = False) -> set[str]:
    """Return all field names from schema including nested element fields."""
    schemas = load_all_schemas()
    fields = resolve_fields(schemas[record_type])
    names: set[str] = set()

    def walk(field_list: list[dict]) -> None:
        for field in field_list:
            semantic_type = field.get("semantic_type")
            if include_reserved or semantic_type != "reserved":
                name = field.get("name")
                if isinstance(name, str):
                    names.add(name)

            element_fields = field.get("element_fields")
            if isinstance(element_fields, list):
                walk(element_fields)

            nested_fields = field.get("fields")
            if isinstance(nested_fields, list):
                walk(nested_fields)

    walk(fields)
    return names


def _extract_cpp_structured_data_keys(record_type: str) -> set[str] | None:
    """Parse C++ source to extract structured_data key names.

    Returns None if the C++ file does not exist in the current checkout.
    """
    cpp_path = CPP_RECORDS_DIR / f"{record_type.lower()}_record.cpp"
    if not cpp_path.exists():
        return None
    source = cpp_path.read_text(encoding="utf-8")
    return {m.group(1) for m in re.finditer(r'structured_data\["(\w+)"\]', source)}


def _extract_cpp_output_keys(record_type: str) -> set[str] | None:
    """Parse C++ source to extract all JSON output keys (top-level + nested)."""
    cpp_path = CPP_RECORDS_DIR / f"{record_type.lower()}_record.cpp"
    if not cpp_path.exists():
        return None

    source = cpp_path.read_text(encoding="utf-8")
    # Matches assignments like:
    #   record.structured_data["foo"] = record.extractAndConvert(...)
    #   odds_entry["bar"] = record.extractAndConvert(...)
    #   performance["baz"] = record.extractAndConvertArray(...)
    from_extract_calls = {
        m.group(1) for m in re.finditer(r'\b\w+\["(\w+)"\]\s*=\s*record\.extractAndConvert(?:Array)?\(', source)
    }
    # Matches assignments like:
    #   record.structured_data["list"] = some_json_array;
    from_object_assignments = {
        m.group(1) for m in re.finditer(r'record\.structured_data\["(\w+)"\]\s*=\s*\w+\s*;', source)
    }

    return from_extract_calls | from_object_assignments


@lru_cache(maxsize=1)
def _decoder_functions() -> dict[str, ast.FunctionDef]:
    source = DECODER_FILE.read_text(encoding="utf-8")
    module = ast.parse(source)
    return {node.name: node for node in module.body if isinstance(node, ast.FunctionDef)}


def _collect_decoder_keys_and_calls(function_def: ast.FunctionDef) -> tuple[set[str], set[str]]:
    keys: set[str] = set()
    called_functions: set[str] = set()

    for node in ast.walk(function_def):
        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Attribute) and node.func.attr == "get" and node.args:
            key = node.args[0]
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)

        if isinstance(node.func, ast.Name):
            called_functions.add(node.func.id)

    return keys, called_functions


def _extract_decoder_payload_keys(record_type: str) -> set[str]:
    """Extract payload/row get keys used by a record decoder and its helper decoders."""
    root_name = f"_decode_{record_type.lower()}"
    functions = _decoder_functions()
    if root_name not in functions:
        return set()

    visited: set[str] = set()
    queue: list[str] = [root_name]
    keys: set[str] = set()

    while queue:
        function_name = queue.pop()
        if function_name in visited:
            continue
        visited.add(function_name)

        function_def = functions.get(function_name)
        if function_def is None:
            continue

        local_keys, called_functions = _collect_decoder_keys_and_calls(function_def)
        keys |= local_keys

        for called in called_functions:
            if called in functions and called.startswith("_decode_") and called not in visited:
                queue.append(called)

    return keys


# ---------------------------------------------------------------------------
# 1. Schema validation (all records)
# ---------------------------------------------------------------------------


def test_all_schemas_validate_without_errors():
    """Every JSON schema must pass structural validation."""
    errors = validate_all()
    assert errors == [], "Schema validation errors:\n" + "\n".join(errors)


@pytest.mark.parametrize("record_type", _all_record_types())
def test_schema_field_names_unique(record_type: str):
    """Each schema must have unique field names (no duplicates)."""
    schemas = load_all_schemas()
    fields = resolve_fields(schemas[record_type])
    names = [f["name"] for f in fields]
    assert len(names) == len(set(names)), f"{record_type}: duplicate field names"


@pytest.mark.parametrize("record_type", _all_record_types())
def test_schema_key_fields_exist(record_type: str):
    """key_fields must reference fields that actually exist in the schema."""
    schemas = load_all_schemas()
    schema = schemas[record_type]
    field_names = {f["name"] for f in resolve_fields(schema)}
    for key_field in schema.get("key_fields", []):
        assert key_field in field_names, f"{record_type}: key_field '{key_field}' not in fields"


# ---------------------------------------------------------------------------
# 2. Decoder contract tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("record_type", _all_record_types())
def test_decoder_keys_are_subset_of_schema(record_type: str):
    """Decoder must only reference field names that exist in the schema.

    This catches typos and stale key references that would silently
    produce None values.
    """
    schema_fields = _schema_all_field_names(record_type)
    decoder_keys = _extract_decoder_payload_keys(record_type)

    # Decoder may reference keys handled by _build_context or 'type'
    allowed = schema_fields | _CONTEXT_FIELDS | {"type"}

    extra = decoder_keys - allowed
    assert extra == set(), f"{record_type}: decoder references keys not in schema: {sorted(extra)}"


@pytest.mark.parametrize("record_type", _all_record_types())
def test_decoder_non_reserved_field_coverage_complete(record_type: str):
    """Decoder must cover all non-reserved schema fields."""
    schema_fields = _schema_all_field_names(record_type)
    decoder_keys = _extract_decoder_payload_keys(record_type)
    missing = schema_fields - decoder_keys - _CONTEXT_FIELDS - {"type"}
    assert missing == set(), f"{record_type}: decoder missing non-reserved fields: {sorted(missing)}"


# ---------------------------------------------------------------------------
# 3. C++ output contract tests (static analysis)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("record_type", _all_record_types())
def test_cpp_top_level_keys_match_schema(record_type: str):
    """C++ structured_data keys must be a subset of schema field names.

    Reserved fields and 'type' are excluded from the comparison.
    """
    cpp_keys = _extract_cpp_structured_data_keys(record_type)
    if cpp_keys is None:
        pytest.skip(f"C++ source not available for {record_type}")

    schema_fields = _schema_top_level_field_names(record_type)
    # Also allow reserved fields that schema intentionally excludes
    schemas = load_all_schemas()
    all_fields = resolve_fields(schemas[record_type])
    reserved = {f["name"] for f in all_fields if f.get("semantic_type") == "reserved"}
    allowed = schema_fields | reserved | {"type"}

    extra = cpp_keys - allowed
    assert extra == set(), f"{record_type}: C++ outputs keys not in schema: {sorted(extra)}"


@pytest.mark.parametrize("record_type", _all_record_types())
def test_cpp_all_output_keys_match_schema(record_type: str):
    """C++ parser output keys (including nested) must be in schema field names."""
    cpp_keys = _extract_cpp_output_keys(record_type)
    if cpp_keys is None:
        pytest.skip(f"C++ source not available for {record_type}")

    schema_fields = _schema_all_field_names(record_type, include_reserved=True)
    allowed = schema_fields | {"type"}

    extra = cpp_keys - allowed
    assert extra == set(), f"{record_type}: C++ outputs nested keys not in schema: {sorted(extra)}"


@pytest.mark.parametrize("record_type", _all_record_types())
def test_cpp_outputs_all_decoder_keys(record_type: str):
    """C++ parser must output every key actually consumed by the decoder."""
    cpp_keys = _extract_cpp_output_keys(record_type)
    if cpp_keys is None:
        pytest.skip(f"C++ source not available for {record_type}")

    decoder_keys = _extract_decoder_payload_keys(record_type)
    required = decoder_keys - _CONTEXT_FIELDS - {"type"}

    missing = required - cpp_keys
    assert missing == set(), f"{record_type}: C++ missing decoder-consumed keys: {sorted(missing)}"


# ---------------------------------------------------------------------------
# 4. Cross-layer consistency
# ---------------------------------------------------------------------------


def test_decoder_covers_all_record_types():
    """Every schema-defined record type must have a corresponding decoder."""
    source = DECODER_FILE.read_text(encoding="utf-8")
    for rt in _all_record_types():
        assert f"_decode_{rt.lower()}" in source, f"No decoder function found for record type {rt}"


def test_codegen_registry_matches_schemas():
    """The generated registry must list exactly the same record types as schemas."""
    from pyjvlink._internal.protocol.generated.registry import RECORD_TYPES

    schema_types = set(_all_record_types())
    assert schema_types == RECORD_TYPES, (
        f"Mismatch between schemas and registry. "
        f"Only in schemas: {schema_types - RECORD_TYPES}. "
        f"Only in registry: {RECORD_TYPES - schema_types}."
    )


# ---------------------------------------------------------------------------
# 5. Typed domain model contract tests
# ---------------------------------------------------------------------------


def _get_record_class(record_type: str):
    """Get the domain model class for a record type."""
    import pyjvlink._internal.domain.models as models_mod

    class_name = f"{record_type}Record"
    return getattr(models_mod, class_name, None)


def _schema_array_object_field_names(record_type: str) -> set[str]:
    """Return field names with semantic_type 'array:object' from schema."""
    schemas = load_all_schemas()
    fields = resolve_fields(schemas[record_type])
    return {f["name"] for f in fields if f.get("semantic_type") == "array:object"}


def _is_typed_dataclass_tuple(annotation) -> bool:
    """Check if annotation is tuple[SomeDataclass, ...]."""
    import dataclasses
    import typing

    origin = typing.get_origin(annotation)
    if origin is not tuple:
        return False
    args = typing.get_args(annotation)
    if len(args) != 2 or args[1] is not Ellipsis:
        return False
    return dataclasses.is_dataclass(args[0]) and isinstance(args[0], type)


def _array_object_field_coverage_gaps() -> dict[str, set[str]]:
    """Return missing array:object model fields by record type."""
    import typing

    gaps: dict[str, set[str]] = {}
    for record_type in _all_record_types():
        schema_ao_fields = _schema_array_object_field_names(record_type)
        if not schema_ao_fields:
            continue
        record_cls = _get_record_class(record_type)
        if record_cls is None:
            gaps[record_type] = schema_ao_fields
            continue
        hints = typing.get_type_hints(record_cls)
        missing = {field_name for field_name in schema_ao_fields if field_name not in hints}
        if missing:
            gaps[record_type] = missing
    return gaps


_KNOWN_ARRAY_OBJECT_GAPS: dict[str, frozenset[str]] = {}


def _typed_array_object_record_types() -> list[str]:
    """Records with array:object fields and no known model coverage gaps."""
    records: list[str] = []
    for record_type in _all_record_types():
        if not _schema_array_object_field_names(record_type):
            continue
        if record_type in _KNOWN_ARRAY_OBJECT_GAPS:
            continue
        records.append(record_type)
    return sorted(records)


def _find_forbidden_public_annotation(annotation) -> str | None:
    """Return forbidden container/type name if present in annotation tree."""
    import typing

    if annotation is typing.Any:
        return "Any"

    origin = typing.get_origin(annotation)
    if origin is dict:
        return "dict"
    if origin is list:
        return "list"

    for arg in typing.get_args(annotation):
        forbidden = _find_forbidden_public_annotation(arg)
        if forbidden is not None:
            return forbidden
    return None


def test_array_object_model_coverage_has_only_known_gaps():
    """array:object model-field gaps must match known debt exactly."""
    actual = {record_type: frozenset(fields) for record_type, fields in _array_object_field_coverage_gaps().items()}
    assert actual == _KNOWN_ARRAY_OBJECT_GAPS, (
        "Unexpected array:object model coverage gaps.\n"
        f"Expected: {dict(sorted(_KNOWN_ARRAY_OBJECT_GAPS.items()))}\n"
        f"Actual: {dict(sorted(actual.items()))}"
    )


@pytest.mark.parametrize("record_type", _typed_array_object_record_types())
def test_array_object_fields_are_typed_tuples(record_type: str):
    """Every array:object schema field on typed records must use tuple[Dataclass, ...]."""
    import typing

    schema_ao_fields = _schema_array_object_field_names(record_type)
    if not schema_ao_fields:
        pytest.skip(f"{record_type} has no array:object fields")

    record_cls = _get_record_class(record_type)
    assert record_cls is not None, f"No record class found for {record_type}"
    hints = typing.get_type_hints(record_cls)

    for field_name in schema_ao_fields:
        assert field_name in hints, f"{record_type}Record.{field_name}: array:object field missing from model"
        annotation = hints[field_name]
        assert _is_typed_dataclass_tuple(annotation), (
            f"{record_type}Record.{field_name}: expected tuple[Dataclass, ...], got {annotation}"
        )


@pytest.mark.parametrize("record_type", _all_record_types())
def test_public_types_no_bare_any_dict_list(record_type: str):
    """Public typed records must not contain bare Any, dict, or list annotations."""
    import typing

    record_cls = _get_record_class(record_type)
    assert record_cls is not None, f"No record class found for {record_type}"
    hints = typing.get_type_hints(record_cls)

    for field_name, annotation in hints.items():
        forbidden = _find_forbidden_public_annotation(annotation)
        assert forbidden is None, f"{record_type}Record.{field_name}: contains forbidden {forbidden}"


# ---------------------------------------------------------------------------
# 6. Schema validation negative tests
# ---------------------------------------------------------------------------


def test_invalid_schema_reports_errors():
    """validate_schema must detect invalid wire_type and missing key_fields."""
    bad_schema = {
        "record_type": "TEST",
        "title": "Test",
        "record_length": 100,
        "key_fields": ["nonexistent_field"],
        "fields": [
            {
                "name": "field1",
                "item_number": 2,
                "wire_type": "invalid",
                "semantic_type": "invalid_type",
                "byte_position": 3,
                "byte_size": 1,
            }
        ],
    }
    errors = validate_schema(bad_schema)
    assert len(errors) >= 2  # At least key_field error + wire_type/semantic_type errors


def test_common_fields_are_validated(monkeypatch: pytest.MonkeyPatch):
    """validate_schema must validate common_fields_ref fields too."""
    schema = {
        "record_type": "TEST",
        "title": "Test",
        "record_length": 100,
        "key_fields": [],
        "common_fields_ref": "../_common_race_fields.json",
        "fields": [],
    }

    monkeypatch.setattr(
        schema_loader_module,
        "load_common_fields",
        lambda: [{"name": "broken_common_field"}],
    )

    errors = validate_schema(schema)
    assert any("missing required keys" in error for error in errors)


# ---------------------------------------------------------------------------
# 7. Source suffix ban
# ---------------------------------------------------------------------------

# Entity-source suffixes that encode the origin table/record, not the meaning.
# e.g. `_ks` (jockey master), `_ch` (trainer master), `_bn` (owner master),
#      `_br` (breeder master), `_um` (horse master).
_SOURCE_SUFFIX_PATTERN = re.compile(r"_(?:ks|ch|bn|br|um)$")


@pytest.mark.parametrize("record_type", _all_record_types())
def test_schema_no_source_suffix(record_type: str):
    """Schema field names must not end with entity-source suffixes (_ks, _ch, _bn, _br, _um)."""
    all_names = _schema_all_field_names(record_type, include_reserved=False)
    violations = {name for name in all_names if _SOURCE_SUFFIX_PATTERN.search(name)}
    assert violations == set(), f"{record_type}: schema fields with forbidden source suffix: {sorted(violations)}"


# ---------------------------------------------------------------------------
# 8. Layout suffix ban
# ---------------------------------------------------------------------------

# Layout suffixes that encode digit counts or byte sizes into the name.
# e.g. `combination_number_2`, `combination_number_4`, `combination_number_6`.
_LAYOUT_SUFFIX_PATTERN = re.compile(r"_number_\d+$")


@pytest.mark.parametrize("record_type", _all_record_types())
def test_schema_no_layout_suffix(record_type: str):
    """Schema field names must not encode digit counts (e.g. combination_number_6)."""
    all_names = _schema_all_field_names(record_type, include_reserved=False)
    violations = {name for name in all_names if _LAYOUT_SUFFIX_PATTERN.search(name)}
    assert violations == set(), f"{record_type}: schema fields with forbidden layout suffix: {sorted(violations)}"


# ---------------------------------------------------------------------------
# 8b. No _category suffix in schema field names
# ---------------------------------------------------------------------------

# The `_category` suffix is a legacy anti-pattern.  All JV-Link "区分"
# fields must use `_code` instead (e.g. `data_code`, `sex_code`).
_CATEGORY_SUFFIX_PATTERN = re.compile(r"_category$")


@pytest.mark.parametrize("record_type", _all_record_types())
def test_schema_no_category_suffix(record_type: str):
    """Schema field names must not use _category suffix; use _code instead."""
    all_names = _schema_all_field_names(record_type, include_reserved=False)
    violations = {name for name in all_names if _CATEGORY_SUFFIX_PATTERN.search(name)}
    assert violations == set(), f"{record_type}: schema fields with forbidden _category suffix: {sorted(violations)}"


# ---------------------------------------------------------------------------
# 9. Scope purity (MeetRecordBase vs RaceRecordBase)
# ---------------------------------------------------------------------------

# Records that are meet-scoped (no race_number in schema).
# These must use MeetRecordBase, not RaceRecordBase.
_MEET_SCOPE_RECORDS = frozenset({"WE"})


@pytest.mark.parametrize("record_type", sorted(_MEET_SCOPE_RECORDS))
def test_meet_scope_record_uses_meet_base(record_type: str):
    """Meet-scoped records must inherit from MeetRecordBase, not RaceRecordBase."""
    from pyjvlink._internal.domain.models.common import MeetRecordBase, RaceRecordBase

    record_cls = _get_record_class(record_type)
    assert record_cls is not None, f"No record class for {record_type}"
    assert issubclass(record_cls, MeetRecordBase), f"{record_type}Record must inherit from MeetRecordBase"
    assert not issubclass(record_cls, RaceRecordBase), f"{record_type}Record must NOT inherit from RaceRecordBase"


@pytest.mark.parametrize("record_type", sorted(_MEET_SCOPE_RECORDS))
def test_meet_scope_record_has_no_race_number(record_type: str):
    """Meet-scoped records must not have race_number field."""
    import typing

    record_cls = _get_record_class(record_type)
    assert record_cls is not None
    hints = typing.get_type_hints(record_cls)
    assert "race_number" not in hints, f"{record_type}Record should not have race_number (meet-scoped)"
    assert "race_id" not in hints, f"{record_type}Record should not have race_id (meet-scoped)"
