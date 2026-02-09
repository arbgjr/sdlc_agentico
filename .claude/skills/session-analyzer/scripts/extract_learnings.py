#!/usr/bin/env python3
"""
Session Learnings Extractor
============================

Analyzes Claude Code session transcripts to extract:
- Decisions made
- Blockers encountered and resolutions
- Learnings and patterns
- Artifacts created
- Next steps

Integrates with PreCompact hook to automatically analyze sessions
before conversation compaction.

Usage:
    # Analyze most recent session
    python3 extract_learnings.py

    # Analyze specific session
    python3 extract_learnings.py --session-id <uuid>

    # Persist results
    python3 extract_learnings.py --persist

    # Process pending analysis markers
    python3 extract_learnings.py --process-markers
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class SessionAnalyzer:
    """Analyzes Claude Code session transcripts."""

    # Keywords for pattern detection
    DECISION_KEYWORDS = [
        "decidi", "escolhi", "vou usar", "optei por",
        "a melhor opcao", "faz mais sentido", "vamos com",
        "prefiro", "recomendo", "sugiro", "decided", "chose",
        "will use", "going with", "recommend"
    ]

    BLOCKER_KEYWORDS = [
        "erro", "falhou", "problema", "nao funcionou",
        "bug", "issue", "bloqueado", "travado",
        "nao consegui", "impossivel", "error", "failed",
        "problem", "doesn't work", "blocked", "stuck"
    ]

    RESOLUTION_KEYWORDS = [
        "resolvido", "funcionou", "corrigido", "sucesso",
        "consegui", "pronto", "finalizado", "ok",
        "resolved", "worked", "fixed", "success", "done"
    ]

    LEARNING_KEYWORDS = [
        "aprendi", "descobri", "percebi", "entendi",
        "importante notar", "lembre-se", "dica",
        "evite", "sempre", "nunca", "learned", "discovered",
        "important", "note", "tip", "avoid", "always", "never"
    ]

    def __init__(self, project_path: Path):
        """Initialize analyzer with project path."""
        self.project_path = project_path
        self.output_dir = project_path / ".project" / "sessions"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def find_session_file(self, session_id: Optional[str] = None) -> Optional[Path]:
        """Find session transcript file."""
        # Claude Code stores sessions in ~/.claude/projects/
        claude_dir = Path.home() / ".claude" / "projects"

        # Encode project path (replace / with -)
        encoded_path = str(self.project_path.absolute()).replace("/", "-")

        session_dir = claude_dir / encoded_path

        if not session_dir.exists():
            print(f"❌ Session directory not found: {session_dir}", file=sys.stderr)
            return None

        # Find session file
        if session_id:
            session_file = session_dir / f"{session_id}.jsonl"
            if session_file.exists():
                return session_file
        else:
            # Get most recent session
            sessions = sorted(
                session_dir.glob("*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if sessions:
                return sessions[0]

        return None

    def parse_session(self, session_file: Path) -> Dict[str, Any]:
        """Parse session transcript JSONL file."""
        events = []

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        events.append(event)
                    except json.JSONDecodeError:
                        continue

            return self._analyze_events(events)

        except Exception as e:
            print(f"❌ Error parsing session: {e}", file=sys.stderr)
            return {}

    def _analyze_events(self, events: List[Dict]) -> Dict[str, Any]:
        """Analyze events to extract patterns."""
        analysis = {
            "summary": {
                "total_events": len(events),
                "user_messages": 0,
                "assistant_messages": 0,
                "tool_uses": 0,
                "thinking_blocks": 0
            },
            "decisions": [],
            "blockers": [],
            "learnings": [],
            "artifacts_created": [],
            "tools_used": set()
        }

        current_blocker = None

        for event in events:
            event_type = event.get("type", "")

            if event_type == "user":
                analysis["summary"]["user_messages"] += 1

            elif event_type == "assistant":
                analysis["summary"]["assistant_messages"] += 1
                content = event.get("content", "")

                # Detect decisions
                for keyword in self.DECISION_KEYWORDS:
                    if keyword.lower() in content.lower():
                        analysis["decisions"].append({
                            "description": self._extract_sentence(content, keyword),
                            "confidence": "medium"
                        })

                # Detect learnings
                for keyword in self.LEARNING_KEYWORDS:
                    if keyword.lower() in content.lower():
                        analysis["learnings"].append({
                            "description": self._extract_sentence(content, keyword),
                            "type": "pattern"
                        })

            elif event_type == "tool_use":
                analysis["summary"]["tool_uses"] += 1
                tool_name = event.get("name", "")
                analysis["tools_used"].add(tool_name)

                # Track file operations
                if tool_name in ["Write", "Edit"]:
                    params = event.get("input", {})
                    file_path = params.get("file_path", "")
                    if file_path:
                        analysis["artifacts_created"].append({
                            "path": file_path,
                            "type": tool_name.lower()
                        })

            elif event_type == "tool_result":
                # Detect errors (potential blockers)
                output = event.get("content", "")
                if any(kw in output.lower() for kw in ["error", "failed", "exception"]):
                    if current_blocker is None:
                        current_blocker = {
                            "description": self._extract_error(output),
                            "resolution": None
                        }

            elif event_type == "thinking":
                analysis["summary"]["thinking_blocks"] += 1

        # Convert sets to lists for JSON serialization
        analysis["tools_used"] = list(analysis["tools_used"])

        return analysis

    def _extract_sentence(self, text: str, keyword: str) -> str:
        """Extract sentence containing keyword."""
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            if keyword.lower() in sentence.lower():
                return sentence.strip()[:200]  # Limit length
        return text[:200]

    def _extract_error(self, text: str) -> str:
        """Extract error message."""
        lines = text.split('\n')
        for line in lines:
            if any(kw in line.lower() for kw in ["error", "exception", "failed"]):
                return line.strip()[:200]
        return text[:200]

    def save_analysis(self, session_file: Path, analysis: Dict[str, Any]) -> Path:
        """Save analysis to output file."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        session_short = session_file.stem[:8]
        output_file = self.output_dir / f"session-{timestamp}-{session_short}.yml"

        output = {
            "session_analysis": {
                "id": session_file.stem,
                "analyzed_at": datetime.now().isoformat(),
                "source_file": str(session_file),
                "project_path": str(self.project_path),
                **analysis
            }
        }

        # Convert to YAML-like format (simple dict dump for now)
        with open(output_file, 'w', encoding='utf-8') as f:
            self._write_yaml(f, output, indent=0)

        print(f"✅ Analysis saved to: {output_file}", file=sys.stderr)
        return output_file

    def _write_yaml(self, f, data: Any, indent: int = 0):
        """Simple YAML writer."""
        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    f.write(f"{prefix}{key}:\n")
                    self._write_yaml(f, value, indent + 1)
                else:
                    f.write(f"{prefix}{key}: {self._format_value(value)}\n")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    f.write(f"{prefix}-\n")
                    self._write_yaml(f, item, indent + 1)
                else:
                    f.write(f"{prefix}- {self._format_value(item)}\n")

    def _format_value(self, value: Any) -> str:
        """Format value for YAML."""
        if isinstance(value, str):
            if '\n' in value or any(c in value for c in [':', '#', '[', ']']):
                return f'"{value}"'
            return value
        return str(value)


def process_pending_markers(project_path: Path) -> int:
    """Process pending analysis markers created by PreCompact hook."""
    marker_dir = project_path / ".agentic_sdlc" / "sessions" / "pending-analysis"

    if not marker_dir.exists():
        return 0

    markers = list(marker_dir.glob("precompact-*.marker"))
    processed = 0

    analyzer = SessionAnalyzer(project_path)

    for marker_file in markers:
        try:
            with open(marker_file, 'r') as f:
                marker_data = json.load(f)

            transcript_path = Path(marker_data.get("transcript_path", ""))

            if not transcript_path.exists():
                print(f"⚠️  Transcript not found: {transcript_path}", file=sys.stderr)
                marker_file.unlink()  # Remove invalid marker
                continue

            print(f"📊 Processing: {transcript_path.name}", file=sys.stderr)

            # Parse and analyze session
            analysis = analyzer.parse_session(transcript_path)

            # Save analysis
            analyzer.save_analysis(transcript_path, analysis)

            # Remove marker after successful processing
            marker_file.unlink()
            processed += 1

        except Exception as e:
            print(f"❌ Error processing marker {marker_file.name}: {e}", file=sys.stderr)

    return processed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract learnings from Claude Code sessions")
    parser.add_argument("--session-id", help="Specific session UUID to analyze")
    parser.add_argument("--persist", action="store_true", help="Persist analysis results")
    parser.add_argument("--project", help="Project path (default: current directory)")
    parser.add_argument("--process-markers", action="store_true", help="Process pending PreCompact markers")

    args = parser.parse_args()

    # Determine project path
    if args.project:
        project_path = Path(args.project).absolute()
    else:
        project_path = Path.cwd()

    # Process pending markers if requested
    if args.process_markers:
        processed = process_pending_markers(project_path)
        print(f"✅ Processed {processed} pending analysis markers", file=sys.stderr)
        return 0

    # Create analyzer
    analyzer = SessionAnalyzer(project_path)

    # Find session file
    session_file = analyzer.find_session_file(args.session_id)

    if not session_file:
        print("❌ No session file found", file=sys.stderr)
        return 1

    print(f"📊 Analyzing session: {session_file.name}", file=sys.stderr)

    # Parse session
    analysis = analyzer.parse_session(session_file)

    # Display summary
    print("\n" + "="*60, file=sys.stderr)
    print("SESSION ANALYSIS SUMMARY", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(f"\nTotal events: {analysis['summary']['total_events']}", file=sys.stderr)
    print(f"User messages: {analysis['summary']['user_messages']}", file=sys.stderr)
    print(f"Assistant messages: {analysis['summary']['assistant_messages']}", file=sys.stderr)
    print(f"Tool uses: {analysis['summary']['tool_uses']}", file=sys.stderr)
    print(f"\nDecisions identified: {len(analysis['decisions'])}", file=sys.stderr)
    print(f"Learnings identified: {len(analysis['learnings'])}", file=sys.stderr)
    print(f"Artifacts created: {len(analysis['artifacts_created'])}", file=sys.stderr)
    print(f"\nTools used: {', '.join(analysis['tools_used'])}", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)

    # Persist if requested
    if args.persist:
        output_file = analyzer.save_analysis(session_file, analysis)
        print(f"💾 Analysis persisted to: {output_file}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
