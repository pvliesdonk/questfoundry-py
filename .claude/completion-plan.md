# QuestFoundry Library Completion Plan

**Repository:** pvliesdonk/questfoundry-py
**Current State:** Epics 1-10 Complete
**Target:** Full Feature Completeness (Not Just MVP)

---

## Architecture Context

**Three-Repository Model:**
1. ✅ **Spec Repo** (`questfoundry`) - Specifications, prompts, schemas
2. 🟡 **Library Repo** (`questfoundry-py`) - THIS REPO - Python SDK
3. 🔄 **CLI Repo** (`questfoundry-cli`) - Command-line interface (separate, ongoing)
4. 🔮 **Future:** WebUI, TUI, etc. (separate repos)

**This Plan Covers:** Only the library repo (questfoundry-py)

---

## Current Completion Status

### ✅ Fully Complete (Epics 1-10)

- Project foundation & tooling
- Schema bundling & validation
- Protocol client & conformance
- State management (SQLite + file-based)
- Artifact models & lifecycles
- Provider system (text, image)
- Role system foundation
- Showrunner & orchestration basics
- Safety & quality (PN Guard, quality bars)
- Export & views (YAML, HTML, Markdown)

### 🟡 Partially Complete

- **Loop Implementations:** 1 of 14 done
- **Provider Coverage:** Core providers only
- **Session Management:** Framework exists, but no conversation tracking
- **Interactive Mode Support:** Prompts exist, no programmatic support

### ❌ Not Started

- Most loop implementations
- Audio providers
- Advanced provider integrations
- Session conversation history
- Agent-to-human callback mechanism

---

## Completion Roadmap

## Epic 11: Documentation & Polish (PLANNED)

**Status:** Next up
**Goal:** Comprehensive documentation for library users

### 11.1: API Documentation

**Files to create/update:**
```
docs/
  api/
    protocol.md           # Protocol client API
    state.md              # State management API
    providers.md          # Provider system API
    roles.md              # Role execution API
    validation.md         # Validation API
    export.md             # Export & views API
  guides/
    getting-started.md    # Quick start for library users
    providers.md          # Provider configuration guide
    custom-providers.md   # Building custom providers
    loops.md              # Loop development guide
    state-management.md   # State persistence guide
  examples/
    basic_workflow.py     # Simple end-to-end example
    custom_provider.py    # Custom provider example
    custom_loop.py        # Custom loop example
```

**Tasks:**
- Auto-generate API docs from docstrings
- Write user guides for common tasks
- Create working code examples
- Document configuration options
- Add troubleshooting guide

**Acceptance Criteria:**
- All public APIs documented
- 5+ working examples
- Clear getting-started path
- Configuration reference complete

---

## Epic 12: Loop Implementations (HIGH PRIORITY)

**Status:** Not started
**Goal:** Implement all 14 loops from playbooks
**Estimated Effort:** 8-10 days

### Priority Groups

#### Group A: Content Creation Loops (High Priority)

**12.1: Hook Harvest Loop**
```
src/questfoundry/loops/hook_harvest.py
tests/loops/test_hook_harvest.py
```
- Wake: Lore Weaver, Showrunner
- Creates: Hook cards from premise
- Playbook: `resources/prompts/loops/hook_harvest.playbook.md`

**12.2: Lore Deepening (Canon Expansion) Loop**
```
src/questfoundry/loops/lore_deepening.py
tests/loops/test_lore_deepening.py
```
- Wake: Lore Weaver, Researcher, Showrunner
- Creates: Canon packs from hooks
- Playbook: `resources/prompts/loops/lore_deepening.playbook.md`

**12.3: Scene Forge Loop**
```
src/questfoundry/loops/scene_forge.py
tests/loops/test_scene_forge.py
```
- Wake: Scene Smith, Showrunner
- Creates: Scene content from hooks/canon
- Requires: Hook + canon → scene draft

**12.4: Codex Expansion Loop**
```
src/questfoundry/loops/codex_expansion.py
tests/loops/test_codex_expansion.py
```
- Wake: Codex Curator, Showrunner
- Creates: Codex entries
- Playbook: `resources/prompts/loops/codex_expansion.playbook.md`

#### Group B: Polish & Refinement Loops (Medium Priority)

**12.5: Style Tune-Up Loop**
```
src/questfoundry/loops/style_tune_up.py
tests/loops/test_style_tune_up.py
```
- Wake: Style Lead, Scene Smith, Showrunner
- Refines: Scene text for style consistency
- Playbook: `resources/prompts/loops/style_tune_up.playbook.md`

**12.6: Gatecheck Loop**
```
src/questfoundry/loops/gatecheck.py
tests/loops/test_gatecheck.py
```
- Wake: Gatekeeper, Showrunner
- Validates: All quality bars
- Playbook: `resources/prompts/loops/gatecheck.playbook.md`

#### Group C: Asset Generation Loops (Medium Priority)

**12.7: Art Touch-Up Loop**
```
src/questfoundry/loops/art_touch_up.py
tests/loops/test_art_touch_up.py
```
- Wake: Art Director, Illustrator, Showrunner
- Creates: Shotlists and images
- Playbook: `resources/prompts/loops/art_touch_up.playbook.md`

**12.8: Audio Pass Loop**
```
src/questfoundry/loops/audio_pass.py
tests/loops/test_audio_pass.py
```
- Wake: Audio Director, Audio Producer, Showrunner
- Creates: Cuelists and audio
- Playbook: `resources/prompts/loops/audio_pass.playbook.md`
- Requires: Audio providers (Epic 13)

#### Group D: Finalization Loops (Lower Priority)

**12.9: Translation Pass Loop**
```
src/questfoundry/loops/translation_pass.py
tests/loops/test_translation_pass.py
```
- Wake: Translator, Showrunner
- Creates: Language packs
- Playbook: `resources/prompts/loops/translation_pass.playbook.md`

**12.10: Binding Run Loop**
```
src/questfoundry/loops/binding_run.py
tests/loops/test_binding_run.py
```
- Wake: Book Binder, Showrunner
- Creates: Final exports (uses Epic 10 export module)
- Playbook: `resources/prompts/loops/binding_run.playbook.md`

**12.11: Narration Dry Run Loop**
```
src/questfoundry/loops/narration_dry_run.py
tests/loops/test_narration_dry_run.py
```
- Wake: Player Narrator, Showrunner
- Tests: Player experience flow
- Playbook: `resources/prompts/loops/narration_dry_run.playbook.md`

**12.12: Archive Snapshot Loop**
```
src/questfoundry/loops/archive_snapshot.py
tests/loops/test_archive_snapshot.py
```
- Wake: Showrunner
- Creates: Cold snapshots
- Playbook: `resources/prompts/loops/archive_snapshot.playbook.md`

**12.13: Post Mortem Loop**
```
src/questfoundry/loops/post_mortem.py
tests/loops/test_post_mortem.py
```
- Wake: Gatekeeper, Showrunner
- Creates: Final quality report
- Playbook: `resources/prompts/loops/post_mortem.playbook.md`

### Acceptance Criteria (All Loops)
- Implements loop playbook faithfully
- Wakes/dormants correct roles
- Creates expected artifacts
- Handles errors gracefully
- Full test coverage (mock LLM)
- Integrates with Showrunner

---

## Epic 13: Session Management & Interactive Mode

**Status:** Not started
**Goal:** Enable conversation history and agent-to-human communication
**Estimated Effort:** 4-5 days
**Priority:** HIGH (needed for interactive mode)

### 13.1: Role Session Class

**Files to create:**
```
src/questfoundry/roles/session.py
tests/roles/test_session.py
```

**Implementation:**
```python
@dataclass
class RoleSession:
    """Maintains conversation context for an active role."""

    role: str
    tu_context: str
    conversation_history: list[Envelope]
    active_since: datetime
    dormancy_signals: list[str]
    workspace_path: Path

    def send_message(self, envelope: Envelope) -> Envelope:
        """Send message and update conversation history."""

    def add_to_history(self, envelope: Envelope) -> None:
        """Add envelope to conversation history."""

    def get_context_window(self, max_messages: int = 50) -> list[Envelope]:
        """Get recent conversation history for LLM context."""

    def archive(self) -> dict:
        """Archive session state for audit trail."""

    def should_dormant(self) -> bool:
        """Check if role should go dormant based on signals."""
```

**Tasks:**
- Implement RoleSession dataclass
- Add conversation history management
- Implement context window (manage token limits)
- Add session archiving
- Store sessions in workspace
- Load archived sessions

**Acceptance Criteria:**
- Sessions maintain conversation history
- Context window respects token limits
- Sessions persist to disk
- Can resume from archived session

---

### 13.2: Session Manager

**Files to create:**
```
src/questfoundry/roles/session_manager.py
tests/roles/test_session_manager.py
```

**Implementation:**
```python
class SessionManager:
    """Manages all active role sessions."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.active_sessions: dict[str, RoleSession] = {}

    def wake_role(self, role: str, tu: str) -> RoleSession:
        """Create new session for role."""

    def dormant_role(self, role: str) -> dict:
        """Archive and clear role session."""

    def get_session(self, role: str) -> RoleSession | None:
        """Get active session for role."""

    def get_active_roles(self) -> list[str]:
        """List currently active roles."""

    def archive_all(self) -> dict[str, dict]:
        """Archive all active sessions."""
```

**Tasks:**
- Implement SessionManager
- Track active sessions
- Handle wake/dormant lifecycle
- Integrate with Showrunner
- Add session directory structure

**Acceptance Criteria:**
- Can manage multiple concurrent sessions
- Sessions archived on dormancy
- Showrunner uses SessionManager
- Session files stored in `.questfoundry/sessions/`

---

### 13.3: Agent-to-Human Communication

**Files to create:**
```
src/questfoundry/roles/human_callback.py
tests/roles/test_human_callback.py
```

**Implementation:**
```python
from typing import Callable

HumanCallback = Callable[[str, dict], str]
"""
Callback function signature for agent-to-human questions.

Args:
    question: The question text
    context: Additional context (suggestions, artifacts, etc.)

Returns:
    Human's response text
"""

class InteractiveRole(Role):
    """Role that can ask humans questions."""

    def __init__(
        self,
        provider: TextProvider,
        human_callback: HumanCallback | None = None,
        **kwargs
    ):
        super().__init__(provider, **kwargs)
        self.human_callback = human_callback

    def ask_human(
        self,
        question: str,
        context: dict | None = None,
        suggestions: list[str] | None = None,
    ) -> str:
        """
        Ask human a question (interactive mode).

        Falls back to auto-response if no callback provided.
        """
        if self.human_callback is None:
            # Batch mode: return default/skip
            return self._default_response(question, context)

        # Interactive mode: use callback
        callback_context = {
            "question": question,
            "context": context or {},
            "suggestions": suggestions or [],
        }
        return self.human_callback(question, callback_context)
```

**Tasks:**
- Define callback interface
- Add ask_human() to Role base class
- Implement in InteractiveRole
- Add to Showrunner orchestration
- Create human.question/human.response intents
- Handle in protocol client

**Acceptance Criteria:**
- Roles can call ask_human()
- Works with callback (interactive)
- Works without callback (batch/guided)
- Integrates with protocol (human.question intent)
- Tests with mock callback

---

### 13.4: Integrate with Existing Roles

**Files to update:**
```
src/questfoundry/roles/showrunner.py
src/questfoundry/roles/gatekeeper.py
src/questfoundry/roles/scene_smith.py
src/questfoundry/roles/lore_weaver.py
[others as needed]
```

**Tasks:**
- Update Role base class to support sessions
- Add session parameter to execute()
- Update Showrunner to use SessionManager
- Add ask_human() calls where prompts indicate
- Update tests to work with sessions

**Acceptance Criteria:**
- All roles work with SessionManager
- Conversation history maintained
- Interactive mode supported
- Backward compatible (sessions optional)

---

## Epic 14: Additional Provider Support

**Status:** Not started
**Goal:** Complete provider coverage for all modalities
**Estimated Effort:** 5-6 days
**Priority:** MEDIUM (nice to have, not blocking)

### 14.1: Audio Generation Providers

**Files to create:**
```
src/questfoundry/providers/audio/
  __init__.py
  base.py                # AudioProvider ABC
  elevenlabs.py          # ElevenLabs TTS
  mock.py                # Mock audio provider
tests/providers/audio/
  test_elevenlabs.py
  test_mock.py
```

**Implementation:**
```python
class AudioProvider(ABC):
    """Base class for audio generation providers."""

    @abstractmethod
    def generate_audio(
        self,
        text: str,
        voice: str | None = None,
        **kwargs
    ) -> bytes:
        """Generate audio from text."""

    @abstractmethod
    def list_voices(self) -> list[dict]:
        """List available voices."""
```

**Providers to Implement:**
1. **ElevenLabs** - Professional TTS
   - API: ElevenLabs API
   - Features: Multiple voices, emotions, languages
2. **Mock Audio Provider** - Testing
   - Returns: Silent WAV file or test audio

**Tasks:**
- Define AudioProvider ABC
- Implement ElevenLabs provider
- Implement mock provider
- Add to provider registry
- Add configuration support
- Update Audio Producer role to use

**Acceptance Criteria:**
- ElevenLabs provider works with API
- Mock provider for testing
- Audio artifacts stored correctly
- Integrated with Audio Producer role

---

### 14.2: Google AI Studio / Gemini Provider

**Files to create:**
```
src/questfoundry/providers/text/gemini.py
tests/providers/text/test_gemini.py
```

**Implementation:**
```python
class GeminiProvider(TextProvider):
    """Google Gemini text generation provider."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        # Use google-generativeai package
```

**Tasks:**
- Implement Gemini provider
- Support latest Gemini models
- Add configuration
- Add to provider registry
- Test with mock and real API

**Acceptance Criteria:**
- Works with Google AI Studio API
- Supports gemini-2.0-flash-exp
- Handles errors gracefully
- Configuration documented

---

### 14.3: Amazon Bedrock Provider

**Files to create:**
```
src/questfoundry/providers/text/bedrock.py
tests/providers/text/test_bedrock.py
```

**Implementation:**
```python
class BedrockProvider(TextProvider):
    """Amazon Bedrock text generation provider."""

    def __init__(
        self,
        region: str = "us-east-1",
        model: str = "anthropic.claude-3-sonnet",
        **kwargs
    ):
        # Use boto3 for Bedrock
```

**Tasks:**
- Implement Bedrock provider
- Support Claude models on Bedrock
- Handle AWS credentials
- Add configuration
- Test with mock and real API

**Acceptance Criteria:**
- Works with AWS Bedrock
- Supports Claude 3 models
- Handles AWS auth correctly
- Configuration documented

---

### 14.4: Google Imagen 4 Provider

**Files to create:**
```
src/questfoundry/providers/image/imagen.py
tests/providers/image/test_imagen.py
```

**Implementation:**
```python
class ImagenProvider(ImageProvider):
    """Google Imagen 4 image generation provider."""

    def __init__(self, api_key: str, model: str = "imagen-4"):
        # Use Google AI API
```

**Tasks:**
- Implement Imagen provider
- Add configuration
- Test with mock and real API

**Acceptance Criteria:**
- Works with Imagen 4 API
- Generates images correctly
- Configuration documented

---

## Epic 15: Advanced Features & Polish

**Status:** Not started
**Goal:** Additional enhancements for production readiness
**Estimated Effort:** 4-5 days
**Priority:** LOW (enhancements)

### 15.1: Provider Caching & Rate Limiting

**Files to create:**
```
src/questfoundry/providers/cache.py
src/questfoundry/providers/rate_limiter.py
tests/providers/test_cache.py
tests/providers/test_rate_limiter.py
```

**Features:**
- Response caching (avoid duplicate LLM calls)
- Rate limiting (respect API limits)
- Cost tracking (monitor spending)
- Retry logic with exponential backoff

**Tasks:**
- Implement response cache
- Add rate limiting
- Track API costs
- Add retry logic
- Integrate with all providers

**Acceptance Criteria:**
- Cached responses used when available
- Rate limits respected
- Costs tracked per provider
- Retries work correctly

---

### 15.2: Per-Role Provider Configuration

**Files to update:**
```
src/questfoundry/providers/config.py
src/questfoundry/roles/base.py
```

**Feature:**
```yaml
# .questfoundry/config.yml
roles:
  scene_smith:
    provider: openai
    model: gpt-4o
    temperature: 0.8
  gatekeeper:
    provider: ollama
    model: llama3
    temperature: 0.2
  illustrator:
    provider: dalle
    model: dall-e-3
```

**Tasks:**
- Update config schema
- Add per-role provider selection
- Update Showrunner to use role-specific providers
- Update Role base class

**Acceptance Criteria:**
- Can configure provider per role
- Falls back to default if not specified
- All roles respect configuration

---

### 15.3: Advanced State Management

**Files to create:**
```
src/questfoundry/state/redis_store.py      # Future: distributed
src/questfoundry/state/migration.py        # Schema migrations
tests/state/test_redis_store.py
tests/state/test_migration.py
```

**Features:**
- Redis/Valkey backend (distributed workflows)
- Schema migrations (version upgrades)
- State export/import (portability)

**Tasks:**
- Design Redis state backend
- Implement migration system
- Add state export/import utilities
- Test with real Redis

**Acceptance Criteria:**
- Redis backend works
- Migrations handle version changes
- Can export/import project state

---

### 15.4: Comprehensive Test Suite

**Files to create:**
```
tests/integration/
  test_end_to_end.py          # Full workflow tests
  test_multi_loop.py          # Multiple loops
  test_error_recovery.py      # Error handling
tests/performance/
  test_large_project.py       # Scale testing
  test_provider_performance.py
```

**Tasks:**
- Add end-to-end integration tests
- Test error recovery
- Performance/scale testing
- Provider integration tests (with real APIs)
- Stress testing

**Acceptance Criteria:**
- Full workflow tested end-to-end
- Error cases covered
- Performance acceptable (benchmarks)
- All providers tested with real APIs

---

## Implementation Timeline

### Phase 1: Core Completeness (3-4 weeks)
**Priority:** HIGH - Makes library feature-complete

1. **Epic 11:** Documentation & Polish (1 week)
2. **Epic 12:** Loop Implementations (2 weeks)
   - Week 1: Group A (content creation) + Group B (polish)
   - Week 2: Group C (assets) + Group D (finalization)
3. **Epic 13:** Session Management (1 week)

**Deliverable:** Fully functional library with all loops and interactive mode

---

### Phase 2: Provider Expansion (1-2 weeks)
**Priority:** MEDIUM - Enhances provider options

4. **Epic 14.1:** Audio Providers (ElevenLabs) (3 days)
5. **Epic 14.2-14.4:** Additional Text/Image Providers (4 days)

**Deliverable:** Complete provider coverage (text, image, audio)

---

### Phase 3: Production Readiness (1-2 weeks)
**Priority:** LOW - Polish and advanced features

6. **Epic 15.1:** Caching & Rate Limiting (3 days)
7. **Epic 15.2:** Per-Role Configuration (2 days)
8. **Epic 15.3:** Advanced State Management (3 days)
9. **Epic 15.4:** Comprehensive Testing (3 days)

**Deliverable:** Production-ready library with advanced features

---

## Total Estimated Effort

- **Phase 1 (Core):** 3-4 weeks
- **Phase 2 (Providers):** 1-2 weeks
- **Phase 3 (Polish):** 1-2 weeks

**Total:** 5-8 weeks for complete library

**Minimum Viable Complete:** Phase 1 (3-4 weeks)

---

## Success Criteria

### Library is "Complete" When:

1. ✅ All 14 loops implemented and tested
2. ✅ Session management working (conversation history)
3. ✅ Interactive mode supported (ask_human callback)
4. ✅ Comprehensive documentation with examples
5. ✅ Audio provider support (at least ElevenLabs)
6. ✅ Additional major providers (Gemini, Bedrock optional)
7. ✅ All tests passing (unit, integration, end-to-end)
8. ✅ Performance acceptable for real projects
9. ✅ Error handling robust
10. ✅ Configuration flexible (per-role providers)

### Library is "Production Ready" When:

- Above +
- Response caching implemented
- Rate limiting working
- Cost tracking functional
- Migration system in place
- Performance benchmarks established
- Real-world projects tested

---

## Dependencies

### Internal (This Repo):
- Epic 11 → Epic 12 (docs help loop implementation)
- Epic 12 → Epic 13 (loops need session support)
- Epic 14.1 → Epic 12.8 (Audio Pass loop needs audio providers)

### External (Other Repos):
- CLI (questfoundry-cli) consumes this library
- Spec repo provides prompts and schemas (already integrated)

---

## Quality Gates

Each epic must pass:
- ✅ All tests passing
- ✅ Mypy type checking clean
- ✅ Ruff linting clean
- ✅ Documentation updated
- ✅ PR reviewed and approved

---

## Notes

- **CLI is separate:** Layer 7 (questfoundry-cli) is separate repo
- **WebUI future:** Will be another separate repo
- **This is library only:** Focus on SDK completeness
- **Not just MVP:** This is full feature completeness
- **Maintainable:** Keep code quality high throughout

---

## Next Action

**Recommended Start:** Epic 11 (Documentation & Polish)
- Good checkpoint after Epic 10
- Helps understand what's needed for loops
- Makes library usable while implementing remaining features
- Documents API for CLI developers
