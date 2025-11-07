# State Management API Reference

The `questfoundry.state` module provides state persistence for QuestFoundry projects, implementing both hot workspace (file-based) and cold storage (SQLite) with the hot/cold Source of Truth pattern.

## Overview

QuestFoundry uses a dual-storage architecture:

- **Hot Workspace** (`.questfoundry/hot/`) - File-based, human-readable, work-in-progress
- **Cold Storage** (`project.qfproj`) - SQLite database, curated, stable snapshots

The state management module provides:

- **WorkspaceManager**: Unified interface for hot and cold storage
- **SQLiteStore**: Cold storage implementation (.qfproj files)
- **FileStore**: Hot workspace implementation (directory structure)
- **StateStore**: Abstract interface for storage backends
- **Data Models**: ProjectInfo, TUState, SnapshotInfo

## Quick Start

```python
from questfoundry.state import WorkspaceManager
from questfoundry.models import Artifact

# Initialize workspace
ws = WorkspaceManager("/path/to/project")
ws.init_workspace(
    name="Dragon Quest",
    description="Epic fantasy adventure",
    author="Alice"
)

# Create and save hot artifact
artifact = Artifact(
    type="hook_card",
    data={
        "hook_id": "HOOK-001",
        "title": "The Dragon's Lair",
        "concept": "Ancient dragon hoarding magical artifacts"
    },
    metadata={"temperature": "hot", "status": "draft"}
)
ws.save_hot_artifact(artifact)

# Promote to cold storage when ready
ws.promote_to_cold("HOOK-001")

# Query artifacts
hooks = ws.list_cold_artifacts("hook_card")
print(f"Found {len(hooks)} hooks in cold storage")
```

## WorkspaceManager

Unified manager for QuestFoundry workspace with both hot and cold storage.

### Constructor

```python
WorkspaceManager(project_dir: str | Path)
```

**Parameters:**
- `project_dir`: Path to project directory

**Directory Structure Created:**
```
project_dir/
  .questfoundry/
    hot/
      hooks/
      canon/
      tus/
      snapshots/
    metadata.json
  project.qfproj  # SQLite database
```

**Example:**
```python
from questfoundry.state import WorkspaceManager

ws = WorkspaceManager("./my-adventure")
```

### Workspace Initialization

#### `init_workspace()`

```python
def init_workspace(
    self,
    name: str,
    description: str = "",
    version: str = "1.0.0",
    author: str | None = None,
) -> None
```

Initialize a new workspace with hot and cold storage. Creates directory structure and initializes both stores with project metadata.

**Parameters:**
- `name`: Project name
- `description`: Project description (optional)
- `version`: Project version (default: "1.0.0")
- `author`: Project author (optional)

**Example:**
```python
ws = WorkspaceManager("./dragon-quest")
ws.init_workspace(
    name="Dragon Quest",
    description="An epic fantasy adventure",
    version="0.1.0",
    author="Alice Smith"
)
```

### Project Information

#### `get_project_info()`

```python
def get_project_info(self, source: str = "hot") -> ProjectInfo
```

Get project information from hot or cold storage.

**Parameters:**
- `source`: Storage source - "hot" or "cold" (default: "hot")

**Returns:** ProjectInfo object

**Raises:**
- `ValueError`: If source is invalid
- `FileNotFoundError`: If project metadata not found

**Example:**
```python
# Get from hot workspace
info = ws.get_project_info("hot")
print(f"Project: {info.name}, Version: {info.version}")

# Get from cold storage
cold_info = ws.get_project_info("cold")
```

#### `save_project_info()`

```python
def save_project_info(
    self,
    info: ProjectInfo,
    target: str = "both"
) -> None
```

Save project information to hot, cold, or both storages.

**Parameters:**
- `info`: ProjectInfo instance to save
- `target`: Where to save - "hot", "cold", or "both" (default: "both")

**Raises:**
- `ValueError`: If target is invalid

**Example:**
```python
from questfoundry.state import ProjectInfo

info = ws.get_project_info()
info.version = "0.2.0"
info.description = "Updated description"
ws.save_project_info(info, target="both")
```

### Hot Workspace Operations

Hot workspace contains work-in-progress artifacts that are actively being edited and reviewed.

#### `save_hot_artifact()`

```python
def save_hot_artifact(self, artifact: Artifact) -> None
```

Save artifact to hot workspace.

**Parameters:**
- `artifact`: Artifact instance to save

**Example:**
```python
artifact = Artifact(
    type="hook_card",
    data={"hook_id": "HOOK-001", "title": "Dragon Awakens"},
    metadata={"temperature": "hot", "status": "draft"}
)
ws.save_hot_artifact(artifact)
```

#### `get_hot_artifact()`

```python
def get_hot_artifact(self, artifact_id: str) -> Artifact | None
```

Get artifact from hot workspace.

**Parameters:**
- `artifact_id`: Unique artifact identifier

**Returns:** Artifact if found, None otherwise

**Example:**
```python
artifact = ws.get_hot_artifact("HOOK-001")
if artifact:
    print(f"Title: {artifact.data['title']}")
```

#### `list_hot_artifacts()`

```python
def list_hot_artifacts(
    self,
    artifact_type: str | None = None,
    filters: dict[str, Any] | None = None,
) -> list[Artifact]
```

List artifacts in hot workspace with optional filtering.

**Parameters:**
- `artifact_type`: Filter by type (e.g., "hook_card"), None for all types
- `filters`: Additional filters as key-value pairs

**Returns:** List of matching artifacts

**Example:**
```python
# List all hot hooks
hooks = ws.list_hot_artifacts("hook_card")

# List draft hooks
drafts = ws.list_hot_artifacts(
    "hook_card",
    {"status": "draft"}
)

# List all hot artifacts
all_hot = ws.list_hot_artifacts()
```

#### `delete_hot_artifact()`

```python
def delete_hot_artifact(self, artifact_id: str) -> bool
```

Delete artifact from hot workspace.

**Parameters:**
- `artifact_id`: Unique artifact identifier

**Returns:** True if deleted, False if not found

**Example:**
```python
if ws.delete_hot_artifact("HOOK-001"):
    print("Artifact deleted")
else:
    print("Artifact not found")
```

### Cold Storage Operations

Cold storage contains curated, stable artifacts that have been reviewed and promoted from hot workspace.

#### `save_cold_artifact()`

```python
def save_cold_artifact(self, artifact: Artifact) -> None
```

Save artifact to cold storage.

**Parameters:**
- `artifact`: Artifact instance to save

**Example:**
```python
artifact = Artifact(
    type="hook_card",
    data={"hook_id": "HOOK-001", "title": "Dragon Awakens"},
    metadata={"temperature": "cold", "status": "approved"}
)
ws.save_cold_artifact(artifact)
```

#### `get_cold_artifact()`

```python
def get_cold_artifact(self, artifact_id: str) -> Artifact | None
```

Get artifact from cold storage.

**Parameters:**
- `artifact_id`: Unique artifact identifier

**Returns:** Artifact if found, None otherwise

**Example:**
```python
artifact = ws.get_cold_artifact("HOOK-001")
if artifact:
    print(f"Curated hook: {artifact.data['title']}")
```

#### `list_cold_artifacts()`

```python
def list_cold_artifacts(
    self,
    artifact_type: str | None = None,
    filters: dict[str, Any] | None = None,
) -> list[Artifact]
```

List artifacts in cold storage with optional filtering.

**Parameters:**
- `artifact_type`: Filter by type (e.g., "hook_card"), None for all types
- `filters`: Additional filters as key-value pairs

**Returns:** List of matching artifacts

**Example:**
```python
# List all cold hooks
hooks = ws.list_cold_artifacts("hook_card")

# List approved canon
canon = ws.list_cold_artifacts(
    "canon_pack",
    {"status": "approved"}
)
```

#### `delete_cold_artifact()`

```python
def delete_cold_artifact(self, artifact_id: str) -> bool
```

Delete artifact from cold storage.

**Parameters:**
- `artifact_id`: Unique artifact identifier

**Returns:** True if deleted, False if not found

**Example:**
```python
if ws.delete_cold_artifact("HOOK-001"):
    print("Artifact removed from cold storage")
```

### Promotion Operations

Move artifacts between hot workspace and cold storage.

#### `promote_to_cold()`

```python
def promote_to_cold(
    self,
    artifact_id: str,
    delete_hot: bool = True
) -> bool
```

Promote artifact from hot workspace to cold storage. This is the primary workflow for curating content.

**Parameters:**
- `artifact_id`: ID of artifact to promote
- `delete_hot`: Whether to delete from hot workspace after promotion (default: True)

**Returns:** True if promotion succeeded, False if artifact not found

**Example:**
```python
# Promote and remove from hot
if ws.promote_to_cold("HOOK-001"):
    print("Hook promoted to cold storage")

# Promote but keep in hot (for comparison)
ws.promote_to_cold("HOOK-002", delete_hot=False)
```

#### `demote_to_hot()`

```python
def demote_to_hot(
    self,
    artifact_id: str,
    delete_cold: bool = False
) -> bool
```

Demote artifact from cold storage to hot workspace. Useful for revisions.

**Parameters:**
- `artifact_id`: ID of artifact to demote
- `delete_cold`: Whether to delete from cold storage after demotion (default: False)

**Returns:** True if demotion succeeded, False if artifact not found

**Example:**
```python
# Copy back to hot for editing
if ws.demote_to_hot("HOOK-001"):
    print("Hook available for editing in hot workspace")

# Move to hot and remove from cold
ws.demote_to_hot("HOOK-002", delete_cold=True)
```

### Thematic Unit (TU) Operations

TUs are tracked in hot workspace only, representing active work units.

#### `save_tu()`

```python
def save_tu(self, tu: TUState) -> None
```

Save TU state to hot workspace.

**Parameters:**
- `tu`: TUState instance

**Example:**
```python
from questfoundry.state import TUState

tu = TUState(
    tu_id="TU-2025-11-07-SR01",
    status="in_progress",
    data={"brief": "Opening scene development"},
    metadata={"loop": "scene_forge"}
)
ws.save_tu(tu)
```

#### `get_tu()`

```python
def get_tu(self, tu_id: str) -> TUState | None
```

Get TU state from hot workspace.

**Parameters:**
- `tu_id`: TU identifier (e.g., "TU-2025-11-07-SR01")

**Returns:** TUState if found, None otherwise

**Example:**
```python
tu = ws.get_tu("TU-2025-11-07-SR01")
if tu:
    print(f"TU Status: {tu.status}")
    print(f"Created: {tu.created}")
```

#### `list_tus()`

```python
def list_tus(
    self,
    filters: dict[str, Any] | None = None
) -> list[TUState]
```

List TUs in hot workspace with optional filtering.

**Parameters:**
- `filters`: Filters as key-value pairs (e.g., `{"status": "open"}`)

**Returns:** List of matching TUs

**Example:**
```python
# List all TUs
all_tus = ws.list_tus()

# List active TUs
active = ws.list_tus({"status": "in_progress"})

# List TUs for specific snapshot
snapshot_tus = ws.list_tus({"snapshot_id": "SNAP-001"})
```

### Snapshot Operations

Snapshots represent points-in-time captures of project state.

#### `save_snapshot()`

```python
def save_snapshot(
    self,
    snapshot: SnapshotInfo,
    target: str = "both"
) -> None
```

Save snapshot metadata to hot, cold, or both storages.

**Parameters:**
- `snapshot`: SnapshotInfo instance
- `target`: Where to save - "hot", "cold", or "both" (default: "both")

**Raises:**
- `ValueError`: If target is invalid or snapshot already exists

**Example:**
```python
from questfoundry.state import SnapshotInfo
from datetime import datetime

snapshot = SnapshotInfo(
    snapshot_id="SNAP-2025-11-07",
    tu_id="TU-2025-11-07-SR01",
    description="Chapter 1 complete",
    metadata={"chapter": 1, "scene_count": 5}
)
ws.save_snapshot(snapshot, target="both")
```

#### `get_snapshot()`

```python
def get_snapshot(
    self,
    snapshot_id: str,
    source: str = "hot"
) -> SnapshotInfo | None
```

Get snapshot metadata from hot or cold storage.

**Parameters:**
- `snapshot_id`: Snapshot identifier
- `source`: Storage source - "hot" or "cold" (default: "hot")

**Returns:** SnapshotInfo or None if not found

**Raises:**
- `ValueError`: If source is invalid

**Example:**
```python
# Get from hot
snapshot = ws.get_snapshot("SNAP-2025-11-07", source="hot")
if snapshot:
    print(f"Snapshot: {snapshot.description}")

# Get from cold
cold_snap = ws.get_snapshot("SNAP-2025-11-07", source="cold")
```

#### `list_snapshots()`

```python
def list_snapshots(
    self,
    filters: dict[str, Any] | None = None,
    source: str = "hot"
) -> list[SnapshotInfo]
```

List snapshots from hot or cold storage.

**Parameters:**
- `filters`: Optional filters (e.g., `{"tu_id": "TU-001"}`)
- `source`: Storage source - "hot" or "cold" (default: "hot")

**Returns:** List of SnapshotInfo objects

**Raises:**
- `ValueError`: If source is invalid

**Example:**
```python
# List all hot snapshots
hot_snapshots = ws.list_snapshots(source="hot")

# List snapshots for specific TU
tu_snapshots = ws.list_snapshots(
    filters={"tu_id": "TU-2025-11-07-SR01"},
    source="cold"
)
```

### Context Manager Support

WorkspaceManager supports Python's context manager protocol for automatic resource cleanup:

```python
with WorkspaceManager("./my-project") as ws:
    ws.init_workspace("My Project")
    artifact = Artifact(...)
    ws.save_hot_artifact(artifact)
# Database connections automatically closed
```

### Methods

#### `close()`

```python
def close() -> None
```

Close database connections and release resources.

**Example:**
```python
ws = WorkspaceManager("./project")
try:
    # ... use workspace ...
finally:
    ws.close()
```

## StateStore (Abstract Interface)

Abstract base class defining the interface for state persistence backends.

### Abstract Methods

All StateStore implementations must provide these methods:

- `get_project_info() -> ProjectInfo`
- `save_project_info(info: ProjectInfo) -> None`
- `save_artifact(artifact: Artifact) -> None`
- `get_artifact(artifact_id: str) -> Artifact | None`
- `list_artifacts(artifact_type, filters) -> list[Artifact]`
- `delete_artifact(artifact_id: str) -> bool`
- `save_tu(tu: TUState) -> None`
- `get_tu(tu_id: str) -> TUState | None`
- `list_tus(filters) -> list[TUState]`
- `save_snapshot(snapshot: SnapshotInfo) -> None`
- `get_snapshot(snapshot_id: str) -> SnapshotInfo | None`
- `list_snapshots(filters) -> list[SnapshotInfo]`

## SQLiteStore

Cold storage implementation using SQLite database (.qfproj files).

### Constructor

```python
SQLiteStore(db_path: Path | str)
```

**Parameters:**
- `db_path`: Path to SQLite database file

**Example:**
```python
from questfoundry.state import SQLiteStore

store = SQLiteStore("./project.qfproj")
```

### Additional Methods

In addition to StateStore interface:

#### `init_database()`

```python
def init_database() -> None
```

Initialize database schema. Creates tables if they don't exist.

**Example:**
```python
store = SQLiteStore("./new-project.qfproj")
store.init_database()
```

#### `get_artifacts_by_ids()` (Batch Query)

```python
def get_artifacts_by_ids(
    self,
    artifact_ids: list[str]
) -> list[Artifact]
```

Get multiple artifacts by IDs in a single query. More efficient than multiple `get_artifact()` calls.

**Parameters:**
- `artifact_ids`: List of artifact IDs to fetch

**Returns:** List of Artifact objects (may be shorter if some IDs not found)

**Example:**
```python
# Efficient batch fetch
artifacts = store.get_artifacts_by_ids([
    "HOOK-001",
    "HOOK-002",
    "HOOK-003"
])
```

#### `get_artifacts_by_snapshot_id()`

```python
def get_artifacts_by_snapshot_id(
    self,
    snapshot_id: str
) -> list[Artifact]
```

Get all artifacts associated with a snapshot.

**Parameters:**
- `snapshot_id`: Snapshot identifier

**Returns:** List of artifacts in this snapshot

**Example:**
```python
snapshot_artifacts = store.get_artifacts_by_snapshot_id("SNAP-2025-11-07")
print(f"Snapshot contains {len(snapshot_artifacts)} artifacts")
```

#### `save_or_replace_snapshot()`

```python
def save_or_replace_snapshot(
    self,
    snapshot: SnapshotInfo
) -> None
```

Save or replace snapshot metadata. Used for import operations.

**Parameters:**
- `snapshot`: SnapshotInfo to save/replace

**Example:**
```python
# Import snapshot (replaces if exists)
store.save_or_replace_snapshot(imported_snapshot)
```

## FileStore

Hot workspace implementation using file-based directory structure.

### Constructor

```python
FileStore(base_dir: Path | str)
```

**Parameters:**
- `base_dir`: Path to hot workspace directory (typically `.questfoundry/`)

**Example:**
```python
from questfoundry.state import FileStore

store = FileStore("./.questfoundry")
```

Files are stored as JSON in subdirectories by artifact type:
```
.questfoundry/
  hot/
    hooks/
      HOOK-001.json
      HOOK-002.json
    canon/
      CANON-001.json
    tus/
      TU-2025-11-07-SR01.json
  metadata.json
```

## Data Models

### ProjectInfo

Project metadata and configuration.

**Fields:**
- `name` (str): Project name
- `description` (str): Project description (default: "")
- `created` (datetime): Creation timestamp (auto-generated)
- `modified` (datetime): Last modification timestamp (auto-updated)
- `version` (str): Project version (default: "1.0.0")
- `author` (str | None): Project author (optional)
- `metadata` (dict[str, Any]): Additional metadata (default: {})

**Example:**
```python
from questfoundry.state import ProjectInfo

info = ProjectInfo(
    name="Dragon Quest",
    description="Epic fantasy adventure",
    version="0.1.0",
    author="Alice Smith",
    metadata={"genre": "fantasy", "target_age": "adult"}
)
```

### TUState

Thematic Unit state tracking.

**Fields:**
- `tu_id` (str): TU identifier (format: "TU-YYYY-MM-DD-ROLEXX")
- `status` (str): TU status ("open", "in_progress", "completed", etc.)
- `created` (datetime): Creation timestamp (auto-generated)
- `modified` (datetime): Last modification timestamp (auto-updated)
- `snapshot_id` (str | None): Associated snapshot ID (optional)
- `data` (dict[str, Any]): TU brief data (default: {})
- `metadata` (dict[str, Any]): Additional metadata (default: {})

**Example:**
```python
from questfoundry.state import TUState

tu = TUState(
    tu_id="TU-2025-11-07-SR01",
    status="in_progress",
    snapshot_id="SNAP-001",
    data={
        "brief": "Develop opening scene",
        "assigned_role": "SS"
    },
    metadata={"priority": "high", "loop": "scene_forge"}
)
```

### SnapshotInfo

Snapshot metadata.

**Fields:**
- `snapshot_id` (str): Snapshot identifier
- `created` (datetime): Creation timestamp (auto-generated)
- `tu_id` (str): Associated TU ID
- `description` (str): Snapshot description (default: "")
- `metadata` (dict[str, Any]): Additional metadata (default: {})

**Example:**
```python
from questfoundry.state import SnapshotInfo

snapshot = SnapshotInfo(
    snapshot_id="SNAP-2025-11-07-001",
    tu_id="TU-2025-11-07-SR01",
    description="Chapter 1 complete - 5 scenes reviewed and approved",
    metadata={
        "chapter": 1,
        "scene_count": 5,
        "word_count": 12500,
        "reviewers": ["Alice", "Bob"]
    }
)
```

## Usage Patterns

### Complete Workflow Example

```python
from questfoundry.state import WorkspaceManager
from questfoundry.models import Artifact

# 1. Initialize workspace
with WorkspaceManager("./dragon-quest") as ws:
    ws.init_workspace(
        name="Dragon Quest",
        description="Epic fantasy RPG",
        author="Alice"
    )

    # 2. Create draft hook in hot workspace
    hook = Artifact(
        type="hook_card",
        data={
            "hook_id": "HOOK-001",
            "title": "Dragon's Awakening",
            "concept": "Ancient dragon stirs after 1000 years",
            "status": "draft"
        },
        metadata={"temperature": "hot"}
    )
    ws.save_hot_artifact(hook)

    # 3. Review and iterate in hot workspace
    hook = ws.get_hot_artifact("HOOK-001")
    hook.data["concept"] += " - adds backstory"
    hook.data["status"] = "reviewed"
    ws.save_hot_artifact(hook)

    # 4. Promote to cold when approved
    ws.promote_to_cold("HOOK-001")

    # 5. Create snapshot
    from questfoundry.state import SnapshotInfo, TUState

    tu = TUState(
        tu_id="TU-2025-11-07-SR01",
        status="completed",
        data={"brief": "Initial hook development"}
    )
    ws.save_tu(tu)

    snapshot = SnapshotInfo(
        snapshot_id="SNAP-001",
        tu_id="TU-2025-11-07-SR01",
        description="First hook complete"
    )
    ws.save_snapshot(snapshot)

    # 6. Query final state
    cold_hooks = ws.list_cold_artifacts("hook_card")
    print(f"Project has {len(cold_hooks)} approved hooks")
```

### Bulk Operations

```python
# Promote multiple artifacts
hot_hooks = ws.list_hot_artifacts("hook_card", {"status": "approved"})
for hook in hot_hooks:
    hook_id = hook.data.get("hook_id")
    if hook_id:
        ws.promote_to_cold(hook_id)

# Batch query with SQLiteStore
hook_ids = [f"HOOK-{i:03d}" for i in range(1, 51)]
hooks = ws.cold_store.get_artifacts_by_ids(hook_ids)
print(f"Retrieved {len(hooks)} hooks in single query")
```

### Filtering and Queries

```python
# Complex filtering
recent_hooks = ws.list_cold_artifacts(
    "hook_card",
    {"status": "approved", "author": "Alice"}
)

# Query by TU
tu_artifacts = ws.list_hot_artifacts(
    filters={"tu_id": "TU-2025-11-07-SR01"}
)

# List active work
active_tus = ws.list_tus({"status": "in_progress"})
for tu in active_tus:
    print(f"TU {tu.tu_id}: {tu.data.get('brief')}")
```

### Data Migration

```python
# Export from one project, import to another
source = WorkspaceManager("./project-a")
target = WorkspaceManager("./project-b")

# Copy all cold hooks
hooks = source.list_cold_artifacts("hook_card")
for hook in hooks:
    target.save_cold_artifact(hook)

# Copy project metadata
info = source.get_project_info("cold")
info.name = "Project B (Imported)"
target.save_project_info(info, target="cold")
```

## Best Practices

1. **Use WorkspaceManager** instead of directly using stores:
   ```python
   # Good
   ws = WorkspaceManager("./project")

   # Avoid (unless you need low-level access)
   store = SQLiteStore("./project.qfproj")
   ```

2. **Always use context managers** to ensure resources are cleaned up:
   ```python
   with WorkspaceManager("./project") as ws:
       # Use workspace...
   ```

3. **Work in hot, curate to cold**:
   ```python
   # Draft in hot
   ws.save_hot_artifact(draft)

   # Review and iterate
   # ...

   # Promote when ready
   ws.promote_to_cold(artifact_id)
   ```

4. **Use batch operations** for performance:
   ```python
   # Good - single query
   artifacts = ws.cold_store.get_artifacts_by_ids(id_list)

   # Avoid - N queries
   artifacts = [ws.get_cold_artifact(id) for id in id_list]
   ```

5. **Include metadata** for filtering:
   ```python
   artifact.metadata = {
       "temperature": "hot",
       "status": "draft",
       "author": "Alice",
       "created_by": "scene_smith"
   }
   ```

6. **Create snapshots** at milestones:
   ```python
   # After each chapter
   snapshot = SnapshotInfo(
       snapshot_id=f"SNAP-{chapter}",
       tu_id=tu_id,
       description=f"Chapter {chapter} complete"
   )
   ws.save_snapshot(snapshot)
   ```

## See Also

- [Protocol API](protocol.md) - Message passing with envelopes
- [Export API](export.md) - View generation and export
- [Models API](models.md) - Artifact types and schemas
