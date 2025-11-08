"""Google Imagen 4 image generation provider."""

import base64
import os
from typing import Any

from ..base import ImageProvider


class ImagenProvider(ImageProvider):
    """
    Google Imagen 4 image generation provider.

    Provides access to Google's Imagen 4 model via Vertex AI API.

    Configuration:
        project_id: Google Cloud project ID (or set GOOGLE_CLOUD_PROJECT env var)
        location: GCP region (default: "us-central1")
        api_key: Google Cloud API key (or set GOOGLE_CLOUD_API_KEY env var)
        model: Model name (default: "imagen-4.0-preview")
        aspect_ratio: Image aspect ratio (default: "1:1")
        safety_filter_level: Safety filter level (default: "BLOCK_SOME")
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Imagen provider.

        Args:
            config: Configuration with project_id and optional settings

        Raises:
            ValueError: If project_id or API key is missing
        """
        super().__init__(config)

        # Get project ID from config or environment
        self.project_id = config.get("project_id") or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError(
                "Google Cloud project ID required. "
                "Set 'project_id' in config or GOOGLE_CLOUD_PROJECT env var"
            )

        # Get API key from config or environment
        self.api_key = config.get("api_key") or os.getenv("GOOGLE_CLOUD_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google Cloud API key required. "
                "Set 'api_key' in config or GOOGLE_CLOUD_API_KEY env var"
            )

        # Model settings
        self.location = config.get("location", "us-central1")
        self.model = config.get("model", "imagen-4.0-preview")
        self.aspect_ratio = config.get("aspect_ratio", "1:1")
        self.safety_filter_level = config.get("safety_filter_level", "BLOCK_SOME")

    def generate_image(
        self,
        prompt: str,
        model: str | None = None,
        width: int | None = None,
        height: int | None = None,
        **kwargs: Any,
    ) -> bytes:
        """
        Generate image using Google Imagen.

        Args:
            prompt: Text prompt for image generation
            width: Image width in pixels (aspect ratio takes precedence)
            height: Image height in pixels (aspect ratio takes precedence)
            **kwargs: Additional generation parameters

        Returns:
            Generated image as bytes

        Raises:
            RuntimeError: If API call fails
        """
        try:
            from google.cloud import aiplatform  # type: ignore
            from vertexai.preview.vision_models import (
                ImageGenerationModel,  # type: ignore
            )
        except ImportError:
            raise RuntimeError(
                "google-cloud-aiplatform library required for Imagen provider. "
                "Install with: pip install google-cloud-aiplatform"
            )

        # Initialize Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)

        # Use provided model or default
        model_name = model if model is not None else self.model

        # Load model
        try:
            gen_model = ImageGenerationModel.from_pretrained(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load Imagen model: {e}")

        # Generate image
        try:
            # Determine aspect ratio from width/height if provided
            aspect_ratio = self.aspect_ratio
            if width and height:
                if width == height:
                    aspect_ratio = "1:1"
                elif width > height:
                    aspect_ratio = "16:9" if width / height > 1.5 else "4:3"
                else:
                    aspect_ratio = "9:16" if height / width > 1.5 else "3:4"

            # Generate
            response = gen_model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                safety_filter_level=self.safety_filter_level,
                **kwargs,
            )

            # Extract image bytes
            if response.images and len(response.images) > 0:
                # Images are returned as PIL Image objects or base64 strings
                image = response.images[0]

                # If it's a base64 string, decode it
                if isinstance(image, str):
                    return base64.b64decode(image)

                # If it's an image object with _image_bytes attribute
                if hasattr(image, "_image_bytes"):
                    return image._image_bytes

                # If it's a PIL Image, convert to bytes
                try:
                    from io import BytesIO

                    buffer = BytesIO()
                    image.save(buffer, format="PNG")
                    return buffer.getvalue()
                except Exception:
                    pass

                raise RuntimeError("Unable to extract image bytes from response")
            else:
                raise RuntimeError("No images returned from Imagen API")

        except Exception as e:
            raise RuntimeError(f"Imagen API call failed: {e}")

    def validate_config(self) -> None:
        """
        Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            from google.cloud import aiplatform  # type: ignore
        except ImportError:
            raise ValueError(
                "google-cloud-aiplatform library required for Imagen provider. "
                "Install with: pip install google-cloud-aiplatform"
            )

        # Test credentials by initializing Vertex AI
        try:
            aiplatform.init(project=self.project_id, location=self.location)
        except Exception as e:
            raise ValueError(f"Invalid Imagen configuration: {e}")

    def __repr__(self) -> str:
        """String representation."""
        has_credentials = bool(self.project_id and self.api_key)
        return (
            f"ImagenProvider(model={self.model}, project={self.project_id}, "
            f"location={self.location}, has_credentials={has_credentials})"
        )
