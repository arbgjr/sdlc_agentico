#!/usr/bin/env python3
"""
client_resolver.py - Cross-platform client profile resolution
Version: 3.0.3
Part of: Phase 1 - Foundation (Multi-Client Architecture)

Provides client detection, validation, and resource resolution.
Works on Linux, macOS, and Windows.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None


class ClientResolver:
    """Resolves and manages SDLC Agêntico client profiles."""

    def __init__(
        self,
        clients_dir: Optional[Path] = None,
        project_dir: Optional[Path] = None,
        default_client: str = "generic",
    ):
        self.clients_dir = clients_dir or Path("clients")
        self.project_dir = project_dir or Path(
            os.getenv("SDLC_PROJECT_ARTIFACTS_DIR", ".project")
        )
        self.default_client = default_client
        self.client_marker = self.project_dir / ".client"

    def detect_client(self) -> str:
        """
        Detect active client using priority order:
        1. Environment variable (SDLC_CLIENT)
        2. Persisted marker (.project/.client)
        3. Auto-detection from profile markers
        4. Default client (generic)

        Returns:
            str: Client ID
        """
        # 1. Check environment variable
        client_from_env = os.getenv("SDLC_CLIENT")
        if client_from_env:
            return client_from_env

        # 2. Check persisted marker
        if self.client_marker.exists():
            try:
                return self.client_marker.read_text().strip()
            except Exception:
                pass

        # 3. Auto-detect from profiles
        if yaml:
            detected = self._auto_detect_from_markers()
            if detected:
                # Persist detection
                self._persist_client(detected)
                return detected

        # 4. Fallback to default
        return self.default_client

    def _auto_detect_from_markers(self) -> Optional[str]:
        """
        Auto-detect client from profile markers.

        Returns:
            Optional[str]: Detected client ID or None
        """
        if not self.clients_dir.exists():
            return None

        for client_dir in self.clients_dir.iterdir():
            if not client_dir.is_dir():
                continue

            client_id = client_dir.name
            profile_path = client_dir / "profile.yml"

            if not profile_path.exists():
                continue

            try:
                with open(profile_path) as f:
                    profile = yaml.safe_load(f)

                markers = profile.get("client", {}).get("detection", {}).get("markers", [])

                for marker in markers:
                    marker_type = marker.get("type")

                    if marker_type == "file":
                        file_path = Path(marker.get("path", ""))
                        if file_path.exists():
                            return client_id

                    elif marker_type == "env":
                        env_var = marker.get("env")
                        env_value = marker.get("value")
                        if os.getenv(env_var) == env_value:
                            return client_id

                    elif marker_type == "git_remote":
                        remote_pattern = marker.get("remote")
                        if self._check_git_remote(remote_pattern):
                            return client_id

            except Exception:
                continue

        return None

    def _check_git_remote(self, pattern: str) -> bool:
        """Check if git remote matches pattern."""
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return pattern in result.stdout if result.returncode == 0 else False
        except Exception:
            return False

    def _persist_client(self, client_id: str) -> None:
        """Persist client ID to marker file."""
        try:
            self.project_dir.mkdir(parents=True, exist_ok=True)
            self.client_marker.write_text(client_id)
        except Exception:
            pass

    def set_client(self, client_id: str) -> Tuple[bool, str]:
        """
        Set active client and persist.

        Args:
            client_id: Client ID to set

        Returns:
            Tuple[bool, str]: (success, message)
        """
        profile_path = self.clients_dir / client_id / "profile.yml"

        if not profile_path.exists():
            available = self.list_clients()
            return False, f"Client profile not found: {profile_path}\n\nAvailable: {', '.join(available)}"

        # Validate profile syntax
        if yaml:
            try:
                with open(profile_path) as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                return False, f"Invalid YAML in profile: {e}"

        # Persist client
        self._persist_client(client_id)

        # Set environment variable (for current process)
        os.environ["SDLC_CLIENT"] = client_id

        return True, f"Active client set to: {client_id}"

    def list_clients(self) -> List[str]:
        """List available client IDs."""
        if not self.clients_dir.exists():
            return []

        clients = []
        for client_dir in self.clients_dir.iterdir():
            if client_dir.is_dir() and (client_dir / "profile.yml").exists():
                clients.append(client_dir.name)

        return sorted(clients)

    def get_client_info(self, client_id: str) -> Optional[Dict]:
        """Get client profile information."""
        profile_path = self.clients_dir / client_id / "profile.yml"

        if not profile_path.exists() or not yaml:
            return None

        try:
            with open(profile_path) as f:
                profile = yaml.safe_load(f)
            return profile.get("client", {})
        except Exception:
            return None

    def resolve_agent(self, agent_name: str, client_id: Optional[str] = None) -> Path:
        """
        Resolve agent path using client override or base fallback.

        Args:
            agent_name: Agent name (e.g., "code-reviewer")
            client_id: Client ID (auto-detected if None)

        Returns:
            Path: Resolved agent path

        Raises:
            FileNotFoundError: If agent not found in client or base
        """
        if client_id is None:
            client_id = self.detect_client()

        # Check client override (if not generic)
        if client_id != "generic":
            client_agent = self.clients_dir / client_id / "agents" / f"{agent_name}.md"
            if client_agent.exists():
                return client_agent

        # Fallback to base agent
        base_agent = Path(".claude") / "agents" / f"{agent_name}.md"
        if base_agent.exists():
            return base_agent

        raise FileNotFoundError(f"Agent not found: {agent_name}")

    def resolve_skill(self, skill_name: str, client_id: Optional[str] = None) -> Path:
        """
        Resolve skill path using client override or base fallback.

        Args:
            skill_name: Skill name (e.g., "gate-evaluator")
            client_id: Client ID (auto-detected if None)

        Returns:
            Path: Resolved skill directory path

        Raises:
            FileNotFoundError: If skill not found in client or base
        """
        if client_id is None:
            client_id = self.detect_client()

        # Check client override (if not generic)
        if client_id != "generic":
            client_skill = self.clients_dir / client_id / "skills" / skill_name
            if client_skill.exists() and client_skill.is_dir():
                return client_skill

        # Fallback to base skill
        base_skill = Path(".claude") / "skills" / skill_name
        if base_skill.exists() and base_skill.is_dir():
            return base_skill

        raise FileNotFoundError(f"Skill not found: {skill_name}")

    def load_profile(self, client_id: Optional[str] = None) -> Dict:
        """
        Load client profile.

        Args:
            client_id: Client ID (auto-detected if None)

        Returns:
            Dict: Profile data

        Raises:
            FileNotFoundError: If profile not found
            yaml.YAMLError: If profile invalid
        """
        if client_id is None:
            client_id = self.detect_client()

        profile_path = self.clients_dir / client_id / "profile.yml"

        if not profile_path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_path}")

        if not yaml:
            raise ImportError("PyYAML not installed (pip install pyyaml)")

        with open(profile_path) as f:
            return yaml.safe_load(f)


def main():
    """CLI interface for testing."""
    resolver = ClientResolver()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "detect":
            client = resolver.detect_client()
            print(f"Detected client: {client}")

        elif command == "list":
            clients = resolver.list_clients()
            print("Available clients:")
            for c in clients:
                print(f"  - {c}")

        elif command == "set" and len(sys.argv) > 2:
            client_id = sys.argv[2]
            success, message = resolver.set_client(client_id)
            print(message)
            sys.exit(0 if success else 1)

        elif command == "info" and len(sys.argv) > 2:
            client_id = sys.argv[2]
            info = resolver.get_client_info(client_id)
            if info:
                print(json.dumps(info, indent=2))
            else:
                print(f"Client not found: {client_id}", file=sys.stderr)
                sys.exit(1)

        elif command == "resolve-agent" and len(sys.argv) > 2:
            agent_name = sys.argv[2]
            try:
                path = resolver.resolve_agent(agent_name)
                print(f"Agent path: {path}")
            except FileNotFoundError as e:
                print(str(e), file=sys.stderr)
                sys.exit(1)

        else:
            print("Unknown command", file=sys.stderr)
            sys.exit(1)
    else:
        # Default: detect and show info
        client = resolver.detect_client()
        print(f"Active client: {client}")
        info = resolver.get_client_info(client)
        if info:
            print(f"Name: {info.get('name', 'N/A')}")
            print(f"Domain: {info.get('domain', 'N/A')}")
            print(f"Version: {info.get('version', 'N/A')}")


if __name__ == "__main__":
    main()
