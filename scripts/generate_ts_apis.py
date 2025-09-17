#!/usr/bin/env python3
"""
Script to generate TypeScript API clients from OpenAPI schema
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def camel_case(name: str) -> str:
    """Convert snake_case to camelCase"""
    # First clean the name of special characters and spaces
    clean_name = re.sub(r"[^a-zA-Z0-9_\s]", "", name)
    clean_name = re.sub(r"\s+", "_", clean_name)
    components = clean_name.split("_")
    components = [
        comp for comp in components if comp
    ]  # Remove empty components
    if not components:
        return "unknown"
    return components[0].lower() + "".join(
        word.capitalize() for word in components[1:]
    )


def pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase"""
    # First clean the name of special characters and spaces
    clean_name = re.sub(r"[^a-zA-Z0-9_\s]", "", name)
    clean_name = re.sub(r"\s+", "_", clean_name)
    return "".join(
        word.capitalize() for word in clean_name.split("_") if word
    )


def get_operation_id(
    path: str, method: str, operation: dict[str, Any]
) -> str:
    """Generate operation ID from path and method"""
    if "operationId" in operation:
        # Use existing operationId but make it cleaner
        op_id = operation["operationId"]
        # Remove common prefixes and suffixes like api_v1_..._post
        op_id = re.sub(r"^[^_]*_api_v\d+_", "", op_id)
        op_id = re.sub(
            r"_(get|post|put|patch|delete|options|head)$", "", op_id
        )
        # Convert to camelCase
        return camel_case(op_id)

    # Generate from path and method
    # Remove /api/v1/ prefix and clean up path
    clean_path = path.replace("/api/v1/", "").replace("/api/v2/", "")

    # Handle specific patterns
    if clean_path == "":
        return f"{method.lower()}Root"

    # Convert path parameters to readable names
    clean_path = re.sub(r"\{([^}]+)\}", r"By\1", clean_path)
    # Replace slashes with underscores
    clean_path = clean_path.replace("/", "_")
    # Remove extra underscores and clean
    clean_path = re.sub(r"[^a-zA-Z0-9_]", "_", clean_path)
    clean_path = re.sub(r"_+", "_", clean_path).strip("_")

    return camel_case(f"{method.lower()}_{clean_path}")


def is_streaming_endpoint(operation: dict[str, Any]) -> bool:
    """Check if this is a streaming endpoint that returns text/event-stream"""
    responses = operation.get("responses", {})

    # Look for 200, 201, or first successful response with text/event-stream
    for status in ["200", "201", "202"]:
        if status in responses:
            response = responses[status]
            content = response.get("content", {})
            if "text/event-stream" in content:
                return True

    # Fallback to any successful response
    for status, response in responses.items():
        if status.startswith("2"):
            content = response.get("content", {})
            if "text/event-stream" in content:
                return True

    return False


def get_response_type(operation: dict[str, Any]) -> str:
    """Extract response type from operation"""
    responses = operation.get("responses", {})

    # Check for streaming endpoint first
    if is_streaming_endpoint(operation):
        return "ReadableStream<Uint8Array>"

    # Look for 200, 201, or first successful response
    for status in ["200", "201", "202"]:
        if status in responses:
            response = responses[status]
            content = response.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                return typescript_type_from_schema(schema)

    # Fallback to any successful response
    for status, response in responses.items():
        if status.startswith("2"):
            content = response.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                return typescript_type_from_schema(schema)

    return "unknown"


def typescript_type_from_schema(schema: dict[str, Any]) -> str:
    """Convert OpenAPI schema to TypeScript type - simplified version"""
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref.startswith("#/components/schemas/"):
            return ref.split("/")[-1]
        return "unknown"

    if "anyOf" in schema:
        types = []
        for s in schema["anyOf"]:
            if s.get("type") == "null":
                continue
            types.append(typescript_type_from_schema(s))

        if not types:
            return "null"

        has_null = any(s.get("type") == "null" for s in schema["anyOf"])
        result = " | ".join(types) if len(types) > 1 else types[0]
        return f"{result} | null" if has_null else result

    schema_type = schema.get("type", "object")

    if schema_type == "string":
        if "enum" in schema:
            enum_values = [f'"{v}"' for v in schema["enum"]]
            return " | ".join(enum_values)
        return "string"
    elif schema_type in ["integer", "number"]:
        return "number"
    elif schema_type == "boolean":
        return "boolean"
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        item_type = typescript_type_from_schema(items_schema)
        return f"{item_type}[]"
    elif schema_type == "object":
        return "Record<string, unknown>"

    return "unknown"


def get_parameters(
    operation: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """Extract parameters from operation"""
    params = {"path": [], "query": [], "header": [], "cookie": []}

    for param in operation.get("parameters", []):
        if "$ref" in param:
            # Would need to resolve reference - skipping for now
            continue

        param_in = param.get("in", "query")
        if param_in in params:
            params[param_in].append(param)

    return params


def get_request_body_type(operation: dict[str, Any]) -> str | None:
    """Extract request body type from operation"""
    request_body = operation.get("requestBody", {})
    if not request_body:
        return None

    content = request_body.get("content", {})
    if "application/json" in content:
        schema = content["application/json"].get("schema", {})
        return typescript_type_from_schema(schema)
    elif "multipart/form-data" in content:
        return "FormData"
    elif "application/x-www-form-urlencoded" in content:
        return "URLSearchParams"

    return None


def has_json_request_body(operation: dict[str, Any]) -> bool:
    """Check if operation has a JSON request body"""
    request_body = operation.get("requestBody", {})
    if not request_body:
        return False

    content = request_body.get("content", {})
    return "application/json" in content


def generate_method(
    path: str, method: str, operation: dict[str, Any]
) -> str:
    """Generate TypeScript method for an API operation"""
    operation_id = get_operation_id(path, method, operation)
    method_name = (
        operation_id  # Already camelCase from get_operation_id
    )

    response_type = get_response_type(operation)
    params = get_parameters(operation)
    request_body_type = get_request_body_type(operation)

    # Build method signature
    method_params = []

    # Path parameters (required)
    for param in params["path"]:
        param_name = camel_case(param["name"])
        param_type = typescript_type_from_schema(
            param.get("schema", {"type": "string"})
        )
        method_params.append(f"{param_name}: {param_type}")

    # Request body (if exists)
    if request_body_type:
        body_param = operation.get("requestBody", {})
        required = body_param.get("required", True)
        if required:
            method_params.append(f"data: {request_body_type}")
        else:
            method_params.append(f"data?: {request_body_type}")

    # Options parameter (for query params, headers, etc.)
    needs_options = bool(
        params["query"] or params["header"] or params["cookie"]
    )
    if needs_options:
        # Check if any query parameter is named 'query' to avoid conflicts
        has_query_param = any(
            p['name'] == 'query' for p in params["query"]
        )
        additional_query_name = (
            "additionalQuery" if has_query_param else "query"
        )

        method_params.append(
            "options?: { "
            + "".join(
                [
                    f"{camel_case(p['name'])}?: {typescript_type_from_schema(p.get('schema', {'type': 'string'}))}; "
                    for p in params["query"]
                    + params["header"]
                    + params["cookie"]
                ]
            )
            + f"{additional_query_name}?: HTTPQuery; headers?: HTTPHeaders; }}"
        )

    params_str = ", ".join(method_params)

    # Build method body
    path_with_params = path

    # Replace path parameters
    for param in params["path"]:
        param_name = param["name"]
        camel_name = camel_case(param_name)
        path_with_params = path_with_params.replace(
            f"{{{param_name}}}", f"${{{camel_name}}}"
        )

    method_body = f"""
  /**{operation.get('summary', f'{method.upper()} {path}')}
   * {operation.get('description', '').replace('*/', '')}
   */
  public async {method_name}({params_str}): Promise<{response_type}> {{
    const requestContext: RequestOpts = {{
      path: `{path_with_params}`,
      method: '{method.upper()}' as HTTPMethod,
      headers: {{"""

    # Add Content-Type header for JSON request bodies
    if has_json_request_body(operation):
        method_body += """
        'Content-Type': 'application/json',"""

    # Add headers from parameters
    if params["header"]:
        for header in params["header"]:
            header_name = header["name"]
            method_body += f"""
        '{header_name}': String(options?.{camel_case(header_name)} ?? ''),"""
        method_body += """
        ...options?.headers,"""
    elif needs_options:
        method_body += """
        ...options?.headers,"""

    method_body += """
      },"""

    # Add query parameters
    if params["query"]:
        # Check if any query parameter is named 'query' to avoid conflicts
        has_query_param = any(
            p['name'] == 'query' for p in params["query"]
        )
        additional_query_name = (
            "additionalQuery" if has_query_param else "query"
        )

        method_body += """
      query: {"""
        for query_param in params["query"]:
            param_name = query_param["name"]
            camel_name = camel_case(param_name)
            method_body += f"""
        '{param_name}': options?.{camel_name},"""
        method_body += f"""
        ...options?.{additional_query_name}
      }},"""
    elif needs_options:
        # Check if we need the alternate naming (though this case shouldn't have conflicts)
        method_body += """
      query: options?.query,"""

    # Add request body
    if request_body_type:
        method_body += """
      body: data,"""

    method_body += f"""
    }};

    const response = await this.{'requestStream' if is_streaming_endpoint(operation) else 'request'}(requestContext);
    {'return response;' if is_streaming_endpoint(operation) else f'return response.json() as Promise<{response_type}>;'}
  }}"""

    return method_body


def group_operations_by_tag(
    spec: dict[str, Any],
) -> dict[str, list[tuple]]:
    """Group operations by their tags"""
    grouped = defaultdict(list)

    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in [
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
            ]:
                continue

            tags = operation.get("tags", ["Default"])
            # Use first tag
            tag = tags[0] if tags else "Default"
            grouped[tag].append((path, method, operation))

    return grouped


def generate_api_class(tag: str, operations: list[tuple]) -> str:
    """Generate API class for a tag"""
    class_name = f"{pascal_case(tag)}Api"

    imports = set()
    methods = []
    uses_http_query = False
    uses_http_headers = False

    for path, method, operation in operations:
        method_code = generate_method(path, method, operation)
        methods.append(method_code)

        # Check if this method uses HTTPQuery or HTTPHeaders
        params = get_parameters(operation)
        if (
            params["query"]
            or "query?: HTTPQuery" in method_code
            or "additionalQuery?: HTTPQuery" in method_code
        ):
            uses_http_query = True
        if params["header"] or "headers?: HTTPHeaders" in method_code:
            uses_http_headers = True

        # Extract types used in this method
        response_type = get_response_type(operation)
        if response_type and not response_type.startswith("Record<"):
            # Extract type names from union types, arrays, etc.
            # Updated regex to handle complex names with double underscores
            type_names = re.findall(
                r"\b[a-zA-Z][a-zA-Z0-9_]*(?:__[a-zA-Z0-9_]+)*\b",
                response_type,
            )
            imports.update(type_names)

        request_body_type = get_request_body_type(operation)
        if (
            request_body_type
            and not request_body_type.startswith("Record<")
            and request_body_type not in ["FormData", "URLSearchParams"]
        ):
            type_names = re.findall(
                r"\b[a-zA-Z][a-zA-Z0-9_]*(?:__[a-zA-Z0-9_]+)*\b",
                request_body_type,
            )
            imports.update(type_names)

        # Also check parameter types
        params = get_parameters(operation)
        for param_list in params.values():
            for param in param_list:
                param_type = typescript_type_from_schema(
                    param.get("schema", {})
                )
                type_names = re.findall(
                    r"\b[a-zA-Z][a-zA-Z0-9_]*(?:__[a-zA-Z0-9_]+)*\b",
                    param_type,
                )
                imports.update(type_names)

    # Generate import statements
    import_statements = []
    if imports:
        # Filter out built-in TypeScript types and generic Record types
        builtin_types = {
            "Record",
            "Array",
            "Promise",
            "Date",
            "RegExp",
            "Error",
            "Object",
            "String",
            "Number",
            "Boolean",
            "Function",
            "Map",
            "Set",
            "WeakMap",
            "WeakSet",
            "ReadonlyArray",
            "Partial",
            "Required",
            "Pick",
            "Omit",
            "Exclude",
            "Extract",
            "string",
            "number",
            "boolean",
            "unknown",
            "null",
            "undefined",
            "void",
            "any",
            "ReadableStream",
            "Uint8Array",  # Browser/Node.js streaming types
        }
        filtered_imports = [
            imp for imp in imports if imp not in builtin_types
        ]
        if filtered_imports:
            import_list = ", ".join(sorted(filtered_imports))
            import_statements.append(
                f"import {{ {import_list} }} from '../models/index';"
            )

    # Build runtime import - only include what's actually used
    runtime_imports = [
        "BaseAPI",
        "Configuration",
        "RequestOpts",
        "HTTPMethod",
    ]
    if uses_http_query:
        runtime_imports.append("HTTPQuery")
    if uses_http_headers:
        runtime_imports.append("HTTPHeaders")

    runtime_import = (
        f"import {{ {', '.join(runtime_imports)} }} from '../runtime';"
    )
    import_statements.append(runtime_import)
    import_statements.append("")

    class_code = f"""/**
 * Generated API client for {tag}
 */
{chr(10).join(import_statements)}
export class {class_name} extends BaseAPI {{
  constructor(configuration?: Configuration) {{
    super(configuration);
  }}
{''.join(methods)}
}}"""

    return class_code


def main():
    # Load OpenAPI spec
    spec_path = Path("docs/api/openapi.json")
    with open(spec_path) as f:
        spec = json.load(f)

    # Group operations by tag
    grouped_ops = group_operations_by_tag(spec)

    # Generate API classes
    apis_dir = Path("sdk/typescript/src/apis")
    apis_dir.mkdir(parents=True, exist_ok=True)

    api_classes = []

    for tag, operations in grouped_ops.items():
        class_name = f"{pascal_case(tag)}Api"
        class_code = generate_api_class(tag, operations)

        # Write to file
        file_name = f"{class_name}.ts"
        file_path = apis_dir / file_name

        with open(file_path, "w") as f:
            f.write(class_code)

        api_classes.append(class_name)
        print(f"Generated {file_name} with {len(operations)} methods")

    # Generate index file that exports all APIs
    index_path = apis_dir / "index.ts"
    with open(index_path, "w") as f:
        f.write(
            "/**\n * Generated TypeScript API clients from OpenAPI schema\n */\n\n"
        )
        for class_name in sorted(api_classes):
            f.write(f"export * from './{class_name}';\n")

    print(f"\nGenerated {len(api_classes)} API client classes")
    print(f"Index file created at {index_path}")


if __name__ == "__main__":
    main()
