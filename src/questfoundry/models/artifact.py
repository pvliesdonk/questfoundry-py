"""Pydantic models for QuestFoundry artifacts"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Artifact(BaseModel):  # type: ignore[misc]
    """Base artifact model"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"type": "hook_card", "data": {}, "metadata": {}}
        }
    )

    type: str = Field(..., description="Artifact type (e.g., 'hook_card')")
    data: dict[str, Any] = Field(default_factory=dict, description="Artifact data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata")

class HookCard(Artifact):
    """Hook Card artifact"""
    type: str = "hook_card"

class TUBrief(Artifact):
    """Thematic Unit Brief artifact"""
    type: str = "tu_brief"
