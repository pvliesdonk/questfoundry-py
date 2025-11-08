# Epic 16.1 - Comprehensive Documentation Design

## Overview

Create a professional MkDocs-based documentation site with API reference, guides, examples, and tutorials.

## Design Decisions

### 1. Documentation Tool: MkDocs vs Sphinx

**Decision**: MkDocs with Material theme

**Rationale**:
- **MkDocs**: Simple, fast, modern
  - Easy to write (just Markdown)
  - Beautiful Material theme
  - Good search functionality
  - Easy to deploy (static site)
  - Better for user-facing docs

- **Sphinx**: Complex but powerful
  - Better for complex API docs
  - More customization
  - Steeper learning curve
  - Older ecosystem

**MkDocs wins for**:
- User-friendly
- Modern look
- Quick to set up
- Markdown native
- Great Material theme

### 2. Site Structure

Four main sections:

1. **Getting Started** - For new users
   - Installation
   - First project
   - Quick examples

2. **API Reference** - For developers
   - Auto-generated from code
   - All public classes/functions
   - Examples in docstrings

3. **Guides** - For practitioners
   - Configuration
   - Custom providers/roles
   - Best practices
   - Deployment

4. **Examples** - Learning by doing
   - Minimal project
   - Fantasy adventure
   - Sci-fi world
   - Code snippets

### 3. Docstring Style: Google

**Decision**: Google-style docstrings

**Format**:
```python
def generate_text(
    self,
    prompt: str,
    model: str | None = None,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> str:
    """Generate text from a prompt.

    Calls the LLM provider with the given prompt and returns
    the generated text. Results are cached if caching is enabled.

    Args:
        prompt: The input prompt for text generation
        model: Model to use (uses default if not specified)
        max_tokens: Maximum tokens to generate
        **kwargs: Additional provider-specific parameters

    Returns:
        Generated text response

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If generation fails

    Example:
        ```python
        provider = OpenAIProvider({"api_key": "..."})
        text = provider.generate_text("Hello world")
        print(text)
        ```
    """
```

**Rationale**:
- mkdocstrings supports Google style natively
- More readable in source code
- Standard in Python community

### 4. API Documentation Generation

**Strategy**: Auto-generate from code using mkdocstrings

```yaml
# mkdocs.yml plugin config
plugins:
  - mkdocstrings:
      handlers:
        python:
          docstring_style: google
          show_source: true
          show_root_heading: true
          show_root_toc_entry: false
```

**Coverage**:
- All public modules
- All public classes
- All public functions/methods
- Important private utilities (with underscore prefix)

### 5. Example Organization

Four types of examples:

1. **Code Snippets** - In API docs and guides
   - 5-10 line examples
   - Demonstrate single concept
   - Runnable code blocks

2. **Minimal Example** - `examples/minimal-project.md`
   - Complete runnable project
   - ~50 lines Python
   - Shows core concepts

3. **Full Examples** - Fantasy, Sci-Fi projects
   - ~200 lines each
   - Real-world scenarios
   - Multiple features

4. **How-To Guides** - Configuration, custom roles
   - Step-by-step instructions
   - Common patterns
   - Troubleshooting tips

### 6. Navigation Structure

```
Home (index)
├── Getting Started
│   ├── Installation
│   ├── First Project
│   └── Configuration
├── API Reference
│   ├── Providers
│   ├── Roles
│   ├── Loops
│   ├── State Management
│   ├── Protocol
│   └── Validation
├── Guides
│   ├── Configuration
│   ├── Per-Role Config
│   ├── Caching Strategy
│   ├── Custom Providers
│   ├── Custom Roles
│   └── Deployment
├── Examples
│   ├── Minimal Project
│   ├── Fantasy Adventure
│   ├── Sci-Fi World
│   └── Code Snippets
├── Changelog
└── Contributing
```

## Implementation Details

### MkDocs Configuration

```yaml
# mkdocs.yml
site_name: QuestFoundry-Py
site_description: "Python library for interactive narrative creation"
site_url: https://questfoundry.liesdonk.nl/
repo_url: https://github.com/pvliesdonk/questfoundry-py
repo_name: questfoundry-py
edit_uri: edit/main/docs/

theme:
  name: material
  logo: assets/logo.png
  favicon: assets/favicon.ico
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

  features:
    - navigation.instant
    - navigation.instant.prefetch
    - navigation.instant.progress
    - navigation.tracking
    - navigation.top
    - navigation.expand
    - content.code.copy
    - content.code.select
    - content.code.annotate
    - search.suggest
    - search.highlight
    - search.share
    - toc.integrate

plugins:
  - search:
      lang: en
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          import_prefix:
            - questfoundry
          docstring_style: google
          show_source: true
          show_root_heading: true
          show_root_members_full_path: false
          show_root_full_path: false
          show_object_full_path: false
          heading_level: 2
          members_order: source
  - awesome-pages
  - callouts

markdown_extensions:
  - md_in_html
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: python
          class: python
          format: "!!python {input}"
  - pymdownx.highlight:
      use_pygments: true
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - toc:
      permalink: true

extra:
  version:
    provider: mike
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/pvliesdonk
    - icon: fontawesome/brands/python
      link: https://pypi.org/project/questfoundry-py/
```

### Essential Documentation Files

#### 1. index.md (Home Page)

```markdown
# QuestFoundry-Py

Python library for creating rich, interactive narratives using LLM-powered agents.

## Features

- 🤖 **14+ AI Roles** - Specialized agents for different narrative tasks
- 🔄 **Multi-Step Loops** - Orchestrate complex workflows
- 🗂️ **State Management** - Persistent project state with hot/cold storage
- ✅ **Quality Gates** - 8 validation bars for content quality
- 🎨 **Multi-Provider** - OpenAI, Ollama, Gemini, and more
- 📦 **Fully Typed** - Complete type hints for IDE support

## Quick Start

```python
from questfoundry.state import WorkspaceManager

# Initialize a new project
ws = WorkspaceManager("my-adventure")
ws.init_workspace(name="Dragon's Legacy", author="Alice")

# Run a workflow
from questfoundry.orchestrator import Showrunner
showrunner = Showrunner()
result = showrunner.execute_loop("story_spark", ws)
```

## Installation

```bash
pip install questfoundry-py[openai]
```

[Read the getting started guide →](getting-started.md)

## What's New

- ✨ Epic 15: Caching, rate limiting, per-role configuration
- 📚 Comprehensive documentation site
- 🚀 Automated releases to PyPI

[See changelog →](changelog.md)
```

#### 2. getting-started.md

```markdown
# Getting Started

This guide walks you through creating your first interactive narrative project.

## Prerequisites

- Python 3.11+
- An API key for at least one provider (OpenAI, Gemini, etc.)

## Installation

### Basic Installation

For OpenAI:
```bash
pip install questfoundry-py[openai]
```

For Ollama (local):
```bash
pip install questfoundry-py
```

For all providers:
```bash
pip install questfoundry-py[all-providers]
```

### Verify Installation

```python
from questfoundry import __version__
print(f"QuestFoundry v{__version__}")
```

## Create Your First Project

### 1. Initialize a Workspace

```python
from questfoundry.state import WorkspaceManager

ws = WorkspaceManager("my-adventure")
ws.init_workspace(
    name="My First Adventure",
    description="A test narrative project",
    author="Your Name"
)
```

### 2. Create Content

```python
from questfoundry.models import Artifact

# Create a hook (narrative hook)
hook = Artifact(
    type="Hook",
    data={
        "title": "The Mysterious Door",
        "content": "A door appears in the forest..."
    }
)

ws.add_artifact(hook)
```

### 3. Run a Workflow

```python
from questfoundry.orchestrator import Showrunner

showrunner = Showrunner()
result = showrunner.execute_loop("story_spark", ws)

print(f"Success: {result.success}")
print(f"Output: {result.output}")
```

## Next Steps

- [Configuration Guide](guides/configuration.md)
- [Explore Available Roles](api/roles.md)
- [See Code Examples](examples/code-examples.md)
- [Custom Providers](guides/custom-providers.md)
```

#### 3. guides/configuration.md

```markdown
# Configuration Guide

QuestFoundry is configured using a YAML file.

## Configuration File

By default, QuestFoundry looks for `.questfoundry/config.yml`.

```yaml
# .questfoundry/config.yml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
    ollama:
      base_url: http://localhost:11434
      model: llama3

caching:
  enabled: true
  ttl_seconds: 86400

rate_limiting:
  global:
    requests_per_minute: 100
```

## Environment Variables

Sensitive values use environment variables:

```yaml
providers:
  text:
    openai:
      api_key: ${OPENAI_API_KEY}  # Read from environment
```

Set with:
```bash
export OPENAI_API_KEY="sk-..."
```

## Per-Role Configuration

See [Per-Role Configuration Guide](per-role-config.md)

## All Options

See [API Reference: Configuration](../api/configuration.md)
```

### Documentation Build & Deploy

#### Build Locally

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs serve
```

#### Deploy to GitHub Pages

```yaml
# .github/workflows/docs-deploy.yml
name: Deploy Docs

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: pip

      - run: |
          pip install mkdocs mkdocs-material mkdocstrings[python]
          mkdocs build

      - uses: actions/upload-artifact@v3
        with:
          name: docs
          path: site/

      - uses: peaceiris/actions-gh-pages@v3
        if: github.ref == 'refs/heads/main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

## Docstring Audit Checklist

Before release, verify all public APIs have docstrings:

```bash
# Check coverage
python -m pydoc_coverage src/questfoundry/

# Required sections:
# - Brief description
# - Args
# - Returns
# - Raises
# - Example (for important functions)
```

## Testing Documentation

All code examples should be valid Python:

```bash
# Extract and test code examples
python -m doctest -v src/questfoundry/providers/base.py
```

## Documentation Standards

### Docstring Structure

```python
def function(param1: str, param2: int) -> bool:
    """One-line summary (imperative mood).

    Longer description explaining what this function does,
    why you might use it, and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Description of return value

    Raises:
        ValueError: When validation fails
        RuntimeError: When operation fails

    Example:
        ```python
        result = function("test", 42)
        assert result is True
        ```
    """
```

### Markdown Style

- **Headers**: Use `#` for h1, `##` for h2, etc.
- **Code blocks**: Use triple backticks with language
- **Inline code**: Use backticks
- **Links**: Use `[text](path)` format
- **Admonitions**: Use !!! note, !!! warning, !!! tip

### Link Conventions

- Relative links: `[API](../api/providers.md)`
- Heading links: `[Installation](#installation)`
- External: Full URLs

## Site Performance

- Minified CSS/JS
- Image optimization
- Search indexing
- Mobile responsive
- Fast page loads (<2s)

## Accessibility

- Proper heading hierarchy
- Alt text for images
- Color not sole method of distinction
- Keyboard navigation
- Screen reader friendly
