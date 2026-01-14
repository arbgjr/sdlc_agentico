#!/usr/bin/env python3
"""
Graph Manager - CRUD operations for semantic knowledge graph.

Manages the graph.json and adjacency.json files for the SDLC Agentico corpus.
Provides operations for adding/removing nodes and edges, traversing the graph,
and finding paths between nodes.

Usage:
    python graph_manager.py add --id ADR-001 --type Decision --title "Use PostgreSQL"
    python graph_manager.py neighbors ADR-001 --hops 2
    python graph_manager.py path ADR-001 ADR-010
    python graph_manager.py edge --source ADR-001 --relation dependsOn --target ADR-005
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque


class RelationType(Enum):
    """Supported semantic relation types."""
    SUPERSEDES = "supersedes"
    IMPLEMENTS = "implements"
    ADDRESSES = "addresses"
    CAUSED_BY = "causedBy"
    RELATED_TO = "relatedTo"
    DEPENDS_ON = "dependsOn"
    USED_IN = "usedIn"
    IS_A = "isA"
    PART_OF = "partOf"


class NodeType(Enum):
    """Supported node types."""
    DECISION = "Decision"
    LEARNING = "Learning"
    PATTERN = "Pattern"
    CONCEPT = "Concept"


# Inverse relation mapping
INVERSE_RELATIONS: Dict[str, str] = {
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


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""
    id: str
    type: str
    title: str
    status: str = "active"
    phases: List[int] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "phases": self.phases,
            "concepts": self.concepts,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphNode":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=data.get("type", "Decision"),
            title=data.get("title", data["id"]),
            status=data.get("status", "active"),
            phases=data.get("phases", []),
            concepts=data.get("concepts", []),
            tags=data.get("tags", []),
        )


@dataclass
class GraphEdge:
    """Represents an edge (relationship) in the knowledge graph."""
    source: str
    relation: str
    target: str
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
        }
        if self.reason:
            result["reason"] = self.reason
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphEdge":
        """Create from dictionary."""
        return cls(
            source=data["source"],
            relation=data["relation"],
            target=data["target"],
            reason=data.get("reason"),
        )


class GraphManager:
    """
    Manages the semantic knowledge graph.

    Handles CRUD operations on nodes and edges, maintains adjacency index,
    and provides graph traversal algorithms.
    """

    def __init__(self, corpus_path: Optional[Path] = None):
        """
        Initialize GraphManager.

        Args:
            corpus_path: Path to corpus directory. Defaults to .agentic_sdlc/corpus
        """
        if corpus_path is None:
            corpus_path = Path(".agentic_sdlc/corpus")

        self.corpus_path = Path(corpus_path)
        self.graph_file = self.corpus_path / "graph.json"
        self.adjacency_file = self.corpus_path / "adjacency.json"

        self._graph: Dict[str, Any] = {
            "version": "1.4.0",
            "updated_at": None,
            "nodes": [],
            "edges": [],
        }
        self._adjacency: Dict[str, Any] = {
            "version": "1.4.0",
            "adjacency": {},
            "metadata": {
                "node_count": 0,
                "edge_count": 0,
                "last_updated": None,
            },
        }

        self._load()

    def _load(self) -> None:
        """Load graph and adjacency from files."""
        if self.graph_file.exists():
            try:
                with open(self.graph_file, "r", encoding="utf-8") as f:
                    self._graph = json.load(f)
            except json.JSONDecodeError:
                pass

        if self.adjacency_file.exists():
            try:
                with open(self.adjacency_file, "r", encoding="utf-8") as f:
                    self._adjacency = json.load(f)
            except json.JSONDecodeError:
                pass

    def _save(self) -> None:
        """Save graph and adjacency to files."""
        now = datetime.now(timezone.utc).isoformat()

        # Update timestamps
        self._graph["updated_at"] = now
        self._adjacency["metadata"]["last_updated"] = now
        self._adjacency["metadata"]["node_count"] = len(self._graph["nodes"])
        self._adjacency["metadata"]["edge_count"] = len(self._graph["edges"])

        # Ensure directory exists
        self.corpus_path.mkdir(parents=True, exist_ok=True)

        # Write files with pretty formatting
        with open(self.graph_file, "w", encoding="utf-8") as f:
            json.dump(self._graph, f, indent=2, ensure_ascii=False)

        with open(self.adjacency_file, "w", encoding="utf-8") as f:
            json.dump(self._adjacency, f, indent=2, ensure_ascii=False)

    # ==================== Node Operations ====================

    def add_node(self, node: GraphNode) -> bool:
        """
        Add a node to the graph.

        Args:
            node: GraphNode to add

        Returns:
            True if added successfully, False if node already exists
        """
        # Check if node already exists
        if self.get_node(node.id):
            return self.update_node(node.id, node.to_dict())

        # Add to graph
        self._graph["nodes"].append(node.to_dict())

        # Initialize adjacency entry
        self._adjacency["adjacency"][node.id] = {
            "outgoing": {},
            "incoming": {},
        }

        self._save()
        return True

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.

        Args:
            node_id: Node identifier

        Returns:
            Node dictionary or None if not found
        """
        for node in self._graph["nodes"]:
            if node["id"] == node_id:
                return node
        return None

    def update_node(self, node_id: str, data: Dict[str, Any]) -> bool:
        """
        Update an existing node.

        Args:
            node_id: Node identifier
            data: Updated node data

        Returns:
            True if updated, False if node not found
        """
        for i, node in enumerate(self._graph["nodes"]):
            if node["id"] == node_id:
                # Preserve ID
                data["id"] = node_id
                self._graph["nodes"][i] = data
                self._save()
                return True
        return False

    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and all its edges.

        Args:
            node_id: Node identifier

        Returns:
            True if deleted, False if not found
        """
        # Find and remove node
        original_count = len(self._graph["nodes"])
        self._graph["nodes"] = [n for n in self._graph["nodes"] if n["id"] != node_id]

        if len(self._graph["nodes"]) == original_count:
            return False

        # Remove all edges involving this node
        self._graph["edges"] = [
            e for e in self._graph["edges"]
            if e["source"] != node_id and e["target"] != node_id
        ]

        # Update adjacency
        if node_id in self._adjacency["adjacency"]:
            del self._adjacency["adjacency"][node_id]

        # Remove from incoming/outgoing of other nodes
        for adj in self._adjacency["adjacency"].values():
            for rel_type, targets in list(adj.get("outgoing", {}).items()):
                adj["outgoing"][rel_type] = [t for t in targets if t != node_id]
            for rel_type, sources in list(adj.get("incoming", {}).items()):
                adj["incoming"][rel_type] = [s for s in sources if s != node_id]

        self._save()
        return True

    def list_nodes(self, node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all nodes, optionally filtered by type.

        Args:
            node_type: Optional filter by node type

        Returns:
            List of node dictionaries
        """
        if node_type:
            return [n for n in self._graph["nodes"] if n.get("type") == node_type]
        return self._graph["nodes"]

    # ==================== Edge Operations ====================

    def add_edge(self, edge: GraphEdge) -> bool:
        """
        Add an edge between nodes.

        Args:
            edge: GraphEdge to add

        Returns:
            True if added, False if edge already exists or nodes don't exist
        """
        # Verify source exists (target might be external reference)
        if not self.get_node(edge.source):
            return False

        # Check if edge already exists
        for existing in self._graph["edges"]:
            if (existing["source"] == edge.source and
                existing["relation"] == edge.relation and
                existing["target"] == edge.target):
                return False

        # Add to graph
        self._graph["edges"].append(edge.to_dict())

        # Update adjacency - outgoing
        source_adj = self._adjacency["adjacency"].setdefault(
            edge.source, {"outgoing": {}, "incoming": {}}
        )
        if edge.relation not in source_adj["outgoing"]:
            source_adj["outgoing"][edge.relation] = []
        if edge.target not in source_adj["outgoing"][edge.relation]:
            source_adj["outgoing"][edge.relation].append(edge.target)

        # Update adjacency - incoming (if target exists in graph)
        if edge.target in self._adjacency["adjacency"]:
            target_adj = self._adjacency["adjacency"][edge.target]
            inverse = INVERSE_RELATIONS.get(edge.relation, f"{edge.relation}Inverse")
            if inverse not in target_adj["incoming"]:
                target_adj["incoming"][inverse] = []
            if edge.source not in target_adj["incoming"][inverse]:
                target_adj["incoming"][inverse].append(edge.source)

        self._save()
        return True

    def remove_edge(self, source: str, relation: str, target: str) -> bool:
        """
        Remove an edge.

        Args:
            source: Source node ID
            relation: Relation type
            target: Target node ID

        Returns:
            True if removed, False if not found
        """
        original_count = len(self._graph["edges"])
        self._graph["edges"] = [
            e for e in self._graph["edges"]
            if not (e["source"] == source and e["relation"] == relation and e["target"] == target)
        ]

        if len(self._graph["edges"]) == original_count:
            return False

        # Update adjacency - outgoing
        if source in self._adjacency["adjacency"]:
            source_adj = self._adjacency["adjacency"][source]
            if relation in source_adj["outgoing"]:
                source_adj["outgoing"][relation] = [
                    t for t in source_adj["outgoing"][relation] if t != target
                ]

        # Update adjacency - incoming
        if target in self._adjacency["adjacency"]:
            target_adj = self._adjacency["adjacency"][target]
            inverse = INVERSE_RELATIONS.get(relation, f"{relation}Inverse")
            if inverse in target_adj["incoming"]:
                target_adj["incoming"][inverse] = [
                    s for s in target_adj["incoming"][inverse] if s != source
                ]

        self._save()
        return True

    def get_edges(self, node_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get all edges for a node.

        Args:
            node_id: Node identifier
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of edge dictionaries
        """
        edges = []

        if direction in ("outgoing", "both"):
            edges.extend([
                e for e in self._graph["edges"]
                if e["source"] == node_id
            ])

        if direction in ("incoming", "both"):
            edges.extend([
                e for e in self._graph["edges"]
                if e["target"] == node_id
            ])

        return edges

    # ==================== Graph Traversal ====================

    def get_neighbors(
        self,
        node_id: str,
        hops: int = 1,
        relation_filter: Optional[List[str]] = None,
        direction: str = "both"
    ) -> List[str]:
        """
        Get neighbors within N hops.

        Args:
            node_id: Starting node ID
            hops: Maximum number of hops (default 1)
            relation_filter: Optional list of relation types to follow
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of neighbor node IDs
        """
        visited: Set[str] = {node_id}
        current_level: Set[str] = {node_id}

        for _ in range(hops):
            next_level: Set[str] = set()

            for current in current_level:
                adj = self._adjacency["adjacency"].get(current, {})

                # Outgoing edges
                if direction in ("outgoing", "both"):
                    for rel_type, targets in adj.get("outgoing", {}).items():
                        if relation_filter and rel_type not in relation_filter:
                            continue
                        for target in targets:
                            if target not in visited:
                                next_level.add(target)

                # Incoming edges
                if direction in ("incoming", "both"):
                    for rel_type, sources in adj.get("incoming", {}).items():
                        if relation_filter:
                            # Check if original relation is in filter
                            original = next(
                                (k for k, v in INVERSE_RELATIONS.items() if v == rel_type),
                                None
                            )
                            if original and original not in relation_filter:
                                continue
                        for source in sources:
                            if source not in visited:
                                next_level.add(source)

            visited.update(next_level)
            current_level = next_level

            if not current_level:
                break

        return list(visited - {node_id})

    def find_path(
        self,
        source: str,
        target: str,
        max_hops: int = 10
    ) -> Optional[List[str]]:
        """
        Find shortest path between two nodes using BFS.

        Args:
            source: Starting node ID
            target: Target node ID
            max_hops: Maximum path length

        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        if source == target:
            return [source]

        visited: Set[str] = {source}
        queue: deque = deque([[source]])

        while queue:
            path = queue.popleft()

            if len(path) > max_hops:
                continue

            current = path[-1]
            neighbors = self.get_neighbors(current, hops=1)

            for neighbor in neighbors:
                if neighbor == target:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return None

    def get_transitive_closure(
        self,
        node_id: str,
        relation: str,
        max_depth: int = 10
    ) -> List[str]:
        """
        Get all nodes reachable via transitive relation.

        For example, get all nodes that a decision transitively depends on.

        Args:
            node_id: Starting node ID
            relation: Relation type to follow
            max_depth: Maximum depth to traverse

        Returns:
            List of reachable node IDs
        """
        result: List[str] = []
        visited: Set[str] = set()
        queue: deque = deque([(node_id, 0)])

        while queue:
            current, depth = queue.popleft()

            if current in visited or depth > max_depth:
                continue

            visited.add(current)

            adj = self._adjacency["adjacency"].get(current, {})
            targets = adj.get("outgoing", {}).get(relation, [])

            for target in targets:
                if target not in visited:
                    result.append(target)
                    queue.append((target, depth + 1))

        return result

    def get_centrality(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get nodes with highest degree centrality.

        Args:
            top_n: Number of top nodes to return

        Returns:
            List of (node_id, degree) tuples sorted by degree
        """
        degrees: Dict[str, int] = {}

        for node in self._graph["nodes"]:
            node_id = node["id"]
            adj = self._adjacency["adjacency"].get(node_id, {})

            outgoing_count = sum(len(v) for v in adj.get("outgoing", {}).values())
            incoming_count = sum(len(v) for v in adj.get("incoming", {}).values())

            degrees[node_id] = outgoing_count + incoming_count

        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_n]

    # ==================== Utility Methods ====================

    def validate(self) -> List[str]:
        """
        Validate graph integrity.

        Returns:
            List of validation errors (empty if valid)
        """
        errors: List[str] = []

        node_ids = {n["id"] for n in self._graph["nodes"]}

        # Check for orphan edges
        for edge in self._graph["edges"]:
            if edge["source"] not in node_ids:
                errors.append(f"Orphan edge: source '{edge['source']}' not found")
            # Target might be external reference (REQ-*, etc.)
            if edge["target"] not in node_ids and not edge["target"].startswith("REQ-"):
                errors.append(f"Orphan edge: target '{edge['target']}' not found")

        # Check adjacency consistency
        for node_id in node_ids:
            if node_id not in self._adjacency["adjacency"]:
                errors.append(f"Missing adjacency entry for node '{node_id}'")

        return errors

    def stats(self) -> Dict[str, Any]:
        """
        Get graph statistics.

        Returns:
            Dictionary with graph statistics
        """
        node_types: Dict[str, int] = {}
        relation_types: Dict[str, int] = {}

        for node in self._graph["nodes"]:
            t = node.get("type", "Unknown")
            node_types[t] = node_types.get(t, 0) + 1

        for edge in self._graph["edges"]:
            r = edge["relation"]
            relation_types[r] = relation_types.get(r, 0) + 1

        return {
            "total_nodes": len(self._graph["nodes"]),
            "total_edges": len(self._graph["edges"]),
            "node_types": node_types,
            "relation_types": relation_types,
            "top_central_nodes": self.get_centrality(5),
        }


def main():
    """CLI interface for graph manager."""
    parser = argparse.ArgumentParser(
        description="Graph Manager - CRUD operations for semantic knowledge graph"
    )
    parser.add_argument(
        "--corpus",
        default=".agentic_sdlc/corpus",
        help="Path to corpus directory"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add node command
    add_parser = subparsers.add_parser("add", help="Add a node to the graph")
    add_parser.add_argument("--id", required=True, help="Node ID")
    add_parser.add_argument(
        "--type",
        required=True,
        choices=["Decision", "Learning", "Pattern", "Concept"],
        help="Node type"
    )
    add_parser.add_argument("--title", required=True, help="Node title")
    add_parser.add_argument("--status", default="active", help="Node status")
    add_parser.add_argument("--phases", type=int, nargs="*", help="SDLC phases")
    add_parser.add_argument("--concepts", nargs="*", help="Related concepts")
    add_parser.add_argument("--tags", nargs="*", help="Tags")

    # Delete node command
    delete_parser = subparsers.add_parser("delete", help="Delete a node")
    delete_parser.add_argument("node_id", help="Node ID to delete")

    # Get neighbors command
    neighbors_parser = subparsers.add_parser("neighbors", help="Get node neighbors")
    neighbors_parser.add_argument("node_id", help="Starting node ID")
    neighbors_parser.add_argument("--hops", type=int, default=1, help="Number of hops")
    neighbors_parser.add_argument(
        "--direction",
        choices=["outgoing", "incoming", "both"],
        default="both",
        help="Edge direction"
    )
    neighbors_parser.add_argument("--relations", nargs="*", help="Relation filter")

    # Find path command
    path_parser = subparsers.add_parser("path", help="Find path between nodes")
    path_parser.add_argument("source", help="Source node ID")
    path_parser.add_argument("target", help="Target node ID")
    path_parser.add_argument("--max-hops", type=int, default=10, help="Maximum hops")

    # Add edge command
    edge_parser = subparsers.add_parser("edge", help="Add an edge")
    edge_parser.add_argument("--source", required=True, help="Source node ID")
    edge_parser.add_argument(
        "--relation",
        required=True,
        choices=[r.value for r in RelationType],
        help="Relation type"
    )
    edge_parser.add_argument("--target", required=True, help="Target node ID")
    edge_parser.add_argument("--reason", help="Reason for relation")

    # Remove edge command
    remove_edge_parser = subparsers.add_parser("remove-edge", help="Remove an edge")
    remove_edge_parser.add_argument("--source", required=True, help="Source node ID")
    remove_edge_parser.add_argument("--relation", required=True, help="Relation type")
    remove_edge_parser.add_argument("--target", required=True, help="Target node ID")

    # Transitive closure command
    closure_parser = subparsers.add_parser("closure", help="Get transitive closure")
    closure_parser.add_argument("node_id", help="Starting node ID")
    closure_parser.add_argument(
        "--relation",
        required=True,
        help="Relation type to follow"
    )
    closure_parser.add_argument("--max-depth", type=int, default=10, help="Maximum depth")

    # Stats command
    subparsers.add_parser("stats", help="Show graph statistics")

    # Validate command
    subparsers.add_parser("validate", help="Validate graph integrity")

    # List command
    list_parser = subparsers.add_parser("list", help="List nodes")
    list_parser.add_argument(
        "--type",
        choices=["Decision", "Learning", "Pattern", "Concept"],
        help="Filter by type"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = GraphManager(Path(args.corpus))

    if args.command == "add":
        node = GraphNode(
            id=args.id,
            type=args.type,
            title=args.title,
            status=args.status,
            phases=args.phases or [],
            concepts=args.concepts or [],
            tags=args.tags or [],
        )
        success = manager.add_node(node)
        print(f"Node added: {success}")

    elif args.command == "delete":
        success = manager.delete_node(args.node_id)
        print(f"Node deleted: {success}")

    elif args.command == "neighbors":
        neighbors = manager.get_neighbors(
            args.node_id,
            hops=args.hops,
            relation_filter=args.relations,
            direction=args.direction
        )
        print(f"Neighbors ({len(neighbors)}): {neighbors}")

    elif args.command == "path":
        path = manager.find_path(args.source, args.target, max_hops=args.max_hops)
        if path:
            print(f"Path found: {' -> '.join(path)}")
        else:
            print("No path found")

    elif args.command == "edge":
        edge = GraphEdge(
            source=args.source,
            relation=args.relation,
            target=args.target,
            reason=args.reason
        )
        success = manager.add_edge(edge)
        print(f"Edge added: {success}")

    elif args.command == "remove-edge":
        success = manager.remove_edge(args.source, args.relation, args.target)
        print(f"Edge removed: {success}")

    elif args.command == "closure":
        closure = manager.get_transitive_closure(
            args.node_id,
            args.relation,
            max_depth=args.max_depth
        )
        print(f"Transitive closure ({len(closure)}): {closure}")

    elif args.command == "stats":
        stats = manager.stats()
        print(json.dumps(stats, indent=2))

    elif args.command == "validate":
        errors = manager.validate()
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("Graph is valid")

    elif args.command == "list":
        nodes = manager.list_nodes(node_type=args.type)
        for node in nodes:
            print(f"  {node['id']}: {node['title']} ({node['type']})")


if __name__ == "__main__":
    main()
