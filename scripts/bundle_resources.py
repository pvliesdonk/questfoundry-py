#!/usr/bin/env python3
"""
Bundle schemas and prompts from the spec submodule into the package.

This script copies resources from the questfoundry-spec submodule into
the Python package resources directory for distribution.
"""

import shutil
from pathlib import Path


def main() -> None:
    """Bundle schemas and prompts into package resources."""
    # Get project root (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Source directories (from spec submodule)
    spec_dir = project_root / "spec"
    schemas_src = spec_dir / "03-schemas"
    prompts_src = spec_dir / "05-prompts"

    # Destination directories (in package)
    resources_dir = project_root / "src" / "questfoundry" / "resources"
    schemas_dest = resources_dir / "schemas"
    prompts_dest = resources_dir / "prompts"

    print(f"Bundling resources from {spec_dir}")

    # Create resources directories
    resources_dir.mkdir(parents=True, exist_ok=True)
    schemas_dest.mkdir(parents=True, exist_ok=True)
    prompts_dest.mkdir(parents=True, exist_ok=True)

    # Bundle schemas (all .json files)
    print(f"Copying schemas from {schemas_src} to {schemas_dest}")
    schema_count = 0
    for schema_file in schemas_src.glob("*.json"):
        dest_file = schemas_dest / schema_file.name
        shutil.copy2(schema_file, dest_file)
        schema_count += 1
        print(f"  ✓ {schema_file.name}")
    print(f"Copied {schema_count} schemas")

    # Bundle prompts (copy entire role directories, excluding tests/upload_kits)
    print(f"\nCopying prompts from {prompts_src} to {prompts_dest}")
    prompt_count = 0
    skip_dirs = {"tests", "upload_kits"}

    for role_dir in prompts_src.iterdir():
        if not role_dir.is_dir() or role_dir.name in skip_dirs:
            continue

        dest_dir = prompts_dest / role_dir.name

        # Remove existing directory if it exists
        if dest_dir.exists():
            shutil.rmtree(dest_dir)

        # Copy entire directory
        shutil.copytree(role_dir, dest_dir)
        prompt_count += 1
        print(f"  ✓ {role_dir.name}/")

    print(f"Copied {prompt_count} prompt directories")

    # Create __init__.py files for resources
    (resources_dir / "__init__.py").touch()
    (schemas_dest / "__init__.py").touch()
    (prompts_dest / "__init__.py").touch()

    print("\n✅ Resource bundling complete!")
    print(f"   Schemas: {schema_count} files")
    print(f"   Prompts: {prompt_count} role directories")


if __name__ == "__main__":
    main()
