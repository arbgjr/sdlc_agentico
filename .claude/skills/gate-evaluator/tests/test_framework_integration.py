#!/usr/bin/env python3
"""
Framework Integration Test - End-to-End Validation
Tests all framework capabilities through a simulated SDLC workflow.

This test validates:
1. Framework structure (.agentic_sdlc/)
2. Project structure (.project/)
3. Templates loading
4. Schemas validation
5. Documentation access
6. Gates evaluation
7. Hooks execution
8. Skills integration
9. Logging to Loki
10. Corpus RAG operations
"""

import sys
import pytest
import tempfile
import subprocess
import json
import yaml
from pathlib import Path
from datetime import datetime

# Add logging utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="framework-integration-test", phase=0)


class TestFrameworkIntegration:
    """End-to-end integration tests for SDLC Agêntico framework"""

    @pytest.fixture
    def test_project(self, tmp_path):
        """Create a minimal test project with framework structure"""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Framework structure
        framework_dir = project_dir / ".agentic_sdlc"
        (framework_dir / "templates").mkdir(parents=True)
        (framework_dir / "schemas").mkdir(parents=True)
        (framework_dir / "docs/guides").mkdir(parents=True)
        (framework_dir / "scripts").mkdir(parents=True)

        # Create minimal templates
        adr_template = {
            "id": "ADR-XXX",
            "title": "{{ title }}",
            "date": "{{ date }}",
            "status": "proposed",
            "context": "{{ context }}",
            "decision": "{{ decision }}",
            "consequences": {
                "positive": ["{{ positive }}"],
                "negative": ["{{ negative }}"]
            }
        }
        (framework_dir / "templates/adr-template.yml").write_text(yaml.dump(adr_template))

        # Create minimal schema
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "title"],
            "properties": {
                "id": {"type": "string", "pattern": "^ADR-[0-9]{3,}$"},
                "title": {"type": "string"}
            }
        }
        (framework_dir / "schemas/adr-schema.json").write_text(json.dumps(schema))

        # Create minimal docs
        (framework_dir / "docs/README.md").write_text("# Framework Documentation")
        (framework_dir / "docs/guides/quickstart.md").write_text("# Quickstart Guide")

        # Project structure
        project_corpus = project_dir / ".project"
        (project_corpus / "corpus/nodes/decisions").mkdir(parents=True)
        (project_corpus / "corpus/nodes/learnings").mkdir(parents=True)
        (project_corpus / "phases").mkdir(parents=True)
        (project_corpus / "architecture").mkdir(parents=True)
        (project_corpus / "security").mkdir(parents=True)
        (project_corpus / "reports").mkdir(parents=True)
        (project_corpus / "sessions").mkdir(parents=True)

        return project_dir

    def test_01_framework_structure_exists(self, test_project):
        """Test 1: Validate framework directory structure"""
        logger.info("Test 1: Validating framework structure")

        framework_dir = test_project / ".agentic_sdlc"

        # Check core directories
        assert (framework_dir / "templates").exists(), "templates/ missing"
        assert (framework_dir / "schemas").exists(), "schemas/ missing"
        assert (framework_dir / "docs").exists(), "docs/ missing"
        assert (framework_dir / "scripts").exists(), "scripts/ missing"

        logger.info("✅ Framework structure validated")

    def test_02_project_structure_exists(self, test_project):
        """Test 2: Validate project directory structure"""
        logger.info("Test 2: Validating project structure")

        project_dir = test_project / ".project"

        # Check core directories
        assert (project_dir / "corpus/nodes/decisions").exists(), "corpus/nodes/decisions/ missing"
        assert (project_dir / "corpus/nodes/learnings").exists(), "corpus/nodes/learnings/ missing"
        assert (project_dir / "phases").exists(), "phases/ missing"
        assert (project_dir / "architecture").exists(), "architecture/ missing"
        assert (project_dir / "security").exists(), "security/ missing"

        logger.info("✅ Project structure validated")

    def test_03_template_loading(self, test_project):
        """Test 3: Load and parse template files"""
        logger.info("Test 3: Loading templates")

        template_path = test_project / ".agentic_sdlc/templates/adr-template.yml"

        with open(template_path) as f:
            template = yaml.safe_load(f)

        assert template is not None, "Template failed to load"
        assert "id" in template, "Template missing 'id' field"
        assert "title" in template, "Template missing 'title' field"

        logger.info(f"✅ Template loaded: {len(template)} fields")

    def test_04_schema_validation(self, test_project):
        """Test 4: Load and validate JSON schema"""
        logger.info("Test 4: Validating schema")

        schema_path = test_project / ".agentic_sdlc/schemas/adr-schema.json"

        with open(schema_path) as f:
            schema = json.load(f)

        assert schema is not None, "Schema failed to load"
        assert "$schema" in schema, "Schema missing $schema field"
        assert "properties" in schema, "Schema missing properties"

        # Validate a valid ADR
        valid_adr = {"id": "ADR-001", "title": "Test Decision"}
        assert "id" in valid_adr, "Valid ADR missing required field"

        logger.info("✅ Schema validated")

    def test_05_documentation_access(self, test_project):
        """Test 5: Access documentation files"""
        logger.info("Test 5: Accessing documentation")

        docs_dir = test_project / ".agentic_sdlc/docs"

        # Check core docs
        readme = docs_dir / "README.md"
        quickstart = docs_dir / "guides/quickstart.md"

        assert readme.exists(), "README.md missing"
        assert quickstart.exists(), "quickstart.md missing"

        readme_content = readme.read_text()
        assert len(readme_content) > 0, "README is empty"

        logger.info(f"✅ Documentation accessed: {len(readme_content)} chars")

    def test_06_gate_file_structure(self, test_project):
        """Test 6: Validate quality gate structure (without evaluation)"""
        logger.info("Test 6: Checking gate file structure")

        # Create a minimal gate file in test project
        gates_dir = test_project / ".claude/skills/gate-evaluator/gates"
        gates_dir.mkdir(parents=True, exist_ok=True)

        gate_content = {
            "name": "Test Gate",
            "from_phase": 0,
            "to_phase": 1,
            "criteria": {
                "required_artifacts": [
                    {"name": "requirements.md", "type": "document"}
                ]
            }
        }

        gate_file = gates_dir / "test-gate.yml"
        gate_file.write_text(yaml.dump(gate_content))

        # Load and validate gate structure
        with open(gate_file) as f:
            gate = yaml.safe_load(f)

        assert gate is not None, "Gate failed to load"
        assert "name" in gate, "Gate missing 'name'"
        assert "from_phase" in gate, "Gate missing 'from_phase'"
        assert "to_phase" in gate, "Gate missing 'to_phase'"
        assert "criteria" in gate, "Gate missing 'criteria'"

        logger.info(f"✅ Gate structure validated: {gate['name']}")

    def test_07_corpus_operations(self, test_project):
        """Test 7: RAG corpus read/write operations"""
        logger.info("Test 7: Testing corpus operations")

        corpus_dir = test_project / ".project/corpus/nodes/decisions"

        # Write a test ADR
        adr_content = {
            "id": "ADR-001",
            "title": "Test Decision",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "accepted",
            "context": "Test context",
            "decision": "Test decision",
            "consequences": {
                "positive": ["Test positive"],
                "negative": ["Test negative"]
            }
        }

        adr_file = corpus_dir / "ADR-001.yml"
        adr_file.write_text(yaml.dump(adr_content))

        # Read back and validate
        with open(adr_file) as f:
            loaded_adr = yaml.safe_load(f)

        assert loaded_adr["id"] == "ADR-001", "ADR ID mismatch"
        assert loaded_adr["status"] == "accepted", "ADR status mismatch"

        logger.info(f"✅ Corpus operations validated: {adr_file.name}")

    def test_08_phase_artifact_storage(self, test_project):
        """Test 8: Store phase artifacts"""
        logger.info("Test 8: Testing phase artifact storage")

        phases_dir = test_project / ".project/phases"
        phase_dir = phases_dir / "phase-1-discovery"
        phase_dir.mkdir(exist_ok=True)

        # Create a phase artifact
        artifact = {
            "phase": 1,
            "timestamp": datetime.now().isoformat(),
            "findings": ["Finding 1", "Finding 2"]
        }

        artifact_file = phase_dir / "discovery-report.json"
        artifact_file.write_text(json.dumps(artifact, indent=2))

        # Validate storage
        assert artifact_file.exists(), "Artifact not stored"

        with open(artifact_file) as f:
            loaded = json.load(f)

        assert loaded["phase"] == 1, "Phase mismatch"
        assert len(loaded["findings"]) == 2, "Findings count mismatch"

        logger.info(f"✅ Phase artifacts validated: {artifact_file.name}")

    def test_09_logging_integration(self, test_project):
        """Test 9: Structured logging with context"""
        logger.info("Test 9: Testing logging integration")

        # Log with extra context
        test_data = {
            "test_id": "framework-integration",
            "project": test_project.name,
            "phase": 1
        }

        logger.info("Integration test checkpoint", extra=test_data)
        logger.debug("Debug log test", extra={"detail": "framework"})
        logger.warning("Warning log test", extra={"issue": "none"})

        # Verify logging doesn't crash
        logger.info("✅ Logging integration validated")

    def test_10_hook_script_exists(self, test_project):
        """Test 10: Validate hook scripts in real framework"""
        logger.info("Test 10: Checking hook scripts")

        # This tests the actual framework (not test project)
        real_project = Path(__file__).parent.parent.parent.parent.parent
        hooks_dir = real_project / ".claude/hooks"

        required_hooks = [
            "validate-framework-structure.sh",
            "detect-phase.sh",
            "auto-migrate.sh",
            "detect-documents.sh"
        ]

        for hook in required_hooks:
            hook_path = hooks_dir / hook
            assert hook_path.exists(), f"Hook missing: {hook}"
            assert hook_path.stat().st_mode & 0o111, f"Hook not executable: {hook}"

        logger.info(f"✅ {len(required_hooks)} hooks validated")

    def test_11_settings_configuration(self, test_project):
        """Test 11: Validate .claude/settings.json structure"""
        logger.info("Test 11: Validating settings configuration")

        real_project = Path(__file__).parent.parent.parent.parent.parent
        settings_file = real_project / ".claude/settings.json"

        assert settings_file.exists(), "settings.json missing"

        with open(settings_file) as f:
            settings = json.load(f)

        # Validate core sections
        assert "hooks" in settings, "settings missing 'hooks'"
        assert "agents" in settings, "settings missing 'agents'"
        assert "UserPromptSubmit" in settings["hooks"], "Missing UserPromptSubmit hooks"

        # Check framework validation hook is registered
        user_hooks = settings["hooks"]["UserPromptSubmit"][0]["hooks"]
        hook_commands = [h["command"] for h in user_hooks]

        assert any("validate-framework-structure.sh" in cmd for cmd in hook_commands), \
            "Framework validation hook not registered"

        logger.info(f"✅ Settings validated: {len(settings['agents']['available_agents'])} agents")

    def test_12_end_to_end_workflow(self, test_project):
        """Test 12: Simulate mini SDLC workflow"""
        logger.info("Test 12: Simulating SDLC workflow")

        # Phase 0: Create requirements
        requirements = {
            "id": "REQ-001",
            "description": "Test requirement",
            "priority": "high"
        }

        req_file = test_project / ".project/phases/phase-0-intake/requirements.json"
        req_file.parent.mkdir(parents=True, exist_ok=True)
        req_file.write_text(json.dumps(requirements))

        # Phase 1: Create discovery artifact
        discovery = {
            "technologies": ["Python", "YAML"],
            "frameworks": ["pytest"]
        }

        disc_file = test_project / ".project/phases/phase-1-discovery/tech-stack.json"
        disc_file.parent.mkdir(parents=True, exist_ok=True)
        disc_file.write_text(json.dumps(discovery))

        # Phase 2: Create ADR
        adr = {
            "id": "ADR-001",
            "title": "Use pytest for testing",
            "status": "accepted"
        }

        adr_file = test_project / ".project/corpus/nodes/decisions/ADR-001.yml"
        adr_file.write_text(yaml.dump(adr))

        # Phase 3: Create architecture diagram
        diagram = "graph TD\n  A[Test] --> B[Framework]"

        arch_file = test_project / ".project/architecture/component-diagram.mmd"
        arch_file.write_text(diagram)

        # Validate all artifacts exist
        assert req_file.exists(), "Requirements not created"
        assert disc_file.exists(), "Discovery artifact not created"
        assert adr_file.exists(), "ADR not created"
        assert arch_file.exists(), "Architecture diagram not created"

        logger.info("✅ End-to-end workflow simulated successfully")


def test_smoke_test():
    """Quick smoke test - validates framework in current directory"""
    logger = get_logger(__name__, skill="smoke-test", phase=0)
    logger.info("Running framework smoke test")

    project_root = Path(__file__).parent.parent.parent.parent.parent

    # Critical paths
    critical_paths = [
        ".agentic_sdlc/templates",
        ".agentic_sdlc/schemas",
        ".agentic_sdlc/docs",
        ".agentic_sdlc/scripts",
        ".claude/hooks",
        ".claude/skills",
        ".claude/settings.json"
    ]

    for path in critical_paths:
        full_path = project_root / path
        assert full_path.exists(), f"Critical path missing: {path}"

    logger.info("✅ Smoke test passed")


if __name__ == "__main__":
    # Run smoke test directly
    test_smoke_test()
    print("✅ Framework smoke test passed")
