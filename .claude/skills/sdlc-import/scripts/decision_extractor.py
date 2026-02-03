#!/usr/bin/env python3
"""
Decision Extractor - Architecture Decision Extraction Module

Extracts architecture decisions from codebase by analyzing:
- Existing ADR markdown files
- Code patterns and frameworks
- Configuration files
- Database schemas
- API contracts

Provides confidence scores for all extracted decisions.
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import yaml

# Add logging utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=1)


class DecisionExtractor:
    """Extracts architecture decisions from codebase"""

    def __init__(self, config: Dict):
        """
        Initialize decision extractor.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.decision_patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """Load decision detection patterns"""
        return {
            # Framework/library choices
            'framework': [
                r'(?:using|import|require)\s+[\'"](react|vue|angular|django|flask|fastapi|express|nextjs)',
                r'package\.json.*(?:react|vue|angular|express)',
                r'requirements\.txt.*(?:django|flask|fastapi)',
                r'\.csproj.*<PackageReference.*(?:EntityFramework|Dapper)'
            ],
            # Database choices
            'database': [
                r'(?:mongodb|postgresql|mysql|sqlserver|redis|dynamodb)',
                r'connectionString.*(?:Server|Host)=',
                r'DATABASE_URL|DB_HOST|MONGO_URI'
            ],
            # Authentication/authorization
            'auth': [
                r'(?:oauth|jwt|saml|openid|keycloak|auth0)',
                r'authentication.*(?:bearer|basic|oauth)',
                r'@Authorize|@RequiresAuth|@login_required'
            ],
            # API patterns
            'api': [
                r'(?:rest|graphql|grpc|soap)',
                r'@(?:Get|Post|Put|Delete|Patch)\(',
                r'app\.(?:get|post|put|delete|patch)\('
            ],
            # Messaging/events
            'messaging': [
                r'(?:kafka|rabbitmq|azure-service-bus|sqs|pub/sub)',
                r'(?:event|message)\.(?:publish|emit|send)',
                r'@KafkaListener|@RabbitListener'
            ],
            # State management
            'state': [
                r'(?:redux|mobx|vuex|recoil|zustand)',
                r'createStore|configureStore|createSlice'
            ]
        }

    def extract(
        self,
        project_path: Path,
        language_analysis: Dict,
        no_llm: bool = False
    ) -> Dict:
        """
        Extract architecture decisions from project.

        Args:
            project_path: Path to project
            language_analysis: Language detection results
            no_llm: Disable LLM synthesis (use pattern matching only)

        Returns:
            Dict with extracted decisions
        """
        logger.info("Starting decision extraction")

        decisions = []

        # 1. Extract from existing ADR files
        existing_adrs = self._extract_from_adr_files(project_path)
        decisions.extend(existing_adrs)
        logger.info(f"Found {len(existing_adrs)} existing ADR files")

        # 2. Infer from codebase patterns (if no_llm or LLM disabled)
        if no_llm or not self.config.get('decision_extraction', {}).get('llm', {}).get('enabled', False):
            inferred = self._infer_from_patterns(project_path, language_analysis)
            decisions.extend(inferred)
            logger.info(f"Inferred {len(inferred)} decisions from patterns")
        else:
            logger.warning("LLM synthesis not yet implemented - using pattern matching only")
            inferred = self._infer_from_patterns(project_path, language_analysis)
            decisions.extend(inferred)

        # 3. Calculate confidence scores for ALL decisions
        for decision in decisions:
            if 'confidence_score' not in decision:
                decision['confidence_score'] = self._calculate_confidence(decision, project_path)

        # 4. Count high-confidence decisions
        high_confidence = sum(1 for d in decisions if d.get('confidence_score', 0) >= 0.8)

        result = {
            'count': len(decisions),
            'decisions': decisions,
            'high_confidence': high_confidence,
            'extraction_method': 'pattern_matching' if no_llm else 'llm_synthesis',
            'confidence_score_coverage': 1.0  # 100% coverage
        }

        logger.info(
            "Decision extraction complete",
            extra={
                'total_decisions': len(decisions),
                'high_confidence': high_confidence,
                'confidence_coverage': '100%'
            }
        )

        return result

    def _extract_from_adr_files(self, project_path: Path) -> List[Dict]:
        """
        Extract decisions from existing ADR markdown files.

        Args:
            project_path: Path to project

        Returns:
            List of decision dicts
        """
        decisions = []

        # Common ADR directory patterns
        adr_paths = [
            project_path / "docs/adr",
            project_path / "docs/decisions",
            project_path / "adr",
            project_path / ".adr",
            project_path / "architecture/decisions"
        ]

        for adr_dir in adr_paths:
            if not adr_dir.exists():
                continue

            for adr_file in adr_dir.glob("*.md"):
                try:
                    content = adr_file.read_text(encoding='utf-8')
                    decision = self._parse_adr_markdown(adr_file.name, content, adr_file)
                    if decision:
                        decisions.append(decision)
                except Exception as e:
                    logger.warning(f"Failed to parse {adr_file}: {e}")

        return decisions

    def _parse_adr_markdown(self, filename: str, content: str, file_path: Path) -> Optional[Dict]:
        """
        Parse ADR markdown file into decision dict.

        Args:
            filename: ADR filename
            content: File content
            file_path: Full path to file

        Returns:
            Decision dict or None
        """
        # Extract ADR number from filename (e.g., "0001-use-postgres.md" -> "ADR-0001")
        match = re.search(r'(\d+)', filename)
        if not match:
            return None

        adr_num = match.group(1).zfill(4)
        adr_id = f"ADR-{adr_num}"

        # Extract title from first heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename.replace('.md', '')

        # Remove ADR number prefix from title if present
        title = re.sub(r'^\d+[:\-\s]+', '', title).strip()

        # Extract status
        status_match = re.search(r'(?:status|Status):\s*(\w+)', content, re.IGNORECASE)
        status = status_match.group(1).lower() if status_match else 'accepted'

        # Extract date
        date_match = re.search(r'(?:date|Date):\s*(\d{4}-\d{2}-\d{2})', content)
        date = date_match.group(1) if date_match else self._get_file_date(file_path)

        # Extract context section
        context_match = re.search(r'##\s*Context\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        context = context_match.group(1).strip() if context_match else ""

        # Extract decision section
        decision_match = re.search(r'##\s*Decision\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        decision_text = decision_match.group(1).strip() if decision_match else ""

        # Extract consequences
        consequences_match = re.search(r'##\s*Consequences\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        consequences = consequences_match.group(1).strip() if consequences_match else ""

        # Determine category based on content
        category = self._categorize_decision(title + " " + context + " " + decision_text)

        return {
            'id': adr_id,
            'title': title,
            'status': status,
            'date': date,
            'category': category,
            'context': context,
            'decision': decision_text,
            'consequences': consequences,
            'source': 'existing_adr',
            'source_file': str(file_path.relative_to(file_path.parent.parent.parent))
        }

    def _get_file_date(self, file_path: Path) -> str:
        """Get file modification date as ISO string"""
        try:
            timestamp = file_path.stat().st_mtime
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return datetime.now(timezone.utc).strftime('%Y-%m-%d')

    def _infer_from_patterns(self, project_path: Path, language_analysis: Dict) -> List[Dict]:
        """
        Infer architecture decisions from code patterns.

        Args:
            project_path: Path to project
            language_analysis: Language detection results

        Returns:
            List of inferred decisions
        """
        decisions = []

        # Infer from primary language/framework
        primary_language = language_analysis.get('primary_language')
        if primary_language:
            framework = language_analysis.get('frameworks', {}).get(primary_language)
            if framework:
                decisions.append({
                    'id': f"ADR-INFERRED-{len(decisions)+1:03d}",
                    'title': f"Use {framework} as {primary_language} Framework",
                    'status': 'accepted',
                    'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                    'category': 'framework',
                    'context': f"Project is primarily {primary_language} codebase",
                    'decision': f"Use {framework} as the primary {primary_language} framework",
                    'consequences': f"All {primary_language} code follows {framework} patterns",
                    'source': 'inferred_from_codebase'
                })

        # Infer from database connections
        db_decision = self._infer_database_decision(project_path)
        if db_decision:
            decisions.append(db_decision)

        # Infer from authentication patterns
        auth_decision = self._infer_auth_decision(project_path)
        if auth_decision:
            decisions.append(auth_decision)

        return decisions

    def _infer_database_decision(self, project_path: Path) -> Optional[Dict]:
        """Infer database technology from connection strings and config"""
        # Search for database connection patterns in common config files
        config_files = [
            '.env',
            'appsettings.json',
            'application.yml',
            'database.yml',
            'config/database.yml'
        ]

        for config_file in config_files:
            file_path = project_path / config_file
            if file_path.exists():
                try:
                    content = file_path.read_text()

                    # PostgreSQL
                    if re.search(r'postgres|postgresql|psql', content, re.IGNORECASE):
                        return {
                            'id': 'ADR-INFERRED-DATABASE',
                            'title': 'Use PostgreSQL as Primary Database',
                            'status': 'accepted',
                            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                            'category': 'database',
                            'context': 'Database choice for application',
                            'decision': 'Use PostgreSQL as the primary relational database',
                            'consequences': 'Leverage PostgreSQL-specific features like JSONB, full-text search',
                            'source': 'inferred_from_config',
                            'source_file': str(config_file)
                        }

                    # MongoDB
                    if re.search(r'mongodb|mongo:', content, re.IGNORECASE):
                        return {
                            'id': 'ADR-INFERRED-DATABASE',
                            'title': 'Use MongoDB as Primary Database',
                            'status': 'accepted',
                            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                            'category': 'database',
                            'context': 'Database choice for application',
                            'decision': 'Use MongoDB as the primary NoSQL database',
                            'consequences': 'Schema flexibility, document-oriented data model',
                            'source': 'inferred_from_config',
                            'source_file': str(config_file)
                        }

                except Exception:
                    continue

        return None

    def _infer_auth_decision(self, project_path: Path) -> Optional[Dict]:
        """Infer authentication/authorization approach"""
        # Search for auth patterns in code
        for file_path in project_path.rglob("*.{py,cs,js,ts}"):
            try:
                content = file_path.read_text()

                if re.search(r'oauth|OAuth|OAUTH', content):
                    return {
                        'id': 'ADR-INFERRED-AUTH',
                        'title': 'Use OAuth 2.0 for Authentication',
                        'status': 'accepted',
                        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                        'category': 'security',
                        'context': 'Authentication and authorization strategy',
                        'decision': 'Use OAuth 2.0 for authentication',
                        'consequences': 'Secure token-based authentication, third-party integration support',
                        'source': 'inferred_from_code'
                    }

                if re.search(r'jwt|JWT|JsonWebToken', content):
                    return {
                        'id': 'ADR-INFERRED-AUTH',
                        'title': 'Use JWT for Authentication Tokens',
                        'status': 'accepted',
                        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                        'category': 'security',
                        'context': 'Token format for authentication',
                        'decision': 'Use JSON Web Tokens (JWT) for authentication',
                        'consequences': 'Stateless authentication, scalable token validation',
                        'source': 'inferred_from_code'
                    }

            except Exception:
                continue

        return None

    def _categorize_decision(self, text: str) -> str:
        """
        Categorize decision based on content keywords.

        Args:
            text: Decision text to analyze

        Returns:
            Category string
        """
        text_lower = text.lower()

        if any(kw in text_lower for kw in ['database', 'postgres', 'mongo', 'sql', 'nosql']):
            return 'database'
        elif any(kw in text_lower for kw in ['auth', 'oauth', 'jwt', 'security', 'login']):
            return 'security'
        elif any(kw in text_lower for kw in ['api', 'rest', 'graphql', 'grpc']):
            return 'api'
        elif any(kw in text_lower for kw in ['framework', 'library', 'react', 'vue', 'django']):
            return 'framework'
        elif any(kw in text_lower for kw in ['deploy', 'infrastructure', 'cloud', 'aws', 'azure']):
            return 'infrastructure'
        elif any(kw in text_lower for kw in ['test', 'testing', 'qa', 'quality']):
            return 'testing'
        else:
            return 'other'

    def _calculate_confidence(self, decision: Dict, project_path: Path) -> float:
        """
        Calculate confidence score for a decision.

        Confidence based on:
        - Source (existing ADR = high, inferred = medium)
        - Completeness of fields
        - Evidence in codebase

        Args:
            decision: Decision dict
            project_path: Path to project

        Returns:
            Confidence score (0.0 to 1.0)
        """
        score = 0.0

        # Base score from source
        if decision.get('source') == 'existing_adr':
            score += 0.5  # ADR files are authoritative
        elif decision.get('source') == 'inferred_from_config':
            score += 0.3  # Config-based inference is reliable
        else:
            score += 0.2  # Code-based inference is less certain

        # Completeness bonus
        required_fields = ['title', 'context', 'decision', 'consequences']
        filled_fields = sum(1 for f in required_fields if decision.get(f))
        score += (filled_fields / len(required_fields)) * 0.3

        # Evidence in codebase (if title contains tech name)
        title_lower = decision.get('title', '').lower()
        tech_keywords = ['postgres', 'mongo', 'react', 'vue', 'oauth', 'jwt']

        for keyword in tech_keywords:
            if keyword in title_lower:
                # Search for evidence in codebase
                evidence_count = self._count_evidence(project_path, keyword)
                if evidence_count > 0:
                    score += min(0.2, evidence_count * 0.02)  # Max 0.2 bonus
                break

        # Cap at 1.0
        return min(1.0, score)

    def _count_evidence(self, project_path: Path, keyword: str) -> int:
        """Count occurrences of keyword in codebase"""
        count = 0
        try:
            for file_path in list(project_path.rglob("*.{py,js,ts,cs,java}"))[:100]:  # Limit to 100 files
                try:
                    content = file_path.read_text()
                    count += content.lower().count(keyword)
                except Exception:
                    continue
        except Exception:
            pass

        return count
