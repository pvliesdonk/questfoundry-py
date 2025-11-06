"""Abstract base classes for QuestFoundry providers"""

from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    """
    Base class for all QuestFoundry providers.

    Providers enable integration with external services for text generation,
    image generation, and other AI capabilities.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize provider with configuration.

        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config

    @abstractmethod
    def validate_config(self) -> None:
        """
        Validate provider configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    def close(self) -> None:
        """
        Close provider and release resources.

        Default implementation does nothing. Providers can override
        to cleanup connections, close clients, etc.
        """
        pass

    def __enter__(self) -> "Provider":
        """Context manager entry"""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Context manager exit"""
        self.close()


class TextProvider(Provider):
    """
    Abstract base class for text generation providers.

    Text providers interface with LLMs to generate text based on prompts.
    """

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: The input prompt
            model: Model to use (uses default if not specified)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If generation fails
        """
        pass

    @abstractmethod
    def generate_text_streaming(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Generate text from a prompt with streaming.

        Args:
            prompt: The input prompt
            model: Model to use (uses default if not specified)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional provider-specific parameters

        Yields:
            Text chunks as they are generated

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If generation fails
        """
        pass


class ImageProvider(Provider):
    """
    Abstract base class for image generation providers.

    Image providers interface with image generation models to create
    images based on text prompts.
    """

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        model: str | None = None,
        width: int | None = None,
        height: int | None = None,
        **kwargs: Any,
    ) -> bytes:
        """
        Generate an image from a text prompt.

        Args:
            prompt: The text prompt describing the image
            model: Model to use (uses default if not specified)
            width: Image width in pixels
            height: Image height in pixels
            **kwargs: Additional provider-specific parameters

        Returns:
            Image data as bytes (typically PNG format)

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If generation fails
        """
        pass
