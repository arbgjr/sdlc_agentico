#!/usr/bin/env python3
"""
Threat Modeler - STRIDE Threat Analysis Module

Performs STRIDE threat modeling on extracted architecture decisions:
- Spoofing
- Tampering
- Repudiation
- Information Disclosure
- Denial of Service
- Elevation of Privilege

Identifies security risks and recommends mitigations.
"""

import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timezone

# Add logging utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=3)


class ThreatModeler:
    """STRIDE threat modeling analyzer"""

    def __init__(self, config: Dict):
        """
        Initialize threat modeler.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.threat_categories = ['spoofing', 'tampering', 'repudiation',
                                   'information_disclosure', 'denial_of_service',
                                   'elevation_of_privilege']

    def analyze(self, project_path: Path, decisions: Dict) -> Dict:
        """
        Perform STRIDE threat analysis.

        Args:
            project_path: Path to project
            decisions: Extracted architecture decisions

        Returns:
            Dict with threat analysis results
        """
        logger.info("Starting STRIDE threat modeling")

        threats = []

        # Analyze each decision for security implications
        for decision in decisions.get('decisions', []):
            decision_threats = self._analyze_decision(decision)
            threats.extend(decision_threats)

        # Categorize by severity
        critical = sum(1 for t in threats if t.get('severity') == 'critical')
        high = sum(1 for t in threats if t.get('severity') == 'high')
        medium = sum(1 for t in threats if t.get('severity') == 'medium')
        low = sum(1 for t in threats if t.get('severity') == 'low')

        result = {
            'total': len(threats),
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low,
            'threats': threats,
            'analysis_method': 'pattern_based_stride',
            'timestamp': datetime.now(timezone.utc).isoformat() + 'Z'
        }

        logger.info(
            "Threat modeling complete",
            extra={
                'total_threats': len(threats),
                'critical': critical,
                'high': high
            }
        )

        return result

    def _analyze_decision(self, decision: Dict) -> List[Dict]:
        """
        Analyze a single decision for security threats.

        Args:
            decision: Decision dict

        Returns:
            List of threat dicts
        """
        threats = []
        category = decision.get('category', '').lower()
        title = decision.get('title', '').lower()
        decision_text = decision.get('decision', '').lower()

        # Database threats
        if category == 'database' or any(kw in title for kw in ['database', 'postgres', 'mongo', 'sql']):
            threats.extend([
                {
                    'id': f"THREAT-{decision.get('id', 'UNKNOWN')}-001",
                    'stride_category': 'information_disclosure',
                    'title': 'Unencrypted Database Connections',
                    'description': 'Database connections may transmit sensitive data without encryption',
                    'severity': 'high',
                    'affected_component': decision.get('title'),
                    'mitigation': 'Enforce TLS/SSL for all database connections',
                    'related_decision': decision.get('id')
                },
                {
                    'id': f"THREAT-{decision.get('id', 'UNKNOWN')}-002",
                    'stride_category': 'tampering',
                    'title': 'SQL Injection Risk',
                    'description': 'Database queries vulnerable to SQL injection if not using parameterized queries',
                    'severity': 'critical',
                    'affected_component': decision.get('title'),
                    'mitigation': 'Use parameterized queries or ORM with prepared statements',
                    'related_decision': decision.get('id')
                }
            ])

        # Authentication/security threats
        if category == 'security' or any(kw in title for kw in ['auth', 'oauth', 'jwt', 'login']):
            threats.extend([
                {
                    'id': f"THREAT-{decision.get('id', 'UNKNOWN')}-003",
                    'stride_category': 'spoofing',
                    'title': 'Weak Authentication Mechanisms',
                    'description': 'Authentication system may be vulnerable to brute force or credential stuffing',
                    'severity': 'high',
                    'affected_component': decision.get('title'),
                    'mitigation': 'Implement rate limiting, account lockout, and multi-factor authentication',
                    'related_decision': decision.get('id')
                },
                {
                    'id': f"THREAT-{decision.get('id', 'UNKNOWN')}-004",
                    'stride_category': 'elevation_of_privilege',
                    'title': 'Insufficient Authorization Checks',
                    'description': 'Users may access resources beyond their privilege level',
                    'severity': 'critical',
                    'affected_component': decision.get('title'),
                    'mitigation': 'Implement role-based access control (RBAC) with least privilege principle',
                    'related_decision': decision.get('id')
                }
            ])

        # API threats
        if category == 'api' or any(kw in title for kw in ['api', 'rest', 'graphql']):
            threats.extend([
                {
                    'id': f"THREAT-{decision.get('id', 'UNKNOWN')}-005",
                    'stride_category': 'denial_of_service',
                    'title': 'API Rate Limiting Not Enforced',
                    'description': 'API endpoints vulnerable to abuse and resource exhaustion',
                    'severity': 'medium',
                    'affected_component': decision.get('title'),
                    'mitigation': 'Implement rate limiting, throttling, and request validation',
                    'related_decision': decision.get('id')
                },
                {
                    'id': f"THREAT-{decision.get('id', 'UNKNOWN')}-006",
                    'stride_category': 'information_disclosure',
                    'title': 'Sensitive Data in API Responses',
                    'description': 'API may expose sensitive data in error messages or responses',
                    'severity': 'high',
                    'affected_component': decision.get('title'),
                    'mitigation': 'Sanitize error messages, use DTOs to control response fields',
                    'related_decision': decision.get('id')
                }
            ])

        # Framework/infrastructure threats
        if category in ['framework', 'infrastructure']:
            threats.append({
                'id': f"THREAT-{decision.get('id', 'UNKNOWN')}-007",
                'stride_category': 'tampering',
                'title': 'Dependency Vulnerabilities',
                'description': 'Third-party dependencies may contain known vulnerabilities',
                'severity': 'high',
                'affected_component': decision.get('title'),
                'mitigation': 'Regularly scan dependencies with tools like Snyk, Dependabot, or npm audit',
                'related_decision': decision.get('id')
            })

        return threats
