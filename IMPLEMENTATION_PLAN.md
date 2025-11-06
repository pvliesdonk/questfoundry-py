# QuestFoundry-Py Implementation Plan

**Version:** 2.0 (Revised Epic 7/8)
**Last Updated:** 2025-11-06
**Target:** Python 3.11+ with UV package manager

## Overview

This document outlines the implementation roadmap for `questfoundry-py`, the Python reference implementation of the QuestFoundry framework. The project is organized into 11 sequential epics spanning foundation, infrastructure, intelligence, quality, and distribution.

### Current Status

✅ **Completed:**
- Epic 1: Project Foundation
- Epic 2: Schema & Validation Integration
- Epic 3: State Management
- Epic 4: Lifecycle State Machines
- Epic 5: Protocol Client
- Epic 6: Provider System

🔄 **In Progress:**
- Epic 7-8: Intelligence Layer (Next)

⏳ **Remaining:**
- Epic 9: Safety & Quality Systems
- Epic 10: Export & Publishing
- Epic 11: Distribution & Documentation

---

## Architecture Overview

### Core Design Principles

1. **Hybrid Architecture**: Hardcoded structure with LLM intelligence
2. **Two-Tier Context**: Registry for selection + Active context for execution
3. **Provider Abstraction**: Multiple LLM/image backends supported
4. **Dual Persistence**: SQLite (.qfproj) + file-based (hot workspace)
5. **Protocol Conformance**: Layer 4 message envelope support

### Key Components

```
questfoundry/
├── models/          # Artifact definitions (Layer 3)
├── validation/      # JSON Schema validation
├── lifecycles/      # State machines (Hook, TU)
├── state/           # Persistence (SQLite, File)
├── protocol/        # Message envelopes & transport
├── providers/       # LLM & image generation
├── roles/           # Agent role implementations
└── loops/           # Orchestration workflows
```

---

## Epic 7-8: Intelligence Layer (REVISED)

**Duration:** 3-4 weeks
**Status:** Not Started

### Architecture Decision

This epic implements a **hybrid architecture** combining hardcoded structure with LLM intelligence, dramatically reducing context usage while maintaining flexibility.

#### Key Principles

1. **Hardcoded Loops**: Python classes define workflow structure, not runtime playbook parsing
2. **LLM Agents**: Role-based agents provide domain expertise via providers
3. **Two-Tier Context**: Registry (~90 lines) + Active Loop (~500 lines) = 97% reduction
4. **Showrunner Orchestration**: Strategic decisions on role assignment and collaboration
5. **Iterative Refinement**: Loops stabilize through cycles, not linear execution

### Phase 1: Role System (Week 12)

**Goal:** Implement role agents that load prompts and execute via LLM providers

#### Deliverables

**`src/questfoundry/roles/base.py`**
```python
class Role(ABC):
    """Base class for all role agents."""

    def __init__(self, provider: TextProvider, config: dict[str, Any]):
        self.provider = provider
        self.config = config
        self.role_name: str  # e.g., "plotwright"
        self.prompt_template: str  # Loaded from spec/01-roles/

    @abstractmethod
    def execute_task(
        self,
        task: str,
        context: dict[str, Any],
        artifacts: list[Artifact]
    ) -> str:
        """Execute a role-specific task with context."""
        pass

    def load_prompt(self, task_type: str) -> str:
        """Load prompt template for specific task type."""
        pass

    def format_context(self, artifacts: list[Artifact]) -> str:
        """Format artifacts into context for LLM."""
        pass
```

**`src/questfoundry/roles/registry.py`**
```python
class RoleRegistry:
    """Registry of available role agents."""

    def __init__(self, provider_registry: ProviderRegistry):
        self._roles: dict[str, type[Role]] = {}
        self.provider_registry = provider_registry

    def register_role(self, name: str, role_class: type[Role]) -> None:
        """Register a role implementation."""

    def get_role(self, name: str) -> Role:
        """Get role instance with configured provider."""

    def list_roles(self) -> list[str]:
        """List all registered roles."""
```

**Role Implementations** (11 roles from spec/01-roles/briefs/):
- `plotwright.py` - Story structure & narrative arc
- `scene_smith.py` - Individual scene content
- `gatekeeper.py` - Quality validation
- `lore_weaver.py` - World-building & consistency
- `codex_curator.py` - Lore documentation
- `style_lead.py` - Writing style & voice
- `illustrator.py` - Image generation
- `art_director.py` - Visual direction
- `translator.py` - Localization
- `audio_producer.py` - Audio content
- `showrunner.py` - Orchestration (special role)

**Prompt Loading Strategy:**
- Load from `spec/01-roles/briefs/{role_name}.md`
- Parse markdown to extract system prompt and task-specific sections
- Support variable substitution: `{project_name}`, `{context}`, etc.
- Cache loaded prompts to reduce I/O

**Tests:**
- Role registration and retrieval
- Prompt loading from spec directory
- Context formatting with artifacts
- Mock LLM execution for each role
- Role-specific validation logic

### Phase 2: Loop Registry (Week 13)

**Goal:** Lightweight registry for loop selection without full context

#### Deliverables

**`src/questfoundry/loops/registry.py`**
```python
@dataclass
class LoopMetadata:
    """Lightweight loop description for selection."""
    loop_id: str                    # e.g., "story_spark"
    display_name: str               # "Story Spark"
    description: str                # One-line purpose
    typical_duration: str           # "2-4 hours"
    primary_roles: list[str]        # ["plotwright", "gatekeeper"]
    entry_conditions: list[str]     # When to use this loop
    exit_conditions: list[str]      # When loop completes
    output_artifacts: list[str]     # Expected artifact types

class LoopRegistry:
    """Registry of all available loops (~90 lines total)."""

    def __init__(self):
        self._loops: dict[str, LoopMetadata] = {}
        self._register_builtin_loops()

    def get_loop_metadata(self, loop_id: str) -> LoopMetadata:
        """Get loop metadata for selection."""

    def list_loops(self, filters: dict[str, Any] = None) -> list[LoopMetadata]:
        """List loops matching criteria."""

    def recommend_loop(self, project_state: dict[str, Any]) -> str:
        """Recommend loop based on project state (via Showrunner)."""
```

**Loop Metadata Definitions** (11 loops from spec/00-north-star/LOOPS/):
1. `story_spark` - Initial quest concept to first draft
2. `hook_harvest` - Generate and refine quest hooks
3. `lore_deepening` - Expand world-building
4. `codex_expansion` - Document lore entries
5. `binding_run` - Assemble complete quest package
6. `style_tune_up` - Refine writing style consistency
7. `art_touch_up` - Generate/refine visual assets
8. `audio_pass` - Create audio content
9. `translation_pass` - Localization workflow
10. `narration_dry_run` - Playtest preparation
11. `full_production_run` - Complete end-to-end workflow

**Metadata Source:**
- Extract from `spec/00-north-star/LOOPS/{loop_name}.md`
- Parse structured sections: Purpose, Duration, Roles, Conditions
- Store as dataclass for type safety

**Tests:**
- Loop registration and retrieval
- Metadata loading from spec
- Filtering by role, duration, artifact type
- Recommendation logic (mock Showrunner)

### Phase 3: Loop Implementations (Week 14)

**Goal:** Hardcoded Python classes for each loop's execution flow

#### Deliverables

**`src/questfoundry/loops/base.py`**
```python
class LoopStep(BaseModel):
    """Single step in a loop execution."""
    step_id: str
    description: str
    assigned_roles: list[str]      # RACI: Responsible roles
    consulted_roles: list[str]     # RACI: Consulted roles
    artifacts_input: list[str]     # Required artifact types
    artifacts_output: list[str]    # Produced artifact types
    validation_required: bool = True

class LoopContext:
    """Context for active loop execution (~500 lines)."""
    loop_id: str
    project_id: str
    workspace: "Workspace"
    role_registry: RoleRegistry
    artifacts: list[Artifact]
    current_step: int
    history: list[dict[str, Any]]

class Loop(ABC):
    """Base class for all loop implementations."""

    metadata: LoopMetadata
    steps: list[LoopStep]

    def __init__(self, context: LoopContext):
        self.context = context
        self.current_step = 0

    @abstractmethod
    def execute(self) -> LoopResult:
        """Execute the complete loop."""
        pass

    def execute_step(self, step: LoopStep) -> StepResult:
        """Execute a single step."""
        # 1. Load required artifacts
        # 2. Assign roles (via Showrunner if needed)
        # 3. Execute role tasks
        # 4. Validate outputs
        # 5. Store results
        pass

    def validate_step(self, step: LoopStep, result: StepResult) -> bool:
        """Validate step completion."""
        pass

    def can_continue(self) -> bool:
        """Check if loop can proceed to next step."""
        pass

    def rollback_step(self) -> None:
        """Roll back to previous step if validation fails."""
        pass
```

**Example Loop Implementation:**

**`src/questfoundry/loops/story_spark.py`**
```python
class StorySparkLoop(Loop):
    """
    Story Spark: Initial quest concept to first draft.

    Steps:
    1. Hook Generation (Plotwright)
    2. Scene Outline (Plotwright)
    3. Draft Scenes (Scene Smith)
    4. Initial Review (Gatekeeper)
    5. Refinement Cycle (Plotwright + Scene Smith)
    """

    metadata = LoopMetadata(
        loop_id="story_spark",
        display_name="Story Spark",
        description="Transform initial quest concept into first draft",
        typical_duration="2-4 hours",
        primary_roles=["plotwright", "scene_smith", "gatekeeper"],
        entry_conditions=["No existing TU brief", "Project metadata exists"],
        exit_conditions=["TU brief validated", "All scenes drafted"],
        output_artifacts=["tu_brief", "hook_card", "canon_pack"]
    )

    steps = [
        LoopStep(
            step_id="generate_hooks",
            description="Generate initial quest hooks",
            assigned_roles=["plotwright"],
            consulted_roles=["lore_weaver"],
            artifacts_input=["project_metadata"],
            artifacts_output=["hook_card"],
            validation_required=True
        ),
        LoopStep(
            step_id="create_tu_brief",
            description="Create TU brief with narrative structure",
            assigned_roles=["plotwright"],
            consulted_roles=["gatekeeper"],
            artifacts_input=["hook_card", "project_metadata"],
            artifacts_output=["tu_brief"],
            validation_required=True
        ),
        # ... additional steps
    ]

    def execute(self) -> LoopResult:
        """Execute Story Spark workflow."""
        for step in self.steps:
            result = self.execute_step(step)
            if not self.validate_step(step, result):
                # Showrunner decides: retry, skip, or abort
                action = self.context.showrunner.handle_validation_failure(step, result)
                if action == "retry":
                    self.rollback_step()
                    continue
                elif action == "abort":
                    return LoopResult(success=False, reason="Validation failed")
            self.current_step += 1
        return LoopResult(success=True, artifacts=self.context.artifacts)
```

**Implementation Priority:**
1. `story_spark` - Most common, foundational
2. `hook_harvest` - Dependency of story_spark
3. `binding_run` - Required for export
4. `style_tune_up` - Quality improvement
5. `lore_deepening` + `codex_expansion` - World-building pair
6. Remaining loops as needed

**Tests:**
- Step execution with mock roles
- Validation checkpoints
- Rollback on failure
- Complete loop execution (integration test)
- Context loading and state management

### Phase 4: Showrunner Orchestration (Week 15)

**Goal:** Intelligent orchestration of role collaboration

#### Deliverables

**`src/questfoundry/roles/showrunner.py`**
```python
class Showrunner(Role):
    """
    Meta-role that orchestrates other roles.

    Responsibilities:
    - Select which loop to run
    - Assign roles to specific tasks
    - Decide on collaboration patterns
    - Handle validation failures
    - Manage iteration cycles
    """

    def select_loop(self, project_state: dict[str, Any]) -> str:
        """Select appropriate loop based on project state."""
        # Use LLM with loop registry context
        # Input: Project metadata, existing artifacts, goals
        # Output: Loop ID recommendation
        pass

    def assign_roles(self, step: LoopStep, context: LoopContext) -> dict[str, Role]:
        """Assign specific roles to a step."""
        # Use RACI from step definition
        # Consult LLM for edge cases
        pass

    def coordinate_collaboration(
        self,
        roles: list[Role],
        task: str,
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Coordinate multi-role collaboration."""
        # Sequential: Each role builds on previous
        # Parallel: Roles work independently, merge results
        # Review: One role produces, another approves
        pass

    def handle_validation_failure(
        self,
        step: LoopStep,
        result: StepResult
    ) -> Literal["retry", "skip", "abort", "escalate"]:
        """Decide how to handle validation failure."""
        # Use LLM to analyze failure reason
        # Consider project constraints (time, budget)
        # Recommend action
        pass

    def should_iterate(self, loop: Loop) -> bool:
        """Decide if loop should iterate vs. complete."""
        # Check quality gates
        # Assess artifact completeness
        # Consider iteration budget
        pass
```

**Orchestration Patterns:**

```python
class CollaborationPattern(Enum):
    SEQUENTIAL = "sequential"      # A → B → C
    PARALLEL = "parallel"          # A, B, C → merge
    REVIEW = "review"              # A produces → B approves
    ITERATIVE = "iterative"        # A ⇄ B until satisfied

class Orchestrator:
    """Manages role collaboration patterns."""

    def execute_pattern(
        self,
        pattern: CollaborationPattern,
        roles: list[Role],
        task: str,
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute collaboration pattern."""
        pass
```

**Context Management:**

```python
class ContextManager:
    """Manages two-tier context architecture."""

    def build_registry_context(self) -> str:
        """Build lightweight context for loop selection (~90 lines)."""
        # Loop metadata only
        # Project state summary
        # High-level goals
        pass

    def build_loop_context(self, loop_id: str) -> str:
        """Build detailed context for loop execution (~500 lines)."""
        # Full loop specification
        # Relevant artifacts
        # Role prompts
        # RACI matrix
        # Quality gates
        pass

    def estimate_token_usage(self, context: str) -> int:
        """Estimate token usage for context."""
        pass
```

**Tests:**
- Loop selection with various project states
- Role assignment based on RACI
- Collaboration pattern execution
- Validation failure handling
- Iteration decision logic
- Context size verification (90/500 line targets)

### Epic 7-8 Success Criteria

✅ All 11 roles implemented and tested
✅ Loop registry with all 11 loop metadata entries
✅ At least 3 complete loop implementations (story_spark, hook_harvest, binding_run)
✅ Showrunner orchestration functional
✅ Context usage < 1000 lines per execution (97% reduction achieved)
✅ Integration tests showing end-to-end loop execution
✅ Role collaboration patterns working (sequential, parallel, review)

---

## Epic 9: Safety & Quality Systems

**Duration:** 2-3 weeks
**Status:** Not Started

### Overview

Implement Player-Neutral (PN) safety boundaries and 8-bar quality validation system.

### Phase 1: PN Safety System (Week 16)

**Goal:** Enforce Player-Neutral boundaries to prevent spoilers

#### Deliverables

**`src/questfoundry/safety/pn_filter.py`**
```python
class PNFilter:
    """Filter artifacts to maintain Player-Neutral boundaries."""

    def filter_artifact(self, artifact: Artifact, context: str) -> Artifact:
        """Remove spoilers based on context."""
        # HOT context: Full access
        # COLD context: Remove spoilers, outcomes, solutions
        pass

    def classify_field(self, field: str, value: Any) -> Literal["safe", "spoiler", "conditional"]:
        """Classify field as safe or spoiler."""
        pass

    def strip_spoilers(self, artifact: Artifact) -> Artifact:
        """Create PN-safe version of artifact."""
        pass
```

**PN Validation:**
- Check artifacts before COLD storage
- Validate protocol envelopes (PN receivers)
- Verify snapshot safety markers
- Enforce PN principles from spec/00-north-star/PN_PRINCIPLES.md

**Tests:**
- HOT vs COLD filtering
- Field classification
- Spoiler stripping
- PN validation on protocol messages

### Phase 2: Quality Bar System (Week 17-18)

**Goal:** Implement 8 quality bars from spec/00-north-star/QUALITY_BARS.md

#### Deliverables

**`src/questfoundry/quality/validators.py`**
```python
class QualityValidator(ABC):
    """Base class for quality validators."""

    @abstractmethod
    def validate(self, artifact: Artifact, context: dict[str, Any]) -> ValidationResult:
        """Validate artifact against quality bar."""
        pass

# 8 Validators:
class IntegrityValidator(QualityValidator):
    """QB1: Artifact Integrity - Schema conformance, no missing fields."""

class ReachabilityValidator(QualityValidator):
    """QB2: Reachability - All choices lead somewhere, no dead ends."""

class StyleConsistencyValidator(QualityValidator):
    """QB3: Style Consistency - Tone, voice, formatting match project style."""

class GatewayDesignValidator(QualityValidator):
    """QB4: Gateway Design - Choices are meaningful, not trivial."""

class NonlinearityValidator(QualityValidator):
    """QB5: Nonlinearity - Multiple paths, not forced railroad."""

class DeterminismValidator(QualityValidator):
    """QB6: Determinism - Outcomes follow from choices, not random."""

class PresentationValidator(QualityValidator):
    """QB7: Presentation - Formatting, readability, polish."""

class SpoilerHygieneValidator(QualityValidator):
    """QB8: Spoiler Hygiene - PN safety, no leaks."""
```

**Quality Gate System:**
```python
class QualityGate:
    """Checkpoint that enforces quality bars."""

    def __init__(self, required_bars: list[type[QualityValidator]]):
        self.validators = [bar() for bar in required_bars]

    def check(self, artifact: Artifact) -> GateResult:
        """Run all validators, return pass/fail."""
        results = [v.validate(artifact) for v in self.validators]
        return GateResult(
            passed=all(r.is_valid for r in results),
            failures=[r for r in results if not r.is_valid]
        )
```

**Integration with Loops:**
- Add quality gates to LoopStep validation
- Gatekeeper role enforces quality bars
- Configurable bar requirements per loop
- Failure handling via Showrunner

**Tests:**
- Each validator with valid/invalid artifacts
- Quality gate pass/fail logic
- Integration with loop execution
- Performance testing (gates shouldn't block)

---

## Epic 10: Export & Publishing

**Duration:** 2 weeks
**Status:** Not Started

### Phase 1: Git Export (Week 19)

**Goal:** Export artifacts to git-friendly YAML format

#### Deliverables

**`src/questfoundry/export/git_exporter.py`**
```python
class GitExporter:
    """Export artifacts to YAML files for version control."""

    def export_project(self, workspace: Workspace, output_dir: Path) -> None:
        """Export entire project to directory structure."""
        # .qfproj/
        # ├── metadata.yml
        # ├── tus/
        # │   ├── {tu_id}.yml
        # ├── artifacts/
        # │   ├── hooks/
        # │   ├── canons/
        # │   └── ...
        # └── snapshots/
        pass

    def export_artifact(self, artifact: Artifact, path: Path) -> None:
        """Export single artifact to YAML."""
        pass

    def import_project(self, source_dir: Path, workspace: Workspace) -> None:
        """Import project from YAML files."""
        pass
```

**YAML Format:**
- Human-readable structure
- Preserve all metadata
- Support round-trip (export → import → export)
- Git-friendly diffs

**Tests:**
- Export/import round-trip
- Directory structure validation
- YAML parsing
- Diff-friendly format verification

### Phase 2: Document Export (Week 20)

**Goal:** Generate publication-ready documents

#### Deliverables

**`src/questfoundry/export/document_exporter.py`**
```python
class DocumentExporter:
    """Export to various document formats."""

    def export_markdown(self, workspace: Workspace, output_path: Path) -> None:
        """Export as Markdown document."""
        pass

    def export_pdf(self, workspace: Workspace, output_path: Path) -> None:
        """Export as PDF (requires external renderer)."""
        pass

    def export_epub(self, workspace: Workspace, output_path: Path) -> None:
        """Export as EPUB for e-readers."""
        pass

    def export_json(self, workspace: Workspace, output_path: Path) -> None:
        """Export as structured JSON."""
        pass
```

**Format Support:**
- Markdown (primary)
- JSON (structured data)
- PDF (via pandoc or similar)
- EPUB (via pandoc or similar)

**Tests:**
- Format generation
- Content preservation
- External tool integration
- Error handling

---

## Epic 11: Distribution & Documentation

**Duration:** 1-2 weeks
**Status:** Not Started

### Phase 1: Documentation (Week 21)

**Goal:** Comprehensive API docs and user guides

#### Deliverables

**Documentation Structure:**
```
docs/
├── index.md                    # Overview
├── quickstart.md               # Getting started
├── user-guide/
│   ├── installation.md
│   ├── configuration.md
│   ├── workflows.md
│   └── troubleshooting.md
├── api-reference/
│   ├── models.md
│   ├── validation.md
│   ├── state.md
│   ├── protocol.md
│   ├── providers.md
│   ├── roles.md
│   └── loops.md
└── developer-guide/
    ├── architecture.md
    ├── extending.md
    └── contributing.md
```

**Documentation Tools:**
- Sphinx or MkDocs for generation
- Autodoc from docstrings
- Mermaid diagrams for architecture
- Code examples in all guides

**Tests:**
- Doc generation successful
- All code examples run
- Link validation
- Spelling/grammar checks

### Phase 2: Examples & Templates (Week 22)

**Goal:** Runnable examples and project templates

#### Deliverables

**`examples/`**
```
examples/
├── quickstart/
│   ├── simple_quest.py         # Minimal working example
│   └── README.md
├── advanced/
│   ├── custom_provider.py      # Extending providers
│   ├── custom_role.py          # Adding new roles
│   ├── custom_loop.py          # Custom workflows
│   └── README.md
└── templates/
    ├── fantasy_quest/          # Genre template
    ├── scifi_quest/
    └── mystery_quest/
```

**Example Requirements:**
- Complete, runnable code
- Detailed comments
- README with setup instructions
- Expected output shown

**Tests:**
- All examples run successfully
- Templates instantiate correctly
- Dependencies resolved

### Phase 3: PyPI Distribution (Week 22)

**Goal:** Publish to PyPI for easy installation

#### Deliverables

**Package Configuration:**
- Version numbering (SemVer)
- Dependency specifications
- Entry points for CLI tools
- Package metadata (description, keywords, classifiers)

**Release Process:**
```bash
# Build
uv build

# Test PyPI upload
uv publish --repository testpypi

# Production PyPI upload
uv publish
```

**Installation Verification:**
```bash
pip install questfoundry
python -c "import questfoundry; print(questfoundry.__version__)"
```

**Distribution Checklist:**
- [ ] Version tagged in git
- [ ] CHANGELOG.md updated
- [ ] All tests passing
- [ ] Documentation built
- [ ] PyPI metadata complete
- [ ] Test PyPI upload successful
- [ ] Production PyPI upload
- [ ] GitHub release created
- [ ] Announcement posted

---

## Testing Strategy

### Unit Tests

**Coverage Target:** >80%

**Test Organization:**
```
tests/
├── models/              # Artifact models
├── validation/          # Schema validation
├── lifecycles/          # State machines
├── state/               # Persistence
├── protocol/            # Message protocol
├── providers/           # LLM/image providers
├── roles/               # Role agents
├── loops/               # Loop execution
├── quality/             # Quality validators
└── export/              # Export functionality
```

**Test Tools:**
- pytest for test framework
- pytest-cov for coverage reporting
- pytest-mock for mocking
- pytest-asyncio if needed

### Integration Tests

**Scenarios:**
1. Complete loop execution (story_spark)
2. Multi-loop workflow (story_spark → binding_run)
3. Export/import round-trip
4. Protocol message exchange
5. Quality gate enforcement
6. Provider failover

**Integration Test Requirements:**
- Use temporary directories
- Mock external services (OpenAI, etc.)
- Verify end-to-end data flow
- Check state persistence

### Performance Tests

**Benchmarks:**
- Loop execution time (target: <5 min for story_spark)
- Context building time (target: <1 sec)
- Artifact validation time (target: <100ms per artifact)
- Database query performance (target: <50ms per query)
- Export generation time (target: <30 sec for full project)

**Performance Tools:**
- pytest-benchmark for microbenchmarks
- memory_profiler for memory usage
- Custom timing decorators

### Continuous Integration

**GitHub Actions Workflow:**
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv sync
      - run: uv run pytest --cov
      - run: uv run mypy src
      - run: uv run ruff check src
```

---

## Dependencies

### Core Dependencies

```toml
[project]
dependencies = [
    "pydantic>=2.0",           # Data validation
    "jsonschema>=4.0",         # Schema validation
    "httpx>=0.25",             # HTTP client
    "python-dotenv>=1.0",      # Environment config
    "pyyaml>=6.0",             # YAML parsing
]
```

### Optional Dependencies

```toml
[project.optional-dependencies]
# LLM Providers
openai = ["openai>=1.0"]
ollama = ["ollama>=0.1"]
google = ["google-generativeai>=0.3"]

# Image Providers
# (included in openai for DALL-E)

# All providers
all-providers = [
    "openai>=1.0",
    "ollama>=0.1",
    "google-generativeai>=0.3",
]

# Documentation
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.24",
]

# Development
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.0",
    "mypy>=1.8",
    "ruff>=0.1",
]
```

---

## Timeline & Estimates

### Conservative Estimate (AI Agent + Human Review)

| Epic | Duration | Cumulative |
|------|----------|------------|
| ✅ Epic 1-6 | 10 weeks | 10 weeks |
| 🔄 Epic 7-8 | 4 weeks | 14 weeks |
| Epic 9 | 3 weeks | 17 weeks |
| Epic 10 | 2 weeks | 19 weeks |
| Epic 11 | 2 weeks | 21 weeks |

**Total:** ~21 weeks (5 months)

### Optimistic Estimate (Full-Time AI Agent)

| Epic | Duration | Cumulative |
|------|----------|------------|
| ✅ Epic 1-6 | 6 weeks | 6 weeks |
| 🔄 Epic 7-8 | 2 weeks | 8 weeks |
| Epic 9 | 2 weeks | 10 weeks |
| Epic 10 | 1 week | 11 weeks |
| Epic 11 | 1 week | 12 weeks |

**Total:** ~12 weeks (3 months)

### Current Pace Analysis

- **Epics 1-6 completed:** ~10 weeks actual
- **Average per epic:** ~1.7 weeks
- **Remaining epics:** 5 (Epic 7-8 combined, 9, 10, 11)
- **Projected completion:** ~8-9 additional weeks

---

## Success Metrics

### Functional Completeness

- [ ] All 17 artifact types supported
- [ ] All 11 loops implemented
- [ ] All 11 roles functional
- [ ] Layer 4 protocol conformant
- [ ] PN safety enforced
- [ ] 8 quality bars operational

### Code Quality

- [ ] >80% test coverage
- [ ] All mypy checks passing
- [ ] All ruff linting passing
- [ ] No critical security issues
- [ ] Performance benchmarks met

### Documentation

- [ ] API reference complete
- [ ] User guide written
- [ ] Developer guide available
- [ ] All examples runnable
- [ ] Quickstart functional

### Distribution

- [ ] PyPI package published
- [ ] GitHub releases tagged
- [ ] CI/CD pipeline green
- [ ] Installation verified

---

## Risk Management

### Technical Risks

**Risk:** LLM provider API changes
**Mitigation:** Abstract provider interface, multiple providers supported

**Risk:** Context size limitations
**Mitigation:** Two-tier context architecture, aggressive summarization

**Risk:** Performance issues with large projects
**Mitigation:** Lazy loading, caching, indexed queries

**Risk:** Quality bar validation complexity
**Mitigation:** Start with simple heuristics, iterate with LLM feedback

### Process Risks

**Risk:** Scope creep in loop implementations
**Mitigation:** Strict adherence to spec, defer enhancements

**Risk:** Integration complexity between epics
**Mitigation:** Clear interfaces, integration tests at epic boundaries

**Risk:** Documentation lag
**Mitigation:** Write docs during implementation, not after

---

## Next Steps

### Immediate Actions (Epic 7-8 Start)

1. **Set up branch:** `claude/epic-07-08-intelligence-layer-{session_id}`
2. **Create base infrastructure:**
   - `src/questfoundry/roles/` directory structure
   - `src/questfoundry/loops/` directory structure
   - Base classes (`Role`, `Loop`, `LoopContext`)
3. **Implement first role:** Plotwright (most common)
4. **Implement loop registry:** Metadata for all 11 loops
5. **Test framework:** Mocking strategies for LLM calls

### Epic 7-8 Milestone Plan

**Week 12:**
- Role system foundation
- 3 core roles (Plotwright, Gatekeeper, Scene Smith)
- Prompt loading from spec/

**Week 13:**
- Loop registry complete
- Loop base class + context management
- First loop: story_spark (skeleton)

**Week 14:**
- story_spark loop complete
- hook_harvest loop implementation
- Integration tests

**Week 15:**
- Showrunner orchestration
- Collaboration patterns
- Context optimization
- Epic 7-8 complete

---

## Appendix A: Layer Dependencies

**QuestFoundry Stack:**
- **Layer 0:** North Star (spec/00-north-star/) - Vision & principles
- **Layer 1:** Roles (spec/01-roles/) - Agent responsibilities
- **Layer 2:** Dictionary (spec/02-dictionary/) - Terminology
- **Layer 3:** Schemas (spec/03-schemas/) - Artifact definitions
- **Layer 4:** Protocol (spec/04-protocol/) - Message format
- **Layer 5:** Prompts (future) - Role execution templates
- **Layer 6:** Library (this project) - Python implementation

**Implementation Status:**
- ✅ Layers 0-4 specifications complete
- 🔄 Layer 6 in progress (Epics 1-6 done)
- ⏳ Layer 5 prompts (parallel development)

---

## Appendix B: Key Architectural Decisions

### ADR-001: Hybrid Loop Architecture

**Decision:** Implement loops as Python classes, not runtime playbook parsing

**Rationale:**
- 97% context reduction (600 lines vs 10,000 lines)
- Type safety and IDE support
- Faster execution, no parsing overhead
- Easier testing and debugging

**Tradeoffs:**
- Less runtime flexibility
- Code changes required for loop modifications
- Accepted: Playbooks are specifications, not runtime code

### ADR-002: Two-Tier Context System

**Decision:** Registry context (~90 lines) + Active context (~500 lines)

**Rationale:**
- Showrunner doesn't need full details for loop selection
- Reduces token usage for strategic decisions
- Only load detailed context when executing

**Tradeoffs:**
- More complex context management
- Accepted: Performance benefit worth complexity

### ADR-003: Provider Abstraction

**Decision:** Abstract provider interface supporting multiple LLM backends

**Rationale:**
- Avoid vendor lock-in
- Support local models (Ollama)
- Enable testing with mocks
- Flexibility for users

**Tradeoffs:**
- Lowest common denominator API
- Accepted: Most features are provider-agnostic

### ADR-004: Dual Persistence (SQLite + Files)

**Decision:** SQLite for .qfproj, files for hot workspace

**Rationale:**
- SQLite: Transactional, queryable, portable
- Files: Git-friendly, human-readable, debuggable
- Best of both worlds

**Tradeoffs:**
- Synchronization complexity
- Accepted: Workspace abstraction hides complexity

---

## Appendix C: Glossary

**Artifact:** Structured content unit (hook, TU brief, codex entry, etc.)
**Loop:** Workflow coordinating roles to produce/refine artifacts
**Role:** Specialized agent (Plotwright, Gatekeeper, etc.)
**Showrunner:** Meta-role orchestrating other roles
**PN (Player-Neutral):** Content safe for players (no spoilers)
**Quality Bar:** Validation criterion (integrity, reachability, etc.)
**TU (Transmedia Unit):** Single quest/mission/episode
**RACI:** Responsible, Accountable, Consulted, Informed
**Hot/Cold:** Storage context (Hot=in-progress, Cold=published)
**Context Tier:** Registry (lightweight) vs Active (detailed)

---

**End of Implementation Plan**
