"""
Post-Import Validators and Fixers
Automatically detect and fix common issues in imported artifacts.
"""

from .adr_evidence_fixer import ADREvidenceFixer
from .tech_debt_fixer import TechDebtFixer
from .diagram_quality_fixer import DiagramQualityFixer
from .artifact_completeness_fixer import ArtifactCompletenessFixer

__all__ = [
    'ADREvidenceFixer',
    'TechDebtFixer',
    'DiagramQualityFixer',
    'ArtifactCompletenessFixer'
]
