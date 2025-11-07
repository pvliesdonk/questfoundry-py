# QuestFoundry-Py Architecture

This document describes the architecture and design decisions of the QuestFoundry Python library (Layer 6).

## Overview

QuestFoundry-Py implements Layer 6 of the QuestFoundry system, providing a Python SDK for creating interactive narratives with LLM-powered agents. The library sits between the specification (Layers 3-5) and user interfaces (Layer 7).

## Layer Architecture

```
┌─────────────────────────────────────────────────┐
│ Layer 7: UI (CLI, Web, MCP)                     │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ Layer 6: Python Library (questfoundry-py)       │
│  ┌──────────────────────────────────────────┐  │
│  │ State Management                          │  │
│  │  - Hot Workspace (Files)                  │  │
│  │  - Cold Storage (SQLite)                  │  │
│  │  - WorkspaceManager (Unified API)         │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ Protocol Client                           │  │
│  │  - Envelope Building                      │  │
│  │  - Message Passing                        │  │
│  │  - Conformance Validation                 │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ Provider System                           │  │
│  │  - Text (OpenAI, Ollama)                  │  │
│  │  - Image (DALL-E, A1111)                  │  │
│  │  - Pluggable Architecture                 │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ Role System                               │  │
│  │  - 14+ Specialized Roles                  │  │
│  │  - Prompt Loading                         │  │
│  │  - Context Management                     │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ Loop Orchestration                        │  │
│  │  - Multi-step Workflows                   │  │
│  │  - Role Coordination                      │  │
│  │  - Step Management                        │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ Validation & Safety                       │  │
│  │  - 8 Quality Bars                         │  │
│  │  - Gatekeeper System                      │  │
│  │  - PN Boundary Enforcement                │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ Export & Views                            │  │
│  │  - View Generation                        │  │
│  │  - Git Export (YAML)                      │  │
│  │  - Book Binding (HTML/MD)                 │  │
│  └──────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ Layers 3-5: Specification                       │
│  - JSON Schemas (17 artifact types)             │
│  - Protocol Definition (envelopes)              │
│  - Role Prompts (bundled in library)            │
└─────────────────────────────────────────────────┘
```

## Core Systems

### 1. State Management

**Purpose**: Manage artifact storage with hot/cold workflow

**Components**:
- **StateStore** (abstract): Interface for storage backends
- **FileStore**: File-based hot workspace storage
- **SQLiteStore**: SQLite-based cold storage
- **WorkspaceManager**: Unified interface for both stores

**Design Pattern**: Dual-storage with hot→cold promotion

```python
# Hot: Work-in-progress
.questfoundry/
  hot/
    hooks/HOOK-001.json
    canon/CANON-001.json
    tus/TU-001.json

# Cold: Curated content
project.qfproj (SQLite database)
  - snapshots
  - artifacts
  - tus
  - history
```

**Key Design Decisions**:
- Hot is file-based for easy human inspection and Git integration
- Cold is SQLite for ACID compliance and efficient querying
- Promotion is explicit (not automatic) to maintain quality
- WorkspaceManager provides consistent API for both stores

### 2. Protocol Client

**Purpose**: Implement Layer 4 protocol for agent communication

**Components**:
- **Envelope**: Pydantic model for protocol messages
- **EnvelopeBuilder**: Fluent builder for creating envelopes
- **ProtocolClient**: High-level API for send/receive
- **Transport**: Abstract transport layer (file-based, HTTP, etc.)
- **Conformance Validator**: Protocol specification compliance

**Design Pattern**: Message passing with envelope wrapping

```python
envelope = {
    "protocol": {"name": "qf-protocol", "version": "1.0.0"},
    "id": "urn:uuid:...",
    "sender": {"role": "SR"},
    "receiver": {"role": "GK"},
    "intent": "hook.validate",
    "context": {"hot_cold": "hot", "tu": "TU-001"},
    "safety": {"player_safe": true, "spoilers": "forbidden"},
    "payload": {"type": "hook_card", "data": {...}}
}
```

**Key Design Decisions**:
- Immutable envelope models (frozen Pydantic)
- Validation at send/receive boundaries
- Support for request/response patterns (correlation_id)
- Subscription-based event handling

### 3. Provider System

**Purpose**: Integrate with external AI services (LLMs, image generation)

**Components**:
- **Provider** (abstract): Base for all providers
- **TextProvider**: Text generation interface
- **ImageProvider**: Image generation interface
- **ProviderConfig**: YAML configuration with env var substitution
- **ProviderRegistry**: Discovery and instantiation

**Design Pattern**: Plugin architecture with registry

**Key Design Decisions**:
- Abstract interfaces for provider types
- Configuration-driven provider selection
- Environment variable substitution for secrets
- Cached provider instances for reuse
- Optional dependencies (don't require all providers installed)

### 4. Role System

**Purpose**: Specialized agents with domain expertise

**Components**:
- **Role** (abstract): Base class for all roles
- **RoleContext**: Input context for role execution
- **RoleResult**: Output from role execution
- **RoleRegistry**: Discovery and instantiation
- **Prompt Loader**: Load role prompts from spec

**Design Pattern**: Template Method with prompt-driven behavior

**Available Roles**:
- **Orchestration**: Showrunner, Gatekeeper
- **Content**: Lore Weaver, Scene Smith, Plotwright, Codex Curator
- **Style**: Style Lead
- **Assets**: Art Director, Illustrator, Audio Director, Audio Producer
- **Support**: Player Narrator, Book Binder, Researcher, Translator

**Key Design Decisions**:
- Roles load prompts from bundled spec resources
- Each role has domain-specific expertise
- Roles are stateless (context passed explicitly)
- Provider can be overridden per-role

### 5. Loop Orchestration

**Purpose**: Coordinate multiple roles in multi-step workflows

**Components**:
- **Loop** (abstract): Base class for all loops
- **LoopContext**: Execution context with workspace and roles
- **LoopResult**: Output from loop execution
- **LoopStep**: Individual step with RACI roles
- **LoopRegistry**: Discovery and instantiation

**Design Pattern**: Workflow coordination with explicit steps

**Example Loop (Story Spark)**:
1. Showrunner creates TU brief
2. Lore Weaver generates initial hooks
3. Gatekeeper validates hooks
4. Repeat or refine based on validation

**Key Design Decisions**:
- Loops coordinate roles but don't call them directly
- Each step has clear RACI (Responsible, Accountable, Consulted, Informed)
- Steps can be validated before proceeding
- Loop state is tracked for checkpointing

### 6. Validation & Safety

**Purpose**: Enforce quality standards and safety boundaries

**Components**:
- **QualityBar** (abstract): Base for all quality bars
- **8 Quality Bars**: Integrity, Reachability, Style, Gateways, Nonlinearity, Determinism, Presentation, Spoiler Hygiene
- **Gatekeeper**: Orchestrates quality bar execution
- **GatecheckReport**: Validation results with blockers/warnings

**Design Pattern**: Strategy pattern for validation rules

**Quality Bar Framework**:
```python
class QualityBar(ABC):
    @property
    def name() -> str: ...
    @property
    def description() -> str: ...
    def validate(artifacts) -> QualityBarResult: ...
```

**Key Design Decisions**:
- Each bar is independent and focused
- Blockers prevent promotion, warnings advise review
- Strict mode treats warnings as blockers
- Reports are stored as artifacts for audit trail
- PN (Player Narrator) boundaries enforced at multiple layers

### 7. Export & Views

**Purpose**: Generate player-facing content and export formats

**Components**:
- **ViewGenerator**: Create player-safe artifact views
- **GitExporter**: Export to version-controllable YAML
- **BookBinder**: Render to HTML and Markdown
- **ViewArtifact**: Filtered collection of player-safe content

**Design Pattern**: Pipeline with filters and transformers

**Export Pipeline**:
```
Snapshot → View (filter player-safe) → Render (HTML/MD)
       ↓
    Git Export (YAML)
```

**Key Design Decisions**:
- Views filter by player_safe flag
- Git export is human-readable YAML for version control
- Book binder supports custom templates
- Exports are immutable (don't modify originals)

## Data Flow

### Typical Workflow

```
1. Draft Content (Hot Workspace)
   └─> Author creates artifacts
   └─> Save to hot with temperature="hot"

2. Validate (Quality Gates)
   └─> Gatekeeper runs 8 quality bars
   └─> Generate gatecheck report
   └─> Block on failures, warn on issues

3. Promote (Hot → Cold)
   └─> If validation passes
   └─> Copy to cold storage
   └─> Optionally delete from hot

4. Snapshot (Cold Storage)
   └─> Create snapshot at milestones
   └─> Link artifacts to snapshot
   └─> Track TU (Thematic Unit)

5. View Generation (Export)
   └─> Filter player-safe artifacts
   └─> Create view artifact
   └─> Save view for repeatability

6. Export (Multiple Formats)
   └─> Git: YAML for version control
   └─> HTML: Rich formatting for players
   └─> Markdown: Plain text alternative
```

### Message Flow (Protocol)

```
Role A                    Protocol Client              Role B
  │                             │                        │
  ├─ create envelope ──────────>│                        │
  │                             ├─ validate ────────────>│
  │                             ├─ send ────────────────>│
  │                             │                        ├─ receive
  │                             │                        ├─ process
  │                             │<─────────── response ──┤
  │<─────────── response ───────┤                        │
```

## Key Design Principles

### 1. Progressive Disclosure
Start simple, reveal complexity as needed:
- Basic: `ws.save_hot_artifact(artifact)`
- Advanced: Custom validation rules, per-role providers

### 2. Separation of Concerns
Each module has a single, well-defined responsibility:
- State: Storage and retrieval
- Protocol: Communication
- Providers: AI services
- Validation: Quality assurance

### 3. Dependency Injection
Dependencies are provided explicitly, not created internally:
```python
# Good
role = SomeRole(provider=text_provider)

# Bad
role = SomeRole()  # Creates provider internally
```

### 4. Immutability Where Possible
Protocol envelopes, validation results use frozen models:
```python
class Envelope(BaseModel):
    model_config = ConfigDict(frozen=True)
```

### 5. Explicit Over Implicit
Make workflows explicit rather than magical:
```python
# Good - explicit promotion
ws.promote_to_cold(artifact_id)

# Bad - automatic promotion
ws.save_artifact(artifact)  # Promotes automatically?
```

### 6. Fail Fast
Validate early and provide clear error messages:
```python
if not artifact.metadata.get("player_safe"):
    raise ValueError("Cannot create view: artifact not player-safe")
```

## Performance Considerations

### 1. Database Connections
- WorkspaceManager uses connection pooling
- Always use context managers to ensure cleanup:
  ```python
  with WorkspaceManager("./project") as ws:
      # Use workspace
  ```

### 2. Batch Operations
- Use `get_artifacts_by_ids()` instead of multiple `get_artifact()` calls
- SQLiteStore supports batch queries

### 3. Provider Caching
- Provider instances are cached in registry
- Reuse instances across multiple calls

### 4. Prompt Loading
- Prompts are loaded once and cached
- No repeated file I/O for same prompt

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock dependencies (providers, storage)
- 374 tests covering all modules

### Integration Tests
- Test component interactions
- Use temporary workspaces
- Validate protocol conformance

### End-to-End Tests
- Complete workflows from creation to export
- Validate quality gates
- Test multi-role collaboration

## Future Enhancements

See [completion-plan.md](./.claude/completion-plan.md) for planned features:
- Additional loop implementations (Hook Harvest, Canon Expansion, etc.)
- Session management for conversation history
- Interactive mode with ask_human callbacks
- Additional providers (audio, Gemini, Bedrock)
- Performance optimizations (caching, rate limiting)

## Related Documentation

- [Getting Started](./docs/guides/getting-started.md)
- [API Reference](./docs/api/)
- [Gap Analysis](./.claude/gap-analysis.md)
- [Completion Plan](./.claude/completion-plan.md)
- [Specification](https://github.com/pvliesdonk/questfoundry-spec)
