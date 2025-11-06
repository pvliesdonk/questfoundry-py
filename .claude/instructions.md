# Claude Code Instructions

This repository contains the Python implementation of the QuestFoundry protocol (Layer 6).

## Project Structure

```
questfoundry-py/
├── spec/                    # Git submodule: questfoundry-spec
│   ├── 03-schemas/         # JSON schemas (Layer 3)
│   ├── 04-protocol/        # Protocol specs (Layer 4)
│   └── 05-prompts/         # Role prompts (Layer 5)
├── src/questfoundry/       # Main package
│   ├── resources/          # Bundled schemas & prompts
│   ├── models/             # Pydantic models
│   ├── validators/         # Schema validation
│   └── utils/              # Utility functions
├── tests/                  # Test suite
└── scripts/                # Build scripts

```

## Commit Message Convention

We use **Conventional Commits**. All commit messages MUST follow this format:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Commit Types

- **feat**: New feature (triggers minor version bump)
- **fix**: Bug fix (triggers patch version bump)
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring (neither fixes a bug nor adds a feature)
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Changes to build process or auxiliary tools
- **ci**: Changes to CI/CD configuration

### Scope (Optional but Recommended)

- `models`: Changes to Pydantic models
- `validators`: Changes to validation logic
- `resources`: Changes to resource loading
- `protocol`: Changes to protocol implementation
- `state`: Changes to state management
- `build`: Changes to build system
- `deps`: Dependency updates

### Examples

```bash
feat(models): add Envelope pydantic model

Implements the Layer 4 protocol envelope structure with
full type safety and validation.

feat(validators): enhance schema validation with detailed errors

- Add ValidationResult dataclass
- Improve error messages with path information
- Add support for warning collection

fix(resources): handle missing schema files gracefully

Previously would crash if schema file was not found.
Now raises FileNotFoundError with clear message.

chore(deps): update pydantic to v2.12.0

test(validators): add comprehensive envelope validation tests

docs: update RESOURCES.md with new bundling instructions
```

## Branch Naming

For Claude Code sessions, branches MUST follow this pattern:
```
claude/<descriptive-name>-<session-id>
```

Example: `claude/epic-01-project-foundation-011CUrRotNspY6xiSRLbKVfR`

## Development Workflow

### 1. Making Changes

```bash
# Ensure all tools pass
uv run pytest          # Run tests
uv run mypy src/       # Type checking
uv run ruff check .    # Linting
```

### 2. Committing

```bash
# Stage changes
git add <files>

# Commit with conventional format
git commit -m "feat(scope): description"
```

### 3. Pushing

Always push with `-u` flag:
```bash
git push -u origin <branch-name>
```

## Coding Standards

### Python Style

- **Python Version**: 3.11+
- **Line Length**: 88 characters (enforced by ruff)
- **Type Hints**: Required on all functions (strict mypy)
- **Docstrings**: Required on all public APIs
- **Imports**: Sorted with ruff (isort-compatible)

### Example Function

```python
"""Module docstring explaining purpose"""

from typing import Any


def validate_artifact(
    artifact_type: str,
    data: dict[str, Any]
) -> bool:
    """
    Validate an artifact against its schema.

    Args:
        artifact_type: The type of artifact (e.g., "hook_card")
        data: The artifact data to validate

    Returns:
        True if valid, False otherwise

    Raises:
        FileNotFoundError: If schema not found for artifact_type
    """
    # Implementation...
    pass
```

### Pydantic Models

Use Pydantic v2 syntax:

```python
from pydantic import BaseModel, ConfigDict, Field


class Artifact(BaseModel):
    """Base artifact model"""

    model_config = ConfigDict(
        json_schema_extra={"example": {"type": "hook_card"}}
    )

    type: str = Field(..., description="Artifact type")
    data: dict[str, Any] = Field(default_factory=dict)
```

## Resource Bundling

After updating the spec submodule, re-bundle resources:

```bash
python scripts/bundle_resources.py
```

This copies schemas and prompts from the spec submodule into the package.

## Testing Guidelines

- **Test File Naming**: `test_*.py`
- **Test Function Naming**: `test_<function_name>` or `test_<scenario>`
- **Coverage Goal**: >80%
- **Test Location**: Mirror source structure in `tests/`

Example:
```python
def test_validate_artifact_success():
    """Test successful artifact validation"""
    artifact = {"type": "hook_card", "data": {...}}
    assert validate_artifact("hook_card", artifact)


def test_validate_artifact_missing_schema():
    """Test validation with missing schema"""
    with pytest.raises(FileNotFoundError):
        validate_artifact("nonexistent", {})
```

## Epic-Based Development

We organize work into Epics and Features:

- **Epic**: Large body of work (e.g., "Epic 1: Project Foundation")
- **Feature**: Individual task within an epic (e.g., "Feature 1.1: Repository Setup")

Each epic gets its own branch, features get individual commits.

### Feature Commit Pattern

```bash
# Epic branch
git checkout -b claude/epic-02-layer-integration-<session-id>

# Feature 1
git add <files>
git commit -m "feat(validators): implement detailed validation"

# Feature 2
git add <files>
git commit -m "feat(protocol): add envelope pydantic models"

# Push epic when complete
git push -u origin claude/epic-02-layer-integration-<session-id>
```

## Helpful Commands

```bash
# Sync dependencies
uv sync

# Run tests with coverage
uv run pytest --cov=src tests/

# Run tests in watch mode
uv run pytest -f

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type check
uv run mypy src/

# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit on all files
uv run pre-commit run --all-files
```

## Important Files

- **RESOURCES.md**: Documents bundled resource versions
- **pyproject.toml**: Package configuration and dependencies
- **uv.lock**: Locked dependency versions
- **.gitmodules**: Spec submodule configuration

## Questions?

If unclear about implementation details:
1. Check the spec in `spec/` directory
2. Check `RESOURCES.md` for resource versions
3. Check existing code patterns in `src/questfoundry/`
4. Refer to the implementation plan in `spec/06-libraries/IMPLEMENTATION_PLAN.md`
