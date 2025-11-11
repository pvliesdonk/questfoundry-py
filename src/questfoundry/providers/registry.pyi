"""Type stubs for provider registry"""

from typing import Any

from .base import ImageProvider, Provider, TextProvider

class ProviderRegistry:
    """Registry for managing provider instances."""

    def __init__(self) -> None: ...

    def register_text_provider(
        self, name: str, provider_class: type[TextProvider]
    ) -> None: ...

    def register_image_provider(
        self, name: str, provider_class: type[ImageProvider]
    ) -> None: ...

    def get_text_provider(self, name: str, config: dict[str, Any]) -> TextProvider: ...

    def get_image_provider(
        self, name: str, config: dict[str, Any]
    ) -> ImageProvider: ...

    def list_providers(self) -> dict[str, list[str]]: ...
