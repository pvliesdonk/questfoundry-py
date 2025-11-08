# Epic 16: Documentation & Release Pipeline - Implementation Plan

**Status:** Preparation Phase
**Branch:** Part of Epic 16 preparation
**Estimated Effort:** 3-4 days
**Priority:** MEDIUM (Essential for public release)

## Overview

Epic 16 focuses on creating professional-grade documentation and automated release infrastructure. It consists of three interconnected sub-epics:

1. **16.1: Comprehensive Documentation** - MkDocs-based site with API docs, guides, examples
2. **16.2: Automated Versioning** - Semantic versioning from conventional commits
3. **16.3: Release Pipeline** - Automated publishing to GitHub and PyPI

---

## Sub-Epic 16.1: Comprehensive Documentation

### Goal
Create a professional documentation site using MkDocs with full API reference, guides, examples, and tutorials.

### Architecture

#### MkDocs Site Structure
```
docs/
├── mkdocs.yml                          # MkDocs configuration
├── index.md                            # Home page
├── getting-started.md                  # Quick start guide
├── installation.md                     # Installation instructions
├── api/
│   ├── index.md                        # API overview
│   ├── providers.md                    # Provider documentation
│   ├── roles.md                        # Role documentation
│   ├── loops.md                        # Loop documentation
│   ├── state.md                        # State management
│   ├── protocol.md                     # Protocol documentation
│   └── validation.md                   # Validation system
├── guides/
│   ├── configuration.md                # Configuration guide
│   ├── per-role-config.md              # Per-role config guide
│   ├── caching-strategy.md             # Caching best practices
│   ├── custom-roles.md                 # Creating custom roles
│   ├── custom-providers.md             # Creating custom providers
│   └── deployment.md                   # Deployment guide
├── examples/
│   ├── minimal-project.md              # Minimal example
│   ├── fantasy-adventure.md            # Fantasy game example
│   ├── sci-fi-world.md                 # Sci-fi example
│   └── code-examples.md                # Code snippets
├── changelog.md                        # Release notes
└── contributing.md                     # Contributing guide
```

#### MkDocs Configuration
```yaml
# mkdocs.yml
site_name: QuestFoundry-Py Documentation
site_url: https://questfoundry.liesdonk.nl/
repo_url: https://github.com/pvliesdonk/questfoundry-py
repo_name: questfoundry-py

theme:
  name: material
  features:
    - navigation.instant
    - navigation.tracking
    - content.code.copy
    - content.code.select
    - search.suggest
    - search.highlight

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          import_options:
            docstring_style: google
  - awesome-pages
  - callouts

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Installation: installation.md
  - API Reference:
    - Overview: api/index.md
    - Providers: api/providers.md
    - Roles: api/roles.md
    - Loops: api/loops.md
    - State: api/state.md
    - Protocol: api/protocol.md
    - Validation: api/validation.md
  - Guides:
    - Configuration: guides/configuration.md
    - Per-Role Config: guides/per-role-config.md
    - Caching Strategy: guides/caching-strategy.md
    - Custom Roles: guides/custom-roles.md
    - Custom Providers: guides/custom-providers.md
    - Deployment: guides/deployment.md
  - Examples: examples/code-examples.md
  - Changelog: changelog.md
  - Contributing: contributing.md
```

#### API Documentation Generation
- **Docstring Style**: Google-style docstrings in all modules
- **Code Examples**: Include examples in docstrings
- **Type Hints**: Leverage Python type hints for documentation
- **mkdocstrings Plugin**: Auto-generate API docs from code

#### Key Documentation Files

**index.md** - Home page with:
- Feature overview
- Quick start snippet
- Links to guides
- Community information

**getting-started.md** - New user guide with:
- Installation steps
- First project creation
- Running first workflow
- Understanding output

**guides/configuration.md** - Configuration guide with:
- Config file structure
- Provider setup
- Role configuration
- Caching and rate limiting

**guides/per-role-config.md** - Per-role configuration (from Epic 15):
- When to use role-specific config
- Examples (cost optimization, specialized models)
- Common patterns

**examples/code-examples.md** - Code snippets for:
- Creating a project
- Running loops
- Custom providers
- Error handling

### Implementation Files

```
docs/mkdocs.yml
docs/index.md
docs/getting-started.md
docs/installation.md
docs/changelog.md
docs/contributing.md
docs/api/index.md
docs/api/providers.md
docs/api/roles.md
docs/api/loops.md
docs/api/state.md
docs/api/protocol.md
docs/api/validation.md
docs/guides/configuration.md
docs/guides/per-role-config.md
docs/guides/caching-strategy.md
docs/guides/custom-roles.md
docs/guides/custom-providers.md
docs/guides/deployment.md
docs/examples/code-examples.md
.github/workflows/docs-deploy.yml
```

### Configuration

```yaml
# pyproject.toml additions
[project.optional-dependencies]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "mkdocstrings[python]>=0.23.0",
    "mkdocs-awesome-pages-plugin>=2.9.0",
    "pymdown-extensions>=10.0",
]
```

### Testing Strategy

- Documentation builds without errors
- All code examples are valid Python
- Links are not broken
- API docs generated from code
- Images render correctly

### Success Criteria

- ✅ Complete API reference auto-generated
- ✅ Getting started guide works end-to-end
- ✅ All configuration options documented
- ✅ Examples are runnable
- ✅ Deployed to GitHub Pages or custom domain

---

## Sub-Epic 16.2: Automated Versioning

### Goal
Implement semantic versioning from conventional commits using commitizen and GitHub workflows.

### Architecture

#### Conventional Commits Schema

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: New feature (MINOR version bump)
- `fix`: Bug fix (PATCH version bump)
- `docs`: Documentation changes (no version bump)
- `style`: Code style changes (no version bump)
- `refactor`: Code refactoring (no version bump)
- `perf`: Performance improvements (PATCH version bump)
- `test`: Test changes (no version bump)
- `chore`: Build/tool changes (no version bump)
- `ci`: CI/CD changes (no version bump)
- `revert`: Revert previous commit (PATCH version bump)

**Breaking Changes**: Use `BREAKING CHANGE:` in footer → MAJOR version bump

#### Version Management Tools

1. **Current**: `versioningit` (dynamic versioning from git)
   - Already configured in pyproject.toml
   - Versions from git tags

2. **Enhance**: `commitizen` - Conventional commit tooling
   - Validate commit messages
   - Generate changelog
   - Create version tags

#### commitizen Configuration

```toml
# pyproject.toml additions
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
version_files = [
    "src/questfoundry/version.py:__version__",
    "pyproject.toml:version"
]
update_changelog_on_bump = true
changelog_file = "CHANGELOG.md"
changelog_indent = "  "
tag_format = "v$version"
bump_message = "bump: version $current_version → $new_version"
annotated_tag = true
```

#### Version Scheme

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Example: 1.2.3-rc.1+20231015
  - 1 = Major (breaking changes)
  - 2 = Minor (new features)
  - 3 = Patch (bug fixes)
  - rc.1 = Release candidate
  - 20231015 = Build date
```

#### Implementation

```python
# src/questfoundry/version.py
__version__ = "0.1.0"
__version_info__ = (0, 1, 0)

def get_version() -> str:
    """Get version string"""
    return __version__
```

### Implementation Files

```
src/questfoundry/version.py               # Version constant
pyproject.toml                            # commitizen config
.pre-commit-config.yaml                  # Pre-commit hooks
CHANGELOG.md                             # Auto-generated changelog
```

### Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.12.0
    hooks:
      - id: commitizen
        stages: [commit-msg]
```

### Testing Strategy

- Commits validated against conventional format
- Version bumps correct based on commits
- Changelog generated correctly
- Version accessible from code

### Success Criteria

- ✅ All commits follow conventional format
- ✅ Version automatically bumped on release
- ✅ Changelog auto-generated
- ✅ Version accessible in code

---

## Sub-Epic 16.3: Release Pipeline

### Goal
Automated release workflow to GitHub and PyPI using GitHub Actions.

### Architecture

#### Release Workflow

```
1. Developer pushes commits
   ↓
2. GitHub Actions runs tests/linting
   ↓
3. PR review and merge to main
   ↓
4. Manual trigger: Run release workflow
   ↓
5. commitizen creates version tag and changelog
   ↓
6. Build package (wheel + sdist)
   ↓
7. Publish to PyPI
   ↓
8. Create GitHub release
   ↓
9. Deploy documentation
```

#### GitHub Actions Workflows

```
.github/workflows/
├── test.yml                  # Run tests on PR/push
├── release.yml               # Manual release trigger
├── docs-deploy.yml           # Deploy docs on release
└── publish-pypi.yml          # Publish to PyPI
```

#### Release Workflow File

```yaml
# .github/workflows/release.yml
name: Release

on:
  workflow_dispatch:  # Manual trigger
    inputs:
      bump:
        description: 'Version bump type'
        required: true
        default: 'patch'
        type: choice
        options:
          - major
          - minor
          - patch

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for commitizen
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install hatchling commitizen build

      - name: Configure git
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"

      - name: Bump version
        run: |
          cz bump --${{ inputs.bump }} --changelog --changelog-to-stdout > CHANGELOG_TMP.txt

      - name: Build package
        run: |
          python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

      - name: Push changes
        run: |
          git push
          git push --tags

      - name: Create GitHub release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          body_path: CHANGELOG_TMP.txt
          draft: false
          prerelease: false
```

#### PyPI Configuration

```toml
# pyproject.toml (already configured)
[build-system]
requires = ["hatchling", "versioningit"]
build-backend = "hatchling.build"

[project]
name = "questfoundry-py"
description = "Python library for QuestFoundry"
# ... rest of config
```

#### Environment Setup

Required secrets in GitHub:
- `PYPI_API_TOKEN` - PyPI API token for publishing
- `GITHUB_TOKEN` - Auto-provided by GitHub

### Implementation Files

```
.github/workflows/test.yml
.github/workflows/release.yml
.github/workflows/docs-deploy.yml
.github/workflows/publish-pypi.yml
.release-notes-config.yml
CHANGELOG.md (template)
```

### Pre-release Checklist

Before releasing:
1. ✅ All tests passing
2. ✅ Code coverage maintained
3. ✅ Documentation updated
4. ✅ CHANGELOG reviewed
5. ✅ Version number correct
6. ✅ No uncommitted changes

### Testing Strategy

- Test workflow runs on pull requests
- Can test release workflow manually
- Verify package publishes to test PyPI first
- Verify documentation deploys

### Success Criteria

- ✅ Automated tests on all PRs
- ✅ Package published to PyPI on release
- ✅ GitHub release created with artifacts
- ✅ Documentation deployed
- ✅ Version synced across codebase

---

## Implementation Sequencing

### Phase 1: Documentation Setup (Day 1)
1. Install MkDocs and plugins
2. Create mkdocs.yml configuration
3. Set up directory structure
4. Create home page and getting started

### Phase 2: API Documentation (Day 1-2)
1. Add docstrings to all public modules
2. Configure mkdocstrings
3. Generate API reference pages
4. Review and polish docs

### Phase 3: Guides and Examples (Day 2-3)
1. Write configuration guide
2. Write custom provider/role guides
3. Create code examples
4. Test all examples work

### Phase 4: Versioning Setup (Day 3)
1. Install commitizen
2. Configure pyproject.toml
3. Set up pre-commit hooks
4. Validate commits

### Phase 5: Release Pipeline (Day 3-4)
1. Create GitHub Actions workflows
2. Set up PyPI credentials
3. Test release workflow
4. Deploy documentation site

---

## Acceptance Criteria Summary

### 16.1: Documentation
- ✅ MkDocs site builds without errors
- ✅ API reference auto-generated from docstrings
- ✅ All guides are clear and actionable
- ✅ All code examples work
- ✅ Site deployed and accessible
- ✅ Mobile-responsive

### 16.2: Versioning
- ✅ All commits follow conventional format
- ✅ Version bumps correct (major/minor/patch)
- ✅ Changelog auto-generated
- ✅ Version accessible in code
- ✅ Pre-commit hooks validate

### 16.3: Release Pipeline
- ✅ Tests run on all PRs
- ✅ Package builds successfully
- ✅ Published to PyPI on release
- ✅ GitHub release created
- ✅ Documentation deployed
- ✅ Can be triggered manually

---

## Dependencies & Prerequisites

### External Dependencies
- MkDocs and plugins (mkdocs-material, mkdocstrings)
- commitizen
- GitHub Actions
- PyPI account with API token

### Knowledge Requirements
- Markdown documentation writing
- YAML configuration
- GitHub Actions workflow syntax
- Python packaging

### Prerequisites
- pyproject.toml already configured
- GitHub repository set up
- PyPI account created
- Domain/GitHub Pages for docs (optional)

---

## Risk & Mitigation

| Risk | Mitigation |
|------|-----------|
| Documentation becomes outdated | Auto-generate API docs, CI check for broken links |
| Versioning mistakes | Pre-commit validation, test on test PyPI first |
| Release failures | Test workflows manually before using |
| Breaking changes not documented | Review CHANGELOG before release |
| PyPI credentials exposed | Use GitHub secrets, rotate tokens regularly |

---

## Success Metrics

1. **Documentation**: >90% of API documented, all guides complete
2. **Versioning**: 100% commits follow conventional format
3. **Releases**: Fully automated, zero-touch releases
4. **Deployment**: Docs deploy on every release
5. **Quality**: No broken links, all examples work

---

## Next Steps

1. Set up MkDocs environment
2. Configure project structure
3. Add comprehensive docstrings to code
4. Configure commitizen
5. Create GitHub Actions workflows
6. Test release process end-to-end
7. Deploy documentation site

---

## Timeline

```
Day 1:
  - MkDocs setup
  - Directory structure
  - Home/getting started pages
  - API docstring audit

Day 1-2:
  - Add docstrings to all modules
  - Configure mkdocstrings
  - Generate API docs
  - Write guides

Day 2-3:
  - Code examples
  - Configuration guide
  - Custom provider guide
  - Custom role guide

Day 3:
  - commitizen setup
  - GitHub Actions workflows
  - PyPI setup

Day 4:
  - Testing and refinement
  - Documentation site deployment
  - Release workflow validation
```
