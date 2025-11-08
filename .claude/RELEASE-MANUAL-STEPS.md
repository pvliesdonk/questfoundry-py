# Manual Release Steps for QuestFoundry-Py

This guide walks you through the manual steps needed to perform the first release (v0.1.0) of QuestFoundry-Py.

## Prerequisites

Ensure you have the following set up locally:
- ✅ All code committed and pushed to branch
- ✅ commitizen installed: `pip install commitizen`
- ✅ Git configured with your credentials
- ✅ uv package manager installed

## Step 1: Test the Release Locally

Before doing anything on GitHub, test the entire release process locally:

### 1a. Test commitizen bump locally

```bash
# This will show what commitizen will do
cd /home/user/questfoundry-py

# Install commitizen as a tool
uv tool install commitizen

# Check current version
cz version --project
```

This shows:
- Current version in pyproject.toml
- Ready for committing and bumping version

### 1b. Verify package builds

```bash
# Build the package locally
uv build

# Verify the dist/ directory contains:
# - questfoundry_py-0.1.0.tar.gz (source distribution)
# - questfoundry_py-0.1.0-py3-none-any.whl (wheel)
ls -lh dist/
```

## Step 2: Create PyPI Account & Token (First Time Only)

If you haven't already:

### 2a. Create PyPI account
- Go to https://pypi.org/account/register/
- Create an account and verify your email
- Enable two-factor authentication (recommended)

### 2b. Create API Token
1. Log in to PyPI
2. Go to Account Settings → API tokens
3. Click "Create Token for QuestFoundry-Py"
4. Scope: Entire Account (or specific project)
5. Save the token (you'll only see it once): `pypi-AgEIcH...`

### 2c. Create Test PyPI account (Optional but recommended)
1. Go to https://test.pypi.org/account/register/
2. Repeat token creation process
3. Save test token

## Step 3: Configure GitHub Secrets

### 3a. Add PyPI Token to GitHub
1. Go to GitHub repository settings
2. Secrets and variables → Actions secrets
3. Create new secret `PYPI_API_TOKEN`
4. Paste the PyPI token you created
5. Save

### 3b. Verify GitHub has write permissions
- Repository Settings → Actions → General
- Ensure "Read and write permissions" is selected for workflows

## Step 4: Test Release on Test PyPI (Recommended)

Before releasing to real PyPI, test on Test PyPI:

### 4a. Configure Test PyPI locally
```bash
# Create ~/.pypirc (or use GitHub environment variable)
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-test-pypi-token>
```

### 4b. Test publish locally
```bash
# Build package
uv build

# Publish to Test PyPI
python -m twine upload \
  --repository testpypi \
  --skip-existing \
  dist/*

# Verify at: https://test.pypi.org/project/questfoundry-py/
```

### 4c. Test install from Test PyPI
```bash
# Using uv
uv pip install \
  --index-url https://test.pypi.org/simple/ \
  questfoundry-py==0.1.0

# Verify it works
uv run python -c "from questfoundry import __version__; print(__version__)"
```

## Step 5: Enable GitHub Pages

### 5a. Configure repository for GitHub Pages
1. Go to GitHub repository settings
2. Pages section
3. Build and deployment:
   - Source: Deploy from a branch
   - Branch: gh-pages (or root if you prefer)

### 5b. Add CNAME file (Optional for custom domain)
If using custom domain questfoundry.liesdonk.nl:
1. Create file `docs/CNAME` with domain name
2. Commit and push
3. Configure DNS to point to GitHub Pages

## Step 6: Manual Release via GitHub Actions

When ready to release:

### 6a. Trigger release workflow
1. Go to GitHub: Actions → Release
2. Click "Run workflow"
3. Optional: Enter version (leave empty for auto-detect from commits)
4. Click green "Run workflow" button

### 6b. Monitor the release
- Watch the workflow execution
- Logs show:
  - Commitizen version bump
  - Changelog generation
  - Package building
  - PyPI publishing
  - GitHub Release creation

### 6c. Verify release
After workflow completes:

```bash
# Verify package on PyPI
pip install questfoundry-py==0.1.0

# Verify GitHub Release exists
# Go to https://github.com/pvliesdonk/questfoundry-py/releases

# Verify documentation deployed
# Visit https://questfoundry.liesdonk.nl (or your GitHub Pages URL)
```

## Step 7: Manual Alternative (If Workflow Fails)

If the automated workflow fails, you can release manually:

### 7a. Local version bump and changelog
```bash
# Make sure you're on main with all commits
git checkout main
git pull origin main

# Install commitizen if not already installed
uv tool install commitizen

# Bump version and generate changelog
cz bump --changelog

# This will:
# - Update src/questfoundry/version.py
# - Update pyproject.toml version
# - Create/update CHANGELOG.md
# - Create git tag (v0.1.0)
```

### 7b. Push changes and tags
```bash
git push
git push --tags
```

### 7c. Build package
```bash
uv build
```

### 7d. Publish to PyPI
```bash
# Ensure package is built
uv build

# Publish using uv (requires PYPI_API_TOKEN or .pypirc configured)
uv publish --skip-existing

# Or use twine if you prefer
uv tool install twine
twine upload dist/* --skip-existing
```

### 7e. Create GitHub Release manually
```bash
# Using GitHub CLI (if installed)
gh release create v0.1.0 \
  --title "Release 0.1.0" \
  --notes-file CHANGELOG.md \
  dist/*

# Or create via GitHub UI:
# 1. Go to Releases
# 2. Click "Draft a new release"
# 3. Choose tag v0.1.0
# 4. Copy content from CHANGELOG.md
# 5. Upload dist/ files
```

### 7f. Deploy docs manually
```bash
# Sync dependencies and build docs
uv sync --extra docs
uv run mkdocs build

# Deploy to GitHub Pages
# Either:
# - Push to main → auto-deploy via docs-deploy.yml workflow
# - Or manually push to gh-pages branch
git subtree push --prefix site origin gh-pages
```

## Step 8: Post-Release Verification

### 8a. Verify PyPI publication
```bash
# Check PyPI (using uv)
uv pip install --upgrade questfoundry-py

# Verify version
uv run python -c "from questfoundry import __version__; print(__version__)"
# Should print: 0.1.0
```

### 8b. Verify documentation
- Visit https://questfoundry.liesdonk.nl (or your GitHub Pages URL)
- Verify all pages load correctly
- Check search works
- Verify code examples render

### 8c. Verify GitHub Release
- Go to Releases page
- Verify v0.1.0 appears
- Verify artifacts (wheel, sdist) attached
- Verify changelog notes present

### 8d. Announce release
- Update any external documentation
- Announce in relevant channels
- Update social media if applicable

## Troubleshooting

### PyPI Publish Fails

**Error: "Invalid distribution"**
- Ensure dist/ directory has both .tar.gz and .whl files
- Verify long_description is valid markdown

**Error: "File already exists"**
- The `--skip-existing` flag handles this
- Or delete old dist/ files first

### Workflow Timeout

- GitHub Actions workflows have 6-hour timeout
- Most release workflows complete in <10 minutes
- If stuck, manually cancel and try manual steps

### Commit Message Validation Fails

- Ensure commits follow conventional format
- Use: `git commit -m "feat: add feature"` or `git commit -m "fix: bug fix"`
- commitizen can fix them: `commitizen modify COMMIT_HASH`

### Version Mismatch

- src/questfoundry/version.py and pyproject.toml must match
- Commitizen handles this automatically
- Verify both files have same version after bump

## Quick Reference

### First Release Checklist
- [ ] All code committed and pushed
- [ ] Tests passing locally
- [ ] Code quality passing (ruff, mypy)
- [ ] Documentation builds successfully
- [ ] PyPI account created with API token
- [ ] GitHub secret `PYPI_API_TOKEN` configured
- [ ] GitHub Pages enabled
- [ ] Release workflow triggered (or manual steps completed)
- [ ] Verify PyPI publication
- [ ] Verify GitHub Release created
- [ ] Verify documentation deployed

### Version Format
- Version: `MAJOR.MINOR.PATCH`
- First release: `0.1.0`
- Tag format: `v0.1.0` (with 'v' prefix)

### Important Files
- Version: `src/questfoundry/version.py`
- Package config: `pyproject.toml`
- Changelog: `CHANGELOG.md` (auto-generated)
- Commit config: `pyproject.toml` [tool.commitizen]

## Support

If you encounter issues during release:

1. Check the GitHub Actions workflow logs for detailed error messages
2. Review this guide's troubleshooting section
3. Check commitizen documentation: https://commitizen-tools.github.io/
4. Check PyPI documentation: https://pypi.org/help/
5. Check GitHub Actions documentation for workflow issues

---

**Ready for the first release?** Follow Steps 1-8 in order, starting with testing locally before triggering the real release workflow! 🚀
