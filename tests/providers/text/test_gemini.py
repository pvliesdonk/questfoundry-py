"""Tests for Google Gemini text provider."""

import os
from unittest.mock import MagicMock, patch

import pytest

from questfoundry.providers.text.gemini import GeminiProvider


@pytest.fixture
def mock_gemini_config():
    """Create mock Gemini config."""
    return {
        "api_key": "test-google-ai-api-key-12345",
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.7,
    }


@pytest.fixture
def provider(mock_gemini_config):
    """Create a Gemini provider with mocked config."""
    return GeminiProvider(mock_gemini_config)


def test_provider_initialization(mock_gemini_config):
    """Test provider initializes correctly."""
    provider = GeminiProvider(mock_gemini_config)

    assert provider.api_key == "test-google-ai-api-key-12345"
    assert provider.model == "gemini-2.0-flash-exp"
    assert provider.temperature == 0.7
    assert provider.top_p == 0.95
    assert provider.top_k == 40


def test_provider_initialization_with_env_var(monkeypatch):
    """Test provider uses GOOGLE_AI_API_KEY from environment."""
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "env-api-key-xyz")

    provider = GeminiProvider({})

    assert provider.api_key == "env-api-key-xyz"


def test_provider_initialization_missing_api_key():
    """Test provider raises error when API key is missing."""
    with pytest.raises(ValueError, match="Google AI API key required"):
        GeminiProvider({})


def test_provider_initialization_with_custom_settings():
    """Test provider initializes with custom settings."""
    config = {
        "api_key": "test-key",
        "model": "gemini-1.5-pro",
        "temperature": 0.5,
        "top_p": 0.9,
        "top_k": 20,
        "max_output_tokens": 2048,
    }

    provider = GeminiProvider(config)

    assert provider.model == "gemini-1.5-pro"
    assert provider.temperature == 0.5
    assert provider.top_p == 0.9
    assert provider.top_k == 20
    assert provider.max_output_tokens == 2048


def test_generate_text_success(provider):
    """Test successful text generation."""
    # Mock the genai module
    mock_genai = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is the generated response."

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    mock_google = MagicMock()
    mock_google.generativeai = mock_genai

    with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_genai}):
        result = provider.generate_text("Test prompt")

    assert result == "This is the generated response."
    mock_genai.configure.assert_called_once_with(api_key=provider.api_key)
    mock_genai.GenerativeModel.assert_called_once_with(provider.model)
    mock_model.generate_content.assert_called_once()


def test_generate_text_with_max_tokens(provider):
    """Test text generation with max_tokens override."""
    mock_genai = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Response"

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    mock_google = MagicMock()
    mock_google.generativeai = mock_genai

    with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_genai}):
        provider.generate_text("Test", max_tokens=1024)

    # Check that generation_config was passed with max_output_tokens
    call_kwargs = mock_model.generate_content.call_args[1]
    assert call_kwargs["generation_config"]["max_output_tokens"] == 1024


def test_generate_text_with_temperature_override(provider):
    """Test text generation with temperature override."""
    mock_genai = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Response"

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    mock_google = MagicMock()
    mock_google.generativeai = mock_genai

    with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_genai}):
        provider.generate_text("Test", temperature=0.9)

    # Check that generation_config uses overridden temperature
    call_kwargs = mock_model.generate_content.call_args[1]
    assert call_kwargs["generation_config"]["temperature"] == 0.9


def test_generate_text_with_parts_response(provider):
    """Test text generation when response has parts instead of text."""
    mock_genai = MagicMock()
    mock_part = MagicMock()
    mock_part.text = "Response from parts"

    mock_response = MagicMock()
    del mock_response.text  # Remove text attribute
    mock_response.parts = [mock_part]

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    mock_google = MagicMock()
    mock_google.generativeai = mock_genai

    with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_genai}):
        result = provider.generate_text("Test")

    assert result == "Response from parts"


def test_generate_text_unexpected_format(provider):
    """Test error handling for unexpected response format."""
    mock_genai = MagicMock()
    mock_response = MagicMock()
    del mock_response.text
    mock_response.parts = []

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    mock_google = MagicMock()
    mock_google.generativeai = mock_genai

    with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_genai}):
        with pytest.raises(RuntimeError, match="Unexpected response format"):
            provider.generate_text("Test")


def test_generate_text_api_error(provider):
    """Test error handling for API failures."""
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("API Error")
    mock_genai.GenerativeModel.return_value = mock_model

    mock_google = MagicMock()
    mock_google.generativeai = mock_genai

    with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_genai}):
        with pytest.raises(RuntimeError, match="Gemini API call failed: API Error"):
            provider.generate_text("Test")


def test_generate_text_missing_library(provider):
    """Test error when google-generativeai library is not installed."""
    with patch.dict("sys.modules", {"google.generativeai": None}):
        with pytest.raises(RuntimeError, match="google-generativeai library required"):
            provider.generate_text("Test")


def test_generate_text_streaming_not_implemented(provider):
    """Test that streaming raises NotImplementedError."""
    with pytest.raises(NotImplementedError, match="Streaming not yet implemented"):
        provider.generate_text_streaming("Test")


def test_validate_config_success(provider):
    """Test successful config validation."""
    mock_genai = MagicMock()
    mock_genai.list_models.return_value = [MagicMock()]

    mock_google = MagicMock()
    mock_google.generativeai = mock_genai

    with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_genai}):
        provider.validate_config()  # Should not raise

    mock_genai.configure.assert_called_once_with(api_key=provider.api_key)


def test_validate_config_invalid_api_key(provider):
    """Test config validation with invalid API key."""
    mock_genai = MagicMock()
    mock_genai.list_models.side_effect = Exception("Invalid API key")

    mock_google = MagicMock()
    mock_google.generativeai = mock_genai

    with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_genai}):
        with pytest.raises(ValueError, match="Invalid Gemini configuration"):
            provider.validate_config()


def test_validate_config_missing_library(provider):
    """Test validation error when library is not installed."""
    with patch.dict("sys.modules", {"google.generativeai": None}):
        with pytest.raises(ValueError, match="google-generativeai library required"):
            provider.validate_config()


def test_repr(provider):
    """Test string representation."""
    repr_str = repr(provider)

    assert "GeminiProvider" in repr_str
    assert "model=gemini-2.0-flash-exp" in repr_str
    assert "has_api_key=True" in repr_str


def test_repr_without_api_key():
    """Test string representation when API key is missing."""
    # Override environment to ensure no key
    with patch.dict(os.environ, {}, clear=True):
        try:
            provider = GeminiProvider({"api_key": ""})
        except ValueError:
            # If it raises on init, create with fake key and clear it
            provider = GeminiProvider({"api_key": "temp"})
            provider.api_key = None

    repr_str = repr(provider)
    assert "has_api_key=False" in repr_str
