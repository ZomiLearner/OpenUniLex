# import json
# from pathlib import Path
# import os
# import sys
# import argparse

# PROJECT_BASE = Path(__file__).resolve().parent.parent.parent
# SCHEMAS = PROJECT_BASE / "schemas"

# # UPOS routing mapping based on your structure
# UPOS_ROUTING = {
#     "functional": ["PRON", "DET", "NUM", "ADP"],
#     "grammar_glue": ["PART", "AUX", "CCONJ", "SCONJ", "INTJ"],
#     "modifier": ["ADJ", "ADV"],
#     "noun": ["NOUN", "PROPN"],
#     "verb": ["VERB"],
#     "structural_void": ["PUNCT", "SYM", "X"]
# }

# # Reverse mapping for lookup
# UPOS_TO_SCHEMA = {}
# for schema_name, upos_list in UPOS_ROUTING.items():
#     for upos in upos_list:
#         UPOS_TO_SCHEMA[upos] = schema_name

# # Valid UPOS types for the script
# VALID_UPOS = list(UPOS_TO_SCHEMA.keys())

# def map_url_to_local_path(url):
#     """Map a URL like https://OpenUniLex.org/schemas/... to local file path."""
#     # Remove protocol and domain
#     if url.startswith("https://OpenUniLex.org/"):
#         local_path = url.replace("https://OpenUniLex.org/", "")
#     elif url.startswith("http://OpenUniLex.org/"):
#         local_path = url.replace("http://OpenUniLex.org/", "")
#     else:
#         return None
    
#     # Remove fragment if present (e.g., #/properties/noun)
#     if "#" in local_path:
#         local_path = local_path.split("#")[0]
    
#     # Construct the full local path - relative to project root
#     full_path = PROJECT_BASE / local_path
    
#     # If the file doesn't exist, try some alternative paths
#     if not full_path.exists():
#         # Try removing any leading paths that might be causing issues
#         path_parts = local_path.split("/")
        
#         # Try various combinations
#         for i in range(len(path_parts)):
#             test_path = PROJECT_BASE / "/".join(path_parts[i:])
#             if test_path.exists():
#                 return test_path
        
#         # Try relative to schemas directory
#         if local_path.startswith("schemas/"):
#             test_path = SCHEMAS / local_path.replace("schemas/", "", 1)
#             if test_path.exists():
#                 return test_path
        
#         # Last resort: search by filename
#         filename = Path(local_path).name
#         for root, dirs, files in os.walk(SCHEMAS):
#             if filename in files:
#                 return Path(root) / filename
    
#     return full_path if full_path.exists() else None

# def load_json(path):
#     """Load JSON from a file path."""
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"Error: Schema file not found: {path}")
#         raise
#     except json.JSONDecodeError as e:
#         print(f"Error: Invalid JSON in {path}: {e}")
#         raise

# def get_schema_from_ref(ref_path):
#     """Get schema from a $ref reference, handling both URLs and local paths."""
#     # Extract fragment if present
#     fragment = None
#     if "#" in ref_path:
#         ref_path, fragment = ref_path.split("#", 1)
#         fragment = "#" + fragment
    
#     # Map URL to local path if needed
#     if ref_path.startswith("http://") or ref_path.startswith("https://"):
#         local_path = map_url_to_local_path(ref_path)
#         if local_path is None:
#             print(f"Warning: Could not map URL to local path: {ref_path}")
#             return None
#         if not local_path.exists():
#             print(f"Warning: Mapped path does not exist: {local_path}")
#             return None
#         schema = load_json(local_path)
#     else:
#         # Local file path
#         local_path = Path(ref_path)
#         if not local_path.exists():
#             # Try relative to schemas
#             local_path = SCHEMAS / ref_path
#             if not local_path.exists():
#                 print(f"Warning: File not found: {ref_path}")
#                 return None
#         schema = load_json(local_path)
    
#     # Navigate to fragment if present
#     if fragment:
#         parts = fragment.lstrip("#").split("/")
#         for part in parts:
#             if part:  # Skip empty parts
#                 if part in schema:
#                     schema = schema[part]
#                 else:
#                     print(f"Warning: Fragment path '{fragment}' not found in schema")
#                     return None
    
#     return schema

# def collect_all_properties(schema, path_parts=None, visited=None):
#     """Collect all properties from a schema, handling nested structures."""
#     if path_parts is None:
#         path_parts = []
#     if visited is None:
#         visited = set()
    
#     # Create a unique identifier to avoid circular references
#     schema_id = str(id(schema))
#     if schema_id in visited:
#         return {}
    
#     visited.add(schema_id)
    
#     props = {}
    
#     # If schema has a $ref, resolve it
#     if "$ref" in schema:
#         ref_schema = get_schema_from_ref(schema["$ref"])
#         if ref_schema:
#             # If the ref schema has properties, collect them
#             if "properties" in ref_schema:
#                 for prop_name, prop_schema in ref_schema["properties"].items():
#                     props[prop_name] = prop_schema
#             # Also check for nested properties
#             nested_props = collect_all_properties(ref_schema, path_parts, visited)
#             props.update(nested_props)
    
#     # If schema has properties, collect them
#     if "properties" in schema:
#         for prop_name, prop_schema in schema["properties"].items():
#             # If the property has a $ref, resolve it
#             if "$ref" in prop_schema:
#                 ref_schema = get_schema_from_ref(prop_schema["$ref"])
#                 if ref_schema:
#                     # If the resolved schema has properties, add them
#                     if "properties" in ref_schema:
#                         for nested_name, nested_schema in ref_schema["properties"].items():
#                             props[nested_name] = nested_schema
#                     else:
#                         # Store the resolved schema as the property
#                         props[prop_name] = ref_schema
#             else:
#                 # Store the property directly
#                 props[prop_name] = prop_schema
            
#             # Recursively check for nested properties
#             nested_props = collect_all_properties(prop_schema, path_parts + [prop_name], visited)
#             props.update(nested_props)
    
#     # Handle allOf references
#     for item in schema.get("allOf", []):
#         if "$ref" in item:
#             ref_schema = get_schema_from_ref(item["$ref"])
#             if ref_schema:
#                 nested_props = collect_all_properties(ref_schema, path_parts, visited)
#                 props.update(nested_props)
#         elif "properties" in item:
#             nested_props = collect_all_properties(item, path_parts, visited)
#             props.update(nested_props)
    
#     # Handle items in arrays
#     if "items" in schema:
#         if "$ref" in schema["items"]:
#             ref_schema = get_schema_from_ref(schema["items"]["$ref"])
#             if ref_schema:
#                 nested_props = collect_all_properties(ref_schema, path_parts, visited)
#                 props.update(nested_props)
#         elif "properties" in schema["items"]:
#             nested_props = collect_all_properties(schema["items"], path_parts, visited)
#             props.update(nested_props)
    
#     return props

# def load_upos_schema(upos_type):
#     """Load the schema for a given UPOS type."""
#     # Get the schema name from the routing
#     schema_name = UPOS_TO_SCHEMA.get(upos_type)
#     if not schema_name:
#         raise ValueError(f"Unknown UPOS type: {upos_type}")
    
#     # Construct the path to the schema file
#     schema_path = SCHEMAS / "upos" / schema_name / f"v1.0.0.{schema_name}.schema.json"
    
#     if not schema_path.exists():
#         # Try alternative naming (some might have different names)
#         alt_path = SCHEMAS / "upos" / schema_name / f"{schema_name}.schema.json"
#         if alt_path.exists():
#             schema_path = alt_path
#         else:
#             raise FileNotFoundError(f"Schema not found: {schema_path} or {alt_path}")
    
#     schema = load_json(schema_path)
#     return schema, schema_path

# def print_upos_properties(upos_type, verbose=False):
#     """Print all properties for a given UPOS type."""
#     try:
#         schema, schema_path = load_upos_schema(upos_type)
#         schema_name = UPOS_TO_SCHEMA.get(upos_type)
        
#         if verbose:
#             print(f"\n--- Schema: {schema_path} ---")
#             print(f"Schema name: {schema_name}")
#             print(f"UPOS types using this schema: {UPOS_ROUTING[schema_name]}")
#             print(f"Schema keys: {list(schema.keys())}")
#             if "properties" in schema:
#                 print(f"Root properties: {list(schema['properties'].keys())}")
        
#         # Collect all properties from the schema
#         props = collect_all_properties(schema)
        
#         print(f"\n=== FULL PROPERTY SET FOR {upos_type.upper()} ===")
#         print(f"(Using schema: {schema_name})")
        
#         # Check for nested properties in pos_payload
#         if "properties" in schema and "pos_payload" in schema["properties"]:
#             pos_payload = schema["properties"]["pos_payload"]
#             if "properties" in pos_payload:
#                 print(f"\nProperties within pos_payload:")
#                 for name, details in pos_payload["properties"].items():
#                     t = details.get("type", "unknown")
#                     required = " [REQUIRED]" if name in pos_payload.get("required", []) else ""
                    
#                     # Check if it's a $ref
#                     if "$ref" in details:
#                         print(f"• {name}: object (references {details['$ref']})")
#                         # Try to show what's in the reference
#                         ref_schema = get_schema_from_ref(details["$ref"])
#                         if ref_schema and "properties" in ref_schema:
#                             for nested_name, nested_details in ref_schema["properties"].items():
#                                 nested_type = nested_details.get("type", "unknown")
#                                 required_nested = " [REQUIRED]" if nested_name in ref_schema.get("required", []) else ""
#                                 print(f"  - {nested_name}: {nested_type}{required_nested}")
#                     else:
#                         enum = details.get("enum", [])
#                         if enum:
#                             enum_str = f" (values: {', '.join(enum)})"
#                         else:
#                             enum_str = ""
#                         print(f"• {name}: {t}{required}{enum_str}")
        
#         if props:
#             print(f"\nAll properties (flattened):")
#             for name in sorted(props.keys()):
#                 details = props[name]
#                 t = details.get("type", "unknown")
#                 required = " [REQUIRED]" if details.get("required") else ""
#                 enum = details.get("enum", [])
#                 if enum:
#                     enum_str = f" (values: {', '.join(enum[:5])}{'...' if len(enum) > 5 else ''})"
#                 else:
#                     enum_str = ""
#                 desc = details.get("description", "")
#                 if desc:
#                     desc = f" - {desc[:50]}{'...' if len(desc) > 50 else ''}"
#                 print(f"• {name}: {t}{required}{enum_str}{desc}")
#         else:
#             print("  No additional properties found")
#             if verbose:
#                 print(f"  Schema content: {json.dumps(schema, indent=2)[:500]}...")
#     except Exception as e:
#         print(f"Error processing {upos_type}: {e}")
#         if verbose:
#             import traceback
#             traceback.print_exc()

# def print_all_upos_mapping():
#     """Print the UPOS to schema mapping."""
#     print("\n=== UPOS TO SCHEMA MAPPING ===")
#     for schema_name, upos_list in UPOS_ROUTING.items():
#         print(f"{schema_name}: {', '.join(upos_list)}")

# if __name__ == "__main__":
#     # Handle command line arguments
#     parser = argparse.ArgumentParser(description="Inspect UPOS schema properties")
#     parser.add_argument("--upos", help="UPOS type to inspect (e.g., NOUN, VERB, ADJ)")
#     parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
#     parser.add_argument("--debug", action="store_true", help="Debug mode")
#     parser.add_argument("--list", action="store_true", help="List all UPOS to schema mappings")
#     args = parser.parse_args()
    
#     if args.list:
#         print_all_upos_mapping()
#         sys.exit(0)
    
#     # Also check environment variable
#     upos = args.upos or os.getenv("UPOS")
    
#     print(f"Valid UPOS types: {VALID_UPOS}")
    
#     if args.debug:
#         print(f"PROJECT_BASE: {PROJECT_BASE}")
#         print(f"SCHEMAS: {SCHEMAS}")
#         print(f"Current working directory: {os.getcwd()}")
#         print(f"UPOS routing: {UPOS_ROUTING}")
    
#     if upos:
#         # Convert to uppercase for consistency
#         upos = upos.upper()
        
#         if upos not in VALID_UPOS:
#             print(f"Invalid UPOS type: {upos}")
#             print(f"Valid types: {', '.join(VALID_UPOS)}")
#             print("\nUse --list to see the mapping between UPOS types and schemas")
#             sys.exit(1)
        
#         print_upos_properties(upos, verbose=args.verbose)
#     else:
#         print("\nNo UPOS type specified. Showing all:")
#         for u in VALID_UPOS:
#             print_upos_properties(u, verbose=args.verbose)


import json
from pathlib import Path
import os
import sys
import argparse

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

# Valid UPOS types for the script
VALID_UPOS = list(UPOS_TO_SCHEMA.keys())

def map_url_to_local_path(url):
    """Map a URL like https://OpenUniLex.org/schemas/... to local file path."""
    if url.startswith("https://OpenUniLex.org/"):
        local_path = url.replace("https://OpenUniLex.org/", "")
    elif url.startswith("http://OpenUniLex.org/"):
        local_path = url.replace("http://OpenUniLex.org/", "")
    else:
        return None
    
    # Remove fragment if present
    if "#" in local_path:
        local_path = local_path.split("#")[0]
    
    # Construct the full local path - relative to project root
    full_path = PROJECT_BASE / local_path
    
    if not full_path.exists():
        # Try various combinations
        path_parts = local_path.split("/")
        for i in range(len(path_parts)):
            test_path = PROJECT_BASE / "/".join(path_parts[i:])
            if test_path.exists():
                return test_path
        
        # Try relative to schemas directory
        if local_path.startswith("schemas/"):
            test_path = SCHEMAS / local_path.replace("schemas/", "", 1)
            if test_path.exists():
                return test_path
        
        # Last resort: search by filename
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
    except FileNotFoundError:
        print(f"Error: Schema file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}")
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
            print(f"Warning: Could not map URL to local path: {ref_path}")
            return None
        schema = load_json(local_path)
    else:
        local_path = Path(ref_path)
        if not local_path.exists():
            local_path = SCHEMAS / ref_path
            if not local_path.exists():
                print(f"Warning: File not found: {ref_path}")
                return None
        schema = load_json(local_path)
    
    if fragment:
        parts = fragment.lstrip("#").split("/")
        for part in parts:
            if part:
                if part in schema:
                    schema = schema[part]
                else:
                    print(f"Warning: Fragment path '{fragment}' not found")
                    return None
    
    return schema

def collect_properties_from_schema(schema, visited=None):
    """Collect all properties from a schema, resolving $refs."""
    if visited is None:
        visited = set()
    
    schema_id = str(id(schema))
    if schema_id in visited:
        return {}
    
    visited.add(schema_id)
    props = {}
    
    # If schema has a $ref, resolve it
    if "$ref" in schema:
        ref_schema = get_schema_from_ref(schema["$ref"])
        if ref_schema:
            props.update(collect_properties_from_schema(ref_schema, visited))
    
    # Get properties from the schema
    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            if "$ref" in prop_schema:
                ref_schema = get_schema_from_ref(prop_schema["$ref"])
                if ref_schema:
                    # If the ref schema has properties, add them
                    if "properties" in ref_schema:
                        for nested_name, nested_schema in ref_schema["properties"].items():
                            props[nested_name] = nested_schema
                    else:
                        props[prop_name] = ref_schema
            else:
                props[prop_name] = prop_schema
            
            # Recursively check nested properties
            nested_props = collect_properties_from_schema(prop_schema, visited)
            props.update(nested_props)
    
    # Handle allOf references
    for item in schema.get("allOf", []):
        if "$ref" in item:
            ref_schema = get_schema_from_ref(item["$ref"])
            if ref_schema:
                props.update(collect_properties_from_schema(ref_schema, visited))
        elif "properties" in item:
            props.update(collect_properties_from_schema(item, visited))
    
    # Handle items in arrays
    if "items" in schema:
        if "$ref" in schema["items"]:
            ref_schema = get_schema_from_ref(schema["items"]["$ref"])
            if ref_schema:
                props.update(collect_properties_from_schema(ref_schema, visited))
        elif "properties" in schema["items"]:
            props.update(collect_properties_from_schema(schema["items"], visited))
    
    return props

def load_master_schema():
    """Load the master schema."""
    master_path = SCHEMAS / "master" / "v1.0.0.master.schema.json"
    if not master_path.exists():
        raise FileNotFoundError(f"Master schema not found: {master_path}")
    return load_json(master_path)

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

def get_required_properties(schema):
    """Extract required properties from a schema."""
    required = set()
    if "required" in schema:
        required.update(schema["required"])
    
    # Check allOf for required properties
    for item in schema.get("allOf", []):
        if "required" in item:
            required.update(item["required"])
    
    return required

def print_upos_properties(upos_type, verbose=False):
    """Print all properties for a given UPOS type."""
    try:
        # Load master schema and UPOS schema
        master_schema = load_master_schema()
        upos_schema, upos_path = load_upos_schema(upos_type)
        schema_name = UPOS_TO_SCHEMA.get(upos_type)
        
        if verbose:
            print(f"\n--- Master Schema: {SCHEMAS / 'master' / 'v1.0.0.master.schema.json'} ---")
            print(f"--- UPOS Schema: {upos_path} ---")
            print(f"Schema name: {schema_name}")
            print(f"UPOS types using this schema: {UPOS_ROUTING[schema_name]}")
        
        # Collect properties from both schemas
        master_props = collect_properties_from_schema(master_schema)
        upos_props = collect_properties_from_schema(upos_schema)
        
        # Merge properties (UPOS schema overrides master if there are conflicts)
        all_props = {**master_props, **upos_props}
        
        # Get required properties
        master_required = get_required_properties(master_schema)
        upos_required = get_required_properties(upos_schema)
        all_required = master_required | upos_required
        
        print(f"\n=== FULL PROPERTY SET FOR {upos_type.upper()} ===")
        print(f"(Using UPOS schema: {schema_name})")
        
        # Print top-level properties (from master schema)
        print(f"\n--- TOP-LEVEL PROPERTIES (from master schema) ---")
        if "properties" in master_schema:
            for name, details in master_schema["properties"].items():
                required = " [REQUIRED]" if name in master_required else ""
                
                # Check if it's a $ref
                if "$ref" in details:
                    ref_schema = get_schema_from_ref(details["$ref"])
                    if ref_schema:
                        ref_type = ref_schema.get("type", "object")
                        print(f"• {name}: {ref_type}{required} (references {details['$ref']})")
                    else:
                        print(f"• {name}: unknown{required} (references {details['$ref']})")
                else:
                    t = details.get("type", "unknown")
                    enum = details.get("enum", [])
                    if enum:
                        enum_str = f" (values: {', '.join(enum)})"
                    else:
                        enum_str = ""
                    print(f"• {name}: {t}{required}{enum_str}")
        
        # Print pos_payload properties (from UPOS schema)
        print(f"\n--- POS_PAYLOAD PROPERTIES (from {schema_name} schema) ---")
        if "properties" in upos_schema and "pos_payload" in upos_schema["properties"]:
            pos_payload = upos_schema["properties"]["pos_payload"]
            if "properties" in pos_payload:
                for name, details in pos_payload["properties"].items():
                    required = " [REQUIRED]" if name in pos_payload.get("required", []) else ""
                    
                    if "$ref" in details:
                        print(f"• {name}: object{required} (references {details['$ref']})")
                        ref_schema = get_schema_from_ref(details["$ref"])
                        if ref_schema and "properties" in ref_schema:
                            for nested_name, nested_details in ref_schema["properties"].items():
                                nested_type = nested_details.get("type", "unknown")
                                nested_required = " [REQUIRED]" if nested_name in ref_schema.get("required", []) else ""
                                enum = nested_details.get("enum", [])
                                if enum:
                                    enum_str = f" (values: {', '.join(enum)})"
                                else:
                                    enum_str = ""
                                print(f"  - {nested_name}: {nested_type}{nested_required}{enum_str}")
                    else:
                        t = details.get("type", "unknown")
                        enum = details.get("enum", [])
                        if enum:
                            enum_str = f" (values: {', '.join(enum)})"
                        else:
                            enum_str = ""
                        print(f"• {name}: {t}{required}{enum_str}")
        
        # Print all flattened properties (for completeness)
        if all_props:
            print(f"\n--- ALL FLATTENED PROPERTIES ---")
            for name in sorted(all_props.keys()):
                details = all_props[name]
                t = details.get("type", "unknown")
                required = " [REQUIRED]" if name in all_required else ""
                enum = details.get("enum", [])
                if enum:
                    enum_str = f" (values: {', '.join(enum[:5])}{'...' if len(enum) > 5 else ''})"
                else:
                    enum_str = ""
                desc = details.get("description", "")
                if desc:
                    desc = f" - {desc[:50]}{'...' if len(desc) > 50 else ''}"
                print(f"• {name}: {t}{required}{enum_str}{desc}")
        else:
            print("  No properties found")
            
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
    parser = argparse.ArgumentParser(description="Inspect UPOS schema properties")
    parser.add_argument("--upos", help="UPOS type to inspect (e.g., NOUN, VERB, ADJ)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    parser.add_argument("--list", action="store_true", help="List all UPOS to schema mappings")
    args = parser.parse_args()
    
    if args.list:
        print_all_upos_mapping()
        sys.exit(0)
    
    upos = args.upos or os.getenv("UPOS")
    
    print(f"Valid UPOS types: {VALID_UPOS}")
    
    if args.debug:
        print(f"PROJECT_BASE: {PROJECT_BASE}")
        print(f"SCHEMAS: {SCHEMAS}")
        print(f"UPOS routing: {UPOS_ROUTING}")
    
    if upos:
        upos = upos.upper()
        
        if upos not in VALID_UPOS:
            print(f"Invalid UPOS type: {upos}")
            print(f"Valid types: {', '.join(VALID_UPOS)}")
            print("\nUse --list to see the mapping between UPOS types and schemas")
            sys.exit(1)
        
        print_upos_properties(upos, verbose=args.verbose)
    else:
        print("\nNo UPOS type specified. Showing all:")
        for u in VALID_UPOS:
            print_upos_properties(u, verbose=args.verbose)