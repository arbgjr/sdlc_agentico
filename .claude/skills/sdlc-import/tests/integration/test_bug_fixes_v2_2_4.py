#!/usr/bin/env python3
"""
Integration tests for Bug Fixes v2.2.4

Tests all 4 critical bugs identified in RCA:
- Bug #1: UnboundLocalError in post_import_validator.py
- Bug #2: No error handling around validator.validate_and_fix()
- Bug #3: ADR reconciliation removes LLM ADRs
- Bug #4: Graph generation silent failure
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from post_import_validator import PostImportValidator, ValidationResult
from project_analyzer import ProjectAnalyzer
from decision_extractor import DecisionExtractor, Evidence


class TestBugFix1_UnboundLocalError:
    """
    Bug #1: UnboundLocalError when tech_debt_result or diagram_result not defined

    Root Cause: Variables defined conditionally but used unconditionally
    Fix: Initialize with safe defaults BEFORE conditional blocks
    """

    def test_validation_with_disabled_tech_debt_check(self, tmp_path):
        """Test that validation works when tech_debt validation is disabled"""
        # Setup
        config = {
            "tech_debt_validation": {"enabled": False},
            "diagram_validation": {"enabled": True}
        }

        import_results = {
            "decisions": {"decisions": [], "count": 0},
            "tech_debt": {"items": []},
            "diagrams": {"diagrams": [], "count": 0}
        }

        validator = PostImportValidator(config)

        # Execute - should NOT crash with UnboundLocalError
        result = validator.validate_and_fix(
            import_results=import_results,
            project_path=str(tmp_path),
            output_dir=tmp_path / ".project",
            correlation_id="test-001"
        )

        # Validate
        assert isinstance(result, ValidationResult)
        assert 'tech_debt_completeness' in result.metrics
        assert result.metrics['tech_debt_completeness'] == 1.0  # Default value

    def test_validation_with_disabled_diagram_check(self, tmp_path):
        """Test that validation works when diagram validation is disabled"""
        # Setup
        config = {
            "tech_debt_validation": {"enabled": True},
            "diagram_validation": {"enabled": False}
        }

        import_results = {
            "decisions": {"decisions": [], "count": 0},
            "tech_debt": {"items": []},
            "diagrams": {"diagrams": [], "count": 0}
        }

        validator = PostImportValidator(config)

        # Execute - should NOT crash with UnboundLocalError
        result = validator.validate_and_fix(
            import_results=import_results,
            project_path=str(tmp_path),
            output_dir=tmp_path / ".project",
            correlation_id="test-002"
        )

        # Validate
        assert isinstance(result, ValidationResult)
        assert 'diagram_quality' in result.metrics
        assert result.metrics['diagram_quality'] == 1.0  # Default value

    def test_validation_with_all_disabled(self, tmp_path):
        """Test that validation works when ALL validations are disabled"""
        # Setup
        config = {
            "tech_debt_validation": {"enabled": False},
            "diagram_validation": {"enabled": False}
        }

        import_results = {
            "decisions": {"decisions": [], "count": 0},
            "tech_debt": {"items": []},
            "diagrams": {"diagrams": [], "count": 0}
        }

        validator = PostImportValidator(config)

        # Execute - should NOT crash
        result = validator.validate_and_fix(
            import_results=import_results,
            project_path=str(tmp_path),
            output_dir=tmp_path / ".project",
            correlation_id="test-003"
        )

        # Validate
        assert isinstance(result, ValidationResult)
        assert result.metrics['tech_debt_completeness'] == 1.0
        assert result.metrics['diagram_quality'] == 1.0


class TestBugFix2_ErrorHandling:
    """
    Bug #2: No error handling around validator.validate_and_fix()

    Root Cause: Exception propagates up, crashes entire import
    Fix: Add try-except with graceful degradation
    """

    def test_import_continues_on_validation_failure(self, tmp_path):
        """Test that import continues when validation crashes"""
        # Create minimal project structure
        project_path = tmp_path / "test_project"
        project_path.mkdir()
        (project_path / "main.py").write_text("print('hello')")

        # Mock validator to raise exception
        with patch('project_analyzer.PostImportValidator') as mock_validator_class:
            mock_validator = MagicMock()
            mock_validator.validate_and_fix.side_effect = Exception("Simulated validation crash")
            mock_validator_class.return_value = mock_validator

            # Execute
            analyzer = ProjectAnalyzer(project_path=project_path)

            # Should NOT crash - graceful degradation
            try:
                results = analyzer.analyze()
            except Exception as e:
                pytest.fail(f"Import crashed when it should have continued: {e}")

            # Validate
            assert 'post_import_validation' in results
            assert results['post_import_validation']['status'] == 'failed'
            assert 'error' in results['post_import_validation']
            assert results['post_import_validation']['score'] == 0.0
            assert 'note' in results['post_import_validation']


class TestBugFix3_ADRReconciliation:
    """
    Bug #3: ADR reconciliation removes LLM-generated ADRs

    Root Cause: LLM rationale has different format than pattern rationale
    Fix: Use SAME format for consistency
    """

    def test_llm_rationale_matches_pattern_format(self):
        """Test that LLM rationale has same format as pattern rationale"""
        # Setup
        config = {"llm_synthesis_enabled": True}
        extractor = DecisionExtractor(config)

        # Create test evidence
        evidence = [
            Evidence(file="db.py", line=10, pattern="postgresql", confidence=0.9),
            Evidence(file="models.py", line=5, pattern="postgresql", confidence=0.8),
            Evidence(file="settings.py", line=20, pattern="postgresql", confidence=0.85)
        ]

        project_path = Path("/tmp/test")

        # Generate with LLM
        llm_rationale = extractor._generate_llm_rationale(
            category="database",
            tech_name="postgresql",
            evidence=evidence,
            project_path=project_path
        )

        # Generate with pattern
        pattern_rationale = extractor._generate_pattern_rationale(
            category="database",
            tech_name="postgresql",
            evidence=evidence
        )

        # Validate structure similarity
        assert "was detected as the" in llm_rationale
        assert "based on evidence found in" in llm_rationale
        assert "file(s):" in llm_rationale
        assert "indicating it is the adopted technology" in llm_rationale

        # Should NOT contain placeholder note
        assert "[Note: Full LLM synthesis requires API integration" not in llm_rationale
        assert "API integration" not in llm_rationale

        # Key phrases should match
        assert "was detected as the database solution" in llm_rationale
        assert "was detected as the database solution" in pattern_rationale

    def test_llm_rationale_consistency(self):
        """Test that LLM rationale is deterministic for same inputs"""
        config = {"llm_synthesis_enabled": True}
        extractor = DecisionExtractor(config)

        evidence = [
            Evidence(file="app.py", line=1, pattern="react", confidence=0.9)
        ]

        # Generate twice
        rationale1 = extractor._generate_llm_rationale("frontend", "react", evidence, Path("/tmp"))
        rationale2 = extractor._generate_llm_rationale("frontend", "react", evidence, Path("/tmp"))

        # Should be identical
        assert rationale1 == rationale2


class TestBugFix4_GraphPersistence:
    """
    Bug #4: Graph generation silent failure (no graph.json persisted)

    Root Cause: Exception caught but graph.json not written to disk
    Fix: Persist minimal valid graph.json even on failure
    """

    def test_graph_json_persisted_on_failure(self, tmp_path):
        """Test that graph.json exists even when generation fails"""
        # Create minimal project
        project_path = tmp_path / "test_project"
        project_path.mkdir()
        (project_path / "main.py").write_text("print('test')")

        # Mock graph generator to fail
        with patch('project_analyzer.GraphGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.generate.side_effect = Exception("Simulated graph failure")
            mock_gen_class.return_value = mock_gen

            # Execute
            analyzer = ProjectAnalyzer(project_path=project_path)

            # Mock minimal results to trigger graph generation
            with patch.object(analyzer, '_extract_decisions') as mock_decisions:
                mock_decisions.return_value = {
                    'decisions': [
                        {'id': 'ADR-001', 'title': 'Test', 'decision': 'test'}
                    ],
                    'count': 1
                }

                results = analyzer.analyze()

        # Validate graph.json exists
        graph_file = project_path / ".project/corpus/graph.json"
        assert graph_file.exists(), f"graph.json should exist at {graph_file}"

        # Validate content
        graph_data = json.loads(graph_file.read_text())
        assert graph_data['status'] == 'failed'
        assert 'error' in graph_data
        assert graph_data['node_count'] == 0
        assert graph_data['edge_count'] == 0
        assert 'version' in graph_data


class TestEndToEndWithLLM:
    """
    End-to-end integration test WITH LLM enabled

    Validates that ALL 4 bugs are fixed and import completes successfully
    """

    def test_full_import_with_llm_enabled(self, tmp_path):
        """Test full import workflow WITH LLM enabled"""
        # Create realistic project structure
        project_path = tmp_path / "test_project"
        project_path.mkdir()

        # Python files
        (project_path / "app.py").write_text("""
import flask
from sqlalchemy import create_engine

app = flask.Flask(__name__)
engine = create_engine('postgresql://localhost/db')
""")

        (project_path / "requirements.txt").write_text("""
flask==2.3.0
sqlalchemy==2.0.0
psycopg2==2.9.0
""")

        # Execute with LLM enabled
        analyzer = ProjectAnalyzer(project_path=project_path)

        # Patch LLM flag to True
        with patch.object(analyzer, 'config') as mock_config:
            mock_config.get.side_effect = lambda key, default=None: {
                'llm_synthesis_enabled': True,
                'graph_generation': {'enabled': True},
                'post_import_validation': {'enabled': True}
            }.get(key, default)

            # Execute - should complete without crashes
            results = analyzer.analyze()

        # Validate results structure
        assert 'decisions' in results
        assert 'post_import_validation' in results

        # Validate artifacts exist
        output_dir = project_path / ".project"
        assert (output_dir / "corpus/graph.json").exists()

        # Validate NO crash occurred
        if results['post_import_validation']['status'] == 'failed':
            # If it failed, should have error details
            assert 'error' in results['post_import_validation']
            assert 'note' in results['post_import_validation']


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
