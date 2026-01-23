#!/usr/bin/env python3
"""
Unit tests for dismissal_tracker module.
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from dismissal_tracker import (
    is_update_dismissed,
    dismiss_update,
    clear_dismissal,
    get_dismissal_info,
    update_check_count,
    STORE_FILE
)


class TestDismissalTracker:
    """Tests for dismissal tracking functions."""

    def setup_method(self):
        """Clear dismissal records before each test."""
        clear_dismissal()

    def teardown_method(self):
        """Clear dismissal records after each test."""
        clear_dismissal()

    def test_no_dismissal_initially(self):
        """Test that no version is dismissed initially."""
        assert is_update_dismissed("2.1.0") is False
        assert is_update_dismissed("2.2.0") is False

    def test_dismiss_version(self):
        """Test dismissing a specific version."""
        dismiss_update("2.1.0")

        assert is_update_dismissed("2.1.0") is True
        assert is_update_dismissed("2.2.0") is False

    def test_dismissal_persists(self):
        """Test that dismissal persists across checks."""
        dismiss_update("2.1.0")

        # Check multiple times
        for _ in range(3):
            assert is_update_dismissed("2.1.0") is True

    def test_clear_dismissal(self):
        """Test clearing dismissal records."""
        dismiss_update("2.1.0")
        assert is_update_dismissed("2.1.0") is True

        clear_dismissal()
        assert is_update_dismissed("2.1.0") is False

    def test_dismiss_overwrites_previous(self):
        """Test that new dismissal overwrites previous."""
        dismiss_update("2.1.0")
        assert is_update_dismissed("2.1.0") is True

        dismiss_update("2.2.0")
        assert is_update_dismissed("2.1.0") is False
        assert is_update_dismissed("2.2.0") is True

    def test_get_dismissal_info_when_empty(self):
        """Test getting info when no dismissal exists."""
        info = get_dismissal_info()
        assert info is None

    def test_get_dismissal_info(self):
        """Test getting dismissal information."""
        dismiss_update("2.1.0")

        info = get_dismissal_info()

        assert info is not None
        assert info["dismissed_version"] == "2.1.0"
        assert "dismissed_at" in info
        assert info["checks_count"] >= 1

        # Verify timestamp format
        datetime.fromisoformat(info["dismissed_at"])

    def test_check_count_increments(self):
        """Test that check count increments."""
        dismiss_update("2.1.0")

        initial_info = get_dismissal_info()
        initial_count = initial_info["checks_count"]

        update_check_count()

        updated_info = get_dismissal_info()
        assert updated_info["checks_count"] == initial_count + 1

    def test_dismissal_file_format(self):
        """Test that dismissal file is valid JSON."""
        dismiss_update("2.1.0")

        assert STORE_FILE.exists()

        with open(STORE_FILE) as f:
            data = json.load(f)

        assert "dismissed_version" in data
        assert "dismissed_at" in data
        assert "checks_count" in data
        assert data["dismissed_version"] == "2.1.0"

    def test_corrupted_file_handling(self):
        """Test handling of corrupted dismissal file."""
        STORE_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Write invalid JSON
        with open(STORE_FILE, "w") as f:
            f.write("invalid json {{{")

        # Should not crash, should return False
        assert is_update_dismissed("2.1.0") is False

        # Should not crash, should return None
        assert get_dismissal_info() is None

    def test_clear_nonexistent_file(self):
        """Test clearing when file doesn't exist."""
        clear_dismissal()  # Should not crash

    def test_update_check_count_without_dismissal(self):
        """Test updating check count when no dismissal exists."""
        update_check_count()  # Should not crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
