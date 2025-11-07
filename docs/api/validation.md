# Validation API Reference

The `questfoundry.validation` module provides quality assurance through quality bars and the Gatekeeper system. Quality bars are validation checks that content must pass before being promoted from hot workspace to cold storage.

## Overview

The validation module implements the **8 Quality Bars** framework:

1. **Integrity** - References resolve, no dead ends
2. **Reachability** - Keystones and goals are reachable
3. **Style** - Voice and register are consistent
4. **Gateways** - Conditions are diegetic (in-world)
5. **Nonlinearity** - Hubs and loops are meaningful
6. **Determinism** - Assets are reproducible
7. **Presentation** - No spoilers/internals on player surfaces
8. **Spoiler Hygiene** - PN (Player Narrator) boundaries maintained

## Quick Start

```python
from questfoundry.validation import Gatekeeper
from questfoundry.models import Artifact

# Create artifacts to validate
hooks = [
    Artifact(
        type="hook_card",
        data={
            "hook_id": "HOOK-001",
            "title": "Dragon's Awakening",
            "concept": "Ancient dragon stirs"
        }
    ),
    # ... more artifacts
]

# Run gatecheck
gatekeeper = Gatekeeper()
report = gatekeeper.run_gatecheck(hooks)

# Check results
if report.passed:
    print("✓ All quality bars passed - safe to promote to cold")
else:
    print(f"✗ {len(report.blockers)} blockers found")
    for bar_name, issue in report.blockers:
        print(f"  [{bar_name}] {issue.message}")

# Generate artifact for audit trail
gatecheck_artifact = report.to_artifact()
```

## Gatekeeper

Main interface for running quality bar validation.

### Constructor

```python
Gatekeeper(
    bars: list[str] | None = None,
    strict: bool = True
)
```

**Parameters:**
- `bars`: List of bar names to run (default: all 8 bars)
- `strict`: If True, warnings also block merge (default: True)

**Available Bar Names:**
- `"integrity"` - Integrity Bar
- `"reachability"` - Reachability Bar
- `"style"` - Style Bar
- `"gateways"` - Gateways Bar
- `"nonlinearity"` - Nonlinearity Bar
- `"determinism"` - Determinism Bar
- `"presentation"` - Presentation Bar
- `"spoiler_hygiene"` - Spoiler Hygiene Bar

**Example:**
```python
# Run all bars (default)
gk = Gatekeeper()

# Run specific bars only
gk = Gatekeeper(bars=["integrity", "reachability", "style"])

# Allow warnings (non-strict mode)
gk = Gatekeeper(strict=False)
```

### Methods

#### `run_gatecheck()`

```python
def run_gatecheck(
    artifacts: list[Artifact],
    **metadata: Any
) -> GatecheckReport
```

Run full gatecheck on artifacts.

**Parameters:**
- `artifacts`: List of artifacts to validate
- `**metadata`: Additional metadata to include in report (e.g., `tu_id`, `snapshot_id`)

**Returns:** GatecheckReport with results from all bars

**Example:**
```python
from datetime import datetime

artifacts = [...]  # Your artifacts

report = gk.run_gatecheck(
    artifacts,
    tu_id="TU-2025-11-07-SR01",
    timestamp=datetime.now().isoformat(),
    author="Alice"
)

print(f"Passed: {report.passed}")
print(f"Merge Safe: {report.merge_safe}")
print(f"Blockers: {len(report.blockers)}")
print(f"Warnings: {len(report.warnings)}")
```

## GatecheckReport

Complete gatecheck report with results from all quality bars.

### Attributes

- `passed` (bool): Whether all bars passed (no blockers)
- `merge_safe` (bool): Whether content can be merged to Cold
- `bar_results` (dict[str, QualityBarResult]): Results from each quality bar
- `summary` (str): Human-readable summary
- `metadata` (dict[str, Any]): Additional context

### Properties

#### `all_issues`

```python
@property
def all_issues() -> list[tuple[str, QualityIssue]]
```

Get all issues across all bars.

**Returns:** List of (bar_name, issue) tuples

**Example:**
```python
for bar_name, issue in report.all_issues:
    print(f"[{bar_name}] {issue.severity}: {issue.message}")
```

#### `blockers`

```python
@property
def blockers() -> list[tuple[str, QualityIssue]]
```

Get all blocker issues (must fix before merge).

**Returns:** List of (bar_name, issue) tuples

**Example:**
```python
if report.blockers:
    print("Blockers that must be fixed:")
    for bar_name, issue in report.blockers:
        print(f"  [{bar_name}] {issue.message}")
        if issue.fix:
            print(f"    Fix: {issue.fix}")
```

#### `warnings`

```python
@property
def warnings() -> list[tuple[str, QualityIssue]]
```

Get all warning issues (should review).

**Returns:** List of (bar_name, issue) tuples

**Example:**
```python
if report.warnings:
    print("Warnings for review:")
    for bar_name, issue in report.warnings:
        print(f"  [{bar_name}] {issue.message}")
```

### Methods

#### `to_artifact()`

```python
def to_artifact() -> Artifact
```

Convert report to gatecheck_report artifact for storage.

**Returns:** Artifact of type "gatecheck_report"

**Example:**
```python
# Store gatecheck report in project
report_artifact = report.to_artifact()
workspace.save_hot_artifact(report_artifact)
```

## Quality Bar Types

All quality bars implement the `QualityBar` interface.

### QualityBar (Abstract Base Class)

Base class for all quality bar validators.

**Abstract Properties:**
- `name` (str): Unique name of this quality bar
- `description` (str): Short description of what this bar validates

**Abstract Method:**

#### `validate()`

```python
def validate(artifacts: list[Artifact]) -> QualityBarResult
```

Validate artifacts against this quality bar.

**Parameters:**
- `artifacts`: List of artifacts to validate

**Returns:** QualityBarResult with pass/fail and issues found

### Available Quality Bars

#### IntegrityBar

Validates that references resolve correctly and there are no dead ends.

**Checks:**
- All referenced artifact IDs exist
- No dangling references
- Cross-references are valid
- Required fields are present

**Example:**
```python
from questfoundry.validation import IntegrityBar

bar = IntegrityBar()
result = bar.validate(artifacts)

if not result.passed:
    for issue in result.blockers:
        print(f"Integrity issue: {issue.message}")
```

#### ReachabilityBar

Validates that keystones and goals are reachable through the narrative.

**Checks:**
- All keystones can be reached
- No unreachable content branches
- Paths to goals exist
- No orphaned scenes

#### StyleBar

Validates voice and register consistency.

**Checks:**
- Consistent tone across content
- Register (formal/informal) matches guidelines
- Style guide adherence
- Voice consistency

#### GatewaysBar

Validates that conditions and gates are diegetic (in-world).

**Checks:**
- Branching conditions make narrative sense
- No metagaming requirements
- Conditions are player-understandable
- Gates feel natural

#### NonlinearityBar

Validates that hubs and loops are meaningful.

**Checks:**
- Non-linear sections add value
- Loops have purpose (not just filler)
- Hubs provide meaningful choices
- Paths converge sensibly

#### DeterminismBar

Validates that assets are reproducible.

**Checks:**
- Generation parameters are captured
- Assets can be regenerated
- Seeds/prompts are stored
- Dependencies are documented

#### PresentationBar

Validates that no spoilers or internals leak to player surfaces.

**Checks:**
- No GM-only information visible
- No internal IDs exposed
- No development notes in output
- Clean player-facing content

#### SpoilerHygieneBar

Validates PN (Player Narrator) boundaries are maintained.

**Checks:**
- Player-safe flag correctly set
- Spoiler policy enforced
- PN boundary not violated
- Safe content properly marked

## QualityBarResult

Result of a quality bar check.

### Attributes

- `bar_name` (str): Name of the quality bar
- `passed` (bool): Whether the bar passed (no blockers)
- `issues` (list[QualityIssue]): List of issues found
- `metadata` (dict[str, Any]): Additional context about the check

### Properties

#### `blockers`

```python
@property
def blockers() -> list[QualityIssue]
```

Get only blocker issues.

#### `warnings`

```python
@property
def warnings() -> list[QualityIssue]
```

Get only warning issues.

#### `info`

```python
@property
def info() -> list[QualityIssue]
```

Get only info issues.

**Example:**
```python
result = bar.validate(artifacts)

print(f"Blockers: {len(result.blockers)}")
print(f"Warnings: {len(result.warnings)}")
print(f"Info: {len(result.info)}")

for issue in result.blockers:
    print(f"BLOCKER: {issue.message} at {issue.location}")
```

## QualityIssue

An issue found during quality bar validation.

### Attributes

- `severity` (str): "blocker", "warning", or "info"
- `message` (str): Human-readable description
- `location` (str): Where the issue was found (artifact_id, field, section, etc.)
- `fix` (str): Suggested remediation (optional)

**Example:**
```python
issue = QualityIssue(
    severity="blocker",
    message="Referenced artifact HOOK-002 not found",
    location="SCENE-001.prerequisites",
    fix="Add HOOK-002 or remove reference"
)
```

## Utility Functions

### `get_quality_bar()`

```python
def get_quality_bar(name: str) -> type[QualityBar]
```

Get a quality bar class by name.

**Parameters:**
- `name`: Quality bar name (e.g., "integrity", "reachability")

**Returns:** Quality bar class

**Raises:**
- `ValueError`: If bar name is unknown

**Example:**
```python
from questfoundry.validation import get_quality_bar

IntegrityBarClass = get_quality_bar("integrity")
bar = IntegrityBarClass()
result = bar.validate(artifacts)
```

### `QUALITY_BARS`

Dictionary mapping bar names to bar classes.

```python
QUALITY_BARS = {
    "integrity": IntegrityBar,
    "reachability": ReachabilityBar,
    "style": StyleBar,
    "gateways": GatewaysBar,
    "nonlinearity": NonlinearityBar,
    "determinism": DeterminismBar,
    "presentation": PresentationBar,
    "spoiler_hygiene": SpoilerHygieneBar,
}
```

**Example:**
```python
from questfoundry.validation import QUALITY_BARS

# List all available bars
for bar_name, bar_class in QUALITY_BARS.items():
    bar = bar_class()
    print(f"{bar_name}: {bar.description}")
```

## Usage Patterns

### Basic Gatecheck Workflow

```python
from questfoundry.validation import Gatekeeper
from questfoundry.state import WorkspaceManager

# Initialize
ws = WorkspaceManager("./project")
gk = Gatekeeper()

# Get artifacts from hot workspace
artifacts = ws.list_hot_artifacts()

# Run gatecheck
report = gk.run_gatecheck(
    artifacts,
    tu_id="TU-2025-11-07-SR01"
)

# Process results
if report.merge_safe:
    print("✓ Safe to promote to cold")
    # Promote artifacts
    for artifact in artifacts:
        artifact_id = artifact.metadata.get("id")
        if artifact_id:
            ws.promote_to_cold(artifact_id)
else:
    print(f"✗ Cannot merge - {len(report.blockers)} blockers")
    # Store report for review
    ws.save_hot_artifact(report.to_artifact())
```

### Selective Bar Validation

```python
# Only run critical bars
gk = Gatekeeper(bars=["integrity", "reachability", "spoiler_hygiene"])
report = gk.run_gatecheck(artifacts)

# Check specific bar results
integrity_result = report.bar_results.get("integrity")
if integrity_result and not integrity_result.passed:
    print("Integrity check failed:")
    for issue in integrity_result.blockers:
        print(f"  {issue.message}")
```

### Detailed Issue Reporting

```python
report = gk.run_gatecheck(artifacts)

# Group issues by severity
print("\n=== BLOCKERS ===")
for bar_name, issue in report.blockers:
    print(f"[{bar_name}] {issue.location}")
    print(f"  Problem: {issue.message}")
    if issue.fix:
        print(f"  Fix: {issue.fix}")

print("\n=== WARNINGS ===")
for bar_name, issue in report.warnings:
    print(f"[{bar_name}] {issue.message}")

print("\n=== SUMMARY ===")
print(f"Total issues: {len(report.all_issues)}")
print(f"Blockers: {len(report.blockers)}")
print(f"Warnings: {len(report.warnings)}")
```

### Custom Validation Pipeline

```python
from questfoundry.validation import get_quality_bar

# Create custom validation pipeline
pipeline = [
    ("Pre-merge", ["integrity", "reachability"]),
    ("Content Quality", ["style", "gateways", "nonlinearity"]),
    ("Player Safety", ["presentation", "spoiler_hygiene"]),
]

all_passed = True
for stage_name, bar_names in pipeline:
    print(f"\n{stage_name}:")
    stage_passed = True

    for bar_name in bar_names:
        bar_class = get_quality_bar(bar_name)
        bar = bar_class()
        result = bar.validate(artifacts)

        if result.passed:
            print(f"  ✓ {bar_name}")
        else:
            print(f"  ✗ {bar_name} - {len(result.blockers)} blockers")
            stage_passed = False

    if not stage_passed:
        all_passed = False
        print(f"  Stage failed - fix issues before continuing")
        break

if all_passed:
    print("\n✓ All validation stages passed!")
```

### Integration with Roles

```python
from questfoundry.validation import Gatekeeper

class GatekeeperRole:
    """Gatekeeper role that validates content."""

    def __init__(self):
        self.gatekeeper = Gatekeeper()

    def validate_content(self, artifacts):
        """Run gatecheck and return report."""
        report = self.gatekeeper.run_gatecheck(artifacts)

        if not report.passed:
            # Generate feedback for other roles
            feedback = self._generate_feedback(report)
            return {"approved": False, "feedback": feedback}
        else:
            return {"approved": True, "report_id": "..."}

    def _generate_feedback(self, report):
        """Convert issues to actionable feedback."""
        feedback = []
        for bar_name, issue in report.blockers:
            feedback.append({
                "bar": bar_name,
                "severity": issue.severity,
                "message": issue.message,
                "location": issue.location,
                "fix": issue.fix
            })
        return feedback
```

### Validation Reporting

```python
# Generate detailed report
report = gk.run_gatecheck(artifacts, author="Alice")

# Convert to artifact for storage
report_artifact = report.to_artifact()

# Save to workspace
ws.save_hot_artifact(report_artifact)

# Also save as markdown
def report_to_markdown(report):
    lines = [
        f"# Gatecheck Report",
        f"",
        f"**Status:** {'✓ PASSED' if report.passed else '✗ FAILED'}",
        f"**Merge Safe:** {'Yes' if report.merge_safe else 'No'}",
        f"**Blockers:** {len(report.blockers)}",
        f"**Warnings:** {len(report.warnings)}",
        f"",
    ]

    if report.blockers:
        lines.append("## Blockers")
        lines.append("")
        for bar_name, issue in report.blockers:
            lines.append(f"### [{bar_name}] {issue.location}")
            lines.append(f"- **Problem:** {issue.message}")
            if issue.fix:
                lines.append(f"- **Fix:** {issue.fix}")
            lines.append("")

    if report.warnings:
        lines.append("## Warnings")
        lines.append("")
        for bar_name, issue in report.warnings:
            lines.append(f"- **[{bar_name}]** {issue.message}")

    return "\n".join(lines)

markdown = report_to_markdown(report)
Path("gatecheck_report.md").write_text(markdown)
```

## Best Practices

1. **Run gatechecks before promotion**:
   ```python
   # Always validate before promoting to cold
   report = gk.run_gatecheck(hot_artifacts)
   if report.merge_safe:
       promote_to_cold(hot_artifacts)
   ```

2. **Store gatecheck reports**:
   ```python
   # Keep audit trail of all gatechecks
   report_artifact = report.to_artifact()
   ws.save_hot_artifact(report_artifact)
   ```

3. **Use strict mode for production**:
   ```python
   # Strict mode treats warnings as blockers
   gk = Gatekeeper(strict=True)
   ```

4. **Run incrementally**:
   ```python
   # Run critical bars first, then full check
   critical = Gatekeeper(bars=["integrity", "spoiler_hygiene"])
   if not critical.run_gatecheck(artifacts).passed:
       return  # Fix critical issues first

   full = Gatekeeper()
   report = full.run_gatecheck(artifacts)
   ```

5. **Provide actionable feedback**:
   ```python
   # Always include location and fix suggestions
   for bar_name, issue in report.blockers:
       print(f"Location: {issue.location}")
       print(f"Problem: {issue.message}")
       if issue.fix:
           print(f"How to fix: {issue.fix}")
   ```

## See Also

- [State Management API](state.md) - Hot/cold promotion
- [Export API](export.md) - View generation with safety checks
- [Models API](models.md) - Artifact types
