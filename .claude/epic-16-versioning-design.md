# Epic 16.2 - Semantic Versioning Design

## Overview

Implement semantic versioning from conventional commits using commitizen and automated workflows.

## Design Decisions

### 1. Version Format: Semantic Versioning

**Format**: `MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`

**Examples**:
- `1.0.0` - First stable release
- `1.1.0` - New features added
- `1.1.5` - Bug fixes
- `2.0.0` - Breaking changes (MAJOR bump)
- `1.0.0-rc.1` - Release candidate
- `1.0.0-beta.2` - Beta version

**Rationale**:
- Industry standard
- Clear semantic meaning
- Tooling support
- User expectations

### 2. Version Bumping Strategy

```
Feature (feat) → MINOR version bump
  0.1.0 → 0.2.0

Bug Fix (fix) → PATCH version bump
  0.1.0 → 0.1.1

Breaking Change (BREAKING CHANGE in footer) → MAJOR version bump
  0.1.0 → 1.0.0

Documentation/Style/Tests → No version bump
```

### 3. Conventional Commits

**Standard**: Angular Convention

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Type Keywords**:

| Type | Bumps | Use Case |
|------|-------|----------|
| `feat` | MINOR | New feature |
| `fix` | PATCH | Bug fix |
| `docs` | NONE | Documentation only |
| `style` | NONE | Code formatting |
| `refactor` | NONE | Code reorganization |
| `perf` | PATCH | Performance improvement |
| `test` | NONE | Test addition/modification |
| `chore` | NONE | Build/dependency updates |
| `ci` | NONE | CI/CD updates |
| `revert` | PATCH | Revert previous commit |

**Scope** (Optional):
```
feat(providers): add Anthropic provider
fix(cache): handle expired entries
docs(api): clarify role parameters
```

**Breaking Change**:
```
feat(api)!: change role signature

BREAKING CHANGE: The execute method now requires
a context parameter instead of individual args.
```

Or:
```
feat!: simplified API

BREAKING CHANGE: Removed deprecated methods
```

### 4. Commit Examples

**Good Examples**:

```
feat(providers): add Anthropic Claude provider

Implements support for Anthropic's Claude models
as a text provider option. Includes rate limiting
and cost tracking.

Closes #42
```

```
fix(cache): handle concurrent writes safely

Use atomic file operations to ensure cache
consistency under concurrent access.

Fixes #38
```

```
docs: update configuration guide examples
```

```
refactor(state): simplify store interface

No API changes, internal reorganization for
better maintainability.
```

```
feat(api)!: change execute_task signature

BREAKING CHANGE: execute_task now takes
RoleContext instead of separate parameters
```

**Bad Examples**:

```
✗ made changes
✗ fixed bug
✗ updated stuff
✗ WIP: testing new feature
```

## Implementation Details

### commitizen Installation & Configuration

```toml
# pyproject.toml
[project.optional-dependencies]
release = [
    "commitizen>=3.12.0",
]

[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"  # Current version
version_files = [
    "src/questfoundry/version.py:__version__",
    "pyproject.toml:version",
]
update_changelog_on_bump = true
changelog_file = "CHANGELOG.md"
changelog_indent = "  "
tag_format = "v$version"
bump_message = "bump: version $current_version → $new_version"
annotated_tag = true
commit_parser = "^(?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\\((?P<scope>[^()\r\n]*)\\)|\\()?(?P<breaking>!)?(?:\\))?(?::\\s*)?(?P<message>.*)?"
parse_message_include_body = true
```

### commitizen Commands

```bash
# Show current version
cz version

# Validate a single commit
cz check --commit-msg-file=.git/COMMIT_EDITMSG

# Bump version and generate changelog
cz bump --dry-run  # Preview changes
cz bump             # Apply changes
cz bump --major     # Force major version
cz bump --minor     # Force minor version
cz bump --patch     # Force patch version

# Changelog only
cz changelog
```

### Pre-commit Hook Integration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.12.0
    hooks:
      - id: commitizen
        stages: [commit-msg]
        args: [--allow-abort, --allow-unconfigured-files]
```

**Installation**:
```bash
pip install pre-commit
pre-commit install

# Manually check commits
cz check --commit-msg-file=.git/COMMIT_EDITMSG
```

### Version File

```python
# src/questfoundry/version.py
"""QuestFoundry version information"""

__version__ = "0.1.0"
"""Current version of QuestFoundry"""

__version_info__ = (0, 1, 0)
"""Version tuple for comparisons"""

def get_version() -> str:
    """Get the current version string."""
    return __version__

def parse_version(version_string: str) -> tuple[int, int, int]:
    """Parse version string to tuple."""
    major, minor, patch = version_string.split('.')
    return (int(major), int(minor), int(patch))
```

**Usage in code**:
```python
from questfoundry import __version__

print(f"QuestFoundry v{__version__}")
```

### CHANGELOG Generation

**Format**: Keep a Changelog (keepachangelog.com)

```markdown
# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2025-11-20

### Added
- Feature: Per-role provider configuration
- Feature: Response caching with TTL
- Feature: Rate limiting and cost tracking
- API: New CacheConfig class for configuration

### Changed
- Enhanced ProviderConfig with role lookup methods
- Improved Role base class with role-specific settings

### Fixed
- Cache expiration handling in concurrent scenarios
- Rate limiter token bucket precision

### Documentation
- New guides for caching strategies
- Configuration examples for all providers

## [0.1.0] - 2025-10-15

### Added
- Initial release
- Complete Layer 6 implementation
- 14+ specialized agent roles
- Multi-step workflow orchestration
- Quality validation system
- Provider integration

[Unreleased]: https://github.com/pvliesdonk/questfoundry-py/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/pvliesdonk/questfoundry-py/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/pvliesdonk/questfoundry-py/releases/tag/v0.1.0
```

### Changelog Generation Template

commitizen auto-generates CHANGELOG based on commits:

```
# Commits are grouped by type:
# - feat → Added
# - fix → Fixed
# - refactor → Changed
# - perf → Changed
# - docs → Documentation
# - test → (not included)
# - chore → (not included)
```

## Git Workflow Integration

### For Developers

**When committing**:
```bash
# Normal development
git commit -m "feat(cache): add TTL support"

# commitizen will validate format
# If invalid, commit is rejected

# Using commitizen interactive mode (optional)
cz commit

# This prompts for type, scope, subject, body, footer
```

**Pre-commit check**:
```bash
# Automatically validates commit messages
# If format is invalid, commit fails

# To bypass (not recommended):
git commit --no-verify
```

### For Release Management

**Preparing a release**:
```bash
# 1. Ensure all commits follow conventional format
cz check --allowed-prefixes feat,fix,docs

# 2. Preview the version bump
cz bump --dry-run

# 3. Bump version and update CHANGELOG
cz bump

# 4. Workflow will build and publish
```

## Version Constraints & Compatibility

### Minimum Version

Project requires Python 3.11+:

```toml
# pyproject.toml
requires-python = ">=3.11"
```

### Dependency Compatibility

Track breaking changes in dependencies:

```
If dependency X.Y.Z is upgraded:
- Check if breaking changes
- Update CHANGELOG
- Consider version bump
```

## Testing Version Changes

```python
# test_version.py
import questfoundry

def test_version_string():
    """Version is valid semver"""
    from questfoundry.version import __version__
    parts = __version__.split('.')
    assert len(parts) >= 3
    assert all(p.isdigit() for p in parts[:3])

def test_version_accessible():
    """Version accessible from package"""
    assert hasattr(questfoundry, '__version__')
    assert isinstance(questfoundry.__version__, str)
```

## Migration Path

### From Unstable to Stable

```
0.1.0-alpha.1 → 0.1.0-beta.1 → 0.1.0-rc.1 → 0.1.0
```

Using commitizen:
```bash
cz bump --pre-release alpha
cz bump --pre-release beta
cz bump --pre-release rc
cz bump  # Remove pre-release, go to 0.1.0
```

## Best Practices

### DO:
- ✅ Use conventional format for all commits
- ✅ Include scope if relevant
- ✅ Mark breaking changes clearly
- ✅ Write descriptive commit messages
- ✅ Reference issues in footers
- ✅ Keep CHANGELOG updated

### DON'T:
- ❌ Mix multiple features in one commit
- ❌ Bypass commit message validation
- ❌ Skip CHANGELOG updates
- ❌ Use vague commit messages
- ❌ Commit directly to main

## Troubleshooting

**Commit rejected with "invalid commit message"**:
```bash
# Check what format is expected
cz commit --help

# Use interactive mode to get format right
cz commit
```

**Need to rewrite commit message**:
```bash
git commit --amend
# Will validate new message
```

**Already committed with wrong format**:
```bash
# Rebase and fix commits
git rebase -i HEAD~3
# Mark commits as reword, fix messages
```

## Integration with CI/CD

### Pre-merge validation (GitHub Actions):
```yaml
- name: Validate commits
  run: |
    pip install commitizen
    cz check --allow-unconfigured-files
```

### Post-merge release (manual trigger or tag-based):
```yaml
- name: Check conventional commits
  run: cz check --from v0.1.0 --to HEAD
```
