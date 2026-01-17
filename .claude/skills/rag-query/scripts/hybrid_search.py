#!/usr/bin/env python3
"""
Hybrid Search - Combined text and graph search for RAG corpus.

Combines keyword-based search with graph traversal for comprehensive results.
Supports filtering by phase, concept, and node type.

Usage:
    # Hybrid search (default)
    python hybrid_search.py "database migration"

    # Text-only search
    python hybrid_search.py "database migration" --mode text

    # Graph-expanded search with more hops
    python hybrid_search.py "database migration" --mode hybrid --hops 3

    # Filter by phase
    python hybrid_search.py "authentication" --phase 3

    # Filter by concept
    python hybrid_search.py "security" --concept oauth
"""

import re
import yaml
import json
import math
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class SearchMode(Enum):
    """Search mode options."""
    TEXT = "text"
    GRAPH = "graph"
    HYBRID = "hybrid"


@dataclass
class SearchResult:
    """Represents a search result."""
    node_id: str
    title: str
    score: float
    match_type: str  # "text", "graph", "both"
    snippet: str
    node_type: str = "Decision"
    path_from_query: Optional[List[str]] = None
    decay_score: Optional[float] = None
    decay_status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "id": self.node_id,
            "title": self.title,
            "type": self.node_type,
            "score": round(self.score, 3),
            "matchType": self.match_type,
            "snippet": self.snippet,
        }
        if self.path_from_query:
            result["pathFromQuery"] = self.path_from_query
        if self.decay_score is not None:
            result["decayScore"] = round(self.decay_score, 3)
            result["decayStatus"] = self.decay_status
        return result


class TextIndex:
    """
    Simple TF-IDF based text index.

    Stores inverted index for fast keyword search.
    """

    # Stop words to filter
    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "must", "shall",
        "can", "need", "dare", "ought", "used", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "into",
        "through", "during", "before", "after", "above", "below",
        "between", "under", "again", "further", "then", "once",
        "and", "or", "but", "if", "so", "than", "too", "very",
        "just", "only", "own", "same", "that", "this", "these",
        "those", "what", "which", "who", "whom", "when", "where",
        "why", "how", "all", "each", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "any", "both",
    }

    def __init__(self, corpus_path: Path):
        """Initialize text index."""
        self.corpus_path = corpus_path
        self.index_file = corpus_path / "index.yml"
        self.cache_file = corpus_path / ".cache" / "search_cache.json"

        self._documents: Dict[str, Dict[str, Any]] = {}
        self._inverted_index: Dict[str, Dict[str, int]] = {}
        self._cache: Dict[str, Any] = {}

        self._load()

    def _load(self) -> None:
        """Load index from file or build it."""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    self._documents = data.get("documents", {})
                    self._inverted_index = data.get("inverted_index", {})
            except Exception:
                self._build()
        else:
            self._build()

        # Load cache
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}

    def _build(self) -> None:
        """Build index from corpus files."""
        self._documents = {}
        self._inverted_index = {}

        nodes_path = self.corpus_path / "nodes"
        if not nodes_path.exists():
            nodes_path = self.corpus_path

        for category in ["decisions", "learnings", "patterns", "concepts"]:
            category_path = nodes_path / category
            if not category_path.exists():
                continue

            for file_path in category_path.glob("*.yml"):
                self._index_file(file_path)

        # Also index from legacy paths
        for legacy_path in [
            self.corpus_path.parent / "decisions",
            self.corpus_path.parent / "projects",
        ]:
            if legacy_path.exists():
                for yml_file in legacy_path.glob("**/*.yml"):
                    self._index_file(yml_file)

        self._save()

    def _index_file(self, file_path: Path) -> None:
        """Index a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
        except Exception:
            return

        if not content:
            return

        # Handle nested structure
        for key in ["decision", "learning", "pattern", "concept"]:
            if key in content:
                content = content[key]
                break

        if "id" not in content:
            return

        doc_id = content["id"]

        # Determine type from path
        path_str = str(file_path).lower()
        doc_type = "Decision"
        if "learning" in path_str:
            doc_type = "Learning"
        elif "pattern" in path_str:
            doc_type = "Pattern"
        elif "concept" in path_str:
            doc_type = "Concept"

        # Extract searchable text
        text = self._extract_text(content)

        # Store document metadata
        self._documents[doc_id] = {
            "title": content.get("title", doc_id),
            "type": doc_type,
            "path": str(file_path),
            "text_length": len(text),
            "phases": content.get("semantic", {}).get("phases", []),
            "concepts": content.get("semantic", {}).get("concepts", []),
        }

        # Build inverted index
        tokens = self._tokenize(text)
        for token in set(tokens):
            if token not in self._inverted_index:
                self._inverted_index[token] = {}
            self._inverted_index[token][doc_id] = tokens.count(token)

    def _extract_text(self, content: Dict[str, Any]) -> str:
        """Extract searchable text from document."""
        parts: List[str] = []

        for field in ["title", "context", "decision", "description",
                     "problem", "solution", "insight", "label"]:
            if field in content and content[field]:
                parts.append(str(content[field]))

        # Handle consequences
        consequences = content.get("consequences", [])
        if isinstance(consequences, list):
            parts.extend(str(c) for c in consequences)
        elif isinstance(consequences, dict):
            for key in ["positive", "negative", "risks"]:
                if key in consequences:
                    parts.extend(str(c) for c in consequences[key])

        # Semantic fields
        semantic = content.get("semantic", {})
        parts.extend(semantic.get("tags", []))
        parts.extend(semantic.get("concepts", []))

        # Tags
        parts.extend(content.get("tags", []))

        return " ".join(parts)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text."""
        text = text.lower()
        tokens = re.findall(r"\b[a-z][a-z0-9_-]*\b", text)
        return [t for t in tokens if t not in self.STOP_WORDS and len(t) > 2]

    def _save(self) -> None:
        """Save index to file."""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": "1.4.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "documents": self._documents,
            "inverted_index": self._inverted_index,
        }

        with open(self.index_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, default_style="'")

    def _save_cache(self) -> None:
        """Save search cache."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self._cache, f)

    def search(self, query: str, limit: int = 20) -> List[Tuple[str, float, str]]:
        """
        Search for documents.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of (doc_id, score, snippet) tuples
        """
        # Check cache
        cache_key = f"text:{query}:{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Calculate TF-IDF scores
        scores: Dict[str, float] = {}
        num_docs = len(self._documents) or 1

        for token in query_tokens:
            if token not in self._inverted_index:
                continue

            doc_freqs = self._inverted_index[token]
            idf = math.log(num_docs / (1 + len(doc_freqs)))

            for doc_id, tf in doc_freqs.items():
                doc_length = self._documents.get(doc_id, {}).get("text_length", 1)
                # Normalized TF-IDF
                tfidf = (tf / math.sqrt(max(doc_length, 1))) * idf
                scores[doc_id] = scores.get(doc_id, 0) + tfidf

        # Sort by score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Build results
        results: List[Tuple[str, float, str]] = []
        for doc_id, score in sorted_results[:limit]:
            snippet = self._generate_snippet(doc_id, query_tokens)
            results.append((doc_id, score, snippet))

        # Cache results
        self._cache[cache_key] = results
        if len(self._cache) % 10 == 0:
            self._save_cache()

        return results

    def _generate_snippet(self, doc_id: str, query_tokens: List[str]) -> str:
        """Generate search snippet."""
        doc_meta = self._documents.get(doc_id, {})
        file_path = doc_meta.get("path")

        if not file_path or not Path(file_path).exists():
            return doc_meta.get("title", doc_id)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
        except Exception:
            return doc_meta.get("title", doc_id)

        # Handle nested structure
        for key in ["decision", "learning", "pattern", "concept"]:
            if key in content:
                content = content[key]
                break

        text = self._extract_text(content)
        text_lower = text.lower()

        # Find first match
        for token in query_tokens:
            pos = text_lower.find(token)
            if pos >= 0:
                start = max(0, pos - 50)
                end = min(len(text), pos + len(token) + 100)
                snippet = text[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."
                return snippet

        return text[:150] + "..." if len(text) > 150 else text

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata."""
        return self._documents.get(doc_id)

    def rebuild(self) -> None:
        """Force rebuild of index."""
        self._build()
        self._cache = {}


class GraphSearcher:
    """
    Graph-based semantic search.

    Expands search results using graph connections.
    """

    def __init__(self, corpus_path: Path):
        """Initialize graph searcher."""
        self.corpus_path = corpus_path
        self.graph_file = corpus_path / "graph.json"
        self.adjacency_file = corpus_path / "adjacency.json"

        self._graph: Dict[str, Any] = {"nodes": [], "edges": []}
        self._adjacency: Dict[str, Any] = {"adjacency": {}}
        self._node_index: Dict[str, Dict[str, Any]] = {}

        self._load()

    def _load(self) -> None:
        """Load graph files."""
        if self.graph_file.exists():
            try:
                with open(self.graph_file, "r", encoding="utf-8") as f:
                    self._graph = json.load(f)
                    # Build node index
                    for node in self._graph.get("nodes", []):
                        self._node_index[node["id"]] = node
            except Exception:
                pass

        if self.adjacency_file.exists():
            try:
                with open(self.adjacency_file, "r", encoding="utf-8") as f:
                    self._adjacency = json.load(f)
            except Exception:
                pass

    def expand_from_nodes(
        self,
        node_ids: List[str],
        hops: int = 2
    ) -> List[Tuple[str, float, List[str]]]:
        """
        Expand search using graph connections.

        Args:
            node_ids: Starting node IDs
            hops: Number of hops to expand

        Returns:
            List of (node_id, score, path) tuples
        """
        results: Dict[str, Tuple[float, List[str]]] = {}

        for start_node in node_ids:
            # BFS expansion
            visited: Set[str] = set()
            queue: List[Tuple[str, int, List[str]]] = [(start_node, 0, [start_node])]

            while queue:
                current, depth, path = queue.pop(0)

                if current in visited or depth > hops:
                    continue
                visited.add(current)

                # Score decreases with distance
                score = 1.0 / (1 + depth)

                if current != start_node:
                    if current not in results or results[current][0] < score:
                        results[current] = (score, path)

                # Get neighbors
                adj = self._adjacency.get("adjacency", {}).get(current, {})

                for targets in adj.get("outgoing", {}).values():
                    for target in targets:
                        if target not in visited:
                            queue.append((target, depth + 1, path + [target]))

                for sources in adj.get("incoming", {}).values():
                    for source in sources:
                        if source not in visited:
                            queue.append((source, depth + 1, path + [source]))

        return [(nid, score, path) for nid, (score, path) in results.items()]

    def find_by_concept(self, concept: str) -> List[str]:
        """Find nodes containing a concept."""
        results: List[str] = []
        concept_lower = concept.lower()

        for node in self._graph.get("nodes", []):
            concepts = node.get("concepts", [])
            if isinstance(concepts, str):
                concepts = [concepts]
            if any(concept_lower in c.lower() for c in concepts):
                results.append(node["id"])

        return results

    def find_by_phase(self, phase: int) -> List[str]:
        """Find nodes in a specific phase."""
        results: List[str] = []

        for node in self._graph.get("nodes", []):
            phases = node.get("phases", [])
            if isinstance(phases, int):
                phases = [phases]
            if phase in phases:
                results.append(node["id"])

        return results

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID."""
        return self._node_index.get(node_id)


class HybridSearcher:
    """
    Combined text and graph search.

    Merges results from text search and graph expansion.
    """

    # Weights for combining scores
    TEXT_WEIGHT = 0.7
    GRAPH_WEIGHT = 0.3
    DECAY_BOOST_WEIGHT = 0.5  # How much decay affects final score

    def __init__(self, corpus_path: Optional[Path] = None):
        """Initialize hybrid searcher."""
        if corpus_path is None:
            corpus_path = Path(".agentic_sdlc/corpus")

        self.corpus_path = Path(corpus_path)
        self.text_index = TextIndex(corpus_path)
        self.graph_searcher = GraphSearcher(corpus_path)
        self._decay_index: Optional[Dict[str, Any]] = None

    def _load_decay_index(self) -> Dict[str, Any]:
        """Load decay index from file."""
        if self._decay_index is not None:
            return self._decay_index

        decay_path = self.corpus_path / "decay_index.json"
        if decay_path.exists():
            try:
                with open(decay_path, "r", encoding="utf-8") as f:
                    self._decay_index = json.load(f)
            except Exception:
                self._decay_index = {"nodes": {}}
        else:
            self._decay_index = {"nodes": {}}

        return self._decay_index

    def _apply_decay_boost(self, results: List[SearchResult]) -> List[SearchResult]:
        """Apply decay score as boost factor to search results."""
        decay_index = self._load_decay_index()
        nodes = decay_index.get("nodes", {})

        for result in results:
            decay_data = nodes.get(result.node_id, {})
            decay_score = decay_data.get("score", 0.5)  # Default to 0.5 if not found
            decay_status = decay_data.get("status", "unknown")

            # Store decay info in result
            result.decay_score = decay_score
            result.decay_status = decay_status

            # Apply decay as multiplicative boost
            # Fresh content (score 1.0) gets full score
            # Obsolete content (score 0.1) gets reduced score
            boost_factor = self.DECAY_BOOST_WEIGHT + (1 - self.DECAY_BOOST_WEIGHT) * decay_score
            result.score = result.score * boost_factor

        # Re-sort by boosted score
        results.sort(key=lambda r: r.score, reverse=True)

        return results

    def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.HYBRID,
        limit: int = 10,
        graph_hops: int = 2,
        phase_filter: Optional[int] = None,
        concept_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Perform hybrid search.

        Args:
            query: Search query
            mode: Search mode (text, graph, hybrid)
            limit: Maximum results
            graph_hops: Hops for graph expansion
            phase_filter: Filter by SDLC phase
            concept_filter: Filter by concept
            type_filter: Filter by node type

        Returns:
            List of SearchResult objects
        """
        text_results: List[Tuple[str, float, str]] = []
        graph_results: List[Tuple[str, float, List[str]]] = []

        # Text search
        if mode in (SearchMode.TEXT, SearchMode.HYBRID):
            text_results = self.text_index.search(query, limit=limit * 2)

        # Graph expansion
        if mode in (SearchMode.GRAPH, SearchMode.HYBRID):
            if text_results:
                seed_nodes = [r[0] for r in text_results[:5]]
                graph_results = self.graph_searcher.expand_from_nodes(
                    seed_nodes, hops=graph_hops
                )

            # Also search by concepts in query
            query_tokens = query.lower().split()
            for token in query_tokens:
                if len(token) > 3:
                    concept_nodes = self.graph_searcher.find_by_concept(token)
                    for node_id in concept_nodes:
                        if not any(r[0] == node_id for r in graph_results):
                            graph_results.append((node_id, 0.4, [node_id]))

        # Apply filters
        if phase_filter is not None:
            phase_nodes = set(self.graph_searcher.find_by_phase(phase_filter))
            text_results = [(id, s, sn) for id, s, sn in text_results if id in phase_nodes]
            graph_results = [(id, s, p) for id, s, p in graph_results if id in phase_nodes]

        if concept_filter:
            concept_nodes = set(self.graph_searcher.find_by_concept(concept_filter))
            text_results = [(id, s, sn) for id, s, sn in text_results if id in concept_nodes]
            graph_results = [(id, s, p) for id, s, p in graph_results if id in concept_nodes]

        # Merge results
        merged = self._merge_results(text_results, graph_results, limit, type_filter)

        # Apply decay boosting
        merged = self._apply_decay_boost(merged)

        return merged

    def _merge_results(
        self,
        text_results: List[Tuple[str, float, str]],
        graph_results: List[Tuple[str, float, List[str]]],
        limit: int,
        type_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        """Merge and rank results."""
        combined: Dict[str, Dict[str, Any]] = {}

        # Process text results
        for node_id, score, snippet in text_results:
            combined[node_id] = {
                "text_score": score,
                "graph_score": 0,
                "snippet": snippet,
                "path": None,
            }

        # Process graph results
        for node_id, score, path in graph_results:
            if node_id in combined:
                combined[node_id]["graph_score"] = score
                combined[node_id]["path"] = path
            else:
                combined[node_id] = {
                    "text_score": 0,
                    "graph_score": score,
                    "snippet": "",
                    "path": path,
                }

        # Calculate final scores
        results: List[SearchResult] = []
        for node_id, data in combined.items():
            final_score = (
                self.TEXT_WEIGHT * data["text_score"] +
                self.GRAPH_WEIGHT * data["graph_score"]
            )

            # Determine match type
            if data["text_score"] > 0 and data["graph_score"] > 0:
                match_type = "both"
            elif data["text_score"] > 0:
                match_type = "text"
            else:
                match_type = "graph"

            # Get node info
            node_info = self._get_node_info(node_id)
            title = node_info.get("title", node_id)
            node_type = node_info.get("type", "Decision")

            # Apply type filter
            if type_filter and node_type != type_filter:
                continue

            # Generate snippet if missing
            snippet = data["snippet"]
            if not snippet and data["path"]:
                snippet = f"Related via: {' -> '.join(data['path'])}"

            results.append(SearchResult(
                node_id=node_id,
                title=title,
                score=final_score,
                match_type=match_type,
                snippet=snippet,
                node_type=node_type,
                path_from_query=data["path"],
            ))

        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)

        return results[:limit]

    def _get_node_info(self, node_id: str) -> Dict[str, Any]:
        """Get node info from index or graph."""
        # Try text index first
        doc = self.text_index.get_document(node_id)
        if doc:
            return doc

        # Try graph
        node = self.graph_searcher.get_node(node_id)
        if node:
            return node

        return {"title": node_id, "type": "Decision"}

    def rebuild_index(self) -> None:
        """Rebuild text index."""
        self.text_index.rebuild()


def main():
    """CLI interface for hybrid search."""
    parser = argparse.ArgumentParser(
        description="Hybrid Search - Combined text and graph search"
    )
    parser.add_argument(
        "query",
        help="Search query"
    )
    parser.add_argument(
        "--corpus",
        default=".agentic_sdlc/corpus",
        help="Path to corpus directory"
    )
    parser.add_argument(
        "--mode",
        choices=["text", "graph", "hybrid"],
        default="hybrid",
        help="Search mode"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum results"
    )
    parser.add_argument(
        "--hops",
        type=int,
        default=2,
        help="Graph expansion hops"
    )
    parser.add_argument(
        "--phase",
        type=int,
        help="Filter by SDLC phase (0-8)"
    )
    parser.add_argument(
        "--concept",
        help="Filter by concept"
    )
    parser.add_argument(
        "--type",
        choices=["Decision", "Learning", "Pattern", "Concept"],
        help="Filter by node type"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild index before search"
    )

    args = parser.parse_args()

    searcher = HybridSearcher(Path(args.corpus))

    if args.rebuild:
        print("Rebuilding index...")
        searcher.rebuild_index()

    results = searcher.search(
        args.query,
        mode=SearchMode(args.mode),
        limit=args.limit,
        graph_hops=args.hops,
        phase_filter=args.phase,
        concept_filter=args.concept,
        type_filter=args.type,
    )

    if args.json:
        output = [r.to_dict() for r in results]
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if not results:
            print("No results found")
        else:
            print(f"\nFound {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. [{result.match_type}] {result.title}")
                print(f"   ID: {result.node_id} | Type: {result.node_type} | Score: {result.score:.3f}")
                print(f"   {result.snippet[:100]}...")
                if result.path_from_query:
                    print(f"   Path: {' -> '.join(result.path_from_query)}")
                print()


if __name__ == "__main__":
    main()
