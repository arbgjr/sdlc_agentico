#!/usr/bin/env python3
"""
Script: Publish ADR to GitHub Wiki

Publishes Architecture Decision Records (ADRs) to GitHub Wiki.
Converts YAML ADRs to Markdown format.

Usage:
    python3 publish_adr.py path/to/adr.yml    # Publish specific ADR
    python3 publish_adr.py --all              # Publish all ADRs
"""

import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Tuple, Optional, List
import yaml

# Add lib path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent.parent.parent / "lib" / "python"
sys.path.insert(0, str(LIB_DIR))

try:
    from sdlc_logging import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

    class FallbackLogger:
        def __init__(self, name):
            self.logger = logging.getLogger(name)

        def info(self, msg, **kwargs):
            print(f"[INFO] {msg}")

        def error(self, msg, **kwargs):
            print(f"[ERROR] {msg}", file=sys.stderr)

        def debug(self, msg, **kwargs):
            pass

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class ADRPublisher:
    """Publishes ADRs to GitHub Wiki."""

    # ADR search paths
    ADR_PATHS = [
        ".project/corpus/nodes/decisions/*.yml",
        ".project/corpus/nodes/decisions/*.yaml",
        ".agentic_sdlc/projects/*/decisions/*.yml",
        ".agentic_sdlc/projects/*/decisions/*.yaml",
    ]

    def __init__(self):
        self.logger = get_logger(__name__, skill="github-wiki")
        self.repo_root = Path.cwd()
        self.wiki_dir: Optional[Path] = None

    def run_command(
        self, cmd: List[str], cwd: Optional[Path] = None
    ) -> Tuple[int, str, str]:
        """Run command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or self.repo_root,
                check=False,
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return 1, "", str(e)

    def get_repo_name(self) -> Optional[str]:
        """Get GitHub repository name."""
        # Check if remote exists
        code, _, _ = self.run_command(["git", "remote", "get-url", "origin"])
        if code != 0:
            self.logger.error("Not in a GitHub repository (no 'origin' remote)")
            print("Configure first: git remote add origin <url>", file=sys.stderr)
            return None

        # Get repo via gh CLI
        code, stdout, _ = self.run_command(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]
        )
        if code != 0 or not stdout:
            self.logger.error("Could not detect GitHub repository via gh CLI")
            print("Check:", file=sys.stderr)
            print("  - gh auth status", file=sys.stderr)
            print("  - git remote -v", file=sys.stderr)
            return None

        return stdout

    def clone_wiki(self, repo: str) -> bool:
        """Clone GitHub wiki to temporary directory."""
        self.wiki_dir = Path(tempfile.mkdtemp())

        wiki_url = f"https://github.com/{repo}.wiki.git"
        print(f"Cloning wiki...")

        code, _, stderr = self.run_command(
            ["git", "clone", wiki_url, str(self.wiki_dir)]
        )

        if code != 0:
            self.logger.error(f"Failed to clone wiki: {stderr}")
            return False

        # Create ADRs directory
        (self.wiki_dir / "ADRs").mkdir(exist_ok=True)

        return True

    def convert_adr(self, adr_file: Path) -> bool:
        """
        Convert YAML ADR to Markdown.

        Args:
            adr_file: Path to ADR YAML file

        Returns:
            True if successful
        """
        if not adr_file.exists():
            self.logger.error(f"File not found: {adr_file}")
            return False

        basename = adr_file.stem
        output_file = self.wiki_dir / "ADRs" / f"{basename}.md"

        try:
            with open(adr_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            adr_id = data.get("id", basename)
            title = data.get("title", "Untitled")
            status = data.get("status", "Proposed")
            context = data.get("context", "")
            decision = data.get("decision", "")
            consequences = data.get("consequences", {})

            # Build markdown
            md = []
            md.append(f"# {adr_id}: {title}")
            md.append("")
            md.append(f"**Status:** {status}")
            md.append("")
            md.append("## Context")
            md.append(context)
            md.append("")
            md.append("## Decision")
            md.append(decision)
            md.append("")
            md.append("## Consequences")
            if isinstance(consequences, dict):
                for key, items in consequences.items():
                    md.append(f"### {key.title()}")
                    for item in (items or []):
                        md.append(f"- {item}")
            md.append("")
            md.append("---")
            md.append("*Generated by SDLC Agentico*")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(md))

            print(f"[OK] Converted: {basename}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to convert {adr_file}: {e}")
            return False

    def find_all_adrs(self) -> List[Path]:
        """Find all ADR files in standard locations."""
        adrs = []
        for pattern in self.ADR_PATHS:
            adrs.extend(self.repo_root.glob(pattern))
        return sorted(set(adrs))

    def commit_and_push(self, repo: str) -> bool:
        """Commit and push changes to wiki."""
        # Check for changes
        code, _, _ = self.run_command(
            ["git", "diff", "--quiet"],
            cwd=self.wiki_dir
        )
        has_unstaged = code != 0

        code, _, _ = self.run_command(
            ["git", "diff", "--staged", "--quiet"],
            cwd=self.wiki_dir
        )
        has_staged = code != 0

        if not has_unstaged and not has_staged:
            print("No changes to publish")
            return True

        # Stage changes
        code, _, _ = self.run_command(["git", "add", "."], cwd=self.wiki_dir)
        if code != 0:
            return False

        # Commit
        from datetime import datetime
        commit_msg = f"docs: publish ADR {datetime.now().strftime('%Y-%m-%d')}"
        code, _, stderr = self.run_command(
            ["git", "commit", "-m", commit_msg],
            cwd=self.wiki_dir
        )
        if code != 0:
            self.logger.error(f"Failed to commit: {stderr}")
            return False

        # Push
        code, _, stderr = self.run_command(["git", "push"], cwd=self.wiki_dir)
        if code == 0:
            print(f"[OK] ADR(s) published to wiki")
            print(f"URL: https://github.com/{repo}/wiki")
            return True
        else:
            self.logger.error(f"Failed to push: {stderr}")
            return False

    def cleanup(self):
        """Clean up temporary wiki directory."""
        if self.wiki_dir and self.wiki_dir.exists():
            shutil.rmtree(self.wiki_dir)

    def execute(self, adr_path: Optional[str] = None, publish_all: bool = False) -> int:
        """
        Execute ADR publishing.

        Args:
            adr_path: Path to specific ADR file
            publish_all: If True, publish all ADRs

        Returns:
            0 on success, 1 on failure
        """
        try:
            # Get repository name
            repo = self.get_repo_name()
            if not repo:
                return 1

            # Clone wiki
            if not self.clone_wiki(repo):
                return 1

            # Process ADRs
            if publish_all:
                print("Publishing all ADRs...")
                adrs = self.find_all_adrs()
                if not adrs:
                    print("No ADRs found")
                    return 0

                for adr in adrs:
                    self.convert_adr(adr)
            else:
                if not adr_path:
                    print("Usage: publish_adr.py <adr-path> | --all", file=sys.stderr)
                    return 1

                adr_file = Path(adr_path)
                if not self.convert_adr(adr_file):
                    return 1

            # Commit and push
            if not self.commit_and_push(repo):
                return 1

            return 0

        finally:
            self.cleanup()


def main() -> int:
    """Main entry point for publish_adr script."""
    if len(sys.argv) < 2:
        print("Usage: python3 publish_adr.py <adr-path> | --all", file=sys.stderr)
        return 1

    publish_all = sys.argv[1] == "--all"
    adr_path = None if publish_all else sys.argv[1]

    publisher = ADRPublisher()

    try:
        return publisher.execute(adr_path, publish_all)
    except Exception as e:
        publisher.logger.error(f"Publishing failed: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
