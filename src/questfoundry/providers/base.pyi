"""Type stubs for provider base classes"""

from abc import ABC, abstractmethod
from typing import Any, Iterator

from .cache import CacheConfig, ResponseCache
from .rate_limiter import CostTracker, RateLimiter

class Provider(ABC):
    """Base class for all QuestFoundry providers."""

    config: dict[str, Any]
    cache: ResponseCache | None
    cache_config: CacheConfig | None
    rate_limiter: RateLimiter | None
    cost_tracker: CostTracker | None

    def __init__(self, config: dict[str, Any]) -> None: ...

    @abstractmethod
    def validate_config(self) -> None: ...

class TextProvider(Provider):
    """Base class for text generation providers (LLMs)."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str: ...

    @abstractmethod
    def generate_text_streaming(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> Iterator[str]: ...

    @abstractmethod
    def count_tokens(self, text: str) -> int: ...

class ImageProvider(Provider):
    """Base class for image generation providers."""

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs: Any,
    ) -> bytes: ...

    @abstractmethod
    def generate_image_url(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs: Any,
    ) -> str: ...
