# Epic 15.2 - Per-Role Provider Configuration Design

## Overview

Allows each role to use different providers and models, enabling cost-effective architectures (e.g., expensive model for creative tasks, cheap model for validation).

## Design Decisions

### 1. Configuration Hierarchy

Three levels of configuration with increasing specificity:

```
1. Default Provider (global fallback)
   providers:
     text:
       default: openai

2. Role Configuration (role-specific)
   roles:
     scene_smith:
       provider: openai
       model: gpt-4o

3. Runtime Override (method parameter)
   role.execute_task(context, provider=some_provider)
```

Lookup order: Runtime > Role Config > Default Provider

### 2. Configuration Schema

```yaml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
    ollama:
      base_url: http://localhost:11434
      model: llama3

roles:
  scene_smith:
    provider: openai
    model: gpt-4o
    temperature: 0.8
    max_tokens: 3000

  gatekeeper:
    provider: ollama
    model: llama3
    temperature: 0.2  # Very deterministic
    max_tokens: 1000

  illustrator:
    provider: dalle
    model: dall-e-3
    width: 1024
    height: 1024

  audio_director:
    provider: elevenlabs
    voice: nova
    language: en
```

### 3. Role Type Detection

```python
# Automatically detect role type from role name
ROLE_TYPE_MAP = {
    "illustrator": "image",
    "art_director": "image",
    "audio_director": "audio",
    "audio_producer": "audio",
    # All others: "text"
}
```

### 4. Provider Instance Caching

Cache provider instances to avoid repeated initialization:

```
Showrunner
  ├─ _provider_cache: Dict[str, Provider]
  │   ├─ "openai": OpenAIProvider(...)
  │   ├─ "ollama": OllamaProvider(...)
  │   └─ "dalle": DALLEProvider(...)
  └─ _role_instances: Dict[str, Role]
      ├─ "scene_smith": SceneSmith(openai_provider)
      ├─ "gatekeeper": Gatekeeper(ollama_provider)
      └─ "illustrator": Illustrator(dalle_provider)
```

## Implementation Details

### Enhanced ProviderConfig

```python
class ProviderConfig:
    """Extended configuration with role support"""

    def get_role_provider_name(
        self,
        role_name: str,
        provider_type: str = "text"
    ) -> str:
        """Get provider name for a role"""
        roles_config = self._config.get("roles", {})
        role_config = roles_config.get(role_name, {})

        # Check if provider specified
        if "provider" in role_config:
            return role_config["provider"]

        # Fall back to default
        return self.get_default_provider(provider_type)

    def get_role_config(self, role_name: str) -> dict[str, Any]:
        """Get all configuration for a role"""
        roles_config = self._config.get("roles", {})
        return roles_config.get(role_name, {})

    def get_role_parameter(
        self,
        role_name: str,
        parameter: str,
        default: Any = None
    ) -> Any:
        """Get specific parameter for a role"""
        role_config = self.get_role_config(role_name)
        return role_config.get(parameter, default)

    def is_role_configured(self, role_name: str) -> bool:
        """Check if role has specific configuration"""
        roles_config = self._config.get("roles", {})
        return role_name in roles_config

    @staticmethod
    def _infer_provider_type(role_name: str) -> str:
        """Infer provider type from role name"""
        image_roles = {"illustrator", "art_director"}
        audio_roles = {"audio_director", "audio_producer"}

        if role_name in image_roles:
            return "image"
        elif role_name in audio_roles:
            return "audio"
        else:
            return "text"
```

### Enhanced Role Base Class

```python
@dataclass
class RoleContext:
    """Extended context with provider info"""
    task: str
    artifacts: list[Artifact] = field(default_factory=list)
    project_metadata: dict[str, Any] = field(default_factory=dict)
    workspace_path: Path | None = None
    additional_context: dict[str, Any] = field(default_factory=dict)

    # NEW: Role-specific configuration
    role_config: dict[str, Any] = field(default_factory=dict)
    provider_name: str | None = None  # For logging/debugging

class Role(ABC):
    def __init__(
        self,
        provider: TextProvider,
        spec_path: Path | None = None,
        config: dict[str, Any] | None = None,
        session: "RoleSession | None" = None,
        human_callback: "HumanCallback | None" = None,
        role_config: dict[str, Any] | None = None,  # NEW
    ):
        self.provider = provider
        self.config = config or {}
        self.session = session
        self.human_callback = human_callback
        self.role_config = role_config or {}  # NEW

        # Set default model/temperature from role config if available
        if "model" in self.role_config:
            self.default_model = self.role_config["model"]

        if "temperature" in self.role_config:
            self.default_temperature = self.role_config["temperature"]

        if "max_tokens" in self.role_config:
            self.default_max_tokens = self.role_config["max_tokens"]

        # Determine spec path...
        if spec_path is None:
            spec_path = Path.cwd() / "spec"
            if not spec_path.exists():
                spec_path = (
                    Path(__file__).parent.parent.parent.parent / "spec"
                )

        self.spec_path = spec_path
        self._prompt_cache: dict[str, str] = {}

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Call LLM with role-specific settings"""
        # Use role config values if not overridden
        if max_tokens is None and "max_tokens" in self.role_config:
            max_tokens = self.role_config["max_tokens"]
        if temperature is None and "temperature" in self.role_config:
            temperature = self.role_config["temperature"]

        # Call provider with effective settings
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        return self.provider.generate_text(
            prompt=full_prompt,
            model=self.role_config.get("model"),
            max_tokens=max_tokens or self.config.get("max_tokens", 2000),
            temperature=temperature or self.config.get("temperature", 0.7),
        )
```

### Showrunner Enhanced Implementation

```python
class Showrunner:
    """Main orchestrator for QuestFoundry workflows"""

    def __init__(self, config: ProviderConfig | None = None):
        self.config = config or ProviderConfig()
        self._provider_cache: dict[str, Provider] = {}
        self._role_instances: dict[str, Role] = {}

    def _get_provider(self, provider_name: str, provider_type: str = "text") -> Provider:
        """Get or create provider instance"""
        cache_key = f"{provider_type}:{provider_name}"

        if cache_key in self._provider_cache:
            return self._provider_cache[cache_key]

        # Get provider config
        provider_config = self.config.get_provider_config(provider_type, provider_name)

        # Instantiate provider
        provider_class = self._get_provider_class(provider_type, provider_name)
        provider = provider_class(provider_config)

        # Cache it
        self._provider_cache[cache_key] = provider

        return provider

    def _get_provider_class(self, provider_type: str, provider_name: str) -> type:
        """Get provider class for name"""
        from questfoundry.providers.registry import ProviderRegistry

        registry = ProviderRegistry(provider_type)
        return registry.get(provider_name)

    def _initialize_role(
        self,
        role_class: type,
        role_name: str
    ) -> Role:
        """Initialize role with its configured provider"""
        # Determine provider type for this role
        provider_type = ProviderConfig._infer_provider_type(role_name)

        # Get role's provider
        provider_name = self.config.get_role_provider_name(role_name, provider_type)
        provider = self._get_provider(provider_name, provider_type)

        # Get role-specific config
        role_config = self.config.get_role_config(role_name)

        # Create role instance
        role = role_class(
            provider=provider,
            config={},  # General config
            role_config=role_config,  # Role-specific config
        )

        return role

    def get_role(self, role_name: str) -> Role:
        """Get or create role instance"""
        if role_name in self._role_instances:
            return self._role_instances[role_name]

        # Import role class
        role_class = self._get_role_class(role_name)

        # Initialize with configured provider
        role = self._initialize_role(role_class, role_name)

        # Cache it
        self._role_instances[role_name] = role

        return role

    def _get_role_class(self, role_name: str) -> type:
        """Get role class for name"""
        from questfoundry.roles.registry import RoleRegistry

        registry = RoleRegistry()
        return registry.get(role_name)

    def close(self):
        """Close all provider connections"""
        for provider in self._provider_cache.values():
            provider.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

### Role Registry Pattern

The Showrunner uses a role registry to dynamically instantiate roles:

```python
class RoleRegistry:
    """Registry for role classes"""

    _roles = {}

    @classmethod
    def register(cls, role_name: str, role_class: type):
        cls._roles[role_name] = role_class

    @classmethod
    def get(cls, role_name: str) -> type:
        if role_name not in cls._roles:
            raise ValueError(f"Unknown role: {role_name}")
        return cls._roles[role_name]

    @classmethod
    def list_roles(cls) -> list[str]:
        return list(cls._roles.keys())

# Register all roles at module load time
RoleRegistry.register("scene_smith", SceneSmith)
RoleRegistry.register("gatekeeper", Gatekeeper)
RoleRegistry.register("illustrator", Illustrator)
# ... etc
```

## Configuration Examples

### Example 1: Cost-Optimized

```yaml
# Use cheap model for validation, expensive for creation
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
    ollama:
      base_url: http://localhost:11434
      model: llama3

roles:
  # Expensive, complex tasks
  scene_smith:
    provider: openai
    model: gpt-4o
    temperature: 0.8
    max_tokens: 3000

  # Validation - use cheap local model
  gatekeeper:
    provider: ollama
    model: llama3
    temperature: 0.1
    max_tokens: 500

  # Creative - use good model
  lore_weaver:
    provider: openai
    model: gpt-4o
    temperature: 0.9
    max_tokens: 2000

  # Simple tasks - use cheap model
  translator:
    provider: ollama
    model: llama3
    temperature: 0.3
    max_tokens: 1000
```

### Example 2: Specialty Models

```yaml
# Use specialized models for different tasks
providers:
  text:
    default: openai
    openai:
      model: gpt-4o
    anthropic:
      model: claude-3-opus
    gemini:
      model: gemini-1.5-pro

roles:
  # Creative writing - Claude
  scene_smith:
    provider: anthropic

  # Code and logic - OpenAI
  translator:
    provider: openai

  # Analysis - Gemini
  codex_curator:
    provider: gemini
```

### Example 3: Local Development

```yaml
# All local, free
providers:
  text:
    default: ollama
    ollama:
      base_url: http://localhost:11434
      model: llama2

roles:
  scene_smith:
    provider: ollama
    model: llama2
    temperature: 0.7

  gatekeeper:
    provider: ollama
    model: llama2
    temperature: 0.2

  # Image generation
  illustrator:
    provider: a1111
    base_url: http://localhost:7860
```

## Testing Strategy

### Unit Tests

```python
def test_get_role_provider_name():
    """Test role provider lookup"""
    config = ProviderConfig()
    config._config = {
        "providers": {
            "text": {"default": "openai"}
        },
        "roles": {
            "scene_smith": {"provider": "ollama"}
        }
    }

    # Should return configured provider
    assert config.get_role_provider_name("scene_smith") == "ollama"

    # Should return default for unconfigured role
    assert config.get_role_provider_name("gatekeeper") == "openai"

def test_get_role_config():
    """Test role configuration retrieval"""
    config = ProviderConfig()
    config._config = {
        "roles": {
            "scene_smith": {
                "provider": "openai",
                "temperature": 0.8,
                "max_tokens": 3000
            }
        }
    }

    role_config = config.get_role_config("scene_smith")
    assert role_config["provider"] == "openai"
    assert role_config["temperature"] == 0.8

def test_role_uses_configured_provider():
    """Test that role uses configured provider"""
    # Mock provider
    mock_provider = Mock(spec=TextProvider)
    mock_provider.generate_text.return_value = "test"

    # Create role with role config
    role_config = {"temperature": 0.5, "max_tokens": 500}
    role = SceneSmith(
        provider=mock_provider,
        role_config=role_config
    )

    # Execute should use configured settings
    context = RoleContext(task="test")
    role.execute_task(context)

    # Verify provider was called with role config
    call_args = mock_provider.generate_text.call_args
    assert call_args.kwargs["temperature"] == 0.5
    assert call_args.kwargs["max_tokens"] == 500

def test_showrunner_role_initialization():
    """Test showrunner initializes roles with correct providers"""
    config = ProviderConfig()
    config._config = {
        "providers": {
            "text": {
                "default": "openai",
                "openai": {"api_key": "test"},
                "ollama": {"base_url": "http://localhost:11434"}
            }
        },
        "roles": {
            "scene_smith": {"provider": "openai"},
            "gatekeeper": {"provider": "ollama"}
        }
    }

    # Mock provider classes
    with patch("questfoundry.roles.showrunner.ProviderRegistry"):
        showrunner = Showrunner(config)
        # Test would verify correct providers created
```

## Integration with Existing Code

1. **Backward Compatibility**: If role config not specified, falls back to default provider
2. **No Breaking Changes**: Existing code without role config continues to work
3. **Opt-in**: Role-specific config is optional

## Future Enhancements

1. **Runtime Provider Override**: Pass provider at execution time
2. **Provider Fallback**: Specify fallback provider if primary fails
3. **A/B Testing**: Route some roles to different providers for comparison
4. **Cost Estimation**: Pre-calculate cost before running
5. **Role Templates**: Pre-defined role configurations
