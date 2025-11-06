"""Schema validation utilities"""

import json
from pathlib import Path
from typing import Any

import jsonschema

from ..utils.resources import get_schema


def validate_instance(instance: dict[str, Any], schema_name: str) -> bool:
    """Validate an instance against a schema"""
    schema = get_schema(schema_name)
    try:
        jsonschema.validate(instance, schema)
        return True
    except jsonschema.ValidationError:
        return False

def validate_instance_detailed(instance: dict[str, Any], schema_name: str) -> dict[str, Any]:
    """Validate instance and return detailed error information"""
    schema = get_schema(schema_name)
    try:
        jsonschema.validate(instance, schema)
        return {"valid": True, "errors": []}
    except jsonschema.ValidationError as e:
        return {
            "valid": False,
            "errors": [str(e)],
            "message": str(e.message),
            "path": list(e.path),
        }

def validate_schema(schema_path: str | Path) -> bool:
    """Validate that a schema file is valid JSON Schema Draft 2020-12"""
    if isinstance(schema_path, str):
        schema_path = Path(schema_path)

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path) as f:
        schema = json.load(f)

    # Basic validation: ensure it has required schema properties
    required_fields = ["$schema", "$id"]
    for field in required_fields:
        if field not in schema:
            return False

    return True
