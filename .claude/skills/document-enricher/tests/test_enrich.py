#!/usr/bin/env python3
"""
Unit tests for enrich.py
"""

import sys
import pytest
import json
import yaml
from pathlib import Path
from datetime import datetime, timezone

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from enrich import (
    generate_enrichment_id,
    get_next_version,
    generate_synthesis,
    create_enrichment_node,
    generate_enriched_markdown
)


class TestGenerateEnrichmentId:
    """Test enrichment ID generation."""

    def test_first_enrichment(self, tmp_path):
        """Test generating first enrichment ID."""
        # Create empty corpus directory
        corpus_dir = tmp_path / "corpus" / "nodes" / "learnings"
        corpus_dir.mkdir(parents=True)

        index_path = tmp_path / "_index.yml"

        enrichment_id = generate_enrichment_id(index_path)
        assert enrichment_id == "ENRICH-001"

    def test_incremental_enrichment(self, tmp_path):
        """Test generating incremental enrichment IDs."""
        # Create corpus directory with existing enrichments
        corpus_dir = tmp_path / "corpus" / "nodes" / "learnings"
        corpus_dir.mkdir(parents=True)

        # Create existing enrichment files
        (corpus_dir / "ENRICH-001.yml").touch()
        (corpus_dir / "ENRICH-002.yml").touch()
        (corpus_dir / "ENRICH-005.yml").touch()

        # Create index in correct location relative to corpus
        index_path = tmp_path / "references" / "_index.yml"
        index_path.parent.mkdir(parents=True)

        enrichment_id = generate_enrichment_id(index_path)
        # Should be max + 1 = 006
        assert enrichment_id == "ENRICH-006"


class TestGetNextVersion:
    """Test version number generation."""

    def test_first_version(self, tmp_path):
        """Test getting first version for document."""
        index_path = tmp_path / "_index.yml"
        index_data = {
            "documents": [
                {
                    "id": "DOC-001",
                    "enrichments": []
                }
            ]
        }

        with open(index_path, 'w') as f:
            yaml.dump(index_data, f)

        version = get_next_version("DOC-001", index_path)
        assert version == 1

    def test_incremental_version(self, tmp_path):
        """Test getting next version for document with existing enrichments."""
        index_path = tmp_path / "_index.yml"
        index_data = {
            "documents": [
                {
                    "id": "DOC-001",
                    "enrichments": [
                        {"version": 1, "enrichment_id": "ENRICH-001"},
                        {"version": 2, "enrichment_id": "ENRICH-002"}
                    ]
                }
            ]
        }

        with open(index_path, 'w') as f:
            yaml.dump(index_data, f)

        version = get_next_version("DOC-001", index_path)
        assert version == 3

    def test_document_not_found(self, tmp_path):
        """Test version for non-existent document."""
        index_path = tmp_path / "_index.yml"
        index_data = {"documents": []}

        with open(index_path, 'w') as f:
            yaml.dump(index_data, f)

        version = get_next_version("DOC-999", index_path)
        assert version == 1


class TestGenerateSynthesis:
    """Test synthesis generation."""

    def test_basic_synthesis(self):
        """Test basic synthesis generation."""
        original = "OAuth 2.0 is an authorization framework."
        research = "OAuth 2.1 consolidates security best practices."

        synthesis = generate_synthesis(original, research)

        # Should contain both original and research
        assert "OAuth 2.0" in synthesis or "original" in synthesis.lower()
        assert "OAuth 2.1" in synthesis or "research" in synthesis.lower()
        assert "synthesis" in synthesis.lower() or "combined" in synthesis.lower()

    def test_empty_inputs(self):
        """Test synthesis with empty inputs."""
        synthesis = generate_synthesis("", "")

        # Should still have structure
        assert "Combined Analysis" in synthesis or "synthesis" in synthesis.lower()


class TestCreateEnrichmentNode:
    """Test corpus node creation."""

    def test_node_structure(self):
        """Test that enrichment node has correct structure."""
        doc_metadata = {
            "id": "DOC-001",
            "title": "OAuth 2.0 Spec",
            "path": "oauth2.pdf",
            "keywords": ["oauth", "auth"]
        }

        research_data = {
            "prompt": "Research OAuth 2.1",
            "topic": "OAuth 2.1 migration",
            "findings": "OAuth 2.1 consolidates...",
            "sources": [
                {"url": "https://oauth.net", "title": "OAuth Site", "accessed_at": "2026-01-22"}
            ],
            "keywords": ["oauth2.1"]
        }

        node = create_enrichment_node(
            enrichment_id="ENRICH-001",
            doc_metadata=doc_metadata,
            research_data=research_data,
            original_summary="Original summary",
            synthesis="Combined analysis",
            agent="domain-researcher",
            phase=1,
            similarity=0.85
        )

        # Validate structure
        assert node["id"] == "ENRICH-001"
        assert node["type"] == "enrichment"
        assert node["agent"] == "domain-researcher"
        assert "source_document" in node
        assert node["source_document"]["id"] == "DOC-001"
        assert "research_context" in node
        assert node["research_context"]["phase"] == 1
        assert node["research_context"]["similarity"] == 0.85
        assert "content" in node
        assert "original_summary" in node["content"]
        assert "research_findings" in node["content"]
        assert "synthesis" in node["content"]
        assert "sources" in node["content"]
        assert len(node["content"]["sources"]) == 1
        assert "relations" in node
        assert node["relations"][0]["type"] == "enriches"
        assert node["relations"][0]["target"] == "DOC-001"
        assert "decay_metadata" in node
        assert node["decay_metadata"]["decay_score"] == 1.0
        assert node["decay_metadata"]["decay_status"] == "fresh"


class TestGenerateEnrichedMarkdown:
    """Test Markdown generation."""

    def test_markdown_structure(self):
        """Test that enriched Markdown has correct structure."""
        doc_metadata = {
            "title": "OAuth 2.0 Specification",
            "path": "references/oauth2.pdf"
        }

        research_data = {
            "topic": "OAuth 2.1 migration",
            "findings": "OAuth 2.1 consolidates best practices.",
            "sources": [
                {
                    "url": "https://oauth.net/2.1/",
                    "title": "OAuth 2.1 Draft",
                    "accessed_at": "2026-01-22T14:30:00Z"
                }
            ]
        }

        markdown = generate_enriched_markdown(
            doc_metadata=doc_metadata,
            research_data=research_data,
            original_summary="Original OAuth 2.0 content",
            synthesis="Combined analysis of both versions",
            enrichment_id="ENRICH-001",
            version=1,
            agent="domain-researcher",
            phase=1
        )

        # Validate Markdown structure
        assert "# OAuth 2.0 Specification - Enhanced Research Edition" in markdown
        assert "Original Document" in markdown
        assert "references/oauth2.pdf" in markdown
        assert "Research Topic" in markdown
        assert "OAuth 2.1 migration" in markdown
        assert "**Version**: v1" in markdown  # Bold format
        assert "**Enrichment ID**: ENRICH-001" in markdown  # Bold format
        assert "## Original Content Summary" in markdown
        assert "Original OAuth 2.0 content" in markdown
        assert "## Research Findings" in markdown
        assert "OAuth 2.1 consolidates" in markdown
        assert "### Sources" in markdown
        assert "OAuth 2.1 Draft" in markdown
        assert "https://oauth.net/2.1/" in markdown
        assert "## Synthesis" in markdown
        assert "Combined analysis" in markdown
        assert "🤖 Generated with SDLC Agêntico by @arbgjr" in markdown

    def test_markdown_no_sources(self):
        """Test Markdown generation with no sources."""
        doc_metadata = {"title": "Test Doc", "path": "test.pdf"}
        research_data = {"topic": "Test", "findings": "Findings", "sources": []}

        markdown = generate_enriched_markdown(
            doc_metadata=doc_metadata,
            research_data=research_data,
            original_summary="Summary",
            synthesis="Synthesis",
            enrichment_id="ENRICH-001",
            version=1,
            agent="test-agent",
            phase=1
        )

        # Should not have Sources section if no sources
        # But should still be valid Markdown
        assert "# Test Doc - Enhanced Research Edition" in markdown


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
