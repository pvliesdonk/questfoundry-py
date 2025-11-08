# Getting Started

Welcome to QuestFoundry-Py! This guide will get you up and running with your first interactive narrative project in just a few minutes.

## Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- An API key from OpenAI, Gemini, or another supported provider
- Basic familiarity with Python

## Installation

The quickest way to get started is with pip:

```bash
pip install questfoundry-py
```

For development with all extras:

```bash
pip install questfoundry-py[dev,docs]
```

## Your First Project

### Step 1: Create a Project Directory

```bash
mkdir my_story_project
cd my_story_project
```

### Step 2: Initialize a Workspace

```python
from questfoundry.state.workspace import WorkspaceManager

workspace = WorkspaceManager("./workspace")
workspace.init_workspace(
    name="My First Story",
    description="An interactive fantasy adventure"
)

print("Workspace initialized!")
```

Save this as `init_project.py` and run it:

```bash
python init_project.py
```

### Step 3: Configure Your Provider

Create a `.questfoundry/config.yml` file:

```yaml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
      temperature: 0.7
```

Set your API key:

```bash
export OPENAI_API_KEY="sk-..."
```

### Step 4: Create a Simple Story

```python
from questfoundry.state.workspace import WorkspaceManager
from questfoundry.orchestrator import Orchestrator

# Initialize workspace
workspace = WorkspaceManager("./workspace")

# Create orchestrator
orchestrator = Orchestrator(workspace)

# Execute a story spark
result = orchestrator.execute_loop(
    loop_id="story_spark",
    project_id="my_story_project",
    config={
        "prompt": "A mysterious library hidden in the mountains",
        "style": "fantasy adventure"
    }
)

if result.success:
    print("✅ Story spark completed!")
    print(f"Artifacts created: {len(result.artifacts_created)}")
    for artifact in result.artifacts_created:
        print(f"  - {artifact.type}: {artifact.artifact_id}")
else:
    print(f"❌ Failed: {result.error}")
```

Save as `create_story.py` and run:

```bash
python create_story.py
```

## Understanding the Output

The story spark loop creates several artifacts:

1. **Hook Card** - The initial story concept
2. **Story Brief** - Detailed story information
3. **TU Brief** - First Thematic Unit (story segment)

These are stored in the workspace and can be accessed programmatically.

## Next Steps

### Explore More Loops

QuestFoundry includes 15+ specialized loops:

```python
# List available loops
from questfoundry.orchestrator import Orchestrator
orchestrator = Orchestrator(workspace)
available_loops = orchestrator.get_available_loops()

for loop_name, loop_info in available_loops.items():
    print(f"{loop_name}: {loop_info.description}")
```

### Configure Per-Role Settings

Use role-specific provider configuration to optimize costs:

```yaml
roles:
  gatekeeper:
    provider: openai
    model: gpt-4o  # Premium model for quality
  plotwright:
    provider: openai
    model: gpt-3.5-turbo  # Cheaper for planning
```

### Enable Caching

Reduce API calls and costs with response caching:

```yaml
providers:
  text:
    openai:
      cache:
        enabled: true
        ttl_seconds: 3600
```

### Set Rate Limits

Protect your budget with rate limiting:

```yaml
providers:
  text:
    openai:
      rate_limit:
        requests_per_minute: 30
        tokens_per_hour: 90000
        cost_per_day: 50.0
```

## Common Issues

### "API Key Not Found"

Make sure your environment variable is set:

```bash
export OPENAI_API_KEY="sk-..."
python create_story.py
```

Or set it in `.questfoundry/config.yml` directly (not recommended for production).

### "No Such File or Directory"

Ensure your workspace directory exists:

```python
import os
os.makedirs("./workspace", exist_ok=True)
```

### Rate Limit Exceeded

Implement backoff or reduce concurrent requests:

```python
import time

try:
    result = orchestrator.execute_loop("story_spark", params)
except RateLimitError:
    time.sleep(60)  # Wait a minute
    result = orchestrator.execute_loop("story_spark", params)
```

## Learn More

- **[Configuration Guide](guides/configuration.md)** - All configuration options
- **[API Reference](api/index.md)** - Complete API documentation
- **[Examples](examples/code-examples.md)** - More code examples
- **[Guides](guides/custom-providers.md)** - Create custom providers and roles

## Getting Help

- 📖 Check the [documentation](index.md)
- 🐛 Report issues on [GitHub](https://github.com/pvliesdonk/questfoundry-py/issues)
- 💬 Ask questions in [Discussions](https://github.com/pvliesdonk/questfoundry-py/discussions)

Good luck with your narrative project! 🎭
