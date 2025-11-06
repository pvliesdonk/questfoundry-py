"""Abstract state store interface"""

from abc import ABC, abstractmethod
from typing import Any

from ..models.artifact import Artifact
from .types import ProjectInfo, SnapshotInfo, TUState


class StateStore(ABC):
    """
    Abstract interface for state persistence.

    Implementations provide storage backends for QuestFoundry projects,
    artifacts, and Thematic Units. Supports both hot (working) and cold
    (archived) storage patterns.

    Example:
        >>> store = SQLiteStore("project.qfproj")
        >>> info = store.get_project_info()
        >>> print(f"Project: {info.name}")
    """

    @abstractmethod
    def get_project_info(self) -> ProjectInfo:
        """
        Get project metadata and configuration.

        Returns:
            ProjectInfo with name, description, timestamps, etc.

        Raises:
            FileNotFoundError: If project file doesn't exist
        """
        pass

    @abstractmethod
    def save_project_info(self, info: ProjectInfo) -> None:
        """
        Save project metadata.

        Args:
            info: ProjectInfo to save

        Raises:
            IOError: If save operation fails
        """
        pass

    @abstractmethod
    def save_artifact(self, artifact: Artifact) -> None:
        """
        Save an artifact to storage.

        Args:
            artifact: Artifact instance with type and data

        Raises:
            ValueError: If artifact is invalid
            IOError: If save operation fails

        Example:
            >>> artifact = Artifact(type="hook_card", data={...})
            >>> store.save_artifact(artifact)
        """
        pass

    @abstractmethod
    def get_artifact(self, artifact_id: str) -> Artifact | None:
        """
        Retrieve an artifact by ID.

        Args:
            artifact_id: Unique artifact identifier

        Returns:
            Artifact if found, None otherwise

        Example:
            >>> artifact = store.get_artifact("HOOK-001")
            >>> if artifact:
            ...     print(artifact.type)
        """
        pass

    @abstractmethod
    def list_artifacts(
        self, artifact_type: str | None = None, filters: dict[str, Any] | None = None
    ) -> list[Artifact]:
        """
        List artifacts with optional filtering.

        Args:
            artifact_type: Filter by type (e.g., "hook_card"), None for all types
            filters: Additional filters as key-value pairs
                Examples: {"status": "proposed"}, {"author": "alice"}

        Returns:
            List of matching artifacts

        Example:
            >>> hooks = store.list_artifacts("hook_card", {"status": "proposed"})
            >>> print(f"Found {len(hooks)} proposed hooks")
        """
        pass

    @abstractmethod
    def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact.

        Args:
            artifact_id: Unique artifact identifier

        Returns:
            True if deleted, False if not found

        Raises:
            IOError: If delete operation fails
        """
        pass

    @abstractmethod
    def save_tu(self, tu: TUState) -> None:
        """
        Save Thematic Unit state.

        Args:
            tu: TUState instance

        Raises:
            ValueError: If TU is invalid
            IOError: If save operation fails

        Example:
            >>> tu = TUState(tu_id="TU-2024-01-15-SR01", status="open", data={...})
            >>> store.save_tu(tu)
        """
        pass

    @abstractmethod
    def get_tu(self, tu_id: str) -> TUState | None:
        """
        Retrieve TU state by ID.

        Args:
            tu_id: TU identifier (e.g., "TU-2024-01-15-SR01")

        Returns:
            TUState if found, None otherwise

        Example:
            >>> tu = store.get_tu("TU-2024-01-15-SR01")
            >>> if tu:
            ...     print(f"Status: {tu.status}")
        """
        pass

    @abstractmethod
    def list_tus(self, filters: dict[str, Any] | None = None) -> list[TUState]:
        """
        List TUs with optional filtering.

        Args:
            filters: Filters as key-value pairs
                Examples: {"status": "open"}, {"snapshot_id": "SNAP-001"}

        Returns:
            List of matching TUs

        Example:
            >>> open_tus = store.list_tus({"status": "open"})
            >>> print(f"{len(open_tus)} TUs in progress")
        """
        pass

    @abstractmethod
    def save_snapshot(self, snapshot: SnapshotInfo) -> None:
        """
        Save snapshot metadata.

        Args:
            snapshot: SnapshotInfo instance

        Raises:
            ValueError: If snapshot is invalid
            IOError: If save operation fails
        """
        pass

    @abstractmethod
    def get_snapshot(self, snapshot_id: str) -> SnapshotInfo | None:
        """
        Retrieve snapshot by ID.

        Args:
            snapshot_id: Snapshot identifier

        Returns:
            SnapshotInfo if found, None otherwise
        """
        pass

    @abstractmethod
    def list_snapshots(
        self, filters: dict[str, Any] | None = None
    ) -> list[SnapshotInfo]:
        """
        List snapshots with optional filtering.

        Args:
            filters: Filters as key-value pairs
                Example: {"tu_id": "TU-2024-01-15-SR01"}

        Returns:
            List of matching snapshots
        """
        pass
