# Installation

Complete installation instructions for QuestFoundry-Py across different environments and use cases.

## Requirements

- **Python**: 3.11 or higher
- **Package Manager**: pip, uv, or poetry
- **Optional**: Git for development installation

## Standard Installation

### Using pip

The simplest way to install QuestFoundry-Py:

```bash
pip install questfoundry-py
```

### Using uv

For faster installation with uv:

```bash
uv pip install questfoundry-py
```

### Using poetry

If you're using poetry for dependency management:

```bash
poetry add questfoundry-py
```

## Installation with Extras

### Documentation Extra

Install with documentation building tools:

```bash
pip install questfoundry-py[docs]
```

This includes:
- mkdocs
- mkdocs-material
- mkdocstrings[python]
- pymdown-extensions

### Development Extra

For development and testing:

```bash
pip install questfoundry-py[dev]
```

This includes:
- pytest
- pytest-cov
- ruff
- mypy
- pre-commit

### All Extras

Install everything:

```bash
pip install questfoundry-py[dev,docs]
```

## Development Installation

### From Source

Clone and install in development mode:

```bash
git clone https://github.com/pvliesdonk/questfoundry-py.git
cd questfoundry-py
pip install -e ".[dev,docs]"
```

### With uv

If using uv for faster dependency resolution:

```bash
git clone https://github.com/pvliesdonk/questfoundry-py.git
cd questfoundry-py
uv sync --all-extras
```

### Running Tests

Verify the installation:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## Provider Setup

Different AI providers require specific setup steps.

### OpenAI

1. Get your API key from [platform.openai.com](https://platform.openai.com/api-keys)
2. Set environment variable:

```bash
export OPENAI_API_KEY="sk-..."
```

3. Or configure in `.questfoundry/config.yml`:

```yaml
providers:
  text:
    openai:
      api_key: "sk-..."
```

### Google Gemini

1. Get API key from [makersuite.google.com](https://makersuite.google.com/app/apikey)
2. Install provider:

```bash
pip install google-generativeai
```

3. Configure:

```yaml
providers:
  text:
    gemini:
      api_key: ${GOOGLE_AI_API_KEY}
```

### Amazon Bedrock

1. Configure AWS credentials (see AWS CLI docs)
2. Install provider:

```bash
pip install boto3
```

3. Configure:

```yaml
providers:
  text:
    bedrock:
      aws_region: us-east-1
```

### Local Models with Ollama

1. Install [Ollama](https://ollama.ai)
2. Run a model:

```bash
ollama run llama2
```

3. Configure:

```yaml
providers:
  text:
    ollama:
      base_url: http://localhost:11434
      model: llama2
```

### Image Providers

#### DALL-E 3

```bash
pip install openai
```

```yaml
providers:
  image:
    dalle:
      api_key: ${OPENAI_API_KEY}
```

#### Imagen

```bash
pip install google-cloud-aiplatform
```

```yaml
providers:
  image:
    imagen:
      project_id: your-project
      api_key: ${GOOGLE_CLOUD_API_KEY}
```

#### Stable Diffusion (A1111)

```yaml
providers:
  image:
    a1111:
      base_url: http://localhost:7860
```

### Audio Providers

#### ElevenLabs

```bash
pip install elevenlabs
```

```yaml
providers:
  audio:
    elevenlabs:
      api_key: ${ELEVENLABS_API_KEY}
```

## Verification

After installation, verify everything works:

```python
from questfoundry import __version__
print(f"QuestFoundry version: {__version__}")

from questfoundry.providers.text.openai import OpenAIProvider
print("OpenAI provider available")

from questfoundry.state.workspace import WorkspaceManager
print("Workspace manager available")

print("\n✅ Installation verified!")
```

Save as `verify.py` and run:

```bash
python verify.py
```

## Troubleshooting

### ImportError: No module named 'questfoundry'

The package wasn't installed. Try:

```bash
pip install --upgrade questfoundry-py
```

### ModuleNotFoundError: No module named 'google.generativeai'

You need the optional dependency for Gemini:

```bash
pip install google-generativeai
```

### OPENAI_API_KEY not found

Set the environment variable:

```bash
export OPENAI_API_KEY="sk-..."
```

Or configure it in your config file instead.

### Version conflicts

Try creating a fresh virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install questfoundry-py
```

### Still having issues?

Check our [troubleshooting guide](guides/deployment.md#troubleshooting) or open an [issue on GitHub](https://github.com/pvliesdonk/questfoundry-py/issues).

## Next Steps

- **[Getting Started Guide](getting-started.md)** - Create your first project
- **[Configuration Guide](guides/configuration.md)** - Set up providers and roles
- **[API Reference](api/index.md)** - Explore the full API

Happy creating! 🎭
