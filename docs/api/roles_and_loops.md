# Roles and Loops API Reference

The `questfoundry.roles` and `questfoundry.loops` modules provide the role execution and loop orchestration systems. Roles are specialized agents that execute domain-specific tasks using LLM providers. Loops are workflows that coordinate multiple roles to produce and refine artifacts.

## Overview

**Roles** are specialized agents with domain expertise:
- Load prompts from the spec directory
- Execute tasks via configured LLM provider
- Produce structured outputs (text, artifacts, metadata)

**Loops** are multi-step workflows that:
- Coordinate multiple roles
- Manage artifact lifecycles
- Implement quality gates
- Produce complete work products

## Quick Start

### Using Roles

```python
from questfoundry.roles import RoleRegistry, RoleContext
from questfoundry.providers import ProviderRegistry, ProviderConfig
from questfoundry.models import Artifact

# Setup providers and roles
provider_config = ProviderConfig()
provider_registry = ProviderRegistry(provider_config)
text_provider = provider_registry.get_text_provider()

role_registry = RoleRegistry(text_provider)

# Get a role
showrunner = role_registry.get_role("showrunner")

# Create context
context = RoleContext(
    task="create_initial_hooks",
    project_metadata={"name": "Dragon Quest"},
    artifacts=[]
)

# Execute
result = showrunner.execute(context)

if result.success:
    print(f"Generated {len(result.artifacts)} artifacts")
    for artifact in result.artifacts:
        print(f"  - {artifact.type}: {artifact.artifact_id}")
else:
    print(f"Error: {result.error}")
```

### Using Loops

```python
from questfoundry.loops import LoopRegistry, LoopContext
from questfoundry.state import WorkspaceManager

# Setup
ws = WorkspaceManager("./project")
loop_registry = LoopRegistry(role_registry)

# Get loop
story_spark = loop_registry.get_loop("story_spark")

# Instantiate required roles
showrunner = role_registry.get_role("showrunner")
lore_weaver = role_registry.get_role("lore_weaver")

# Create context
loop_context = LoopContext(
    loop_id="story_spark",
    project_id="dragon-quest",
    workspace=ws,
    role_instances={"showrunner": showrunner, "lore_weaver": lore_weaver},
    project_metadata={"name": "Dragon Quest"}
)

# Execute loop
result = story_spark.execute(loop_context)

if result.success:
    print(f"Loop completed: {result.summary}")
    print(f"Artifacts produced: {len(result.artifacts)}")
else:
    print(f"Loop failed: {result.error}")
```

## Roles Module

### Role (Abstract Base Class)

Base class for all QuestFoundry roles. Each role is a specialized agent with domain expertise.

**Abstract Properties:**
- `role_name` (str): Role identifier (e.g., "showrunner", "gatekeeper")
- `description` (str): Human-readable description of role's purpose

**Constructor:**

```python
Role(
    provider: TextProvider,
    spec_path: Path | None = None,
    config: dict[str, Any] | None = None
)
```

**Parameters:**
- `provider`: Text provider for LLM interactions
- `spec_path`: Path to spec directory (default: ./spec)
- `config`: Role-specific configuration

**Abstract Method:**

#### `execute()`

```python
def execute(context: RoleContext) -> RoleResult
```

Execute the role's task based on provided context.

**Parameters:**
- `context`: RoleContext with task and artifacts

**Returns:** RoleResult with output and artifacts

### RoleContext

Context provided to a role for task execution.

**Attributes:**
- `task` (str): The specific task to execute (e.g., "generate_hooks")
- `artifacts` (list[Artifact]): Input artifacts available to the role
- `project_metadata` (dict[str, Any]): Project-level configuration and metadata
- `workspace_path` (Path | None): Path to workspace for file operations
- `additional_context` (dict[str, Any]): Any additional execution context

**Example:**
```python
from questfoundry.roles import RoleContext
from pathlib import Path

context = RoleContext(
    task="validate_hooks",
    artifacts=[hook1, hook2, hook3],
    project_metadata={
        "name": "Dragon Quest",
        "genre": "fantasy",
        "setting": "medieval"
    },
    workspace_path=Path("./project"),
    additional_context={"tu_id": "TU-2025-11-07-SR01"}
)
```

### RoleResult

Result of a role execution.

**Attributes:**
- `success` (bool): Whether the task completed successfully
- `output` (str): Primary output from the role (could be text, JSON, etc.)
- `artifacts` (list[Artifact]): Artifacts produced or modified by this role
- `metadata` (dict[str, Any]): Additional metadata about the execution
- `error` (str | None): Error message if success=False

**Example:**
```python
result = role.execute(context)

if result.success:
    print(f"Output: {result.output}")
    print(f"Produced {len(result.artifacts)} artifacts")
    print(f"Metadata: {result.metadata}")
else:
    print(f"Error: {result.error}")
```

### RoleRegistry

Registry for discovering and instantiating roles.

**Constructor:**

```python
RoleRegistry(
    text_provider: TextProvider,
    spec_path: Path | None = None
)
```

**Parameters:**
- `text_provider`: Default text provider for roles
- `spec_path`: Path to spec directory

**Methods:**

#### `get_role()`

```python
def get_role(
    role_name: str,
    provider: TextProvider | None = None
) -> Role
```

Get or create a role instance.

**Parameters:**
- `role_name`: Role identifier (e.g., "showrunner", "gatekeeper")
- `provider`: Optional provider override (uses default if None)

**Returns:** Role instance

**Example:**
```python
registry = RoleRegistry(text_provider)

# Get roles
showrunner = registry.get_role("showrunner")
gatekeeper = registry.get_role("gatekeeper")
lore_weaver = registry.get_role("lore_weaver")

# Use custom provider
custom_provider = ...
scene_smith = registry.get_role("scene_smith", provider=custom_provider)
```

#### `list_roles()`

```python
def list_roles() -> list[str]
```

List all available role names.

**Example:**
```python
roles = registry.list_roles()
print(f"Available roles: {roles}")
# Output: ['showrunner', 'gatekeeper', 'lore_weaver', 'scene_smith', ...]
```

### Available Roles

The following roles are available in the system:

**Core Orchestration:**
- **showrunner** - Loop orchestration and workflow management
- **gatekeeper** - Quality validation and gate checking

**Content Creation:**
- **lore_weaver** - World-building and canon management
- **scene_smith** - Scene writing and narrative development
- **plotwright** - Plot structure and story arcs
- **codex_curator** - Codex entries and encyclopedic content

**Style and Presentation:**
- **style_lead** - Style guide enforcement and consistency

**Asset Generation:**
- **art_director** - Visual direction and art planning
- **illustrator** - Image generation
- **audio_director** - Audio direction and planning
- **audio_producer** - Audio generation

**Support:**
- **player_narrator** - Player-facing content and playtest
- **book_binder** - Export and rendering
- **researcher** - Research and reference gathering
- **translator** - Localization and translation

## Loops Module

### Loop (Abstract Base Class)

Base class for all QuestFoundry loops. Loops are multi-step workflows that coordinate roles.

**Abstract Properties:**
- `loop_id` (str): Loop identifier (e.g., "story_spark")
- `metadata` (LoopMetadata): Loop metadata (name, description, etc.)

**Constructor:**

```python
Loop(role_registry: RoleRegistry, config: dict[str, Any] | None = None)
```

**Parameters:**
- `role_registry`: Registry for accessing roles
- `config`: Loop-specific configuration

**Abstract Method:**

#### `execute()`

```python
def execute(context: LoopContext) -> LoopResult
```

Execute the complete loop workflow.

**Parameters:**
- `context`: LoopContext with workspace and roles

**Returns:** LoopResult with success status and artifacts

### LoopMetadata

Metadata about a loop for selection and documentation.

**Attributes:**
- `loop_id` (str): Loop identifier
- `name` (str): Display name
- `description` (str): What the loop accomplishes
- `primary_roles` (list[str]): Roles required for this loop
- `input_artifact_types` (list[str]): Expected input types
- `output_artifact_types` (list[str]): Produced output types
- `estimated_duration` (str): Human-readable duration estimate
- `complexity` (str): "simple", "moderate", or "complex"
- `prerequisites` (list[str]): Required prior loops or conditions

**Example:**
```python
metadata = LoopMetadata(
    loop_id="story_spark",
    name="Story Spark",
    description="Generate initial story hooks and world foundation",
    primary_roles=["showrunner", "lore_weaver"],
    input_artifact_types=[],
    output_artifact_types=["hook_card", "canon_pack"],
    estimated_duration="5-10 minutes",
    complexity="simple",
    prerequisites=[]
)
```

### LoopContext

Context for active loop execution.

**Attributes:**
- `loop_id` (str): ID of the loop being executed
- `project_id` (str): ID of the project
- `workspace` (WorkspaceManager): Workspace for artifact storage
- `role_instances` (dict[str, Role]): Instantiated role objects keyed by name
- `artifacts` (list[Artifact]): Artifacts available for this loop
- `project_metadata` (dict[str, Any]): Project-level metadata
- `current_step` (int): Index of currently executing step
- `history` (list[dict]): Execution history
- `config` (dict[str, Any]): Loop configuration

**Example:**
```python
from questfoundry.loops import LoopContext

context = LoopContext(
    loop_id="hook_harvest",
    project_id="dragon-quest",
    workspace=ws,
    role_instances={
        "showrunner": showrunner,
        "lore_weaver": lore_weaver,
        "gatekeeper": gatekeeper,
    },
    artifacts=existing_hooks,
    project_metadata={"name": "Dragon Quest", "genre": "fantasy"},
    config={"hook_count": 10}
)
```

### LoopResult

Result of loop execution.

**Attributes:**
- `success` (bool): Whether loop completed successfully
- `artifacts` (list[Artifact]): Artifacts produced by the loop
- `summary` (str): Human-readable summary of what happened
- `steps_completed` (int): Number of steps successfully completed
- `total_steps` (int): Total number of steps in loop
- `metadata` (dict[str, Any]): Additional execution metadata
- `error` (str | None): Error message if success=False

**Example:**
```python
result = loop.execute(context)

print(f"Success: {result.success}")
print(f"Steps: {result.steps_completed}/{result.total_steps}")
print(f"Summary: {result.summary}")
print(f"Artifacts: {len(result.artifacts)}")

if not result.success:
    print(f"Error: {result.error}")
```

### LoopStep

Single step in a loop execution.

**Attributes:**
- `step_id` (str): Unique identifier for this step
- `description` (str): What this step does
- `assigned_roles` (list[str]): Roles that perform this step (RACI: Responsible)
- `consulted_roles` (list[str]): Roles that provide input (RACI: Consulted)
- `informed_roles` (list[str]): Roles that receive updates (RACI: Informed)
- `artifacts_input` (list[str]): Required artifact types for input
- `artifacts_output` (list[str]): Expected artifact types to produce
- `validation_required` (bool): Whether validation is required before proceeding
- `status` (StepStatus): Current status (pending, in_progress, completed, failed, skipped)
- `result` (Any | None): Result of executing this step
- `error` (str | None): Error message if step failed

**Example:**
```python
from questfoundry.loops import LoopStep, StepStatus

step = LoopStep(
    step_id="generate_hooks",
    description="Generate initial story hooks",
    assigned_roles=["lore_weaver"],
    consulted_roles=["showrunner"],
    informed_roles=["gatekeeper"],
    artifacts_input=[],
    artifacts_output=["hook_card"],
    validation_required=True,
    status=StepStatus.PENDING
)
```

### StepStatus (Enum)

Status of a loop step.

**Values:**
- `PENDING` = "pending"
- `IN_PROGRESS` = "in_progress"
- `COMPLETED` = "completed"
- `FAILED` = "failed"
- `SKIPPED` = "skipped"

### LoopRegistry

Registry for discovering and instantiating loops.

**Constructor:**

```python
LoopRegistry(role_registry: RoleRegistry)
```

**Parameters:**
- `role_registry`: Registry for accessing roles

**Methods:**

#### `get_loop()`

```python
def get_loop(loop_id: str) -> Loop
```

Get or create a loop instance.

**Parameters:**
- `loop_id`: Loop identifier (e.g., "story_spark")

**Returns:** Loop instance

**Example:**
```python
loop_registry = LoopRegistry(role_registry)

# Get loops
story_spark = loop_registry.get_loop("story_spark")
hook_harvest = loop_registry.get_loop("hook_harvest")
scene_forge = loop_registry.get_loop("scene_forge")
```

#### `list_loops()`

```python
def list_loops() -> list[LoopMetadata]
```

List all available loops with their metadata.

**Returns:** List of LoopMetadata objects

**Example:**
```python
loops = loop_registry.list_loops()

for meta in loops:
    print(f"{meta.name} ({meta.loop_id})")
    print(f"  {meta.description}")
    print(f"  Roles: {', '.join(meta.primary_roles)}")
    print(f"  Duration: {meta.estimated_duration}")
    print()
```

### Available Loops

**Currently Implemented:**
- **story_spark** - Generate initial story hooks and world foundation

**Planned (Have Playbooks):**
- **hook_harvest** - Expand and refine story hooks
- **canon_expansion** - Deepen world lore and canon
- **scene_forge** - Write narrative scenes
- **codex_expansion** - Create codex entries
- **style_tuneup** - Refine style consistency
- **gatecheck** - Run quality validation
- **binding_run** - Export and render content
- **art_touchup** - Generate/refine visual assets
- **audio_pass** - Generate audio assets
- **translation_pass** - Localize content
- **archive_snapshot** - Create project snapshots
- **post_mortem** - Retrospective analysis
- **narration_dryrun** - Playtest preparation

## Usage Patterns

### Complete Role Execution

```python
from questfoundry.roles import RoleRegistry, RoleContext
from questfoundry.providers import ProviderRegistry, ProviderConfig

# Setup
config = ProviderConfig()
provider_reg = ProviderRegistry(config)
text_provider = provider_reg.get_text_provider("openai")

role_registry = RoleRegistry(text_provider)

# Get role
lore_weaver = role_registry.get_role("lore_weaver")

# Create context
context = RoleContext(
    task="create_initial_canon",
    project_metadata={
        "name": "Dragon's Legacy",
        "genre": "fantasy",
        "themes": ["heroism", "sacrifice", "redemption"]
    }
)

# Execute
result = lore_weaver.execute(context)

if result.success:
    # Process artifacts
    for artifact in result.artifacts:
        if artifact.type == "canon_pack":
            print(f"Canon: {artifact.data.get('title')}")
            # Save to workspace
            ws.save_hot_artifact(artifact)
else:
    print(f"Error: {result.error}")
```

### Complete Loop Execution

```python
from questfoundry.loops import LoopRegistry, LoopContext
from questfoundry.state import WorkspaceManager

# Setup
ws = WorkspaceManager("./dragon-legacy")
role_registry = RoleRegistry(text_provider)
loop_registry = LoopRegistry(role_registry)

# Get loop
story_spark = loop_registry.get_loop("story_spark")

# Prepare roles
roles = {
    "showrunner": role_registry.get_role("showrunner"),
    "lore_weaver": role_registry.get_role("lore_weaver"),
    "gatekeeper": role_registry.get_role("gatekeeper"),
}

# Create context
context = LoopContext(
    loop_id="story_spark",
    project_id="dragon-legacy",
    workspace=ws,
    role_instances=roles,
    project_metadata={
        "name": "Dragon's Legacy",
        "genre": "fantasy"
    }
)

# Execute
result = story_spark.execute(context)

print(f"Success: {result.success}")
print(f"Summary: {result.summary}")

# Save artifacts
for artifact in result.artifacts:
    ws.save_hot_artifact(artifact)

print(f"Generated {len(result.artifacts)} artifacts")
```

### Multi-Role Collaboration

```python
# Setup roles
roles = {
    "lore_weaver": role_registry.get_role("lore_weaver"),
    "scene_smith": role_registry.get_role("scene_smith"),
    "gatekeeper": role_registry.get_role("gatekeeper"),
}

# Step 1: Lore Weaver creates canon
lw_context = RoleContext(
    task="create_canon",
    project_metadata={"name": "Quest"}
)
lw_result = roles["lore_weaver"].execute(lw_context)

# Step 2: Scene Smith uses canon
ss_context = RoleContext(
    task="write_scene",
    artifacts=lw_result.artifacts,  # Canon from lore weaver
    project_metadata={"name": "Quest"}
)
ss_result = roles["scene_smith"].execute(ss_context)

# Step 3: Gatekeeper validates
gk_context = RoleContext(
    task="validate",
    artifacts=ss_result.artifacts,  # Scene from scene smith
    project_metadata={"name": "Quest"}
)
gk_result = roles["gatekeeper"].execute(gk_context)

if gk_result.success:
    # Validation passed, promote to cold
    for artifact in ss_result.artifacts:
        ws.promote_to_cold(artifact.artifact_id)
```

### Custom Loop Steps

```python
from questfoundry.loops import LoopStep, StepStatus

# Define custom loop steps
steps = [
    LoopStep(
        step_id="brainstorm",
        description="Brainstorm initial concepts",
        assigned_roles=["lore_weaver"],
        artifacts_output=["hook_card"],
    ),
    LoopStep(
        step_id="validate",
        description="Validate concepts",
        assigned_roles=["gatekeeper"],
        consulted_roles=["lore_weaver"],
        artifacts_input=["hook_card"],
        artifacts_output=["gatecheck_report"],
        validation_required=True,
    ),
    LoopStep(
        step_id="refine",
        description="Refine approved concepts",
        assigned_roles=["lore_weaver"],
        artifacts_input=["hook_card", "gatecheck_report"],
        artifacts_output=["hook_card"],
    ),
]

# Execute steps sequentially
for step in steps:
    step.status = StepStatus.IN_PROGRESS
    try:
        # Execute step logic
        # ...
        step.status = StepStatus.COMPLETED
    except Exception as e:
        step.status = StepStatus.FAILED
        step.error = str(e)
        break
```

### Error Handling

```python
# Role execution with error handling
try:
    result = role.execute(context)

    if not result.success:
        # Handle role failure
        print(f"Role failed: {result.error}")
        # Log for review
        # Retry with modified context
        # Or escalate to human
    else:
        # Process success
        pass

except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {e}")
    # Log exception
    # Clean up resources
```

## Best Practices

1. **Use role registry** for role instantiation:
   ```python
   # Good - managed instances
   role = role_registry.get_role("showrunner")

   # Avoid - manual instantiation
   role = ShowrunnerRole(provider)
   ```

2. **Provide complete context**:
   ```python
   context = RoleContext(
       task="clear_task_description",
       artifacts=relevant_artifacts,  # Only what's needed
       project_metadata=full_metadata,  # All project info
       additional_context={"tu_id": "..."}  # Extra details
   )
   ```

3. **Check results before proceeding**:
   ```python
   result = role.execute(context)
   if not result.success:
       # Handle error before continuing
       return

   # Now safe to use result.artifacts
   ```

4. **Use loops for complex workflows**:
   ```python
   # Good - coordinated workflow
   loop = loop_registry.get_loop("story_spark")
   result = loop.execute(context)

   # Avoid - manual coordination
   role1.execute(...)
   role2.execute(...)
   # ... error-prone
   ```

5. **Save artifacts promptly**:
   ```python
   result = role.execute(context)
   for artifact in result.artifacts:
       ws.save_hot_artifact(artifact)  # Save immediately
   ```

6. **Cache role instances**:
   ```python
   # Good - reuse instances
   roles = {
       name: role_registry.get_role(name)
       for name in ["showrunner", "lore_weaver", "gatekeeper"]
   }

   # Use throughout session
   roles["lore_weaver"].execute(...)
   ```

## See Also

- [Provider API](providers.md) - LLM provider configuration
- [State Management API](state.md) - Workspace and artifacts
- [Validation API](validation.md) - Quality gates
