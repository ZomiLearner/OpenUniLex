#!/usr/bin/env python3

"""
OpenUniLex schema + lexeme validator.

Uses referencing.Registry (Draft 2020-12) instead of RefResolver.
Registry is built dynamically from the schemas directory.
"""

import json
import yaml
import argparse
from pathlib import Path
from referencing import Registry, Resource
from jsonschema import Draft202012Validator


# ============================================================
# Build full schema registry (OpenUniLex version)
# ============================================================

def build_registry(root: Path) -> Registry:
    registry = Registry()

    for path in root.rglob("*"):
        if path.suffix not in [".json", ".yaml", ".yml"]:
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                schema = json.load(f) if path.suffix == ".json" else yaml.safe_load(f)
        except Exception:
            continue

        if not isinstance(schema, dict):
            continue

        # Only load actual schemas
        if "$id" not in schema and "$schema" not in schema:
            continue

        # Canonical URI for OpenUniLex
        rel = path.relative_to(root).as_posix()
        canonical_uri = f"https://OpenUniLex.org/schemas/{rel}"

        registry = registry.with_resource(
            uri=canonical_uri,
            resource=Resource.from_contents(schema)
        )

    return registry


# ============================================================
# Load registry index.json
# ============================================================

def load_registry_index(schema_root: Path):
    index_path = schema_root / "index.json"
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Schema validation
# ============================================================

def validate_schema(schema_path: Path, registry: Registry):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validator = Draft202012Validator(schema, registry=registry)
    validator.check_schema(schema)


# ============================================================
# Lexeme validation
# ============================================================

def validate_lexeme(lexeme_path: Path, master_schema_path: Path, registry: Registry):
    with open(lexeme_path, "r", encoding="utf-8") as f:
        entry = json.load(f)

    with open(master_schema_path, "r", encoding="utf-8") as f:
        master_schema = json.load(f)

    validator = Draft202012Validator(master_schema, registry=registry)
    validator.validate(entry)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="OpenUniLex Validator")
    parser.add_argument("--schemas", help="Validate schema files")
    parser.add_argument("--lexicons", help="Validate lexeme files")
    args = parser.parse_args()

    schema_root = Path("schemas").resolve()
    registry = build_registry(schema_root)
    index = load_registry_index(schema_root)

    master_version = index["master"]["default"]
    master_schema_path = Path(index["master"]["versions"][master_version]).resolve()

    # Validate schemas
    if args.schemas:
        print("Validating schemas...")
        for schema_file in Path(args.schemas).rglob("*.json"):
            try:
                validate_schema(schema_file, registry)
                print(f"[OK] {schema_file}")
            except Exception as e:
                print(f"[ERROR] {schema_file}: {e}")
                exit(1)

    # Validate lexemes
    if args.lexicons:
        print("Validating lexemes...")
        for lexeme_file in Path(args.lexicons).rglob("*.json"):
            try:
                validate_lexeme(lexeme_file, master_schema_path, registry)
                print(f"[OK] {lexeme_file}")
            except Exception as e:
                print(f"[ERROR] {lexeme_file}: {e}")
                exit(1)

    print("Validation complete.")


if __name__ == "__main__":
    main()
