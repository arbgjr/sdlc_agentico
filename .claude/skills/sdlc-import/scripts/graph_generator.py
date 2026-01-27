#!/usr/bin/env python3
"""
Graph Generator - Build semantic knowledge graph from extracted ADRs
Reuses patterns from graph-navigator skill.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timezone
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class GraphGenerator:
    """Generate knowledge graph from ADRs"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('graph_generation', {}).get('enabled', True)

    def generate(self, corpus_dir: Path, extracted_adrs: List[Dict]) -> Dict:
        """Generate graph.json and adjacency.json from extracted ADRs"""
        with log_operation("generate_graph", logger):
            # Build nodes from ADRs
            nodes = self._build_nodes(extracted_adrs)

            # Extract relations from ADRs
            edges = self._extract_relations(extracted_adrs)

            # Build adjacency list for fast traversal
            adjacency = self._build_adjacency(nodes, edges)

            # Create graph.json
            graph = {
                "version": "2.1.0",
                "generated_by": "sdlc-import",
                "updated_at": datetime.now(timezone.utc).isoformat() + "Z",
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "relation_types": list(set(e['relation'] for e in edges))
                }
            }

            # Ensure corpus directory exists
            corpus_dir.mkdir(parents=True, exist_ok=True)

            # Save to corpus
            graph_file = corpus_dir / "graph.json"
            graph_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure parent exists
            with open(graph_file, 'w') as f:
                json.dump(graph, f, indent=2)

            adjacency_file = corpus_dir / "adjacency.json"
            adjacency_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure parent exists
            with open(adjacency_file, 'w') as f:
                json.dump(adjacency, f, indent=2)

            logger.info(
                "Graph generation complete",
                extra={
                    "nodes": len(nodes),
                    "edges": len(edges),
                    "graph_file": str(graph_file),
                    "adjacency_file": str(adjacency_file)
                }
            )

            return {
                "graph_file": str(graph_file),
                "adjacency_file": str(adjacency_file),
                "node_count": len(nodes),
                "edge_count": len(edges)
            }

    def _build_nodes(self, adrs: List[Dict]) -> List[Dict]:
        """Build graph nodes from ADRs"""
        nodes = []

        for adr in adrs:
            node = {
                "id": adr.get('id', 'UNKNOWN'),
                "type": "Decision",
                "title": adr.get('title', ''),
                "status": adr.get('status', 'inferred'),
                "confidence": adr.get('confidence', 0.0),
                "category": adr.get('category', ''),
                "tags": adr.get('tags', []),
                "concepts": self._extract_concepts(adr)
            }
            nodes.append(node)

        return nodes

    def _extract_concepts(self, adr: Dict) -> List[str]:
        """Extract key concepts from ADR for graph relations"""
        concepts = []

        # Extract from category
        category = adr.get('category', '')
        if category:
            concepts.append(category)

        # Extract from title
        title = adr.get('title', '').lower()
        concept_keywords = ['database', 'authentication', 'api', 'caching', 'messaging', 'security']
        for keyword in concept_keywords:
            if keyword in title:
                concepts.append(keyword)

        return list(set(concepts))

    def _extract_relations(self, adrs: List[Dict]) -> List[Dict]:
        """Extract semantic relations between ADRs"""
        edges = []

        # Build concept index for relatedTo relations
        concept_index = {}
        for adr in adrs:
            adr_id = adr.get('id')
            concepts = self._extract_concepts(adr)
            for concept in concepts:
                if concept not in concept_index:
                    concept_index[concept] = []
                concept_index[concept].append(adr_id)

        # Create relatedTo edges for ADRs sharing concepts
        for concept, adr_ids in concept_index.items():
            if len(adr_ids) > 1:
                # Create edges between all ADRs sharing this concept
                for i, source_id in enumerate(adr_ids):
                    for target_id in adr_ids[i+1:]:
                        edges.append({
                            "source": source_id,
                            "relation": "relatedTo",
                            "target": target_id,
                            "reason": f"Both related to {concept}"
                        })

        # Temporal relations (newer ADRs may supersede older ones)
        sorted_adrs = sorted(adrs, key=lambda x: x.get('date', ''), reverse=True)
        for i, newer_adr in enumerate(sorted_adrs):
            for older_adr in sorted_adrs[i+1:]:
                # If same category and high confidence, may supersede
                if (newer_adr.get('category') == older_adr.get('category') and
                    newer_adr.get('confidence', 0) > 0.8):
                    edges.append({
                        "source": newer_adr.get('id'),
                        "relation": "supersedes",
                        "target": older_adr.get('id'),
                        "reason": f"Newer decision in same category ({newer_adr.get('category')})"
                    })
                    break  # Only supersede the most recent older one

        return edges

    def _build_adjacency(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """Build adjacency list for fast graph traversal"""
        adjacency = {
            "version": "2.1.0",
            "adjacency": {},
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "last_updated": datetime.now(timezone.utc).isoformat() + "Z"
            }
        }

        # Initialize adjacency for each node
        for node in nodes:
            node_id = node['id']
            adjacency["adjacency"][node_id] = {
                "outgoing": {},
                "incoming": {}
            }

        # Populate adjacency from edges
        for edge in edges:
            source = edge['source']
            target = edge['target']
            relation = edge['relation']

            # Add outgoing edge
            if relation not in adjacency["adjacency"][source]["outgoing"]:
                adjacency["adjacency"][source]["outgoing"][relation] = []
            adjacency["adjacency"][source]["outgoing"][relation].append(target)

            # Add incoming edge (reverse relation)
            reverse_relation = self._get_reverse_relation(relation)
            if reverse_relation not in adjacency["adjacency"][target]["incoming"]:
                adjacency["adjacency"][target]["incoming"][reverse_relation] = []
            adjacency["adjacency"][target]["incoming"][reverse_relation].append(source)

        return adjacency

    def _get_reverse_relation(self, relation: str) -> str:
        """Get reverse relation type"""
        reverse_map = {
            "supersedes": "supersededBy",
            "implements": "implementedBy",
            "addresses": "addressedBy",
            "dependsOn": "dependedOnBy",
            "relatedTo": "relatedTo",  # bidirectional
            "usedIn": "uses"
        }
        return reverse_map.get(relation, relation)


if __name__ == "__main__":
    # Test graph generation
    import argparse

    parser = argparse.ArgumentParser(description="Generate knowledge graph from ADRs")
    parser.add_argument("corpus_dir", type=Path, help="Corpus directory")
    parser.add_argument("--config", type=Path, help="Config file")
    args = parser.parse_args()

    config = {}
    if args.config and args.config.exists():
        with open(args.config) as f:
            config = yaml.safe_load(f)

    generator = GraphGenerator(config)

    # Load ADRs from corpus/nodes/decisions
    decisions_dir = args.corpus_dir / "nodes" / "decisions"
    adrs = []
    if decisions_dir.exists():
        for adr_file in decisions_dir.glob("*.yml"):
            with open(adr_file) as f:
                adr = yaml.safe_load(f)
                adrs.append(adr)

    result = generator.generate(args.corpus_dir, adrs)
    print(json.dumps(result, indent=2))
