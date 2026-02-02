#!/usr/bin/env python3
"""
Hook: validate-framework-structure
Validates that all required framework files exist.
Version: 3.0.0 (Python-First)

Cross-platform (Linux, macOS, Windows)
Logs missing files to Loki for monitoring.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Add lib path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib" / "python"))

from sdlc_logging import get_logger

logger = get_logger(__name__, skill="framework-validator", phase=0)

# Required framework files (templates, schemas, docs)
REQUIRED_FILES: List[str] = [
    # Templates
    ".agentic_sdlc/templates/adr-template.yml",
    ".agentic_sdlc/templates/odr-template.yml",
    ".agentic_sdlc/templates/spec-template.md",
    ".agentic_sdlc/templates/threat-model-template.yml",

    # Schemas
    ".agentic_sdlc/schemas/adr-schema.json",

    # Core documentation
    ".agentic_sdlc/docs/README.md",
    ".agentic_sdlc/docs/enrichment-guide.md",
    ".agentic_sdlc/docs/guides/quickstart.md",
    ".agentic_sdlc/docs/guides/infrastructure.md",
    ".agentic_sdlc/docs/guides/troubleshooting.md",
    ".agentic_sdlc/docs/guides/adr-vs-odr.md",
    ".agentic_sdlc/docs/sdlc/agents.md",
    ".agentic_sdlc/docs/sdlc/commands.md",
    ".agentic_sdlc/docs/sdlc/overview.md",

    # Engineering playbook
    ".agentic_sdlc/docs/engineering-playbook/README.md",
    ".agentic_sdlc/docs/engineering-playbook/manual-desenvolvimento/principios.md",
    ".agentic_sdlc/docs/engineering-playbook/manual-desenvolvimento/standards.md",
    ".agentic_sdlc/docs/engineering-playbook/manual-desenvolvimento/qualidade.md",
    ".agentic_sdlc/docs/engineering-playbook/manual-desenvolvimento/testes.md",
    ".agentic_sdlc/docs/engineering-playbook/stacks/devops/security.md",
    ".agentic_sdlc/docs/engineering-playbook/stacks/devops/ci-cd.md",
    ".agentic_sdlc/docs/engineering-playbook/stacks/devops/observability.md",

    # Scripts
    ".agentic_sdlc/scripts/setup-sdlc.sh",
    ".agentic_sdlc/scripts/validate-sdlc-phase.sh",
]

# Quality gates (critical for SDLC workflow)
REQUIRED_GATES: List[str] = [
    ".claude/skills/gate-evaluator/gates/phase-0-to-1.yml",
    ".claude/skills/gate-evaluator/gates/phase-1-to-2.yml",
    ".claude/skills/gate-evaluator/gates/phase-2-to-3.yml",
    ".claude/skills/gate-evaluator/gates/phase-3-to-4.yml",
    ".claude/skills/gate-evaluator/gates/phase-4-to-5.yml",
    ".claude/skills/gate-evaluator/gates/phase-5-to-6.yml",
    ".claude/skills/gate-evaluator/gates/phase-6-to-7.yml",
    ".claude/skills/gate-evaluator/gates/phase-7-to-8.yml",
    ".claude/skills/gate-evaluator/gates/security-gate.yml",
]


def validate_files(files: List[str], category: str) -> Tuple[int, int]:
    """
    Validate file existence.

    Args:
        files: List of file paths to check
        category: Category name for logging (framework, gate)

    Returns:
        Tuple of (missing_count, total_count)
    """
    missing = 0

    for filepath in files:
        file_path = Path(filepath)

        if not file_path.exists():
            missing += 1
            logger.error(
                f"Required {category} file missing",
                extra={"file": filepath, "category": category}
            )
        else:
            logger.debug(
                f"{category.capitalize()} file exists",
                extra={"file": filepath}
            )

    return missing, len(files)


def main():
    """Main validation function."""
    logger.info("Starting framework structure validation")

    # Validate required files
    files_missing, files_total = validate_files(REQUIRED_FILES, "framework")

    # Validate quality gates
    gates_missing, gates_total = validate_files(REQUIRED_GATES, "gate")

    # Calculate totals
    total_missing = files_missing + gates_missing
    total_checked = files_total + gates_total

    # Log summary
    if total_missing == 0:
        logger.info(
            "Framework structure validation passed",
            extra={
                "checked": total_checked,
                "missing": 0
            }
        )
    else:
        logger.warning(
            "Framework structure validation completed with missing files",
            extra={
                "checked": total_checked,
                "missing": total_missing,
                "files_missing": files_missing,
                "gates_missing": gates_missing
            }
        )

        # Print summary to console (visible to user)
        print(
            f"⚠️  Framework structure check: {total_missing} files missing "
            f"(see Loki logs for details)"
        )

    # Exit with success (don't block workflow)
    sys.exit(0)


if __name__ == "__main__":
    main()
