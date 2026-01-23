#!/usr/bin/env python3
"""
Unit tests for find_related.py
"""

import sys
import pytest
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from find_related import (
    extract_keywords,
    calculate_keyword_overlap,
    calculate_text_similarity,
    find_related_documents
)


class TestExtractKeywords:
    """Test keyword extraction."""

    def test_basic_extraction(self):
        text = "OAuth authentication security best practices implementation"
        keywords = extract_keywords(text)

        assert "oauth" in keywords
        assert "authentication" in keywords
        assert "security" in keywords
        # Stop words should be filtered
        assert "the" not in keywords
        assert "and" not in keywords

    def test_case_insensitive(self):
        text = "OAuth OAUTH oauth"
        keywords = extract_keywords(text)

        # Should normalize to lowercase
        assert keywords.count("oauth") == 1

    def test_minimum_length(self):
        text = "a an be to OAuth"
        keywords = extract_keywords(text)

        # Short words (< 3 chars) should be filtered
        assert "a" not in keywords
        assert "an" not in keywords
        assert "be" not in keywords
        assert "to" not in keywords
        assert "oauth" in keywords

    def test_top_n_limit(self):
        text = " ".join([f"word{i}" for i in range(20)])
        keywords = extract_keywords(text, top_n=5)

        assert len(keywords) <= 5


class TestCalculateKeywordOverlap:
    """Test keyword overlap calculation."""

    def test_identical_keywords(self):
        keywords1 = ["oauth", "authentication", "security"]
        keywords2 = ["oauth", "authentication", "security"]

        overlap = calculate_keyword_overlap(keywords1, keywords2)
        assert overlap == 1.0

    def test_no_overlap(self):
        keywords1 = ["oauth", "authentication"]
        keywords2 = ["database", "migration"]

        overlap = calculate_keyword_overlap(keywords1, keywords2)
        assert overlap == 0.0

    def test_partial_overlap(self):
        keywords1 = ["oauth", "authentication", "security"]
        keywords2 = ["oauth", "database", "migration"]

        overlap = calculate_keyword_overlap(keywords1, keywords2)
        # Intersection: 1 (oauth), Union: 5 (all unique)
        assert overlap == pytest.approx(0.2, abs=0.01)

    def test_empty_keywords(self):
        keywords1 = []
        keywords2 = ["oauth"]

        overlap = calculate_keyword_overlap(keywords1, keywords2)
        assert overlap == 0.0


class TestCalculateTextSimilarity:
    """Test text similarity calculation."""

    def test_identical_text(self):
        text1 = "OAuth 2.0 authentication best practices"
        text2 = "OAuth 2.0 authentication best practices"

        similarity = calculate_text_similarity(text1, text2)
        assert similarity == 1.0

    def test_no_similarity(self):
        text1 = "OAuth authentication"
        text2 = "Database migration"

        similarity = calculate_text_similarity(text1, text2)
        assert similarity == 0.0

    def test_partial_similarity(self):
        text1 = "OAuth 2.0 authentication security"
        text2 = "OAuth authentication implementation"

        similarity = calculate_text_similarity(text1, text2)
        # Some words overlap (oauth, authentication)
        assert 0.0 < similarity < 1.0

    def test_case_insensitive(self):
        text1 = "OAuth Authentication"
        text2 = "oauth authentication"

        similarity = calculate_text_similarity(text1, text2)
        assert similarity == 1.0


class TestFindRelatedDocuments:
    """Test document finding functionality."""

    @pytest.fixture
    def temp_index(self, tmp_path):
        """Create temporary index file."""
        import yaml

        index_data = {
            "documents": [
                {
                    "id": "DOC-001",
                    "title": "OAuth 2.0 Specification",
                    "path": "references/oauth-spec.pdf",
                    "keywords": ["oauth", "authentication", "security"],
                    "summary": "OAuth 2.0 authorization framework specification",
                    "category": "technical"
                },
                {
                    "id": "DOC-002",
                    "title": "Database Migration Guide",
                    "path": "references/db-migration.pdf",
                    "keywords": ["database", "migration", "postgresql"],
                    "summary": "Guide to database schema migrations",
                    "category": "technical"
                },
                {
                    "id": "DOC-003",
                    "title": "OAuth 2.1 Draft",
                    "path": "references/oauth2.1-draft.pdf",
                    "keywords": ["oauth", "oauth2.1", "security"],
                    "summary": "OAuth 2.1 draft specification with security improvements",
                    "category": "technical"
                }
            ]
        }

        index_path = tmp_path / "_index.yml"
        with open(index_path, 'w') as f:
            yaml.dump(index_data, f)

        return index_path

    def test_find_related_by_keywords(self, temp_index):
        prompt = "Research OAuth 2.1 migration best practices"
        results = find_related_documents(prompt, temp_index, min_similarity=0.1)

        # Should find OAuth-related documents (with low threshold)
        doc_ids = [doc_id for doc_id, _, _ in results]
        assert len(doc_ids) > 0
        # DOC-001 or DOC-003 should be in results (both OAuth-related)
        assert "DOC-001" in doc_ids or "DOC-003" in doc_ids

    def test_similarity_threshold(self, temp_index):
        prompt = "OAuth authentication"

        # Low threshold - should find more documents
        results_low = find_related_documents(prompt, temp_index, min_similarity=0.1)

        # High threshold - should find fewer documents
        results_high = find_related_documents(prompt, temp_index, min_similarity=0.8)

        assert len(results_high) <= len(results_low)

    def test_top_k_limit(self, temp_index):
        prompt = "OAuth security"

        results = find_related_documents(prompt, temp_index, min_similarity=0.1, top_k=1)

        # Should return at most 1 result
        assert len(results) <= 1

    def test_no_documents_found(self, temp_index):
        prompt = "Kubernetes deployment"

        results = find_related_documents(prompt, temp_index, min_similarity=0.6)

        # Should not find any related documents
        assert len(results) == 0

    def test_empty_index(self, tmp_path):
        import yaml

        # Create empty index
        index_path = tmp_path / "_index.yml"
        with open(index_path, 'w') as f:
            yaml.dump({"documents": []}, f)

        prompt = "OAuth authentication"
        results = find_related_documents(prompt, index_path)

        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
