#!/usr/bin/env python3
"""
create_client.py - Create new SDLC Agêntico client profile from template
Version: 3.0.0
Part of: Phase 5 - Documentation & Tooling (Multi-Client Architecture)

Cross-platform (Linux, macOS, Windows)
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed (pip install pyyaml)", file=sys.stderr)
    sys.exit(1)


def create_client_profile(
    name: str,
    domain: str,
    client_id: str,
    clients_dir: Path = Path("clients"),
    template_dir: Optional[Path] = None,
) -> bool:
    """
    Create new client profile from template.

    Args:
        name: Client display name
        domain: Industry domain
        client_id: Client ID (lowercase, hyphens)
        clients_dir: Clients directory
        template_dir: Template directory (default: clients/_base)

    Returns:
        bool: Success
    """
    if template_dir is None:
        template_dir = clients_dir / "_base"

    client_dir = clients_dir / client_id

    # Validate client_id
    if not client_id.replace("-", "").replace("_", "").isalnum():
        print(f"ERROR: Invalid client ID: {client_id}", file=sys.stderr)
        print("Client ID must contain only lowercase letters, numbers, hyphens, and underscores", file=sys.stderr)
        return False

    if client_id in ("generic", "_base"):
        print(f"ERROR: Reserved client ID: {client_id}", file=sys.stderr)
        return False

    # Check if client already exists
    if client_dir.exists():
        print(f"ERROR: Client already exists: {client_dir}", file=sys.stderr)
        return False

    # Check template exists
    template_profile = template_dir / "profile.yml"
    if not template_profile.exists():
        print(f"ERROR: Template not found: {template_profile}", file=sys.stderr)
        return False

    print(f"Creating client profile: {client_id}")
    print(f"  Name: {name}")
    print(f"  Domain: {domain}")
    print()

    # Create directory structure
    print("Creating directory structure...")
    (client_dir / "agents").mkdir(parents=True, exist_ok=True)
    (client_dir / "skills" / "gate-evaluator" / "gates").mkdir(parents=True, exist_ok=True)
    (client_dir / "templates").mkdir(parents=True, exist_ok=True)
    (client_dir / "corpus" / "nodes" / "decisions").mkdir(parents=True, exist_ok=True)
    (client_dir / "corpus" / "nodes" / "patterns").mkdir(parents=True, exist_ok=True)
    (client_dir / "corpus" / "nodes" / "learnings").mkdir(parents=True, exist_ok=True)

    # Load and customize profile template
    print("Creating profile.yml...")
    with open(template_profile) as f:
        profile = yaml.safe_load(f)

    # Customize profile
    profile["client"]["id"] = client_id
    profile["client"]["name"] = name
    profile["client"]["domain"] = domain
    profile["client"]["version"] = "1.0.0"

    # Update detection marker
    profile["client"]["detection"]["markers"] = [
        {"path": f".{client_id}-client", "type": "file"}
    ]

    # Write profile
    profile_path = client_dir / "profile.yml"
    with open(profile_path, "w") as f:
        yaml.dump(profile, f, default_flow_style=False, sort_keys=False)

    # Create README.md
    print("Creating README.md...")
    readme_content = f"""# {name} Client Profile

This is the {name} client profile for SDLC Agêntico.

## Overview

- **ID**: `{client_id}`
- **Name**: {name}
- **Domain**: {domain}
- **Version**: 1.0.0

## Activation

To use this client profile:

```bash
# Option 1: Manual activation
/set-client {client_id}

# Option 2: Auto-detection (create marker file)
touch .{client_id}-client
# Framework auto-detects on next workflow
```

## Customizations

This profile starts empty. Add customizations as needed:

### Agent Overrides

Override base agents for domain-specific behavior:

```bash
# Copy base agent
cp .claude/agents/code-reviewer.md clients/{client_id}/agents/

# Edit to add custom checks
vim clients/{client_id}/agents/code-reviewer.md
```

Then update `profile.yml`:

```yaml
agents:
  overrides:
    - name: "code-reviewer"
      path: "agents/code-reviewer.md"
      reason: "Adds {domain}-specific checks"
```

### Custom Quality Gates

Add domain-specific validation gates:

```yaml
gates:
  additions:
    - name: "compliance-check"
      path: "skills/gate-evaluator/gates/compliance-check.yml"
      after_phase: 6
      reason: "Validates {domain} compliance requirements"
```

### Custom Templates

Override templates for domain-specific fields:

```yaml
templates:
  overrides:
    - name: "adr-template"
      path: "templates/adr-template.yml"
      reason: "Adds {domain} compliance fields"
```

## Testing

Run a workflow to test your customizations:

```bash
/set-client {client_id}
/sdlc-start "Test feature"
```

## Documentation

- **Base Template**: `clients/_base/profile.yml`
- **Onboarding Guide**: `clients/_base/README.md`
- **Demo Client**: `clients/demo-client/` (learning example)

## Support

- **Issues**: https://github.com/arbgjr/sdlc_agentico/issues
- **Discussions**: https://github.com/arbgjr/sdlc_agentico/discussions
"""

    readme_path = client_dir / "README.md"
    readme_path.write_text(readme_content)

    # Create .gitkeep files
    for empty_dir in [
        client_dir / "agents",
        client_dir / "skills/gate-evaluator/gates",
        client_dir / "templates",
        client_dir / "corpus/nodes/decisions",
        client_dir / "corpus/nodes/patterns",
        client_dir / "corpus/nodes/learnings",
    ]:
        (empty_dir / ".gitkeep").touch()

    print()
    print("✅ Client profile created successfully!")
    print()
    print(f"Location: {client_dir}")
    print()
    print("Next steps:")
    print(f"  1. Review and customize: {profile_path}")
    print(f"  2. Add customizations (agents, gates, templates)")
    print(f"  3. Activate: /set-client {client_id}")
    print(f"  4. Test: /sdlc-start 'Test feature'")
    print()
    print("Documentation:")
    print(f"  - Profile: {profile_path}")
    print(f"  - README: {readme_path}")
    print("  - Template: clients/_base/profile.yml")
    print("  - Guide: clients/_base/README.md")
    print()

    return True


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description="Create new SDLC Agêntico client profile from template"
    )
    parser.add_argument("--name", required=True, help="Client display name (e.g., 'Acme Corp')")
    parser.add_argument("--domain", required=True, help="Industry domain (e.g., 'financial-services')")
    parser.add_argument("--id", dest="client_id", required=True, help="Client ID (lowercase-hyphenated)")
    parser.add_argument("--clients-dir", default="clients", help="Clients directory (default: clients)")

    args = parser.parse_args()

    success = create_client_profile(
        name=args.name,
        domain=args.domain,
        client_id=args.client_id,
        clients_dir=Path(args.clients_dir),
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
