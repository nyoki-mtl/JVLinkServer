"""Generate record field tables as Markdown from record schemas.

Output: python/src/pyjvlink/protocol/schema/domain/{record_type}.md
"""

from __future__ import annotations

from typing import Any

from .schema_loader import load_all_schemas, resolve_fields


def _generate_table(record_type: str, schema: dict[str, Any]) -> str:
    """Generate a Markdown field table for a single record type."""
    all_fields = resolve_fields(schema)
    title = schema["title"]
    record_length = schema["record_length"]
    key_fields = set(schema["key_fields"])

    lines: list[str] = []
    lines.append(f"# {record_type} - {title}")
    lines.append("")
    lines.append(f"レコード長: {record_length} バイト")
    lines.append("")
    lines.append("| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |")
    lines.append("|---:|---|---|---:|---:|---|---|")

    for field in all_fields:
        item = field["item_number"]
        name = field["name"]
        st = field["semantic_type"]
        pos = field["byte_position"]
        size = field["byte_size"]
        label = field.get("display", {}).get("label", "")
        is_key = "KEY" if name in key_fields or field.get("is_key") else ""

        if st == "array:object":
            info = field.get("array_info", {})
            count = info.get("count", "?")
            st_display = f"array:object[{count}]"
        elif st.startswith("array:"):
            info = field.get("array_info", {})
            count = info.get("count", "?")
            st_display = f"{st}[{count}]"
        else:
            st_display = st

        lines.append(f"| {item} | `{name}` | {st_display} | {pos} | {size} | {label} | {is_key} |")

        # Sub-fields for array:object
        if st == "array:object" and "element_fields" in field:
            for ef in field["element_fields"]:
                ef_name = ef["name"]
                ef_st = ef["semantic_type"]
                ef_offset = ef["byte_offset"]
                ef_size = ef["byte_size"]
                ef_label = ef.get("display", {}).get("label", "")
                lines.append(f"|  | `  .{ef_name}` | {ef_st} | +{ef_offset} | {ef_size} | {ef_label} |  |")

    lines.append("")
    return "\n".join(lines)


def generate_field_tables() -> dict[str, str]:
    """Generate field tables for all record types. Returns {record_type: markdown_content}."""
    schemas = load_all_schemas()
    tables: dict[str, str] = {}
    for rt, schema in sorted(schemas.items()):
        tables[rt] = _generate_table(rt, schema)
    return tables
