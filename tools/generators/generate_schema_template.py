import json
from pathlib import Path
import os
import sys
import argparse
import yaml
from typing import Any, Dict, List

PROJECT_BASE = Path(__file__).resolve().parent.parent.parent
SCHEMAS = PROJECT_BASE / "schemas"

# UPOS routing mapping based on your structure
UPOS_ROUTING = {
    "functional": ["PRON", "DET", "NUM", "ADP"],
    "grammar_glue": ["PART", "AUX", "CCONJ", "SCONJ", "INTJ"],
    "modifier": ["ADJ", "ADV"],
    "noun": ["NOUN", "PROPN"],
    "verb": ["VERB"],
    "structural_void": ["PUNCT", "SYM", "X"]
}

# Reverse mapping for lookup
UPOS_TO_SCHEMA = {}
for schema_name, upos_list in UPOS_ROUTING.items():
    for upos in upos_list:
        UPOS_TO_SCHEMA[upos] = schema_name

VALID_UPOS = list(UPOS_TO_SCHEMA.keys())

def map_url_to_local_path(url):
    """Map a URL like https://OpenUniLex.org/schemas/... to local file path."""
    if url.startswith("https://OpenUniLex.org/"):
        local_path = url.replace("https://OpenUniLex.org/", "")
    elif url.startswith("http://OpenUniLex.org/"):
        local_path = url.replace("http://OpenUniLex.org/", "")
    else:
        return None
    
    if "#" in local_path:
        local_path = local_path.split("#")[0]
    
    full_path = PROJECT_BASE / local_path
    
    if not full_path.exists():
        path_parts = local_path.split("/")
        for i in range(len(path_parts)):
            test_path = PROJECT_BASE / "/".join(path_parts[i:])
            if test_path.exists():
                return test_path
        
        if local_path.startswith("schemas/"):
            test_path = SCHEMAS / local_path.replace("schemas/", "", 1)
            if test_path.exists():
                return test_path
        
        filename = Path(local_path).name
        for root, dirs, files in os.walk(SCHEMAS):
            if filename in files:
                return Path(root) / filename
    
    return full_path if full_path.exists() else None

def load_json(path):
    """Load JSON from a file path."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        raise

def get_schema_from_ref(ref_path):
    """Get schema from a $ref reference, handling both URLs and local paths."""
    fragment = None
    if "#" in ref_path:
        ref_path, fragment = ref_path.split("#", 1)
        fragment = "#" + fragment
    
    if ref_path.startswith("http://") or ref_path.startswith("https://"):
        local_path = map_url_to_local_path(ref_path)
        if local_path is None or not local_path.exists():
            return None
        schema = load_json(local_path)
    else:
        local_path = Path(ref_path)
        if not local_path.exists():
            local_path = SCHEMAS / ref_path
            if not local_path.exists():
                return None
        schema = load_json(local_path)
    
    if fragment:
        parts = fragment.lstrip("#").split("/")
        for part in parts:
            if part:
                if part in schema:
                    schema = schema[part]
                else:
                    return None
    
    return schema

def resolve_schema(schema, visited=None):
    """Resolve all $refs in a schema and return the complete schema."""
    if visited is None:
        visited = set()
    
    schema_id = str(id(schema))
    if schema_id in visited:
        return schema
    
    visited.add(schema_id)
    resolved = {}
    
    # Handle $ref at root
    if "$ref" in schema:
        ref_schema = get_schema_from_ref(schema["$ref"])
        if ref_schema:
            resolved.update(resolve_schema(ref_schema, visited))
    
    # Copy other properties
    for key, value in schema.items():
        if key == "$ref":
            continue
        if isinstance(value, dict):
            if "$ref" in value:
                ref_schema = get_schema_from_ref(value["$ref"])
                if ref_schema:
                    resolved[key] = resolve_schema(ref_schema, visited)
                else:
                    resolved[key] = value
            else:
                resolved[key] = resolve_schema(value, visited)
        elif isinstance(value, list):
            resolved[key] = [resolve_schema(item, visited) if isinstance(item, dict) else item for item in value]
        else:
            resolved[key] = value
    
    return resolved

def create_template_from_schema(schema, required_fields=None, include_examples=True):
    """Create a template instance from a schema."""
    if required_fields is None:
        required_fields = set()
    
    template = {}
    
    # Handle properties
    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            is_required = prop_name in schema.get("required", []) or prop_name in required_fields
            
            # Get default value or example
            if include_examples:
                if "examples" in prop_schema and prop_schema["examples"]:
                    template[prop_name] = prop_schema["examples"][0]
                    continue
                elif "default" in prop_schema:
                    template[prop_name] = prop_schema["default"]
                    continue
            
            # Generate based on type
            prop_type = prop_schema.get("type")
            
            if "$ref" in prop_schema:
                ref_schema = get_schema_from_ref(prop_schema["$ref"])
                if ref_schema:
                    template[prop_name] = create_template_from_schema(
                        ref_schema, 
                        set(ref_schema.get("required", [])),
                        include_examples
                    )
                else:
                    template[prop_name] = {}
            elif prop_type == "object":
                template[prop_name] = create_template_from_schema(
                    prop_schema,
                    set(prop_schema.get("required", [])),
                    include_examples
                )
            elif prop_type == "array":
                if "items" in prop_schema:
                    items_schema = prop_schema["items"]
                    if "$ref" in items_schema:
                        ref_schema = get_schema_from_ref(items_schema["$ref"])
                        if ref_schema:
                            template[prop_name] = [create_template_from_schema(
                                ref_schema,
                                set(ref_schema.get("required", [])),
                                include_examples
                            )]
                        else:
                            template[prop_name] = []
                    elif "properties" in items_schema:
                        template[prop_name] = [create_template_from_schema(
                            items_schema,
                            set(items_schema.get("required", [])),
                            include_examples
                        )]
                    else:
                        # Simple array items
                        item_type = items_schema.get("type", "string")
                        if item_type == "string":
                            template[prop_name] = ["example"]
                        elif item_type == "integer":
                            template[prop_name] = [0]
                        elif item_type == "number":
                            template[prop_name] = [0.0]
                        elif item_type == "boolean":
                            template[prop_name] = [True]
                        else:
                            template[prop_name] = []
                else:
                    template[prop_name] = []
            elif prop_type == "string":
                if "enum" in prop_schema and prop_schema["enum"]:
                    template[prop_name] = prop_schema["enum"][0]
                else:
                    template[prop_name] = ""
            elif prop_type == "integer":
                template[prop_name] = 0
            elif prop_type == "number":
                template[prop_name] = 0.0
            elif prop_type == "boolean":
                template[prop_name] = False
            elif prop_type == "null":
                template[prop_name] = None
            else:
                template[prop_name] = {}
    
    return template

def generate_upos_template(upos_type, format="json", include_examples=True):
    """Generate a complete template for a UPOS type."""
    try:
        # Load schemas
        master_schema = load_json(SCHEMAS / "master" / "v1.0.0.master.schema.json")
        upos_schema, upos_path = load_upos_schema(upos_type)
        schema_name = UPOS_TO_SCHEMA.get(upos_type)
        
        # Resolve all references
        resolved_master = resolve_schema(master_schema)
        resolved_upos = resolve_schema(upos_schema)
        
        # Create template
        template = {}
        
        # Add master properties
        if "properties" in resolved_master:
            master_required = set(resolved_master.get("required", []))
            for prop_name, prop_schema in resolved_master["properties"].items():
                # Skip pos_payload as we'll handle it separately
                if prop_name == "pos_payload":
                    continue
                is_required = prop_name in master_required
                if is_required or include_examples:
                    template[prop_name] = create_template_from_schema(
                        {"properties": {prop_name: prop_schema}},
                        master_required if is_required else set(),
                        include_examples
                    ).get(prop_name)
        
        # Add pos_payload from UPOS schema
        if "properties" in resolved_upos and "pos_payload" in resolved_upos["properties"]:
            pos_payload_schema = resolved_upos["properties"]["pos_payload"]
            template["pos_payload"] = create_template_from_schema(
                pos_payload_schema,
                set(pos_payload_schema.get("required", [])),
                include_examples
            )
        
        # Add comments/documentation
        result = {
            "$schema": "https://OpenUniLex.org/schemas/master/v1.0.0.master.schema.json",
            "$comment": f"Template for {upos_type} entries",
            "upos": upos_type,
            **template
        }
        
        # Format output
        if format.lower() == "yaml":
            return yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)
        else:
            return json.dumps(result, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error generating template for {upos_type}: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_upos_schema(upos_type):
    """Load the schema for a given UPOS type."""
    schema_name = UPOS_TO_SCHEMA.get(upos_type)
    if not schema_name:
        raise ValueError(f"Unknown UPOS type: {upos_type}")
    
    schema_path = SCHEMAS / "upos" / schema_name / f"v1.0.0.{schema_name}.schema.json"
    
    if not schema_path.exists():
        alt_path = SCHEMAS / "upos" / schema_name / f"{schema_name}.schema.json"
        if alt_path.exists():
            schema_path = alt_path
        else:
            raise FileNotFoundError(f"Schema not found: {schema_path} or {alt_path}")
    
    schema = load_json(schema_path)
    return schema, schema_path

def print_upos_properties(upos_type, verbose=False):
    """Print all properties for a given UPOS type."""
    try:
        master_schema = load_json(SCHEMAS / "master" / "v1.0.0.master.schema.json")
        upos_schema, upos_path = load_upos_schema(upos_type)
        schema_name = UPOS_TO_SCHEMA.get(upos_type)
        
        if verbose:
            print(f"\n--- Master Schema: {SCHEMAS / 'master' / 'v1.0.0.master.schema.json'} ---")
            print(f"--- UPOS Schema: {upos_path} ---")
            print(f"Schema name: {schema_name}")
            print(f"UPOS types using this schema: {UPOS_ROUTING[schema_name]}")
        
        # Collect properties from both schemas
        master_props = {}
        if "properties" in master_schema:
            for name, details in master_schema["properties"].items():
                if name != "pos_payload":  # Skip pos_payload as it's handled by UPOS schema
                    master_props[name] = details
        
        print(f"\n=== FULL PROPERTY SET FOR {upos_type.upper()} ===")
        print(f"(Using UPOS schema: {schema_name})")
        
        # Print top-level properties
        print(f"\n--- TOP-LEVEL PROPERTIES ---")
        master_required = set(master_schema.get("required", []))
        for name, details in master_props.items():
            required = " [REQUIRED]" if name in master_required else ""
            if "$ref" in details:
                print(f"• {name}: ref{required}")
            else:
                t = details.get("type", "unknown")
                enum = details.get("enum", [])
                enum_str = f" (values: {', '.join(enum)})" if enum else ""
                print(f"• {name}: {t}{required}{enum_str}")
        
        # Print pos_payload properties
        print(f"\n--- POS_PAYLOAD PROPERTIES ---")
        if "properties" in upos_schema and "pos_payload" in upos_schema["properties"]:
            pos_payload = upos_schema["properties"]["pos_payload"]
            if "properties" in pos_payload:
                for name, details in pos_payload["properties"].items():
                    required = " [REQUIRED]" if name in pos_payload.get("required", []) else ""
                    if "$ref" in details:
                        print(f"• {name}: object{required}")
                        ref_schema = get_schema_from_ref(details["$ref"])
                        if ref_schema and "properties" in ref_schema:
                            for nested_name, nested_details in ref_schema["properties"].items():
                                nested_required = " [REQUIRED]" if nested_name in ref_schema.get("required", []) else ""
                                nested_type = nested_details.get("type", "unknown")
                                enum = nested_details.get("enum", [])
                                enum_str = f" (values: {', '.join(enum)})" if enum else ""
                                print(f"  - {nested_name}: {nested_type}{nested_required}{enum_str}")
                    else:
                        t = details.get("type", "unknown")
                        enum = details.get("enum", [])
                        enum_str = f" (values: {', '.join(enum)})" if enum else ""
                        print(f"• {name}: {t}{required}{enum_str}")
        
    except Exception as e:
        print(f"Error processing {upos_type}: {e}")
        if verbose:
            import traceback
            traceback.print_exc()

def print_all_upos_mapping():
    """Print the UPOS to schema mapping."""
    print("\n=== UPOS TO SCHEMA MAPPING ===")
    for schema_name, upos_list in UPOS_ROUTING.items():
        print(f"{schema_name}: {', '.join(upos_list)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate UPOS schema templates")
    parser.add_argument("--upos", help="UPOS type to inspect or generate template for")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    parser.add_argument("--list", action="store_true", help="List all UPOS to schema mappings")
    parser.add_argument("--template", action="store_true", help="Generate a complete template")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format for template")
    parser.add_argument("--no-examples", action="store_true", help="Don't include example values in template")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    args = parser.parse_args()
    
    if args.list:
        print_all_upos_mapping()
        sys.exit(0)
    
    upos = args.upos or os.getenv("UPOS")
    
    if args.debug:
        print(f"PROJECT_BASE: {PROJECT_BASE}")
        print(f"SCHEMAS: {SCHEMAS}")
        print(f"UPOS routing: {UPOS_ROUTING}")
    
    if args.template:
        if not upos:
            print("Error: --upos is required when using --template")
            sys.exit(1)
        
        upos = upos.upper()
        if upos not in VALID_UPOS:
            print(f"Invalid UPOS type: {upos}")
            print(f"Valid types: {', '.join(VALID_UPOS)}")
            sys.exit(1)
        
        template = generate_upos_template(
            upos, 
            format=args.format,
            include_examples=not args.no_examples
        )
        
        if template:
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(template)
                print(f"Template saved to: {args.output}")
            else:
                print(template)
    else:
        if args.debug:
            print(f"Valid UPOS types: {VALID_UPOS}")
        
        if upos:
            upos = upos.upper()
            if upos not in VALID_UPOS:
                print(f"Invalid UPOS type: {upos}")
                print(f"Valid types: {', '.join(VALID_UPOS)}")
                sys.exit(1)
            print_upos_properties(upos, verbose=args.verbose)
        else:
            print("\nNo UPOS type specified. Showing all:")
            for u in VALID_UPOS:
                print_upos_properties(u, verbose=args.verbose)

# # Generate JSON template:                
# python3 tools/generators/generate_schema_template.py --upos NOUN --template
# # Generate YAML template:
# python3 tools/generators/generate_schema_template.py --upos NOUN --template --format yaml
# # Save to a file:
# python3 tools/generators/generate_schema_template.py --upos NOUN --template --output noun_template.json
# # Generate without example values (just structure):
# python3 tools/generators/generate_schema_template.py --upos NOUN --template --no-examples
