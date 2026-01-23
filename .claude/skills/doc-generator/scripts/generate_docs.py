#!/usr/bin/env python3
"""
Documentation generator for SDLC Agêntico.

Analyzes project structure and generates CLAUDE.md and README.md
with SDLC Agêntico signature.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="doc-generator", phase=7)

# Signature to add at the end of generated files
SIGNATURE = "\n---\n\n🤖 *Generated with [SDLC Agêntico](https://github.com/arbgjr/sdlc_agentico) by [@arbgjr](https://github.com/arbgjr)*\n"


def analyze_project() -> Dict:
    """
    Analyze current project structure to extract documentation metadata.

    Returns:
        dict: Project metadata including name, description, structure, etc.
    """
    logger.info("Analyzing project structure")

    project_root = Path.cwd()
    project_name = project_root.name

    metadata = {
        "project_name": project_name,
        "project_root": str(project_root),
        "languages": detect_languages(project_root),
        "frameworks": detect_frameworks(project_root),
        "structure": analyze_directory_structure(project_root),
        "has_tests": has_tests(project_root),
        "has_docker": (project_root / "Dockerfile").exists(),
        "has_ci": (project_root / ".github/workflows").exists(),
    }

    logger.info("Project analysis complete", extra=metadata)
    return metadata


def detect_languages(root: Path) -> List[str]:
    """Detect programming languages used in project."""
    languages = set()

    language_patterns = {
        "Python": ["*.py"],
        "JavaScript": ["*.js", "*.jsx"],
        "TypeScript": ["*.ts", "*.tsx"],
        "Java": ["*.java"],
        "C#": ["*.cs"],
        "Go": ["*.go"],
        "Rust": ["*.rs"],
        "Ruby": ["*.rb"],
    }

    for lang, patterns in language_patterns.items():
        for pattern in patterns:
            if list(root.rglob(pattern)):
                languages.add(lang)
                break

    return sorted(languages)


def detect_frameworks(root: Path) -> List[str]:
    """Detect frameworks based on project files."""
    frameworks = []

    # Python frameworks
    if (root / "requirements.txt").exists():
        content = (root / "requirements.txt").read_text()
        if "django" in content.lower():
            frameworks.append("Django")
        if "flask" in content.lower():
            frameworks.append("Flask")
        if "fastapi" in content.lower():
            frameworks.append("FastAPI")

    # JavaScript/TypeScript frameworks
    if (root / "package.json").exists():
        try:
            pkg = json.loads((root / "package.json").read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

            if "react" in deps:
                frameworks.append("React")
            if "next" in deps:
                frameworks.append("Next.js")
            if "vue" in deps:
                frameworks.append("Vue.js")
            if "angular" in deps or "@angular/core" in deps:
                frameworks.append("Angular")
            if "express" in deps:
                frameworks.append("Express")
        except:
            pass

    # .NET
    if list(root.rglob("*.csproj")):
        frameworks.append(".NET")

    # Java
    if (root / "pom.xml").exists():
        frameworks.append("Maven/Spring")
    if (root / "build.gradle").exists():
        frameworks.append("Gradle")

    return frameworks


def analyze_directory_structure(root: Path, max_depth: int = 3) -> str:
    """
    Generate directory tree structure.

    Args:
        root: Project root directory
        max_depth: Maximum depth to traverse

    Returns:
        str: Formatted directory tree
    """
    lines = []

    def walk_dir(path: Path, prefix: str = "", depth: int = 0):
        if depth >= max_depth:
            return

        # Skip common excluded directories
        excluded = {
            ".git", "__pycache__", "node_modules", ".venv", "venv",
            "dist", "build", ".pytest_cache", ".mypy_cache"
        }

        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            for i, item in enumerate(items):
                if item.name in excluded or item.name.startswith("."):
                    continue

                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                lines.append(f"{prefix}{current_prefix}{item.name}")

                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    walk_dir(item, prefix + extension, depth + 1)
        except PermissionError:
            pass

    lines.append(root.name + "/")
    walk_dir(root)

    return "\n".join(lines)


def has_tests(root: Path) -> bool:
    """Check if project has tests."""
    test_patterns = ["test_*.py", "*_test.py", "*.test.js", "*.spec.js"]
    test_dirs = ["tests", "test", "__tests__", "spec"]

    # Check for test files
    for pattern in test_patterns:
        if list(root.rglob(pattern)):
            return True

    # Check for test directories
    for test_dir in test_dirs:
        if (root / test_dir).exists():
            return True

    return False


def generate_claude_md(metadata: Dict) -> str:
    """
    Generate CLAUDE.md content from project metadata.

    Args:
        metadata: Project metadata dict

    Returns:
        str: Generated CLAUDE.md content
    """
    logger.info("Generating CLAUDE.md")

    template_path = Path(__file__).parent.parent / "templates/CLAUDE.md.template"
    template = template_path.read_text()

    # Replace placeholders
    replacements = {
        "{{project_name}}": metadata["project_name"],
        "{{project_description}}": f"A {', '.join(metadata['languages'])} project",
        "{{technologies}}": format_technologies(metadata),
        "{{components}}": "- Main application\n- Supporting modules",
        "{{architecture_description}}": generate_architecture_description(metadata),
        "{{directory_structure}}": metadata["structure"],
        "{{prerequisites}}": generate_prerequisites(metadata),
        "{{installation_commands}}": generate_installation_commands(metadata),
        "{{configuration_instructions}}": generate_configuration(metadata),
        "{{run_commands}}": generate_run_commands(metadata),
        "{{test_commands}}": generate_test_commands(metadata),
        "{{build_commands}}": generate_build_commands(metadata),
        "{{file_organization}}": "Follow language-specific conventions",
        "{{naming_conventions}}": "- Files: lowercase with underscores (Python) or camelCase (JS/TS)\n- Classes: PascalCase\n- Functions: snake_case (Python) or camelCase (JS/TS)",
        "{{code_style}}": generate_code_style(metadata),
        "{{testing_strategy}}": generate_testing_strategy(metadata),
        "{{deployment_instructions}}": generate_deployment(metadata),
        "{{common_tasks}}": "- Development: Follow standard workflow\n- Testing: Run test suite before commits",
        "{{troubleshooting_tips}}": "Check logs and error messages for debugging",
    }

    content = template
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    return content


def generate_readme_md(metadata: Dict) -> str:
    """
    Generate README.md content from project metadata.

    Args:
        metadata: Project metadata dict

    Returns:
        str: Generated README.md content
    """
    logger.info("Generating README.md")

    template_path = Path(__file__).parent.parent / "templates/README.md.template"
    template = template_path.read_text()

    replacements = {
        "{{project_name}}": metadata["project_name"],
        "{{project_tagline}}": f"A modern {', '.join(metadata['languages'])} application",
        "{{project_overview}}": f"This project uses {', '.join(metadata['frameworks']) if metadata['frameworks'] else ', '.join(metadata['languages'])}.",
        "{{features_list}}": "- Feature 1\n- Feature 2\n- Feature 3",
        "{{tech_stack}}": format_tech_stack(metadata),
        "{{prerequisites}}": generate_prerequisites(metadata),
        "{{installation_steps}}": generate_installation_commands(metadata),
        "{{configuration_steps}}": "Configure environment variables as needed.",
        "{{run_steps}}": generate_run_commands(metadata),
        "{{usage_examples}}": "See documentation for usage examples.",
        "{{api_documentation}}": "API documentation available in `/docs` directory.",
        "{{architecture_diagram}}": "",
        "{{architecture_description}}": generate_architecture_description(metadata),
        "{{project_structure}}": metadata["structure"],
        "{{test_commands}}": generate_test_commands(metadata),
        "{{code_style_guide}}": "Follow standard code style for " + ", ".join(metadata["languages"]),
        "{{deployment_guide}}": generate_deployment(metadata),
        "{{contributing_guidelines}}": "Contributions welcome! Please open an issue or PR.",
        "{{license_info}}": "See LICENSE file for details.",
        "{{support_info}}": "For support, please open an issue.",
        "{{changelog_link}}": "See CHANGELOG.md for version history.",
    }

    content = template
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    return content


def format_technologies(metadata: Dict) -> str:
    """Format technologies list."""
    techs = []
    if metadata["languages"]:
        techs.append(f"- **Languages**: {', '.join(metadata['languages'])}")
    if metadata["frameworks"]:
        techs.append(f"- **Frameworks**: {', '.join(metadata['frameworks'])}")
    return "\n".join(techs) if techs else "- To be determined"


def format_tech_stack(metadata: Dict) -> str:
    """Format tech stack markdown."""
    stack = []
    for lang in metadata["languages"]:
        stack.append(f"- **{lang}**")
    for fw in metadata["frameworks"]:
        stack.append(f"- **{fw}**")
    return "\n".join(stack) if stack else "- To be determined"


def generate_architecture_description(metadata: Dict) -> str:
    """Generate architecture description."""
    if "Python" in metadata["languages"]:
        return "Standard Python application structure with modular design."
    elif "JavaScript" in metadata["languages"] or "TypeScript" in metadata["languages"]:
        return "Modern JavaScript/TypeScript application following best practices."
    return "Standard application architecture."


def generate_prerequisites(metadata: Dict) -> str:
    """Generate prerequisites list."""
    prereqs = []
    if "Python" in metadata["languages"]:
        prereqs.append("- Python 3.9+")
    if "JavaScript" in metadata["languages"] or "TypeScript" in metadata["languages"]:
        prereqs.append("- Node.js 18+")
    if "Java" in metadata["languages"]:
        prereqs.append("- Java 11+")
    if metadata["has_docker"]:
        prereqs.append("- Docker")
    return "\n".join(prereqs) if prereqs else "- To be determined"


def generate_installation_commands(metadata: Dict) -> str:
    """Generate installation commands."""
    commands = []
    if "Python" in metadata["languages"]:
        commands.append("pip install -r requirements.txt")
    if "JavaScript" in metadata["languages"] or "TypeScript" in metadata["languages"]:
        commands.append("npm install")
    if "Java" in metadata["languages"]:
        commands.append("mvn install")
    return "\n".join(commands) if commands else "# Installation commands"


def generate_configuration(metadata: Dict) -> str:
    """Generate configuration instructions."""
    return "Copy `.env.example` to `.env` and configure environment variables."


def generate_run_commands(metadata: Dict) -> str:
    """Generate run commands."""
    if "Python" in metadata["languages"]:
        if "Django" in metadata["frameworks"]:
            return "python manage.py runserver"
        elif "Flask" in metadata["frameworks"] or "FastAPI" in metadata["frameworks"]:
            return "python main.py"
        return "python app.py"
    if "JavaScript" in metadata["languages"] or "TypeScript" in metadata["languages"]:
        return "npm start"
    return "# Run command"


def generate_test_commands(metadata: Dict) -> str:
    """Generate test commands."""
    if not metadata["has_tests"]:
        return "# No tests configured yet"

    if "Python" in metadata["languages"]:
        return "pytest"
    if "JavaScript" in metadata["languages"] or "TypeScript" in metadata["languages"]:
        return "npm test"
    return "# Test command"


def generate_build_commands(metadata: Dict) -> str:
    """Generate build commands."""
    if "JavaScript" in metadata["languages"] or "TypeScript" in metadata["languages"]:
        return "npm run build"
    if "Java" in metadata["languages"]:
        return "mvn package"
    return "# Build command"


def generate_code_style(metadata: Dict) -> str:
    """Generate code style guide."""
    if "Python" in metadata["languages"]:
        return "Follow PEP 8 style guide. Use `black` for formatting."
    if "JavaScript" in metadata["languages"] or "TypeScript" in metadata["languages"]:
        return "Follow Airbnb style guide. Use ESLint and Prettier."
    return "Follow language-specific style guides."


def generate_testing_strategy(metadata: Dict) -> str:
    """Generate testing strategy."""
    if metadata["has_tests"]:
        return "- Unit tests for all modules\n- Integration tests for critical paths\n- Run tests before commits"
    return "Tests should be added for all new features."


def generate_deployment(metadata: Dict) -> str:
    """Generate deployment instructions."""
    if metadata["has_docker"]:
        return "Deploy using Docker:\n\n```bash\ndocker build -t app .\ndocker run -p 8000:8000 app\n```"
    if metadata["has_ci"]:
        return "Automated deployment via GitHub Actions. See `.github/workflows/`."
    return "Deployment instructions to be added."


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate project documentation with SDLC Agêntico signature"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for generated files (default: current directory)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files"
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    claude_md = output_dir / "CLAUDE.md"
    readme_md = output_dir / "README.md"

    # Check if files exist
    if not args.force:
        if claude_md.exists() or readme_md.exists():
            logger.warning("Files already exist. Use --force to overwrite.")
            print("❌ Files already exist. Use --force to overwrite.")
            return 1

    try:
        # Analyze project
        metadata = analyze_project()

        # Generate CLAUDE.md
        claude_content = generate_claude_md(metadata)
        with open(claude_md, "w") as f:
            f.write(claude_content)
        logger.info(f"Generated {claude_md}")
        print(f"✅ Generated {claude_md}")

        # Generate README.md
        readme_content = generate_readme_md(metadata)
        with open(readme_md, "w") as f:
            f.write(readme_content)
        logger.info(f"Generated {readme_md}")
        print(f"✅ Generated {readme_md}")

        print(f"\n🤖 Documentation generated with SDLC Agêntico signature!")
        return 0

    except Exception as e:
        logger.error(f"Failed to generate documentation: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
