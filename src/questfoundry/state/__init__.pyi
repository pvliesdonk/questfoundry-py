"""Type stubs for questfoundry.state module"""

from .conflict_detection import (
    CanonConflict as CanonConflict,
    ConflictDetector as ConflictDetector,
    ConflictReport as ConflictReport,
    ConflictResolution as ConflictResolution,
    ConflictSeverity as ConflictSeverity,
)
from .constraint_manifest import (
    ConstraintManifest as ConstraintManifest,
    ConstraintManifestGenerator as ConstraintManifestGenerator,
)
from .entity_registry import (
    Entity as Entity,
    EntityRegistry as EntityRegistry,
    EntityType as EntityType,
)
from .file_store import FileStore as FileStore
from .sqlite_store import SQLiteStore as SQLiteStore
from .store import StateStore as StateStore
from .timeline import (
    TimelineAnchor as TimelineAnchor,
    TimelineManager as TimelineManager,
)
from .types import (
    ProjectInfo as ProjectInfo,
    SnapshotInfo as SnapshotInfo,
    TUState as TUState,
)
from .workspace import WorkspaceManager as WorkspaceManager

__all__ = [
    "StateStore",
    "SQLiteStore",
    "FileStore",
    "WorkspaceManager",
    "ProjectInfo",
    "TUState",
    "SnapshotInfo",
    "Entity",
    "EntityRegistry",
    "EntityType",
    "TimelineAnchor",
    "TimelineManager",
    "CanonConflict",
    "ConflictDetector",
    "ConflictReport",
    "ConflictResolution",
    "ConflictSeverity",
    "ConstraintManifest",
    "ConstraintManifestGenerator",
]
