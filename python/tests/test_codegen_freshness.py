"""Tests that generated files are in sync with schemas.

If any of these tests fail, run `make codegen` to regenerate.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from codegen.gen_formatter_meta import generate_formatter_meta
from codegen.gen_registry import generate_registry

GENERATED_DIR = Path(__file__).resolve().parents[1] / "src" / "pyjvlink" / "_internal" / "protocol" / "generated"

STALE_MSG = "Generated file is stale. Run 'make codegen' to regenerate."


@pytest.mark.parametrize(
    ("filename", "generator"),
    [
        ("formatter_meta.py", generate_formatter_meta),
        ("registry.py", generate_registry),
    ],
)
def test_generated_file_is_fresh(filename: str, generator):
    path = GENERATED_DIR / filename
    assert path.exists(), f"{path} does not exist. Run 'make codegen' to generate."
    actual = path.read_text(encoding="utf-8")
    expected = generator()
    assert actual == expected, f"{filename}: {STALE_MSG}"
