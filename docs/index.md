# QuestFoundry-Py

A powerful Python framework for creating and managing interactive narrative projects with AI integration. QuestFoundry enables you to build complex, multi-character story systems with state management, role-based processing, and sophisticated workflow orchestration.

## Key Features

🎭 **Multi-Role System**
- Dedicated roles for different aspects of storytelling (Gatekeeper, Plotwright, Scene Smith, etc.)
- Role-specific provider configuration for cost optimization
- Flexible role-aware provider selection

🔄 **Advanced Workflows**
- 15+ specialized loops for different narrative tasks
- Composable workflow orchestration
- Hot and cold artifact storage
- Snapshot-based state management

💾 **Intelligent Caching**
- Transparent response caching for API calls
- Configurable per-provider or global settings
- Automatic TTL and cleanup

⚡ **Rate Limiting & Cost Control**
- Three-layer rate limiting (requests, tokens, cost)
- Real-time cost tracking by provider
- Per-provider pricing models
- Budget enforcement

🔐 **State Management**
- Bidirectional state migrations
- Atomic backup and restore
- Project, Thematic Unit, and Snapshot tracking
- Export/import for sharing and archival

📊 **Validation Framework**
- Schema validation for artifacts
- Lifecycle hooks for state transitions
- Custom validation rules

## Quick Start

### Installation

```bash
pip install questfoundry-py
```

### Basic Usage

```python
from questfoundry.state.workspace import WorkspaceManager
from questfoundry.providers.text.openai import OpenAIProvider
from questfoundry.orchestrator import Orchestrator

# Initialize workspace
workspace = WorkspaceManager("./my_project")
workspace.init_workspace(name="My Story Project")

# Configure provider
provider_config = {
    "api_key": "your-api-key",
    "model": "gpt-4o"
}

# Create orchestrator
orchestrator = Orchestrator(workspace)

# Run a story spark loop
result = orchestrator.execute_loop(
    "story_spark",
    {"prompt": "A mysterious library appears..."}
)

print(f"Story spark completed: {result.success}")
```

## Core Concepts

### Workspaces
Projects are organized into workspaces with hot (active) and cold (archived) storage. Snapshots capture state at key points.

### Roles
Specialized actors that process narrative content:
- **Plotwright**: Plans overall story structure
- **Gatekeeper**: Validates narrative quality and consistency
- **Scene Smith**: Creates detailed scenes and descriptions
- **Illustrator**: Generates images for scenes
- **And many more...**

### Loops
Composable workflows that orchestrate roles:
- **Story Spark**: Initial story concept generation
- **Hook Generation**: Create engaging story hooks
- **Scene Forge**: Generate detailed scenes
- **And 12+ more specialized loops**

### State Management
Track your project with:
- **ProjectInfo**: Metadata and configuration
- **TUState**: Thematic units (story segments)
- **SnapshotInfo**: Snapshots of project state

## Documentation

- **[Getting Started](getting-started.md)** - Step-by-step tutorial
- **[Installation](installation.md)** - Installation options and setup
- **[API Reference](api/index.md)** - Complete API documentation
- **[Guides](guides/configuration.md)** - How-to guides and best practices
- **[Examples](examples/code-examples.md)** - Code examples and templates

## Architecture Highlights

### Provider System
- **Text Providers**: OpenAI, Gemini, Bedrock, Ollama
- **Image Providers**: DALL-E, Imagen, A1111, Mock
- **Audio Providers**: ElevenLabs, Mock
- Pluggable architecture for custom providers

### Configuration
```yaml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
      cache:
        enabled: true
      rate_limit:
        requests_per_minute: 60

roles:
  gatekeeper:
    provider: openai
    model: gpt-4o
```

### Performance Features
- **Caching**: Eliminates redundant API calls
- **Rate Limiting**: Prevents API throttling
- **Cost Tracking**: Real-time budget monitoring
- **Connection Pooling**: Efficient resource usage

## Quality Metrics

- ✅ **824+ Tests**: Comprehensive test coverage
- ✅ **Type Safety**: Full mypy compliance
- ✅ **Code Quality**: Clean ruff linting
- ✅ **Documentation**: 100+ pages of docs

## Community

- 📧 **Issues**: [GitHub Issues](https://github.com/pvliesdonk/questfoundry-py/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/pvliesdonk/questfoundry-py/discussions)
- 🐦 **Updates**: Follow for latest news

## License

MIT License - See LICENSE file for details

---

**Ready to build your next interactive narrative?** Start with the [Getting Started guide](getting-started.md)!
