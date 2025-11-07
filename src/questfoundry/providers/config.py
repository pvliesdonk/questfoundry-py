"""Configuration management for QuestFoundry providers"""

import os
import re
from pathlib import Path
from typing import Any

import yaml


class ProviderConfig:
    """
    Manages provider configuration with environment variable substitution.

    Configuration files use YAML format and support ${ENV_VAR} syntax
    for environment variable substitution.

    Example config.yml:
        providers:
          text:
            default: openai
            openai:
              api_key: ${OPENAI_API_KEY}
              model: gpt-4o
            ollama:
              base_url: http://localhost:11434
              model: llama3
    """

    ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")

    def __init__(self, config_path: Path | str | None = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config file. If None, looks for
                        .questfoundry/config.yml in current directory.
        """
        if config_path is None:
            config_path = Path.cwd() / ".questfoundry" / "config.yml"
        else:
            config_path = Path(config_path)

        self.config_path = config_path
        self._config: dict[str, Any] = {}

        if config_path.exists():
            self.load()
        else:
            self._config = self._get_default_config()

    def load(self) -> None:
        """
        Load configuration from file.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid YAML
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path) as f:
                raw_config = yaml.safe_load(f)
                self._config = self._substitute_env_vars(raw_config or {})
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}") from e

    def save(self) -> None:
        """
        Save configuration to file.

        Creates parent directories if they don't exist.
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w") as f:
            yaml.safe_dump(self._config, f, default_flow_style=False)

    def get_provider_config(
        self, provider_type: str, provider_name: str
    ) -> dict[str, Any]:
        """
        Get configuration for a specific provider.

        Args:
            provider_type: Type of provider ('text' or 'image')
            provider_name: Name of provider (e.g., 'openai', 'ollama')

        Returns:
            Provider configuration dictionary

        Raises:
            KeyError: If provider not found in configuration
        """
        providers = self._config.get("providers", {})
        provider_configs = providers.get(provider_type, {})

        if provider_name not in provider_configs:
            raise KeyError(
                f"{provider_type} provider '{provider_name}' not found in configuration"
            )

        # Filter out 'default' key
        config = provider_configs.get(provider_name, {})
        if isinstance(config, dict):
            return config
        return {}

    def get_default_provider(self, provider_type: str) -> str | None:
        """
        Get default provider name for a type.

        Args:
            provider_type: Type of provider ('text' or 'image')

        Returns:
            Default provider name, or None if not configured
        """
        providers = self._config.get("providers", {})
        provider_configs = providers.get(provider_type, {})
        default = provider_configs.get("default")
        return str(default) if default is not None else None

    def set_default_provider(self, provider_type: str, provider_name: str) -> None:
        """
        Set default provider for a type.

        Args:
            provider_type: Type of provider ('text' or 'image')
            provider_name: Name of provider
        """
        providers = self._config.setdefault("providers", {})
        provider_config = providers.setdefault(provider_type, {})
        provider_config["default"] = provider_name

    def list_providers(self, provider_type: str) -> list[str]:
        """
        List available providers of a given type.

        Args:
            provider_type: Type of provider ('text' or 'image')

        Returns:
            List of provider names
        """
        providers = self._config.get("providers", {})
        provider_configs = providers.get(provider_type, {})

        # Exclude 'default' key from list
        return [name for name in provider_configs.keys() if name != "default"]

    def _substitute_env_vars(self, obj: Any) -> Any:
        """
        Recursively substitute environment variables in configuration.

        Replaces ${ENV_VAR} with os.environ['ENV_VAR'].

        Args:
            obj: Configuration object (dict, list, str, etc.)

        Returns:
            Object with environment variables substituted
        """
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            return self._substitute_env_var_in_string(obj)
        return obj

    def _substitute_env_var_in_string(self, value: str) -> str:
        """
        Substitute environment variables in a string.

        Args:
            value: String potentially containing ${ENV_VAR} patterns

        Returns:
            String with variables substituted

        Raises:
            ValueError: If a referenced environment variable is not set
        """

        def replace_match(match: re.Match[str]) -> str:
            env_var = match.group(1)
            env_value = os.environ.get(env_var)
            if env_value is None:
                raise ValueError(
                    f"Environment variable '{env_var}' is not set. "
                    f"Please set it before loading configuration."
                )
            return env_value

        return self.ENV_VAR_PATTERN.sub(replace_match, value)

    def _get_default_config(self) -> dict[str, Any]:
        """
        Get default configuration structure.

        Returns:
            Default configuration dictionary
        """
        return {
            "providers": {
                "text": {
                    "default": "openai",
                },
                "image": {
                    "default": "dalle",
                },
            }
        }
