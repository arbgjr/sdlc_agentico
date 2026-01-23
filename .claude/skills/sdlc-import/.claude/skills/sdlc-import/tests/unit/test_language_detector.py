#!/usr/bin/env python3
"""
Unit tests for language_detector.py
"""

import sys
import os
import pytest
import tempfile
import yaml
from pathlib import Path

# Add lib and scripts directories to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from language_detector import LanguageDetector


@pytest.fixture
def config():
    """Load test config"""
    config_path = Path(__file__).parent.parent.parent / "config" / "import_config.yml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        yield project_path


def create_file(path: Path, content: str):
    """Helper to create file with content"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class TestLanguageDetector:
    """Test language detection"""

    def test_detect_python_django(self, config, temp_project):
        """Test Python/Django detection"""
        # Create Python files
        create_file(temp_project / "manage.py", "#!/usr/bin/env python\nimport django")
        create_file(temp_project / "settings.py", "DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql'}}")
        create_file(temp_project / "views.py", "from django.http import HttpResponse\n\ndef index(request):\n    return HttpResponse('Hello')")
        create_file(temp_project / "requirements.txt", "django==4.2.0\npsycopg2==2.9.0")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert result["primary_language"] == "python"
        assert "python" in result["languages"]
        assert "django" in [f.lower() for f in result["frameworks"]["backend"]]
        assert result["confidence"] > 0.5

    def test_detect_javascript_react(self, config, temp_project):
        """Test JavaScript/React detection"""
        # Create JS files
        create_file(temp_project / "package.json", '{"dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}}')
        create_file(temp_project / "src/App.js", "import React from 'react';\n\nfunction App() {\n  return <div>Hello</div>;\n}")
        create_file(temp_project / "src/index.js", "import React from 'react';\nimport ReactDOM from 'react-dom';\nimport App from './App';")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert result["primary_language"] == "javascript"
        assert "javascript" in result["languages"]
        assert "react" in [f.lower() for f in result["frameworks"]["frontend"]]

    def test_detect_typescript_angular(self, config, temp_project):
        """Test TypeScript/Angular detection"""
        create_file(temp_project / "package.json", '{"dependencies": {"@angular/core": "^15.0.0"}}')
        create_file(temp_project / "src/app.component.ts", "import { Component } from '@angular/core';\n\n@Component({\n  selector: 'app-root',\n  template: '<h1>Hello</h1>'\n})\nexport class AppComponent {}")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert result["primary_language"] == "typescript"
        assert "angular" in [f.lower() for f in result["frameworks"]["frontend"]]

    def test_detect_java_spring(self, config, temp_project):
        """Test Java/Spring detection"""
        create_file(temp_project / "pom.xml", """
            <project>
                <dependencies>
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-web</artifactId>
                    </dependency>
                </dependencies>
            </project>
        """)
        create_file(temp_project / "src/main/java/App.java", """
            import org.springframework.boot.SpringApplication;
            import org.springframework.boot.autoconfigure.SpringBootApplication;

            @SpringBootApplication
            public class App {
                public static void main(String[] args) {
                    SpringApplication.run(App.class, args);
                }
            }
        """)

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert result["primary_language"] == "java"
        assert "spring" in [f.lower() for f in result["frameworks"]["backend"]]

    def test_detect_devops_docker(self, config, temp_project):
        """Test Docker detection"""
        create_file(temp_project / "Dockerfile", "FROM python:3.11\nRUN pip install django")
        create_file(temp_project / "docker-compose.yml", "version: '3'\nservices:\n  web:\n    build: .")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert "Docker" in result["devops"]
        assert "Docker Compose" in result["devops"]

    def test_detect_terraform(self, config, temp_project):
        """Test Terraform detection"""
        create_file(temp_project / "main.tf", """
            resource "aws_instance" "web" {
                ami = "ami-12345678"
                instance_type = "t2.micro"
            }
        """)

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert "Terraform" in result["devops"]

    def test_detect_github_actions(self, config, temp_project):
        """Test GitHub Actions detection"""
        create_file(temp_project / ".github/workflows/ci.yml", """
            on: push
            jobs:
              test:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v3
        """)

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert "GitHub Actions" in result["devops"]

    def test_min_files_threshold(self, config, temp_project):
        """Test minimum files threshold"""
        # Create only 1 Python file (below threshold of 3)
        create_file(temp_project / "app.py", "print('hello')")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Should not detect Python (below min_files)
        assert "python" not in result["languages"]

    def test_min_percentage_threshold(self, config, temp_project):
        """Test minimum percentage threshold"""
        # Create mostly Python files, few Ruby files
        for i in range(10):
            create_file(temp_project / f"file{i}.py", "print('hello')\n" * 10)

        for i in range(3):
            create_file(temp_project / f"file{i}.rb", "puts 'hello'\n" * 2)

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Python should be detected, Ruby might not (below percentage threshold)
        assert "python" in result["languages"]
        assert result["primary_language"] == "python"

    def test_empty_project(self, config, temp_project):
        """Test empty project"""
        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert result["primary_language"] is None
        assert len(result["languages"]) == 0
        assert result["confidence"] == 0.0

    def test_confidence_calculation(self, config, temp_project):
        """Test confidence score calculation"""
        # Create well-defined project
        create_file(temp_project / "package.json", '{"dependencies": {"react": "^18.0.0", "express": "^4.18.0"}}')
        create_file(temp_project / "src/App.js", "import React from 'react';")
        create_file(temp_project / "server.js", "const express = require('express');")
        create_file(temp_project / "Dockerfile", "FROM node:18")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Should have high confidence (language + frameworks + devops)
        assert result["confidence"] >= 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
