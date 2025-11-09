## v0.2.0 (2025-11-09)

### Feat

- **epic-16**: implement documentation, versioning, and release pipeline
- **state-management**: implement advanced state management for Epic 15 Phase 4
- **per-role-config**: implement per-role provider configuration for Epic 15
- **rate-limiter**: implement rate limiting and cost tracking
- **cache**: implement response caching layer
- add Gemini, Bedrock, and Imagen providers with E2E tests (Epic 14)
- **providers**: implement audio provider base class and implementations
- **roles**: integrate session and human callback with Role base class
- **roles**: implement Agent-to-Human callback mechanism
- **roles**: implement SessionManager for managing multiple sessions
- **roles**: implement RoleSession class for conversation history
- implement all 13 remaining loops for Epic 12
- **export**: Epic 10 - Export & Views implementation
- Epic 9 - Safety & Quality validation system
- **orchestration**: implement Showrunner role and Orchestrator (Epic 7 Phase 4)
- **loops**: implement Story Spark loop with comprehensive tests (Epic 7 Phase 3)
- **loops**: implement loop registry and base classes (Epic 7 Phase 2)
- **roles**: implement role system foundation (Epic 7 Phase 1)
- **providers**: add image generation providers (Epic 6 Phase 2)
- **providers**: implement provider system foundation (Epic 6 Phase 1)
- **protocol**: implement Protocol Client for agent communication
- **protocol**: implement file-based transport for message passing
- Epic 4 - Artifact Types & Lifecycles
- **state**: implement unified workspace manager
- **state**: implement file-based hot workspace store
- **state**: implement SQLite project file store
- **state**: add state store interface and types
- **protocol**: add protocol conformance validation
- **protocol**: add Layer 4 protocol envelope models
- **validators**: add enhanced schema validation with detailed error reporting
- implement schema and prompt bundling at build time
- update development tools and fix type checking
- improve package structure and metadata
- add MIT license and fix CI/CD workflows
- add Epic 1 - Project Foundation for questfoundry-py
- add questfoundry-spec as submodule

### Fix

- use RELEASE_PAT for pushing to protected branch instead of GITHUB_TOKEN
- add GITHUB_TOKEN authentication for pushing to protected branch
- move mkdocs.yml to repository root and simplify build command
- add --yes flag to commitizen bump for non-interactive environments
- correct workflow issues and release guide
- move mkdocs.yml to repository root and simplify build command
- add --yes flag to commitizen bump for non-interactive environments
- correct workflow issues and release guide
- use proper uv commands without pip-isms
- **epic-16**: address PR feedback on documentation and configuration
- address ruff lint issues in test files
- **providers,roles,state**: address PR #18 feedback for Epic 15
- address all PR #16 review comments
- resolve ruff linting errors in Epic 13
- resolve all ruff line length violations
- address all PR #15 review comments
- configure mypy to work properly with Pydantic models
- resolve mypy type errors in style.py
- correct artifact attribute references and test fixtures
- address PR feedback - code quality and correctness issues
- resolve mypy type errors in new code
- address critical and high-severity PR review issues
- address PR #7 review comments
- address mypy type checking errors in provider system
- address PR #6 review comments
- address PR #5 review comments and mypy errors
- address PR #4 review comments
- add type annotations for mypy compliance
- address PR review comments for Epic 3
- **protocol**: add type narrowing assertions for EnvelopeBuilder
- remove unused type: ignore comment in artifact.py
- Update scripts/bundle_resources.py
- pyproject.toml versioning

### Refactor

- address PR #17 review comments
- **export**: address PR #12 review feedback
- address medium-priority PR review feedback
- move import re to module top per PEP 8
- address PR review comments
