# Bundled Resources

This package bundles schemas and prompts from the [questfoundry-spec](https://github.com/pvliesdonk/questfoundry-spec) repository.

## Resource Versions

The following versions are pinned and bundled:

- **Schemas (Layer 3)**: `schemas-v0.2.0`
- **Protocols (Layer 4)**: `protocol-v0.2.1`
- **Prompts (Layer 5)**: `milestone-layer5-complete`

## Bundling Process

Resources are bundled at build time by running:

```bash
python scripts/bundle_resources.py
```

This copies:
- All JSON schema files from `spec/03-schemas/` → `src/questfoundry/resources/schemas/`
- All prompt directories from `spec/05-prompts/` → `src/questfoundry/resources/prompts/`

## Updating Resources

To update to a newer spec version:

1. Update the spec submodule:
   ```bash
   cd spec
   git fetch --tags
   git checkout <new-tag>
   cd ..
   ```

2. Re-bundle resources:
   ```bash
   python scripts/bundle_resources.py
   ```

3. Update this file with the new version tags

4. Commit the changes:
   ```bash
   git add spec src/questfoundry/resources/ RESOURCES.md
   git commit -m "chore: update bundled resources to spec <version>"
   ```

## Resource Contents

### Schemas (26 files)

All Layer 3 JSON schemas for artifacts:
- `hook_card.schema.json`
- `tu_brief.schema.json`
- `canon_pack.schema.json`
- `gatecheck_report.schema.json`
- `codex_entry.schema.json`
- And 21 more...

### Prompts (18 role directories)

System prompts for all roles:
- `showrunner/`
- `gatekeeper/`
- `lore_weaver/`
- `plotwright/`
- `scene_smith/`
- And 13 more...

Plus shared components, role adapters, and loop playbooks.

## License Note

The bundled resources are from the questfoundry-spec repository and maintain their original licensing.
This package (questfoundry-py) is licensed under MIT.
