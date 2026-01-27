#!/usr/bin/env python3
"""
Integration test for infrastructure preservation during sdlc-import
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from infrastructure_preserver import InfrastructurePreserver


def test_infrastructure_preserver_backup_and_restore():
    """Test that infrastructure is preserved during import"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / ".agentic_sdlc"
        output_dir.mkdir()

        # Create mock infrastructure
        templates_dir = output_dir / "templates"
        templates_dir.mkdir()
        (templates_dir / "adr-template.yml").write_text("template: adr")
        (templates_dir / "odr-template.yml").write_text("template: odr")

        corpus_dir = output_dir / "corpus/nodes/decisions"
        corpus_dir.mkdir(parents=True)
        (corpus_dir / "ADR-001-framework.yml").write_text("framework: adr")
        (corpus_dir / ".gitkeep").touch()

        (output_dir / "logo.png").write_text("logo")

        # Initialize preserver
        preserver = InfrastructurePreserver(output_dir)

        # Backup infrastructure
        backup_stats = preserver.backup_existing_infrastructure()
        assert backup_stats['backed_up'] > 0
        assert backup_stats['preserved'] > 0

        # Simulate import by deleting all files
        shutil.rmtree(output_dir)
        output_dir.mkdir()

        # Create mock imported files
        corpus_dir.mkdir(parents=True)
        (corpus_dir / "ADR-INFERRED-001.yml").write_text("imported: adr")

        # Restore infrastructure
        restore_stats = preserver.restore_infrastructure()
        assert restore_stats['restored'] > 0

        # Verify infrastructure was restored
        assert (templates_dir / "adr-template.yml").exists()
        assert (templates_dir / "odr-template.yml").exists()
        assert (corpus_dir / "ADR-001-framework.yml").exists()
        assert (corpus_dir / ".gitkeep").exists()
        assert (output_dir / "logo.png").exists()

        # Verify imported file still exists
        assert (corpus_dir / "ADR-INFERRED-001.yml").exists()


def test_framework_adr_detection():
    """Test that framework ADRs (001-099) are detected as infrastructure"""

    preserver = InfrastructurePreserver(Path("/tmp"))

    # Framework ADRs should be preserved
    assert preserver._is_infrastructure_file(Path("corpus/nodes/decisions/ADR-001-test.yml"))
    assert preserver._is_infrastructure_file(Path("corpus/nodes/decisions/ADR-022-legacy.yml"))
    assert preserver._is_infrastructure_file(Path("corpus/nodes/decisions/ADR-099-test.yml"))

    # Inferred ADRs should NOT be preserved (will be regenerated)
    assert not preserver._is_infrastructure_file(Path("corpus/nodes/decisions/ADR-INFERRED-001.yml"))

    # High-number ADRs should NOT be preserved (user ADRs)
    assert not preserver._is_infrastructure_file(Path("corpus/nodes/decisions/ADR-100-user.yml"))
    assert not preserver._is_infrastructure_file(Path("corpus/nodes/decisions/ADR-200-user.yml"))


def test_templates_detection():
    """Test that templates are detected as infrastructure"""

    preserver = InfrastructurePreserver(Path("/tmp"))

    assert preserver._is_infrastructure_file(Path("templates/adr-template.yml"))
    assert preserver._is_infrastructure_file(Path("templates/odr-template.yml"))
    assert preserver._is_infrastructure_file(Path("templates/spec-template.md"))
    assert preserver._is_infrastructure_file(Path("templates/threat-model-template.yml"))


def test_gitkeep_detection():
    """Test that .gitkeep files are detected as infrastructure"""

    preserver = InfrastructurePreserver(Path("/tmp"))

    assert preserver._is_infrastructure_file(Path("corpus/nodes/concepts/.gitkeep"))
    assert preserver._is_infrastructure_file(Path("references/.gitkeep"))
    assert preserver._is_infrastructure_file(Path("sessions/.gitkeep"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
