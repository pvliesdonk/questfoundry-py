# questfoundry-py

Python library for QuestFoundry protocol and artifact management (Layer 6).

## Installation

```bash
pip install questfoundry-py
```

Or with extras for development:

```bash
pip install questfoundry-py[dev]
```

## Quick Start

### Load and validate a schema

```python
from questfoundry import get_schema, validate_instance

# Load a schema
schema = get_schema("hook_card")

# Validate an instance
instance = {"type": "hook_card", "data": {}}
is_valid = validate_instance(instance, "hook_card")
```

### Load prompts

```python
from questfoundry import get_prompt

prompt = get_prompt("showrunner")
print(prompt)
```

### List available resources

```python
from questfoundry import list_schemas, list_prompts

schemas = list_schemas()
prompts = list_prompts()
```

## Architecture

This library (Layer 6) implements the QuestFoundry protocol specification (Layer 3-5).

```
Layer 3: Schemas
    ↓
Layer 4: Protocol & Envelopes
    ↓
Layer 5: Prompts
    ↓
Layer 6: Python Library (questfoundry-py) ← You are here
    ↓
Layer 7: CLI (questfoundry-cli)
```

## Documentation

- [Specification](https://github.com/pvliesdonk/questfoundry-spec)
- [API Reference](https://github.com/pvliesdonk/questfoundry-spec/tree/main/06-libraries)
- [Schemas](https://questfoundry.liesdonk.nl/schemas/)

## Development

### Setup

```bash
git clone https://github.com/pvliesdonk/questfoundry-py
cd questfoundry-py
git submodule add https://github.com/pvliesdonk/questfoundry-spec spec
uv sync
```

### Run tests

```bash
uv run pytest
```

### Run linter

```bash
uv run ruff check .
uv run mypy src
```

### Run pre-commit hooks

```bash
pre-commit run --all-files
```

## License

MIT

## Related Repositories

- [questfoundry-spec](https://github.com/pvliesdonk/questfoundry-spec) - Specification and schemas
- [questfoundry-cli](https://github.com/pvliesdonk/questfoundry-cli) - Command-line interface
