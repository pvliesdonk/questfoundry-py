# Epic-Based Development Guide

We organize development into Epics and Features for better tracking and organization.

## Structure

```
Epic (Branch)
├── Feature 1 (Commit)
├── Feature 2 (Commit)
├── Feature 3 (Commit)
└── Feature N (Commit)
```

## Epic Workflow

### 1. Start an Epic

Create a new branch from the base:

```bash
# Branch naming: claude/epic-<number>-<name>-<session-id>
git checkout -b claude/epic-02-layer-integration-011CUrRotNspY6xiSRLbKVfR
```

### 2. Implement Features

Each feature gets its own commit:

```bash
# Feature 1
git add <files>
git commit -m "feat(validators): implement schema validation"

# Feature 2
git add <files>
git commit -m "feat(validators): add detailed error reporting"

# Feature 3
git add <files>
git commit -m "test(validators): add comprehensive validation tests"
```

### 3. Validation Checklist

Before committing each feature:

```bash
✅ Tests pass:        uv run pytest
✅ Type check passes: uv run mypy src/
✅ Linting passes:    uv run ruff check .
✅ Code formatted:    uv run ruff format .
```

### 4. Push Epic

After completing all features:

```bash
git push -u origin claude/epic-02-layer-integration-<session-id>
```

## Example: Epic 1 Implementation

**Epic 1: Project Foundation**

Branch: `claude/epic-01-project-foundation-011CUrRotNspY6xiSRLbKVfR`

Commits:
1. `chore: update spec submodule to protocol-v0.2.1`
2. `feat: add MIT license and fix CI/CD workflows`
3. `feat: improve package structure and metadata`
4. `feat: update development tools and fix type checking`
5. `feat: implement schema and prompt bundling at build time`

Each commit is:
- ✅ Self-contained
- ✅ Follows conventional commits
- ✅ Passes all checks
- ✅ Has descriptive message

## Epic Planning

Before starting an epic:

1. **Review the plan** in `spec/06-libraries/IMPLEMENTATION_PLAN.md`
2. **List features** needed for the epic
3. **Define acceptance criteria** for each feature
4. **Check dependencies** on previous epics

### Example Epic 2 Plan

**Epic 2: Layer 3/4 Integration**

Dependencies: Epic 1 ✅

Features:
- ✅ 2.1: Schema Bundling (done in Epic 1.4)
- 2.2: Enhanced Schema Validation
- 2.3: Protocol Envelope Models
- 2.4: Protocol Conformance Validation

## Feature Implementation Pattern

For each feature:

### 1. Create/Modify Files

```bash
# Create new files
touch src/questfoundry/protocol/envelope.py
touch tests/protocol/test_envelope.py

# Edit existing files
# (using your editor)
```

### 2. Write Tests First (TDD)

```python
# tests/protocol/test_envelope.py
def test_envelope_creation():
    """Test creating a valid envelope"""
    envelope = Envelope(...)
    assert envelope.protocol.version == "0.2.1"
```

### 3. Implement Feature

```python
# src/questfoundry/protocol/envelope.py
class Envelope(BaseModel):
    """Protocol envelope"""
    protocol: Protocol
    sender: Sender
    # ...
```

### 4. Run Checks

```bash
uv run pytest -xvs tests/protocol/test_envelope.py
uv run mypy src/questfoundry/protocol/
uv run ruff check src/questfoundry/protocol/
```

### 5. Commit Feature

```bash
git add src/questfoundry/protocol/ tests/protocol/
git commit -m "feat(protocol): add envelope pydantic model

Implements Layer 4 protocol envelope structure with:
- Full Pydantic validation
- Type-safe field access
- JSON serialization/deserialization
- Examples from spec/04-protocol/EXAMPLES/"
```

## Multi-Feature Commit Guidelines

Sometimes features are tightly coupled:

```bash
# Option 1: Separate commits (preferred)
git commit -m "feat(protocol): add envelope model"
git commit -m "test(protocol): add envelope tests"

# Option 2: Combined commit (if tightly coupled)
git commit -m "feat(protocol): add envelope model with comprehensive tests"
```

## Epic Completion Checklist

Before pushing an epic:

- [ ] All features implemented
- [ ] All tests passing
- [ ] Type checking passing (mypy)
- [ ] Linting passing (ruff)
- [ ] Documentation updated
- [ ] PR description created (see below)
- [ ] CHANGELOG updated (if applicable)
- [ ] Conventional commit format on all commits

## Quality Gates (REQUIRED)

Every epic MUST pass these quality gates before being pushed:

### 1. Tests Must Pass
```bash
uv run pytest tests/
# Expected: All tests pass, skips are acceptable
```

### 2. Type Checking Must Pass (mypy)
```bash
uv run mypy src/questfoundry/<your-module>/
# Expected: No errors in new code
# Note: Pre-existing errors in other modules are acceptable
```

### 3. Linting Must Pass (ruff)
```bash
uv run ruff check src/questfoundry/<your-module>/ tests/<your-module>/
# Expected: No errors
# Use: uv run ruff check --fix . to auto-fix issues
```

### 4. Code Formatting (ruff format)
```bash
uv run ruff format src/questfoundry/<your-module>/ tests/<your-module>/
# All code should be formatted before commit
```

**IMPORTANT**: If any quality gate fails, fix the issues before pushing. Do not push failing code.

## Creating Epic Documentation

Every epic should have comprehensive documentation for the pull request.

### PR Description Template

Create a file in `.claude/pr-description-epic-<number>.md` with this structure:

````markdown
# Epic X: [Epic Name]

## Overview
Brief description of the epic and its goals.

## Features Implemented

### X.1: [Feature Name]
- Description of feature
- Key components
- Important methods/classes

**Key Methods:**
- `method_name()` - Description

### X.2: [Feature Name]
...

## Infrastructure Improvements
Any improvements to shared infrastructure (e.g., database API)

## Code Quality

### Validation Results
- ✅ **XXX tests passing, X skipped**
- ✅ **Ruff linting clean**
- ✅ **Mypy type checking clean**

### Standards Met
- ✅ Encapsulation (list specifics)
- ✅ Performance (list improvements)
- ✅ Security (list measures)
- ✅ Code Standards (list what was followed)

## Testing

### Test Coverage: XX new tests
- **test_module.py** - X tests for feature
- Summary of test categories

## API Examples

```python
# Example usage of new features
```

## File Changes

### New Files (X)
- List new files

### Modified Files (X)
- List modified files with reason

## Dependencies

- **Required**: Previous epics
- **Python**: Version requirements
- **External**: Any new dependencies

## Breaking Changes

List any breaking changes or "None"

## Future Enhancements

- List planned future work that builds on this

---

**Ready for merge** - All quality gates passing.
````

### Example

See `.claude/pr-description-epic-10.md` for a complete example.

### Using the Template

1. Copy the template above
2. Fill in all sections with epic-specific details
3. Save as `.claude/pr-description-epic-<number>.md`
4. Copy content to GitHub PR description when creating PR
5. Keep the file for documentation reference

**Tip**: Use four backticks (````) to fence code blocks within the markdown to preserve formatting.

## Branch Cleanup

After epic is merged:

```bash
# Delete local branch
git branch -D claude/epic-01-project-foundation-<session-id>

# Remote branch will be deleted after merge
```

## Tips

1. **Atomic commits**: Each commit should work independently
2. **Clear messages**: Future you will thank you
3. **Test coverage**: Add tests with features, not after
4. **Documentation**: Update docs in the same commit
5. **Review before push**: Check git log before pushing

## Common Mistakes to Avoid

❌ **Giant commits**: Don't bundle all features into one commit
❌ **WIP commits**: Complete each feature before committing
❌ **Breaking changes**: Test after each commit
❌ **Missing tests**: Always include tests with features
❌ **Poor messages**: Be descriptive and follow conventions
