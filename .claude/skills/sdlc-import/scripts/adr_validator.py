#!/usr/bin/env python3
"""
ADR Claim Validator - Cross-reference ADR claims against code
Validates that architectural decisions are actually implemented.

NEW (v2.1.7): ADR Reconciliation - Detect existing ADRs and avoid duplicates
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="sdlc-import", phase=0)


@dataclass
class ExistingADR:
    """Represents an existing ADR found in the project"""
    path: Path
    format: str  # "markdown", "yaml", "asciidoc"
    title: str
    content: str
    id: Optional[str] = None
    status: Optional[str] = None


@dataclass
class ReconciliationResult:
    """Result of ADR reconciliation"""
    duplicate: List[Dict]  # ADRs já existentes (skip generation)
    enrich: List[Dict]  # ADRs que podem ser enriquecidos
    new: List[Dict]  # ADRs novos (gerar)
    index: Dict  # Cross-reference index


class ADRValidator:
    """Validate ADR claims against codebase"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('adr_validation', {}).get('enabled', True)
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> Dict:
        """Load validation rules from config"""
        rules_file = Path(__file__).parent.parent / "config" / "adr_validation_rules.yml"

        if not rules_file.exists():
            logger.warning(f"Validation rules file not found: {rules_file}")
            return self._get_default_rules()

        with open(rules_file, 'r') as f:
            return yaml.safe_load(f)

    def _get_default_rules(self) -> Dict:
        """Return default validation rules if config file not found"""
        return {
            "validation_types": {
                "coverage_claims": {
                    "lgpd": {
                        "method_pattern": "(RequestDataDeletion|RequestDataPortability|RevokeConsent|RequestDataAccess)",
                        "file_patterns": [
                            "*DataSubjectRight*.cs",
                            "*LGPDCompliance*.cs",
                            "*ConsentManagement*.cs"
                        ],
                        "expected_methods": 8,
                        "tolerance_percentage": 10
                    }
                },
                "technology_claims": {
                    "rls": {
                        "patterns": [
                            "CREATE POLICY",
                            "ENABLE ROW LEVEL SECURITY"
                        ],
                        "file_patterns": [
                            "**/*.sql",
                            "**/Migrations/*.cs"
                        ],
                        "minimum_occurrences": 1
                    }
                }
            }
        }

    def detect_existing_adrs(self, project_path: Path) -> List[ExistingADR]:
        """
        Detect existing ADRs in the project.

        Searches for ADRs in common locations:
        - docs/adr/*.md
        - docs/decisions/*.md
        - .adr/*.md
        - decisions/*.md
        - Also checks for .adr-dir config file

        Args:
            project_path: Path to project root

        Returns:
            List of ExistingADR objects
        """
        with log_operation("detect_existing_adrs", logger):
            existing_adrs = []

            # Check for .adr-dir config file
            adr_dir_config = project_path / ".adr-dir"
            custom_dir = None
            if adr_dir_config.exists():
                try:
                    custom_dir = adr_dir_config.read_text().strip()
                    logger.info(f"Found .adr-dir config: {custom_dir}")
                except Exception as e:
                    logger.warning(f"Failed to read .adr-dir: {e}")

            # Define search patterns
            search_patterns = [
                "**/docs/adr/*.md",
                "**/docs/decisions/*.md",
                "**/.adr/*.md",
                "**/decisions/*.md",
                "**/architecture/decisions/*.md",
            ]

            # Add custom directory if found
            if custom_dir:
                search_patterns.append(f"**/{custom_dir}/*.md")

            # Search for existing ADRs
            for pattern in search_patterns:
                for adr_file in project_path.rglob(pattern):
                    try:
                        existing_adr = self._parse_existing_adr(adr_file, project_path)
                        if existing_adr:
                            existing_adrs.append(existing_adr)
                    except Exception as e:
                        logger.warning(f"Failed to parse {adr_file}: {e}")

            logger.info(
                "ADR detection complete",
                extra={
                    "existing_adrs_found": len(existing_adrs),
                    "search_patterns": search_patterns
                }
            )

            return existing_adrs

    def _parse_existing_adr(self, file_path: Path, project_root: Path) -> Optional[ExistingADR]:
        """
        Parse an existing ADR file.

        Supports:
        - Markdown (most common)
        - YAML (if already SDLC Agêntico format)

        Args:
            file_path: Path to ADR file
            project_root: Project root path

        Returns:
            ExistingADR object or None if parsing fails
        """
        content = file_path.read_text()

        # Detect format
        if file_path.suffix == '.md':
            return self._parse_markdown_adr(file_path, content, project_root)
        elif file_path.suffix in ['.yml', '.yaml']:
            return self._parse_yaml_adr(file_path, content, project_root)

        return None

    def _parse_markdown_adr(self, file_path: Path, content: str, project_root: Path) -> Optional[ExistingADR]:
        """Parse Markdown ADR (common format)"""
        # Extract title (usually first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem

        # Try to extract ID from filename (e.g., "0001-use-postgres.md")
        id_match = re.match(r'^(\d+)', file_path.stem)
        adr_id = f"ADR-{id_match.group(1)}" if id_match else None

        # Try to extract status
        status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', content, re.IGNORECASE)
        status = status_match.group(1) if status_match else None

        return ExistingADR(
            path=file_path.relative_to(project_root),
            format="markdown",
            title=title,
            content=content,
            id=adr_id,
            status=status
        )

    def _parse_yaml_adr(self, file_path: Path, content: str, project_root: Path) -> Optional[ExistingADR]:
        """Parse YAML ADR (SDLC Agêntico format)"""
        try:
            data = yaml.safe_load(content)
            return ExistingADR(
                path=file_path.relative_to(project_root),
                format="yaml",
                title=data.get('title', file_path.stem),
                content=content,
                id=data.get('id'),
                status=data.get('status')
            )
        except Exception as e:
            logger.warning(f"Failed to parse YAML ADR {file_path}: {e}")
            return None

    def reconcile_adrs(self, existing_adrs: List[ExistingADR], inferred_adrs: List[Dict], similarity_threshold: float = 0.8) -> ReconciliationResult:
        """
        Reconcile existing ADRs with newly inferred ADRs.

        Compares ADRs by title/topic similarity and categorizes them:
        - duplicate: ADR already exists (skip generation)
        - enrich: Existing ADR can be enriched with analysis
        - new: Truly new ADR (generate)

        Args:
            existing_adrs: List of ExistingADR found in project
            inferred_adrs: List of ADR dicts inferred from code
            similarity_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            ReconciliationResult with categorized ADRs
        """
        with log_operation("reconcile_adrs", logger):
            duplicate = []
            enrich = []
            new = []
            index = {}

            for inferred in inferred_adrs:
                inferred_title = inferred.get('title', '')
                best_match = None
                best_similarity = 0.0

                # Compare with all existing ADRs
                for existing in existing_adrs:
                    similarity = self._calculate_similarity(inferred_title, existing.title)

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = existing

                # Categorize based on similarity
                if best_similarity >= similarity_threshold:
                    # Duplicate or enrichment candidate
                    if best_match.format == "yaml":
                        # Already in SDLC format, skip
                        duplicate.append({
                            "inferred": inferred,
                            "existing": {
                                "path": str(best_match.path),
                                "id": best_match.id,
                                "title": best_match.title,
                                "format": best_match.format
                            },
                            "similarity": best_similarity,
                            "action": "skip"
                        })
                    else:
                        # Markdown format, can enrich
                        enrich.append({
                            "inferred": inferred,
                            "existing": {
                                "path": str(best_match.path),
                                "title": best_match.title,
                                "format": best_match.format
                            },
                            "similarity": best_similarity,
                            "action": "enrich"
                        })

                    # Add to cross-reference index
                    index[inferred.get('id', '')] = {
                        "original": str(best_match.path),
                        "format": best_match.format,
                        "status": "reconciled",
                        "similarity": best_similarity
                    }
                else:
                    # Truly new ADR
                    new.append(inferred)

            logger.info(
                "ADR reconciliation complete",
                extra={
                    "total_inferred": len(inferred_adrs),
                    "duplicate": len(duplicate),
                    "enrich": len(enrich),
                    "new": len(new)
                }
            )

            return ReconciliationResult(
                duplicate=duplicate,
                enrich=enrich,
                new=new,
                index=index
            )

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using SequenceMatcher.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0-1.0)
        """
        # Normalize texts
        norm1 = text1.lower().strip()
        norm2 = text2.lower().strip()

        # Calculate similarity
        return SequenceMatcher(None, norm1, norm2).ratio()

    def validate(self, project_path: Path, extracted_adrs: List[Dict]) -> Dict:
        """Main validation entry point"""
        with log_operation("validate_adrs", logger):
            validation_results = []

            for adr in extracted_adrs:
                result = self._validate_single_adr(project_path, adr)
                validation_results.append(result)

            # Calculate overall validation score
            total_claims = sum(r['claims_count'] for r in validation_results)
            validated_claims = sum(r['validated_count'] for r in validation_results)
            validation_rate = validated_claims / total_claims if total_claims > 0 else 0

            logger.info(
                "ADR validation complete",
                extra={
                    "total_adrs": len(extracted_adrs),
                    "total_claims": total_claims,
                    "validated_claims": validated_claims,
                    "validation_rate": validation_rate
                }
            )

            return {
                "results": validation_results,
                "summary": {
                    "total_adrs": len(extracted_adrs),
                    "total_claims": total_claims,
                    "validated_claims": validated_claims,
                    "validation_rate": validation_rate
                }
            }

    def _validate_single_adr(self, project_path: Path, adr: Dict) -> Dict:
        """Validate a single ADR's claims"""
        adr_id = adr.get('id', 'UNKNOWN')
        title = adr.get('title', '')

        # Extract claims from ADR
        claims = self._extract_claims(adr)

        validation_results = []
        for claim in claims:
            validated = self._validate_claim(project_path, claim)
            validation_results.append(validated)

        validated_count = sum(1 for v in validation_results if v['is_valid'])

        return {
            "adr_id": adr_id,
            "title": title,
            "claims_count": len(claims),
            "validated_count": validated_count,
            "validation_rate": validated_count / len(claims) if claims else 0,
            "claims": validation_results
        }

    def _extract_claims(self, adr: Dict) -> List[Dict]:
        """Extract validatable claims from ADR"""
        claims = []

        # Combine decision and rationale text
        decision_text = adr.get('decision', '') + ' ' + adr.get('rationale', '')

        # Coverage claim pattern (e.g., "LGPD coverage 95%")
        coverage_match = re.search(r'(\w+)\s+coverage\s+(\d+)%', decision_text, re.IGNORECASE)
        if coverage_match:
            framework = coverage_match.group(1)
            percentage = int(coverage_match.group(2))
            claims.append({
                "type": "coverage",
                "framework": framework,
                "claimed_percentage": percentage,
                "text": coverage_match.group(0)
            })

        # Technology claim pattern (e.g., "uses PostgreSQL Row-Level Security")
        tech_patterns = [
            (r'(uses?|implements?)\s+(?:\w+\s+)?(Row[- ]Level Security|RLS)', "Row-Level Security"),
            (r'(uses?|implements?)\s+(?:\w+\s+)?(JWT|JSON Web Token)', "JWT"),
            (r'(uses?|implements?|with)\s+(?:\w+\s+)?(multi[- ]tenant|multi-tenancy)', "Multi-Tenancy")
        ]

        for pattern, tech_name in tech_patterns:
            tech_match = re.search(pattern, decision_text, re.IGNORECASE)
            if tech_match:
                claims.append({
                    "type": "technology",
                    "technology": tech_name,
                    "text": tech_match.group(0)
                })

        return claims

    def _validate_claim(self, project_path: Path, claim: Dict) -> Dict:
        """Validate a specific claim against codebase"""
        claim_type = claim.get('type')

        if claim_type == "coverage":
            return self._validate_coverage_claim(project_path, claim)
        elif claim_type == "technology":
            return self._validate_technology_claim(project_path, claim)
        else:
            return {
                "claim": claim,
                "is_valid": False,
                "reason": "Unknown claim type",
                "confidence": 0.0
            }

    def _validate_coverage_claim(self, project_path: Path, claim: Dict) -> Dict:
        """Validate coverage claims (e.g., 'LGPD coverage 95%')"""
        framework = claim.get('framework', '').upper()
        claimed_percentage = claim.get('claimed_percentage', 0)

        # LGPD validation
        if framework == "LGPD":
            # Check for Data Subject Rights implementation
            lgpd_files = list(project_path.rglob("*DataSubjectRight*.cs"))
            lgpd_files.extend(project_path.rglob("*LGPDCompliance*.cs"))
            lgpd_files.extend(project_path.rglob("*ConsentManagement*.cs"))

            # Check for LGPD-specific methods (use set to count unique methods)
            lgpd_methods_found = set()
            for file in lgpd_files:
                try:
                    content = file.read_text()
                    # Find all LGPD Art. 18 rights implementations
                    matches = re.findall(
                        r'(RequestDataDeletion|RequestDataPortability|RevokeConsent|RequestDataAccess|RequestDataRectification|RequestDataAnonymization|RequestDataOpposition)',
                        content
                    )
                    lgpd_methods_found.update(matches)
                except:
                    pass

            # Estimate coverage based on unique methods found
            expected_methods = 8  # LGPD Art. 18 has 8 rights
            lgpd_methods = len(lgpd_methods_found)
            actual_coverage = (lgpd_methods / expected_methods) * 100 if expected_methods > 0 else 0

            is_valid = abs(actual_coverage - claimed_percentage) <= 10  # 10% tolerance

            return {
                "claim": claim,
                "is_valid": is_valid,
                "actual_coverage": actual_coverage,
                "claimed_coverage": claimed_percentage,
                "evidence_files": [str(f.relative_to(project_path)) for f in lgpd_files[:10]],
                "confidence": 0.8 if is_valid else 0.3
            }

        # ISO 27001 validation
        elif framework == "ISO":
            iso_files = list(project_path.rglob("*Security*.cs"))
            iso_files.extend(project_path.rglob("*Audit*.cs"))
            iso_files.extend(project_path.rglob("*AccessControl*.cs"))

            # Count security controls
            controls_found = len(iso_files)
            expected_controls = 114  # ISO 27001:2013 Annex A has 114 controls
            actual_coverage = (controls_found / expected_controls) * 100

            is_valid = abs(actual_coverage - claimed_percentage) <= 15

            return {
                "claim": claim,
                "is_valid": is_valid,
                "actual_coverage": actual_coverage,
                "claimed_coverage": claimed_percentage,
                "evidence_files": [str(f.relative_to(project_path)) for f in iso_files[:10]],
                "confidence": 0.6 if is_valid else 0.2
            }

        return {
            "claim": claim,
            "is_valid": False,
            "reason": f"No validation rule for {framework}",
            "confidence": 0.0
        }

    def _validate_technology_claim(self, project_path: Path, claim: Dict) -> Dict:
        """Validate technology usage claims"""
        technology = claim.get('technology', '')

        # PostgreSQL RLS validation
        if "Row-Level Security" in technology or "RLS" in technology:
            rls_files = []

            # Check SQL files
            for sql_file in project_path.rglob("**/*.sql"):
                try:
                    content = sql_file.read_text()
                    if re.search(r'CREATE POLICY|ALTER TABLE.*ENABLE ROW LEVEL SECURITY', content, re.IGNORECASE):
                        rls_files.append(sql_file)
                except:
                    pass

            # Check C# migration files
            for cs_file in project_path.rglob("**/Migrations/*.cs"):
                try:
                    content = cs_file.read_text()
                    if re.search(r'ENABLE ROW LEVEL SECURITY|CREATE POLICY', content):
                        rls_files.append(cs_file)
                except:
                    pass

            is_valid = len(rls_files) > 0

            return {
                "claim": claim,
                "is_valid": is_valid,
                "evidence_files": [str(f.relative_to(project_path)) for f in rls_files],
                "confidence": 0.95 if is_valid else 0.1
            }

        # JWT validation
        elif "JWT" in technology or "JSON Web Token" in technology:
            jwt_files = []

            # Check for JWT usage
            for code_file in project_path.rglob("**/*.cs"):
                try:
                    content = code_file.read_text()
                    if re.search(r'JwtSecurityTokenHandler|jwt\.(encode|decode)', content, re.IGNORECASE):
                        jwt_files.append(code_file)
                except:
                    pass

            is_valid = len(jwt_files) > 0

            return {
                "claim": claim,
                "is_valid": is_valid,
                "evidence_files": [str(f.relative_to(project_path)) for f in jwt_files[:5]],
                "confidence": 0.90 if is_valid else 0.2
            }

        # Multi-tenancy validation
        elif any(term in technology for term in ["Multi-Tenant", "Multi-tenancy", "Multi-Tenancy"]):
            tenant_files = []
            tenant_occurrences = 0

            # Check for tenant_id patterns in all code files
            for code_file in project_path.rglob("**/*"):
                if code_file.suffix in ['.cs', '.py', '.java', '.ts', '.js']:
                    try:
                        content = code_file.read_text()
                        matches = re.findall(r'tenant_?[iI]d|TenantId|X-Tenant-Id', content, re.IGNORECASE)
                        if len(matches) > 0:
                            tenant_files.append(code_file)
                            tenant_occurrences += len(matches)
                    except:
                        pass

            is_valid = tenant_occurrences >= 3  # At least 3 occurrences for validation

            return {
                "claim": claim,
                "is_valid": is_valid,
                "occurrences": tenant_occurrences,
                "evidence_files": [str(f.relative_to(project_path)) for f in tenant_files[:5]],
                "confidence": 0.85 if is_valid else 0.3
            }

        return {
            "claim": claim,
            "is_valid": False,
            "reason": f"No validation rule for {technology}",
            "confidence": 0.0
        }


if __name__ == "__main__":
    # Test ADR validation
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Validate ADR claims against codebase")
    parser.add_argument("project_path", type=Path, help="Project directory")
    parser.add_argument("--adrs-file", type=Path, help="ADRs JSON file")
    parser.add_argument("--config", type=Path, help="Config file")
    args = parser.parse_args()

    config = {}
    if args.config and args.config.exists():
        with open(args.config) as f:
            config = yaml.safe_load(f)

    validator = ADRValidator(config)

    # Load ADRs
    adrs = []
    if args.adrs_file and args.adrs_file.exists():
        with open(args.adrs_file) as f:
            data = json.load(f)
            adrs = data.get('decisions', [])

    result = validator.validate(args.project_path, adrs)
    print(json.dumps(result, indent=2))
