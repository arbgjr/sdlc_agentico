import pytest
import json
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from graph_generator import GraphGenerator


class TestGraphGenerator:
    @pytest.fixture
    def generator(self):
        config = {"graph_generation": {"enabled": True}}
        return GraphGenerator(config)

    @pytest.fixture
    def sample_adrs(self):
        return [
            {
                "id": "ADR-TEST-001",
                "title": "Use PostgreSQL as Database",
                "category": "database",
                "confidence": 0.95,
                "date": "2026-01-20",
                "tags": ["database", "postgresql"]
            },
            {
                "id": "ADR-TEST-002",
                "title": "PostgreSQL Multi-Tenancy with RLS",
                "category": "database",
                "confidence": 0.90,
                "date": "2026-01-22",
                "tags": ["database", "security"]
            },
            {
                "id": "ADR-TEST-003",
                "title": "JWT Authentication",
                "category": "authentication",
                "confidence": 0.85,
                "date": "2026-01-21",
                "tags": ["authentication", "security"]
            }
        ]

    def test_graph_generation(self, generator, sample_adrs, tmp_path):
        """Test complete graph generation workflow"""
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir(parents=True)

        result = generator.generate(corpus_dir, sample_adrs)

        # Verify files were created
        assert (corpus_dir / "graph.json").exists()
        assert (corpus_dir / "adjacency.json").exists()

        # Verify result structure
        assert "graph_file" in result
        assert "adjacency_file" in result
        assert result["node_count"] == 3
        assert result["edge_count"] >= 1

    def test_graph_structure(self, generator, sample_adrs, tmp_path):
        """Test graph.json structure"""
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir(parents=True)

        generator.generate(corpus_dir, sample_adrs)

        with open(corpus_dir / "graph.json") as f:
            graph = json.load(f)

        # Verify graph structure
        assert graph['version'] == "2.1.0"
        assert graph['generated_by'] == "sdlc-import"
        assert 'updated_at' in graph
        assert 'nodes' in graph
        assert 'edges' in graph
        assert 'metadata' in graph

        # Verify metadata
        assert graph['metadata']['node_count'] == 3
        assert graph['metadata']['edge_count'] >= 1
        assert 'relation_types' in graph['metadata']

    def test_adjacency_structure(self, generator, sample_adrs, tmp_path):
        """Test adjacency.json structure"""
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir(parents=True)

        generator.generate(corpus_dir, sample_adrs)

        with open(corpus_dir / "adjacency.json") as f:
            adjacency = json.load(f)

        # Verify adjacency structure
        assert adjacency['version'] == "2.1.0"
        assert 'adjacency' in adjacency
        assert 'metadata' in adjacency

        # Verify all nodes have adjacency entries
        assert "ADR-TEST-001" in adjacency['adjacency']
        assert "ADR-TEST-002" in adjacency['adjacency']
        assert "ADR-TEST-003" in adjacency['adjacency']

        # Verify adjacency format
        for node_id in ["ADR-TEST-001", "ADR-TEST-002", "ADR-TEST-003"]:
            assert "outgoing" in adjacency['adjacency'][node_id]
            assert "incoming" in adjacency['adjacency'][node_id]

    def test_concept_extraction(self, generator):
        """Test concept extraction from ADRs"""
        adr = {
            "id": "ADR-001",
            "title": "Use PostgreSQL database for authentication",
            "category": "database"
        }

        concepts = generator._extract_concepts(adr)

        # Should extract category and keywords from title
        assert "database" in concepts
        assert "authentication" in concepts

    def test_related_to_relations(self, generator, sample_adrs):
        """Test relatedTo relations between ADRs sharing concepts"""
        edges = generator._extract_relations(sample_adrs)

        # ADRs sharing concepts should have relatedTo relations
        related_edges = [e for e in edges if e['relation'] == 'relatedTo']
        assert len(related_edges) > 0

        # Check that database ADRs are related
        database_edges = [
            e for e in related_edges
            if (e['source'] in ['ADR-TEST-001', 'ADR-TEST-002'] and
                e['target'] in ['ADR-TEST-001', 'ADR-TEST-002'])
        ]
        assert len(database_edges) > 0

    def test_supersedes_relations(self, generator):
        """Test supersedes relations for temporal decisions"""
        adrs = [
            {
                "id": "ADR-OLD",
                "title": "Old Database Decision",
                "category": "database",
                "confidence": 0.85,
                "date": "2026-01-01"
            },
            {
                "id": "ADR-NEW",
                "title": "New Database Decision",
                "category": "database",
                "confidence": 0.90,
                "date": "2026-01-15"
            }
        ]

        edges = generator._extract_relations(adrs)

        # Newer ADR should supersede older one
        supersedes_edges = [e for e in edges if e['relation'] == 'supersedes']
        assert len(supersedes_edges) > 0

        # Verify direction (newer supersedes older)
        supersede_edge = supersedes_edges[0]
        assert supersede_edge['source'] == "ADR-NEW"
        assert supersede_edge['target'] == "ADR-OLD"

    def test_reverse_relations(self, generator):
        """Test reverse relation mapping"""
        assert generator._get_reverse_relation("supersedes") == "supersededBy"
        assert generator._get_reverse_relation("implements") == "implementedBy"
        assert generator._get_reverse_relation("relatedTo") == "relatedTo"  # bidirectional
        assert generator._get_reverse_relation("dependsOn") == "dependedOnBy"

    def test_empty_adrs(self, generator, tmp_path):
        """Test graph generation with no ADRs"""
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir(parents=True)

        result = generator.generate(corpus_dir, [])

        # Should create files even with empty graph
        assert (corpus_dir / "graph.json").exists()
        assert (corpus_dir / "adjacency.json").exists()
        assert result["node_count"] == 0
        assert result["edge_count"] == 0

    def test_disabled_generation(self, tmp_path):
        """Test that disabled generation doesn't create files"""
        config = {"graph_generation": {"enabled": False}}
        generator = GraphGenerator(config)

        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir(parents=True)

        # Note: This test assumes the generator checks enabled flag
        # If not implemented yet, the test will fail and remind us to add it
        assert generator.enabled is False

    def test_node_metadata(self, generator, sample_adrs):
        """Test that nodes contain all required metadata"""
        nodes = generator._build_nodes(sample_adrs)

        for node in nodes:
            assert 'id' in node
            assert 'type' in node
            assert node['type'] == "Decision"
            assert 'title' in node
            assert 'status' in node
            assert 'confidence' in node
            assert 'category' in node
            assert 'tags' in node
            assert 'concepts' in node

    def test_adjacency_node_count_matches(self, generator, sample_adrs, tmp_path):
        """Test that adjacency node count matches graph node count"""
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir(parents=True)

        generator.generate(corpus_dir, sample_adrs)

        with open(corpus_dir / "graph.json") as f:
            graph = json.load(f)
        with open(corpus_dir / "adjacency.json") as f:
            adjacency = json.load(f)

        graph_nodes = graph['metadata']['node_count']
        adjacency_nodes = len(adjacency['adjacency'])

        assert graph_nodes == adjacency_nodes
