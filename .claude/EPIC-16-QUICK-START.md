# Epic 16 - Documentation & Release Pipeline - Quick Start

## 📋 What's Included

4 detailed design documents for building professional documentation and release infrastructure:

1. **epic-16-implementation-plan.md** - Overall roadmap (3 sub-epics, 4 days)
2. **epic-16-documentation-design.md** - MkDocs site architecture
3. **epic-16-versioning-design.md** - Semantic versioning with commitizen
4. **epic-16-release-pipeline-design.md** - GitHub Actions + PyPI publishing

Plus this summary and quick start guide.

## 🎯 Epic 16 Overview

Three interconnected components for professional releases:

| Component | Purpose | Tools |
|-----------|---------|-------|
| **16.1: Documentation** | Professional docs site | MkDocs + Material theme |
| **16.2: Versioning** | Semantic versioning from commits | commitizen + conventional commits |
| **16.3: Release Pipeline** | Automated publishing | GitHub Actions + PyPI |

## 🚀 Implementation Path (4 Days)

### Day 1: Documentation Setup
```bash
# Install MkDocs
pip install mkdocs mkdocs-material mkdocstrings[python]

# Create configuration
# mkdocs.yml (see design doc for full config)

# Create structure
mkdir -p docs/{api,guides,examples}

# Serve locally
mkdocs serve
```

### Day 1-2: API Documentation
```python
# Add docstrings to all public modules
def generate_text(self, prompt: str, **kwargs) -> str:
    """Generate text from prompt.

    Args:
        prompt: Input prompt
        **kwargs: Additional parameters

    Returns:
        Generated text

    Example:
        ```python
        result = provider.generate_text("hello")
        ```
    """
```

### Day 2-3: Guides & Examples
```markdown
# Create documentation files
docs/
├── getting-started.md       # New user guide
├── guides/configuration.md  # Configuration guide
├── guides/custom-roles.md   # Custom role guide
└── examples/code-examples.md
```

### Day 3: Versioning Setup
```bash
# Install commitizen
pip install commitizen

# Configure
# Add [tool.commitizen] to pyproject.toml

# Create version file
# src/questfoundry/version.py

# Set up pre-commit
pip install pre-commit
pre-commit install
```

### Day 4: Release Pipeline
```bash
# Create GitHub Actions workflows
# .github/workflows/
#   ├── test.yml
#   ├── release.yml
#   ├── docs-deploy.yml
#   └── lint.yml

# Set PyPI credentials in GitHub
# Settings → Secrets → PYPI_API_TOKEN

# Test release workflow
```

## 🔧 Key Implementation Details

### Conventional Commits

```
feat(scope): description      # MINOR version bump
fix(scope): description       # PATCH version bump
docs: description             # No version bump
feat!: breaking change        # MAJOR version bump
```

**Examples**:
```
✅ feat(cache): implement response caching
✅ fix(rate-limiter): handle concurrent access
✅ docs: update configuration guide
✅ feat(api)!: changed execute signature
```

### MkDocs Configuration

```yaml
# mkdocs.yml
site_name: QuestFoundry-Py
theme:
  name: material
  palette:
    - scheme: default
    - scheme: slate

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          docstring_style: google
```

### GitHub Actions Release

Manual trigger in Actions tab:
```
GitHub → Actions → Release → Run workflow
  ↓ Select version bump
  ↓ Runs tests
  ↓ Bumps version with commitizen
  ↓ Builds wheel + sdist
  ↓ Publishes to PyPI
  ↓ Creates GitHub release
  ↓ Deploys documentation
```

## 📊 Success Metrics

**Documentation**
- ✓ API reference auto-generated
- ✓ All guides complete
- ✓ Code examples work
- ✓ Mobile responsive

**Versioning**
- ✓ All commits follow conventional format
- ✓ Version bumps correct
- ✓ Changelog auto-generated
- ✓ Pre-commit hooks validate

**Release Pipeline**
- ✓ Automated tests on PR
- ✓ Package published to PyPI
- ✓ GitHub release created
- ✓ Docs deployed

## 🧪 Testing Commands

```bash
# Test documentation builds
mkdocs build
mkdocs serve

# Test versioning
cz bump --dry-run
cz check --from main

# Test package
python -m build
pip install dist/questfoundry_py-*.whl
```

## 📝 Commit Examples

```bash
# Good commits
git commit -m "feat(cache): add TTL support"
git commit -m "fix(rate-limiter): thread safety"
git commit -m "docs: update getting started"
git commit -m "feat(api)!: new execute signature"

# Will be rejected
git commit -m "fixed bug"
git commit -m "made changes"
```

## 🔐 GitHub Setup

### Secrets Required

```
Settings → Secrets and Variables → Actions

PYPI_API_TOKEN
  → Get from PyPI.org → Account → API Tokens
  → Scope: Entire repository
  → Paste token value

GITHUB_TOKEN
  → Auto-provided by GitHub
```

### Workflows Needed

```
.github/workflows/
├── test.yml           # Runs on PR/push to main
├── release.yml        # Manual workflow_dispatch
├── docs-deploy.yml    # Auto on release
└── lint.yml           # Runs on PR
```

## 🎓 File Organization

### Documentation Files

```
docs/
├── mkdocs.yml                 # Configuration
├── index.md                   # Home
├── getting-started.md         # Quick start
├── installation.md
├── changelog.md               # Auto-updated
├── api/
│   ├── index.md
│   ├── providers.md
│   ├── roles.md
│   ├── loops.md
│   ├── state.md
│   └── protocol.md
└── guides/
    ├── configuration.md
    ├── per-role-config.md
    ├── custom-roles.md
    └── custom-providers.md
```

### Version Management

```
src/questfoundry/version.py
  → __version__ = "0.1.0"
  → get_version()

pyproject.toml
  → [tool.commitizen] config
  → version_files reference
```

## 💡 Pro Tips

1. **Start with docstrings**: Add Google-style docstrings first, docs auto-generate
2. **Pre-commit validation**: Catches bad commits before push
3. **Test PyPI first**: Test release workflow on test.pypi.org before main
4. **Dry-run release**: Use `cz bump --dry-run` to preview changes
5. **Version in one place**: version.py is source of truth

## ⚠️ Common Pitfalls

- ❌ Don't skip docstrings (API docs won't generate)
- ❌ Don't use bad commit messages (pre-commit will reject)
- ❌ Don't release without running tests locally
- ❌ Don't hardcode version (use version.py)
- ❌ Don't forget CHANGELOG before releasing

## 📚 Reference Documents

| Document | Contains |
|----------|----------|
| epic-16-implementation-plan.md | Complete overview & sequencing |
| epic-16-documentation-design.md | MkDocs architecture & file structure |
| epic-16-versioning-design.md | commitizen & semantic versioning |
| epic-16-release-pipeline-design.md | GitHub Actions & PyPI setup |

## 🚀 Getting Started

1. Read this quick start guide
2. Skim `epic-16-implementation-plan.md`
3. Review specific design doc for current phase
4. Install required tools
5. Follow step-by-step instructions in design doc
6. Test locally before publishing

## ✅ Checklist Before First Release

- [ ] All docstrings added to public APIs
- [ ] Documentation site builds locally
- [ ] All links work
- [ ] Code examples are valid Python
- [ ] Tests passing locally
- [ ] Commit messages follow conventional format
- [ ] version.py up to date
- [ ] PyPI API token configured in GitHub
- [ ] Release workflow tested on test PyPI

## 🔗 Quick Links

- **MkDocs**: https://www.mkdocs.org/
- **Material Theme**: https://squidfunk.github.io/mkdocs-material/
- **commitizen**: https://commitizen-tools.github.io/commitizen/
- **Conventional Commits**: https://www.conventionalcommits.org/
- **Semantic Versioning**: https://semver.org/

## Questions?

Check the detailed design documents in `.claude/` for:
- Specific implementation steps
- Configuration examples
- Workflow definitions
- Troubleshooting guides
- All API details

---

**Ready to implement professional documentation and releases!** 🎯

**Questions?** → Check detailed design docs
**Phase stuck?** → Review corresponding design document
**Workflows failing?** → See release pipeline design for troubleshooting
