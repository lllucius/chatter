#!/usr/bin/env python3
"""
Script to generate TypeScript models from OpenAPI schema
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Union, Optional

def typescript_type_from_schema(schema: Dict[str, Any], schema_name: str = "") -> str:
    """Convert OpenAPI schema to TypeScript type"""
    
    if "$ref" in schema:
        # Extract reference name
        ref = schema["$ref"]
        if ref.startswith("#/components/schemas/"):
            return ref.split("/")[-1]
        return "unknown"
    
    # Handle anyOf, oneOf, allOf first (before checking type)
    if "anyOf" in schema:
        types = []
        for s in schema["anyOf"]:
            if s.get("type") == "null":
                continue  # We'll handle null separately
            types.append(typescript_type_from_schema(s))
        
        if not types:
            return "null"
        
        # Check if null was in the anyOf
        has_null = any(s.get("type") == "null" for s in schema["anyOf"])
        result = " | ".join(types) if len(types) > 1 else types[0]
        return f"{result} | null" if has_null else result
    
    if "oneOf" in schema:
        types = [typescript_type_from_schema(s) for s in schema["oneOf"]]
        return " | ".join(types)
    
    if "allOf" in schema:
        # For allOf, we'll need to merge the schemas - simplified approach
        types = [typescript_type_from_schema(s) for s in schema["allOf"]]
        return " & ".join(types)
    
    schema_type = schema.get("type", "object")
    
    if schema_type == "string":
        if "enum" in schema:
            enum_values = [f'"{v}"' for v in schema["enum"]]
            return " | ".join(enum_values)
        # Handle string formats
        format_type = schema.get("format")
        if format_type in ["date", "date-time"]:
            return "string"  # Could be Date but string is safer for API
        return "string"
    
    elif schema_type == "integer":
        return "number"
    
    elif schema_type == "number":
        return "number"
    
    elif schema_type == "boolean":
        return "boolean"
    
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        item_type = typescript_type_from_schema(items_schema)
        return f"{item_type}[]"
    
    elif schema_type == "object":
        if "properties" in schema:
            return generate_inline_interface(schema)
        if "additionalProperties" in schema:
            additional = schema["additionalProperties"]
            if additional is True:
                return "Record<string, unknown>"
            else:
                prop_type = typescript_type_from_schema(additional)
                return f"Record<string, {prop_type}>"
        return "Record<string, unknown>"
    
    return "unknown"

def generate_inline_interface(schema: Dict[str, Any]) -> str:
    """Generate inline interface for object schema"""
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    lines = ["{"]
    for prop_name, prop_schema in properties.items():
        prop_type = typescript_type_from_schema(prop_schema)
        optional = "" if prop_name in required else "?"
        
        # Handle property names that need escaping
        if re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', prop_name):
            lines.append(f"  {prop_name}{optional}: {prop_type};")
        else:
            lines.append(f'  "{prop_name}"{optional}: {prop_type};')
    
    lines.append("}")
    return "\n".join(lines)

def generate_typescript_interface(name: str, schema: Dict[str, Any]) -> str:
    """Generate a TypeScript interface from OpenAPI schema"""
    
    # Handle enums
    if schema.get("type") == "string" and "enum" in schema:
        enum_values = [f'  {v} = "{v}"' for v in schema["enum"]]
        return f"export enum {name} {{\n" + ",\n".join(enum_values) + "\n}"
    
    # Handle simple type aliases
    if "type" in schema and schema["type"] != "object":
        type_def = typescript_type_from_schema(schema)
        return f"export type {name} = {type_def};"
    
    # Handle objects
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    if not properties:
        return f"export interface {name} {{\n  [key: string]: unknown;\n}}"
    
    lines = [f"export interface {name} {{"]
    
    for prop_name, prop_schema in properties.items():
        prop_type = typescript_type_from_schema(prop_schema)
        optional = "" if prop_name in required else "?"
        description = prop_schema.get("description", "")
        
        if description:
            lines.append(f"  /** {description} */")
        
        # Handle property names that need escaping
        if re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', prop_name):
            lines.append(f"  {prop_name}{optional}: {prop_type};")
        else:
            lines.append(f'  "{prop_name}"{optional}: {prop_type};')
    
    lines.append("}")
    
    return "\n".join(lines)

def main():
    # Load OpenAPI spec
    spec_path = Path("docs/api/openapi.json")
    with open(spec_path) as f:
        spec = json.load(f)
    
    schemas = spec.get("components", {}).get("schemas", {})
    
    # Generate models
    models_dir = Path("sdk-ts/src/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_files = []
    
    for schema_name, schema in schemas.items():
        # Generate TypeScript interface
        ts_interface = generate_typescript_interface(schema_name, schema)
        
        # Write to file
        file_name = f"{schema_name}.ts"
        file_path = models_dir / file_name
        
        with open(file_path, "w") as f:
            f.write(f"/**\n * Generated from OpenAPI schema: {schema_name}\n */\n\n")
            f.write(ts_interface)
            f.write("\n")
        
        model_files.append(schema_name)
        print(f"Generated {file_name}")
    
    # Generate index file that exports all models
    index_path = models_dir / "index.ts"
    with open(index_path, "w") as f:
        f.write("/**\n * Generated TypeScript models from OpenAPI schema\n */\n\n")
        for model_name in sorted(model_files):
            f.write(f"export * from './{model_name}';\n")
    
    print(f"\nGenerated {len(model_files)} model files")
    print(f"Index file created at {index_path}")

if __name__ == "__main__":
    main()