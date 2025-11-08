# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- Epic 15: Advanced Features & Polish
  - Response caching layer with file-based storage
  - Rate limiting with three-layer system (requests, tokens, cost)
  - Per-role provider configuration
  - Advanced state management with bidirectional migrations
  - Cost tracking and budget enforcement

### Changed
- Improved configuration merging for nested settings
- Cache default changed to opt-in (disabled by default)

### Fixed
- Configuration deep merging preserves nested dictionaries
- Side effects in cache key generation

## [0.1.0] - 2024-11-08

### Added
- Initial release with core QuestFoundry features
- Workspace management (hot/cold storage)
- State management with snapshots
- Provider system (text, image, audio)
- Role-based narrative processing
- 15+ specialized loops for workflow automation
- Artifact lifecycle management
- Validation framework
- Response caching
- Rate limiting and cost tracking
- Per-role provider configuration
- Bidirectional state migrations

### Features
- Support for multiple AI providers (OpenAI, Gemini, Bedrock, Ollama, etc.)
- Comprehensive test coverage (824+ tests)
- Full type safety with mypy
- Clean code quality with ruff
- Extensive documentation

---

This changelog will be automatically updated with each release.
