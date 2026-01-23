#!/usr/bin/env python3
"""
Threat Modeler - STRIDE threat analysis
Uses security-guidance plugin patterns.

References:
- awesome-copilot: threat-model-generator.prompt
- claude-plugins-official: security-guidance
"""

import sys
import re
from pathlib import Path
from typing import Dict, List
import yaml

sys.path.insert(0, '.claude/lib/python')
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class ThreatModeler:
    """Perform STRIDE threat modeling"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config['threat_modeling']['enabled']
        self.escalation_threshold = config['threat_modeling']['escalation_threshold']

    def analyze(self, project_path: Path, decisions: Dict) -> Dict:
        """Run STRIDE analysis"""
        if not self.enabled:
            return {"status": "skipped"}

        threats = {
            "spoofing": self._detect_spoofing(project_path),
            "tampering": self._detect_tampering(project_path),
            "repudiation": self._detect_repudiation(project_path),
            "information_disclosure": self._detect_info_disclosure(project_path),
            "denial_of_service": self._detect_dos(project_path),
            "elevation_of_privilege": self._detect_eop(project_path)
        }

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
