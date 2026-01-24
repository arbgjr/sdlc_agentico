import pytest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from issue_creator import IssueCreator


class TestIssueCreator:
    @pytest.fixture
    def creator(self):
        config = {
            "github_integration": {
                "create_issues": True,
                "min_priority": "P1"
            }
        }
        return IssueCreator(config)

    @pytest.fixture
    def sample_tech_debt(self):
        return [
            {
                "title": "Hardcoded database connection",
                "priority": "P0",
                "category": "security",
                "description": "Database credentials hardcoded in appsettings.json",
                "file": "appsettings.json",
                "line": 15,
                "effort_hours": 2,
                "recommendation": "Move to environment variables or Key Vault"
            },
            {
                "title": "Missing input validation",
                "priority": "P1",
                "category": "security",
                "description": "API endpoints lack input validation",
                "file": "Controllers/UserController.cs",
                "line": 42,
                "effort_hours": 4,
                "recommendation": "Add FluentValidation or Data Annotations"
            },
            {
                "title": "Code duplication in services",
                "priority": "P2",
                "category": "maintainability",
                "description": "Duplicate code across service classes",
                "file": "Services/",
                "line": 0,
                "effort_hours": 8,
                "recommendation": "Extract common logic to base class"
            }
        ]

    def test_priority_filtering(self, creator):
        """Test that priority filtering works correctly"""
        # P0 should be created
        assert creator._should_create_issue("P0") is True

        # P1 should be created
        assert creator._should_create_issue("P1") is True

        # P2 should be skipped
        assert creator._should_create_issue("P2") is False

        # P3 should be skipped
        assert creator._should_create_issue("P3") is False

    def test_priority_filtering_with_different_min(self):
        """Test priority filtering with different minimum"""
        config = {
            "github_integration": {
                "create_issues": True,
                "min_priority": "P2"
            }
        }
        creator = IssueCreator(config)

        # Now P2 should also be created
        assert creator._should_create_issue("P0") is True
        assert creator._should_create_issue("P1") is True
        assert creator._should_create_issue("P2") is True
        assert creator._should_create_issue("P3") is False

    def test_disabled_creation(self, sample_tech_debt):
        """Test that disabled creation returns correct result"""
        config = {
            "github_integration": {
                "create_issues": False
            }
        }
        creator = IssueCreator(config)

        result = creator.create_issues(sample_tech_debt, Path("."))
        assert result["created"] == 0
        assert result["skipped"] == 3
        assert "error" not in result

    def test_gh_cli_check(self, creator):
        """Test gh CLI availability check"""
        # Check if gh CLI is available
        has_gh = creator._check_gh_cli()
        # Test passes regardless, just checking the method works
        assert isinstance(has_gh, bool)

    def test_create_issues_without_gh_cli(self, sample_tech_debt, monkeypatch):
        """Test that missing gh CLI is handled gracefully"""
        config = {
            "github_integration": {
                "create_issues": True,
                "min_priority": "P1"
            }
        }
        creator = IssueCreator(config)

        # Mock _check_gh_cli to return False
        def mock_check_gh_cli(self):
            return False

        monkeypatch.setattr(IssueCreator, "_check_gh_cli", mock_check_gh_cli)

        result = creator.create_issues(sample_tech_debt, Path("."))
        assert result["created"] == 0
        assert result["skipped"] == 3
        assert "error" in result
        assert result["error"] == "gh CLI not available"

    def test_enabled_flag(self):
        """Test that enabled flag is read from config"""
        config = {"github_integration": {"create_issues": True}}
        creator = IssueCreator(config)
        assert creator.enabled is True

        config = {"github_integration": {"create_issues": False}}
        creator = IssueCreator(config)
        assert creator.enabled is False

    def test_min_priority_default(self):
        """Test that min_priority defaults to P1"""
        config = {"github_integration": {"create_issues": True}}
        creator = IssueCreator(config)
        assert creator.min_priority == "P1"

    def test_min_priority_custom(self):
        """Test that min_priority can be customized"""
        config = {"github_integration": {"create_issues": True, "min_priority": "P0"}}
        creator = IssueCreator(config)
        assert creator.min_priority == "P0"

    def test_issue_filtering(self, creator, sample_tech_debt):
        """Test that issues are filtered correctly before creation"""
        # With min_priority=P1, should filter out P2 and keep P0, P1
        filtered = [item for item in sample_tech_debt
                   if creator._should_create_issue(item.get('priority', 'P3'))]

        assert len(filtered) == 2
        assert all(item['priority'] in ['P0', 'P1'] for item in filtered)

    def test_empty_tech_debt_list(self, creator):
        """Test handling of empty tech debt list"""
        result = creator.create_issues([], Path("."))

        if creator.enabled and creator._check_gh_cli():
            assert result["created"] == 0
            assert result["skipped"] == 0
        else:
            # If disabled or no gh CLI
            assert result["created"] == 0

    def test_tech_debt_without_priority(self, creator):
        """Test tech debt items without priority field"""
        items = [
            {
                "title": "No priority item",
                "description": "Item without priority field"
            }
        ]

        # Should default to P3 and be skipped
        filtered = [item for item in items
                   if creator._should_create_issue(item.get('priority', 'P3'))]
        assert len(filtered) == 0
