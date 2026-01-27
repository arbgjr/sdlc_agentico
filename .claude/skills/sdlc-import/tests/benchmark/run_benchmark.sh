#!/bin/bash
# Automated Benchmark Validation for SDLC Import
# Validates sdlc-import accuracy against 10 open-source projects
#
# Usage:
#   ./run_benchmark.sh                  # Run all 10 projects
#   ./run_benchmark.sh --project django-cms  # Run single project
#   ./run_benchmark.sh --cleanup        # Clean benchmark directory

set -euo pipefail

BENCHMARK_DIR="/tmp/sdlc-benchmark"
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_FILTER="${1:-}"

# Project URLs
declare -A PROJECTS=(
  ["django-cms"]="https://github.com/django-cms/django-cms"
  ["ghost"]="https://github.com/TryGhost/Ghost"
  ["spring-petclinic"]="https://github.com/spring-projects/spring-petclinic"
  ["gitlab"]="https://github.com/gitlabhq/gitlabhq"
  ["mastodon"]="https://github.com/mastodon/mastodon"
  ["discourse"]="https://github.com/discourse/discourse"
  ["kubernetes"]="https://github.com/kubernetes/kubernetes"
  ["terraform"]="https://github.com/hashicorp/terraform"
  ["rocketchat"]="https://github.com/RocketChat/Rocket.Chat"
  ["nextcloud"]="https://github.com/nextcloud/server"
)

# Cleanup mode
if [[ "$PROJECT_FILTER" == "--cleanup" ]]; then
  echo "Cleaning up benchmark directory: $BENCHMARK_DIR"
  rm -rf "$BENCHMARK_DIR"
  echo "✅ Cleanup complete"
  exit 0
fi

# Create benchmark directory
mkdir -p "$BENCHMARK_DIR"

# Counters
total_adr_accuracy=0
total_threat_recall=0
passed=0
failed=0

# Function to validate single project
validate_project() {
  local project_name=$1
  local project_url=$2

  echo ""
  echo "======================================"
  echo "Validating $project_name..."
  echo "======================================"

  # Clone
  echo "📥 Cloning $project_url..."
  if [[ -d "$BENCHMARK_DIR/$project_name" ]]; then
    echo "⚠️  Directory already exists, skipping clone"
  else
    if ! git clone --depth 1 "$project_url" "$BENCHMARK_DIR/$project_name" 2>/dev/null; then
      echo "❌ ERROR: Failed to clone $project_name"
      return 1
    fi
  fi

  # Extract baseline
  echo "📊 Extracting baseline..."
  if ! python3 "$SCRIPTS_DIR/tests/benchmark/extract_baseline.py" \
    --project "$BENCHMARK_DIR/$project_name" \
    --output "$BENCHMARK_DIR/${project_name}_baseline.json" 2>&1 | tee "$BENCHMARK_DIR/${project_name}_baseline.log"; then
    echo "❌ ERROR: Failed to extract baseline for $project_name"
    return 1
  fi

  # Check if baseline has content
  baseline_count=$(jq '.decisions | length' "$BENCHMARK_DIR/${project_name}_baseline.json" 2>/dev/null || echo "0")
  if [[ "$baseline_count" == "0" ]]; then
    echo "⚠️  WARNING: No decisions found in baseline for $project_name"
    echo "   This project may not have sufficient documentation for validation"
    return 1
  fi
  echo "   Found $baseline_count decisions in baseline"

  # Run analysis
  echo "🔍 Running sdlc-import analysis..."
  if ! python3 "$SCRIPTS_DIR/scripts/project_analyzer.py" \
    "$BENCHMARK_DIR/$project_name" \
    --no-llm \
    --output "$BENCHMARK_DIR/${project_name}_results.json" 2>&1 | tee "$BENCHMARK_DIR/${project_name}_analysis.log"; then
    echo "❌ ERROR: Failed to analyze $project_name"
    return 1
  fi

  # Validate
  echo "✅ Validating accuracy..."
  if ! python3 "$SCRIPTS_DIR/tests/benchmark/validate_accuracy.py" \
    --baseline "$BENCHMARK_DIR/${project_name}_baseline.json" \
    --results "$BENCHMARK_DIR/${project_name}_results.json" \
    --output "$BENCHMARK_DIR/${project_name}_report.md" 2>&1 | tee "$BENCHMARK_DIR/${project_name}_validation.log"; then
    echo "❌ ERROR: Failed to validate $project_name"
    return 1
  fi

  # Parse scores from report
  local adr_accuracy=$(grep -oP "ADR Detection Accuracy:\*\* \K\d+\.\d+" "$BENCHMARK_DIR/${project_name}_report.md" || echo "0")
  local threat_recall=$(grep -oP "Threat Recall:\*\* \K\d+\.\d+" "$BENCHMARK_DIR/${project_name}_report.md" || echo "0")

  if [[ -n "$adr_accuracy" ]] && [[ -n "$threat_recall" ]] && [[ "$adr_accuracy" != "0" ]]; then
    total_adr_accuracy=$(echo "$total_adr_accuracy + $adr_accuracy" | bc)
    total_threat_recall=$(echo "$total_threat_recall + $threat_recall" | bc)
    echo "✅ $project_name validated successfully"
    echo "   ADR Accuracy: ${adr_accuracy}% | Threat Recall: ${threat_recall}%"
    ((passed++))
    return 0
  else
    echo "❌ ERROR: Failed to parse scores for $project_name"
    return 1
  fi
}

# Main execution
echo "SDLC Import Benchmark Validation"
echo "================================="
echo "Benchmark directory: $BENCHMARK_DIR"
echo "Scripts directory: $SCRIPTS_DIR"
echo ""

if [[ -n "$PROJECT_FILTER" ]] && [[ "$PROJECT_FILTER" != "--"* ]]; then
  # Single project mode
  if [[ -v "PROJECTS[$PROJECT_FILTER]" ]]; then
    validate_project "$PROJECT_FILTER" "${PROJECTS[$PROJECT_FILTER]}" || ((failed++))
  else
    echo "❌ ERROR: Unknown project '$PROJECT_FILTER'"
    echo "Available projects:"
    for proj in "${!PROJECTS[@]}"; do
      echo "  - $proj"
    done
    exit 1
  fi
else
  # All projects mode
  for project_name in "${!PROJECTS[@]}"; do
    validate_project "$project_name" "${PROJECTS[$project_name]}" || ((failed++))
  done
fi

# Summary
echo ""
echo "======================================"
echo "Benchmark Summary"
echo "======================================"
echo "Projects validated: $passed"
echo "Projects failed: $failed"
echo "Total projects: $((passed + failed))"

if [[ $passed -gt 0 ]]; then
  avg_adr=$(echo "scale=1; $total_adr_accuracy / $passed" | bc)
  avg_threat=$(echo "scale=1; $total_threat_recall / $passed" | bc)
  echo ""
  echo "Average ADR Accuracy: ${avg_adr}% (Target: ≥80%)"
  echo "Average Threat Recall: ${avg_threat}% (Target: ≥70%)"
  echo ""

  if (( $(echo "$avg_adr >= 80" | bc -l) )) && (( $(echo "$avg_threat >= 70" | bc -l) )); then
    echo "✅ BENCHMARK PASSED - All targets met!"
    echo ""
    echo "Results saved to: $BENCHMARK_DIR/*_report.md"
    exit 0
  else
    echo "❌ BENCHMARK FAILED - Targets not met"
    echo ""
    echo "Review individual reports in: $BENCHMARK_DIR/*_report.md"
    exit 1
  fi
else
  echo ""
  echo "❌ BENCHMARK FAILED - No successful validations"
  echo ""
  echo "Check logs in: $BENCHMARK_DIR/*.log"
  exit 1
fi
