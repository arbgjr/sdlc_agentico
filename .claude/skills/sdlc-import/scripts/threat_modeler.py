#!/usr/bin/env python3
"""
Threat Modeler - STRIDE threat analysis
Uses security-guidance plugin patterns.

NEW (v2.1.7): Bounded Context-Aware Threat Modeling
- Analyzes each bounded context individually
- Domain-specific threats (GDPR, financial, event-driven)
- Data lifecycle threats (backup, retention, PITR, export)

References:
- awesome-copilot: threat-model-generator.prompt
- claude-plugins-official: security-guidance
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import yaml

# Add logging utilities (absolute path from project root)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


@dataclass
class BoundedContext:
    """Represents a bounded context in DDD"""
    name: str
    path: Path
    has_events: bool = False
    has_gdpr_data: bool = False
    has_financial_data: bool = False
    description: str = ""


class ThreatModeler:
    """Perform STRIDE threat modeling"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config['threat_modeling']['enabled']
        self.escalation_threshold = config['threat_modeling']['escalation_threshold']
        self.threat_templates = self._load_threat_templates()

    def _load_threat_templates(self) -> Dict:
        """Load domain-specific threat templates"""
        return {
            "gdpr": [
                {
                    "id": "STRIDE-T-GDPR-001",
                    "title": "Data Subject Access Request (DSAR) Manipulation",
                    "category": "Tampering",
                    "severity": "HIGH",
                    "cvss_score": 7.5,
                    "description": "Attacker could manipulate DSAR responses to expose other users' data",
                    "mitigation": "Implement strict tenant isolation checks in DSAR handlers"
                },
                {
                    "id": "STRIDE-E-GDPR-002",
                    "title": "Unauthorized Data Export Elevation",
                    "category": "Elevation of Privilege",
                    "severity": "HIGH",
                    "cvss_score": 7.0,
                    "description": "Privilege escalation to export data beyond authorized scope",
                    "mitigation": "Enforce role-based access control on data export endpoints"
                },
                {
                    "id": "STRIDE-I-GDPR-003",
                    "title": "PII Exposure in Logs",
                    "category": "Information Disclosure",
                    "severity": "MEDIUM",
                    "cvss_score": 5.5,
                    "description": "Personal Identifiable Information logged in plaintext",
                    "mitigation": "Implement PII masking/redaction in logging pipelines"
                }
            ],
            "financial": [
                {
                    "id": "STRIDE-T-FIN-001",
                    "title": "Financial Transaction Tampering",
                    "category": "Tampering",
                    "severity": "CRITICAL",
                    "cvss_score": 9.0,
                    "description": "Attacker could modify transaction amounts or recipients",
                    "mitigation": "Implement cryptographic signing and audit trails for all transactions"
                },
                {
                    "id": "STRIDE-R-FIN-002",
                    "title": "Transaction Repudiation",
                    "category": "Repudiation",
                    "severity": "HIGH",
                    "cvss_score": 7.5,
                    "description": "Users could deny legitimate financial transactions",
                    "mitigation": "Implement immutable audit logs with timestamps and digital signatures"
                }
            ],
            "event_driven": [
                {
                    "id": "STRIDE-T-EVT-001",
                    "title": "Event Tampering in Queue",
                    "category": "Tampering",
                    "severity": "HIGH",
                    "cvss_score": 7.0,
                    "description": "Attacker could modify events in message queue before consumption",
                    "mitigation": "Sign events with HMAC and validate signatures on consumption"
                },
                {
                    "id": "STRIDE-R-EVT-002",
                    "title": "Event Replay Attack",
                    "category": "Repudiation",
                    "severity": "MEDIUM",
                    "cvss_score": 6.0,
                    "description": "Attacker could replay old events to trigger unintended actions",
                    "mitigation": "Implement event deduplication using unique event IDs and timestamps"
                }
            ],
            "data_lifecycle": [
                {
                    "id": "STRIDE-I-DATA-001",
                    "title": "Unencrypted Backup Exposure",
                    "category": "Information Disclosure",
                    "severity": "CRITICAL",
                    "cvss_score": 9.0,
                    "description": "Database backups stored without encryption",
                    "mitigation": "Enable encryption at rest for all backups (e.g., PostgreSQL encrypted backups)"
                },
                {
                    "id": "STRIDE-E-DATA-002",
                    "title": "Data Retention Policy Bypass",
                    "category": "Elevation of Privilege",
                    "severity": "HIGH",
                    "cvss_score": 7.5,
                    "description": "Attacker could bypass data retention policies to access deleted data",
                    "mitigation": "Implement secure data deletion (overwrite, not just mark as deleted)"
                },
                {
                    "id": "STRIDE-T-DATA-003",
                    "title": "Point-in-Time Recovery (PITR) Abuse",
                    "category": "Tampering",
                    "severity": "MEDIUM",
                    "cvss_score": 6.0,
                    "description": "Unauthorized PITR operations could restore deleted sensitive data",
                    "mitigation": "Restrict PITR permissions to DBA role only, audit all restore operations"
                },
                {
                    "id": "STRIDE-I-DATA-004",
                    "title": "Data Export Exfiltration",
                    "category": "Information Disclosure",
                    "severity": "HIGH",
                    "cvss_score": 7.0,
                    "description": "Bulk data export features could be abused for exfiltration",
                    "mitigation": "Rate-limit exports, require MFA for bulk operations, log all exports"
                }
            ]
        }

    def _detect_bounded_contexts(self, project_path: Path) -> List[BoundedContext]:
        """
        NEW (v2.1.7): Detect bounded contexts in project.

        Heuristics:
        - Top-level directories with common suffixes (.api, .service, .domain)
        - Presence of Controllers/Endpoints (API boundary)
        - Presence of Domain/ or Models/ (domain logic)

        Args:
            project_path: Path to project root

        Returns:
            List of BoundedContext objects
        """
        contexts = []

        # Heuristic 1: Top-level directories with suffixes
        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check for common suffixes
                if any(suffix in item.name.lower() for suffix in ['.api', '.service', '.domain', '-api', '-service']):
                    context = BoundedContext(
                        name=item.name,
                        path=item,
                        description=f"Bounded context detected from directory structure"
                    )

                    # Analyze context characteristics
                    context.has_events = self._has_events(item)
                    context.has_gdpr_data = self._has_gdpr_data(item)
                    context.has_financial_data = self._has_financial_data(item)

                    contexts.append(context)

        # Heuristic 2: If no contexts found, treat whole project as single context
        if not contexts:
            context = BoundedContext(
                name=project_path.name,
                path=project_path,
                description="Single-context project"
            )
            context.has_events = self._has_events(project_path)
            context.has_gdpr_data = self._has_gdpr_data(project_path)
            context.has_financial_data = self._has_financial_data(project_path)
            contexts.append(context)

        logger.info(f"Detected {len(contexts)} bounded context(s)")
        return contexts

    def _has_events(self, context_path: Path) -> bool:
        """Check if context uses event-driven architecture"""
        # Look for event-related patterns
        patterns = [
            r'class \w+Event',
            r'EventHandler',
            r'Publish\w+Event',
            r'IEventBus',
            r'@Event',
            r'RabbitMQ|Kafka|EventGrid'
        ]

        for file in context_path.rglob("*.cs"):
            try:
                content = file.read_text()
                if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                    return True
            except:
                pass

        return False

    def _has_gdpr_data(self, context_path: Path) -> bool:
        """Check if context handles GDPR-regulated data"""
        # Look for GDPR-related keywords
        keywords = [
            'gdpr', 'lgpd', 'vdpo', 'datasubject', 'consent', 'pii',
            'personaldata', 'righttobeforget', 'dataportability', 'dsar'
        ]

        for file in context_path.rglob("*.cs"):
            try:
                content = file.read_text().lower()
                if any(keyword in content for keyword in keywords):
                    return True
            except:
                pass

        return False

    def _has_financial_data(self, context_path: Path) -> bool:
        """Check if context handles financial data"""
        keywords = [
            'payment', 'transaction', 'invoice', 'billing', 'financial',
            'stripe', 'paypal', 'creditcard', 'money', 'currency'
        ]

        for file in context_path.rglob("*.cs"):
            try:
                content = file.read_text().lower()
                if any(keyword in content for keyword in keywords):
                    return True
            except:
                pass

        return False

    def analyze(self, project_path: Path, decisions: Dict) -> Dict:
        """
        Run STRIDE analysis.

        NEW (v2.1.7): Bounded context-aware threat modeling.
        Analyzes each bounded context individually and adds domain-specific threats.

        Args:
            project_path: Path to project root
            decisions: Extracted architecture decisions

        Returns:
            Dict with threats categorized by STRIDE
        """
        if not self.enabled:
            return {"status": "skipped"}

        # NEW (v2.1.7): Detect bounded contexts
        bounded_contexts = self._detect_bounded_contexts(project_path)

        # Standard STRIDE analysis (generic threats)
        threats = {
            "spoofing": self._detect_spoofing(project_path),
            "tampering": self._detect_tampering(project_path),
            "repudiation": self._detect_repudiation(project_path),
            "information_disclosure": self._detect_info_disclosure(project_path),
            "denial_of_service": self._detect_dos(project_path),
            "elevation_of_privilege": self._detect_eop(project_path)
        }

        # NEW (v2.1.7): Add context-specific threats
        for context in bounded_contexts:
            logger.info(f"Analyzing threats for bounded context: {context.name}")

            # GDPR threats
            if context.has_gdpr_data:
                logger.info(f"  {context.name}: Adding GDPR-specific threats")
                for threat_template in self.threat_templates['gdpr']:
                    threat = threat_template.copy()
                    threat['context'] = context.name
                    threat['file'] = str(context.path)
                    category_key = threat['category'].lower().replace(' ', '_')
                    if category_key in threats:
                        threats[category_key].append(threat)

            # Financial threats
            if context.has_financial_data:
                logger.info(f"  {context.name}: Adding financial-specific threats")
                for threat_template in self.threat_templates['financial']:
                    threat = threat_template.copy()
                    threat['context'] = context.name
                    threat['file'] = str(context.path)
                    category_key = threat['category'].lower().replace(' ', '_')
                    if category_key in threats:
                        threats[category_key].append(threat)

            # Event-driven threats
            if context.has_events:
                logger.info(f"  {context.name}: Adding event-driven threats")
                for threat_template in self.threat_templates['event_driven']:
                    threat = threat_template.copy()
                    threat['context'] = context.name
                    threat['file'] = str(context.path)
                    category_key = threat['category'].lower().replace(' ', '_')
                    if category_key in threats:
                        threats[category_key].append(threat)

        # NEW (v2.1.7): Add data lifecycle threats (always applicable)
        logger.info("Adding data lifecycle threats")
        for threat_template in self.threat_templates['data_lifecycle']:
            threat = threat_template.copy()
            threat['context'] = 'data_lifecycle'
            threat['file'] = str(project_path)
            category_key = threat['category'].lower().replace(' ', '_')
            if category_key in threats:
                threats[category_key].append(threat)

        all_threats = []
        for category, threats_list in threats.items():
            all_threats.extend(threats_list)

        critical = [t for t in all_threats if t['severity'] == 'CRITICAL']
        high = [t for t in all_threats if t['severity'] == 'HIGH']

        logger.info(f"Threat modeling complete: {len(all_threats)} threats ({len(critical)} CRITICAL, {len(high)} HIGH)")

        return {
            "threats": threats,
            "total": len(all_threats),
            "critical": len(critical),
            "high": len(high),
            "bounded_contexts": [
                {
                    "name": ctx.name,
                    "has_events": ctx.has_events,
                    "has_gdpr_data": ctx.has_gdpr_data,
                    "has_financial_data": ctx.has_financial_data
                }
                for ctx in bounded_contexts
            ],
            "severity_distribution": {
                "CRITICAL": len(critical),
                "HIGH": len(high),
                "MEDIUM": len([t for t in all_threats if t['severity'] == 'MEDIUM']),
                "LOW": len([t for t in all_threats if t['severity'] == 'LOW'])
            }
        }

    def _detect_spoofing(self, path: Path) -> List[Dict]:
        """Detect spoofing threats"""
        threats = []
        for file in path.rglob("*.py"):
            try:
                content = file.read_text()
                if re.search(r'jwt\.decode\([^,]+,\s*verify=False', content):
                    threats.append({
                        "id": f"THREAT-SPOOF-{len(threats)+1:03d}",
                        "title": "JWT Signature Verification Disabled",
                        "severity": "HIGH",
                        "cvss_score": 7.5,
                        "file": str(file),
                        "mitigation": "Enable JWT signature verification"
                    })
            except:
                pass
        return threats

    def _detect_tampering(self, path: Path) -> List[Dict]:
        return []

    def _detect_repudiation(self, path: Path) -> List[Dict]:
        return []

    def _detect_info_disclosure(self, path: Path) -> List[Dict]:
        threats = []
        for file in path.rglob("*"):
            try:
                content = file.read_text()
                if re.search(r'(password|secret|api_key)\s*=\s*["\'][^"\']+["\']', content):
                    threats.append({
                        "id": f"THREAT-INFO-{len(threats)+1:03d}",
                        "title": "Hardcoded Secret Detected",
                        "severity": "CRITICAL",
                        "cvss_score": 9.0,
                        "file": str(file),
                        "mitigation": "Move secrets to environment variables"
                    })
            except:
                pass
        return threats

    def _detect_dos(self, path: Path) -> List[Dict]:
        return []

    def _detect_eop(self, path: Path) -> List[Dict]:
        return []


def main():
    import argparse, json
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path")
    args = parser.parse_args()

    config = {"threat_modeling": {"enabled": True, "escalation_threshold": 7.0}}
    modeler = ThreatModeler(config)
    result = modeler.analyze(Path(args.project_path), {})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
