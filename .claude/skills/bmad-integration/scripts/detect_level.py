#!/usr/bin/env python3
"""
BMAD complexity level detector.

Classifies an incoming request into one of 4 SDLC complexity levels
(0..3) and emits the suggested command + agent routing. The decision
is deterministic given the same inputs, explained, and auditable —
never a black box.

Classification heuristics (intentionally simple so the output is
debuggable):

Level 0 — Quick flow (bug fix, typo, one-liner)
  keywords: fix, bug, typo, broken, crash, revert
  AND scope <= 5 files touched
  AND no new public endpoint / auth / crypto change

Level 1 — Feature in existing service
  keywords: add, feature, extend, refactor
  AND single service affected
  AND no new persistent data model

Level 2 — New product/service (BMAD Method full run)
  keywords: new service, new product, MVP, system, platform
  OR introduces a new bounded context
  OR new external integration

Level 3 — Enterprise (compliance/multi-team/critical)
  keywords: compliance, LGPD, GDPR, PCI, SOX, regulated, critical,
            multi-team, migration
  OR touches PII/auth/payment/crypto per security_by_design
  OR complexity flag explicitly set by user

Escalation rules (override detected level upward):
  - auth/authz change detected → min Level 2
  - PII exposure detected → min Level 2
  - new public endpoint → min Level 2
  - CVSS >= 7.0 mentioned → min Level 3

Usage:
  echo "description" | python3 detect_level.py
  python3 detect_level.py --text "rewrite billing system"
  python3 detect_level.py --text "..." --files file1.py file2.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Detection:
    level: int
    level_name: str
    suggested_command: str
    reasoning: list[str] = field(default_factory=list)
    triggered_escalations: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    suggested_agents: list[str] = field(default_factory=list)


LEVEL_META: dict[int, dict[str, str]] = {
    0: {"name": "Quick Flow", "command": "/quick-fix"},
    1: {"name": "Feature", "command": "/new-feature"},
    2: {"name": "BMAD Method", "command": "/sdlc-start"},
    3: {"name": "Enterprise", "command": "/sdlc-start"},
}

AGENT_ROUTING: dict[int, list[str]] = {
    0: ["code-author", "test-author", "code-reviewer"],
    1: [
        "requirements-analyst",
        "code-author",
        "test-author",
        "code-reviewer",
        "qa-analyst",
    ],
    2: [
        "intake-analyst",
        "product-owner",
        "requirements-analyst",
        "system-architect",
        "adr-author",
        "data-architect",
        "threat-modeler",
        "delivery-planner",
        "code-author",
        "code-reviewer",
        "test-author",
        "security-scanner",
        "qa-analyst",
        "release-manager",
    ],
    3: [
        "compliance-guardian",  # added on top of Level 2
        "intake-analyst",
        "product-owner",
        "requirements-analyst",
        "system-architect",
        "adr-author",
        "data-architect",
        "threat-modeler",
        "delivery-planner",
        "code-author",
        "code-reviewer",
        "test-author",
        "security-scanner",
        "performance-analyst",
        "qa-analyst",
        "release-manager",
        "change-manager",
        "observability-engineer",
    ],
}

LEVEL_0_KEYWORDS = {
    "fix",
    "bug",
    "typo",
    "broken",
    "crash",
    "revert",
    "hotfix",
    "off by one",
    "wrong",
}
LEVEL_1_KEYWORDS = {"add", "feature", "extend", "refactor", "improve", "enhance"}
LEVEL_2_KEYWORDS = {
    "new service",
    "new product",
    "mvp",
    "system",
    "platform",
    "greenfield",
    "rewrite",
    "overhaul",
    "migrate to",
    "introduce",
}
LEVEL_3_KEYWORDS = {
    "compliance",
    "lgpd",
    "gdpr",
    "pci",
    "sox",
    "regulated",
    "critical",
    "multi-team",
    "mission critical",
    "regulatory",
    "enterprise",
    "audit",
}

SECURITY_ESCALATORS = {
    r"\bauth(entication|orization)?\b": "auth/authz change",
    r"\bpii\b|\bcpf\b|\bssn\b|personally identifiable": "PII exposure",
    r"\bnew public endpoint\b|\bpublic api\b|\bpublic route\b": "new public endpoint",
    r"\bcvss\s*[>=]\s*7": "CVSS >= 7.0",
    r"\bcrypto(graphy)?\b|\bencrypt\b|\btls\b|\bprivate key\b": "cryptography change",
    r"\bpayment\b|\bcharge\b|\brefund\b|\bpix\b|\bcredit card\b": "payment flow",
}


def _find_keywords(text: str, keywords: set[str]) -> list[str]:
    tl = text.lower()
    matched = [k for k in keywords if re.search(rf"\b{re.escape(k)}\b", tl)]
    return matched


def detect(text: str, files: list[str] | None = None) -> Detection:
    files = files or []
    reasoning: list[str] = []
    matched: list[str] = []
    escalations: list[str] = []

    lvl_0 = _find_keywords(text, LEVEL_0_KEYWORDS)
    lvl_1 = _find_keywords(text, LEVEL_1_KEYWORDS)
    lvl_2 = _find_keywords(text, LEVEL_2_KEYWORDS)
    lvl_3 = _find_keywords(text, LEVEL_3_KEYWORDS)

    # Base level: strongest match wins, ties broken by higher level
    base_level = 0
    if lvl_3:
        base_level = 3
        matched.extend(lvl_3)
        reasoning.append(f"Level 3 keywords present: {sorted(lvl_3)}")
    elif lvl_2:
        base_level = 2
        matched.extend(lvl_2)
        reasoning.append(f"Level 2 keywords present: {sorted(lvl_2)}")
    elif lvl_1 and not lvl_0:
        base_level = 1
        matched.extend(lvl_1)
        reasoning.append(f"Level 1 keywords present: {sorted(lvl_1)}")
    elif lvl_0:
        base_level = 0
        matched.extend(lvl_0)
        reasoning.append(f"Level 0 keywords present: {sorted(lvl_0)}")
    else:
        base_level = 1
        reasoning.append("No distinctive keywords — defaulting to Level 1 (feature)")

    # File-count heuristic: pushes Level 0 -> 1 if too many files
    if base_level == 0 and len(files) > 5:
        base_level = 1
        reasoning.append(
            f"Level 0 upgraded to 1: {len(files)} files exceeds quick-fix threshold"
        )

    # Security escalations — can push level upward only
    for pattern, label in SECURITY_ESCALATORS.items():
        if re.search(pattern, text, re.IGNORECASE):
            escalations.append(label)

    escalated_level = base_level
    if escalations:
        # CVSS >= 7.0 → min Level 3; others → min Level 2
        if any("CVSS" in e for e in escalations):
            escalated_level = max(escalated_level, 3)
        else:
            escalated_level = max(escalated_level, 2)
        reasoning.append(
            f"Security escalation: {escalations} -> level {escalated_level}"
        )

    meta = LEVEL_META[escalated_level]
    return Detection(
        level=escalated_level,
        level_name=meta["name"],
        suggested_command=meta["command"],
        reasoning=reasoning,
        triggered_escalations=escalations,
        matched_keywords=sorted(set(matched)),
        suggested_agents=AGENT_ROUTING[escalated_level],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", help="Request text to classify")
    parser.add_argument(
        "--files", nargs="*", help="File paths affected (optional heuristic)"
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = args.text or sys.stdin.read().strip()
    if not text:
        print("ERROR: no text provided via --text or stdin", file=sys.stderr)
        return 2

    result = detect(text, args.files)
    payload: dict[str, Any] = {
        "level": result.level,
        "level_name": result.level_name,
        "suggested_command": result.suggested_command,
        "reasoning": result.reasoning,
        "triggered_escalations": result.triggered_escalations,
        "matched_keywords": result.matched_keywords,
        "suggested_agents": result.suggested_agents,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Detected level: {result.level} ({result.level_name})")
        print(f"Suggested command: {result.suggested_command}")
        if result.triggered_escalations:
            print(f"Escalations: {', '.join(result.triggered_escalations)}")
        print("Reasoning:")
        for r in result.reasoning:
            print(f"  - {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
