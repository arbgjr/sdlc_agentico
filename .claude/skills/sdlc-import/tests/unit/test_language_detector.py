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

# Add scripts directory to path
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
        # Create JS files (need 3+ for min_files threshold)
        create_file(temp_project / "package.json", '{"dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}}')
        create_file(temp_project / "src/App.js", "import React from 'react';\n\nfunction App() {\n  return <div>Hello</div>;\n}")
        create_file(temp_project / "src/index.js", "import React from 'react';\nimport ReactDOM from 'react-dom';\nimport App from './App';")
        create_file(temp_project / "src/components/Header.js", "import React from 'react';\nexport const Header = () => <header>Header</header>;")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert result["primary_language"] == "javascript"
        assert "javascript" in result["languages"]
        assert "react" in [f.lower() for f in result["frameworks"]["frontend"]]

    def test_detect_typescript_angular(self, config, temp_project):
        """Test TypeScript/Angular detection"""
        # Create TS files (need 3+ for min_files threshold)
        create_file(temp_project / "package.json", '{"dependencies": {"@angular/core": "^15.0.0"}}')
        create_file(temp_project / "src/app.component.ts", "import { Component } from '@angular/core';\n\n@Component({\n  selector: 'app-root',\n  template: '<h1>Hello</h1>'\n})\nexport class AppComponent {}")
        create_file(temp_project / "src/app.module.ts", "import { NgModule } from '@angular/core';\n\n@NgModule({\n  declarations: []\n})\nexport class AppModule {}")
        create_file(temp_project / "src/main.ts", "import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert result["primary_language"] == "typescript"
        assert "angular" in [f.lower() for f in result["frameworks"]["frontend"]]

    def test_detect_java_spring(self, config, temp_project):
        """Test Java/Spring detection"""
        # Create Java files (need 3+ for min_files threshold)
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
        create_file(temp_project / "src/main/java/Controller.java", """
            import org.springframework.web.bind.annotation.RestController;

            @RestController
            public class Controller {
            }
        """)
        create_file(temp_project / "src/main/java/Service.java", """
            import org.springframework.stereotype.Service;

            @Service
            public class Service {
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
        # Create well-defined project (need 3+ JS files for min_files threshold)
        create_file(temp_project / "package.json", '{"dependencies": {"react": "^18.0.0", "express": "^4.18.0"}}')
        create_file(temp_project / "src/App.js", "import React from 'react';")
        create_file(temp_project / "server.js", "const express = require('express');")
        create_file(temp_project / "routes/api.js", "module.exports = router;")
        create_file(temp_project / "Dockerfile", "FROM node:18")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Should have high confidence (language + frameworks + devops)
        assert result["confidence"] >= 0.7


    # NEW TESTS FOR v2.1.0 - 20 New Technologies

    def test_detect_cpp_cmake(self, config, temp_project):
        """Test C++/CMake detection"""
        # Create C++ files (need 3+ for min_files threshold)
        create_file(temp_project / "CMakeLists.txt", "cmake_minimum_required(VERSION 3.10)\nproject(MyApp)\nadd_executable(myapp main.cpp utils.cpp)")
        create_file(temp_project / "src/main.cpp", "#include <iostream>\n#include <boost/filesystem.hpp>\n\nint main() {\n    std::cout << \"Hello\";\n    return 0;\n}")
        create_file(temp_project / "src/utils.cpp", "#include \"utils.h\"\nstd::string get_version() { return \"1.0.0\"; }")
        create_file(temp_project / "src/utils.h", "#pragma once\nstd::string get_version();")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        assert result["primary_language"] == "cpp"
        assert "cpp" in result["languages"]
        assert "cmake" in [f.lower() for f in result["frameworks"]["backend"]]

    def test_detect_bicep(self, config, temp_project):
        """Test Bicep (Azure IaC) detection"""
        # Create Bicep files (need 3+ for min_files threshold)
        create_file(temp_project / "main.bicep", "resource storageAccount 'Microsoft.Storage/storageAccounts@2021-02-01' = {\n  name: 'mystorageaccount'\n  location: 'eastus'\n}")
        create_file(temp_project / "network.bicep", "resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' = {\n  name: 'myvnet'\n}")
        create_file(temp_project / "compute.bicep", "resource vm 'Microsoft.Compute/virtualMachines@2021-03-01' = {\n  name: 'myvm'\n}")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Verify Bicep detected as IaC
        frameworks = result["frameworks"]
        assert "iac" in frameworks
        iac_tools = [f.lower() for f in frameworks["iac"]]
        assert "bicep" in iac_tools

    def test_detect_ansible(self, config, temp_project):
        """Test Ansible detection (YAML disambiguation)"""
        # Create Ansible files with ansible.cfg marker
        create_file(temp_project / "ansible.cfg", "[defaults]\ninventory = inventory/hosts.yml")
        create_file(temp_project / "playbook.yml", "---\n- name: Configure servers\n  hosts: webservers\n  tasks:\n    - name: Install nginx\n      ansible.builtin.apt:\n        name: nginx")
        create_file(temp_project / "inventory/hosts.yml", "---\nall:\n  hosts:\n    web1:\n      ansible_host: 192.168.1.10")
        create_file(temp_project / "roles/web/tasks/main.yml", "---\n- name: Configure web\n  ansible.builtin.service:\n    name: nginx")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Verify Ansible detected (not generic YAML)
        frameworks = result["frameworks"]
        assert "iac" in frameworks
        iac_tools = [f.lower() for f in frameworks["iac"]]
        assert "ansible" in iac_tools

    def test_detect_jenkins(self, config, temp_project):
        """Test Jenkins detection"""
        # Create Jenkins files
        create_file(temp_project / "Jenkinsfile", "pipeline {\n  agent any\n  stages {\n    stage('Build') {\n      steps {\n        sh 'make'\n      }\n    }\n  }\n}")
        create_file(temp_project / "pipeline.groovy", "node {\n  stage('Test') {\n    echo 'Running tests'\n  }\n}")
        create_file(temp_project / "deploy.groovy", "pipeline {\n  post {\n    success {\n      echo 'Deploy success'\n    }\n  }\n}")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Verify Jenkins detected as CI/CD
        frameworks = result["frameworks"]
        assert "cicd" in frameworks
        cicd_tools = [f.lower() for f in frameworks["cicd"]]
        assert "jenkins" in cicd_tools

    def test_detect_vue(self, config, temp_project):
        """Test Vue.js detection"""
        # Create Vue files (need 3+ for min_files threshold)
        create_file(temp_project / "package.json", '{"dependencies": {"vue": "^3.3.4"}}')
        create_file(temp_project / "src/App.vue", "<template>\n  <div>{{ message }}</div>\n</template>\n<script setup>\nimport { ref } from 'vue'\nconst message = ref('Hello')\n</script>")
        create_file(temp_project / "src/components/Header.vue", "<template>\n  <header>Header</header>\n</template>\n<script setup>\n</script>")
        create_file(temp_project / "src/main.js", "import { createApp } from 'vue'\nimport App from './App.vue'\ncreateApp(App).mount('#app')")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Verify Vue detected as frontend framework
        frameworks = result["frameworks"]
        assert "frontend" in frameworks
        frontend_frameworks = [f.lower() for f in frameworks["frontend"]]
        assert "vue" in frontend_frameworks

    def test_detect_svelte(self, config, temp_project):
        """Test Svelte detection"""
        # Create Svelte files
        create_file(temp_project / "package.json", '{"dependencies": {"svelte": "^4.0.0"}}')
        create_file(temp_project / "src/App.svelte", "<script>\n  let count = 0;\n  $: doubled = count * 2;\n</script>\n<main>\n  <button on:click={() => count++}>{count}</button>\n</main>")
        create_file(temp_project / "src/components/Button.svelte", "<script>\n  export let text;\n</script>\n<button>{text}</button>")
        create_file(temp_project / "src/routes/+page.svelte", "<script>\n  import App from '../App.svelte';\n</script>")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Verify Svelte detected as frontend framework
        frameworks = result["frameworks"]
        assert "frontend" in frameworks
        frontend_frameworks = [f.lower() for f in frameworks["frontend"]]
        assert "svelte" in frontend_frameworks

    def test_detect_playwright(self, config, temp_project):
        """Test Playwright testing framework detection"""
        # Create Playwright test files
        create_file(temp_project / "package.json", '{"devDependencies": {"@playwright/test": "^1.40.0"}}')
        create_file(temp_project / "tests/home.spec.ts", "import { test, expect } from '@playwright/test';\n\ntest('home page', async ({ page }) => {\n  await page.goto('/');\n});")
        create_file(temp_project / "tests/login.spec.ts", "import { test, expect } from '@playwright/test';\n\ntest('login', async ({ page }) => {\n  await page.goto('/login');\n});")
        create_file(temp_project / "playwright.config.ts", "import { defineConfig } from '@playwright/test';\n\nexport default defineConfig({});")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Verify Playwright detected as testing framework
        frameworks = result["frameworks"]
        assert "testing" in frameworks
        testing_frameworks = [f.lower() for f in frameworks["testing"]]
        assert "playwright" in testing_frameworks

    def test_detect_flutter(self, config, temp_project):
        """Test Flutter/Dart detection"""
        # Create Flutter Dart files
        create_file(temp_project / "pubspec.yaml", "name: my_flutter_app\ndependencies:\n  flutter:\n    sdk: flutter")
        create_file(temp_project / "lib/main.dart", "import 'package:flutter/material.dart';\n\nvoid main() {\n  runApp(MyApp());\n}\n\nclass MyApp extends StatelessWidget {}")
        create_file(temp_project / "lib/screens/home.dart", "import 'package:flutter/material.dart';\n\nclass HomeScreen extends StatefulWidget {}")
        create_file(temp_project / "lib/widgets/button.dart", "import 'package:flutter/material.dart';\n\nclass CustomButton extends StatelessWidget {}")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Verify Dart detected
        assert result["primary_language"] == "dart"
        assert "dart" in result["languages"]

        # Verify Flutter detected as mobile framework
        frameworks = result["frameworks"]
        assert "mobile" in frameworks
        mobile_frameworks = [f.lower() for f in frameworks["mobile"]]
        assert "flutter" in mobile_frameworks

    def test_detect_swift(self, config, temp_project):
        """Test Swift (iOS) detection"""
        # Create Swift files
        create_file(temp_project / "Package.swift", "// swift-tools-version:5.5\nimport PackageDescription\n\nlet package = Package(\n    name: \"MyApp\"\n)")
        create_file(temp_project / "Sources/App.swift", "import SwiftUI\n\n@main\nstruct MyApp: App {\n    var body: some Scene {\n        WindowGroup {\n            ContentView()\n        }\n    }\n}")
        create_file(temp_project / "Sources/ContentView.swift", "import SwiftUI\n\nstruct ContentView: View {\n    @State private var count = 0\n}")
        create_file(temp_project / "Sources/Models/User.swift", "import Foundation\n\nstruct User {\n    let id: UUID\n}")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Verify Swift detected
        assert result["primary_language"] == "swift"
        assert "swift" in result["languages"]

        # Verify SwiftUI detected
        frameworks = result["frameworks"]
        assert "mobile" in frameworks
        mobile_frameworks = [f.lower() for f in frameworks["mobile"]]
        assert "swiftui" in mobile_frameworks

    def test_detect_vite(self, config, temp_project):
        """Test Vite build tool detection"""
        # Create Vite project files
        create_file(temp_project / "package.json", '{"devDependencies": {"vite": "^4.4.9"}}')
        create_file(temp_project / "vite.config.js", "import { defineConfig } from 'vite'\n\nexport default defineConfig({\n  plugins: []\n})")
        create_file(temp_project / "src/main.js", "console.log('Hello');")

        detector = LanguageDetector(config)
        result = detector.detect(temp_project)

        # Verify Vite detected as build tool
        frameworks = result["frameworks"]
        assert "build_tools" in frameworks
        build_tools = [f.lower() for f in frameworks["build_tools"]]
        assert "vite" in build_tools


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
