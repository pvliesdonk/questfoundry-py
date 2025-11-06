"""Resource loading utilities for schemas and prompts"""

import json
from pathlib import Path
from typing import Any


def get_schema(schema_name: str) -> dict[str, Any]:
    """Load a schema from bundled resources"""
    resource_dir = Path(__file__).parent.parent / "resources" / "schemas"
    schema_file = resource_dir / f"{schema_name}.schema.json"

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema not found: {schema_name}")

    with open(schema_file) as f:
        return json.load(f)

def get_prompt(role_name: str) -> str:
    """Load a prompt from bundled resources"""
    resource_dir = Path(__file__).parent.parent / "resources" / "prompts"
    prompt_file = resource_dir / role_name / "system_prompt.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt not found: {role_name}")

    return prompt_file.read_text()

def list_schemas() -> list[str]:
    """List available schemas"""
    resource_dir = Path(__file__).parent.parent / "resources" / "schemas"
    return [f.stem for f in resource_dir.glob("*.schema.json")]

def list_prompts() -> list[str]:
    """List available prompt roles"""
    resource_dir = Path(__file__).parent.parent / "resources" / "prompts"
    return [d.name for d in resource_dir.iterdir() if d.is_dir()]
