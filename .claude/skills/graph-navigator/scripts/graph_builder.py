#!/usr/bin/env python3
"""
Graph Builder - Build semantic graph from corpus YAML files.

Scans all YAML node files in the corpus and constructs the graph.json
and adjacency.json files. Supports incremental updates for single files.

Usage:
    # Full rebuild
    python graph_builder.py

    # With relation inference
    python graph_builder.py --infer

    # Incremental update for single file
    python graph_builder.py --incremental path/to/file.yml

    # Dry run (show stats without saving)
    python graph_builder.py --dry-run
"""

import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class ParsedNode:
    """Represents a parsed node from YAML file."""
    id: str
    type: str
    title: str
    status: str = "active"
    phases: List[int] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    relations: List[Dict[str, str]] = field(default_factory=list)
    source_path: str = ""


class GraphBuilder:
    """
    Builds the semantic graph from corpus YAML files.

    Scans all node files, extracts semantic information, and generates
    the graph.json and adjacency.json files.
    """

    # Directories to scan for nodes
    NODE_DIRECTORIES = ["decisions", "learnings", "patterns", "concepts"]

    # Inverse relation mapping
    INVERSE_RELATIONS = {
        "supersedes": "supersededBy",
        "implements": "implementedBy",
        "addresses": "addressedBy",
        "causedBy": "caused",
        "relatedTo": "relatedTo",
        "dependsOn": "dependedOnBy",
        "usedIn": "uses",
        "isA": "hasSubtype",
        "partOf": "hasPart",
    }

    def __init__(self, corpus_path: Optional[Path] = None):
        """
        Initialize GraphBuilder.

        Args:
            corpus_path: Path to corpus directory
        """
        if corpus_path is None:
            corpus_path = Path(".agentic_sdlc/corpus")

        self.corpus_path = Path(corpus_path)
        self.nodes_path = self.corpus_path / "nodes"
        self.graph_file = self.corpus_path / "graph.json"
        self.adjacency_file = self.corpus_path / "adjacency.json"

        # Fallback to old structure if nodes/ doesn't exist
        if not self.nodes_path.exists():
            self.nodes_path = self.corpus_path

        self._parsed_nodes: Dict[str, ParsedNode] = {}
        self._edges: List[Dict[str, str]] = []

    def _infer_type_from_path(self, file_path: Path) -> str:
        """Infer node type from file path."""
        path_str = str(file_path).lower()

        if "decisions" in path_str or "adr" in path_str:
            return "Decision"
        elif "learnings" in path_str or "learning" in path_str:
            return "Learning"
        elif "patterns" in path_str:
            return "Pattern"
        elif "concepts" in path_str:
            return "Concept"
        else:
            return "Decision"  # Default

    def _parse_yaml_file(self, file_path: Path) -> Optional[ParsedNode]:
        """
        Parse a YAML file into a ParsedNode.

        Args:
            file_path: Path to YAML file

        Returns:
            ParsedNode or None if parsing fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return None

        if not content:
            return None

        # Handle nested structure (decision: {...} or learning: {...})
        root_key = None
        for key in ["decision", "learning", "pattern", "concept"]:
            if key in content:
                root_key = key
                content = content[key]
                break

        # Must have an ID
        if "id" not in content:
            # Try to generate ID from filename
            content["id"] = file_path.stem.upper()

        # Determine node type
        node_type = self._infer_type_from_path(file_path)
        if "type" in content:
            type_map = {
                "decision": "Decision",
                "architectural": "Decision",
                "technical": "Decision",
                "process": "Decision",
                "tool": "Decision",
                "learning": "Learning",
                "incident": "Learning",
                "retrospective": "Learning",
                "discovery": "Learning",
                "pattern": "Pattern",
                "concept": "Concept",
            }
            node_type = type_map.get(content["type"].lower(), node_type)

        # Extract semantic information
        semantic = content.get("semantic", {})

        # Extract relations
        relations = []

        # From semantic.relations
        for rel in semantic.get("relations", []):
            if "type" in rel and "target" in rel:
                relations.append({
                    "type": rel["type"],
                    "target": rel["target"],
                    "reason": rel.get("reason"),
                })

        # From legacy fields
        if content.get("supersedes"):
            relations.append({
                "type": "supersedes",
                "target": content["supersedes"],
            })

        if content.get("related_decisions"):
            for related in content["related_decisions"]:
                if related:  # Skip empty entries
                    relations.append({
                        "type": "relatedTo",
                        "target": related,
                    })

        # Extract phases
        phases = semantic.get("phases", [])
        if "phase" in content:
            phases = [content["phase"]] if isinstance(content["phase"], int) else []

        return ParsedNode(
            id=content["id"],
            type=node_type,
            title=content.get("title", content["id"]),
            status=content.get("status", "active"),
            phases=phases,
            concepts=semantic.get("concepts", []),
            tags=semantic.get("tags", content.get("tags", [])),
            relations=relations,
            source_path=str(file_path),
        )

    def scan_directory(self, directory: Path) -> int:
        """
        Scan a directory for YAML files.

        Args:
            directory: Directory to scan

        Returns:
            Number of nodes parsed
        """
        count = 0

        for pattern in ["*.yml", "*.yaml"]:
            for file_path in directory.glob(pattern):
                node = self._parse_yaml_file(file_path)
                if node:
                    self._parsed_nodes[node.id] = node
                    count += 1

        return count

    def scan_corpus(self) -> int:
        """
        Scan entire corpus for nodes.

        Returns:
            Total number of nodes parsed
        """
        self._parsed_nodes.clear()
        total = 0

        # Scan nodes/ subdirectories
        for category in self.NODE_DIRECTORIES:
            category_path = self.nodes_path / category
            if category_path.exists():
                total += self.scan_directory(category_path)

        # Also scan legacy locations
        legacy_paths = [
            self.corpus_path.parent / "decisions",
            self.corpus_path.parent / "projects",
        ]

        for legacy_path in legacy_paths:
            if legacy_path.exists():
                # Scan recursively
                for yml_file in legacy_path.glob("**/*.yml"):
                    node = self._parse_yaml_file(yml_file)
                    if node and node.id not in self._parsed_nodes:
                        self._parsed_nodes[node.id] = node
                        total += 1

        return total

    def build_edges(self) -> int:
        """
        Build edges from parsed node relations.

        Returns:
            Number of edges created
        """
        self._edges.clear()

        for node in self._parsed_nodes.values():
            for rel in node.relations:
                self._edges.append({
                    "source": node.id,
                    "relation": rel["type"],
                    "target": rel["target"],
                })

        return len(self._edges)

    def infer_relations(self) -> int:
        """
        Infer additional relations based on shared concepts.

        Nodes sharing concepts are linked with 'relatedTo' relations.

        Returns:
            Number of inferred relations
        """
        inferred = 0

        # Build concept-to-nodes index
        concept_index: Dict[str, Set[str]] = {}
        for node_id, node in self._parsed_nodes.items():
            for concept in node.concepts:
                if concept not in concept_index:
                    concept_index[concept] = set()
                concept_index[concept].add(node_id)

        # Find existing relations to avoid duplicates
        existing_pairs: Set[Tuple[str, str]] = set()
        for edge in self._edges:
            existing_pairs.add((edge["source"], edge["target"]))
            existing_pairs.add((edge["target"], edge["source"]))

        # Create relatedTo for nodes sharing concepts
        for concept, node_ids in concept_index.items():
            if len(node_ids) < 2:
                continue

            nodes_list = list(node_ids)
            for i, node_a in enumerate(nodes_list):
                for node_b in nodes_list[i + 1:]:
                    # Skip if relation already exists
                    if (node_a, node_b) in existing_pairs:
                        continue

                    self._edges.append({
                        "source": node_a,
                        "relation": "relatedTo",
                        "target": node_b,
                    })
                    existing_pairs.add((node_a, node_b))
                    existing_pairs.add((node_b, node_a))
                    inferred += 1

        return inferred

    def build_adjacency(self) -> Dict[str, Any]:
        """
        Build adjacency index from edges.

        Returns:
            Adjacency dictionary
        """
        adjacency: Dict[str, Dict[str, Dict[str, List[str]]]] = {}

        # Initialize all nodes
        for node_id in self._parsed_nodes:
            adjacency[node_id] = {
                "outgoing": {},
                "incoming": {},
            }

        # Process edges
        for edge in self._edges:
            source = edge["source"]
            target = edge["target"]
            relation = edge["relation"]

            # Add outgoing
            if source in adjacency:
                if relation not in adjacency[source]["outgoing"]:
                    adjacency[source]["outgoing"][relation] = []
                if target not in adjacency[source]["outgoing"][relation]:
                    adjacency[source]["outgoing"][relation].append(target)

            # Add incoming (if target is in graph)
            if target in adjacency:
                inverse = self.INVERSE_RELATIONS.get(relation, f"{relation}Inverse")
                if inverse not in adjacency[target]["incoming"]:
                    adjacency[target]["incoming"][inverse] = []
                if source not in adjacency[target]["incoming"][inverse]:
                    adjacency[target]["incoming"][inverse].append(source)

        return adjacency

    def build_graph(self) -> Dict[str, Any]:
        """
        Build the full graph structure.

        Returns:
            Graph dictionary
        """
        nodes = []
        for node in self._parsed_nodes.values():
            nodes.append({
                "id": node.id,
                "type": node.type,
                "title": node.title,
                "status": node.status,
                "phases": node.phases,
                "concepts": node.concepts,
                "tags": node.tags,
            })

        return {
            "version": "1.4.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "nodes": nodes,
            "edges": self._edges,
        }

    def save(self) -> None:
        """Save graph and adjacency to files."""
        # Build structures
        graph = self.build_graph()
        adjacency = self.build_adjacency()

        # Prepare adjacency file
        adjacency_output = {
            "version": "1.4.0",
            "adjacency": adjacency,
            "metadata": {
                "node_count": len(self._parsed_nodes),
                "edge_count": len(self._edges),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            },
        }

        # Ensure directory exists
        self.corpus_path.mkdir(parents=True, exist_ok=True)

        # Write files
        with open(self.graph_file, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)

        with open(self.adjacency_file, "w", encoding="utf-8") as f:
            json.dump(adjacency_output, f, indent=2, ensure_ascii=False)

        print(f"Graph saved: {len(self._parsed_nodes)} nodes, {len(self._edges)} edges")

    def update_single_file(self, file_path: Path) -> bool:
        """
        Incrementally update graph for a single file.

        Args:
            file_path: Path to updated YAML file

        Returns:
            True if successful
        """
        # Load existing graph
        if self.graph_file.exists():
            try:
                with open(self.graph_file, "r", encoding="utf-8") as f:
                    existing_graph = json.load(f)
            except json.JSONDecodeError:
                existing_graph = {"nodes": [], "edges": []}
        else:
            existing_graph = {"nodes": [], "edges": []}

        # Parse updated file
        node = self._parse_yaml_file(file_path)
        if not node:
            return False

        # Remove old node and its edges
        existing_graph["nodes"] = [
            n for n in existing_graph["nodes"]
            if n["id"] != node.id
        ]
        existing_graph["edges"] = [
            e for e in existing_graph["edges"]
            if e["source"] != node.id
        ]

        # Add updated node
        existing_graph["nodes"].append({
            "id": node.id,
            "type": node.type,
            "title": node.title,
            "status": node.status,
            "phases": node.phases,
            "concepts": node.concepts,
            "tags": node.tags,
        })

        # Add updated edges
        for rel in node.relations:
            existing_graph["edges"].append({
                "source": node.id,
                "relation": rel["type"],
                "target": rel["target"],
            })

        # Update timestamp
        existing_graph["version"] = "1.4.0"
        existing_graph["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Save graph
        with open(self.graph_file, "w", encoding="utf-8") as f:
            json.dump(existing_graph, f, indent=2, ensure_ascii=False)

        # Rebuild adjacency (easier than incremental update)
        self._parsed_nodes = {
            n["id"]: ParsedNode(
                id=n["id"],
                type=n.get("type", "Decision"),
                title=n.get("title", n["id"]),
                status=n.get("status", "active"),
                phases=n.get("phases", []),
                concepts=n.get("concepts", []),
                tags=n.get("tags", []),
            )
            for n in existing_graph["nodes"]
        }
        self._edges = existing_graph["edges"]

        adjacency = self.build_adjacency()
        adjacency_output = {
            "version": "1.4.0",
            "adjacency": adjacency,
            "metadata": {
                "node_count": len(existing_graph["nodes"]),
                "edge_count": len(existing_graph["edges"]),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            },
        }

        with open(self.adjacency_file, "w", encoding="utf-8") as f:
            json.dump(adjacency_output, f, indent=2, ensure_ascii=False)

        print(f"Updated graph for node: {node.id}")
        return True

    def stats(self) -> Dict[str, Any]:
        """
        Get build statistics.

        Returns:
            Statistics dictionary
        """
        node_types: Dict[str, int] = {}
        relation_types: Dict[str, int] = {}

        for node in self._parsed_nodes.values():
            node_types[node.type] = node_types.get(node.type, 0) + 1

        for edge in self._edges:
            r = edge["relation"]
            relation_types[r] = relation_types.get(r, 0) + 1

        return {
            "total_nodes": len(self._parsed_nodes),
            "total_edges": len(self._edges),
            "node_types": node_types,
            "relation_types": relation_types,
        }


def main():
    """CLI interface for graph builder."""
    parser = argparse.ArgumentParser(
        description="Graph Builder - Build semantic graph from corpus YAML files"
    )
    parser.add_argument(
        "--corpus",
        default=".agentic_sdlc/corpus",
        help="Path to corpus directory"
    )
    parser.add_argument(
        "--infer",
        action="store_true",
        help="Infer additional relations from shared concepts"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show statistics without saving"
    )
    parser.add_argument(
        "--incremental",
        metavar="FILE",
        help="Update graph incrementally for single file"
    )

    args = parser.parse_args()

    builder = GraphBuilder(Path(args.corpus))

    if args.incremental:
        # Incremental update
        success = builder.update_single_file(Path(args.incremental))
        if not success:
            print("Failed to update graph")
            exit(1)
    else:
        # Full build
        print("Scanning corpus...")
        node_count = builder.scan_corpus()
        print(f"Found {node_count} nodes")

        print("Building edges...")
        edge_count = builder.build_edges()
        print(f"Found {edge_count} explicit edges")

        if args.infer:
            print("Inferring relations...")
            inferred = builder.infer_relations()
            print(f"Inferred {inferred} additional relations")

        if args.dry_run:
            print("\nStatistics (dry run):")
            stats = builder.stats()
            print(json.dumps(stats, indent=2))
        else:
            builder.save()


if __name__ == "__main__":
    main()
