# Conventional Commits Quick Reference

## Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

## Common Types

| Type | Description | Version Bump |
|------|-------------|--------------|
| `feat` | New feature | Minor (0.x.0) |
| `fix` | Bug fix | Patch (0.0.x) |
| `docs` | Documentation | None |
| `style` | Formatting | None |
| `refactor` | Code restructuring | None |
| `perf` | Performance | Patch |
| `test` | Tests | None |
| `chore` | Maintenance | None |
| `ci` | CI/CD | None |

## Breaking Changes

Add `!` after type or `BREAKING CHANGE:` in footer:

```bash
feat(protocol)!: change envelope structure

BREAKING CHANGE: Envelope.context is now required
```

## Examples for This Project

```bash
# Adding new functionality
feat(models): add HookCard pydantic model
feat(validators): implement protocol conformance checking
feat(state): add SQLite workspace store

# Fixing bugs
fix(resources): handle missing prompt files
fix(validators): correct schema validation error messages
fix(protocol): fix envelope serialization for datetime

# Refactoring
refactor(models): simplify artifact base class
refactor(validators): extract validation result handling

# Tests
test(protocol): add envelope parsing tests
test(validators): add conformance validation tests

# Documentation
docs: update installation instructions
docs(protocol): document envelope structure

# Maintenance
chore(deps): update pydantic to v2.12.0
chore: update spec submodule to protocol-v0.2.1

# CI/CD
ci: add package build workflow
ci: fix workflow submodule checkout
```

## Rules

1. **Imperative mood**: "add" not "added" or "adds"
2. **Lowercase**: subject line should be lowercase
3. **No period**: don't end subject with a period
4. **Max 72 chars**: keep subject line concise
5. **Body optional**: use for complex changes
6. **Reference issues**: `Closes #123` in footer

## Multi-line Example

```bash
feat(state): implement workspace hot/cold management

- Add FileStore for hot workspace
- Add SQLiteStore for cold storage
- Implement Workspace class coordinating both
- Add promotion logic from hot to cold

This allows artifacts to move through the workflow from
hot development to cold production state.

Refs: #42
```

## Quick Tips

- **One commit = one logical change**
- **Separate features = separate commits**
- **Tests in same commit** as the code they test
- **Breaking changes** must be clearly marked
- **Scope helps** with changelog generation

## Bad Examples (Don't Do This)

```bash
❌ "fixed stuff"
❌ "WIP"
❌ "asdf"
❌ "Updated files"
❌ "feat: Added feature"  # (use lowercase, no past tense)
❌ "feat(models) Add model"  # (missing colon)
```

## Good Examples

```bash
✅ feat(models): add envelope pydantic model
✅ fix(validators): handle empty schema gracefully
✅ test(protocol): add conformance validation tests
✅ docs: update README with quick start guide
✅ chore(deps): update dependencies
```
