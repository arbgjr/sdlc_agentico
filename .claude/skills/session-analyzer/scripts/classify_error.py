#!/usr/bin/env python3
"""
Classify Error - Classifica erro como bug do SDLC ou problema do projeto.

Usage:
    python classify_error.py --error-json errors.json
"""

import argparse
import json
import re
import sys
from typing import Dict, List


# Padrões que indicam bug do SDLC Agêntico
SDLC_BUG_PATTERNS = [
    # Erros de skills
    r"\.claude/skills/.*/scripts/.*\.py.*Error",
    r"\.claude/hooks/.*\.sh.*failed",
    r"\.claude/commands/.*\.md.*not found",

    # Erros de estrutura
    r"\.agentic_sdlc/.*not found",
    r"manifest\.json.*not found",
    r"gate-.*\.yml.*not found",

    # Erros de dependências do framework
    r"sdlc_logging.*ImportError",
    r"logging_utils\.sh.*No such file",
    r"fallback\.sh.*command not found",

    # Erros de automação
    r"gate-check.*failed",
    r"phase-commit.*failed",
    r"session-analyzer.*failed",
    r"rag-curator.*failed",
    r"github-sync.*failed",
    r"github-projects.*failed",

    # Erros de configuração do framework
    r"SDLC_.*not set",
    r"settings\.json.*parse error",

    # Comandos internos
    r"update-phase.*command not found",
    r"configure-fields.*failed",
    r"create_issues_from_tasks.*failed"
]

# Padrões que indicam problema do projeto do usuário
PROJECT_ISSUE_PATTERNS = [
    # Build/compile
    r"compilation error",
    r"syntax error.*\.py",
    r"syntax error.*\.js",
    r"ImportError.*module",
    r"ModuleNotFoundError",

    # Tests
    r"test.*failed",
    r"assertion.*failed",

    # Linting
    r"lint.*error",
    r"type.*error",

    # Dependencies
    r"npm.*ERR",
    r"pip.*error",
    r"package.*not found",

    # Git
    r"git.*merge conflict",
    r"git.*authentication failed",

    # Infrastructure
    r"docker.*failed",
    r"kubernetes.*error",
    r"terraform.*error"
]


def classify_error(error: Dict) -> Dict:
    """
    Classifica um erro.

    Returns:
        {
            "classification": "sdlc_bug" | "project_issue" | "unknown",
            "confidence": float,
            "reason": str,
            "owner": "arbgjr" | "user"
        }
    """
    message = error.get("message", "")
    script = error.get("script", "")
    skill = error.get("skill", "")

    full_context = f"{message} {script} {skill}"

    # Checar padrões SDLC
    sdlc_matches = []
    for pattern in SDLC_BUG_PATTERNS:
        if re.search(pattern, full_context, re.IGNORECASE):
            sdlc_matches.append(pattern)

    # Checar padrões projeto
    project_matches = []
    for pattern in PROJECT_ISSUE_PATTERNS:
        if re.search(pattern, full_context, re.IGNORECASE):
            project_matches.append(pattern)

    # Decidir classificação
    if sdlc_matches and not project_matches:
        return {
            "classification": "sdlc_bug",
            "confidence": 0.9 if len(sdlc_matches) > 1 else 0.7,
            "reason": f"Matched SDLC patterns: {', '.join(sdlc_matches[:2])}",
            "owner": "arbgjr",
            "action": "report_to_owner"
        }

    elif project_matches and not sdlc_matches:
        return {
            "classification": "project_issue",
            "confidence": 0.9 if len(project_matches) > 1 else 0.7,
            "reason": f"Matched project patterns: {', '.join(project_matches[:2])}",
            "owner": "user",
            "action": "notify_user"
        }

    elif sdlc_matches and project_matches:
        # Ambos - priorizar SDLC se script é do framework
        if ".claude/" in script or ".agentic_sdlc/" in script:
            return {
                "classification": "sdlc_bug",
                "confidence": 0.6,
                "reason": "Mixed patterns but script is from framework",
                "owner": "arbgjr",
                "action": "report_to_owner"
            }
        else:
            return {
                "classification": "project_issue",
                "confidence": 0.6,
                "reason": "Mixed patterns but script is from project",
                "owner": "user",
                "action": "notify_user"
            }

    else:
        return {
            "classification": "unknown",
            "confidence": 0.0,
            "reason": "No patterns matched",
            "owner": "unknown",
            "action": "notify_user"  # Safe default
        }


def main():
    parser = argparse.ArgumentParser(description="Classifica erros")
    parser.add_argument("--error-json", required=True, help="JSON com erros")
    parser.add_argument("--output", default="classified_errors.json", help="Output file")
    args = parser.parse_args()

    # Ler erros
    with open(args.error_json) as f:
        errors = json.load(f)

    if not isinstance(errors, list):
        errors = [errors]

    # Classificar cada erro
    classified = []
    for error in errors:
        classification = classify_error(error)
        classified.append({
            **error,
            "classification": classification
        })

    # Agrupar por classificação
    sdlc_bugs = [e for e in classified if e["classification"]["classification"] == "sdlc_bug"]
    project_issues = [e for e in classified if e["classification"]["classification"] == "project_issue"]
    unknown = [e for e in classified if e["classification"]["classification"] == "unknown"]

    # Salvar resultado
    result = {
        "summary": {
            "total_errors": len(classified),
            "sdlc_bugs": len(sdlc_bugs),
            "project_issues": len(project_issues),
            "unknown": len(unknown)
        },
        "sdlc_bugs": sdlc_bugs,
        "project_issues": project_issues,
        "unknown": unknown
    }

    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)

    # Output resumo
    print(f"\n📊 Classificação de Erros:")
    print(f"   Total: {result['summary']['total_errors']}")
    print(f"   🐛 SDLC Bugs: {result['summary']['sdlc_bugs']}")
    print(f"   ⚠️  Project Issues: {result['summary']['project_issues']}")
    print(f"   ❓ Unknown: {result['summary']['unknown']}")
    print(f"\n   Resultado salvo em: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
