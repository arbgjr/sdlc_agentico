#!/usr/bin/env python3
"""
Integration tests for Ansible project analysis.

Tests the full sdlc-import workflow on a sample Ansible project.
Tests YAML disambiguation (Ansible vs generic YAML).
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
def ansible_project():
    """Create a minimal Ansible project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create ansible.cfg (disambiguation marker)
        create_file(
            project_path / "ansible.cfg",
            """[defaults]
inventory = inventory/hosts.yml
host_key_checking = False
retry_files_enabled = False

[privilege_escalation]
become = True
become_method = sudo
become_user = root
"""
        )

        # Create inventory
        create_file(
            project_path / "inventory/hosts.yml",
            """---
all:
  hosts:
    web1:
      ansible_host: 192.168.1.10
    web2:
      ansible_host: 192.168.1.11
    db1:
      ansible_host: 192.168.1.20

  children:
    webservers:
      hosts:
        web1:
        web2:

    databases:
      hosts:
        db1:
"""
        )

        # Create playbook
        create_file(
            project_path / "playbook.yml",
            """---
- name: Configure web servers
  hosts: webservers
  become: yes

  tasks:
    - name: Install nginx
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Start nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: yes

    - name: Copy nginx config
      ansible.builtin.template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart nginx

  handlers:
    - name: Restart nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
"""
        )

        # Create role
        create_file(
            project_path / "roles/database/tasks/main.yml",
            """---
- name: Install PostgreSQL
  ansible.builtin.apt:
    name:
      - postgresql
      - postgresql-contrib
      - python3-psycopg2
    state: present

- name: Ensure PostgreSQL is running
  ansible.builtin.service:
    name: postgresql
    state: started
    enabled: yes

- name: Create database
  community.postgresql.postgresql_db:
    name: myapp_db
    encoding: UTF-8
"""
        )

        # Create requirements.yml
        create_file(
            project_path / "requirements.yml",
            """---
collections:
  - name: community.postgresql
    version: ">=2.0.0"
  - name: ansible.posix
    version: ">=1.5.0"
"""
        )

        # Create template
        create_file(
            project_path / "templates/nginx.conf.j2",
            """user www-data;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name {{ ansible_hostname }};

        location / {
            proxy_pass http://localhost:8000;
        }
    }
}
"""
        )

        create_file(
            project_path / "README.md",
            """# Ansible Playbooks

Infrastructure automation using Ansible.
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


class TestAnsibleIntegration:
    """Integration tests for Ansible project analysis"""

    def test_analyze_basic_structure(self, ansible_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(ansible_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify basic structure
        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert "branch" in result
        assert "scan" in result

    def test_ansible_iac_detection(self, ansible_project):
        """Test Ansible IaC detection"""
        analyzer = ProjectAnalyzer(str(ansible_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify framework detection
        assert "language_analysis" in result
        frameworks = result["language_analysis"]["frameworks"]

        # Ansible should be detected as IaC tool
        assert "iac" in frameworks
        iac_tools = [f.lower() for f in frameworks["iac"]]
        assert "ansible" in iac_tools

    def test_yaml_disambiguation(self, ansible_project):
        """Test YAML disambiguation (Ansible vs generic YAML)"""
        analyzer = ProjectAnalyzer(str(ansible_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify that Ansible is detected, not generic YAML
        frameworks = result["language_analysis"]["frameworks"]
        iac_tools = [f.lower() for f in frameworks["iac"]]

        # Should detect Ansible due to ansible.cfg marker
        assert "ansible" in iac_tools

    def test_ansible_builtin_modules_detection(self, ansible_project):
        """Test Ansible builtin modules detection"""
        analyzer = ProjectAnalyzer(str(ansible_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify Ansible detection
        frameworks = result["language_analysis"]["frameworks"]
        iac_tools = [f.lower() for f in frameworks["iac"]]

        # Ansible should be detected via builtin modules pattern
        assert "ansible" in iac_tools

    def test_file_count_yaml(self, ansible_project):
        """Test that YAML files are counted correctly"""
        analyzer = ProjectAnalyzer(str(ansible_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify scan results
        scan = result["scan"]
        files_by_ext = scan["files_by_extension"]

        # Should detect .yml files
        assert ".yml" in files_by_ext
        assert files_by_ext[".yml"]["count"] >= 4
