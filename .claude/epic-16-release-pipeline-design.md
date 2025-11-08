# Epic 16.3 - Release Pipeline Design

## Overview

Implement fully automated release workflow to GitHub and PyPI using GitHub Actions.

## Design Decisions

### 1. Trigger Strategy: Manual with Automation

**Decision**: Manual trigger via GitHub Actions workflow_dispatch

**Rationale**:
- Safe: Human reviews before release
- Controlled: Can choose version bump
- Flexible: Can run anytime
- Auditable: Full history in Actions tab

**Alternative considered**: Automatic on tag push
- Less control
- Harder to rollback
- Can release incomplete work

### 2. Release Checklist

Before triggering release:

```markdown
## Release Checklist

- [ ] All PRs merged and tests passing
- [ ] CHANGELOG reviewed
- [ ] No uncommitted changes
- [ ] Version bump correct
- [ ] Documentation complete
- [ ] No known issues in milestone
- [ ] Tested locally: `pytest tests/`
- [ ] Docs build: `mkdocs build`
```

### 3. Pipeline Stages

```
1. Validation
   ├─ Checkout code
   ├─ Setup Python environment
   ├─ Install dependencies
   └─ Run tests & linting

2. Version Bump
   ├─ commitizen bump version
   ├─ Update CHANGELOG
   └─ Create git tag

3. Build Package
   ├─ Build wheel
   ├─ Build sdist
   └─ Verify artifacts

4. Publish
   ├─ Publish to PyPI
   ├─ Create GitHub release
   └─ Deploy documentation

5. Notification
   ├─ GitHub release notes
   └─ Optional: Slack/Discord
```

## Implementation Details

### GitHub Actions Workflow Files

#### 1. Test Workflow (runs on every PR/push)

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint with ruff
        run: ruff check src tests

      - name: Type check with mypy
        run: mypy src/questfoundry

      - name: Run tests
        run: pytest tests/ -v --cov=src/questfoundry --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true
```

#### 2. Release Workflow (manual trigger)

```yaml
# .github/workflows/release.yml
name: Release

on:
  workflow_dispatch:
    inputs:
      bump:
        description: 'Version bump type'
        required: true
        default: 'minor'
        type: choice
        options:
          - major
          - minor
          - patch

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for commitizen
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[release]"
          pip install hatchling build

      - name: Configure git
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"

      - name: Run tests
        run: |
          pip install -e ".[dev]"
          pytest tests/ -v

      - name: Bump version
        id: bump
        run: |
          # Check for uncommitted changes
          if ! git diff-index --quiet HEAD --; then
            echo "❌ Uncommitted changes detected. Commit them first."
            exit 1
          fi

          # Bump version
          cz bump --${{ inputs.bump }} --changelog

          # Get new version
          VERSION=$(cz version)
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Build package
        run: python -m build

      - name: Verify build
        run: |
          python -m pip install dist/questfoundry_py-*.whl
          python -c "import questfoundry; print(f'Built {questfoundry.__version__}')"

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

      - name: Push changes to repository
        run: |
          git push --follow-tags

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          body_path: CHANGELOG.md
          draft: false
          prerelease: false
          tag_name: v${{ steps.bump.outputs.version }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Notify release
        run: |
          echo "✅ Released v${{ steps.bump.outputs.version }}"
          echo "📦 PyPI: https://pypi.org/project/questfoundry-py/${{ steps.bump.outputs.version }}/"
          echo "📖 Release: https://github.com/${{ github.repository }}/releases/tag/v${{ steps.bump.outputs.version }}"
```

#### 3. Documentation Deploy Workflow

```yaml
# .github/workflows/docs-deploy.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'src/questfoundry/**'
      - 'mkdocs.yml'
      - '.github/workflows/docs-deploy.yml'
  workflow_run:
    workflows: [Release]
    types: [completed]
  workflow_dispatch:

jobs:
  deploy:
    if: github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: pip

      - name: Install documentation dependencies
        run: |
          pip install -e ".[docs]"

      - name: Build documentation
        run: mkdocs build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
          cname: questfoundry.liesdonk.nl  # Optional custom domain
```

#### 4. Lint/Format Check (on PR)

```yaml
# .github/workflows/lint.yml
name: Lint & Format

on:
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install linting tools
        run: |
          pip install ruff mypy

      - name: Check code formatting
        run: ruff format --check src tests

      - name: Lint code
        run: ruff check src tests

      - name: Type check
        run: mypy src/questfoundry

      - name: Validate commit messages
        run: |
          pip install commitizen
          cz check --from origin/main
```

### PyPI Configuration

#### 1. Create PyPI API Token

1. Go to PyPI.org → Account Settings → API Tokens
2. Create new token with scope "Entire repository"
3. Copy token

#### 2. Add GitHub Secret

```
Settings → Secrets and Variables → Actions
New repository secret:
  Name: PYPI_API_TOKEN
  Value: pypi-AgEIcHlwaS5vcmc...
```

#### 3. Verify Configuration

```bash
# Test locally (with test PyPI)
twine upload --repository testpypi dist/*
```

### Build Configuration

#### Verify pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "questfoundry-py"
version = "0.1.0"  # Will be overridden by versioningit
dynamic = ["version"]
# ... rest of config

[tool.hatch.build.targets.wheel]
packages = ["src/questfoundry"]

[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/tests",
    "/README.md",
    "/LICENSE",
    "/CHANGELOG.md",
]
```

### Release Checklist Template

Create a GitHub release checklist:

```markdown
# Release v0.2.0

## Pre-Release Checklist

- [ ] All PRs merged to main
- [ ] Tests passing on main
- [ ] CHANGELOG updated with all changes
- [ ] Documentation up to date
- [ ] No known critical bugs
- [ ] Code reviewed by maintainer

## Release Steps

- [ ] Run `pytest tests/` locally
- [ ] Run `mkdocs build` locally
- [ ] Trigger release workflow
  - [ ] Select appropriate version bump
  - [ ] Verify workflow completes
- [ ] Check PyPI package
- [ ] Check GitHub release
- [ ] Check documentation deployed

## Post-Release

- [ ] Test installation: `pip install questfoundry-py==0.2.0`
- [ ] Verify version: `python -c "import questfoundry; print(questfoundry.__version__)"`
- [ ] Check changelog on GitHub
- [ ] Announce release (optional)
```

## Release Process Step-by-Step

### For Release Manager

#### 1. Prepare Release

```bash
# Clone/pull latest code
git clone https://github.com/pvliesdonk/questfoundry-py.git
cd questfoundry-py

# Ensure main branch is up to date
git checkout main
git pull origin main

# Verify tests pass locally
pytest tests/

# Build docs locally
mkdocs build
```

#### 2. Trigger Release

1. Go to GitHub repo → Actions tab
2. Select "Release" workflow
3. Click "Run workflow"
4. Choose version bump (major/minor/patch)
5. Click "Run workflow"

#### 3. Monitor Progress

1. Watch workflow execution
2. Verify each step completes
3. Check PyPI page updates
4. Verify GitHub release created

#### 4. Post-Release Verification

```bash
# Test installed package
pip install --upgrade questfoundry-py

# Verify version
python -c "from questfoundry import __version__; print(__version__)"

# Check documentation
# Visit https://questfoundry.liesdonk.nl/
```

## Version Numbering Examples

### Scenario: Bug fix for v0.1.0

```
Current: 0.1.0
Commits: fix(cache): handle expired entries
Action: Select "patch"
Result: 0.1.1
```

### Scenario: Add caching feature

```
Current: 0.1.0
Commits: feat(cache): implement response caching
         feat(rate): add rate limiting
         docs(guides): new caching guide
Action: Select "minor"
Result: 0.2.0
```

### Scenario: API redesign

```
Current: 0.1.0
Commits: feat(api)!: changed execute signature
         refactor!: removed deprecated methods
Action: Select "major"
Result: 1.0.0
```

## Rollback Procedure

If release has critical issue:

```bash
# Delete PyPI release (if still possible)
# https://pypi.org/project/questfoundry-py/

# Delete GitHub release
# GitHub → Releases → Delete release

# Delete tag
git push origin :refs/tags/v0.2.0

# Revert version commit
git revert <commit-hash>
git push origin main

# Fix issue and re-release
```

## Monitoring & Notifications

### Optional: Slack Notification

```yaml
- name: Notify Slack on release
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "🚀 questfoundry-py v${{ steps.bump.outputs.version }} released!",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*📦 QuestFoundry Released*\nVersion: v${{ steps.bump.outputs.version }}\nPyPI: https://pypi.org/project/questfoundry-py/"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Dry-Run / Testing Release

### Test PyPI

```bash
# Configure test PyPI
# Add to ~/.pypirc:
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgE...  # test PyPI token

# Upload to test PyPI
twine upload -r testpypi dist/*

# Install from test PyPI
pip install -i https://test.pypi.org/simple/ questfoundry-py
```

## Success Metrics

- ✅ Release takes <5 minutes from trigger
- ✅ Package available on PyPI immediately
- ✅ GitHub release created with artifacts
- ✅ Documentation deployed
- ✅ Version synced across all files
- ✅ Changelog updated
- ✅ Zero manual steps during release

## Troubleshooting

**Release workflow fails at build step**:
- Check `python -m build` works locally
- Verify pyproject.toml is correct
- Check all dependencies available

**PyPI upload fails**:
- Verify PYPI_API_TOKEN secret is set
- Check token has correct permissions
- Verify token not expired

**Git operations fail**:
- Ensure GITHUB_TOKEN has write permission
- Check SSH keys configured (if using SSH)

**Documentation deployment fails**:
- Check mkdocs.yml syntax
- Verify docs/ folder structure
- Check Python version compatibility
