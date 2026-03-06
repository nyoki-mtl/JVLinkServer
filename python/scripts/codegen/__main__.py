"""Code generation entry point.

Usage:
    cd python && uv run python -m scripts.codegen
"""

from __future__ import annotations

import sys
from pathlib import Path

from .gen_field_tables import generate_field_tables
from .gen_formatter_meta import generate_formatter_meta
from .gen_registry import generate_registry
from .schema_loader import validate_all

# Output directories
PYJVLINK_DIR = Path(__file__).resolve().parents[2] / "src" / "pyjvlink"
GENERATED_DIR = PYJVLINK_DIR / "_internal" / "protocol" / "generated"
FIELD_TABLES_DIR = PYJVLINK_DIR / "_internal" / "protocol" / "schema" / "domain"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  OK: {path.relative_to(PYJVLINK_DIR.parent.parent)}")


def main() -> int:
    # Step 1: Validate schemas
    print("Validating schemas...")
    errors = validate_all()
    if errors:
        print("Schema validation FAILED:")
        for e in errors:
            print(f"  {e}")
        return 1
    print("  All schemas valid.")

    # Step 2: Generate formatter metadata
    print("Generating formatter metadata...")
    _write(GENERATED_DIR / "formatter_meta.py", generate_formatter_meta())

    # Step 3: Generate registry
    print("Generating registry...")
    _write(GENERATED_DIR / "registry.py", generate_registry())

    # Step 4: Generate field tables
    print("Generating field tables...")
    tables = generate_field_tables()
    for rt, content in tables.items():
        _write(FIELD_TABLES_DIR / f"{rt.lower()}.md", content)

    print(f"Done. Generated {2 + len(tables)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
