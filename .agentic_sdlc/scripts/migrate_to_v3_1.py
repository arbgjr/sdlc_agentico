#!/usr/bin/env python3
"""
Migration script for SDLC Agêntico v3.0 → v3.1
Adds Design System Phase (Phase 4) and shifts existing phases 4-8 to 5-9.
Cross-platform compatible (Linux + Windows).
"""

import os
import re
import shutil
import json
from pathlib import Path
from datetime import datetime

def migrate_project():
    """Migrate project to v3.1.0 with Design System Phase"""
    print("🔄 Migrating project to SDLC Agêntico v3.1.0 (Design System Phase)...")
    print()

    project_root = Path.cwd()
    settings_file = project_root / ".claude" / "settings.json"
    project_dir = project_root / ".project"

    # Step 1: Backup settings.json
    if settings_file.exists():
        backup_file = settings_file.with_suffix(f'.json.backup-{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        shutil.copy2(settings_file, backup_file)
        print(f"✅ Backup created: {backup_file}")
    else:
        print("⚠️  settings.json not found - skipping backup")

    # Step 2: Update phase references in .project/ files
    if project_dir.exists():
        phase_mappings = {
            "phase: 8": "phase: 9",
            "phase: 7": "phase: 8",
            "phase: 6": "phase: 7",
            "phase: 5": "phase: 6",
            "phase: 4": "phase: 5",
            "Phase 8": "Phase 9",
            "Phase 7": "Phase 8",
            "Phase 6": "Phase 7",
            "Phase 5": "Phase 6",
            "Phase 4": "Phase 5",
        }

        files_updated = 0
        for pattern in ["*.md", "*.yml", "*.yaml"]:
            for file_path in project_dir.rglob(pattern):
                if update_phase_references(file_path, phase_mappings):
                    files_updated += 1

        print(f"✅ Phase references updated in {files_updated} files")
    else:
        print("⚠️  .project/ directory not found - skipping phase updates")

    # Step 3: Create design directory structure
    design_dirs = [
        project_dir / "design" / "specifications",
        project_dir / "design" / "mockups",
        project_dir / "design" / "components",
        project_dir / "design" / "design-system",
        project_dir / "design" / "handoff",
        project_dir / "design" / "brand",
    ]

    for dir_path in design_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)

    print("✅ Design directory structure created")

    # Step 4: Copy templates
    templates_src = project_root / ".agentic_sdlc" / "templates"
    templates_dest = project_dir / "design"

    if templates_src.exists():
        try:
            shutil.copy2(
                templates_src / "design-system-tokens.yml",
                templates_dest / "design-system" / "tokens.yml.example"
            )
            shutil.copy2(
                templates_src / "component-spec.md",
                templates_dest / "components" / "_TEMPLATE.md"
            )
            shutil.copy2(
                templates_src / "accessibility-checklist.md",
                templates_dest / "accessibility-checklist.md"
            )
            print("✅ Templates copied to .project/design/")
        except FileNotFoundError as e:
            print(f"⚠️  Template not found: {e}")
    else:
        print("⚠️  Templates directory not found - skipping template copy")

    # Step 5: Summary
    print()
    print("✅ Migration complete!")
    print()
    print("📋 Next steps:")
    print("   1. Review updated phase numbers in .project/")
    print("   2. Update .claude/settings.json if using custom configuration")
    print("   3. Test Phase 4 with: /sdlc-start --level 2 'Test project'")
    print("   4. Commit changes: git add -A && git commit -m 'chore: migrate to v3.1.0'")
    print()
    print(f"📁 Design templates available at: {templates_dest}")

def update_phase_references(file_path: Path, mappings: dict) -> bool:
    """Update phase references in a file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        modified = False

        for old, new in mappings.items():
            if old in content:
                content = content.replace(old, new)
                modified = True

        if modified:
            file_path.write_text(content, encoding='utf-8')
            print(f"  📝 Updated: {file_path.relative_to(Path.cwd())}")
            return True
        return False

    except Exception as e:
        print(f"  ⚠️  Failed to update {file_path}: {e}")
        return False

if __name__ == "__main__":
    try:
        migrate_project()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        exit(1)
