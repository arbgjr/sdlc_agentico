#!/usr/bin/env python3
"""
find_related.py - Finds documents related to a research topic

Uses hybrid search combining:
- Keyword overlap (TF-IDF)
- Title similarity
- Summary similarity
- Category matching

Returns documents with similarity > threshold (default 0.6)
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter
import re

# Add lib path for logging
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib" / "python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="document-enricher", phase=1)


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis.

    Args:
        text: Input text
        top_n: Number of top keywords to return

    Returns:
        List of keywords sorted by frequency
    """
    # Simple tokenization (lowercase, alphanumeric only)
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())

    # Remove common stop words
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
        'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
        'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
        'its', 'let', 'put', 'say', 'she', 'too', 'use', 'with', 'this', 'that',
        'from', 'have', 'they', 'will', 'what', 'when', 'your', 'than', 'been',
        'call', 'find', 'long', 'make', 'many', 'more', 'must', 'over', 'such',
        'take', 'them', 'then', 'very', 'well', 'here', 'just', 'like', 'some',
        'time', 'into', 'only', 'also', 'back', 'come', 'good', 'know', 'look'
    }

    filtered_words = [w for w in words if w not in stop_words]

    # Count frequencies
    word_counts = Counter(filtered_words)

    # Return top N
    return [word for word, _ in word_counts.most_common(top_n)]


def calculate_keyword_overlap(keywords1: List[str], keywords2: List[str]) -> float:
    """
    Calculate Jaccard similarity between two keyword sets.

    Returns:
        Similarity score [0.0, 1.0]
    """
    if not keywords1 or not keywords2:
        return 0.0

    set1 = set(keywords1)
    set2 = set(keywords2)

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity using word overlap.

    Returns:
        Similarity score [0.0, 1.0]
    """
    words1 = set(re.findall(r'\b[a-z]{3,}\b', text1.lower()))
    words2 = set(re.findall(r'\b[a-z]{3,}\b', text2.lower()))

    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


def load_index(index_path: Path) -> Dict:
    """
    Load _index.yml file.

    Returns:
        Dictionary with document metadata
    """
    if not index_path.exists():
        logger.warning(f"Index file not found: {index_path}")
        return {"documents": []}

    with open(index_path, 'r') as f:
        return yaml.safe_load(f) or {"documents": []}


def find_related_documents(
    prompt: str,
    index_path: Path,
    min_similarity: float = 0.6,
    top_k: int = 5
) -> List[Tuple[str, float, Dict]]:
    """
    Find documents related to the research prompt.

    Args:
        prompt: Research prompt/topic
        index_path: Path to _index.yml
        min_similarity: Minimum similarity threshold
        top_k: Maximum number of results

    Returns:
        List of (doc_id, similarity, metadata) tuples
    """
    logger.info(f"Searching for documents related to: {prompt[:100]}...")

    # Extract keywords from prompt
    prompt_keywords = extract_keywords(prompt)
    logger.debug(f"Extracted keywords: {prompt_keywords}")

    # Load index
    index_data = load_index(index_path)
    documents = index_data.get("documents", [])

    if not documents:
        logger.info("No documents in index")
        return []

    # Calculate similarity for each document
    results = []

    for doc in documents:
        doc_id = doc.get("id")
        doc_title = doc.get("title", "")
        doc_keywords = doc.get("keywords", [])
        doc_summary = doc.get("summary", "")
        doc_category = doc.get("category", "")

        # Hybrid similarity calculation
        keyword_score = calculate_keyword_overlap(prompt_keywords, doc_keywords)
        title_score = calculate_text_similarity(prompt, doc_title)
        summary_score = calculate_text_similarity(prompt, doc_summary)

        # Category match (exact match = 1.0, else 0.0)
        prompt_lower = prompt.lower()
        category_score = 1.0 if doc_category.lower() in prompt_lower else 0.0

        # Weighted hybrid score
        similarity = (
            0.40 * keyword_score +
            0.30 * title_score +
            0.20 * summary_score +
            0.10 * category_score
        )

        logger.debug(
            f"Document {doc_id}: keyword={keyword_score:.2f}, "
            f"title={title_score:.2f}, summary={summary_score:.2f}, "
            f"category={category_score:.2f}, total={similarity:.2f}"
        )

        if similarity >= min_similarity:
            results.append((doc_id, similarity, doc))

    # Sort by similarity (descending) and limit to top_k
    results.sort(key=lambda x: x[1], reverse=True)
    results = results[:top_k]

    logger.info(f"Found {len(results)} related documents (threshold: {min_similarity})")

    for doc_id, sim, _ in results:
        logger.info(f"  {doc_id}: similarity={sim:.2f}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Find related documents")
    parser.add_argument("prompt", help="Research prompt/topic")
    parser.add_argument(
        "--index",
        default=".project/references/_index.yml",
        help="Path to _index.yml"
    )
    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.6,
        help="Minimum similarity threshold (0.0-1.0)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Maximum number of results"
    )
    parser.add_argument(
        "--output",
        choices=["json", "yaml", "text"],
        default="text",
        help="Output format"
    )

    args = parser.parse_args()

    # Find related documents
    index_path = Path(args.index)
    results = find_related_documents(
        args.prompt,
        index_path,
        args.min_similarity,
        args.top_k
    )

    # Output results
    if args.output == "json":
        output_data = [
            {
                "doc_id": doc_id,
                "similarity": similarity,
                "title": meta.get("title"),
                "path": meta.get("path"),
                "keywords": meta.get("keywords", [])
            }
            for doc_id, similarity, meta in results
        ]
        print(json.dumps(output_data, indent=2))

    elif args.output == "yaml":
        output_data = [
            {
                "doc_id": doc_id,
                "similarity": similarity,
                "title": meta.get("title"),
                "path": meta.get("path"),
                "keywords": meta.get("keywords", [])
            }
            for doc_id, similarity, meta in results
        ]
        print(yaml.dump(output_data, default_flow_style=False))

    else:  # text
        if not results:
            print("No related documents found.")
        else:
            print(f"Found {len(results)} related documents:\n")
            for doc_id, similarity, meta in results:
                print(f"  [{similarity:.2f}] {doc_id}: {meta.get('title')}")
                print(f"           Path: {meta.get('path')}")
                print(f"           Keywords: {', '.join(meta.get('keywords', []))}")
                print()

    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
