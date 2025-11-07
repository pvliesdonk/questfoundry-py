"""View generation for QuestFoundry projects

Extracts cold artifacts from snapshots and filters by player-safe flag
to create player-facing views.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..models.artifact import Artifact
from ..state.sqlite_store import SQLiteStore
from ..state.types import SnapshotInfo


class ViewArtifact(BaseModel):
    """
    View artifact containing player-safe content.

    A view is a filtered collection of artifacts from a snapshot,
    containing only player-safe content suitable for export.
    """

    view_id: str = Field(..., description="View identifier")
    snapshot_id: str = Field(..., description="Source snapshot ID")
    created: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )
    artifacts: list[Artifact] = Field(
        default_factory=list, description="Player-safe artifacts"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ViewGenerator:
    """
    Generate views from cold snapshots.

    Extracts artifacts from snapshots, filters by player-safe flag,
    and packages them into view artifacts for export.

    Example:
        >>> generator = ViewGenerator(cold_store)
        >>> view = generator.generate_view("SNAP-001")
        >>> print(f"Generated view with {len(view.artifacts)} artifacts")
    """

    def __init__(self, cold_store: SQLiteStore):
        """
        Initialize view generator.

        Args:
            cold_store: SQLite store for cold storage access
        """
        self.cold_store = cold_store

    def generate_view(
        self,
        snapshot_id: str,
        view_id: str | None = None,
        include_types: list[str] | None = None,
        exclude_types: list[str] | None = None,
    ) -> ViewArtifact:
        """
        Generate a view from a snapshot.

        Extracts all artifacts from the specified snapshot and filters
        to include only player-safe content. Optionally filters by
        artifact types.

        Args:
            snapshot_id: Snapshot ID to generate view from
            view_id: Optional view ID (auto-generated if not provided)
            include_types: Optional list of artifact types to include
            exclude_types: Optional list of artifact types to exclude

        Returns:
            ViewArtifact containing player-safe content

        Raises:
            ValueError: If snapshot not found or no artifacts available
        """
        # Verify snapshot exists
        snapshot = self._get_snapshot(snapshot_id)

        # Generate view ID if not provided
        if view_id is None:
            view_id = f"VIEW-{snapshot_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Get all artifacts from snapshot
        artifacts = self._get_snapshot_artifacts(snapshot_id)

        # Filter to player-safe only
        player_safe_artifacts = self._filter_player_safe(artifacts)

        # Apply type filters
        if include_types is not None:
            player_safe_artifacts = [
                a for a in player_safe_artifacts if a.type in include_types
            ]

        if exclude_types is not None:
            player_safe_artifacts = [
                a for a in player_safe_artifacts if a.type not in exclude_types
            ]

        # Create view artifact
        view = ViewArtifact(
            view_id=view_id,
            snapshot_id=snapshot_id,
            artifacts=player_safe_artifacts,
            metadata={
                "snapshot_description": snapshot.description,
                "tu_id": snapshot.tu_id,
                "total_artifacts": len(artifacts),
                "player_safe_artifacts": len(player_safe_artifacts),
            },
        )

        return view

    def save_view(self, view: ViewArtifact) -> None:
        """
        Save view to cold storage.

        Stores the view artifact in the SQLite database for later retrieval.

        Args:
            view: ViewArtifact to save

        Raises:
            IOError: If save operation fails
        """
        # Convert view to artifact format for storage
        view_artifact = Artifact(
            type="view_log",
            data={
                "view_id": view.view_id,
                "snapshot_id": view.snapshot_id,
                "created": view.created.isoformat(),
                "artifact_count": len(view.artifacts),
                "artifact_ids": [a.artifact_id for a in view.artifacts],
            },
            metadata={**view.metadata, "id": view.view_id},
        )

        # Save to cold store
        self.cold_store.save_artifact(view_artifact)

    def get_view(self, view_id: str) -> ViewArtifact | None:
        """
        Retrieve a previously saved view.

        Args:
            view_id: View ID to retrieve

        Returns:
            ViewArtifact if found, None otherwise
        """
        # Try to get view artifact by ID directly
        view_artifact = self.cold_store.get_artifact(view_id)

        if not view_artifact or view_artifact.type != "view_log":
            return None

        # Get the view metadata
        data = view_artifact.data

        # Reconstruct view by loading referenced artifacts
        artifact_ids = data.get("artifact_ids", [])
        view_artifacts = []
        for artifact_id in artifact_ids:
            artifact = self.cold_store.get_artifact(artifact_id)
            if artifact:
                view_artifacts.append(artifact)

        return ViewArtifact(
            view_id=data["view_id"],
            snapshot_id=data["snapshot_id"],
            created=datetime.fromisoformat(data["created"]),
            artifacts=view_artifacts,
            metadata=view_artifact.metadata,
        )

    def _get_snapshot(self, snapshot_id: str) -> SnapshotInfo:
        """
        Get snapshot metadata.

        Args:
            snapshot_id: Snapshot ID

        Returns:
            SnapshotInfo

        Raises:
            ValueError: If snapshot not found
        """
        conn = self.cold_store._get_connection()
        cursor = conn.execute(
            """
            SELECT snapshot_id, tu_id, created, description, metadata
            FROM snapshots
            WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        )
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"Snapshot not found: {snapshot_id}")

        import json

        return SnapshotInfo(
            snapshot_id=row["snapshot_id"],
            tu_id=row["tu_id"],
            created=datetime.fromisoformat(row["created"]),
            description=row["description"],
            metadata=json.loads(row["metadata"]),
        )

    def _get_snapshot_artifacts(self, snapshot_id: str) -> list[Artifact]:
        """
        Get all artifacts associated with a snapshot.

        Retrieves artifacts that explicitly reference the snapshot ID
        in their metadata.

        Args:
            snapshot_id: Snapshot ID

        Returns:
            List of artifacts
        """
        # Get all artifacts with metadata referencing this snapshot
        conn = self.cold_store._get_connection()
        cursor = conn.execute(
            """
            SELECT artifact_id, artifact_type, data, metadata, created, modified
            FROM artifacts
            WHERE json_extract(metadata, '$.snapshot_id') = ?
            ORDER BY modified DESC
            """,
            (snapshot_id,),
        )

        import json

        artifacts = []
        for row in cursor.fetchall():
            artifact = Artifact(
                type=row["artifact_type"],
                data=json.loads(row["data"]),
                metadata=json.loads(row["metadata"]),
            )
            artifacts.append(artifact)

        return artifacts

    def _filter_player_safe(self, artifacts: list[Artifact]) -> list[Artifact]:
        """
        Filter artifacts to only player-safe content.

        Args:
            artifacts: List of artifacts to filter

        Returns:
            List of player-safe artifacts
        """
        player_safe_artifacts = []

        for artifact in artifacts:
            # Check metadata for player_safe flag
            player_safe = artifact.metadata.get("player_safe", False)

            # Also check temperature is cold
            temperature = artifact.metadata.get("temperature")

            if player_safe and temperature == "cold":
                player_safe_artifacts.append(artifact)

        return player_safe_artifacts
