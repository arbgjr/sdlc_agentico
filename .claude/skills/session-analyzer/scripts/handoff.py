#!/usr/bin/env python3
"""
Session Handoff Summary Generator

Generates session handoff summaries for continuity between Claude Code sessions.
Adapted from claude-orchestrator for SDLC Agêntico.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import re

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parents[3] / "lib" / "python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="session-analyzer", phase=0)


class HandoffGenerator:
    """Generates session handoff summaries"""

    def __init__(self, sessions_dir: Optional[Path] = None):
        self.sessions_dir = sessions_dir or Path.home() / ".claude" / "projects"
        self.output_dir = Path(".agentic_sdlc") / "sessions"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "HandoffGenerator initialized",
            extra={
                "sessions_dir": str(self.sessions_dir),
                "output_dir": str(self.output_dir)
            }
        )

    def find_latest_session(self, project_path: Optional[Path] = None) -> Optional[Path]:
        """Find latest session file"""
        if project_path:
            # Encode project path
            import base64
            encoded = base64.urlsafe_b64encode(
                str(project_path.resolve()).encode()
            ).decode().rstrip("=")
            session_dir = self.sessions_dir / encoded
        else:
            # Find most recent directory
            dirs = [d for d in self.sessions_dir.iterdir() if d.is_dir()]
            if not dirs:
                logger.error("No session directories found")
                return None
            session_dir = max(dirs, key=lambda d: d.stat().st_mtime)

        # Find latest .jsonl file
        sessions = list(session_dir.glob("*.jsonl"))
        if not sessions:
            logger.error(f"No session files found in {session_dir}")
            return None

        latest = max(sessions, key=lambda f: f.stat().st_mtime)
        logger.info(f"Latest session: {latest}")
        return latest

    def parse_session(self, session_file: Path) -> Dict[str, Any]:
        """Parse session JSONL file"""
        with log_operation(f"parse_session:{session_file.name}", logger):
            messages = []
            with open(session_file, "r") as f:
                for line in f:
                    if line.strip():
                        messages.append(json.loads(line))

            logger.debug(f"Parsed {len(messages)} messages", extra={"file": session_file.name})
            return {"messages": messages, "file": session_file}

    def extract_completed_tasks(self, messages: List[Dict]) -> List[str]:
        """Extract completed tasks from session"""
        completed = []

        # Look for todo completions
        for msg in messages:
            content = msg.get("content", [])
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    if tool_name == "TodoWrite":
                        params = block.get("input", {})
                        todos = params.get("todos", [])
                        for todo in todos:
                            if todo.get("status") == "completed":
                                completed.append(todo["content"])

        # Look for commits
        for msg in messages:
            content = msg.get("content", [])
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    if tool_name == "Bash":
                        params = block.get("input", {})
                        cmd = params.get("command", "")
                        if "git commit" in cmd:
                            # Extract commit message
                            match = re.search(r'-m\s+["\']([^"\']+)["\']', cmd)
                            if match:
                                completed.append(f"Committed: {match.group(1)}")

        return list(set(completed))  # Remove duplicates

    def extract_pending_tasks(self, messages: List[Dict]) -> List[str]:
        """Extract pending tasks from session"""
        pending = []

        # Look for pending todos
        last_todos = None
        for msg in reversed(messages):
            content = msg.get("content", [])
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    if tool_name == "TodoWrite":
                        last_todos = block.get("input", {}).get("todos", [])
                        break
            if last_todos:
                break

        if last_todos:
            for todo in last_todos:
                if todo.get("status") == "pending":
                    pending.append(todo["content"])

        return pending

    def extract_context(self, messages: List[Dict]) -> Dict[str, Any]:
        """Extract context for next session"""
        context = {
            "phase": None,
            "decisions": [],
            "blockers": [],
            "files_modified": [],
            "tools_used": [],
            "notes": []
        }

        # Extract phase
        for msg in messages:
            content_str = json.dumps(msg)
            match = re.search(r'phase[:\s]+(\d+)', content_str.lower())
            if match:
                context["phase"] = int(match.group(1))
                break

        # Extract files modified
        for msg in messages:
            content = msg.get("content", [])
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    context["tools_used"].append(tool_name)

                    if tool_name in ["Write", "Edit"]:
                        params = block.get("input", {})
                        file_path = params.get("file_path")
                        if file_path:
                            context["files_modified"].append(file_path)

        # Remove duplicates
        context["files_modified"] = list(set(context["files_modified"]))
        context["tools_used"] = list(set(context["tools_used"]))

        return context

    def generate_markdown(
        self,
        completed: List[str],
        pending: List[str],
        context: Dict[str, Any],
        session_file: Path
    ) -> str:
        """Generate markdown summary"""
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        repo = Path.cwd().name

        md = f"# Session Summary: {date} - {repo}\n\n"

        # Metadata
        md += "## Session Metadata\n\n"
        md += f"- **Date**: {datetime.now(timezone.utc).isoformat()}\n"
        md += f"- **Session File**: `{session_file.name}`\n"
        md += f"- **Repository**: {repo}\n"
        if context["phase"] is not None:
            md += f"- **SDLC Phase**: {context['phase']}\n"
        md += "\n"

        # Completed
        md += "## Completed\n\n"
        if completed:
            for item in completed:
                md += f"- {item}\n"
        else:
            md += "- *(No completed tasks recorded)*\n"
        md += "\n"

        # Pending
        md += "## Pending\n\n"
        if pending:
            for item in pending:
                md += f"- {item}\n"
        else:
            md += "- *(No pending tasks)*\n"
        md += "\n"

        # Context for Next Session
        md += "## Context for Next Session\n\n"

        if context["phase"] is not None:
            md += f"**Current Phase**: Phase {context['phase']}\n\n"

        if context["files_modified"]:
            md += "**Files Modified**:\n"
            for file_path in sorted(context["files_modified"])[:10]:  # Limit to 10
                md += f"- `{file_path}`\n"
            md += "\n"

        if context["tools_used"]:
            md += "**Tools Used**: "
            md += ", ".join(sorted(set(context["tools_used"]))[:10])
            md += "\n\n"

        if context["decisions"]:
            md += "**Decisions Made**:\n"
            for decision in context["decisions"]:
                md += f"- {decision}\n"
            md += "\n"

        if context["blockers"]:
            md += "**Blockers**:\n"
            for blocker in context["blockers"]:
                md += f"- {blocker}\n"
            md += "\n"

        if context["notes"]:
            md += "**Notes**:\n"
            for note in context["notes"]:
                md += f"- {note}\n"
            md += "\n"

        md += "---\n\n"
        md += "*Generated by session-analyzer skill (v2.0)*\n"

        return md

    def generate(
        self,
        project_path: Optional[Path] = None,
        output_file: Optional[Path] = None
    ) -> Path:
        """Generate handoff summary"""
        with log_operation("generate_handoff", logger):
            # Find latest session
            session_file = self.find_latest_session(project_path)
            if not session_file:
                raise FileNotFoundError("No session file found")

            # Parse session
            session_data = self.parse_session(session_file)
            messages = session_data["messages"]

            # Extract information
            completed = self.extract_completed_tasks(messages)
            pending = self.extract_pending_tasks(messages)
            context = self.extract_context(messages)

            logger.info(
                "Extracted session data",
                extra={
                    "completed": len(completed),
                    "pending": len(pending),
                    "phase": context["phase"],
                    "files_modified": len(context["files_modified"])
                }
            )

            # Generate markdown
            markdown = self.generate_markdown(completed, pending, context, session_file)

            # Determine output file
            if output_file is None:
                date = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
                repo = Path.cwd().name
                output_file = self.output_dir / f"{date}-{repo}.md"

            # Write file
            with open(output_file, "w") as f:
                f.write(markdown)

            logger.info(
                "Handoff summary generated",
                extra={"output_file": str(output_file)}
            )

            return output_file


def main():
    parser = argparse.ArgumentParser(description="Session Handoff Summary Generator")
    parser.add_argument(
        "--project",
        type=Path,
        help="Project path (default: current directory)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file (default: auto-generated)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output"
    )

    args = parser.parse_args()

    generator = HandoffGenerator()

    try:
        output_file = generator.generate(
            project_path=args.project,
            output_file=args.output
        )

        if not args.quiet:
            print(f"Session handoff summary generated: {output_file}")
            print()
            print("=== Preview ===")
            print(output_file.read_text())

        sys.exit(0)

    except Exception as e:
        logger.error("Failed to generate handoff", extra={"error": str(e)})
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
