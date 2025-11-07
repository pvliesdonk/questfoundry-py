# Export API Reference

The `questfoundry.export` module provides tools for exporting QuestFoundry projects to various formats. It includes view generation (player-safe content filtering), Git-friendly YAML export, and book binding (rendering to HTML/Markdown).

## Overview

The export module consists of three main components:

- **ViewGenerator**: Creates player-safe views from cold snapshots
- **GitExporter**: Exports snapshots to version-controllable YAML format
- **BookBinder**: Renders views to HTML and Markdown formats

## Quick Start

```python
from questfoundry.export import ViewGenerator, GitExporter, BookBinder
from questfoundry.state import WorkspaceManager

# Initialize
ws = WorkspaceManager("./my-project")
view_gen = ViewGenerator(ws.cold_store)
git_exporter = GitExporter(ws.cold_store)
binder = BookBinder()

# Generate player-safe view
view = view_gen.generate_view("SNAP-2025-11-07")
print(f"View contains {len(view.artifacts)} player-safe artifacts")

# Save view
view_gen.save_view(view)

# Export to Git-friendly YAML
export_path = git_exporter.export_snapshot("SNAP-2025-11-07", "./export")
print(f"Exported to {export_path}")

# Render to HTML
html = binder.render_html(view, title="Chapter 1")
binder.save_html(html, "./output/chapter1.html")

# Render to Markdown
markdown = binder.render_markdown(view)
binder.save_markdown(markdown, "./output/chapter1.md")
```

## ViewGenerator

Generates player-safe views from cold snapshots by filtering artifacts based on their player_safe flag.

### Constructor

```python
ViewGenerator(cold_store: SQLiteStore)
```

**Parameters:**
- `cold_store`: SQLite store for cold storage access

**Example:**
```python
from questfoundry.export import ViewGenerator
from questfoundry.state import WorkspaceManager

ws = WorkspaceManager("./project")
generator = ViewGenerator(ws.cold_store)
```

### Methods

#### `generate_view()`

```python
def generate_view(
    snapshot_id: str,
    view_id: str | None = None,
    include_types: list[str] | None = None,
    exclude_types: list[str] | None = None,
) -> ViewArtifact
```

Generate a view from a snapshot. Extracts all artifacts from the specified snapshot and filters to include only player-safe content.

**Parameters:**
- `snapshot_id`: Snapshot ID to generate view from
- `view_id`: Optional view ID (auto-generated if not provided)
- `include_types`: Optional list of artifact types to include (e.g., `["hook_card", "scene"]`)
- `exclude_types`: Optional list of artifact types to exclude

**Returns:** ViewArtifact containing player-safe content

**Raises:**
- `ValueError`: If snapshot not found or no artifacts available

**Example:**
```python
# Generate full view
view = generator.generate_view("SNAP-001")

# Generate view with custom ID
view = generator.generate_view("SNAP-001", view_id="VIEW-CHAPTER-1")

# Generate view with only specific types
view = generator.generate_view(
    "SNAP-001",
    include_types=["hook_card", "canon_pack"]
)

# Generate view excluding certain types
view = generator.generate_view(
    "SNAP-001",
    exclude_types=["gatecheck_report", "tu_brief"]
)
```

#### `save_view()`

```python
def save_view(view: ViewArtifact) -> None
```

Save view to cold storage. Stores the view artifact in the SQLite database for later retrieval.

**Parameters:**
- `view`: ViewArtifact to save

**Raises:**
- `IOError`: If save operation fails

**Example:**
```python
view = generator.generate_view("SNAP-001")
generator.save_view(view)
print(f"Saved view: {view.view_id}")
```

#### `get_view()`

```python
def get_view(view_id: str) -> ViewArtifact | None
```

Retrieve a previously saved view.

**Parameters:**
- `view_id`: View identifier

**Returns:** ViewArtifact if found, None otherwise

**Example:**
```python
view = generator.get_view("VIEW-CHAPTER-1")
if view:
    print(f"Found view with {len(view.artifacts)} artifacts")
```

#### `list_views()`

```python
def list_views() -> list[str]
```

List all saved view IDs.

**Returns:** List of view IDs

**Example:**
```python
views = generator.list_views()
print(f"Available views: {views}")
```

## ViewArtifact

View artifact containing player-safe content. A view is a filtered collection of artifacts from a snapshot.

### Attributes

- `view_id` (str): View identifier
- `snapshot_id` (str): Source snapshot ID
- `created` (datetime): Creation timestamp
- `artifacts` (list[Artifact]): Player-safe artifacts
- `metadata` (dict[str, Any]): Additional metadata

**Example:**
```python
view = generator.generate_view("SNAP-001")

print(f"View ID: {view.view_id}")
print(f"From snapshot: {view.snapshot_id}")
print(f"Created: {view.created}")
print(f"Artifacts: {len(view.artifacts)}")

# Access metadata
print(f"Total artifacts: {view.metadata['total_artifacts']}")
print(f"Player-safe: {view.metadata['player_safe_artifacts']}")

# Iterate artifacts
for artifact in view.artifacts:
    print(f"  {artifact.type}: {artifact.artifact_id}")
```

## GitExporter

Exports cold snapshots to Git-friendly YAML format. Creates a human-readable directory structure suitable for version control and diffing.

### Constructor

```python
GitExporter(cold_store: SQLiteStore)
```

**Parameters:**
- `cold_store`: SQLite store for cold storage access

**Example:**
```python
from questfoundry.export import GitExporter

exporter = GitExporter(ws.cold_store)
```

### Directory Structure

Export creates the following structure:

```
export_dir/
    manifest.yml          # Snapshot metadata and artifact index
    hooks/
        HOOK-001.yml
        HOOK-002.yml
    canon/
        CANON-001.yml
    scenes/
        SCENE-001.yml
    tus/
        TU-2025-11-07-SR01.yml
    gatechecks/
        gatecheck_20251107.yml
    ...
```

### Methods

#### `export_snapshot()`

```python
def export_snapshot(
    snapshot_id: str,
    export_dir: str | Path,
    include_hot: bool = False,
) -> Path
```

Export snapshot to Git-friendly YAML format. Creates directory structure with YAML files for each artifact and a manifest file with snapshot metadata.

**Parameters:**
- `snapshot_id`: Snapshot ID to export
- `export_dir`: Directory to export to (will be created if needed)
- `include_hot`: Whether to include hot artifacts (default: False)

**Returns:** Path to export directory

**Raises:**
- `ValueError`: If snapshot not found
- `IOError`: If export fails

**Example:**
```python
# Export to directory
export_path = exporter.export_snapshot(
    "SNAP-2025-11-07",
    "./exports/chapter1"
)
print(f"Exported to: {export_path}")

# Export including hot workspace
export_path = exporter.export_snapshot(
    "SNAP-2025-11-07",
    "./exports/chapter1-with-wip",
    include_hot=True
)
```

#### `import_snapshot()`

```python
def import_snapshot(
    export_dir: str | Path,
    target_snapshot_id: str | None = None,
) -> SnapshotInfo
```

Import snapshot from Git export directory. Reads YAML files and reconstructs artifacts in cold storage.

**Parameters:**
- `export_dir`: Directory containing exported snapshot
- `target_snapshot_id`: Optional new snapshot ID (uses manifest ID if None)

**Returns:** SnapshotInfo for imported snapshot

**Raises:**
- `ValueError`: If manifest not found or invalid
- `IOError`: If import fails

**Example:**
```python
# Import from export directory
snapshot = exporter.import_snapshot("./exports/chapter1")
print(f"Imported snapshot: {snapshot.snapshot_id}")

# Import with new snapshot ID
snapshot = exporter.import_snapshot(
    "./exports/chapter1",
    target_snapshot_id="SNAP-IMPORTED-2025-11-07"
)
```

### Manifest Format

The `manifest.yml` file contains snapshot metadata and artifact index:

```yaml
version: "1.0.0"
snapshot:
  snapshot_id: SNAP-2025-11-07
  created: "2025-11-07T15:30:00"
  tu_id: TU-2025-11-07-SR01
  description: "Chapter 1 complete"

artifacts:
  hook_card:
    - HOOK-001
    - HOOK-002
  canon_pack:
    - CANON-001
  # ... more artifact types

statistics:
  total_artifacts: 25
  artifact_types: 8
  exported_at: "2025-11-07T15:35:00"
```

## BookBinder

Renders views to various export formats (HTML, Markdown). Handles artifact ordering, formatting, and presentation.

### Constructor

```python
BookBinder(
    html_template: str | None = None,
    sort_artifacts: bool = True,
)
```

**Parameters:**
- `html_template`: Custom HTML template (uses default if None)
- `sort_artifacts`: Whether to sort artifacts by type and ID (default: True)

**Example:**
```python
from questfoundry.export import BookBinder

# Use default template
binder = BookBinder()

# Custom template
custom_template = """
<!DOCTYPE html>
<html>
<head><title>{title}</title></head>
<body>{content}</body>
</html>
"""
binder = BookBinder(html_template=custom_template)

# Disable sorting
binder = BookBinder(sort_artifacts=False)
```

### HTML Rendering

#### `render_html()`

```python
def render_html(
    view: ViewArtifact,
    title: str | None = None
) -> str
```

Render view to HTML format.

**Parameters:**
- `view`: ViewArtifact to render
- `title`: Page title (uses view_id if None)

**Returns:** HTML string

**Example:**
```python
view = generator.generate_view("SNAP-001")

# Basic rendering
html = binder.render_html(view)

# With custom title
html = binder.render_html(view, title="Chapter 1: The Beginning")

print(html)  # Complete HTML document
```

#### `save_html()`

```python
def save_html(
    html: str,
    output_path: str | Path
) -> Path
```

Save HTML to file.

**Parameters:**
- `html`: HTML string to save
- `output_path`: Path to output file

**Returns:** Path to saved file

**Example:**
```python
html = binder.render_html(view)
output_path = binder.save_html(html, "./output/chapter1.html")
print(f"Saved to: {output_path}")
```

### Markdown Rendering

#### `render_markdown()`

```python
def render_markdown(
    view: ViewArtifact,
    title: str | None = None,
    include_metadata: bool = True,
) -> str
```

Render view to Markdown format.

**Parameters:**
- `view`: ViewArtifact to render
- `title`: Document title (uses view_id if None)
- `include_metadata`: Whether to include view metadata (default: True)

**Returns:** Markdown string

**Example:**
```python
view = generator.generate_view("SNAP-001")

# Basic rendering
markdown = binder.render_markdown(view)

# With custom title, no metadata
markdown = binder.render_markdown(
    view,
    title="Chapter 1",
    include_metadata=False
)

print(markdown)
```

#### `save_markdown()`

```python
def save_markdown(
    markdown: str,
    output_path: str | Path
) -> Path
```

Save Markdown to file.

**Parameters:**
- `markdown`: Markdown string to save
- `output_path`: Path to output file

**Returns:** Path to saved file

**Example:**
```python
markdown = binder.render_markdown(view)
output_path = binder.save_markdown(markdown, "./output/chapter1.md")
print(f"Saved to: {output_path}")
```

## Usage Patterns

### Complete Export Workflow

```python
from questfoundry.export import ViewGenerator, GitExporter, BookBinder
from questfoundry.state import WorkspaceManager

# Initialize
ws = WorkspaceManager("./dragon-quest")
view_gen = ViewGenerator(ws.cold_store)
git_exporter = GitExporter(ws.cold_store)
binder = BookBinder()

snapshot_id = "SNAP-2025-11-07"

# 1. Generate player-safe view
view = view_gen.generate_view(snapshot_id)
print(f"Generated view with {len(view.artifacts)} artifacts")

# 2. Save view for later use
view_gen.save_view(view)

# 3. Export to Git for version control
git_export_path = git_exporter.export_snapshot(
    snapshot_id,
    f"./exports/{snapshot_id}"
)
print(f"Exported to Git format: {git_export_path}")

# 4. Render to HTML for players
html = binder.render_html(view, title="Chapter 1: Dragon's Awakening")
html_path = binder.save_html(html, "./output/chapter1.html")
print(f"Rendered HTML: {html_path}")

# 5. Render to Markdown for review
markdown = binder.render_markdown(view)
md_path = binder.save_markdown(markdown, "./output/chapter1.md")
print(f"Rendered Markdown: {md_path}")
```

### Player-Safe Content Filtering

```python
# Generate view with only player-facing content
view = view_gen.generate_view(
    "SNAP-001",
    include_types=[
        "hook_card",
        "scene",
        "canon_pack",
        "codex_entry",
    ]
)

# Verify all artifacts are player-safe
for artifact in view.artifacts:
    assert artifact.metadata.get("player_safe", True)
    print(f"✓ {artifact.type}: {artifact.artifact_id} is player-safe")
```

### Git Export for Version Control

```python
import subprocess

# Export snapshot
export_path = git_exporter.export_snapshot("SNAP-001", "./exports/v1")

# Initialize git repo (if not already)
subprocess.run(["git", "init"], cwd=export_path)

# Add and commit
subprocess.run(["git", "add", "."], cwd=export_path)
subprocess.run([
    "git", "commit", "-m",
    "Export SNAP-001: Chapter 1 complete"
], cwd=export_path)

print("Committed to git!")
```

### Import and Re-export

```python
# Import from one export
imported_snapshot = git_exporter.import_snapshot("./exports/v1")
print(f"Imported: {imported_snapshot.snapshot_id}")

# Re-export with new snapshot ID
new_export_path = git_exporter.export_snapshot(
    imported_snapshot.snapshot_id,
    "./exports/v2"
)
```

### Custom HTML Template

```python
# Define custom template
custom_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: #f0f0f0;
        }}
        .artifact {{
            border: 1px solid #333;
            padding: 20px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
"""

binder = BookBinder(html_template=custom_template)
html = binder.render_html(view, title="Dark Fantasy Chapter")
binder.save_html(html, "./output/dark_chapter.html")
```

### Batch Export Multiple Snapshots

```python
# Export all snapshots
snapshots = ws.cold_store.list_snapshots()

for snapshot in snapshots:
    snapshot_id = snapshot.snapshot_id

    # Generate view
    view = view_gen.generate_view(snapshot_id)

    # Export to Git
    git_exporter.export_snapshot(
        snapshot_id,
        f"./exports/{snapshot_id}"
    )

    # Render to HTML
    html = binder.render_html(view, title=snapshot.description)
    binder.save_html(html, f"./output/{snapshot_id}.html")

    print(f"✓ Exported {snapshot_id}")
```

### Selective Artifact Export

```python
# Export only narrative content (no reports, metadata, etc.)
narrative_types = [
    "hook_card",
    "scene",
    "canon_pack",
    "codex_entry",
    "front_matter",
]

view = view_gen.generate_view(
    "SNAP-001",
    include_types=narrative_types
)

print(f"Narrative view: {len(view.artifacts)} artifacts")

# Render clean player-facing output
html = binder.render_html(view, title="Player's Guide")
binder.save_html(html, "./output/players_guide.html")
```

### Comparison Between Snapshots

```python
from difflib import unified_diff

# Export two snapshots
git_exporter.export_snapshot("SNAP-001", "./exports/snap1")
git_exporter.export_snapshot("SNAP-002", "./exports/snap2")

# Compare manifests
with open("./exports/snap1/manifest.yml") as f1, \
     open("./exports/snap2/manifest.yml") as f2:
    diff = unified_diff(
        f1.readlines(),
        f2.readlines(),
        fromfile="SNAP-001",
        tofile="SNAP-002"
    )
    print("".join(diff))
```

### View Metadata Analysis

```python
view = view_gen.generate_view("SNAP-001")

# Analyze view metadata
print(f"Snapshot: {view.snapshot_id}")
print(f"View ID: {view.view_id}")
print(f"Created: {view.created}")
print(f"Total artifacts: {view.metadata['total_artifacts']}")
print(f"Player-safe: {view.metadata['player_safe_artifacts']}")

# Artifact type breakdown
type_counts = {}
for artifact in view.artifacts:
    type_counts[artifact.type] = type_counts.get(artifact.type, 0) + 1

print("\nArtifact types:")
for artifact_type, count in sorted(type_counts.items()):
    print(f"  {artifact_type}: {count}")
```

## Best Practices

1. **Always generate views before rendering**:
   ```python
   # Good - filtered player-safe content
   view = view_gen.generate_view(snapshot_id)
   html = binder.render_html(view)

   # Bad - might expose GM-only content
   all_artifacts = ws.list_cold_artifacts()
   # ... render directly
   ```

2. **Save views for reproducibility**:
   ```python
   view = view_gen.generate_view("SNAP-001")
   view_gen.save_view(view)  # Can retrieve later with same filters
   ```

3. **Use Git export for version control**:
   ```python
   # Export snapshots regularly
   git_exporter.export_snapshot(snapshot_id, f"./exports/{snapshot_id}")
   # Commit to version control
   ```

4. **Include only relevant types**:
   ```python
   # Don't export internal reports to players
   view = view_gen.generate_view(
       snapshot_id,
       exclude_types=["gatecheck_report", "tu_brief", "edit_notes"]
   )
   ```

5. **Organize exports**:
   ```python
   # Structured export organization
   base_dir = Path("./exports")
   (base_dir / "snapshots").mkdir(exist_ok=True, parents=True)
   (base_dir / "views").mkdir(exist_ok=True, parents=True)
   (base_dir / "rendered").mkdir(exist_ok=True, parents=True)

   git_exporter.export_snapshot(snap_id, base_dir / "snapshots" / snap_id)
   binder.save_html(html, base_dir / "rendered" / f"{snap_id}.html")
   ```

6. **Custom templates for different audiences**:
   ```python
   player_template = "..."  # Clean, simple
   gm_template = "..."  # Detailed, with annotations
   review_template = "..."  # With change highlights

   player_binder = BookBinder(html_template=player_template)
   gm_binder = BookBinder(html_template=gm_template)
   ```

## See Also

- [State Management API](state.md) - Snapshots and artifacts
- [Validation API](validation.md) - Quality checks before export
- [Protocol API](protocol.md) - Message passing
