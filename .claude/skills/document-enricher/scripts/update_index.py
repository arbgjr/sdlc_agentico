#!/usr/bin/env python3
"""
update_index.py - Updates _index.yml and graph.json with enrichment metadata

Workflow:
1. Load enrichment metadata (from enrich.py output)
2. Update _index.yml with enrichment entry
3. Update graph.json with 'enriches' relation
4. Validate graph integrity
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, Optional

# Add lib path for logging
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib" / "python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="document-enricher", phase=1)


def load_yaml(path: Path) -> Dict:
    """Load YAML file."""
    if not path.exists():
        return {}

    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}


def save_yaml(data: Dict, path: Path):
    """Save YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_json(path: Path) -> Dict:
    """Load JSON file."""
    if not path.exists():
        return {}

    with open(path, 'r') as f:
        return json.load(f)


def save_json(data: Dict, path: Path):
    """Save JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def update_index(enrichment_metadata: Dict, index_path: Path):
    """
    Update _index.yml with enrichment metadata.

    Args:
        enrichment_metadata: Enrichment metadata from enrich.py
        index_path: Path to _index.yml
    """
    logger.info(f"Updating index: {index_path}")

    # Load index
    index_data = load_yaml(index_path)

    if "documents" not in index_data:
        index_data["documents"] = []

    # Find document by ID (from corpus_node path)
    corpus_node_path = enrichment_metadata.get("corpus_node", "")
    enrichment_id = enrichment_metadata.get("enrichment_id", "")

    # Extract doc_id from source (need to read corpus node)
    corpus_file = Path(".agentic_sdlc") / corpus_node_path
    if not corpus_file.exists():
        logger.error(f"Corpus node not found: {corpus_file}")
        return False

    corpus_node = load_yaml(corpus_file)
    doc_id = corpus_node.get("source_document", {}).get("id")

    if not doc_id:
        logger.error("Could not determine document ID from corpus node")
        return False

    # Find document in index
    doc_found = False
    for doc in index_data["documents"]:
        if doc.get("id") == doc_id:
            doc_found = True

            # Add enrichments list if not exists
            if "enrichments" not in doc:
                doc["enrichments"] = []

            # Add new enrichment
            doc["enrichments"].append(enrichment_metadata)

            logger.info(f"Added enrichment to document {doc_id}: {enrichment_id}")
            break

    if not doc_found:
        logger.warning(f"Document {doc_id} not found in index")
        return False

    # Save updated index
    save_yaml(index_data, index_path)
    logger.info(f"Index updated successfully")

    return True


def update_graph(enrichment_metadata: Dict, graph_path: Path):
    """
    Update graph.json with 'enriches' relation.

    Args:
        enrichment_metadata: Enrichment metadata from enrich.py
        graph_path: Path to graph.json
    """
    logger.info(f"Updating graph: {graph_path}")

    # Load graph
    graph_data = load_json(graph_path)

    if "nodes" not in graph_data:
        graph_data["nodes"] = []
    if "edges" not in graph_data:
        graph_data["edges"] = []

    enrichment_id = enrichment_metadata.get("enrichment_id", "")

    # Load corpus node to get source document ID
    corpus_node_path = enrichment_metadata.get("corpus_node", "")
    corpus_file = Path(".agentic_sdlc") / corpus_node_path

    if not corpus_file.exists():
        logger.error(f"Corpus node not found: {corpus_file}")
        return False

    corpus_node = load_yaml(corpus_file)
    doc_id = corpus_node.get("source_document", {}).get("id")

    if not doc_id:
        logger.error("Could not determine document ID from corpus node")
        return False

    # Add enrichment node if not exists
    node_exists = any(n.get("id") == enrichment_id for n in graph_data["nodes"])

    if not node_exists:
        graph_data["nodes"].append({
            "id": enrichment_id,
            "type": "enrichment",
            "title": corpus_node.get("title", ""),
            "created_at": corpus_node.get("created_at", "")
        })
        logger.info(f"Added node: {enrichment_id}")

    # Add 'enriches' edge
    edge_exists = any(
        e.get("source") == enrichment_id and
        e.get("target") == doc_id and
        e.get("type") == "enriches"
        for e in graph_data["edges"]
    )

    if not edge_exists:
        graph_data["edges"].append({
            "source": enrichment_id,
            "target": doc_id,
            "type": "enriches",
            "created_at": enrichment_metadata.get("enriched_at", "")
        })
        logger.info(f"Added edge: {enrichment_id} --enriches--> {doc_id}")

    # Save updated graph
    save_json(graph_data, graph_path)
    logger.info(f"Graph updated successfully")

    return True


def validate_graph_integrity(graph_path: Path) -> bool:
    """
    Validate graph integrity after update.

    Checks:
    - All edges reference existing nodes
    - No orphan edges

    Args:
        graph_path: Path to graph.json

    Returns:
        True if valid, False otherwise
    """
    logger.info("Validating graph integrity...")

    graph_data = load_json(graph_path)

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    node_ids = {n.get("id") for n in nodes}

    # Check for orphan edges
    orphan_edges = []
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")

        if source not in node_ids:
            orphan_edges.append(f"{source} (source missing)")
        if target not in node_ids:
            orphan_edges.append(f"{target} (target missing)")

    if orphan_edges:
        logger.error(f"Found orphan edges: {orphan_edges}")
        return False

    logger.info("Graph integrity validated successfully")
    return True


def main():
    parser = argparse.ArgumentParser(description="Update index and graph with enrichment metadata")
    parser.add_argument(
        "metadata_json",
        help="Path to enrichment metadata JSON (from enrich.py)"
    )
    parser.add_argument(
        "--index",
        default=".agentic_sdlc/references/_index.yml",
        help="Path to _index.yml"
    )
    parser.add_argument(
        "--graph",
        default=".agentic_sdlc/corpus/graph.json",
        help="Path to graph.json"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate graph integrity after update"
    )

    args = parser.parse_args()

    # Load enrichment metadata
    metadata_path = Path(args.metadata_json)
    if not metadata_path.exists():
        logger.error(f"Metadata file not found: {metadata_path}")
        return 1

    with open(metadata_path, 'r') as f:
        enrichment_metadata = json.load(f)

    # Update index
    index_path = Path(args.index)
    if not update_index(enrichment_metadata, index_path):
        logger.error("Failed to update index")
        return 1

    # Update graph
    graph_path = Path(args.graph)
    if not update_graph(enrichment_metadata, graph_path):
        logger.error("Failed to update graph")
        return 1

    # Validate graph integrity
    if args.validate:
        if not validate_graph_integrity(graph_path):
            logger.error("Graph integrity validation failed")
            return 1

    logger.info("✅ Index and graph updated successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
