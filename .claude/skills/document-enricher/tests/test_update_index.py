#!/usr/bin/env python3
"""
Unit tests for update_index.py
"""

import sys
import pytest
import json
import yaml
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from update_index import (
    update_index,
    update_graph,
    validate_graph_integrity
)


class TestUpdateIndex:
    """Test index update functionality."""

    @pytest.fixture
    def temp_index(self, tmp_path):
        """Create temporary index with sample data."""
        index_path = tmp_path / "_index.yml"
        index_data = {
            "documents": [
                {
                    "id": "DOC-001",
                    "path": "references/oauth2.pdf",
                    "title": "OAuth 2.0 Spec",
                    "keywords": ["oauth"],
                    "enrichments": []
                }
            ]
        }

        with open(index_path, 'w') as f:
            yaml.dump(index_data, f)

        return index_path

    @pytest.fixture
    def temp_corpus_node(self, tmp_path):
        """Create temporary corpus node."""
        corpus_dir = tmp_path / "corpus" / "nodes" / "learnings"
        corpus_dir.mkdir(parents=True)

        corpus_file = corpus_dir / "ENRICH-001.yml"
        corpus_data = {
            "id": "ENRICH-001",
            "type": "enrichment",
            "source_document": {
                "id": "DOC-001",
                "path": "references/oauth2.pdf"
            }
        }

        with open(corpus_file, 'w') as f:
            yaml.dump(corpus_data, f)

        return corpus_file

    def test_add_first_enrichment(self, temp_index, temp_corpus_node, tmp_path):
        """Test adding first enrichment to document."""
        enrichment_metadata = {
            "enrichment_id": "ENRICH-001",
            "enriched_at": "2026-01-22T14:30:00Z",
            "research_topic": "OAuth 2.1 migration",
            "agent": "domain-researcher",
            "phase": 1,
            "corpus_node": str(temp_corpus_node.relative_to(tmp_path)),
            "enriched_file": "oauth2.enriched.v1.md",
            "version": 1,
            "similarity": 0.85
        }

        # Update index
        result = update_index(enrichment_metadata, temp_index)
        assert result is True

        # Verify update
        with open(temp_index, 'r') as f:
            index_data = yaml.safe_load(f)

        doc = index_data["documents"][0]
        assert "enrichments" in doc
        assert len(doc["enrichments"]) == 1
        assert doc["enrichments"][0]["enrichment_id"] == "ENRICH-001"
        assert doc["enrichments"][0]["version"] == 1

    def test_add_multiple_enrichments(self, temp_index, temp_corpus_node, tmp_path):
        """Test adding multiple enrichments to same document."""
        # Add first enrichment
        enrichment1 = {
            "enrichment_id": "ENRICH-001",
            "enriched_at": "2026-01-22T14:30:00Z",
            "research_topic": "OAuth 2.1",
            "agent": "domain-researcher",
            "phase": 1,
            "corpus_node": str(temp_corpus_node.relative_to(tmp_path)),
            "enriched_file": "oauth2.enriched.v1.md",
            "version": 1,
            "similarity": 0.85
        }

        update_index(enrichment1, temp_index)

        # Create second corpus node
        corpus_file2 = temp_corpus_node.parent / "ENRICH-002.yml"
        corpus_data2 = {
            "id": "ENRICH-002",
            "type": "enrichment",
            "source_document": {
                "id": "DOC-001",
                "path": "references/oauth2.pdf"
            }
        }
        with open(corpus_file2, 'w') as f:
            yaml.dump(corpus_data2, f)

        # Add second enrichment
        enrichment2 = {
            "enrichment_id": "ENRICH-002",
            "enriched_at": "2026-01-23T10:00:00Z",
            "research_topic": "OAuth PKCE",
            "agent": "domain-researcher",
            "phase": 1,
            "corpus_node": str(corpus_file2.relative_to(tmp_path)),
            "enriched_file": "oauth2.enriched.v2.md",
            "version": 2,
            "similarity": 0.78
        }

        update_index(enrichment2, temp_index)

        # Verify both enrichments
        with open(temp_index, 'r') as f:
            index_data = yaml.safe_load(f)

        doc = index_data["documents"][0]
        assert len(doc["enrichments"]) == 2
        assert doc["enrichments"][0]["enrichment_id"] == "ENRICH-001"
        assert doc["enrichments"][1]["enrichment_id"] == "ENRICH-002"


class TestUpdateGraph:
    """Test graph update functionality."""

    @pytest.fixture
    def temp_graph(self, tmp_path):
        """Create temporary graph file."""
        graph_path = tmp_path / "graph.json"
        graph_data = {
            "nodes": [
                {
                    "id": "DOC-001",
                    "type": "document",
                    "title": "OAuth 2.0 Spec"
                }
            ],
            "edges": []
        }

        with open(graph_path, 'w') as f:
            json.dump(graph_data, f)

        return graph_path

    @pytest.fixture
    def temp_corpus_node_for_graph(self, tmp_path):
        """Create temporary corpus node for graph tests."""
        corpus_dir = tmp_path / "corpus" / "nodes" / "learnings"
        corpus_dir.mkdir(parents=True)

        corpus_file = corpus_dir / "ENRICH-001.yml"
        corpus_data = {
            "id": "ENRICH-001",
            "type": "enrichment",
            "title": "OAuth Enhanced",
            "created_at": "2026-01-22T14:30:00Z",
            "source_document": {
                "id": "DOC-001",
                "path": "references/oauth2.pdf"
            }
        }

        with open(corpus_file, 'w') as f:
            yaml.dump(corpus_data, f)

        return corpus_file

    def test_add_enrichment_to_graph(self, temp_graph, temp_corpus_node_for_graph, tmp_path):
        """Test adding enrichment node and edge to graph."""
        enrichment_metadata = {
            "enrichment_id": "ENRICH-001",
            "enriched_at": "2026-01-22T14:30:00Z",
            "corpus_node": str(temp_corpus_node_for_graph.relative_to(tmp_path))
        }

        result = update_graph(enrichment_metadata, temp_graph)
        assert result is True

        # Verify graph update
        with open(temp_graph, 'r') as f:
            graph_data = json.load(f)

        # Should have 2 nodes (DOC-001 + ENRICH-001)
        assert len(graph_data["nodes"]) == 2
        enrichment_node = [n for n in graph_data["nodes"] if n["id"] == "ENRICH-001"][0]
        assert enrichment_node["type"] == "enrichment"
        assert enrichment_node["title"] == "OAuth Enhanced"

        # Should have 1 edge (ENRICH-001 → DOC-001)
        assert len(graph_data["edges"]) == 1
        edge = graph_data["edges"][0]
        assert edge["source"] == "ENRICH-001"
        assert edge["target"] == "DOC-001"
        assert edge["type"] == "enriches"

    def test_idempotent_graph_update(self, temp_graph, temp_corpus_node_for_graph, tmp_path):
        """Test that updating graph twice doesn't duplicate nodes/edges."""
        enrichment_metadata = {
            "enrichment_id": "ENRICH-001",
            "enriched_at": "2026-01-22T14:30:00Z",
            "corpus_node": str(temp_corpus_node_for_graph.relative_to(tmp_path))
        }

        # Update twice
        update_graph(enrichment_metadata, temp_graph)
        update_graph(enrichment_metadata, temp_graph)

        # Verify no duplicates
        with open(temp_graph, 'r') as f:
            graph_data = json.load(f)

        # Should still have 2 nodes (not 3)
        assert len(graph_data["nodes"]) == 2
        # Should still have 1 edge (not 2)
        assert len(graph_data["edges"]) == 1


class TestValidateGraphIntegrity:
    """Test graph integrity validation."""

    def test_valid_graph(self, tmp_path):
        """Test validation of valid graph."""
        graph_path = tmp_path / "graph.json"
        graph_data = {
            "nodes": [
                {"id": "DOC-001", "type": "document"},
                {"id": "ENRICH-001", "type": "enrichment"}
            ],
            "edges": [
                {"source": "ENRICH-001", "target": "DOC-001", "type": "enriches"}
            ]
        }

        with open(graph_path, 'w') as f:
            json.dump(graph_data, f)

        result = validate_graph_integrity(graph_path)
        assert result is True

    def test_orphan_source(self, tmp_path):
        """Test validation fails with orphan source node."""
        graph_path = tmp_path / "graph.json"
        graph_data = {
            "nodes": [
                {"id": "DOC-001", "type": "document"}
            ],
            "edges": [
                {"source": "ENRICH-999", "target": "DOC-001", "type": "enriches"}
            ]
        }

        with open(graph_path, 'w') as f:
            json.dump(graph_data, f)

        result = validate_graph_integrity(graph_path)
        assert result is False

    def test_orphan_target(self, tmp_path):
        """Test validation fails with orphan target node."""
        graph_path = tmp_path / "graph.json"
        graph_data = {
            "nodes": [
                {"id": "ENRICH-001", "type": "enrichment"}
            ],
            "edges": [
                {"source": "ENRICH-001", "target": "DOC-999", "type": "enriches"}
            ]
        }

        with open(graph_path, 'w') as f:
            json.dump(graph_data, f)

        result = validate_graph_integrity(graph_path)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
