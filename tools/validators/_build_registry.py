#!/usr/bin/env python3

import os
import sys
import json
import argparse
from pathlib import Path

def extract_version(filename):
    # Example: v1.0.0.master.schema.json → 1.0.0
    name = Path(filename).name
    if name.startswith("v") and "." in name:
        return name.split(".", 3)[0][1:]
    return None

def build_registry(schema_root):
    registry = {
        "master": {},
        "shared": {},
        "upos": {}
    }

    for path in Path(schema_root).rglob("v*.schema.json"):
        version = extract_version(path.name)
        if not version:
            continue

        parts = path.parts
        # parts example: ['schemas', 'shared', 'metadata', 'v1.0.0.metadata.schema.json']

        if "master" in parts:
            registry["master"].setdefault("versions", {})[version] = str(path)
            registry["master"]["default"] = version

        elif "shared" in parts:
            family = parts[2]
            registry["shared"].setdefault(family, {"versions": {}})
            registry["shared"][family]["versions"][version] = str(path)
            registry["shared"][family]["default"] = version

        elif "upos" in parts:
            family = parts[2]
            registry["upos"].setdefault(family, {"versions": {}})
            registry["upos"][family]["versions"][version] = str(path)
            registry["upos"][family]["default"] = version

    return registry

def main():
    parser = argparse.ArgumentParser(description="Build OpenUniLex schema registry")
    parser.add_argument("--schemas", required=True)
    args = parser.parse_args()

    registry = build_registry(args.schemas)

    output_path = Path(args.schemas) / "index.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    print(f"Registry written to {output_path}")

if __name__ == "__main__":
    main()
