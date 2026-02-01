"""
Pytest fixtures for hook testing.

Provides common fixtures for testing Python hooks:
- Temporary git repository
- Mock files and directories
- Environment variables
"""

import os
import tempfile
import shutil
from pathlib import Path
import subprocess
import pytest


@pytest.fixture
def temp_git_repo(tmp_path):
    """
    Create a temporary git repository for testing.

    Returns:
        Path: Path to temporary git repository
    """
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        check=True,
        capture_output=True
    )

    # Create .claude directory structure
    claude_dir = repo_dir / ".claude"
    claude_dir.mkdir()
    (claude_dir / "hooks").mkdir()
    (claude_dir / "skills").mkdir()
    (claude_dir / "agents").mkdir()

    # Create gate-evaluator structure
    gate_dir = claude_dir / "skills" / "gate-evaluator" / "gates"
    gate_dir.mkdir(parents=True)

    # Create initial commit
    (repo_dir / "README.md").write_text("# Test Repository\n")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True
    )

    return repo_dir


@pytest.fixture
def mock_env(monkeypatch):
    """
    Provide clean environment for testing.

    Args:
        monkeypatch: pytest monkeypatch fixture

    Returns:
        dict: Environment variables that can be modified
    """
    env = {
        "SDLC_LOG_LEVEL": "DEBUG",
        "SDLC_LOKI_ENABLED": "false",
    }

    for key, value in env.items():
        monkeypatch.setenv(key, value)

    return env


@pytest.fixture
def sample_commit_message():
    """
    Provide sample commit messages for testing.

    Returns:
        dict: Valid and invalid commit messages
    """
    return {
        "valid": "feat(auth): add user authentication",
        "valid_with_scope": "fix(orders): correct order calculation",
        "valid_no_scope": "docs: update README",
        "invalid_no_type": "add new feature",
        "invalid_too_long": "feat(orders): " + "x" * 100,
        "forbidden_word": "feat(test): add TODO feature",
    }


@pytest.fixture
def sample_gate_definition(temp_git_repo):
    """
    Create sample gate definition YAML file.

    Args:
        temp_git_repo: Temporary git repository fixture

    Returns:
        Path: Path to gate definition file
    """
    gate_content = """---
name: phase-2-to-3
description: Gate between Requirements and Architecture phases
required_artifacts:
  - name: Requirements Document
    path: .agentic_sdlc/projects/current/requirements/requirements.md

  - name: User Stories
    path: .agentic_sdlc/projects/current/requirements/user-stories.yml

quality_criteria:
  - criterion: All user stories have acceptance criteria
    validation: manual
"""

    gate_file = (
        temp_git_repo
        / ".claude"
        / "skills"
        / "gate-evaluator"
        / "gates"
        / "phase-2-to-3.yml"
    )
    gate_file.write_text(gate_content)

    return gate_file


@pytest.fixture
def sample_files(temp_git_repo):
    """
    Create sample files in repository.

    Args:
        temp_git_repo: Temporary git repository fixture

    Returns:
        dict: Paths to created sample files
    """
    files = {}

    # Create sample source file
    src_dir = temp_git_repo / "src"
    src_dir.mkdir()
    files["source"] = src_dir / "main.py"
    files["source"].write_text("def main():\n    print('Hello')\n")

    # Create sample test file
    test_dir = temp_git_repo / "tests"
    test_dir.mkdir()
    files["test"] = test_dir / "test_main.py"
    files["test"].write_text("def test_main():\n    assert True\n")

    # Create sample README
    files["readme"] = temp_git_repo / "README.md"
    files["readme"].write_text("# Sample Project\n")

    return files
