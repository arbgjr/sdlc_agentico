#!/usr/bin/env python3
"""
Integration tests for Django project analysis.

Tests the full sdlc-import workflow on a sample Django project.

NOTE: These tests are currently limited to Steps 1-3 of the analyze() workflow:
- Step 1: Branch creation
- Step 2: Project validation
- Step 3: Directory scanning

Steps 4-9 (language detection, decision extraction, etc.) are marked TODO
and will be implemented in subsequent tasks.
"""

import sys
import pytest
import tempfile
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from project_analyzer import ProjectAnalyzer


def create_file(path: Path, content: str):
    """Helper to create file with content"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


@pytest.fixture
def django_project():
    """Create a minimal Django project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create Django structure
        create_file(
            project_path / "manage.py",
            """#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
"""
        )

        create_file(
            project_path / "myproject/settings.py",
            """
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'mydb'),
        'USER': os.environ.get('DB_USER', 'user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]
"""
        )

        create_file(
            project_path / "myproject/urls.py",
            """
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""
        )

        create_file(
            project_path / "requirements.txt",
            """django==4.2.0
psycopg2-binary==2.9.5
redis==4.5.0
celery==5.2.7
"""
        )

        create_file(
            project_path / "tasks.py",
            """
from celery import Celery

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')

@app.task
def example_task(x, y):
    return x + y
"""
        )

        create_file(
            project_path / "README.md",
            """# My Django Project

This is a sample Django project.
"""
        )

        # Initialize git (required for analyze())
        import subprocess
        subprocess.run(["git", "init"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(project_path), check=True, capture_output=True)

        yield project_path


class TestDjangoIntegration:
    """Integration tests for Django project analysis (Steps 1-3 only)"""

    def test_analyze_basic_structure(self, django_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(django_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify basic structure (Steps 1-3 output)
        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert "branch" in result
        assert "scan" in result

        # Verify project path
        assert result["project_path"] == str(django_project)

        # Verify timestamp format (ISO 8601 with Z)
        assert result["timestamp"].endswith("Z")
        assert "T" in result["timestamp"]

    def test_branch_creation_django(self, django_project):
        """Test that feature branch is created (Step 1)"""
        analyzer = ProjectAnalyzer(str(django_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify branch info is returned
        assert "branch" in result
        assert isinstance(result["branch"], dict)
        assert "branch" in result["branch"]
        assert "created" in result["branch"]

        # Verify branch name format
        branch_name = result["branch"]["branch"]
        assert branch_name.startswith("feature/import-")

        # Verify branch was created
        assert result["branch"]["created"] is True

        # Verify branch exists in git
        import subprocess
        branches_result = subprocess.run(
            ["git", "branch"],
            cwd=str(django_project),
            capture_output=True,
            text=True
        )
        assert branch_name in branches_result.stdout

    def test_directory_scan_django(self, django_project):
        """Test directory scanning (Step 3)"""
        analyzer = ProjectAnalyzer(str(django_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify scan results
        assert "scan" in result
        scan = result["scan"]

        assert "total_files" in scan
        assert "total_loc" in scan
        assert "files_by_extension" in scan

        # Should detect Python files
        assert scan["total_files"] >= 5
        assert ".py" in scan["files_by_extension"]

        # Verify Python files structure
        py_info = scan["files_by_extension"][".py"]
        assert "count" in py_info
        assert "loc" in py_info
        assert "files" in py_info
        assert py_info["count"] >= 3

    def test_project_validation_django(self, django_project):
        """Test project validation (Step 2)"""
        analyzer = ProjectAnalyzer(str(django_project))

        # Validation should pass for valid Django project
        is_valid = analyzer.validate_project()
        assert is_valid is True

    @pytest.mark.skip(reason="Language detection (Step 4) not yet implemented")
    def test_language_detection_django(self, django_project):
        """Test language detection - FUTURE IMPLEMENTATION"""
        pass

    @pytest.mark.skip(reason="Decision extraction (Step 5) not yet implemented")
    def test_decision_extraction_django(self, django_project):
        """Test decision extraction - FUTURE IMPLEMENTATION"""
        pass
