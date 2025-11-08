# Code Examples

Practical code examples for common QuestFoundry-Py tasks.

## Creating a Workspace

```python
from questfoundry.state.workspace import WorkspaceManager

# Create workspace
workspace = WorkspaceManager("./my_project")

# Initialize with project info
workspace.init_workspace(
    name="My Story Project",
    description="An interactive fantasy adventure"
)

print("Workspace initialized!")
```

## Configuring Providers

### Using OpenAI

```yaml
# .questfoundry/config.yml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
      temperature: 0.7
      cache:
        enabled: true
```

### Per-Role Configuration

```yaml
providers:
  text:
    openai:
      model: gpt-4o

roles:
  gatekeeper:
    provider: openai
    model: gpt-4o  # Premium model for quality
  plotwright:
    provider: openai
    model: gpt-3.5-turbo  # Cheaper for planning
```

## Running a Simple Loop

```python
from questfoundry.orchestrator import Orchestrator
from questfoundry.state.workspace import WorkspaceManager

workspace = WorkspaceManager("./my_project")
orchestrator = Orchestrator(workspace)

# Execute story spark loop
result = orchestrator.execute_loop(
    loop_id="story_spark",
    project_id="my_project",
    config={
        "prompt": "A hidden library in the mountains",
        "style": "fantasy adventure"
    }
)

if result.success:
    print(f"✅ Loop completed!")
    print(f"Artifacts created: {len(result.artifacts_created)}")
    for artifact in result.artifacts_created:
        print(f"  - {artifact.type}: {artifact.artifact_id}")
else:
    print(f"❌ Failed: {result.error}")
```

## Accessing Artifacts

```python
from questfoundry.state.workspace import WorkspaceManager

workspace = WorkspaceManager("./my_project")

# Get specific artifact
artifact = workspace.get_artifact("ARTIFACT-123")
print(f"Artifact type: {artifact.type}")
print(f"Artifact data: {artifact.data}")

# List artifacts by type
hooks = workspace.list_artifacts(artifact_type="hook_card")
print(f"Found {len(hooks)} hooks")

# List artifacts in a snapshot
snapshot_artifacts = workspace.list_artifacts(snapshot_id="SNAP-456")
print(f"Snapshot contains {len(snapshot_artifacts)} artifacts")
```

## Managing State

### Saving Thematic Units

```python
from questfoundry.state.workspace import WorkspaceManager
from questfoundry.state.types import TUState

workspace = WorkspaceManager("./my_project")

# Create a TU
tu = TUState(
    tu_id="TU-2024-01-15-INTRO",
    status="in_progress",
    data={
        "title": "Introduction",
        "description": "The story begins...",
    }
)

# Save to hot storage (active/working)
workspace.save_tu(tu, target="hot")

# Later, promote to cold storage (archived)
workspace.promote_to_cold(tu.tu_id)
```

### Creating Snapshots

```python
from questfoundry.state.types import SnapshotInfo
from datetime import datetime

workspace = WorkspaceManager("./my_project")

# Create snapshot
snapshot = SnapshotInfo(
    snapshot_id="SNAP-001",
    tu_id="TU-2024-01-15-INTRO",
    description="After first draft completion"
)

workspace.save_snapshot(snapshot)

# Save artifacts to snapshot
artifact = workspace.get_artifact("ARTIFACT-123")
workspace.save_artifact(artifact, snapshot_id="SNAP-001")
```

### Exporting State

```python
workspace = WorkspaceManager("./my_project")

# Export to file
workspace.export_state(
    "export.yaml",
    include=["artifacts", "tus", "snapshots"]
)

# Import from file
workspace.import_state("export.yaml", merge=True)
```

## Error Handling

```python
from questfoundry.orchestrator import Orchestrator
from questfoundry.state.workspace import WorkspaceManager

workspace = WorkspaceManager("./my_project")
orchestrator = Orchestrator(workspace)

try:
    result = orchestrator.execute_loop(
        loop_id="story_spark",
        project_id="my_project",
        config={"prompt": "A story concept"}
    )

    if not result.success:
        print(f"Loop failed: {result.error}")
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
```

## Custom Provider

```python
from questfoundry.providers.base import TextProvider

class CustomProvider(TextProvider):
    """Custom text provider."""

    def validate_config(self) -> None:
        """Validate configuration."""
        if "api_key" not in self.config:
            raise ValueError("api_key required")

    def generate_text(
        self,
        prompt: str,
        model: str | None = None,
        **kwargs
    ) -> str:
        """Generate text using custom API."""
        # Your implementation here
        return "Generated text"

    def generate_text_streaming(
        self,
        prompt: str,
        model: str | None = None,
        **kwargs
    ):
        """Generate text streaming."""
        yield "chunk1"
        yield "chunk2"

# Use custom provider directly
provider = CustomProvider({"api_key": "your-api-key"})
text = provider.generate_text("Hello, world!")
print(f"Generated: {text}")
```

## Full Example: Mini Project

```python
from questfoundry.orchestrator import Orchestrator
from questfoundry.state.workspace import WorkspaceManager

def main():
    # Setup
    workspace = WorkspaceManager("./story_project")
    workspace.init_workspace(name="Short Story")
    orchestrator = Orchestrator(workspace)

    # Generate story concept
    result = orchestrator.execute_loop(
        loop_id="story_spark",
        project_id="time_travel_story",
        config={"prompt": "A time traveler arrives in ancient Rome"}
    )

    if not result.success:
        print(f"Failed: {result.error}")
        return

    print(f"✅ Story created with {len(result.artifacts_created)} artifacts")

    # List what was created
    artifacts = workspace.list_artifacts()
    for artifact in artifacts:
        print(f"  - {artifact.type}")

if __name__ == "__main__":
    main()
```

## More Resources

- **[Configuration Guide](../guides/configuration.md)** - All configuration options
- **[API Reference](../api/index.md)** - Complete API docs
- **[Guides](../guides/deployment.md)** - How-to guides
