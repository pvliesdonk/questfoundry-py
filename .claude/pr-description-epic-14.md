# Epic 14: Additional Provider Support

## Summary

Epic 14 adds three new AI provider integrations to expand QuestFoundry's capabilities: Google Gemini for text generation, Amazon Bedrock for AWS-based Claude access, and Google Imagen 4 for image generation. This implementation includes comprehensive unit tests and end-to-end integration tests that can run manually with real API keys.

## Changes

### New Text Providers

**Google Gemini Provider** (`src/questfoundry/providers/text/gemini.py`)
- Supports latest Gemini models including gemini-2.0-flash-exp
- Configurable temperature, top_p, top_k parameters
- API key from config or GOOGLE_AI_API_KEY env var
- 17 unit tests covering all functionality

**Amazon Bedrock Provider** (`src/questfoundry/providers/text/bedrock.py`)
- Access to Claude and other foundation models via AWS Bedrock
- Supports both Claude (Messages API) and generic model formats
- AWS credentials from config or standard AWS env vars
- Configurable region with default us-east-1
- 18 unit tests covering Claude and generic models

### New Image Providers

**Google Imagen 4 Provider** (`src/questfoundry/providers/image/imagen.py`)
- State-of-the-art image generation via Google Cloud Vertex AI
- Configurable aspect ratios (1:1, 16:9, 9:16, etc.)
- Safety filter levels (BLOCK_SOME, BLOCK_MOST, etc.)
- Automatic aspect ratio detection from width/height
- 17 unit tests covering all scenarios

### End-to-End Integration Tests

**Manual E2E Test Suite** (`tests/integration/test_providers_e2e.py`)
- Tests for all providers with real API calls
- Automatically skips when API keys not available (perfect for CI)
- Cross-provider consistency tests
- Clear documentation on running manually with API keys
- 8 tests (2 pass without keys, 6 skip when keys missing)

### Testing Coverage

**Unit Tests:**
- Gemini: 17 tests (initialization, generation, streaming stub, validation, error handling)
- Bedrock: 18 tests (Claude + generic models, AWS auth, configuration)
- Imagen: 17 tests (generation, aspect ratios, base64/PIL handling, validation)
- Total: 52 new provider-specific tests

**Integration Tests:**
- OpenAI E2E (skips without key)
- Gemini E2E (skips without key)
- Bedrock E2E (skips without AWS creds)
- Imagen E2E (skips without Google Cloud creds)
- ElevenLabs E2E (skips without key)
- Mock Audio E2E (always runs)
- Cross-provider comparison tests

All tests follow the same mocking patterns using sys.modules for optional dependencies.

## Quality Gates

✅ **Tests**: 664 passed, 10 skipped
✅ **Mypy**: Clean (minor unused type: ignore warnings in validate_config methods)
✅ **Ruff**: Clean with auto-formatted imports

## Key Features

1. **Consistent Interface**: All new providers implement the standard Provider base class methods (validate_config, generate_text/image, close)

2. **Flexible Configuration**: API keys and credentials can come from config dict or environment variables

3. **Error Handling**: Comprehensive error messages for missing libraries, invalid configs, and API failures

4. **Model Parameter Support**: All text providers support the standard `model` parameter for runtime model selection

5. **Type Safety**: Full type hints and mypy compatibility

6. **Manual E2E Testing**: Integration tests skip in CI but provide manual validation path

## Architecture Decisions

### Provider Signatures

Updated all new providers to match the base class signatures:
- `generate_text(prompt, model=None, max_tokens=None, temperature=None, **kwargs)`
- `generate_text_streaming(...)` - NotImplementedError stubs for future work
- `validate_config() -> None` - raises ValueError on invalid config
- `generate_image(prompt, model=None, width=None, height=None, **kwargs)`

### Library Import Strategy

All optional provider dependencies use try/except ImportError patterns:
```python
try:
    import boto3  # type: ignore
except ImportError:
    raise RuntimeError("boto3 library required...")
```

This allows QuestFoundry to remain lightweight while supporting many providers.

### E2E Test Design

Integration tests use `pytest.mark.skipif` with environment variable checks:
```python
@pytest.mark.skipif(
    not GOOGLE_AI_API_KEY,
    reason="GOOGLE_AI_API_KEY not set. Set it to run this E2E test manually."
)
def test_gemini_provider_e2e():
    ...
```

This ensures CI passes without API keys while enabling manual validation.

## Dependencies

### Required (Already in pyproject.toml)
- pydantic>=2.0
- httpx>=0.25
- requests (for ElevenLabs)

### Optional (User Installs as Needed)
- `google-generativeai` - for Gemini provider
- `boto3` - for Bedrock provider
- `google-cloud-aiplatform` - for Imagen provider

## Migration Notes

No breaking changes. All new functionality is additive.

Users can start using new providers immediately:

```python
# Google Gemini
from questfoundry.providers.text.gemini import GeminiProvider
provider = GeminiProvider({"api_key": "your-key"})
text = provider.generate_text("Hello, world!")

# Amazon Bedrock
from questfoundry.providers.text.bedrock import BedrockProvider
provider = BedrockProvider({
    "aws_access_key_id": "key",
    "aws_secret_access_key": "secret",
    "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"
})
text = provider.generate_text("Hello, world!")

# Google Imagen
from questfoundry.providers.image.imagen import ImagenProvider
provider = ImagenProvider({
    "project_id": "my-project",
    "api_key": "key"
})
image_bytes = provider.generate_image("A red circle")
```

## Future Enhancements

Potential follow-up work:
1. Implement streaming support for Gemini and Bedrock
2. Add more Imagen 4 features (negative prompts, style presets)
3. Support for additional Bedrock models beyond Claude
4. Batch generation support for Imagen
5. Cost tracking and usage monitoring

## Files Changed

**New Files:**
- `src/questfoundry/providers/text/gemini.py` (167 lines)
- `src/questfoundry/providers/text/bedrock.py` (215 lines)
- `src/questfoundry/providers/image/imagen.py` (183 lines)
- `tests/providers/text/test_gemini.py` (244 lines)
- `tests/providers/text/test_bedrock.py` (313 lines)
- `tests/providers/image/test_imagen.py` (364 lines)
- `tests/integration/test_providers_e2e.py` (285 lines)
- `tests/integration/__init__.py` (1 line)

**Total:** 1,816 lines added across 8 new files

## Related Issues

Part of QuestFoundry completion plan Epic 14: Additional Provider Support

## Checklist

- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Comments added for complex logic
- [x] Documentation updated (inline docstrings)
- [x] Tests added and passing (664 total, 52 new provider tests)
- [x] No breaking changes
- [x] Type hints complete
- [x] Conventional commits used
