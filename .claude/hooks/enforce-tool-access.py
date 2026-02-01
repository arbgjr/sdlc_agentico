#!/usr/bin/env python3
"""
Tool Access Control Enforcement Hook

Validates tool usage against agent-specific allow/deny lists.
Prevents security risks by restricting tools per agent role.

Based on OpenClaw pattern: https://github.com/openclaw/openclaw/blob/main/AGENTS.md

Usage: Triggered by PreToolUse hook
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set


class ToolAccessViolation(Exception):
    """Raised when agent attempts to use denied tool"""
    pass


class ToolAccessEnforcer:
    """Enforces tool access control per agent"""

    # Tool groups (OpenClaw pattern)
    TOOL_GROUPS = {
        "fs": ["Read", "Write", "Edit", "Glob", "Grep", "NotebookEdit"],
        "runtime": ["Bash", "TaskOutput", "TaskStop"],
        "git": ["Bash"],  # Git ops via Bash
        "sessions": ["Task", "TaskCreate", "TaskUpdate", "TaskGet", "TaskList"],
        "ui": ["AskUserQuestion"],
        "web": ["WebFetch", "WebSearch"],
        "skills": ["Skill"],
        "planning": ["EnterPlanMode", "ExitPlanMode"],
    }

    def __init__(self):
        self.claude_dir = Path.home() / ".claude"
        self.agents_dir = Path(".claude/agents")
        self.current_agent = self._detect_current_agent()

    def _detect_current_agent(self) -> Optional[str]:
        """Detect which agent is currently active"""
        # Try to get from environment variable (set by orchestrator)
        agent = os.getenv("SDLC_CURRENT_AGENT")
        if agent:
            return agent

        # Fallback: check SDLC phase and map to likely agent
        phase = os.getenv("SDLC_PHASE")
        if phase:
            phase_agents = {
                "0": "intake-analyst",
                "1": "domain-researcher",
                "2": "requirements-analyst",
                "3": "system-architect",
                "4": "delivery-planner",
                "5": "code-author",
                "6": "qa-analyst",
                "7": "release-manager",
                "8": "incident-commander",
            }
            return phase_agents.get(phase)

        return None

    def _load_agent_config(self, agent_name: str) -> Dict:
        """Load agent frontmatter configuration"""
        agent_file = self.agents_dir / f"{agent_name}.md"
        if not agent_file.exists():
            return {}

        with open(agent_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract YAML frontmatter
        if not content.startswith("---"):
            return {}

        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}

        try:
            return yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            return {}

    def _expand_tool_groups(self, groups: List[str]) -> Set[str]:
        """Expand tool group references to actual tool names"""
        tools = set()
        for item in groups:
            if item.startswith("group:"):
                group_name = item.split(":", 1)[1]
                tools.update(self.TOOL_GROUPS.get(group_name, []))
            else:
                tools.add(item)
        return tools

    def check_tool_permission(self, tool_name: str) -> bool:
        """
        Check if current agent is allowed to use the given tool.

        Returns:
            True if allowed
            Raises ToolAccessViolation if denied
        """
        # If no agent detected, allow (backward compatibility)
        if not self.current_agent:
            return True

        # Load agent configuration
        config = self._load_agent_config(self.current_agent)

        # Get allowed and denied tools
        allowed_raw = config.get("allowed_tools", [])
        denied_raw = config.get("denied_tools", [])

        # If no restrictions configured, allow (backward compatibility)
        if not allowed_raw and not denied_raw:
            return True

        # Expand tool groups
        allowed = self._expand_tool_groups(allowed_raw)
        denied = self._expand_tool_groups(denied_raw)

        # Check deny list first (takes precedence)
        if tool_name in denied:
            raise ToolAccessViolation(
                f"Agent '{self.current_agent}' is DENIED access to tool '{tool_name}'\n"
                f"Denied tools: {sorted(denied)}\n"
                f"Reason: Security restriction - this agent should not perform this operation"
            )

        # If allow list is defined, check it
        if allowed and tool_name not in allowed:
            raise ToolAccessViolation(
                f"Agent '{self.current_agent}' is NOT ALLOWED to use tool '{tool_name}'\n"
                f"Allowed tools: {sorted(allowed)}\n"
                f"Reason: Tool not in whitelist for this agent role"
            )

        return True

    def get_tool_summary(self) -> Dict:
        """Get summary of tool restrictions for current agent"""
        if not self.current_agent:
            return {
                "agent": "unknown",
                "allowed": "all",
                "denied": "none",
                "mode": "unrestricted",
            }

        config = self._load_agent_config(self.current_agent)
        allowed_raw = config.get("allowed_tools", [])
        denied_raw = config.get("denied_tools", [])

        allowed = self._expand_tool_groups(allowed_raw)
        denied = self._expand_tool_groups(denied_raw)

        mode = "unrestricted"
        if allowed:
            mode = "whitelist"
        elif denied:
            mode = "blacklist"

        return {
            "agent": self.current_agent,
            "allowed": sorted(allowed) if allowed else "all",
            "denied": sorted(denied) if denied else "none",
            "mode": mode,
        }


def main():
    """
    PreToolUse hook entrypoint.

    Receives tool call info via stdin (JSON):
    {
        "tool": "Bash",
        "parameters": {...}
    }

    Returns:
    - Exit 0: Tool allowed
    - Exit 1: Tool denied (with error message)
    """
    # Read tool call info from stdin
    try:
        call_info = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        # No input or invalid JSON - allow by default
        sys.exit(0)

    tool_name = call_info.get("tool")
    if not tool_name:
        sys.exit(0)

    # Create enforcer and check permission
    enforcer = ToolAccessEnforcer()

    try:
        enforcer.check_tool_permission(tool_name)
        # Allowed - exit success
        sys.exit(0)
    except ToolAccessViolation as e:
        # Denied - print error and exit failure
        print(f"❌ TOOL ACCESS DENIED\n", file=sys.stderr)
        print(str(e), file=sys.stderr)
        print(f"\n💡 TIP: If this tool is needed, update agent frontmatter:", file=sys.stderr)
        print(f"   .claude/agents/{enforcer.current_agent}.md", file=sys.stderr)
        print(f"   allowed_tools: [{tool_name}]", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
