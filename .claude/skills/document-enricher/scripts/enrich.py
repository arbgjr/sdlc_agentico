#!/usr/bin/env python3
"""
enrich.py - Enriches documents with research findings

Workflow:
1. Load original document metadata
2. Extract content (uses document-processor if available)
3. Structure enriched content:
   - Original content summary
   - Research findings
   - Synthesis (combined analysis)
4. Create corpus node ENRICH-{id}.yml
5. Generate enriched Markdown file
6. Update metadata

Returns enriched content, corpus node, and metadata.
"""

import os
import sys
import json
import yaml
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, List

# Add lib path for logging
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib" / "python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="document-enricher", phase=1)


def generate_enrichment_id(index_path: Path) -> str:
    """
    Generate next available ENRICH-{id}.

    Returns:
        Next enrichment ID (e.g., "ENRICH-001")
    """
    corpus_dir = index_path.parent.parent / "corpus" / "nodes" / "learnings"
    corpus_dir.mkdir(parents=True, exist_ok=True)

    # Find existing enrichment IDs
    existing_ids = []
    for file in corpus_dir.glob("ENRICH-*.yml"):
        id_str = file.stem.split("-")[1]
        try:
            existing_ids.append(int(id_str))
        except ValueError:
            continue

    # Generate next ID
    next_id = max(existing_ids, default=0) + 1
    return f"ENRICH-{next_id:03d}"


def get_next_version(doc_id: str, index_path: Path) -> int:
    """
    Get next enrichment version for a document.

    Args:
        doc_id: Document ID
        index_path: Path to _index.yml

    Returns:
        Next version number (1, 2, 3, ...)
    """
    if not index_path.exists():
        return 1

    with open(index_path, 'r') as f:
        index_data = yaml.safe_load(f) or {}

    documents = index_data.get("documents", [])

    for doc in documents:
        if doc.get("id") == doc_id:
            enrichments = doc.get("enrichments", [])
            if not enrichments:
                return 1
            max_version = max(e.get("version", 0) for e in enrichments)
            return max_version + 1

    return 1


def extract_document_content(doc_path: Path) -> str:
    """
    Extract content from document.

    Uses document-processor if available, otherwise returns placeholder.

    Args:
        doc_path: Path to document

    Returns:
        Extracted text content
    """
    # Check if document-processor is available
    doc_processor = Path(__file__).parent.parent.parent / "document-processor" / "scripts" / "extract.py"

    if doc_processor.exists() and doc_path.exists():
        logger.info(f"Extracting content from {doc_path}")
        import subprocess
        try:
            result = subprocess.run(
                ["python3", str(doc_processor), str(doc_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning(f"Document extraction failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"Error extracting document: {e}")

    # Fallback: return placeholder
    logger.info("Document extraction not available, using placeholder")
    return f"[Original document content from {doc_path.name}]"


def generate_synthesis(original_summary: str, research_findings: str) -> str:
    """
    Generate synthesis combining original content and research findings.

    For now, uses simple concatenation. In v2.0, could use LLM.

    Args:
        original_summary: Summary of original document
        research_findings: New research results

    Returns:
        Combined synthesis
    """
    # Simple rule-based synthesis
    synthesis_parts = []

    synthesis_parts.append("## Combined Analysis\n")

    synthesis_parts.append("### Original Document Insights\n")
    synthesis_parts.append(original_summary)
    synthesis_parts.append("\n")

    synthesis_parts.append("### New Research Findings\n")
    synthesis_parts.append(research_findings)
    synthesis_parts.append("\n")

    synthesis_parts.append("### Key Takeaways\n")
    synthesis_parts.append("- Original document provides foundational understanding")
    synthesis_parts.append("- New research extends knowledge with recent developments")
    synthesis_parts.append("- Combined, both sources offer comprehensive coverage of the topic")

    return "\n".join(synthesis_parts)


def create_enrichment_node(
    enrichment_id: str,
    doc_metadata: Dict,
    research_data: Dict,
    original_summary: str,
    synthesis: str,
    agent: str,
    phase: int,
    similarity: float
) -> Dict:
    """
    Create enrichment corpus node structure.

    Args:
        enrichment_id: Generated enrichment ID
        doc_metadata: Original document metadata
        research_data: Research results
        original_summary: Summary of original document
        synthesis: Combined analysis
        agent: Agent that performed research
        phase: SDLC phase
        similarity: Similarity score

    Returns:
        Corpus node dictionary
    """
    now = datetime.now(timezone.utc).isoformat()

    node = {
        "id": enrichment_id,
        "type": "enrichment",
        "title": f"{doc_metadata.get('title', 'Document')} - Enhanced with {research_data.get('topic', 'research')}",
        "created_at": now,
        "agent": agent,
        "source_document": {
            "id": doc_metadata.get("id"),
            "path": doc_metadata.get("path")
        },
        "research_context": {
            "prompt": research_data.get("prompt", ""),
            "phase": phase,
            "similarity": similarity
        },
        "content": {
            "original_summary": original_summary,
            "research_findings": research_data.get("findings", ""),
            "synthesis": synthesis,
            "sources": research_data.get("sources", [])
        },
        "relations": [
            {
                "type": "enriches",
                "target": doc_metadata.get("id")
            }
        ],
        "decay_metadata": {
            "last_validated_at": now,
            "decay_score": 1.0,
            "decay_status": "fresh"
        },
        "tags": list(set(doc_metadata.get("keywords", []) + research_data.get("keywords", [])))
    }

    return node


def enrich_document(
    doc_id: str,
    doc_metadata: Dict,
    research_data: Dict,
    agent: str = "domain-researcher",
    phase: int = 1,
    similarity: float = 0.8,
    index_path: Path = None
) -> Dict:
    """
    Enrich document with research findings.

    Args:
        doc_id: Document ID
        doc_metadata: Original document metadata
        research_data: Research results with keys:
            - prompt: Research prompt
            - topic: Research topic
            - findings: Research findings text
            - sources: List of sources (url, title, accessed_at)
            - keywords: List of keywords
        agent: Agent performing enrichment
        phase: SDLC phase
        similarity: Similarity score
        index_path: Path to _index.yml

    Returns:
        Dictionary with:
            - enriched_content: Markdown content
            - corpus_node: Corpus node data
            - metadata: Enrichment metadata
    """
    logger.info(f"Enriching document {doc_id} with research findings")

    # Generate enrichment ID
    if index_path is None:
        index_path = Path(".agentic_sdlc/references/_index.yml")

    enrichment_id = generate_enrichment_id(index_path)
    version = get_next_version(doc_id, index_path)

    logger.info(f"Generated enrichment ID: {enrichment_id}, version: {version}")

    # Extract original document content
    doc_path = Path(doc_metadata.get("path", ""))
    original_summary = extract_document_content(doc_path)

    # Generate synthesis
    synthesis = generate_synthesis(
        original_summary,
        research_data.get("findings", "")
    )

    # Create corpus node
    corpus_node = create_enrichment_node(
        enrichment_id,
        doc_metadata,
        research_data,
        original_summary,
        synthesis,
        agent,
        phase,
        similarity
    )

    # Generate enriched Markdown content
    enriched_content = generate_enriched_markdown(
        doc_metadata,
        research_data,
        original_summary,
        synthesis,
        enrichment_id,
        version,
        agent,
        phase
    )

    # Create metadata
    metadata = {
        "enrichment_id": enrichment_id,
        "enriched_at": datetime.now(timezone.utc).isoformat(),
        "research_topic": research_data.get("topic", ""),
        "agent": agent,
        "phase": phase,
        "corpus_node": f"corpus/nodes/learnings/{enrichment_id}.yml",
        "enriched_file": f"{doc_path.stem}.enriched.v{version}.md",
        "version": version,
        "similarity": similarity
    }

    logger.info(f"Enrichment complete: {enrichment_id}")

    return {
        "enriched_content": enriched_content,
        "corpus_node": corpus_node,
        "metadata": metadata
    }


def generate_enriched_markdown(
    doc_metadata: Dict,
    research_data: Dict,
    original_summary: str,
    synthesis: str,
    enrichment_id: str,
    version: int,
    agent: str,
    phase: int
) -> str:
    """
    Generate enriched Markdown file content.

    Args:
        doc_metadata: Original document metadata
        research_data: Research results
        original_summary: Summary of original content
        synthesis: Combined analysis
        enrichment_id: Enrichment ID
        version: Version number
        agent: Agent name
        phase: SDLC phase

    Returns:
        Markdown content as string
    """
    lines = []

    # Header
    lines.append(f"# {doc_metadata.get('title', 'Document')} - Enhanced Research Edition\n")
    lines.append(f"**Original Document**: `{doc_metadata.get('path', '')}`")
    lines.append(f"**Enriched**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"**Research Topic**: {research_data.get('topic', '')}")
    lines.append(f"**Agent**: {agent}")
    lines.append(f"**Phase**: {phase}")
    lines.append(f"**Version**: v{version}")
    lines.append(f"**Enrichment ID**: {enrichment_id}\n")
    lines.append("---\n")

    # Original Content Summary
    lines.append("## Original Content Summary\n")
    lines.append(original_summary)
    lines.append("\n---\n")

    # Research Findings
    lines.append("## Research Findings\n")
    lines.append(research_data.get("findings", ""))
    lines.append("\n")

    # Sources
    sources = research_data.get("sources", [])
    if sources:
        lines.append("### Sources\n")
        for source in sources:
            lines.append(f"- [{source.get('title', 'Source')}]({source.get('url', '')})")
            if source.get('accessed_at'):
                lines.append(f" - Accessed {source.get('accessed_at')}")
        lines.append("\n")

    lines.append("---\n")

    # Synthesis
    lines.append("## Synthesis\n")
    lines.append(synthesis)
    lines.append("\n")

    lines.append("---\n")
    lines.append("\n**🤖 Generated with SDLC Agêntico by @arbgjr**\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Enrich document with research findings")
    parser.add_argument("doc_id", help="Document ID to enrich")
    parser.add_argument("research_json", help="Path to research results JSON file")
    parser.add_argument(
        "--index",
        default=".agentic_sdlc/references/_index.yml",
        help="Path to _index.yml"
    )
    parser.add_argument("--agent", default="domain-researcher", help="Agent name")
    parser.add_argument("--phase", type=int, default=1, help="SDLC phase")
    parser.add_argument("--similarity", type=float, default=0.8, help="Similarity score")
    parser.add_argument(
        "--output-dir",
        help="Output directory for enriched files (default: same as original)"
    )

    args = parser.parse_args()

    # Load index
    index_path = Path(args.index)
    if not index_path.exists():
        logger.error(f"Index file not found: {index_path}")
        return 1

    with open(index_path, 'r') as f:
        index_data = yaml.safe_load(f) or {}

    # Find document
    doc_metadata = None
    for doc in index_data.get("documents", []):
        if doc.get("id") == args.doc_id:
            doc_metadata = doc
            break

    if not doc_metadata:
        logger.error(f"Document not found: {args.doc_id}")
        return 1

    # Load research data
    research_path = Path(args.research_json)
    if not research_path.exists():
        logger.error(f"Research file not found: {research_path}")
        return 1

    with open(research_path, 'r') as f:
        research_data = json.load(f)

    # Enrich document
    result = enrich_document(
        args.doc_id,
        doc_metadata,
        research_data,
        args.agent,
        args.phase,
        args.similarity,
        index_path
    )

    # Save outputs
    output_dir = Path(args.output_dir) if args.output_dir else index_path.parent

    # Save corpus node
    corpus_dir = output_dir.parent / "corpus" / "nodes" / "learnings"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    corpus_file = corpus_dir / f"{result['metadata']['enrichment_id']}.yml"

    with open(corpus_file, 'w') as f:
        yaml.dump(result['corpus_node'], f, default_flow_style=False, sort_keys=False)

    logger.info(f"Saved corpus node: {corpus_file}")

    # Save enriched Markdown
    enriched_file = output_dir / result['metadata']['enriched_file']
    with open(enriched_file, 'w') as f:
        f.write(result['enriched_content'])

    logger.info(f"Saved enriched Markdown: {enriched_file}")

    # Output metadata for next step (update_index.py)
    print(json.dumps(result['metadata'], indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
