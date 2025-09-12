#!/usr/bin/env python3
"""OpenAPI specification generation for Chatter API."""

import json
import sys
from pathlib import Path
from typing import Any

import yaml

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from chatter.main import app


def generate_openapi_spec() -> dict[str, Any]:
    """Generate OpenAPI specification from FastAPI app.

    Returns:
        Dict containing the OpenAPI specification
    """
    return app.openapi()


def convert_openapi_3_1_to_3_0(spec: dict[str, Any]) -> dict[str, Any]:
    """Convert OpenAPI 3.1 spec to 3.0 for better compatibility.

    Args:
        spec: OpenAPI 3.1 specification

    Returns:
        OpenAPI 3.0 compatible specification
    """
    # Create a deep copy to avoid modifying the original
    import copy

    converted = copy.deepcopy(spec)

    # Convert version to 3.0.3
    converted["openapi"] = "3.0.3"

    # Move $defs to components/schemas if it exists
    if "$defs" in converted:
        if "components" not in converted:
            converted["components"] = {}
        if "schemas" not in converted["components"]:
            converted["components"]["schemas"] = {}

        # Move all $defs to components/schemas
        converted["components"]["schemas"].update(converted["$defs"])
        del converted["$defs"]

    # Recursively replace $defs references with components/schemas
    def replace_refs(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if (
                    key == "$ref"
                    and isinstance(value, str)
                    and value.startswith("#/$defs/")
                ):
                    obj[key] = value.replace(
                        "#/$defs/", "#/components/schemas/"
                    )
                else:
                    replace_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                replace_refs(item)

    replace_refs(converted)

    return converted


def export_openapi_json(
    spec: dict[str, Any], output_path: Path
) -> None:
    """Export OpenAPI specification as JSON.

    Args:
        spec: OpenAPI specification dictionary
        output_path: Path to write JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)


def export_openapi_yaml(
    spec: dict[str, Any], output_path: Path
) -> None:
    """Export OpenAPI specification as YAML.

    Args:
        spec: OpenAPI specification dictionary
        output_path: Path to write YAML file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(spec, f, default_flow_style=False, allow_unicode=True)


if __name__ == "__main__":
    """Generate OpenAPI spec and save to default locations."""
    spec = generate_openapi_spec()

    # Save to docs directory
    docs_dir = Path(__file__).parent.parent / "docs" / "api"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Export original 3.1 spec
    export_openapi_json(spec, docs_dir / "openapi.json")
    export_openapi_yaml(spec, docs_dir / "openapi.yaml")

    # Export 3.0 compatible spec for SDK generation
    converted_spec = convert_openapi_3_1_to_3_0(spec)
    export_openapi_json(converted_spec, docs_dir / "openapi-3.0.json")
    export_openapi_yaml(converted_spec, docs_dir / "openapi-3.0.yaml")

    print(f"OpenAPI spec generated in {docs_dir}")
