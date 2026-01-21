#!/usr/bin/env python3
"""
Simple Memory Store

Fast, JSON-based memory system for working context (facts, tools, repos).
Complements RAG corpus with lightweight, human-readable storage.

Adapted from claude-orchestrator for SDLC Agêntico.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parents[3] / "lib" / "python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="memory-manager", phase=0)


class SimpleStore:
    """Manages simple JSON-based memory"""

    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or Path.home() / ".claude" / "simple-memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.facts_file = self.memory_dir / "facts.json"
        self.toolchain_file = self.memory_dir / "toolchain.json"
        self.repos_file = self.memory_dir / "repos.json"
        self.projects_dir = self.memory_dir / "projects"
        self.projects_dir.mkdir(exist_ok=True)

        logger.info(
            "SimpleStore initialized",
            extra={"memory_dir": str(self.memory_dir)}
        )

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file or return empty dict"""
        if not file_path.exists():
            return {}
        with open(file_path, "r") as f:
            return json.load(f)

    def _save_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Save JSON file atomically"""
        temp_file = file_path.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)
        temp_file.replace(file_path)

    # === Facts Management ===

    def add_fact(
        self,
        text: str,
        tags: Optional[List[str]] = None,
        project: Optional[str] = None
    ) -> str:
        """Add a fact to memory"""
        with log_operation("add_fact", logger):
            facts = self._load_json(self.facts_file)

            if "facts" not in facts:
                facts["facts"] = []

            fact_id = f"fact-{len(facts['facts']) + 1:03d}"
            fact = {
                "id": fact_id,
                "text": text,
                "added": datetime.now(timezone.utc).isoformat(),
                "tags": tags or [],
                "project": project,
                "access_count": 0
            }

            facts["facts"].append(fact)
            self._save_json(self.facts_file, facts)

            logger.info(
                "Fact added",
                extra={
                    "fact_id": fact_id,
                    "tags": tags or [],
                    "project": project
                }
            )

            return fact_id

    def recall_facts(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        project: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Recall facts by query, tags, or project"""
        with log_operation("recall_facts", logger):
            facts = self._load_json(self.facts_file).get("facts", [])

            # Filter
            filtered = facts
            if query:
                query_lower = query.lower()
                filtered = [
                    f for f in filtered
                    if query_lower in f["text"].lower()
                ]

            if tags:
                filtered = [
                    f for f in filtered
                    if any(tag in f.get("tags", []) for tag in tags)
                ]

            if project:
                filtered = [
                    f for f in filtered
                    if f.get("project") == project
                ]

            # Sort by recency
            filtered.sort(key=lambda f: f["added"], reverse=True)

            # Update access count
            for fact in filtered[:limit]:
                fact["access_count"] = fact.get("access_count", 0) + 1

            self._save_json(self.facts_file, {"facts": facts})

            logger.debug(
                "Facts recalled",
                extra={
                    "query": query,
                    "tags": tags,
                    "project": project,
                    "count": len(filtered[:limit])
                }
            )

            return filtered[:limit]

    def delete_fact(self, fact_id: str) -> bool:
        """Delete a fact by ID"""
        with log_operation(f"delete_fact:{fact_id}", logger):
            facts = self._load_json(self.facts_file)

            if "facts" not in facts:
                return False

            original_count = len(facts["facts"])
            facts["facts"] = [f for f in facts["facts"] if f["id"] != fact_id]

            if len(facts["facts"]) == original_count:
                logger.warning("Fact not found", extra={"fact_id": fact_id})
                return False

            self._save_json(self.facts_file, facts)
            logger.info("Fact deleted", extra={"fact_id": fact_id})
            return True

    # === Toolchain Management ===

    def add_tool(
        self,
        name: str,
        repo: Optional[str] = None,
        version: Optional[str] = None,
        install_cmd: Optional[str] = None,
        docs_url: Optional[str] = None
    ) -> None:
        """Add a tool to toolchain"""
        with log_operation(f"add_tool:{name}", logger):
            toolchain = self._load_json(self.toolchain_file)

            toolchain[name] = {
                "repo": repo,
                "version": version,
                "install": install_cmd,
                "docs": docs_url,
                "added": datetime.now(timezone.utc).isoformat()
            }

            self._save_json(self.toolchain_file, toolchain)

            logger.info(
                "Tool added",
                extra={"tool": name, "version": version}
            )

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool information"""
        toolchain = self._load_json(self.toolchain_file)
        return toolchain.get(name)

    def list_tools(self) -> Dict[str, Any]:
        """List all tools"""
        return self._load_json(self.toolchain_file)

    # === Repos Management ===

    def add_repo(
        self,
        name: str,
        url: str,
        branch: Optional[str] = "main",
        description: Optional[str] = None
    ) -> None:
        """Add a repository reference"""
        with log_operation(f"add_repo:{name}", logger):
            repos = self._load_json(self.repos_file)

            repos[name] = {
                "url": url,
                "branch": branch,
                "description": description,
                "added": datetime.now(timezone.utc).isoformat()
            }

            self._save_json(self.repos_file, repos)

            logger.info(
                "Repo added",
                extra={"repo": name, "url": url}
            )

    def get_repo(self, name: str) -> Optional[Dict[str, Any]]:
        """Get repository information"""
        repos = self._load_json(self.repos_file)
        return repos.get(name)

    def list_repos(self) -> Dict[str, Any]:
        """List all repositories"""
        return self._load_json(self.repos_file)

    # === Project Context ===

    def save_project_context(
        self,
        project_name: str,
        data: Dict[str, Any]
    ) -> None:
        """Save project-specific context"""
        with log_operation(f"save_project:{project_name}", logger):
            project_file = self.projects_dir / f"{project_name}.json"

            existing = self._load_json(project_file) if project_file.exists() else {}
            existing.update({
                **data,
                "updated_at": datetime.now(timezone.utc).isoformat()
            })

            if "created_at" not in existing:
                existing["created_at"] = existing["updated_at"]

            self._save_json(project_file, existing)

            logger.info(
                "Project context saved",
                extra={"project": project_name}
            )

    def load_project_context(self, project_name: str) -> Dict[str, Any]:
        """Load project-specific context"""
        project_file = self.projects_dir / f"{project_name}.json"

        if not project_file.exists():
            logger.warning(
                "Project context not found",
                extra={"project": project_name}
            )
            return {}

        return self._load_json(project_file)

    # === Utilities ===

    def search(self, query: str) -> Dict[str, List[Any]]:
        """Search across all memory types"""
        with log_operation(f"search:{query}", logger):
            query_lower = query.lower()
            results = {
                "facts": [],
                "tools": [],
                "repos": [],
                "projects": []
            }

            # Search facts
            facts = self._load_json(self.facts_file).get("facts", [])
            results["facts"] = [
                f for f in facts
                if query_lower in f["text"].lower()
            ]

            # Search tools
            toolchain = self._load_json(self.toolchain_file)
            results["tools"] = [
                {"name": name, **data}
                for name, data in toolchain.items()
                if query_lower in name.lower()
            ]

            # Search repos
            repos = self._load_json(self.repos_file)
            results["repos"] = [
                {"name": name, **data}
                for name, data in repos.items()
                if query_lower in name.lower() or
                   query_lower in data.get("description", "").lower()
            ]

            # Search projects
            for project_file in self.projects_dir.glob("*.json"):
                project_name = project_file.stem
                project_data = self._load_json(project_file)

                if any(
                    query_lower in str(v).lower()
                    for v in project_data.values()
                    if isinstance(v, str)
                ):
                    results["projects"].append({
                        "name": project_name,
                        **project_data
                    })

            logger.info(
                "Search complete",
                extra={
                    "query": query,
                    "facts": len(results["facts"]),
                    "tools": len(results["tools"]),
                    "repos": len(results["repos"]),
                    "projects": len(results["projects"])
                }
            )

            return results

    def export(self, output_file: Path) -> None:
        """Export all memory to single JSON file"""
        with log_operation(f"export:{output_file}", logger):
            export_data = {
                "facts": self._load_json(self.facts_file),
                "toolchain": self._load_json(self.toolchain_file),
                "repos": self._load_json(self.repos_file),
                "projects": {
                    p.stem: self._load_json(p)
                    for p in self.projects_dir.glob("*.json")
                },
                "exported_at": datetime.now(timezone.utc).isoformat()
            }

            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2)

            logger.info("Memory exported", extra={"file": str(output_file)})


def main():
    parser = argparse.ArgumentParser(description="Simple Memory Store")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add-fact
    fact_parser = subparsers.add_parser("add-fact", help="Add a fact")
    fact_parser.add_argument("text", help="Fact text")
    fact_parser.add_argument("--tags", nargs="+", help="Tags")
    fact_parser.add_argument("--project", help="Project name")

    # recall
    recall_parser = subparsers.add_parser("recall", help="Recall facts")
    recall_parser.add_argument("query", nargs="?", help="Search query")
    recall_parser.add_argument("--tags", nargs="+", help="Filter by tags")
    recall_parser.add_argument("--project", help="Filter by project")
    recall_parser.add_argument("--limit", type=int, default=10, help="Result limit")

    # delete-fact
    delete_parser = subparsers.add_parser("delete-fact", help="Delete a fact")
    delete_parser.add_argument("fact_id", help="Fact ID")

    # add-tool
    tool_parser = subparsers.add_parser("add-tool", help="Add a tool")
    tool_parser.add_argument("name", help="Tool name")
    tool_parser.add_argument("--repo", help="Repository URL")
    tool_parser.add_argument("--version", help="Version")
    tool_parser.add_argument("--install", help="Install command")
    tool_parser.add_argument("--docs", help="Documentation URL")

    # list-tools
    subparsers.add_parser("list-tools", help="List all tools")

    # add-repo
    repo_parser = subparsers.add_parser("add-repo", help="Add a repository")
    repo_parser.add_argument("name", help="Repo name")
    repo_parser.add_argument("url", help="Repo URL")
    repo_parser.add_argument("--branch", default="main", help="Default branch")
    repo_parser.add_argument("--description", help="Description")

    # list-repos
    subparsers.add_parser("list-repos", help="List all repositories")

    # search
    search_parser = subparsers.add_parser("search", help="Search all memory")
    search_parser.add_argument("query", help="Search query")

    # export
    export_parser = subparsers.add_parser("export", help="Export memory")
    export_parser.add_argument("output", type=Path, help="Output file")

    args = parser.parse_args()
    store = SimpleStore()

    if args.command == "add-fact":
        fact_id = store.add_fact(args.text, args.tags, args.project)
        print(f"Fact added: {fact_id}")

    elif args.command == "recall":
        facts = store.recall_facts(args.query, args.tags, args.project, args.limit)
        print(json.dumps(facts, indent=2))

    elif args.command == "delete-fact":
        success = store.delete_fact(args.fact_id)
        print(f"Fact deleted: {success}")
        sys.exit(0 if success else 1)

    elif args.command == "add-tool":
        store.add_tool(args.name, args.repo, args.version, args.install, args.docs)
        print(f"Tool added: {args.name}")

    elif args.command == "list-tools":
        tools = store.list_tools()
        print(json.dumps(tools, indent=2))

    elif args.command == "add-repo":
        store.add_repo(args.name, args.url, args.branch, args.description)
        print(f"Repo added: {args.name}")

    elif args.command == "list-repos":
        repos = store.list_repos()
        print(json.dumps(repos, indent=2))

    elif args.command == "search":
        results = store.search(args.query)
        print(json.dumps(results, indent=2))

    elif args.command == "export":
        store.export(args.output)
        print(f"Memory exported to: {args.output}")


if __name__ == "__main__":
    main()
