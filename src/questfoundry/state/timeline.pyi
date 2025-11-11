"""Type stubs for timeline management (Layer 6/7 canon workflows)"""

from dataclasses import dataclass
from typing import Any

@dataclass
class TimelineAnchor:
    """A chronological anchor point in the timeline."""
    anchor_id: str
    event: str
    year: int | None = None
    offset: int | None = None
    description: str = ...
    source: str = ...
    immutable: bool = ...

class TimelineManager:
    """Manager for timeline anchors across canon workflows."""

    def __init__(self) -> None: ...

    def add_anchor(
        self,
        anchor_id: str,
        event: str,
        year: int | None = None,
        offset: int | None = None,
        description: str = "",
        source: str = "",
        immutable: bool = False,
    ) -> TimelineAnchor: ...

    def get_anchor(self, anchor_id: str) -> TimelineAnchor | None: ...

    def get_baseline_anchors(self) -> list[TimelineAnchor]: ...

    def get_extension_anchors(self) -> list[TimelineAnchor]: ...

    def update_anchor(
        self,
        anchor_id: str,
        event: str | None = None,
        year: int | None = None,
        offset: int | None = None,
        description: str | None = None,
    ) -> TimelineAnchor: ...

    def delete_anchor(self, anchor_id: str) -> bool: ...

    def validate_chronology(self) -> list[str]: ...

    def merge(
        self,
        anchors: list[TimelineAnchor],
        deduplicate: bool = True,
    ) -> dict[str, Any]: ...

    def count(self) -> int: ...

    def to_dict(self) -> dict[str, Any]: ...
