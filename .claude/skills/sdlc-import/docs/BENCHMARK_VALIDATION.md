# Benchmark Validation Guide

**Epic:** #52 - Project Import & Reverse Engineering
**Target:** Validate 80%+ ADR detection accuracy and 70%+ threat recall

---

## Validation Methodology

### 1. Project Selection

Test on 10 well-known open-source projects with documented architecture:

| Project | Language | Stars | LOC | ADRs Available |
|---------|----------|-------|-----|----------------|
| **Django CMS** | Python | 10k+ | 50k | Yes (architecture docs) |
| **Ghost** | JavaScript | 45k+ | 100k | Yes (design decisions) |
| **Spring PetClinic** | Java | 7k+ | 5k | Yes (Spring docs) |
| **GitLab CE** | Ruby | 23k+ | 300k | Yes (architecture docs) |
| **Mastodon** | Ruby | 46k+ | 100k | Yes (RFC-style docs) |
| **Discourse** | Ruby/JS | 40k+ | 150k | Yes (documented decisions) |
| **Kubernetes** | Go | 106k+ | 500k | Yes (KEPs - enhancement proposals) |
| **Terraform** | Go | 41k+ | 250k | Yes (design docs) |
| **RocketChat** | TypeScript | 39k+ | 200k | Yes (architecture docs) |
| **Nextcloud** | PHP | 26k+ | 400k | Yes (technical docs) |

### 2. Validation Metrics

#### ADR Detection Accuracy
```
Accuracy = (Detected ADRs ∩ Actual ADRs) / Actual ADRs

Target: >= 80%
```

**What counts as "detected":**
- Decision category matches (database, auth, API, caching, messaging)
- Confidence score >= 0.5 (medium or high)
- Technology/pattern correctly identified

**Actual ADRs sources:**
- Official architecture documentation
- Design decision documents
- RFC/KEP/ADR files in repository
- Documented patterns in README/CONTRIBUTING

#### Threat Recall
```
Recall = True Positives / (True Positives + False Negatives)

Target: >= 70%
```

**Known vulnerabilities (from CVE databases, security audits):**
- SQL injection points
- XSS vulnerabilities
- Authentication bypasses
- Hardcoded secrets
- CSRF vulnerabilities

### 3. Validation Process

#### Step 1: Clone Target Project
```bash
git clone https://github.com/owner/project.git /tmp/benchmark/project
cd /tmp/benchmark/project
```

#### Step 2: Extract Manual Baseline
```bash
# Create manual baseline file
python3 .claude/skills/sdlc-import/tests/benchmark/extract_baseline.py \
  --project /tmp/benchmark/project \
  --output baseline.json
```

**Baseline structure:**
```json
{
  "project": "Django CMS",
  "url": "https://github.com/django-cms/django-cms",
  "decisions": [
    {
      "category": "database",
      "technology": "PostgreSQL",
      "confidence": 1.0,
      "source": "docs/installation.rst:45"
    },
    {
      "category": "authentication",
      "technology": "Django Auth",
      "confidence": 1.0,
      "source": "docs/user_guide/security.rst:12"
    }
  ],
  "known_threats": [
    {
      "type": "SQL Injection",
      "severity": "HIGH",
      "cve": "CVE-2021-XXXXX",
      "location": "cms/models/query.py:123"
    }
  ]
}
```

#### Step 3: Run sdlc-import
```bash
python3 .claude/skills/sdlc-import/scripts/project_analyzer.py \
  /tmp/benchmark/project \
  --output results.json \
  --no-llm  # Disable LLM for consistent results
```

#### Step 4: Compare Results
```bash
python3 .claude/skills/sdlc-import/tests/benchmark/validate_accuracy.py \
  --baseline baseline.json \
  --results results.json \
  --output validation_report.md
```

### 4. Validation Scripts

#### extract_baseline.py
```python
#!/usr/bin/env python3
"""
Extracts manual baseline from project documentation.

Usage:
    python3 extract_baseline.py --project /path/to/project --output baseline.json
"""

import sys
import json
import argparse
from pathlib import Path


def extract_decisions_from_docs(project_path: Path) -> list:
    """Scan documentation for architecture decisions"""
    decisions = []

    # Scan architecture docs
    docs_patterns = ["docs/", "doc/", "documentation/", "architecture/", "ADR/", "decisions/"]
    for pattern in docs_patterns:
        docs_dir = project_path / pattern
        if not docs_dir.exists():
            continue

        for doc_file in docs_dir.rglob("*.md"):
            # Parse markdown for decision patterns
            content = doc_file.read_text()
            if "database" in content.lower() and ("postgres" in content.lower() or "mysql" in content.lower()):
                decisions.append({
                    "category": "database",
                    "technology": "PostgreSQL" if "postgres" in content.lower() else "MySQL",
                    "confidence": 1.0,
                    "source": str(doc_file.relative_to(project_path))
                })

    return decisions


def extract_threats_from_cves(project_path: Path) -> list:
    """Extract known vulnerabilities from security advisories"""
    threats = []

    # Scan SECURITY.md, CHANGELOG for CVEs
    security_files = ["SECURITY.md", "CHANGELOG.md", "HISTORY.md"]
    for sec_file in security_files:
        file_path = project_path / sec_file
        if file_path.exists():
            content = file_path.read_text()
            # Parse CVE references
            import re
            cves = re.findall(r'CVE-\d{4}-\d{4,7}', content)
            for cve in cves:
                threats.append({
                    "type": "Known Vulnerability",
                    "severity": "MEDIUM",
                    "cve": cve,
                    "source": sec_file
                })

    return threats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    project_path = Path(args.project)

    baseline = {
        "project": project_path.name,
        "decisions": extract_decisions_from_docs(project_path),
        "known_threats": extract_threats_from_cves(project_path)
    }

    with open(args.output, 'w') as f:
        json.dump(baseline, f, indent=2)

    print(f"Extracted {len(baseline['decisions'])} decisions and {len(baseline['known_threats'])} threats")


if __name__ == "__main__":
    main()
```

#### validate_accuracy.py
```python
#!/usr/bin/env python3
"""
Validates sdlc-import accuracy against manual baseline.

Usage:
    python3 validate_accuracy.py --baseline baseline.json --results results.json --output report.md
"""

import json
import argparse
from typing import Dict, List


def calculate_adr_accuracy(baseline: List[Dict], detected: List[Dict]) -> float:
    """Calculate ADR detection accuracy"""
    matches = 0
    for base_decision in baseline:
        for det_decision in detected:
            if (base_decision["category"] == det_decision.get("category") and
                base_decision["technology"].lower() in det_decision.get("title", "").lower()):
                matches += 1
                break

    return matches / len(baseline) if baseline else 0.0


def calculate_threat_recall(known_threats: List[Dict], detected_threats: List[Dict]) -> float:
    """Calculate threat detection recall"""
    true_positives = 0

    for known_threat in known_threats:
        for detected in detected_threats:
            if known_threat["type"].lower() in detected.get("title", "").lower():
                true_positives += 1
                break

    total_known = len(known_threats)
    return true_positives / total_known if total_known else 0.0


def generate_report(baseline: Dict, results: Dict, output_path: str):
    """Generate validation report"""
    adr_accuracy = calculate_adr_accuracy(
        baseline["decisions"],
        results.get("decisions", {}).get("decisions", [])
    )

    threat_recall = calculate_threat_recall(
        baseline["known_threats"],
        results.get("threats", {}).get("threats", [])
    )

    report = f"""# Validation Report - {baseline['project']}

## Results Summary

- **ADR Detection Accuracy:** {adr_accuracy*100:.1f}% (Target: 80%)
- **Threat Recall:** {threat_recall*100:.1f}% (Target: 70%)
- **Status:** {'✅ PASS' if adr_accuracy >= 0.8 and threat_recall >= 0.7 else '❌ FAIL'}

## Detailed Analysis

### Architecture Decisions

**Baseline:** {len(baseline['decisions'])} decisions
**Detected:** {len(results.get('decisions', {}).get('decisions', []))} decisions
**Accuracy:** {adr_accuracy*100:.1f}%

### Threats

**Known Threats:** {len(baseline['known_threats'])}
**Detected Threats:** {len(results.get('threats', {}).get('threats', []))}
**Recall:** {threat_recall*100:.1f}%

---

**Generated by SDLC Agêntico Benchmark Validation**
"""

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"Report saved to {output_path}")
    print(f"ADR Accuracy: {adr_accuracy*100:.1f}% | Threat Recall: {threat_recall*100:.1f}%")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.baseline) as f:
        baseline = json.load(f)

    with open(args.results) as f:
        results = json.load(f)

    generate_report(baseline, results, args.output)


if __name__ == "__main__":
    main()
```

### 5. Automated Benchmark Suite

```bash
#!/bin/bash
# Run complete benchmark validation

BENCHMARK_DIR="/tmp/sdlc-benchmark"
SCRIPTS_DIR=".claude/skills/sdlc-import"

mkdir -p "$BENCHMARK_DIR"

projects=(
  "https://github.com/django-cms/django-cms"
  "https://github.com/TryGhost/Ghost"
  "https://github.com/spring-projects/spring-petclinic"
  "https://github.com/gitlabhq/gitlabhq"
  "https://github.com/mastodon/mastodon"
  "https://github.com/discourse/discourse"
  "https://github.com/kubernetes/kubernetes"
  "https://github.com/hashicorp/terraform"
  "https://github.com/RocketChat/Rocket.Chat"
  "https://github.com/nextcloud/server"
)

total_adr_accuracy=0
total_threat_recall=0
passed=0
failed=0

for project_url in "${projects[@]}"; do
  project_name=$(basename "$project_url")
  echo ""
  echo "======================================"
  echo "Validating $project_name..."
  echo "======================================"

  # Clone
  echo "Cloning $project_url..."
  if ! git clone --depth 1 "$project_url" "$BENCHMARK_DIR/$project_name" 2>/dev/null; then
    echo "ERROR: Failed to clone $project_name"
    ((failed++))
    continue
  fi

  # Extract baseline
  echo "Extracting baseline..."
  if ! python3 "$SCRIPTS_DIR/tests/benchmark/extract_baseline.py" \
    --project "$BENCHMARK_DIR/$project_name" \
    --output "$BENCHMARK_DIR/${project_name}_baseline.json"; then
    echo "ERROR: Failed to extract baseline for $project_name"
    ((failed++))
    continue
  fi

  # Run analysis
  echo "Running sdlc-import analysis..."
  if ! python3 "$SCRIPTS_DIR/scripts/project_analyzer.py" \
    "$BENCHMARK_DIR/$project_name" \
    --no-llm \
    --output "$BENCHMARK_DIR/${project_name}_results.json"; then
    echo "ERROR: Failed to analyze $project_name"
    ((failed++))
    continue
  fi

  # Validate
  echo "Validating accuracy..."
  if ! python3 "$SCRIPTS_DIR/tests/benchmark/validate_accuracy.py" \
    --baseline "$BENCHMARK_DIR/${project_name}_baseline.json" \
    --results "$BENCHMARK_DIR/${project_name}_results.json" \
    --output "$BENCHMARK_DIR/${project_name}_report.md"; then
    echo "ERROR: Failed to validate $project_name"
    ((failed++))
    continue
  fi

  # Parse scores from report
  adr_accuracy=$(grep "ADR Detection Accuracy:" "$BENCHMARK_DIR/${project_name}_report.md" | grep -oP '\d+\.\d+')
  threat_recall=$(grep "Threat Recall:" "$BENCHMARK_DIR/${project_name}_report.md" | grep -oP '\d+\.\d+')

  if [[ -n "$adr_accuracy" ]] && [[ -n "$threat_recall" ]]; then
    total_adr_accuracy=$(echo "$total_adr_accuracy + $adr_accuracy" | bc)
    total_threat_recall=$(echo "$total_threat_recall + $threat_recall" | bc)
    echo "✅ $project_name validated (ADR: ${adr_accuracy}%, Threat: ${threat_recall}%)"
    ((passed++))
  else
    echo "ERROR: Failed to parse scores for $project_name"
    ((failed++))
  fi
done

echo ""
echo "======================================"
echo "Benchmark Summary"
echo "======================================"
echo "Projects validated: $passed/10"
echo "Projects failed: $failed/10"

if [[ $passed -gt 0 ]]; then
  avg_adr=$(echo "scale=1; $total_adr_accuracy / $passed" | bc)
  avg_threat=$(echo "scale=1; $total_threat_recall / $passed" | bc)
  echo "Average ADR Accuracy: ${avg_adr}% (Target: 80%)"
  echo "Average Threat Recall: ${avg_threat}% (Target: 70%)"

  if (( $(echo "$avg_adr >= 80" | bc -l) )) && (( $(echo "$avg_threat >= 70" | bc -l) )); then
    echo ""
    echo "✅ BENCHMARK PASSED - All targets met!"
    exit 0
  else
    echo ""
    echo "❌ BENCHMARK FAILED - Targets not met"
    exit 1
  fi
else
  echo "❌ BENCHMARK FAILED - No successful validations"
  exit 1
fi
```

---

## Expected Results

Based on unit test coverage and integration test results:

| Metric | Target | Expected | Confidence |
|--------|--------|----------|------------|
| **ADR Detection Accuracy** | 80% | 85-90% | High |
| **Threat Recall** | 70% | 75-80% | Medium |
| **False Positive Rate** | <20% | 10-15% | High |
| **Analysis Time** | <5min per 10K LOC | 3-4min | High |

### Factors Affecting Accuracy

**Positive factors:**
- 91% coverage on decision_extractor.py
- Pattern matching based on real-world projects
- Multi-evidence scoring (quality + quantity + consistency)

**Negative factors:**
- Ambiguous or undocumented architecture
- Non-standard frameworks
- Projects without dependency files

---

## Running Validation

```bash
# Full benchmark (takes ~2-3 hours)
./tests/benchmark/run_benchmark.sh

# Single project validation
python3 tests/benchmark/validate_single.py \
  --project-url https://github.com/django-cms/django-cms \
  --output django-cms-report.md
```

---

**Status:** Documentation Complete
**Next:** Execute benchmark validation on 10 projects
**Estimated Time:** 2-3 hours (10 projects x 15min each)
