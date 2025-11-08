# Epic 13: Session Management & Interactive Mode

## Overview

Epic 13 implements session management and agent-to-human communication for the QuestFoundry library, enabling conversation history tracking and interactive mode support. This infrastructure allows roles to maintain context across multiple interactions and optionally ask humans questions during execution.

This epic is HIGH PRIORITY according to the completion plan, as it enables interactive mode workflows while remaining fully backward compatible with existing batch/guided modes.

## Features Implemented

### 13.1: RoleSession Class

**File:** `src/questfoundry/roles/session.py` (196 lines)

Conversation history and state tracking for individual roles:

**Key Features:**
- Tracks all conversation history (Envelope objects)
- Context window management (limit to recent N messages)
- Dormancy signal tracking (task.complete, error.fatal, etc.)
- Session persistence (save/load to JSON files)
- Active duration tracking

**Key Methods:**
- `send_message(envelope)` - Send message and update history
- `add_to_history(envelope)` - Add envelope to conversation
- `get_context_window(max_messages=50)` - Get recent messages for LLM
- `add_dormancy_signal(signal)` - Signal role should go dormant
- `should_dormant()` - Check if role should go dormant
- `archive()` - Export session state as dict
- `save_to_file(path)` - Save session to `.questfoundry/sessions/{role}/`
- `load_from_file(path)` - Restore session from file

**Storage Structure:**
```
.questfoundry/sessions/
  scene_smith/
    session-20250108-143022.json
    session-20250108-150135.json
  showrunner/
    session-20250108-143025.json
```

**Tests:** 15 tests in `tests/roles/test_session.py`

### 13.2: SessionManager Class

**File:** `src/questfoundry/roles/session_manager.py` (177 lines)

Multi-role session coordination:

**Key Features:**
- Manages all active role sessions simultaneously
- Wake/dormant lifecycle management
- Bulk operations (archive_all, dormant_all)
- Dormancy signal coordination
- Total message counting across sessions

**Key Methods:**
- `wake_role(role, tu_context)` - Create/get session for role
- `dormant_role(role)` - Archive and clear role session
- `get_session(role)` - Get active session if exists
- `get_active_roles()` - List all awake roles
- `is_role_awake(role)` - Check if role is active
- `archive_all()` - Snapshot all sessions (non-destructive)
- `dormant_all()` - Archive and clear all sessions
- `get_sessions_needing_dormancy()` - Find roles with signals
- `clear_dormancy_signals(role)` - Manual intervention
- `get_total_message_count()` - Monitoring across all sessions

**Usage Pattern:**
```python
manager = SessionManager(workspace_path)

# Wake roles
scene_smith_session = manager.wake_role("scene_smith", "TU-2024-01-15-TEST01")
showrunner_session = manager.wake_role("showrunner", "TU-2024-01-15-TEST01")

# Track conversation
scene_smith_session.add_to_history(envelope)

# Check status
if manager.is_role_awake("scene_smith"):
    session = manager.get_session("scene_smith")

# Make dormant when done
manager.dormant_role("scene_smith")
```

**Tests:** 18 tests in `tests/roles/test_session_manager.py`

### 13.3: Agent-to-Human Communication

**File:** `src/questfoundry/roles/human_callback.py` (285 lines)

Callback mechanism for roles to ask humans questions:

**Key Components:**

**HumanCallback Type:**
```python
HumanCallback = Callable[[str, dict[str, Any]], str]
```

**Callbacks Provided:**
- `default_human_callback` - Simple stdin prompts (reference implementation)
- `batch_mode_callback` - Auto-answers with first suggestion (automated workflows)

**HumanInteractionMixin Class:**
- Mixin for roles that need human interaction
- Can be added to any Role subclass
- Three convenience methods for common patterns

**Key Methods:**
- `ask_human(question, context, suggestions, artifacts)` - Open-ended question
- `ask_yes_no(question, default)` - Boolean question
  - Recognizes: yes/y/true/1 → True, no/n/false/0 → False
- `ask_choice(question, choices, default)` - Multiple choice
  - Accepts direct match or 1-indexed number

**Batch vs Interactive Mode:**
- **Batch mode** (no callback): Returns first suggestion or empty string
- **Interactive mode** (with callback): Prompts human and waits for response

**Integration:**
```python
# Batch mode (automated)
role = SceneSmith(provider)
# ask_human() returns first suggestion automatically

# Interactive mode
def my_callback(question: str, context: dict) -> str:
    print(f"Question: {question}")
    return input("Answer: ")

role = SceneSmith(provider, human_callback=my_callback)
# ask_human() prompts user via callback
```

**Tests:** 16 tests in `tests/roles/test_human_callback.py`

### 13.4: Role Base Class Integration

**Modified:** `src/questfoundry/roles/base.py` (+147 lines)

Integrated session and human callback support into Role base class:

**Changes:**
- Added optional `session: RoleSession | None` parameter to `__init__()`
- Added optional `human_callback: HumanCallback | None` parameter to `__init__()`
- Added `ask_human()`, `ask_yes_no()`, `ask_choice()` methods
- Updated `__repr__()` to show session and interactive status
- TYPE_CHECKING used to avoid circular imports

**Backward Compatibility:**
- Both parameters are optional (default None)
- Existing code works unchanged
- No breaking changes to existing APIs
- All existing tests still pass

**Usage:**
```python
# Without sessions (existing code - still works)
role = SceneSmith(provider)
result = role.execute_task(context)

# With session tracking
session = RoleSession(role="scene_smith")
role = SceneSmith(provider, session=session)
result = role.execute_task(context)
# Session now contains conversation history

# With interactive mode
def callback(q: str, ctx: dict) -> str:
    return input(f"{q} ")

role = SceneSmith(provider, human_callback=callback)
if role.ask_yes_no("Generate images?"):
    generate_images()

# With both
role = SceneSmith(provider, session=session, human_callback=callback)
```

**Tests:** 16 tests in `tests/roles/test_base_session_integration.py`

## Code Quality

### Validation Results
- ✅ **439 tests passing, 4 skipped**
- ✅ **Mypy type checking clean** (72 source files)
- ✅ **Ruff linting clean**

### Standards Met
- ✅ **Backward Compatibility**: All existing code works unchanged
- ✅ **Type Safety**: Full type annotations with strict mypy
- ✅ **Encapsulation**: Session data properly encapsulated
- ✅ **Optional Features**: Sessions and callbacks are opt-in
- ✅ **Clean Separation**: Concerns properly separated (session storage, callback mechanism, role integration)

## Testing Strategy

### Unit Tests (65 new tests total)

**RoleSession Tests (15)**:
- Session creation and basic operations
- Conversation history management
- Context window limiting
- Dormancy signal tracking
- File persistence (save/load)
- Archive functionality

**SessionManager Tests (18)**:
- Multi-session management
- Wake/dormant lifecycle
- Bulk operations
- Signal coordination
- Message counting

**HumanCallback Tests (16)**:
- Batch mode behavior
- Interactive mode with callbacks
- Yes/no question parsing
- Multiple choice selection
- Mixin inheritance

**Integration Tests (16)**:
- Role with/without sessions
- Role with/without callbacks
- Backward compatibility verification
- Combined session + callback usage

### Integration Points
- Protocol envelope integration
- File-based session storage
- Workspace directory structure
- Existing Role base class

## File Changes

### New Files (8)

**Implementation (4)**:
- src/questfoundry/roles/session.py (196 lines)
- src/questfoundry/roles/session_manager.py (177 lines)
- src/questfoundry/roles/human_callback.py (285 lines)
- .claude/pr-description-epic-13.md (this file)

**Tests (4)**:
- tests/roles/test_session.py (178 lines)
- tests/roles/test_session_manager.py (220 lines)
- tests/roles/test_human_callback.py (263 lines)
- tests/roles/test_base_session_integration.py (227 lines)

### Modified Files (1)

- **src/questfoundry/roles/base.py**: Added session and human_callback support (+147 lines)
  - Optional session and human_callback parameters
  - ask_human(), ask_yes_no(), ask_choice() methods
  - Enhanced __repr__() with session/interactive status

## Architecture Patterns

### Session Management Pattern

```python
# 1. Create manager
manager = SessionManager(workspace_path)

# 2. Wake roles as needed
session = manager.wake_role("scene_smith", tu_context)

# 3. Track conversation
session.add_to_history(envelope)

# 4. Check dormancy
if session.should_dormant():
    manager.dormant_role("scene_smith")
```

### Interactive Mode Pattern

```python
# 1. Define callback (or use default)
def my_callback(question: str, context: dict) -> str:
    suggestions = context.get("suggestions", [])
    print(f"Q: {question}")
    if suggestions:
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s}")
    return input("Answer: ")

# 2. Create role with callback
role = SceneSmith(provider, human_callback=my_callback)

# 3. Use ask_human methods
tone = role.ask_choice("Scene tone?", ["dark", "light"])
if role.ask_yes_no("Add images?"):
    generate_images()
```

### Batch Mode Pattern

```python
# No callback = batch mode
role = SceneSmith(provider)  # Uses batch_mode_callback

# Automatically uses first suggestion
tone = role.ask_choice("Tone?", ["dark", "light"])  # Returns "dark"
proceed = role.ask_yes_no("Continue?")  # Returns True (first suggestion "yes")
```

## Key Design Decisions

1. **Optional Integration**: Sessions and callbacks are opt-in, maintaining backward compatibility
2. **TYPE_CHECKING**: Used to avoid circular imports between base.py and session.py
3. **Batch Mode Default**: ask_human() defaults to batch_mode_callback for automated workflows
4. **Context Window**: Sessions limit history to prevent token overflow
5. **Dormancy Signals**: Explicit signals (task.complete, error.fatal) control lifecycle
6. **File Persistence**: Sessions saved to `.questfoundry/sessions/{role}/` for audit trails
7. **Yes/No Parsing**: Liberal parsing (yes/y/true/1, no/n/false/0) for flexibility
8. **Choice Selection**: Supports both direct match and 1-indexed numbers

## Dependencies

- **Required**: Epic 1-12 (all complete)
- **Python**: 3.11+
- **External**: None (uses only standard library + existing dependencies)
- **Integrates With**:
  - Epic 2 (Protocol) - Envelope objects in conversation history
  - Epic 3 (State Management) - Workspace path for session storage

## Breaking Changes

**None** - This epic is fully backward compatible:
- Sessions are optional (default None)
- Human callbacks are optional (default batch_mode_callback)
- All existing Role usage patterns work unchanged
- No changes to existing method signatures (only additions)

## Future Enhancements

**From Completion Plan:**
- **Epic 14**: Additional provider support (audio, Gemini, Bedrock)
- **Epic 15**: Advanced features (caching, rate limiting, per-role configuration)

**Session Management:**
- Redis/Valkey backend for distributed sessions
- Session migration tools for version upgrades
- Session analytics and monitoring

**Interactive Mode:**
- Rich text formatting for CLI prompts
- Web-based callback implementations
- Voice input support
- Multi-modal interaction (text + images)

## Usage Examples

### Example 1: Basic Session Tracking

```python
from questfoundry.roles.session_manager import SessionManager
from questfoundry.roles.scene_smith import SceneSmith

# Create manager
manager = SessionManager(workspace_path=Path("."))

# Wake role with session
session = manager.wake_role("scene_smith", "TU-2024-01-15-TEST01")

# Create role with session
role = SceneSmith(provider, session=session)

# Execute task (history tracked in session)
result = role.execute_task(context)

# Get conversation history
history = session.get_context_window(max_messages=10)
print(f"Messages: {len(history)}")

# Make dormant when done
manager.dormant_role("scene_smith")
```

### Example 2: Interactive Workflow

```python
from questfoundry.roles.scene_smith import SceneSmith
from questfoundry.roles.human_callback import default_human_callback

# Create interactive role
role = SceneSmith(
    provider=provider,
    human_callback=default_human_callback
)

# Ask questions during execution
tone = role.ask_choice(
    "What tone for this scene?",
    choices=["dark", "lighthearted", "suspenseful"]
)

add_description = role.ask_yes_no(
    "Add detailed environment description?"
)

if add_description:
    detail_level = role.ask_choice(
        "Detail level?",
        choices=["minimal", "moderate", "extensive"],
        default=1  # Default to "moderate"
    )
```

### Example 3: Combined Session + Interactive

```python
# Create session
session = RoleSession(role="scene_smith", workspace_path=Path("."))

# Create interactive role with session
role = SceneSmith(
    provider=provider,
    session=session,
    human_callback=my_custom_callback
)

# Role can ask questions AND track conversation
if role.ask_yes_no("Proceed with generation?"):
    result = role.execute_task(context)

    # Session contains full conversation
    print(f"Total messages: {len(session.conversation_history)}")

    # Save session for later
    session.save_to_file()
```

## API Summary

### RoleSession
```python
session = RoleSession(role, tu_context, workspace_path)
session.send_message(envelope)
session.add_to_history(envelope)
history = session.get_context_window(max_messages)
session.add_dormancy_signal("task.complete")
if session.should_dormant(): ...
data = session.archive()
path = session.save_to_file()
session = RoleSession.load_from_file(path)
```

### SessionManager
```python
manager = SessionManager(workspace_path)
session = manager.wake_role(role, tu_context)
manager.dormant_role(role)
session = manager.get_session(role)
roles = manager.get_active_roles()
if manager.is_role_awake(role): ...
archives = manager.archive_all()
manager.dormant_all()
needing = manager.get_sessions_needing_dormancy()
```

### HumanCallback
```python
role = Role(provider, human_callback=callback)
answer = role.ask_human(question, context, suggestions, artifacts)
result = role.ask_yes_no(question, default)
choice = role.ask_choice(question, choices, default)
```

---

**Ready for merge** - All quality gates passing. This implements the complete session management and interactive mode infrastructure for QuestFoundry, enabling conversation tracking and human-in-the-loop workflows while maintaining full backward compatibility.
