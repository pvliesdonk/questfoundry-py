# Provider API Reference

The `questfoundry.providers` module provides a pluggable architecture for integrating with external AI services (LLMs, image generation, audio generation, etc.). It implements a registry pattern with configuration management and automatic provider discovery.

## Overview

The provider system consists of:

- **Provider Base Classes**: Abstract interfaces for different provider types
- **Provider Registry**: Central registry for discovering and instantiating providers
- **Provider Config**: Configuration management with environment variable support
- **Built-in Providers**: Text (OpenAI, Ollama) and Image (DALL-E, Automatic1111)

## Quick Start

```python
from questfoundry.providers import ProviderRegistry, ProviderConfig

# Load configuration (from .questfoundry/config.yml)
config = ProviderConfig()
registry = ProviderRegistry(config)

# Get text provider (default or by name)
text_provider = registry.get_text_provider()  # Uses default
# text_provider = registry.get_text_provider("openai")  # Specific provider

# Generate text
response = text_provider.generate_text(
    prompt="Write a fantasy hook about a dragon",
    max_tokens=200,
    temperature=0.7
)
print(response)

# Get image provider
image_provider = registry.get_image_provider("dalle")

# Generate image
image_data = image_provider.generate_image(
    prompt="A majestic dragon perched on ancient ruins",
    width=1024,
    height=1024
)

# Save image
with open("dragon.png", "wb") as f:
    f.write(image_data)
```

## ProviderConfig

Manages provider configuration with environment variable substitution.

### Constructor

```python
ProviderConfig(config_path: Path | str | None = None)
```

**Parameters:**
- `config_path`: Path to config file. If None, looks for `.questfoundry/config.yml` in current directory.

**Configuration File Format (YAML):**

```yaml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
      organization: org-xxxxx  # Optional
    ollama:
      base_url: http://localhost:11434
      model: llama3

  image:
    default: dalle
    dalle:
      api_key: ${OPENAI_API_KEY}
      model: dall-e-3
    a1111:
      base_url: http://localhost:7860
      model: sd-xl
```

**Environment Variable Substitution:**

The config supports `${ENV_VAR}` syntax for referencing environment variables:

```yaml
api_key: ${OPENAI_API_KEY}
```

This will be replaced with the value of `OPENAI_API_KEY` environment variable when the config is loaded.

**Example:**
```python
from questfoundry.providers import ProviderConfig

# Load from default location
config = ProviderConfig()

# Load from custom path
config = ProviderConfig("/path/to/config.yml")

# Load will raise ValueError if referenced environment variables are not set
```

### Methods

#### `load()`

```python
def load() -> None
```

Load configuration from file.

**Raises:**
- `FileNotFoundError`: If config file doesn't exist
- `ValueError`: If config file is invalid YAML or if a referenced environment variable is not set

**Example:**
```python
config = ProviderConfig("./config.yml")
try:
    config.load()
except FileNotFoundError:
    print("Config file not found")
except ValueError as e:
    print(f"Invalid config: {e}")
```

#### `save()`

```python
def save() -> None
```

Save configuration to file. Creates parent directories if they don't exist.

**Example:**
```python
config = ProviderConfig()
config.set_default_provider("text", "ollama")
config.save()
```

#### `get_provider_config()`

```python
def get_provider_config(
    provider_type: str,
    provider_name: str
) -> dict[str, Any]
```

Get configuration for a specific provider.

**Parameters:**
- `provider_type`: Type of provider ("text" or "image")
- `provider_name`: Name of provider (e.g., "openai", "ollama")

**Returns:** Provider configuration dictionary

**Raises:**
- `KeyError`: If provider not found in configuration

**Example:**
```python
openai_config = config.get_provider_config("text", "openai")
print(f"Model: {openai_config['model']}")
print(f"API Key: {openai_config['api_key']}")
```

#### `get_default_provider()`

```python
def get_default_provider(provider_type: str) -> str | None
```

Get default provider name for a type.

**Parameters:**
- `provider_type`: Type of provider ("text" or "image")

**Returns:** Default provider name, or None if not configured

**Example:**
```python
default_text = config.get_default_provider("text")
print(f"Default text provider: {default_text}")
```

#### `set_default_provider()`

```python
def set_default_provider(
    provider_type: str,
    provider_name: str
) -> None
```

Set default provider for a type.

**Parameters:**
- `provider_type`: Type of provider ("text" or "image")
- `provider_name`: Name of provider

**Example:**
```python
config.set_default_provider("text", "ollama")
config.save()  # Persist to file
```

#### `list_providers()`

```python
def list_providers(provider_type: str) -> list[str]
```

List available providers of a given type in configuration.

**Parameters:**
- `provider_type`: Type of provider ("text" or "image")

**Returns:** List of provider names

**Example:**
```python
text_providers = config.list_providers("text")
print(f"Available text providers: {text_providers}")
# Output: ['openai', 'ollama']
```

## ProviderRegistry

Registry for managing text and image providers. Handles provider instantiation, configuration, and caching.

### Constructor

```python
ProviderRegistry(config: ProviderConfig)
```

**Parameters:**
- `config`: Provider configuration

**Example:**
```python
from questfoundry.providers import ProviderRegistry, ProviderConfig

config = ProviderConfig()
registry = ProviderRegistry(config)
```

### Provider Access Methods

#### `get_text_provider()`

```python
def get_text_provider(name: str | None = None) -> TextProvider
```

Get or create a text provider instance. Instances are cached for reuse.

**Parameters:**
- `name`: Provider name. If None, uses default from config.

**Returns:** Text provider instance

**Raises:**
- `ValueError`: If provider not found or not registered, or if no default configured

**Example:**
```python
# Get default text provider
provider = registry.get_text_provider()

# Get specific provider
openai = registry.get_text_provider("openai")
ollama = registry.get_text_provider("ollama")

# Cached - returns same instance
provider2 = registry.get_text_provider()
assert provider is provider2
```

#### `get_image_provider()`

```python
def get_image_provider(name: str | None = None) -> ImageProvider
```

Get or create an image provider instance. Instances are cached for reuse.

**Parameters:**
- `name`: Provider name. If None, uses default from config.

**Returns:** Image provider instance

**Raises:**
- `ValueError`: If provider not found or not registered, or if no default configured

**Example:**
```python
# Get default image provider
provider = registry.get_image_provider()

# Get specific provider
dalle = registry.get_image_provider("dalle")
sd = registry.get_image_provider("a1111")
```

### Provider Registration Methods

#### `register_text_provider()`

```python
def register_text_provider(
    name: str,
    provider_class: type[TextProvider]
) -> None
```

Register a custom text provider class.

**Parameters:**
- `name`: Provider name (e.g., "custom", "anthropic")
- `provider_class`: Provider class to register (must extend TextProvider)

**Example:**
```python
from questfoundry.providers import TextProvider

class CustomTextProvider(TextProvider):
    def validate_config(self):
        # Implementation...
        pass

    def generate_text(self, prompt, **kwargs):
        # Implementation...
        return "generated text"

    def generate_text_streaming(self, prompt, **kwargs):
        # Implementation...
        yield "chunk1"

registry.register_text_provider("custom", CustomTextProvider)

# Now can use it
provider = registry.get_text_provider("custom")
```

#### `register_image_provider()`

```python
def register_image_provider(
    name: str,
    provider_class: type[ImageProvider]
) -> None
```

Register a custom image provider class.

**Parameters:**
- `name`: Provider name (e.g., "midjourney", "imagen")
- `provider_class`: Provider class to register (must extend ImageProvider)

**Example:**
```python
from questfoundry.providers import ImageProvider

class CustomImageProvider(ImageProvider):
    def validate_config(self):
        # Implementation...
        pass

    def generate_image(self, prompt, **kwargs):
        # Implementation...
        return b"...image bytes..."

registry.register_image_provider("custom", CustomImageProvider)
```

### Utility Methods

#### `list_text_providers()`

```python
def list_text_providers() -> list[str]
```

List registered text providers.

**Returns:** List of text provider names

**Example:**
```python
providers = registry.list_text_providers()
print(f"Available: {providers}")
# Output: ['openai', 'ollama', 'custom']
```

#### `list_image_providers()`

```python
def list_image_providers() -> list[str]
```

List registered image providers.

**Returns:** List of image provider names

**Example:**
```python
providers = registry.list_image_providers()
print(f"Available: {providers}")
# Output: ['dalle', 'a1111']
```

#### `close_all()`

```python
def close_all() -> None
```

Close all provider instances and release resources. Clears the instance cache.

**Example:**
```python
# Use providers...
# ...

# Clean up all resources
registry.close_all()
```

## Base Classes

### Provider

Abstract base class for all providers.

**Methods:**

#### `__init__(config: dict[str, Any])`

Initialize provider with configuration.

#### `validate_config() -> None` (abstract)

Validate provider configuration. Must be implemented by subclasses.

**Raises:**
- `ValueError`: If configuration is invalid

#### `close() -> None`

Close provider and release resources. Default implementation does nothing, but providers can override to cleanup connections.

**Context Manager Support:**

All providers support context manager protocol:

```python
with registry.get_text_provider("openai") as provider:
    result = provider.generate_text("Hello")
# Provider automatically closed
```

### TextProvider

Abstract base class for text generation providers. Extends Provider.

**Abstract Methods:**

#### `generate_text()`

```python
def generate_text(
    prompt: str,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    **kwargs: Any,
) -> str
```

Generate text from a prompt.

**Parameters:**
- `prompt`: The input prompt
- `model`: Model to use (uses default if not specified)
- `max_tokens`: Maximum tokens to generate
- `temperature`: Sampling temperature (0.0 to 2.0)
- `**kwargs`: Additional provider-specific parameters

**Returns:** Generated text

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If generation fails

#### `generate_text_streaming()`

```python
def generate_text_streaming(
    prompt: str,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    **kwargs: Any,
) -> Iterator[str]
```

Generate text from a prompt with streaming.

**Parameters:** Same as `generate_text()`

**Yields:** Text chunks as they are generated

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If generation fails

### ImageProvider

Abstract base class for image generation providers. Extends Provider.

**Abstract Method:**

#### `generate_image()`

```python
def generate_image(
    prompt: str,
    model: str | None = None,
    width: int | None = None,
    height: int | None = None,
    **kwargs: Any,
) -> bytes
```

Generate an image from a text prompt.

**Parameters:**
- `prompt`: The text prompt describing the image
- `model`: Model to use (uses default if not specified)
- `width`: Image width in pixels
- `height`: Image height in pixels
- `**kwargs`: Additional provider-specific parameters

**Returns:** Image data as bytes (typically PNG format)

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If generation fails

## Built-in Providers

### Text Providers

#### OpenAIProvider

OpenAI text generation provider using GPT models.

**Configuration:**
```yaml
providers:
  text:
    openai:
      api_key: ${OPENAI_API_KEY}  # Required
      model: gpt-4o              # Optional, default: gpt-4o
      organization: org-xxxxx     # Optional
      base_url: https://...       # Optional (for proxies)
```

**Installation:**
```bash
pip install questfoundry[openai]
```

**Example:**
```python
provider = registry.get_text_provider("openai")

# Basic generation
text = provider.generate_text(
    prompt="Write a fantasy scene",
    max_tokens=500,
    temperature=0.7
)

# With OpenAI-specific parameters
text = provider.generate_text(
    prompt="Write a fantasy scene",
    max_tokens=500,
    temperature=0.7,
    top_p=0.9,
    frequency_penalty=0.5,
    presence_penalty=0.5
)

# Streaming
for chunk in provider.generate_text_streaming(
    prompt="Write a long story",
    temperature=0.8
):
    print(chunk, end="", flush=True)
```

**Supported Models:**
- gpt-4o (default)
- gpt-4-turbo
- gpt-4
- gpt-3.5-turbo
- All OpenAI chat models

#### OllamaProvider

Local Ollama text generation provider.

**Configuration:**
```yaml
providers:
  text:
    ollama:
      base_url: http://localhost:11434  # Required
      model: llama3                     # Optional, default: llama3
```

**Installation:**
```bash
pip install questfoundry[ollama]
# Also requires Ollama running locally
```

**Example:**
```python
provider = registry.get_text_provider("ollama")

text = provider.generate_text(
    prompt="Write a fantasy hook",
    max_tokens=200,
    temperature=0.9
)

# Streaming
for chunk in provider.generate_text_streaming(prompt="Tell a story"):
    print(chunk, end="", flush=True)
```

**Supported Models:**
- llama3 (default)
- llama2
- mistral
- Any model available in your Ollama installation

### Image Providers

#### DalleProvider

OpenAI DALL-E image generation provider.

**Configuration:**
```yaml
providers:
  image:
    dalle:
      api_key: ${OPENAI_API_KEY}  # Required
      model: dall-e-3              # Optional, default: dall-e-3
```

**Installation:**
```bash
pip install questfoundry[openai]
```

**Example:**
```python
provider = registry.get_image_provider("dalle")

image_data = provider.generate_image(
    prompt="A majestic dragon on a mountain peak",
    width=1024,
    height=1024,
    # DALL-E specific parameters
    quality="hd",
    style="vivid"
)

with open("dragon.png", "wb") as f:
    f.write(image_data)
```

**Supported Models:**
- dall-e-3 (default) - 1024x1024, 1024x1792, 1792x1024
- dall-e-2 - 256x256, 512x512, 1024x1024

#### Automatic1111Provider

Stable Diffusion via Automatic1111 Web UI.

**Configuration:**
```yaml
providers:
  image:
    a1111:
      base_url: http://localhost:7860  # Required
      model: sd-xl                     # Optional, default: sd-xl
```

**Installation:**
```bash
pip install questfoundry[image]
# Also requires Automatic1111 Web UI running locally
```

**Example:**
```python
provider = registry.get_image_provider("a1111")

image_data = provider.generate_image(
    prompt="fantasy dragon, highly detailed, 4k",
    width=512,
    height=512,
    # A1111 specific parameters
    negative_prompt="blurry, low quality",
    steps=30,
    cfg_scale=7.5,
    sampler_name="Euler a"
)

with open("dragon.png", "wb") as f:
    f.write(image_data)
```

**Supported Parameters:**
- `negative_prompt`: What to avoid in generation
- `steps`: Number of inference steps (default: 20)
- `cfg_scale`: Classifier-free guidance scale (default: 7.0)
- `sampler_name`: Sampler algorithm (e.g., "Euler a", "DPM++ 2M")
- `seed`: Random seed for reproducibility

## Usage Patterns

### Basic Text Generation

```python
from questfoundry.providers import ProviderRegistry, ProviderConfig

config = ProviderConfig()
registry = ProviderRegistry(config)

# Get provider
provider = registry.get_text_provider()

# Generate text
scene = provider.generate_text(
    prompt="""
Write a fantasy scene where the protagonist discovers
an ancient artifact in a forgotten temple.
""",
    max_tokens=500,
    temperature=0.8
)

print(scene)
```

### Streaming Text Generation

```python
provider = registry.get_text_provider("openai")

print("Generating story...")
for chunk in provider.generate_text_streaming(
    prompt="Write a long adventure story",
    max_tokens=2000,
    temperature=0.9
):
    print(chunk, end="", flush=True)
print("\nDone!")
```

### Image Generation

```python
provider = registry.get_image_provider("dalle")

# Generate image
image_data = provider.generate_image(
    prompt="A mystical forest with glowing mushrooms",
    width=1024,
    height=1024
)

# Save to file
from pathlib import Path
output = Path("generated_images")
output.mkdir(exist_ok=True)
(output / "forest.png").write_bytes(image_data)
```

### Multi-Provider Setup

```python
# Use different providers for different tasks
openai = registry.get_text_provider("openai")
ollama = registry.get_text_provider("ollama")
dalle = registry.get_image_provider("dalle")

# Use OpenAI for creative writing
story = openai.generate_text(
    prompt="Write a dramatic scene",
    temperature=0.9
)

# Use Ollama for structured output (faster, cheaper)
summary = ollama.generate_text(
    prompt=f"Summarize this scene in 3 bullet points:\n\n{story}",
    temperature=0.3
)

# Generate illustration
image = dalle.generate_image(
    prompt=summary,
    width=1024,
    height=1024
)
```

### Provider Comparison

```python
providers = ["openai", "ollama"]
prompt = "Write a short fantasy hook about a dragon"

results = {}
for provider_name in providers:
    provider = registry.get_text_provider(provider_name)
    result = provider.generate_text(prompt, max_tokens=100)
    results[provider_name] = result

for name, text in results.items():
    print(f"\n{name}:\n{text}\n")
```

### Error Handling

```python
from questfoundry.providers import ProviderRegistry, ProviderConfig

try:
    config = ProviderConfig()
    registry = ProviderRegistry(config)
    provider = registry.get_text_provider("openai")

    text = provider.generate_text("Write a scene")
    print(text)

except ValueError as e:
    # Configuration or parameter errors
    print(f"Configuration error: {e}")

except RuntimeError as e:
    # API call failures
    print(f"Generation failed: {e}")

except ImportError as e:
    # Missing dependencies
    print(f"Install required package: {e}")
```

### Context Manager Pattern

```python
config = ProviderConfig()
registry = ProviderRegistry(config)

# Automatic cleanup
with registry.get_text_provider("openai") as provider:
    result = provider.generate_text("Hello world")
# Provider closed automatically

# Or manually
provider = registry.get_text_provider("openai")
try:
    result = provider.generate_text("Hello world")
finally:
    provider.close()
```

### Custom Provider Implementation

```python
from questfoundry.providers import TextProvider
from typing import Any, Iterator

class MyCustomProvider(TextProvider):
    """Custom text provider implementation."""

    def validate_config(self) -> None:
        """Validate configuration."""
        if "api_key" not in self.config:
            raise ValueError("api_key required")

    def generate_text(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text."""
        # Your implementation here
        api_key = self.config["api_key"]
        # ... call your API ...
        return "generated text"

    def generate_text_streaming(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Generate text with streaming."""
        # Your implementation here
        yield "chunk 1"
        yield "chunk 2"

    def close(self) -> None:
        """Cleanup resources."""
        # Close connections, etc.
        pass

# Register and use
registry.register_text_provider("custom", MyCustomProvider)
provider = registry.get_text_provider("custom")
```

## Configuration Best Practices

1. **Use environment variables** for sensitive data:
   ```yaml
   api_key: ${OPENAI_API_KEY}  # Good
   # api_key: sk-xxxxx  # Bad - don't commit secrets
   ```

2. **Set reasonable defaults**:
   ```yaml
   openai:
     api_key: ${OPENAI_API_KEY}
     model: gpt-4o
     max_tokens: 2000  # Reasonable default
     temperature: 0.7
   ```

3. **Use different providers** for different tasks:
   - OpenAI GPT-4: Creative writing, complex reasoning
   - Ollama (local): Fast iterations, structured output, development
   - DALL-E: High-quality illustrations
   - Stable Diffusion: Rapid prototyping, style exploration

4. **Cache provider instances**:
   ```python
   # Good - reuses instance
   provider = registry.get_text_provider()

   # Avoid - creates new instances
   for i in range(100):
       p = registry.get_text_provider()  # Wasteful
   ```

5. **Clean up resources**:
   ```python
   # Always cleanup when done
   registry.close_all()

   # Or use context managers
   with registry.get_text_provider() as provider:
       # Use provider
       pass
   ```

## See Also

- [Protocol API](protocol.md) - Message passing with envelopes
- [State Management API](state.md) - Project storage
- [Roles API](roles.md) - Role execution with providers
