#!/usr/bin/env python3
"""
Integration tests for document-enricher skill

Tests the complete enrichment workflow from search to graph update.
"""

import sys
import pytest
import json
import yaml
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from find_related import find_related_documents
from enrich import enrich_document
from update_index import update_index, update_graph, validate_graph_integrity


class TestEndToEndEnrichment:
    """End-to-end enrichment workflow tests."""

    @pytest.fixture
    def test_environment(self, tmp_path):
        """Set up complete test environment."""
        # Create directory structure
        references_dir = tmp_path / "references" / "technical"
        references_dir.mkdir(parents=True)

        corpus_dir = tmp_path / "corpus" / "nodes" / "learnings"
        corpus_dir.mkdir(parents=True)

        # Create index file
        index_path = references_dir.parent / "_index.yml"
        index_data = {
            "documents": [
                {
                    "id": "DOC-001",
                    "path": str(references_dir / "oauth2-spec.pdf"),
                    "title": "OAuth 2.0 Specification",
                    "keywords": ["oauth", "authentication", "authorization", "security"],
                    "summary": "OAuth 2.0 authorization framework specification",
                    "category": "technical"
                },
                {
                    "id": "DOC-002",
                    "path": str(references_dir / "database-guide.pdf"),
                    "title": "Database Best Practices",
                    "keywords": ["database", "postgresql", "performance"],
                    "summary": "Guide to database design and optimization",
                    "category": "technical"
                }
            ]
        }

        with open(index_path, 'w') as f:
            yaml.dump(index_data, f)

        # Create graph file
        graph_path = tmp_path / "corpus" / "graph.json"
        graph_data = {
            "nodes": [
                {"id": "DOC-001", "type": "document", "title": "OAuth 2.0 Specification"},
                {"id": "DOC-002", "type": "document", "title": "Database Best Practices"}
            ],
            "edges": []
        }

        with open(graph_path, 'w') as f:
            json.dump(graph_data, f)

        # Create dummy document files
        (references_dir / "oauth2-spec.pdf").write_text("OAuth 2.0 content")
        (references_dir / "database-guide.pdf").write_text("Database content")

        return {
            "tmp_path": tmp_path,
            "index_path": index_path,
            "graph_path": graph_path,
            "references_dir": references_dir,
            "corpus_dir": corpus_dir
        }

    def test_complete_enrichment_workflow(self, test_environment):
        """Test complete enrichment workflow from search to graph update."""
        env = test_environment

        # Step 1: Find related documents
        prompt = "Research OAuth 2.1 migration best practices"
        results = find_related_documents(
            prompt,
            env["index_path"],
            min_similarity=0.1  # Lower threshold for test
        )

        # Should find DOC-001 (OAuth related)
        assert len(results) > 0
        doc_id, similarity, doc_metadata = results[0]
        assert doc_id == "DOC-001"
        assert similarity > 0.1  # Lower threshold since hybrid search may return lower scores

        # Step 2: Prepare research data
        research_data = {
            "prompt": prompt,
            "topic": "OAuth 2.1 migration",
            "findings": "OAuth 2.1 consolidates OAuth 2.0 best practices including:\n- Mandatory PKCE\n- Removal of Implicit Flow\n- Enhanced security recommendations",
            "sources": [
                {
                    "url": "https://oauth.net/2.1/",
                    "title": "OAuth 2.1 Draft",
                    "accessed_at": "2026-01-22T14:30:00Z"
                }
            ],
            "keywords": ["oauth", "oauth2.1", "migration", "pkce", "security"]
        }

        # Step 3: Enrich document
        enrichment_result = enrich_document(
            doc_id,
            doc_metadata,
            research_data,
            agent="domain-researcher",
            phase=1,
            similarity=similarity,
            index_path=env["index_path"]
        )

        # Verify enrichment result structure
        assert "enriched_content" in enrichment_result
        assert "corpus_node" in enrichment_result
        assert "metadata" in enrichment_result

        metadata = enrichment_result["metadata"]
        assert "enrichment_id" in metadata
        assert metadata["enrichment_id"].startswith("ENRICH-")
        assert metadata["version"] == 1

        # Step 4: Save corpus node
        corpus_file = env["corpus_dir"] / f"{metadata['enrichment_id']}.yml"
        with open(corpus_file, 'w') as f:
            yaml.dump(enrichment_result["corpus_node"], f)

        # Step 5: Save enriched Markdown
        enriched_file = env["references_dir"] / metadata["enriched_file"]
        with open(enriched_file, 'w') as f:
            f.write(enrichment_result["enriched_content"])

        # Verify enriched file exists
        assert enriched_file.exists()
        content = enriched_file.read_text()
        assert "OAuth 2.0 Specification - Enhanced Research Edition" in content
        assert "OAuth 2.1 migration" in content

        # Step 6: Update index
        # Fix metadata corpus_node path to be relative
        metadata["corpus_node"] = str(corpus_file.relative_to(env["tmp_path"]))

        result = update_index(metadata, env["index_path"])
        assert result is True

        # Verify index update
        with open(env["index_path"], 'r') as f:
            index_data = yaml.safe_load(f)

        doc = [d for d in index_data["documents"] if d["id"] == "DOC-001"][0]
        assert "enrichments" in doc
        assert len(doc["enrichments"]) == 1
        assert doc["enrichments"][0]["enrichment_id"] == metadata["enrichment_id"]

        # Step 7: Update graph
        result = update_graph(metadata, env["graph_path"])
        assert result is True

        # Verify graph update
        with open(env["graph_path"], 'r') as f:
            graph_data = json.load(f)

        # Should have enrichment node
        enrichment_nodes = [n for n in graph_data["nodes"] if n["id"] == metadata["enrichment_id"]]
        assert len(enrichment_nodes) == 1
        assert enrichment_nodes[0]["type"] == "enrichment"

        # Should have enriches edge
        enriches_edges = [
            e for e in graph_data["edges"]
            if e["source"] == metadata["enrichment_id"] and e["target"] == "DOC-001"
        ]
        assert len(enriches_edges) == 1
        assert enriches_edges[0]["type"] == "enriches"

        # Step 8: Validate graph integrity
        result = validate_graph_integrity(env["graph_path"])
        assert result is True

    def test_multiple_enrichments_same_document(self, test_environment):
        """Test multiple enrichments for the same document."""
        env = test_environment

        # First enrichment
        research_data1 = {
            "prompt": "Research OAuth 2.1 migration",
            "topic": "OAuth 2.1 migration",
            "findings": "OAuth 2.1 findings...",
            "sources": [{"url": "https://oauth.net/2.1/", "title": "OAuth 2.1", "accessed_at": "2026-01-22"}],
            "keywords": ["oauth2.1"]
        }

        doc_metadata = {
            "id": "DOC-001",
            "title": "OAuth 2.0 Specification",
            "path": str(env["references_dir"] / "oauth2-spec.pdf"),
            "keywords": ["oauth"]
        }

        result1 = enrich_document("DOC-001", doc_metadata, research_data1, index_path=env["index_path"])

        # Save corpus node
        corpus_file1 = env["corpus_dir"] / f"{result1['metadata']['enrichment_id']}.yml"
        with open(corpus_file1, 'w') as f:
            yaml.dump(result1["corpus_node"], f)

        # Fix path
        result1["metadata"]["corpus_node"] = str(corpus_file1.relative_to(env["tmp_path"]))

        update_index(result1["metadata"], env["index_path"])

        # Second enrichment
        research_data2 = {
            "prompt": "Research OAuth PKCE implementation",
            "topic": "OAuth PKCE",
            "findings": "PKCE implementation details...",
            "sources": [{"url": "https://oauth.net/pkce/", "title": "PKCE", "accessed_at": "2026-01-23"}],
            "keywords": ["pkce", "oauth"]
        }

        result2 = enrich_document("DOC-001", doc_metadata, research_data2, index_path=env["index_path"])

        # Save corpus node
        corpus_file2 = env["corpus_dir"] / f"{result2['metadata']['enrichment_id']}.yml"
        with open(corpus_file2, 'w') as f:
            yaml.dump(result2["corpus_node"], f)

        # Fix path
        result2["metadata"]["corpus_node"] = str(corpus_file2.relative_to(env["tmp_path"]))

        update_index(result2["metadata"], env["index_path"])

        # Verify both enrichments in index
        with open(env["index_path"], 'r') as f:
            index_data = yaml.safe_load(f)

        doc = [d for d in index_data["documents"] if d["id"] == "DOC-001"][0]
        assert len(doc["enrichments"]) == 2
        assert doc["enrichments"][0]["version"] == 1
        assert doc["enrichments"][1]["version"] == 2

    def test_no_related_documents_found(self, test_environment):
        """Test workflow when no related documents are found."""
        env = test_environment

        # Search for unrelated topic
        prompt = "Research Kubernetes deployment strategies"
        results = find_related_documents(
            prompt,
            env["index_path"],
            min_similarity=0.6
        )

        # Should not find related documents
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
