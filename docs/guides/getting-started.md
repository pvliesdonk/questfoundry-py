# Getting Started with QuestFoundry

This guide will help you get started with QuestFoundry, from installation to creating your first interactive narrative project.

## Installation

### Prerequisites

- Python 3.10 or later
- pip or uv package manager
- (Optional) Git for version control

### Install QuestFoundry

```bash
# Install with pip
pip install questfoundry-py

# Or with uv (recommended)
uv pip install questfoundry-py

# Install with provider support
pip install questfoundry-py[openai]  # For OpenAI integration
pip install questfoundry-py[all]     # All optional dependencies
```

### Verify Installation

```python
import questfoundry
print(questfoundry.__version__)
```

## Initial Setup

### 1. Set Up Environment Variables

Create a `.env` file in your project directory:

```bash
# OpenAI (if using)
OPENAI_API_KEY=sk-your-api-key-here

# Or Ollama (if using local models)
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. Initialize a Project

```python
from questfoundry.state import WorkspaceManager

# Create and initialize workspace
ws = WorkspaceManager("./my-adventure")
ws.init_workspace(
    name="My First Adventure",
    description="An epic fantasy quest",
    author="Your Name"
)

print("Project initialized!")
```

This creates:
```
my-adventure/
  .questfoundry/
    hot/              # Work-in-progress files
    metadata.json     # Project configuration
  project.qfproj      # SQLite database
```

### 3. Configure Providers

Create `.questfoundry/config.yml`:

```yaml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o

  image:
    default: dalle
    dalle:
      api_key: ${OPENAI_API_KEY}
      model: dall-e-3
```

## Your First Workflow

### Step 1: Create Artifacts

```python
from questfoundry.models import Artifact

# Create a hook (story concept)
hook = Artifact(
    type="hook_card",
    data={
        "hook_id": "HOOK-001",
        "title": "The Dragon's Awakening",
        "concept": "An ancient dragon stirs after a thousand years of slumber",
        "stakes": "The kingdom faces destruction unless heroes intervene",
        "twist": "The dragon was protecting the kingdom, not threatening it"
    },
    metadata={"temperature": "hot", "status": "draft"}
)

# Save to workspace
ws.save_hot_artifact(hook)
print(f"Created hook: {hook.data['hook_id']}")
```

### Step 2: Validate Content

```python
from questfoundry.validation import Gatekeeper

# Get all hot artifacts
artifacts = ws.list_hot_artifacts()

# Run quality check
gatekeeper = Gatekeeper()
report = gatekeeper.run_gatecheck(artifacts)

if report.passed:
    print("✓ All quality checks passed")
else:
    print(f"✗ Found {len(report.blockers)} issues:")
    for bar_name, issue in report.blockers:
        print(f"  [{bar_name}] {issue.message}")
```

### Step 3: Promote to Cold Storage

```python
if report.passed:
    # Promote approved content
    ws.promote_to_cold("HOOK-001")
    print("Hook promoted to cold storage")
```

### Step 4: Create a Snapshot

```python
from questfoundry.state import SnapshotInfo, TUState
from datetime import datetime

# Create TU (Thematic Unit)
tu = TUState(
    tu_id="TU-2025-11-07-SR01",
    status="completed",
    data={"brief": "Initial hook development"}
)
ws.save_tu(tu)

# Create snapshot
snapshot_id = "SNAP-2025-11-07-001"
snapshot = SnapshotInfo(
    snapshot_id=snapshot_id,
    tu_id=tu.tu_id,
    description="First hook complete"
)
ws.save_snapshot(snapshot)
print(f"Created snapshot: {snapshot_id}")
```

### Step 5: Generate a View and Export

```python
from questfoundry.export import ViewGenerator, BookBinder

# Generate player-safe view (using snapshot_id from previous step)
snapshot_id = "SNAP-2025-11-07-001"
view_gen = ViewGenerator(ws.cold_store)
view = view_gen.generate_view(snapshot_id)
print(f"View contains {len(view.artifacts)} player-safe artifacts")

# Render to HTML
binder = BookBinder()
html = binder.render_html(view, title="Chapter 1")
binder.save_html(html, "./output/chapter1.html")
print("Rendered to HTML!")
```

## Working with Providers

### Using OpenAI

```python
from questfoundry.providers import ProviderRegistry, ProviderConfig

# Setup
config = ProviderConfig()
registry = ProviderRegistry(config)

# Get provider
provider = registry.get_text_provider("openai")

# Generate text
response = provider.generate_text(
    prompt="Write a fantasy hook about a dragon",
    max_tokens=200,
    temperature=0.8
)
print(response)
```

### Using Local Models (Ollama)

```python
# Use Ollama for local generation
ollama = registry.get_text_provider("ollama")

response = ollama.generate_text(
    prompt="Describe a mystical forest",
    max_tokens=150
)
print(response)
```

## Next Steps

### Learn More

- [API Reference](../api/) - Detailed API documentation
- [State Management API](../api/state.md) - Working with hot/cold storage
- [Provider API](../api/providers.md) - Configuring LLM providers
- [Export API](../api/export.md) - Generating player-facing content

### Explore Advanced Features

1. **Role-Based Workflows**: Use specialized roles for different tasks
2. **Loop Orchestration**: Run multi-step workflows
3. **Quality Gates**: Enforce quality standards
4. **Git Export**: Version control your content

### Example Projects

See the `examples/` directory for complete project templates:
- `examples/fantasy-quest/` - Complete fantasy adventure
- `examples/sci-fi-mystery/` - Science fiction mystery
- `examples/minimal/` - Minimal starter project

## Common Tasks

### List All Artifacts

```python
# List hot artifacts
hot_artifacts = ws.list_hot_artifacts()
for artifact in hot_artifacts:
    print(f"{artifact.type}: {artifact.artifact_id}")

# List cold artifacts
cold_artifacts = ws.list_cold_artifacts("hook_card")
print(f"Found {len(cold_artifacts)} hooks in cold storage")
```

### Query by Type and Filters

```python
# Get draft hooks
drafts = ws.list_hot_artifacts(
    "hook_card",
    {"status": "draft"}
)

# Get approved canon
canon = ws.list_cold_artifacts(
    "canon_pack",
    {"status": "approved"}
)
```

### Update an Artifact

```python
# Get artifact
artifact = ws.get_hot_artifact("HOOK-001")

# Modify
artifact.data["concept"] += " - Now with more dragons!"
artifact.data["status"] = "revised"

# Save changes
ws.save_hot_artifact(artifact)
```

### Delete an Artifact

```python
# Delete from hot
ws.delete_hot_artifact("HOOK-001")

# Delete from cold
ws.delete_cold_artifact("HOOK-001")
```

## Troubleshooting

### Provider Configuration Issues

If you see `ValueError: Environment variable 'OPENAI_API_KEY' is not set`:

1. Create a `.env` file with your API key
2. Or set environment variable: `export OPENAI_API_KEY=sk-...`
3. Verify config.yml uses `${OPENAI_API_KEY}` syntax

### Import Errors

If you see `ModuleNotFoundError`:

```bash
# Install with provider support
pip install questfoundry-py[openai]

# Or install all dependencies
pip install questfoundry-py[all]
```

### Database Locked

If you see `database is locked`:

```python
# Always close connections
with WorkspaceManager("./project") as ws:
    # Use workspace
    pass
# Automatically closed

# Or manually
ws.close()
```

## Getting Help

- [Documentation](../api/) - Complete API reference
- [GitHub Issues](https://github.com/pvliesdonk/questfoundry-py/issues) - Report bugs
- [Discussions](https://github.com/pvliesdonk/questfoundry-py/discussions) - Ask questions
- [Specification](https://github.com/pvliesdonk/questfoundry-spec) - System design

## What's Next?

Now that you've completed the getting started guide, explore:

1. **[State Management](../api/state.md)** - Master hot/cold workflow
2. **[Providers](../api/providers.md)** - Configure LLM and image providers
3. **[Validation](../api/validation.md)** - Quality gates and gatekeeping
4. **[Export](../api/export.md)** - Generate player-facing content
5. **[Architecture](../../ARCHITECTURE.md)** - Understand the system design

Happy quest building! 🎮✨
