"""Type stubs for provider configuration"""

from typing import Any

from pydantic import BaseModel

class ProviderConfig(BaseModel):
    """Configuration for a provider instance."""
    name: str
    provider_type: str
    config: dict[str, Any]
    default_params: dict[str, Any]
