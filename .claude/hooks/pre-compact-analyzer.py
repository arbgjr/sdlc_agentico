#!/usr/bin/env python3
"""
Pre-Compact Hook for Session Analysis
======================================

Executes before automatic conversation compaction to extract learnings
from the session using the session-analyzer skill.

Hook Type: PreCompact
Trigger: auto (automatic compaction)
Decision: Cannot block (informational only)

Input JSON Schema:
{
    "session_id": "abc123",
    "transcript_path": "/path/to/session.jsonl",
    "cwd": "/working/directory",
    "hook_event_name": "PreCompact",
    "trigger": "auto" | "manual",
    "permission_mode": "default",
    "custom_instructions": ""
}
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime


def log_info(message: str) -> None:
    """Log information to stderr (visible to user)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ℹ️ PreCompact: {message}", file=sys.stderr)


def log_error(message: str) -> None:
    """Log error to stderr (visible to user)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ❌ PreCompact: {message}", file=sys.stderr)


def log_success(message: str) -> None:
    """Log success to stderr (visible to user)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ✅ PreCompact: {message}", file=sys.stderr)


def extract_learnings(transcript_path: str, cwd: str) -> bool:
    """
    Extract learnings from session using session-analyzer skill.

    Args:
        transcript_path: Path to session transcript file
        cwd: Current working directory

    Returns:
        True if successful, False otherwise
    """
    try:
        # Verify transcript exists
        if not Path(transcript_path).exists():
            log_error(f"Transcript not found: {transcript_path}")
            return False

        # Get session file size to decide if worth analyzing
        file_size = Path(transcript_path).stat().st_size

        # Skip if session is too small (< 10KB)
        if file_size < 10 * 1024:
            log_info(f"Session too small ({file_size} bytes), skipping analysis")
            return True

        log_info(f"Analyzing session ({file_size} bytes) before compaction...")

        # Invoke session-analyzer skill
        # Note: This creates a request for Claude to analyze the session
        # The actual analysis happens in the main conversation flow
        result = subprocess.run(
            [
                "python3",
                "-c",
                f"""
import json
import sys
from pathlib import Path

# Create a marker file for Claude to detect
marker_dir = Path("{cwd}") / ".agentic_sdlc" / "sessions" / "pending-analysis"
marker_dir.mkdir(parents=True, exist_ok=True)

marker_file = marker_dir / f"precompact-{{Path("{transcript_path}").stem}}.marker"
marker_data = {{
    "transcript_path": "{transcript_path}",
    "trigger": "pre-compact",
    "timestamp": "{{}}".format(__import__('datetime').datetime.now().isoformat()),
    "status": "pending"
}}

with open(marker_file, 'w') as f:
    json.dump(marker_data, f, indent=2)

print(f"Created analysis marker: {{marker_file}}", file=sys.stderr)
"""
            ],
            capture_output=True,
            text=True,
            cwd=cwd
        )

        if result.returncode == 0:
            log_success("Session marked for analysis")
            log_info("Use /session-analyzer to extract learnings manually if needed")
            return True
        else:
            log_error(f"Failed to mark session: {result.stderr}")
            return False

    except Exception as e:
        log_error(f"Exception during learning extraction: {e}")
        return False


def main() -> int:
    """Main hook execution."""
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())

        # Extract required fields
        trigger = input_data.get("trigger", "unknown")
        transcript_path = input_data.get("transcript_path", "")
        cwd = input_data.get("cwd", ".")
        session_id = input_data.get("session_id", "unknown")

        # Only process automatic compaction
        if trigger != "auto":
            log_info(f"Skipping manual compaction (trigger={trigger})")
            return 0

        log_info(f"Automatic compaction detected (session: {session_id})")

        # Extract learnings before compaction
        success = extract_learnings(transcript_path, cwd)

        if success:
            log_success("Session analysis prepared successfully")
        else:
            log_error("Session analysis preparation failed (non-blocking)")

        # Always return 0 (cannot block compaction)
        return 0

    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON input: {e}")
        return 0  # Non-blocking

    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return 0  # Non-blocking


if __name__ == "__main__":
    sys.exit(main())
