#!/usr/bin/env python3
"""
Graph Visualizer - Generate visualizations from semantic graph.

Exports the knowledge graph to Mermaid diagrams and DOT format for visualization.
Supports filtering by node type, phase, and generating subgraphs.

Usage:
    # Generate full Mermaid diagram
    python graph_visualizer.py --format mermaid

    # Generate DOT format
    python graph_visualizer.py --format dot

    # Filter by node type
    python graph_visualizer.py --format mermaid --type Decision

    # Filter by phase
    python graph_visualizer.py --format mermaid --phase 3

    # Generate subgraph around a node
    python graph_visualizer.py --format mermaid --center ADR-001 --hops 2

    # Show centrality metrics
    python graph_visualizer.py --metrics
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict


class GraphVisualizer:
    """
    Generates visualizations from the semantic graph.

    Supports Mermaid flowcharts and DOT format output.
    """

    # Node type colors for Mermaid
    TYPE_COLORS = {
        "Decision": "#4CAF50",     # Green
        "Learning": "#2196F3",     # Blue
        "Pattern": "#FF9800",      # Orange
        "Concept": "#9C27B0",      # Purple
    }

    # Node type shapes for Mermaid
    TYPE_SHAPES = {
        "Decision": "([{label}])",      # Stadium shape
        "Learning": "[/{label}/]",       # Parallelogram
        "Pattern": "{{{label}}}",        # Hexagon
        "Concept": "(({label}))",        # Circle
    }

    # Relation labels for display
    RELATION_LABELS = {
        "supersedes": "supersedes",
        "implements": "implements",
        "addresses": "addresses",
        "causedBy": "caused by",
        "relatedTo": "related to",
        "dependsOn": "depends on",
        "usedIn": "used in",
        "isA": "is a",
        "partOf": "part of",
    }

    def __init__(self, corpus_path: Optional[Path] = None):
        """Initialize visualizer."""
        if corpus_path is None:
            corpus_path = Path(".agentic_sdlc/corpus")

        self.corpus_path = Path(corpus_path)
        self.graph_file = corpus_path / "graph.json"
        self.adjacency_file = corpus_path / "adjacency.json"

        self._graph: Dict[str, Any] = {"nodes": [], "edges": []}
        self._adjacency: Dict[str, Any] = {"adjacency": {}}

        self._load()

    def _load(self) -> None:
        """Load graph files."""
        if self.graph_file.exists():
            try:
                with open(self.graph_file, "r", encoding="utf-8") as f:
                    self._graph = json.load(f)
            except Exception:
                pass

        if self.adjacency_file.exists():
            try:
                with open(self.adjacency_file, "r", encoding="utf-8") as f:
                    self._adjacency = json.load(f)
            except Exception:
                pass

    def _sanitize_id(self, node_id: str) -> str:
        """Sanitize node ID for diagram."""
        return node_id.replace("-", "_").replace(".", "_")

    def _sanitize_label(self, label: str) -> str:
        """Sanitize label for diagram (escape special chars)."""
        # Escape quotes and special chars
        label = label.replace('"', "'")
        label = label.replace("<", "&lt;")
        label = label.replace(">", "&gt;")
        # Truncate long labels
        if len(label) > 40:
            label = label[:37] + "..."
        return label

    def _get_subgraph_nodes(
        self,
        center_id: str,
        hops: int = 2
    ) -> Set[str]:
        """Get nodes within N hops of center."""
        nodes: Set[str] = {center_id}
        current_level: Set[str] = {center_id}

        for _ in range(hops):
            next_level: Set[str] = set()

            for node_id in current_level:
                adj = self._adjacency.get("adjacency", {}).get(node_id, {})

                # Outgoing
                for targets in adj.get("outgoing", {}).values():
                    next_level.update(targets)

                # Incoming
                for sources in adj.get("incoming", {}).values():
                    next_level.update(sources)

            nodes.update(next_level)
            current_level = next_level - nodes

            if not current_level:
                break

        return nodes

    def to_mermaid(
        self,
        type_filter: Optional[str] = None,
        phase_filter: Optional[int] = None,
        center_node: Optional[str] = None,
        hops: int = 2,
        include_orphans: bool = False,
    ) -> str:
        """
        Generate Mermaid flowchart.

        Args:
            type_filter: Filter by node type
            phase_filter: Filter by SDLC phase
            center_node: Generate subgraph around this node
            hops: Hops for subgraph
            include_orphans: Include nodes without edges

        Returns:
            Mermaid diagram string
        """
        lines: List[str] = []
        lines.append("```mermaid")
        lines.append("flowchart TD")
        lines.append("")

        # Determine which nodes to include
        if center_node:
            include_nodes = self._get_subgraph_nodes(center_node, hops)
        else:
            include_nodes = None

        # Group nodes by type
        nodes_by_type: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        node_ids: Set[str] = set()

        for node in self._graph.get("nodes", []):
            node_id = node["id"]
            node_type = node.get("type", "Decision")
            phases = node.get("phases", [])

            # Apply filters
            if type_filter and node_type != type_filter:
                continue

            if phase_filter is not None:
                if isinstance(phases, int):
                    phases = [phases]
                if phase_filter not in phases:
                    continue

            if include_nodes and node_id not in include_nodes:
                continue

            nodes_by_type[node_type].append(node)
            node_ids.add(node_id)

        # Add subgraphs by type
        for node_type, nodes in nodes_by_type.items():
            if not nodes:
                continue

            lines.append(f"    subgraph {node_type}s")
            lines.append(f"        style {node_type}s fill:{self.TYPE_COLORS.get(node_type, '#ccc')},stroke:#333")

            for node in nodes:
                safe_id = self._sanitize_id(node["id"])
                label = self._sanitize_label(node.get("title", node["id"]))
                shape = self.TYPE_SHAPES.get(node_type, "([{label}])")
                shape_str = shape.format(label=label)

                lines.append(f"        {safe_id}{shape_str}")

            lines.append("    end")
            lines.append("")

        # Add edges
        lines.append("    %% Relationships")
        added_edges: Set[str] = set()

        for edge in self._graph.get("edges", []):
            source = edge["source"]
            target = edge["target"]
            relation = edge["relation"]

            # Skip if nodes not in diagram
            if source not in node_ids:
                continue
            # Target might be external, include edge if source is in diagram
            target_in_graph = target in node_ids

            safe_source = self._sanitize_id(source)
            safe_target = self._sanitize_id(target)

            # Avoid duplicate edges
            edge_key = f"{safe_source}-{relation}-{safe_target}"
            if edge_key in added_edges:
                continue
            added_edges.add(edge_key)

            rel_label = self.RELATION_LABELS.get(relation, relation)

            if target_in_graph:
                lines.append(f"    {safe_source} -->|{rel_label}| {safe_target}")
            else:
                # External target - show as text
                lines.append(f"    {safe_source} -.->|{rel_label}| ext_{safe_target}[{target}]")

        lines.append("```")

        return "\n".join(lines)

    def to_dot(
        self,
        type_filter: Optional[str] = None,
        phase_filter: Optional[int] = None,
    ) -> str:
        """
        Generate DOT format for Graphviz.

        Args:
            type_filter: Filter by node type
            phase_filter: Filter by SDLC phase

        Returns:
            DOT format string
        """
        lines: List[str] = []
        lines.append("digraph KnowledgeGraph {")
        lines.append("    rankdir=TB;")
        lines.append('    node [fontname="Arial", fontsize=10];')
        lines.append('    edge [fontname="Arial", fontsize=8];')
        lines.append("")

        # Node shapes for DOT
        dot_shapes = {
            "Decision": "box",
            "Learning": "parallelogram",
            "Pattern": "hexagon",
            "Concept": "ellipse",
        }

        node_ids: Set[str] = set()

        # Add nodes
        for node in self._graph.get("nodes", []):
            node_id = node["id"]
            node_type = node.get("type", "Decision")
            phases = node.get("phases", [])

            # Apply filters
            if type_filter and node_type != type_filter:
                continue

            if phase_filter is not None:
                if isinstance(phases, int):
                    phases = [phases]
                if phase_filter not in phases:
                    continue

            safe_id = self._sanitize_id(node_id)
            label = self._sanitize_label(node.get("title", node_id))
            shape = dot_shapes.get(node_type, "box")
            color = self.TYPE_COLORS.get(node_type, "#ccc")

            lines.append(
                f'    {safe_id} [label="{label}", shape={shape}, '
                f'style=filled, fillcolor="{color}"];'
            )
            node_ids.add(node_id)

        lines.append("")

        # Add edges
        for edge in self._graph.get("edges", []):
            source = edge["source"]
            target = edge["target"]
            relation = edge["relation"]

            if source not in node_ids:
                continue

            safe_source = self._sanitize_id(source)
            safe_target = self._sanitize_id(target)
            rel_label = self.RELATION_LABELS.get(relation, relation)

            if target in node_ids:
                lines.append(f'    {safe_source} -> {safe_target} [label="{rel_label}"];')

        lines.append("}")

        return "\n".join(lines)

    def get_metrics(self) -> Dict[str, Any]:
        """
        Calculate graph metrics.

        Returns:
            Dictionary with metrics
        """
        nodes = self._graph.get("nodes", [])
        edges = self._graph.get("edges", [])
        adjacency = self._adjacency.get("adjacency", {})

        # Basic counts
        node_count = len(nodes)
        edge_count = len(edges)

        # Type distribution
        type_counts: Dict[str, int] = defaultdict(int)
        for node in nodes:
            type_counts[node.get("type", "Unknown")] += 1

        # Relation distribution
        relation_counts: Dict[str, int] = defaultdict(int)
        for edge in edges:
            relation_counts[edge["relation"]] += 1

        # Degree centrality
        degrees: List[Tuple[str, int]] = []
        for node_id, adj in adjacency.items():
            out_degree = sum(len(v) for v in adj.get("outgoing", {}).values())
            in_degree = sum(len(v) for v in adj.get("incoming", {}).values())
            degrees.append((node_id, out_degree + in_degree))

        degrees.sort(key=lambda x: x[1], reverse=True)
        top_central = degrees[:10]

        # Orphan nodes (no edges)
        orphan_count = sum(1 for _, degree in degrees if degree == 0)

        # Connected components (simplified)
        # Just check if graph is connected from first node
        if nodes:
            visited: Set[str] = set()
            queue = [nodes[0]["id"]]
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                adj = adjacency.get(current, {})
                for targets in adj.get("outgoing", {}).values():
                    queue.extend(t for t in targets if t not in visited)
                for sources in adj.get("incoming", {}).values():
                    queue.extend(s for s in sources if s not in visited)

            connectivity = len(visited) / node_count if node_count > 0 else 0
        else:
            connectivity = 0

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "type_distribution": dict(type_counts),
            "relation_distribution": dict(relation_counts),
            "top_central_nodes": top_central,
            "orphan_nodes": orphan_count,
            "connectivity": round(connectivity, 2),
            "avg_degree": round(edge_count * 2 / node_count, 2) if node_count > 0 else 0,
        }


def main():
    """CLI interface for graph visualizer."""
    parser = argparse.ArgumentParser(
        description="Graph Visualizer - Generate visualizations from semantic graph"
    )
    parser.add_argument(
        "--corpus",
        default=".agentic_sdlc/corpus",
        help="Path to corpus directory"
    )
    parser.add_argument(
        "--format",
        choices=["mermaid", "dot"],
        default="mermaid",
        help="Output format"
    )
    parser.add_argument(
        "--type",
        choices=["Decision", "Learning", "Pattern", "Concept"],
        help="Filter by node type"
    )
    parser.add_argument(
        "--phase",
        type=int,
        help="Filter by SDLC phase (0-8)"
    )
    parser.add_argument(
        "--center",
        metavar="NODE_ID",
        help="Generate subgraph centered on this node"
    )
    parser.add_argument(
        "--hops",
        type=int,
        default=2,
        help="Hops for subgraph (with --center)"
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Show graph metrics instead of diagram"
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Write output to file"
    )

    args = parser.parse_args()

    visualizer = GraphVisualizer(Path(args.corpus))

    if args.metrics:
        metrics = visualizer.get_metrics()
        output = json.dumps(metrics, indent=2)
    elif args.format == "mermaid":
        output = visualizer.to_mermaid(
            type_filter=args.type,
            phase_filter=args.phase,
            center_node=args.center,
            hops=args.hops,
        )
    else:  # dot
        output = visualizer.to_dot(
            type_filter=args.type,
            phase_filter=args.phase,
        )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Output written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
