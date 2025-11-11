# Canon Workflows (Layer 6/7)

Canon workflows enable systematic worldbuilding and canon transfer across QuestFoundry projects, supporting sequels, prequels, and shared universe stories.

## Overview

Layer 6/7 introduces three main workflows:

1. **Canon-First Worldbuilding**: Proactive worldbuilding before story development
2. **Canon Transfer**: Export and import canon between projects
3. **Conflict Detection**: Validate canon consistency during import

### Key Concepts

#### Canon Mutability Levels

- **Invariant**: Immutable canon that cannot be changed (core worldbuilding facts)
- **Mutable**: Extensible canon that can be elaborated upon
- **Local**: Project-specific canon not exported to other projects

#### Immutability Tracking

All canon artifacts track:
- `immutable`: Boolean flag indicating if canon can be changed
- `source`: Attribution string (e.g., "canon-import", "world-genesis", "project-local")

## Canon Transfer Package

Canon Transfer Packages export worldbuilding elements for reuse in other projects.

### Structure

```python
from questfoundry.models import CanonTransferPackage

package = CanonTransferPackage(
    type="canon_transfer_package",
    data={
        "package_id": "CANON-DRAGON-LORE-001",
        "source_project": "Dragon's Quest I",
        "exported": "2025-11-11",
        "version": "1.0.0",
        "mutability_filter": "mixed",
        "description": "Core dragon lore for Dragon's Quest universe",
        "invariant_canon": [
            {
                "facts": [
                    "Dragons sleep for decades between hunts",
                    "Dragon scales reflect magical attacks"
                ],
                "theme": "Dragon Physiology",
                "source": "world-genesis"
            }
        ],
        "mutable_canon": [
            {
                "facts": [
                    "Regional dragon variants have different scale colors"
                ],
                "theme": "Dragon Diversity",
                "elaboration_guidance": "Feel free to create new regional variants"
            }
        ],
        "entity_registry": {
            "entities": [
                {
                    "name": "Ancient Dragon Council",
                    "entity_type": "faction",
                    "role": "governing body",
                    "description": "Elder dragons who maintain peace",
                    "source": "world-genesis",
                    "immutable": True
                }
            ]
        },
        "timeline": {
            "anchors": [
                {
                    "anchor_id": "T0",
                    "event": "First dragon awakening",
                    "year": -1000,
                    "source": "world-genesis",
                    "immutable": True
                }
            ]
        }
    }
)
```

### Exporting Canon

Use the `canon.transfer.export` intent to create a transfer package:

```python
from questfoundry.protocol import Envelope, Intent

# Create export request
envelope = Envelope(
    intent=Intent.CANON_TRANSFER_EXPORT,
    sender="SR",
    data={
        "mutability_filter": "invariant",  # Only export immutable canon
        "entity_types": ["character", "place"],  # Optional filter
        "timeline_anchors": ["T0", "T1"]  # Optional filter
    }
)

# Showrunner processes this intent and generates Canon Transfer Package
```

### Importing Canon

Use the `canon.transfer.import` intent with conflict detection:

```python
from questfoundry.protocol import Envelope, Intent

# Create import request
envelope = Envelope(
    intent=Intent.CANON_TRANSFER_IMPORT,
    sender="SR",
    data={
        "package_id": "CANON-DRAGON-LORE-001",
        "seed_ideas": [
            "Dragons can be domesticated",
            "A character repairs ancient dragon technology"
        ],
        "conflict_resolution_strategy": "revise"  # "reject", "revise", or "downgrade"
    }
)

# System will:
# 1. Detect conflicts between invariant canon and seed ideas
# 2. Generate conflict report with resolution recommendations
# 3. Merge entities and timeline anchors with deduplication
# 4. Generate constraint manifest for creative guidance
```

## World Genesis Manifest

World Genesis Manifest documents proactive worldbuilding before story development.

### Worldbuilding Budgets

- **Minimal** (2-4 hours): 3-5 core themes, light detail
- **Standard** (5-10 hours): 5-8 themes, moderate depth
- **Epic** (20+ hours): 10+ themes, exhaustive exploration

### Structure

```python
from questfoundry.models import WorldGenesisManifest

manifest = WorldGenesisManifest(
    type="world_genesis_manifest",
    data={
        "manifest_id": "GENESIS-DRAGON-WORLD-001",
        "project_name": "Dragon's Quest II",
        "created": "2025-11-11",
        "version": "1.0.0",
        "budget_level": "standard",
        "budget_spent": {
            "hours": 6.5,
            "tokens": 125000
        },
        "themes_explored": [
            {
                "theme": "History",
                "coverage": "moderate",
                "key_facts": [
                    "Kingdom unified 500 years ago",
                    "Dragons and humans signed peace treaty"
                ],
                "immutable_count": 2,
                "mutable_count": 3
            },
            {
                "theme": "Magic System",
                "coverage": "deep",
                "key_facts": [
                    "Magic flows from dragon veins underground",
                    "Only dragon-bonded humans can use magic"
                ],
                "immutable_count": 5,
                "mutable_count": 2
            }
        ],
        "canon_facts": {
            "invariant": [
                {
                    "fact": "Magic cannot resurrect the dead",
                    "theme": "Magic System",
                    "rationale": "Core constraint for story stakes"
                }
            ],
            "mutable": [
                {
                    "fact": "Different regions have different magical traditions",
                    "theme": "Magic System",
                    "elaboration_hooks": [
                        "Create regional spell variants",
                        "Design unique magical academies"
                    ]
                }
            ]
        }
    }
)
```

### Creating World Genesis

Use the `canon.genesis.create` intent to start worldbuilding:

```python
from questfoundry.protocol import Envelope, Intent

# Create genesis request
envelope = Envelope(
    intent=Intent.CANON_GENESIS_CREATE,
    sender="SR",
    data={
        "theme_list": [
            "History",
            "Geography",
            "Magic System",
            "Culture",
            "Politics"
        ],
        "budget_level": "standard",
        "baseline_anchors": [
            {"anchor_id": "T0", "event": "Kingdom founding"}
        ]
    }
)

# System will:
# 1. Wake Lore Weaver role for canon-first worldbuilding loop
# 2. Systematically explore each theme within budget
# 3. Create entities with immutability marking
# 4. Define timeline anchors
# 5. Generate World Genesis Manifest
# 6. Generate Constraint Manifest for Story Spark
```

## Entity Registry

The entity registry tracks canonical entities across canon workflows.

### Entity Types

- `character`: Characters (people, creatures, AI)
- `place`: Locations (cities, dungeons, planes)
- `faction`: Organizations (guilds, kingdoms, cults)
- `item`: Objects (artifacts, weapons, MacGuffins)

### Usage

```python
from questfoundry.state import EntityRegistry, Entity, EntityType

# Create registry
registry = EntityRegistry()

# Add entity
entity = Entity(
    name="Queen Elara",
    entity_type=EntityType.CHARACTER,
    role="ruler",
    description="First queen of united kingdom",
    source="world-genesis",
    immutable=True
)
registry.create(entity)

# Query entities
characters = registry.get_by_type(EntityType.CHARACTER)
queen = registry.get_by_name("Queen Elara")
immutable_entities = registry.get_by_immutability(True)

# Merge from canon import
imported_entities = [...]  # List of Entity objects
merge_report = registry.merge(imported_entities, deduplicate=True)
# Deduplication: immutable entities take precedence over mutable ones
```

## Timeline Management

Timeline anchors provide chronological structure for stories.

### Anchor Types

- **Baseline anchors** (T0, T1, T2): Project-wide historical events
- **Extension anchors** (T3+): Story-specific events

### Usage

```python
from questfoundry.state import TimelineManager, TimelineAnchor

# Create timeline
timeline = TimelineManager()

# Add baseline anchors
timeline.add_anchor(
    anchor_id="T0",
    event="Kingdom founding",
    year=0,
    description="First king unified the warring clans",
    source="world-genesis",
    immutable=True
)

timeline.add_anchor(
    anchor_id="T1",
    event="Dragon-Human peace treaty",
    year=250,
    description="End of Dragon War",
    source="world-genesis",
    immutable=True
)

# Add extension anchors with offsets
timeline.add_anchor(
    anchor_id="T3-REVOLT",
    event="Mage rebellion",
    offset=500,  # 500 years after T0
    description="Mages revolt against magic restrictions",
    source="project-local",
    immutable=False
)

# Validate chronology
errors = timeline.validate_chronology()
if errors:
    for error in errors:
        print(f"Timeline error: {error}")

# Query anchors
baseline = timeline.get_baseline_anchors()
t0 = timeline.get_anchor("T0")
```

## Conflict Detection

Conflict detection identifies contradictions between invariant canon and new project ideas.

### Conflict Types

- **Contradiction**: Direct opposition (e.g., "dragons extinct" vs. "dragon appears")
- **Temporal paradox**: Timeline inconsistency
- **Entity conflict**: Duplicate entities with different immutability

### Usage

```python
from questfoundry.state import ConflictDetector, ConflictResolution

# Create detector
detector = ConflictDetector()

# Define invariant canon
invariant_canon = [
    "Dragons sleep for decades between hunts",
    "Magic cannot resurrect the dead",
    "Ancient dragon artifacts are indestructible"
]

# Define seed ideas for new story
seed_ideas = [
    "A character destroys an ancient dragon artifact",
    "The protagonist resurrects their dead mentor",
    "Dragons appear every week in this story"
]

# Detect conflicts
report = detector.detect_conflicts(
    invariant_canon=invariant_canon,
    seed_ideas=seed_ideas,
    canon_source="Dragon's Quest I"
)

# Review conflicts
for conflict in report.conflicts:
    print(f"Conflict: {conflict.seed_idea}")
    print(f"Contradicts: {conflict.canon_statement}")
    print(f"Severity: {conflict.severity}")
    print(f"Recommendation: {conflict.recommended_resolution}")
    print(f"Fix: {conflict.fix_suggestion}")
    print()

# Apply resolution
if conflict.recommended_resolution == ConflictResolution.REJECT:
    # Abandon seed idea, keep invariant canon
    pass
elif conflict.recommended_resolution == ConflictResolution.REVISE:
    # Modify seed idea to align with canon
    pass
elif conflict.recommended_resolution == ConflictResolution.DOWNGRADE:
    # Change invariant to mutable (requires approval)
    pass
```

## Constraint Manifests

Constraint manifests provide creative guidance derived from canon.

### Structure

```python
from questfoundry.state import ConstraintManifestGenerator

# Generate manifest
generator = ConstraintManifestGenerator()
manifest = generator.generate(
    invariant_canon=[...],
    mutable_canon=[...],
    entity_registry=registry,
    timeline=timeline,
    source="canon-import"
)

# Access constraints
print("You CANNOT:")
for invariant in manifest.invariants:
    print(f"  ❌ {invariant}")

print("\nYou CAN:")
for mutable in manifest.mutables:
    print(f"  ✅ {mutable}")

print("\nTimeline Constraints:")
for constraint in manifest.timeline_constraints:
    print(f"  📅 {constraint}")

print("\nEntity Constraints:")
for constraint in manifest.entity_constraints:
    print(f"  👤 {constraint}")

print("\nCreative Guidance:")
for guide in manifest.guidance:
    print(f"  💡 {guide}")

# Export to markdown
markdown = manifest.to_markdown()
# Use in Story Spark prompts to guide creative roles
```

## Hot/Cold Merge with Immutability

Workspace promotion now supports immutability tracking:

```python
from questfoundry.state import WorkspaceManager

ws = WorkspaceManager("/path/to/project")

# Promote with immutability tracking
ws.promote_to_cold(
    artifact_id="CANON-001",
    immutable=True,
    source="canon-import",
    delete_hot=True
)
# Artifact metadata now includes: {"immutable": True, "source": "canon-import"}

# Demote while preserving immutability
ws.demote_to_hot(
    artifact_id="CANON-001",
    preserve_immutability=True  # Default: True
)
# Immutability tracking preserved during demotion
```

## Quality Bars

Three new quality bars validate canon workflows:

### Canon Conflict Bar

Validates no contradictions in imported canon:
- Detects internal conflicts within canon packages
- Checks for duplicate immutable entities
- Uses keyword-based contradiction detection

### Timeline Chronology Bar

Validates timeline anchor ordering:
- Ensures proper baseline sequence (T0, T1, T2)
- Checks for temporal paradoxes
- Validates year and offset values

### Entity Reference Bar

Validates entity registry consistency:
- Checks required fields
- Validates entity types
- Ensures source attribution for immutable entities

### Usage

```python
from questfoundry.validation import Gatekeeper

# Run gatecheck with canon bars
gatekeeper = Gatekeeper(bars=[
    "canon_conflict",
    "timeline_chronology",
    "entity_reference"
])

artifacts = [canon_package, world_manifest]
report = gatekeeper.run_gatecheck(artifacts)

if not report.passed:
    print("Gatecheck failed!")
    for bar_name, issue in report.blockers:
        print(f"[{bar_name}] {issue.message}")
        print(f"  Location: {issue.location}")
        print(f"  Fix: {issue.fix}")
```

## Best Practices

### 1. Canon-First Worldbuilding

- Start with world genesis before story development
- Use appropriate budget level for project scope
- Mark foundational facts as immutable
- Leave room for elaboration with mutable canon

### 2. Canon Transfer

- Export only necessary canon (invariant for hard rules, mixed for flexibility)
- Include comprehensive entity registry
- Validate timeline chronology before export
- Provide clear import guidance

### 3. Conflict Detection

- Run conflict detection before finalizing canon import
- Review all critical and major conflicts
- Prefer REVISE over REJECT when possible
- Document resolution decisions

### 4. Constraint Manifests

- Generate manifests after every canon import or world genesis
- Include in Story Spark prompts for creative roles
- Update when canon evolves
- Balance constraints with creative freedom

### 5. Immutability Tracking

- Mark core worldbuilding as immutable
- Track source attribution for all canon
- Preserve immutability during hot/cold moves
- Only downgrade immutability with explicit approval

## Related Documentation

- [State Management API](../api/state.md) - EntityRegistry and TimelineManager APIs
- [Validation API](../api/validation.md) - Quality bars and Gatekeeper
- [Protocol](../api/protocol.md) - Intent handlers and envelopes
- [Artifact Models](../api/index.md) - CanonTransferPackage and WorldGenesisManifest

## Specification References

For implementation details, see:
- `questfoundry-spec/00-north-star/LAYER6_7_CANON_IMPACT.md`
- Canon workflow intent handlers in `src/questfoundry/resources/prompts/showrunner/intent_handlers/`
