# Contributing

Thank you for your interest in contributing to QuestFoundry-Py! This guide will help you get started.

## Code of Conduct

Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

Found a bug? Please open an [issue on GitHub](https://github.com/pvliesdonk/questfoundry-py/issues) with:

- Clear, descriptive title
- Detailed description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python and QuestFoundry versions
- Screenshots if applicable

### Suggesting Features

Have an idea? Open a [discussion](https://github.com/pvliesdonk/questfoundry-py/discussions) or [issue](https://github.com/pvliesdonk/questfoundry-py/issues) with:

- Feature description
- Use case and motivation
- Proposed implementation (optional)
- Related existing features

### Code Contributions

#### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/pvliesdonk/questfoundry-py.git
cd questfoundry-py
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev,docs]"
```

#### Development Workflow

1. Create a branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and add tests:
```bash
# Edit files
# Add tests in tests/ directory
```

3. Run tests to verify:
```bash
pytest tests/ -v
```

4. Run linting and type checks:
```bash
ruff check .
mypy src/
```

5. Commit with conventional commit format:
```bash
git commit -m "feat: add my new feature"
git commit -m "fix: resolve issue #123"
```

6. Push and create a Pull Request:
```bash
git push origin feature/your-feature-name
```

#### Commit Message Format

Use conventional commits:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style changes
- `refactor` - Code refactoring
- `perf` - Performance improvements
- `test` - Test additions/changes
- `chore` - Build/tool changes

**Examples:**
```bash
git commit -m "feat: add per-role configuration support"
git commit -m "fix(providers): resolve cache key generation"
git commit -m "docs: update installation guide"
git commit -m "test: add cache tests"
```

## Code Standards

### Style Guide

- Use [PEP 8](https://pep8.org/) for code style
- Use [ruff](https://github.com/astral-sh/ruff) for linting
- Use [mypy](https://mypy.readthedocs.io/) for type checking

### Docstrings

Use Google-style docstrings:

```python
def process_artifact(artifact: Artifact, role: str) -> bool:
    """
    Process an artifact through a specific role.

    Args:
        artifact: The artifact to process
        role: The role to process through

    Returns:
        True if processing was successful, False otherwise

    Raises:
        RoleError: If the role is invalid

    Example:
        >>> artifact = Artifact(type="hook_card", data={})
        >>> process_artifact(artifact, "gatekeeper")
        True
    """
    pass
```

### Type Hints

Add complete type hints:

```python
from typing import Optional
from questfoundry.models import Artifact

def get_artifact(artifact_id: str) -> Optional[Artifact]:
    """Get an artifact by ID."""
    pass

def process_artifacts(artifacts: list[Artifact]) -> dict[str, int]:
    """Process multiple artifacts."""
    pass
```

## Testing

### Writing Tests

```python
import pytest
from questfoundry.models import Artifact

class TestArtifact:
    """Tests for Artifact model."""

    def test_artifact_creation(self) -> None:
        """Test creating an artifact."""
        artifact = Artifact(
            type="hook_card",
            data={"title": "Test Hook"},
        )
        assert artifact.type == "hook_card"

    def test_artifact_with_invalid_type(self) -> None:
        """Test artifact with invalid type."""
        with pytest.raises(ValueError):
            Artifact(type="invalid_type", data={})
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_artifacts.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Documentation

### Writing Documentation

- Add docstrings to all public classes and functions
- Update README.md for significant changes
- Add guide pages in `docs/guides/` for new features
- Update API reference pages if applicable

### Building Documentation Locally

```bash
pip install -e ".[docs]"
mkdocs serve
```

Then visit http://localhost:8000 to view the docs.

## Pull Request Process

1. Update your branch with latest main:
```bash
git fetch origin
git rebase origin/main
```

2. Ensure all checks pass:
```bash
pytest tests/
ruff check .
mypy src/
```

3. Push and create PR with:
   - Clear title and description
   - Reference related issues
   - Mention any breaking changes
   - Add screenshots if UI-related

4. Respond to reviewer feedback

5. Once approved, maintainers will merge

## Release Process

Releases follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features
- **PATCH**: Bug fixes

Commits automatically trigger version bumps:
- `feat` commits → Minor version bump
- `fix` commits → Patch version bump
- `BREAKING CHANGE:` footer → Major version bump

## Getting Help

- 📖 Check the [documentation](index.md)
- 🐛 Search [existing issues](https://github.com/pvliesdonk/questfoundry-py/issues)
- 💬 Ask in [discussions](https://github.com/pvliesdonk/questfoundry-py/discussions)
- 📧 Email maintainers if needed

## Thank You!

Your contributions make QuestFoundry-Py better! 🎭
