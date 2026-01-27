#!/usr/bin/env python3
"""
Migration Analyzer - Extract decisions from database migrations
Supports: EF Core, Alembic, Flyway
"""

import sys
import re
from pathlib import Path
from typing import Dict, List
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class MigrationAnalyzer:
    """Analyze database migrations for architectural decisions"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('migration_analysis', {}).get('enabled', True)
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """Load migration patterns from config"""
        patterns_file = Path(__file__).parent.parent / "config" / "migration_patterns.yml"

        if not patterns_file.exists():
            logger.warning(f"Migration patterns file not found: {patterns_file}")
            return self._get_default_patterns()

        with open(patterns_file, 'r') as f:
            return yaml.safe_load(f)

    def _get_default_patterns(self) -> Dict:
        """Return default patterns if config file not found"""
        return {
            "frameworks": {
                "ef_core": {
                    "file_pattern": "**/Migrations/*.cs",
                    "language": "csharp",
                    "patterns": {
                        "table_creation": {
                            "regex": r"migrationBuilder\.CreateTable\(\s*name:\s*\"(\w+)\"",
                            "decision_template": "Create table {table_name} via migration",
                            "confidence": 0.95
                        },
                        "index_creation": {
                            "regex": r"migrationBuilder\.CreateIndex\(.*name:\s*\"(\w+)\"",
                            "decision_template": "Create index {index_name} for performance",
                            "confidence": 0.90
                        },
                        "rls_policy": {
                            "regex": r"CREATE POLICY|ENABLE ROW LEVEL SECURITY",
                            "decision_template": "Implement Row-Level Security for multi-tenancy",
                            "confidence": 1.0
                        }
                    }
                },
                "alembic": {
                    "file_pattern": "**/alembic/versions/*.py",
                    "language": "python",
                    "patterns": {
                        "table_creation": {
                            "regex": r"op\.create_table\(['\"]([\\w_]+)['\"]",
                            "decision_template": "Create table {table_name} via migration",
                            "confidence": 0.95
                        },
                        "index_creation": {
                            "regex": r"op\.create_index\(['\"]([\\w_]+)['\"]",
                            "decision_template": "Create index {index_name} for performance",
                            "confidence": 0.90
                        }
                    }
                },
                "flyway": {
                    "file_pattern": "**/db/migration/*.sql",
                    "language": "sql",
                    "patterns": {
                        "table_creation": {
                            "regex": r"CREATE TABLE\s+(IF NOT EXISTS\s+)?([\\w_]+)",
                            "decision_template": "Create table {table_name} via migration",
                            "confidence": 0.95
                        },
                        "index_creation": {
                            "regex": r"CREATE\s+(UNIQUE\s+)?INDEX\s+([\\w_]+)",
                            "decision_template": "Create index {index_name} for performance",
                            "confidence": 0.90
                        },
                        "rls_policy": {
                            "regex": r"CREATE POLICY\s+([\\w_]+)",
                            "decision_template": "Implement Row-Level Security policy {policy_name}",
                            "confidence": 1.0
                        }
                    }
                }
            }
        }

    def analyze(self, project_path: Path) -> Dict:
        """Main entry point for migration analysis"""
        with log_operation("analyze_migrations", logger):
            migrations = {
                "ef_core": self._analyze_ef_core(project_path),
                "alembic": self._analyze_alembic(project_path),
                "flyway": self._analyze_flyway(project_path)
            }

            # Aggregate results
            all_decisions = []
            for framework, decisions in migrations.items():
                all_decisions.extend(decisions)

            logger.info(
                "Migration analysis complete",
                extra={
                    "total_decisions": len(all_decisions),
                    "ef_core": len(migrations["ef_core"]),
                    "alembic": len(migrations["alembic"]),
                    "flyway": len(migrations["flyway"])
                }
            )

            return {
                "decisions": all_decisions,
                "count": len(all_decisions),
                "by_framework": {
                    "ef_core": len(migrations["ef_core"]),
                    "alembic": len(migrations["alembic"]),
                    "flyway": len(migrations["flyway"])
                }
            }

    def _analyze_ef_core(self, project_path: Path) -> List[Dict]:
        """Analyze EF Core migrations (C#)"""
        decisions = []

        for migration_file in project_path.rglob("Migrations/*.cs"):
            try:
                content = migration_file.read_text()

                # Extract schema changes
                if re.search(r'CreateTable', content):
                    decision = self._extract_table_creation(migration_file, content, "EF Core")
                    if decision:
                        decisions.append(decision)

                if re.search(r'CreateIndex', content):
                    decision = self._extract_index_creation(migration_file, content, "EF Core")
                    if decision:
                        decisions.append(decision)

                # RLS policies (PostgreSQL-specific)
                if re.search(r'CREATE POLICY|ALTER TABLE.*ENABLE ROW LEVEL SECURITY', content):
                    decision = self._extract_rls_policy(migration_file, content, "EF Core")
                    if decision:
                        decisions.append(decision)

            except Exception as e:
                logger.warning(f"Failed to parse {migration_file}: {e}")

        return decisions

    def _analyze_alembic(self, project_path: Path) -> List[Dict]:
        """Analyze Alembic migrations (Python)"""
        decisions = []

        for migration_file in project_path.rglob("alembic/versions/*.py"):
            try:
                content = migration_file.read_text()

                # Extract schema changes
                if re.search(r'op\.create_table', content):
                    decision = self._extract_table_creation(migration_file, content, "Alembic")
                    if decision:
                        decisions.append(decision)

                if re.search(r'op\.create_index', content):
                    decision = self._extract_index_creation(migration_file, content, "Alembic")
                    if decision:
                        decisions.append(decision)

            except Exception as e:
                logger.warning(f"Failed to parse {migration_file}: {e}")

        return decisions

    def _analyze_flyway(self, project_path: Path) -> List[Dict]:
        """Analyze Flyway migrations (SQL)"""
        decisions = []

        # Find all SQL files in db/migration directories
        for migration_file in project_path.rglob("**/db/migration/*.sql"):
            try:
                content = migration_file.read_text()

                # Extract schema changes
                if re.search(r'CREATE TABLE', content, re.IGNORECASE):
                    decision = self._extract_table_creation(migration_file, content, "Flyway")
                    if decision:
                        decisions.append(decision)

                if re.search(r'CREATE\s+(?:UNIQUE\s+)?INDEX', content, re.IGNORECASE):
                    decision = self._extract_index_creation(migration_file, content, "Flyway")
                    if decision:
                        decisions.append(decision)

                if re.search(r'CREATE POLICY', content, re.IGNORECASE):
                    decision = self._extract_rls_policy(migration_file, content, "Flyway")
                    if decision:
                        decisions.append(decision)

            except Exception as e:
                logger.warning(f"Failed to parse {migration_file}: {e}")

        return decisions

    def _extract_table_creation(self, file: Path, content: str, framework: str) -> Dict:
        """Extract table creation decision"""
        # Parse table name
        table_name = None

        if framework == "EF Core":
            match = re.search(r'migrationBuilder\.CreateTable\(\s*name:\s*"(\w+)"', content)
            if match:
                table_name = match.group(1)
        elif framework == "Alembic":
            match = re.search(r'op\.create_table\([\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]', content)
            if match:
                table_name = match.group(1)
        elif framework == "Flyway":
            match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][a-zA-Z0-9_]+)', content, re.IGNORECASE)
            if match:
                table_name = match.group(1)

        if not table_name:
            return None

        return {
            "id": f"ADR-INFERRED-MIGRATION-TABLE-{table_name}",
            "title": f"Database Schema: {table_name} entity",
            "category": "data_model",
            "source": "migration",
            "framework": framework,
            "migration_file": str(file.relative_to(file.parents[len(file.parents) - 1])),
            "confidence": 0.95,
            "decision": f"Created {table_name} table via {framework} migration",
            "evidence": [
                {
                    "file": str(file),
                    "pattern": "table_creation",
                    "quality": 1.0,
                    "source": "migration"
                }
            ]
        }

    def _extract_index_creation(self, file: Path, content: str, framework: str) -> Dict:
        """Extract index creation decision"""
        index_name = None

        if framework == "EF Core":
            match = re.search(r'migrationBuilder\.CreateIndex\(.*?name:\s*"(\w+)"', content, re.DOTALL)
            if match:
                index_name = match.group(1)
        elif framework == "Alembic":
            match = re.search(r'op\.create_index\([\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]', content)
            if match:
                index_name = match.group(1)
        elif framework == "Flyway":
            match = re.search(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.IGNORECASE)
            if match:
                index_name = match.group(1)

        if not index_name:
            return None

        return {
            "id": f"ADR-INFERRED-MIGRATION-INDEX-{index_name}",
            "title": f"Performance Optimization: {index_name} index",
            "category": "performance",
            "source": "migration",
            "framework": framework,
            "migration_file": str(file.relative_to(file.parents[len(file.parents) - 1])),
            "confidence": 0.90,
            "decision": f"Created {index_name} index via {framework} migration for performance",
            "evidence": [
                {
                    "file": str(file),
                    "pattern": "index_creation",
                    "quality": 1.0,
                    "source": "migration"
                }
            ]
        }

    def _extract_rls_policy(self, file: Path, content: str, framework: str) -> Dict:
        """Extract RLS policy decision"""
        policy_name = None

        # Extract policy name
        match = re.search(r'CREATE POLICY\s+([\\w_]+)', content, re.IGNORECASE)
        if match:
            policy_name = match.group(1)
        else:
            policy_name = "RLS_POLICY"

        return {
            "id": f"ADR-INFERRED-MIGRATION-RLS-{policy_name}",
            "title": "Security Architecture: Row-Level Security",
            "category": "security",
            "source": "migration",
            "framework": framework,
            "migration_file": str(file.relative_to(file.parents[len(file.parents) - 1])),
            "confidence": 1.0,
            "decision": f"Implemented Row-Level Security via {framework} migration",
            "rationale": "RLS provides database-level multi-tenancy isolation",
            "evidence": [
                {
                    "file": str(file),
                    "pattern": "rls_policy",
                    "quality": 1.0,
                    "source": "migration"
                }
            ]
        }


if __name__ == "__main__":
    # Test migration analysis
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Analyze database migrations")
    parser.add_argument("project_path", type=Path, help="Project directory")
    parser.add_argument("--config", type=Path, help="Config file")
    args = parser.parse_args()

    config = {}
    if args.config and args.config.exists():
        with open(args.config) as f:
            config = yaml.safe_load(f)

    analyzer = MigrationAnalyzer(config)
    result = analyzer.analyze(args.project_path)
    print(json.dumps(result, indent=2))
