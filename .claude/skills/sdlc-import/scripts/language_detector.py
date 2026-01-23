#!/usr/bin/env python3
"""
Language Detector - Detect programming languages and frameworks
Uses pattern matching + LSP plugins for deep analysis.

Supports 10 languages:
- Python (Django, Flask, FastAPI)
- JavaScript (React, Next.js, Express)
- TypeScript (Angular, NestJS)
- Java (Spring, Maven, Gradle)
- C# (ASP.NET, Entity Framework)
- Go (Gin, GORM)
- Ruby (Rails)
- PHP (Laravel, Symfony)
- Rust (Actix)
- Kotlin (Ktor)

References:
- awesome-copilot: language-stack-identifier.prompt
- awesome-copilot: framework-detector.prompt
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import yaml

# Add logging utilities
# Add logging utilities (absolute path from project root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class LanguageDetector:
    """Detect programming languages and frameworks in a project"""

    def __init__(self, config: Dict):
        """
        Initialize language detector.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.language_patterns = self._load_language_patterns()
        self.min_files = config['language_detection']['min_files']
        self.min_percentage = config['language_detection']['min_percentage']
        self.confidence_threshold = config['language_detection']['confidence_threshold']
        self.lsp_enabled = config['language_detection'].get('lsp_enabled', True)

        logger.info(
            "Initialized LanguageDetector",
            extra={
                "min_files": self.min_files,
                "min_percentage": self.min_percentage,
                "lsp_enabled": self.lsp_enabled
            }
        )

    def _load_language_patterns(self) -> Dict:
        """Load language patterns from YAML"""
        patterns_file = Path(__file__).parent.parent / "config" / "language_patterns.yml"
        with open(patterns_file, 'r') as f:
            patterns = yaml.safe_load(f)
        return patterns

    def detect(self, project_path: Path) -> Dict:
        """
        Detect languages and frameworks in project.

        Args:
            project_path: Path to project

        Returns:
            Dict with language analysis
        """
        with log_operation("detect_languages", logger):
            # Step 1: Count files by extension
            file_stats = self._count_files_by_extension(project_path)

            # Step 2: Calculate language percentages (with disambiguation)
            language_stats = self._calculate_language_stats(file_stats, project_path)

            # Step 3: Detect frameworks
            frameworks = self._detect_frameworks(project_path, language_stats)

            # Step 4: Detect IaC and CI/CD
            devops = self._detect_devops(project_path)

            # Step 5: Calculate overall confidence
            confidence = self._calculate_confidence(language_stats, frameworks)

            # Step 6: LSP analysis (if enabled)
            lsp_analysis = {}
            if self.lsp_enabled and language_stats:
                lsp_analysis = self._lsp_analysis(project_path, language_stats)

            result = {
                "primary_language": self._get_primary_language(language_stats),
                "languages": language_stats,
                "frameworks": frameworks,
                "devops": devops,
                "lsp_analysis": lsp_analysis,
                "confidence": confidence
            }

            logger.info(
                "Language detection complete",
                extra={
                    "primary_language": result["primary_language"],
                    "language_count": len(language_stats),
                    "confidence": confidence
                }
            )

            return result

    def _count_files_by_extension(self, project_path: Path) -> Dict:
        """Count files and LOC by extension"""
        exclude_patterns = self.config['general']['exclude_patterns']
        file_stats = defaultdict(lambda: {"count": 0, "loc": 0, "files": []})

        for file in project_path.rglob("*"):
            # Skip excluded patterns
            if any(pattern in str(file) for pattern in exclude_patterns):
                continue

            if not file.is_file():
                continue

            ext = file.suffix.lower()
            if not ext:
                continue

            # Count LOC
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    # Count non-empty, non-comment lines
                    loc = sum(
                        1 for line in lines
                        if line.strip() and not line.strip().startswith(('#', '//', '/*'))
                    )
                    file_stats[ext]["loc"] += loc
            except Exception:
                continue

            file_stats[ext]["count"] += 1
            file_stats[ext]["files"].append(str(file.relative_to(project_path)))

        return dict(file_stats)

    def _calculate_language_stats(self, file_stats: Dict, project_path: Path = None) -> Dict:
        """Calculate language statistics from file counts with disambiguation"""
        language_stats = {}
        total_loc = sum(stats["loc"] for stats in file_stats.values())

        if total_loc == 0:
            return {}

        # Check for disambiguation markers
        has_chef_markers = self._has_chef_markers(project_path) if project_path else False
        has_ansible_markers = self._has_ansible_markers(project_path) if project_path else False

        # Map extensions to languages
        for lang_name, lang_config in self.language_patterns['languages'].items():
            extensions = lang_config['extensions']

            # Handle disambiguation for overlapping extensions
            if lang_name == 'ruby' and has_chef_markers:
                # Skip Ruby if Chef markers are present
                continue
            elif lang_name == 'chef' and not has_chef_markers:
                # Skip Chef if no Chef markers
                continue

            lang_loc = sum(
                file_stats.get(ext, {}).get("loc", 0)
                for ext in extensions
            )
            lang_files = sum(
                file_stats.get(ext, {}).get("count", 0)
                for ext in extensions
            )

            if lang_files < self.min_files:
                continue

            percentage = (lang_loc / total_loc) * 100

            if percentage < self.min_percentage:
                continue

            language_stats[lang_name] = {
                "percentage": round(percentage, 2),
                "files": lang_files,
                "loc": lang_loc
            }

        return language_stats

    def _has_chef_markers(self, project_path: Path) -> bool:
        """Check if project has Chef markers"""
        if not project_path:
            return False

        config_mgmt = self.language_patterns.get('config_mgmt_tools', {})
        chef_config = config_mgmt.get('chef', {})

        if not chef_config:
            return False

        # Check for marker files
        disambiguation = chef_config.get('disambiguation', {})
        marker_files = disambiguation.get('marker_files', [])

        for marker in marker_files:
            if (project_path / marker).exists():
                return True

        return False

    def _has_ansible_markers(self, project_path: Path) -> bool:
        """Check if project has Ansible markers"""
        if not project_path:
            return False

        iac_config = self.language_patterns.get('iac', {})
        ansible_config = iac_config.get('ansible', {})

        if not ansible_config:
            return False

        # Check for marker files
        disambiguation = ansible_config.get('disambiguation', {})
        marker_files = disambiguation.get('marker_files', [])

        for marker in marker_files:
            if (project_path / marker).exists():
                return True

        return False

    def _get_primary_language(self, language_stats: Dict) -> Optional[str]:
        """Get primary language (highest percentage)"""
        if not language_stats:
            return None
        return max(language_stats.items(), key=lambda x: x[1]["percentage"])[0]

    def _detect_frameworks(self, project_path: Path, language_stats: Dict) -> Dict:
        """Detect frameworks for detected languages"""
        frameworks = {
            "backend": [],
            "frontend": [],
            "database": [],
            "cache": [],
            "messaging": [],
            "testing": [],
            "iac": [],
            "config_mgmt": [],
            "cicd": [],
            "build_tools": [],
            "mobile": []
        }

        for lang_name in language_stats.keys():
            if lang_name not in self.language_patterns['languages']:
                continue

            lang_config = self.language_patterns['languages'][lang_name]
            framework_signatures = lang_config.get('framework_signatures', {})

            for framework_name, signatures in framework_signatures.items():
                if self._check_framework_signatures(project_path, signatures):
                    # Categorize framework
                    category = self._categorize_framework(framework_name, lang_name)
                    if category and framework_name not in frameworks[category]:
                        frameworks[category].append(framework_name.title())

        # Detect testing frameworks
        for test_name, test_config in self.language_patterns.get('testing', {}).items():
            if self._check_pattern(project_path, test_config['pattern'], test_config.get('location', ['**/*'])):
                frameworks['testing'].append(test_name)

        # NEW: Detect IaC tools
        frameworks['iac'] = self._detect_iac_tools(project_path)

        # NEW: Detect configuration management tools
        frameworks['config_mgmt'] = self._detect_config_mgmt_tools(project_path)

        # NEW: Detect CI/CD tools
        frameworks['cicd'] = self._detect_cicd_tools(project_path)

        # NEW: Detect frontend frameworks
        frameworks['frontend'].extend(self._detect_frontend_frameworks(project_path))

        # NEW: Detect build tools
        frameworks['build_tools'] = self._detect_build_tools(project_path)

        # NEW: Detect mobile frameworks
        frameworks['mobile'] = self._detect_mobile_frameworks(project_path)

        # NEW: Detect testing frameworks (multi-language)
        frameworks['testing'].extend(self._detect_testing_frameworks(project_path, language_stats))

        return frameworks

    def _detect_iac_tools(self, project_path: Path) -> List[str]:
        """Detect Infrastructure as Code tools"""
        iac_tools = []
        iac_config = self.language_patterns.get('iac', {})

        for tool_name, tool_config in iac_config.items():
            if self._check_tool_signatures(project_path, tool_config):
                iac_tools.append(tool_name.title())

        return iac_tools

    def _detect_config_mgmt_tools(self, project_path: Path) -> List[str]:
        """Detect Configuration Management tools (Chef, Puppet)"""
        tools = []
        config_mgmt = self.language_patterns.get('config_mgmt_tools', {})

        for tool_name, tool_config in config_mgmt.items():
            if self._check_tool_signatures(project_path, tool_config):
                tools.append(tool_name.title())

        return tools

    def _detect_cicd_tools(self, project_path: Path) -> List[str]:
        """Detect CI/CD tools"""
        tools = []
        cicd_config = self.language_patterns.get('cicd', {})

        for tool_name, tool_config in cicd_config.items():
            if self._check_tool_signatures(project_path, tool_config):
                tools.append(tool_name.replace('_', ' ').title())

        return tools

    def _detect_frontend_frameworks(self, project_path: Path) -> List[str]:
        """Detect frontend frameworks (Vue, Svelte, React Native, etc.)"""
        frameworks = []
        frontend_config = self.language_patterns.get('frontend_frameworks', {})

        for framework_name, framework_config in frontend_config.items():
            if self._check_tool_signatures(project_path, framework_config):
                frameworks.append(framework_name.replace('_', ' ').title())

        return frameworks

    def _detect_build_tools(self, project_path: Path) -> List[str]:
        """Detect build tools (Vite, Webpack)"""
        tools = []
        build_config = self.language_patterns.get('build_tools', {})

        for tool_name, tool_config in build_config.items():
            if self._check_tool_signatures(project_path, tool_config):
                tools.append(tool_name.title())

        return tools

    def _detect_mobile_frameworks(self, project_path: Path) -> List[str]:
        """Detect mobile frameworks from frontend_frameworks config"""
        mobile_frameworks = []
        frontend_config = self.language_patterns.get('frontend_frameworks', {})

        mobile_framework_names = ['react_native', 'xamarin']

        for framework_name in mobile_framework_names:
            if framework_name in frontend_config:
                framework_config = frontend_config[framework_name]
                if self._check_tool_signatures(project_path, framework_config):
                    mobile_frameworks.append(framework_name.replace('_', ' ').title())

        return mobile_frameworks

    def _detect_testing_frameworks(self, project_path: Path, languages: List[str]) -> List[str]:
        """Detect testing frameworks (Selenium, Playwright) for detected languages"""
        frameworks = []
        testing_config = self.language_patterns.get('testing', {})

        multi_lang_frameworks = ['selenium', 'playwright']

        for framework_name in multi_lang_frameworks:
            if framework_name not in testing_config:
                continue

            framework_config = testing_config[framework_name]

            # Check signatures for detected languages
            for lang in languages:
                if lang in framework_config:
                    lang_signatures = framework_config[lang]
                    if self._check_framework_signatures(project_path, lang_signatures):
                        frameworks.append(framework_name.title())
                        break

        return frameworks

    def _check_tool_signatures(self, project_path: Path, tool_config: Dict) -> bool:
        """Check if tool signature patterns are present"""
        signature_patterns = tool_config.get('signature_patterns', [])

        for signature in signature_patterns:
            pattern = signature.get('pattern')
            locations = signature.get('location', ['**/*'])
            weight = signature.get('weight', 1.0)

            if self._check_pattern(project_path, pattern, locations):
                return True

        return False

    def _disambiguate_ruby_chef(self, project_path: Path, file_path: Path) -> str:
        """Determine if .rb file is Ruby or Chef"""
        # Check for Chef metadata.rb
        if (project_path / "metadata.rb").exists():
            return "chef"

        # Check for Chef-specific keywords in file
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if re.search(r'\b(cookbook_file|template|package|service)\s+["\']', content):
                    return "chef"
        except Exception:
            pass

        return "ruby"

    def _disambiguate_yaml_ansible(self, project_path: Path, file_path: Path) -> str:
        """Determine if .yml file is Ansible"""
        # Check for ansible.cfg
        if (project_path / "ansible.cfg").exists():
            return "ansible"

        # Check for Ansible keywords
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if re.search(r'^---\s*\n.*(hosts|tasks|roles|plays):', content, re.MULTILINE):
                    return "ansible"
        except Exception:
            pass

        return "yaml"

    def _categorize_framework(self, framework_name: str, lang_name: str) -> Optional[str]:
        """Categorize framework into backend/frontend/etc"""
        frontend_frameworks = ['react', 'vue', 'angular', 'nextjs', 'svelte']
        backend_frameworks = ['django', 'flask', 'fastapi', 'spring', 'aspnet', 'express', 'nestjs', 'gin', 'rails', 'laravel', 'symfony', 'actix', 'ktor', 'tokio', 'async_std']
        mobile_frameworks = ['react_native', 'flutter', 'swiftui', 'uikit', 'android', 'jetpack_compose', 'xamarin']

        if framework_name.lower() in frontend_frameworks:
            return 'frontend'
        elif framework_name.lower() in backend_frameworks:
            return 'backend'
        elif framework_name.lower() in mobile_frameworks:
            return 'mobile'

        return None

    def _check_framework_signatures(self, project_path: Path, signatures: List[Dict]) -> bool:
        """Check if framework signatures are present"""
        for signature in signatures:
            pattern = signature['pattern']
            locations = signature.get('location', ['**/*'])

            if self._check_pattern(project_path, pattern, locations):
                return True

        return False

    def _check_pattern(self, project_path: Path, pattern: str, locations: List[str]) -> bool:
        """Check if pattern exists in specified locations"""
        for location in locations:
            for file in project_path.glob(location):
                if not file.is_file():
                    continue

                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if re.search(pattern, content):
                            logger.debug(f"Pattern '{pattern}' found in {file.name}")
                            return True
                except Exception as e:
                    logger.debug(f"Error checking {file}: {e}")
                    continue

        return False

    def _detect_devops(self, project_path: Path) -> List[str]:
        """Detect DevOps tools (IaC, CI/CD, Docker)"""
        devops_tools = []

        # Docker
        if (project_path / "Dockerfile").exists():
            devops_tools.append("Docker")

        # Docker Compose
        if (project_path / "docker-compose.yml").exists() or (project_path / "docker-compose.yaml").exists():
            devops_tools.append("Docker Compose")

        # Terraform
        if list(project_path.glob("**/*.tf")):
            devops_tools.append("Terraform")

        # Kubernetes
        if list(project_path.glob("**/*.{yml,yaml}")):
            for file in project_path.glob("**/*.{yml,yaml}"):
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        if re.search(r'apiVersion:|kind:\s+(Deployment|Service|Pod)', content):
                            devops_tools.append("Kubernetes")
                            break
                except Exception:
                    continue

        # GitHub Actions
        if (project_path / ".github" / "workflows").exists():
            devops_tools.append("GitHub Actions")

        # GitLab CI
        if (project_path / ".gitlab-ci.yml").exists():
            devops_tools.append("GitLab CI")

        return devops_tools

    def _lsp_analysis(self, project_path: Path, language_stats: Dict) -> Dict:
        """
        Deep analysis using LSP plugins.

        Note: This is a placeholder for LSP integration.
        Actual LSP plugin calls would require claude-plugins-official installation.
        """
        lsp_results = {}

        for lang_name in language_stats.keys():
            lang_config = self.language_patterns['languages'].get(lang_name, {})
            lsp_plugin = lang_config.get('lsp_plugin')

            if not lsp_plugin:
                continue

            # Placeholder for LSP analysis
            # In production, would call: from claude_plugins.lsp import PyrightLSP
            lsp_results[lang_name] = {
                "plugin": lsp_plugin,
                "status": "not_implemented",
                "message": f"LSP analysis with {lsp_plugin} requires claude-plugins-official"
            }

        return lsp_results

    def _calculate_confidence(self, language_stats: Dict, frameworks: Dict) -> float:
        """
        Calculate overall detection confidence.

        Realistic thresholds:
        - 1 primary language = base 0.5 confidence
        - 1+ framework = +0.2
        - 2+ frameworks = +0.3
        - Testing/DevOps tools = +0.1 each
        """
        if not language_stats:
            return 0.0

        # Base confidence from primary language (50%)
        lang_confidence = 0.5

        # Multiple languages bonus (up to +0.2)
        if len(language_stats) >= 2:
            lang_confidence += 0.2
        elif len(language_stats) >= 3:
            lang_confidence = 1.0

        # Framework detection bonus (up to +0.3)
        framework_count = sum(len(f) for f in frameworks.values())
        if framework_count >= 1:
            lang_confidence += 0.2
        if framework_count >= 2:
            lang_confidence += 0.1

        # Testing/DevOps bonus (up to +0.1)
        if frameworks.get('testing'):
            lang_confidence += 0.05
        if any(len(frameworks.get(k, [])) > 0 for k in ['database', 'cache', 'messaging']):
            lang_confidence += 0.05

        return round(min(lang_confidence, 1.0), 3)


def main():
    """Test language detector"""
    import argparse

    parser = argparse.ArgumentParser(description="Detect languages and frameworks in project")
    parser.add_argument("project_path", help="Path to project")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--output", help="Output file (JSON)")

    args = parser.parse_args()

    # Load config
    if args.config:
        config_path = Path(args.config)
    else:
        config_path = Path(__file__).parent.parent / "config" / "import_config.yml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Run detection
    detector = LanguageDetector(config)
    result = detector.detect(Path(args.project_path))

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
