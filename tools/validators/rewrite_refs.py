#!/usr/bin/env python3

import json
import argparse
from pathlib import Path

CANONICAL_BASE = "https://OpenUniLex.org/schemas"

def rewrite_refs_in_schema(schema: dict, file_path: Path, root: Path):
    """
    Recursively rewrite all $ref values inside a schema dict.
    """
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == "$ref" and isinstance(value, str):
                # Compute canonical URI
                # Convert relative path → canonical URI
                rel = (file_path.parent / value).resolve().relative_to(root).as_posix()
                schema[key] = f"{CANONICAL_BASE}/{rel}"
            else:
                rewrite_refs_in_schema(value, file_path, root)

    elif isinstance(schema, list):
        for item in schema:
            rewrite_refs_in_schema(item, file_path, root)


def process_schema_file(path: Path, root: Path):
    """
    Load → rewrite → save schema file.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except Exception:
        return

    rewrite_refs_in_schema(schema, path, root)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"[UPDATED] {path}")


def main():
    parser = argparse.ArgumentParser(description="Rewrite all $ref paths to canonical URIs")
    parser.add_argument("--schemas", required=True)
    args = parser.parse_args()

    root = Path(args.schemas).resolve()

    for path in root.rglob("*.json"):
        process_schema_file(path, root)

    print("All $ref paths rewritten to canonical OpenUniLex URIs.")


if __name__ == "__main__":
    main()

# python3 tools/validators/rewrite_refs.py --schemas schemas
# Run it once, and it will rewrite all $ref paths in place.