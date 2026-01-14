#!/usr/bin/env python3
"""
Concept Extractor - Extract concepts from corpus documents.

Analyzes YAML documents to extract key concepts (technologies, patterns,
domain terms) for building the semantic graph.

Usage:
    # Show extracted concepts as JSON
    python concept_extractor.py --output json

    # Save concepts as YAML files
    python concept_extractor.py --output save

    # Filter by minimum confidence
    python concept_extractor.py --min-confidence 0.5

    # Extract from single file
    python concept_extractor.py --file path/to/document.yml
"""

import re
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class ExtractedConcept:
    """Represents an extracted concept."""
    term: str
    frequency: int
    sources: List[str]
    category: str
    confidence: float
    aliases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "term": self.term,
            "frequency": self.frequency,
            "sources": self.sources,
            "category": self.category,
            "confidence": round(self.confidence, 2),
            "aliases": self.aliases,
        }


class ConceptExtractor:
    """
    Extracts concepts from corpus documents.

    Uses multiple extraction methods:
    - Seed-based matching (known technologies, patterns)
    - Pattern-based extraction (CamelCase, kebab-case)
    - N-gram extraction for technical terms
    """

    # Known concept categories with seed terms
    CATEGORY_SEEDS: Dict[str, Set[str]] = {
        "technology": {
            # Databases
            "postgresql", "postgres", "mysql", "mongodb", "redis", "sqlite",
            "elasticsearch", "dynamodb", "cassandra", "neo4j",
            # Languages
            "python", "javascript", "typescript", "csharp", "java", "golang",
            "rust", "kotlin", "swift", "ruby", "php",
            # Frameworks
            "dotnet", "react", "angular", "vue", "django", "flask", "fastapi",
            "spring", "express", "nextjs", "nuxt", "svelte",
            # Infrastructure
            "docker", "kubernetes", "terraform", "ansible", "helm",
            "prometheus", "grafana", "loki", "jaeger", "istio",
            # Cloud
            "aws", "azure", "gcp", "cloudflare", "vercel", "netlify",
            # Messaging
            "kafka", "rabbitmq", "nats", "pulsar", "sqs", "sns",
            # Auth
            "oauth", "oauth2", "jwt", "keycloak", "auth0", "okta",
            # Other
            "nginx", "apache", "graphql", "grpc", "rest", "openapi",
            "git", "github", "gitlab", "bitbucket",
        },
        "pattern": {
            # Architecture
            "microservices", "monolith", "serverless", "event-driven",
            "domain-driven", "hexagonal", "clean-architecture", "layered",
            # Design patterns
            "cqrs", "event-sourcing", "saga", "outbox", "inbox",
            "circuit-breaker", "retry", "timeout", "bulkhead", "fallback",
            "repository", "factory", "singleton", "observer", "strategy",
            "adapter", "facade", "decorator", "proxy", "mediator",
            "command", "query", "handler", "aggregate", "entity",
            # Data patterns
            "cache-aside", "write-through", "write-behind", "read-through",
            "sharding", "replication", "partitioning",
        },
        "domain": {
            # Security
            "authentication", "authorization", "encryption", "hashing",
            "audit", "compliance", "security", "rbac", "abac",
            # Operations
            "logging", "monitoring", "observability", "alerting", "tracing",
            "metrics", "healthcheck", "resilience", "availability",
            # Development
            "testing", "validation", "serialization", "deserialization",
            "migration", "deployment", "integration", "api",
            # Business
            "workflow", "pipeline", "batch", "streaming", "realtime",
            "notification", "scheduling", "queuing",
        },
        "process": {
            "agile", "scrum", "kanban", "xp", "lean",
            "sdlc", "devops", "devsecops", "gitops", "cicd",
            "review", "approval", "gate", "phase", "milestone",
            "sprint", "retrospective", "planning", "estimation",
            "tdd", "bdd", "ddd", "atdd",
        },
    }

    # Technical term patterns
    TECH_PATTERNS = [
        r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b",  # CamelCase
        r"\b[a-z]+(?:-[a-z]+)+\b",            # kebab-case
        r"\b[a-z]+(?:_[a-z]+)+\b",            # snake_case
    ]

    # Skip words (common non-concept terms)
    SKIP_WORDS = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can",
        "had", "her", "was", "one", "our", "out", "has", "have", "been",
        "being", "each", "which", "their", "will", "would", "could",
        "should", "there", "when", "what", "where", "this", "that",
        "these", "those", "with", "from", "into", "more", "some",
        "than", "then", "them", "such", "only", "other", "also",
        "just", "over", "after", "before", "because", "while",
        "about", "must", "very", "both", "even", "well", "back",
        "need", "want", "make", "like", "time", "good", "year",
        "take", "come", "know", "think", "see", "look", "way",
        "day", "thing", "man", "woman", "child", "world", "life",
        "part", "place", "case", "week", "company", "system",
        "program", "question", "work", "government", "number",
        "night", "point", "home", "water", "room", "mother",
        "area", "money", "story", "fact", "month", "lot", "right",
        "study", "book", "eye", "job", "word", "business", "issue",
        "side", "kind", "head", "house", "service", "friend",
        "father", "power", "hour", "game", "line", "end", "member",
        "law", "car", "city", "community", "name", "president",
        "team", "minute", "idea", "kid", "body", "information",
        "nothing", "ago", "lead", "social", "understand", "whether",
        "watch", "together", "follow", "around", "parent", "stop",
        "face", "anything", "create", "public", "already", "speak",
        "others", "read", "level", "allow", "add", "office", "spend",
        "door", "health", "person", "art", "sure", "war", "history",
        "party", "within", "grow", "result", "open", "change",
        "morning", "walk", "reason", "low", "win", "research", "girl",
        "guy", "early", "food", "moment", "himself", "air", "teacher",
        "force", "offer", "enough", "education", "across", "although",
        "remember", "foot", "second", "boy", "maybe", "toward",
        "able", "age", "policy", "everything", "love", "process",
        "music", "including", "consider", "appear", "actually", "buy",
        "probably", "human", "wait", "serve", "market", "die", "send",
        "expect", "sense", "build", "stay", "fall", "nation", "plan",
        "cut", "college", "interest", "death", "course", "someone",
        "experience", "behind", "reach", "local", "kill", "sit",
        "central", "run", "price", "half", "pass", "foreign",
        "always", "use", "new", "first", "last", "long", "great",
        "little", "own", "old", "same", "big", "high", "different",
        "small", "large", "next", "important", "possible", "particular",
        "major", "current", "national", "federal", "political",
        "true", "wrong", "clear", "free", "special", "available",
    }

    def __init__(self, corpus_path: Optional[Path] = None):
        """
        Initialize ConceptExtractor.

        Args:
            corpus_path: Path to corpus directory
        """
        if corpus_path is None:
            corpus_path = Path(".agentic_sdlc/corpus")

        self.corpus_path = Path(corpus_path)
        self.nodes_path = self.corpus_path / "nodes"
        self.concepts_dir = self.nodes_path / "concepts"

        # Fallback to old structure
        if not self.nodes_path.exists():
            self.nodes_path = self.corpus_path

        # Tracking
        self._all_terms: Counter = Counter()
        self._term_sources: Dict[str, Set[str]] = {}
        self._term_categories: Dict[str, str] = {}

        # Build flat seed set for quick lookup
        self._all_seeds: Set[str] = set()
        for seeds in self.CATEGORY_SEEDS.values():
            self._all_seeds.update(seeds)

    def _extract_text(self, content: Dict[str, Any]) -> str:
        """
        Extract all searchable text from document.

        Args:
            content: Document content

        Returns:
            Combined text string
        """
        parts: List[str] = []

        # Direct fields
        for field in ["title", "context", "decision", "description",
                     "problem", "solution", "rationale", "insight"]:
            if field in content and content[field]:
                parts.append(str(content[field]))

        # List fields
        for field in ["consequences", "alternatives", "requirements",
                     "actions", "tags"]:
            value = content.get(field)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        parts.append(item)
                    elif isinstance(item, dict):
                        parts.extend(str(v) for v in item.values() if v)

        # Nested consequences
        if isinstance(content.get("consequences"), dict):
            for key in ["positive", "negative", "risks"]:
                items = content["consequences"].get(key, [])
                if isinstance(items, list):
                    parts.extend(str(item) for item in items)

        # Semantic section
        semantic = content.get("semantic", {})
        parts.extend(semantic.get("tags", []))
        parts.extend(semantic.get("concepts", []))

        return " ".join(parts)

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into terms.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        text = text.lower()
        tokens = re.findall(r"\b[a-z][a-z0-9_-]*\b", text)

        # Filter out skip words and short tokens
        return [
            t for t in tokens
            if t not in self.SKIP_WORDS and len(t) > 2
        ]

    def _normalize_term(self, term: str) -> str:
        """
        Normalize a term to standard format.

        Args:
            term: Input term

        Returns:
            Normalized term
        """
        term = term.lower()
        term = term.replace("_", "-")
        term = term.strip("-")
        return term

    def _categorize_term(self, term: str) -> str:
        """
        Determine category for a term.

        Args:
            term: Input term

        Returns:
            Category name
        """
        for category, seeds in self.CATEGORY_SEEDS.items():
            if term in seeds:
                return category

            # Check partial matches
            for seed in seeds:
                if seed in term or term in seed:
                    return category

        return "domain"  # Default category

    def _extract_by_seeds(self, text: str) -> Set[str]:
        """
        Extract concepts matching seed terms.

        Args:
            text: Input text

        Returns:
            Set of matched terms
        """
        concepts: Set[str] = set()
        text_lower = text.lower()

        for term in self._all_seeds:
            if term in text_lower:
                concepts.add(term)

        return concepts

    def _extract_by_patterns(self, text: str) -> Set[str]:
        """
        Extract concepts using regex patterns.

        Args:
            text: Input text

        Returns:
            Set of matched terms
        """
        concepts: Set[str] = set()

        for pattern in self.TECH_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                normalized = self._normalize_term(match)
                if len(normalized) > 2 and normalized not in self.SKIP_WORDS:
                    concepts.add(normalized)

        return concepts

    def _extract_technical_bigrams(self, tokens: List[str]) -> Set[str]:
        """
        Extract technical bigrams (two-word terms).

        Args:
            tokens: List of tokens

        Returns:
            Set of bigram terms
        """
        concepts: Set[str] = set()

        # Technical suffixes that indicate bigrams
        tech_suffixes = {
            "service", "server", "client", "handler", "manager",
            "controller", "provider", "factory", "builder",
            "repository", "adapter", "gateway", "proxy",
            "pattern", "model", "layer", "module", "component",
        }

        for i in range(len(tokens) - 1):
            if tokens[i + 1] in tech_suffixes:
                bigram = f"{tokens[i]}-{tokens[i + 1]}"
                concepts.add(bigram)

            # Also check if first token is a seed
            if tokens[i] in self._all_seeds:
                bigram = f"{tokens[i]}-{tokens[i + 1]}"
                if tokens[i + 1] not in self.SKIP_WORDS:
                    concepts.add(bigram)

        return concepts

    def extract_from_file(self, file_path: Path) -> List[str]:
        """
        Extract concepts from a single file.

        Args:
            file_path: Path to YAML file

        Returns:
            List of extracted concepts
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
        except Exception:
            return []

        if not content:
            return []

        # Handle nested structure
        for key in ["decision", "learning", "pattern", "concept"]:
            if key in content:
                content = content[key]
                break

        doc_id = content.get("id", file_path.stem)

        # Extract text
        text = self._extract_text(content)
        tokens = self._tokenize(text)

        # Extract using multiple methods
        concepts: Set[str] = set()

        # 1. Seed matching
        concepts.update(self._extract_by_seeds(text))

        # 2. Pattern matching
        concepts.update(self._extract_by_patterns(text))

        # 3. Technical bigrams
        concepts.update(self._extract_technical_bigrams(tokens))

        # Update global tracking
        for concept in concepts:
            self._all_terms[concept] += 1
            if concept not in self._term_sources:
                self._term_sources[concept] = set()
            self._term_sources[concept].add(doc_id)

            # Track category
            if concept not in self._term_categories:
                self._term_categories[concept] = self._categorize_term(concept)

        return list(concepts)

    def extract_all(self) -> List[ExtractedConcept]:
        """
        Extract concepts from all corpus documents.

        Returns:
            List of ExtractedConcept objects
        """
        # Scan directories
        for category in ["decisions", "learnings", "patterns"]:
            category_path = self.nodes_path / category
            if not category_path.exists():
                continue

            for file_path in category_path.glob("*.yml"):
                self.extract_from_file(file_path)

        # Also scan legacy paths
        legacy_paths = [
            self.corpus_path.parent / "decisions",
            self.corpus_path.parent / "projects",
        ]

        for legacy_path in legacy_paths:
            if legacy_path.exists():
                for yml_file in legacy_path.glob("**/*.yml"):
                    self.extract_from_file(yml_file)

        # Build concept list
        concepts: List[ExtractedConcept] = []

        for term, frequency in self._all_terms.most_common():
            is_seed = term in self._all_seeds
            sources = list(self._term_sources.get(term, set()))
            category = self._term_categories.get(term, "domain")

            # Calculate confidence
            # Higher for seeds, higher for more frequent terms
            base_confidence = 0.3 if not is_seed else 0.7
            freq_bonus = min(0.3, frequency * 0.05)
            confidence = min(1.0, base_confidence + freq_bonus)

            # Generate aliases
            aliases = self._generate_aliases(term)

            concepts.append(ExtractedConcept(
                term=term,
                frequency=frequency,
                sources=sources,
                category=category,
                confidence=confidence,
                aliases=aliases,
            ))

        return concepts

    def _generate_aliases(self, term: str) -> List[str]:
        """
        Generate aliases for a term.

        Args:
            term: Input term

        Returns:
            List of aliases
        """
        aliases: Set[str] = set()

        # Add variations
        aliases.add(term.replace("-", " "))
        aliases.add(term.replace("-", "_"))
        aliases.add(term.replace("-", ""))

        # Remove original
        aliases.discard(term)

        return list(aliases)

    def save_concepts(
        self,
        concepts: List[ExtractedConcept],
        min_confidence: float = 0.3
    ) -> int:
        """
        Save extracted concepts as YAML files.

        Args:
            concepts: List of concepts to save
            min_confidence: Minimum confidence threshold

        Returns:
            Number of concepts saved
        """
        self.concepts_dir.mkdir(parents=True, exist_ok=True)

        saved = 0
        for concept in concepts:
            if concept.confidence < min_confidence:
                continue

            file_name = f"{concept.term.replace(' ', '-')}.yml"
            file_path = self.concepts_dir / file_name

            content = {
                "id": f"CONCEPT-{concept.term}",
                "type": "concept",
                "label": concept.term.replace("-", " ").title(),
                "description": f"Concept extracted from {len(concept.sources)} documents",
                "semantic": {
                    "category": concept.category,
                    "relations": [],
                    "referencedBy": concept.sources[:10],  # Limit to 10
                },
                "aliases": concept.aliases,
                "metadata": {
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                    "frequency": concept.frequency,
                    "confidence": round(concept.confidence, 2),
                },
            }

            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(content, f, default_flow_style=False, sort_keys=False,
                         allow_unicode=True)

            saved += 1

        return saved

    def stats(self) -> Dict[str, Any]:
        """
        Get extraction statistics.

        Returns:
            Statistics dictionary
        """
        category_counts: Dict[str, int] = {}
        for category in self._term_categories.values():
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "total_concepts": len(self._all_terms),
            "unique_sources": len(set().union(*self._term_sources.values())),
            "category_distribution": category_counts,
            "top_concepts": self._all_terms.most_common(10),
        }


def main():
    """CLI interface for concept extractor."""
    parser = argparse.ArgumentParser(
        description="Concept Extractor - Extract concepts from corpus documents"
    )
    parser.add_argument(
        "--corpus",
        default=".agentic_sdlc/corpus",
        help="Path to corpus directory"
    )
    parser.add_argument(
        "--output",
        choices=["json", "yaml", "save", "stats"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.3,
        help="Minimum confidence threshold"
    )
    parser.add_argument(
        "--file",
        help="Extract from single file only"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="Limit output to top N concepts"
    )

    args = parser.parse_args()

    extractor = ConceptExtractor(Path(args.corpus))

    if args.file:
        # Single file extraction
        concepts = extractor.extract_from_file(Path(args.file))
        print(f"Extracted {len(concepts)} concepts:")
        for concept in sorted(concepts):
            print(f"  - {concept}")
    else:
        # Full extraction
        concepts = extractor.extract_all()

        # Filter by confidence
        concepts = [c for c in concepts if c.confidence >= args.min_confidence]

        # Limit
        concepts = concepts[:args.top]

        if args.output == "save":
            saved = extractor.save_concepts(concepts, args.min_confidence)
            print(f"Saved {saved} concepts to {extractor.concepts_dir}")

        elif args.output == "stats":
            stats = extractor.stats()
            print(json.dumps(stats, indent=2))

        elif args.output == "json":
            output = [c.to_dict() for c in concepts]
            print(json.dumps(output, indent=2, ensure_ascii=False))

        else:  # yaml
            for concept in concepts:
                print(f"\n{concept.term} ({concept.category})")
                print(f"  Frequency: {concept.frequency}")
                print(f"  Confidence: {concept.confidence:.2f}")
                print(f"  Sources: {', '.join(concept.sources[:5])}")


if __name__ == "__main__":
    main()
