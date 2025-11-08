# API Reference

Complete API reference for QuestFoundry-Py. This section documents all public modules, classes, and functions.

## Core Modules

### State Management
State management system for projects, thematic units, and snapshots.

- **[State Module](state.md)** - `questfoundry.state`
  - `WorkspaceManager` - Manage hot and cold storage
  - `StateStore` - State persistence
  - `SnapshotInfo` - Snapshot tracking

### Providers
AI provider integrations for text, image, and audio generation.

- **[Providers Module](providers.md)** - `questfoundry.providers`
  - Text providers (OpenAI, Gemini, Bedrock, Ollama)
  - Image providers (DALL-E, Imagen, A1111)
  - Audio providers (ElevenLabs)
  - Caching and rate limiting

### Roles
Role-based actors for narrative processing.

- **[Roles Module](roles.md)** - `questfoundry.roles`
  - `Gatekeeper` - Quality validation
  - `Plotwright` - Story planning
  - `Scene Smith` - Scene creation
  - Custom role creation

### Loops
Workflow orchestration for narrative processing.

- **[Loops Module](loops.md)** - `questfoundry.loops`
  - `StorySparkLoop` - Initial concept generation
  - `HookGenerationLoop` - Hook creation
  - `SceneForgeLoop` - Scene generation
  - And 12+ more specialized loops

### Protocol
Protocol definitions and artifact handling.

- **[Protocol Module](protocol.md)** - `questfoundry.protocol`
  - Message definitions
  - Request/response formats
  - Protocol versioning

### Validation
Schema validation and artifact validation.

- **[Validation Module](validation.md)** - `questfoundry.validators`
  - Artifact schema validation
  - Custom validators
  - Validation results

## Module Organization

```
questfoundry/
├── state/              # State management
├── providers/          # AI providers
├── roles/              # Narrative roles
├── loops/              # Workflow loops
├── protocol/           # Protocol definitions
├── validators/         # Validation system
├── models/             # Data models
└── orchestrator.py     # Main orchestration
```

## Common Patterns

### Creating a Workspace

```python
from questfoundry.state.workspace import WorkspaceManager

workspace = WorkspaceManager("./my_project")
workspace.init_workspace(name="My Project")
```

### Configuring Providers

```python
from questfoundry.providers.config import ProviderConfig

config = ProviderConfig.load("config.yml")
provider = config.get_provider_instance("openai", "text")
```

### Executing a Loop

```python
from questfoundry.orchestrator import Orchestrator

orchestrator = Orchestrator(workspace)
result = orchestrator.execute_loop("story_spark", {"prompt": "..."})
```

### Working with State

```python
from questfoundry.state.workspace import WorkspaceManager

workspace = WorkspaceManager("./my_project")
artifact = workspace.get_artifact("ARTIFACT-123")
snapshot = workspace.get_snapshot("SNAP-456")
```

## Error Handling

All exceptions inherit from `QuestFoundryError`:

```python
from questfoundry.exceptions import (
    QuestFoundryError,
    ProviderError,
    RoleError,
    LoopError,
    StateError,
)

try:
    result = orchestrator.execute_loop("story_spark", {})
except ProviderError as e:
    print(f"Provider error: {e}")
except RoleError as e:
    print(f"Role error: {e}")
except QuestFoundryError as e:
    print(f"QuestFoundry error: {e}")
```

## Type Hints

All modules are fully typed with type hints. You can use them in your IDE for better autocomplete and error checking.

## Next Steps

- **[Providers](providers.md)** - AI provider integration
- **[Roles](roles.md)** - Narrative role system
- **[Loops](loops.md)** - Workflow orchestration
- **[Configuration Guide](../guides/configuration.md)** - How to configure QuestFoundry

