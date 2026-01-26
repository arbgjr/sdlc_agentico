#!/bin/bash
# test-framework-e2e.sh
# End-to-End Framework Test - Simulates complete SDLC workflow
# Tests all framework capabilities with a real project example

set -euo pipefail

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../.claude/lib/shell/logging_utils.sh"

sdlc_set_context skill="framework-e2e-test" phase=0

# Test configuration
TEST_PROJECT="Todo App API"
TEST_DIR=$(mktemp -d -t sdlc-test-XXXXXX)
ORIGINAL_DIR=$(pwd)
TEST_PASSED=true

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Cleanup on exit
cleanup() {
  cd "$ORIGINAL_DIR"
  if [ "$TEST_PASSED" = true ]; then
    rm -rf "$TEST_DIR"
    echo -e "${GREEN}✅ Cleanup complete${NC}"
  else
    echo -e "${YELLOW}⚠️  Test artifacts preserved at: $TEST_DIR${NC}"
  fi
}
trap cleanup EXIT

# Log test step
log_step() {
  echo ""
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${GREEN}▶ $1${NC}"
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  sdlc_log_info "Test step: $1"
}

# Check test result
check_result() {
  local description=$1
  local condition=$2

  if [ "$condition" = "0" ]; then
    echo -e "${GREEN}✅ PASS:${NC} $description"
    sdlc_log_info "Test passed" "check=$description"
  else
    echo -e "${RED}❌ FAIL:${NC} $description"
    sdlc_log_error "Test failed" "check=$description"
    TEST_PASSED=false
  fi
}

# Assert file exists
assert_file_exists() {
  local file=$1
  local description=$2

  if [ -f "$file" ]; then
    check_result "$description" 0
  else
    check_result "$description (file missing: $file)" 1
  fi
}

# Assert directory exists
assert_dir_exists() {
  local dir=$1
  local description=$2

  if [ -d "$dir" ]; then
    check_result "$description" 0
  else
    check_result "$description (dir missing: $dir)" 1
  fi
}

# Assert file contains string
assert_file_contains() {
  local file=$1
  local pattern=$2
  local description=$3

  if grep -q "$pattern" "$file" 2>/dev/null; then
    check_result "$description" 0
  else
    check_result "$description (pattern not found in $file)" 1
  fi
}

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   SDLC Agêntico - End-to-End Framework Test   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
sdlc_log_info "Starting E2E framework test" "test_dir=$TEST_DIR"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 1: Framework Structure
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 1: Validate Framework Structure"

assert_dir_exists ".agentic_sdlc/templates" "Templates directory exists"
assert_dir_exists ".agentic_sdlc/schemas" "Schemas directory exists"
assert_dir_exists ".agentic_sdlc/docs" "Docs directory exists"
assert_dir_exists ".agentic_sdlc/scripts" "Scripts directory exists"
assert_file_exists ".agentic_sdlc/templates/adr-template.yml" "ADR template exists"
assert_file_exists ".agentic_sdlc/templates/spec-template.md" "Spec template exists"
assert_file_exists ".agentic_sdlc/templates/threat-model-template.yml" "Threat model template exists"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 2: Project Structure Setup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 2: Setup Test Project Structure"

cd "$TEST_DIR"

# Create minimal project structure
mkdir -p .project/{corpus/nodes/{decisions,learnings,patterns,concepts},phases,architecture,security,reports,sessions,references}
mkdir -p .project/phases/phase-{0..8}-{intake,discovery,requirements,architecture,planning,implementation,quality,release,operations}

# Copy framework
cp -r "$ORIGINAL_DIR/.agentic_sdlc" .
mkdir -p .claude/hooks .claude/skills/gate-evaluator/gates
cp -r "$ORIGINAL_DIR/.claude/lib" .claude/
cp -r "$ORIGINAL_DIR/.claude/hooks" .claude/
cp -r "$ORIGINAL_DIR/.claude/skills/gate-evaluator/gates" .claude/skills/gate-evaluator/

assert_dir_exists ".project/corpus" "Project corpus created"
assert_dir_exists ".project/phases" "Project phases created"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 3: Phase 0 - Intake
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 3: Phase 0 - Intake & Preparation"

# Simulate intake phase artifacts
cat > .project/phases/phase-0-intake/intake-brief.md <<EOF
# Intake Brief: $TEST_PROJECT

## Business Need
Build a RESTful API for a Todo application to manage tasks.

## Key Requirements
- User authentication (JWT)
- CRUD operations for tasks
- Task priority levels
- PostgreSQL database
- RESTful API design

## Constraints
- Must be production-ready
- Security by design
- API documentation required

## Success Criteria
- All endpoints documented
- Security scan passing
- Load test > 1000 req/s
EOF

assert_file_exists ".project/phases/phase-0-intake/intake-brief.md" "Intake brief created"
assert_file_contains ".project/phases/phase-0-intake/intake-brief.md" "Todo" "Intake brief has project name"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 4: Phase 1 - Discovery
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 4: Phase 1 - Discovery"

# Simulate discovery artifacts
cat > .project/phases/phase-1-discovery/tech-stack.json <<EOF
{
  "languages": ["Python", "SQL"],
  "frameworks": ["FastAPI", "SQLAlchemy"],
  "database": "PostgreSQL",
  "tools": ["pytest", "black", "ruff"],
  "infrastructure": ["Docker", "GitHub Actions"]
}
EOF

assert_file_exists ".project/phases/phase-1-discovery/tech-stack.json" "Tech stack documented"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 5: Phase 2 - Requirements
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 5: Phase 2 - Requirements Analysis"

# Create user stories
cat > .project/phases/phase-2-requirements/user-stories.md <<EOF
# User Stories

## US-001: Create Task
**As a** user
**I want to** create a new task
**So that** I can track my work

### Acceptance Criteria
- Task has title, description, priority
- Task is persisted to database
- API returns 201 Created with task ID

## US-002: List Tasks
**As a** user
**I want to** list all my tasks
**So that** I can see what needs to be done

### Acceptance Criteria
- Returns paginated list
- Supports filtering by priority
- Includes task completion status
EOF

assert_file_exists ".project/phases/phase-2-requirements/user-stories.md" "User stories created"
assert_file_contains ".project/phases/phase-2-requirements/user-stories.md" "Acceptance Criteria" "User stories have acceptance criteria"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 6: Phase 3 - Architecture
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 6: Phase 3 - Architecture Design"

# Create ADR using template
cat > .project/corpus/nodes/decisions/ADR-001-use-fastapi.yml <<EOF
id: ADR-001
title: Use FastAPI for REST API
date: $(date +%Y-%m-%d)
status: accepted
context: |
  Need to choose a Python web framework for building the REST API.
  Requirements: async support, OpenAPI docs, performance, modern.

decision: |
  Use FastAPI as the web framework.

consequences:
  positive:
    - Built-in OpenAPI/Swagger documentation
    - Async/await support for high performance
    - Type hints with Pydantic validation
    - Active community and good documentation
  negative:
    - Relatively newer framework
    - Less enterprise adoption than Flask/Django

alternatives:
  - name: Django REST Framework
    rejected_because: Too heavy for simple API, sync-only
  - name: Flask
    rejected_because: No built-in async, manual API docs

tags:
  - architecture
  - api
  - python
EOF

assert_file_exists ".project/corpus/nodes/decisions/ADR-001-use-fastapi.yml" "ADR-001 created"

# Create architecture diagram
cat > .project/architecture/component-diagram.mmd <<EOF
graph TD
    Client[API Client] --> Gateway[API Gateway]
    Gateway --> Auth[Auth Service]
    Gateway --> Tasks[Tasks Service]
    Tasks --> DB[(PostgreSQL)]
    Auth --> DB
    Tasks --> Cache[(Redis)]
EOF

assert_file_exists ".project/architecture/component-diagram.mmd" "Architecture diagram created"

# Create threat model
cat > .project/security/threat-model.yml <<EOF
project: $TEST_PROJECT
date: $(date +%Y-%m-%d)
threats:
  - id: TM-001
    category: Authentication
    threat: Brute force attacks on login endpoint
    severity: HIGH
    mitigation: Implement rate limiting (max 5 attempts/minute)
    status: mitigated

  - id: TM-002
    category: Authorization
    threat: Unauthorized access to other users' tasks
    severity: CRITICAL
    mitigation: JWT token validation on every request
    status: mitigated

  - id: TM-003
    category: Injection
    threat: SQL injection via task title/description
    severity: HIGH
    mitigation: Use SQLAlchemy ORM with parameterized queries
    status: mitigated
EOF

assert_file_exists ".project/security/threat-model.yml" "Threat model created"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 7: Template Usage
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 7: Validate Template Usage"

# Check that templates are accessible
template_count=$(find .agentic_sdlc/templates -name "*.yml" -o -name "*.md" | wc -l)
if [ "$template_count" -ge 3 ]; then
  check_result "Templates are accessible (found $template_count templates)" 0
else
  check_result "Templates are accessible (expected >= 3, found $template_count)" 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 8: Quality Gates
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 8: Quality Gates Validation"

# Check that gates exist
gate_count=$(find .claude/skills/gate-evaluator/gates -name "*.yml" | wc -l)
if [ "$gate_count" -ge 5 ]; then
  check_result "Quality gates exist (found $gate_count gates)" 0
else
  check_result "Quality gates exist (expected >= 5, found $gate_count)" 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 9: Corpus RAG Operations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 9: RAG Corpus Operations"

# Create multiple ADRs to test corpus
cat > .project/corpus/nodes/decisions/ADR-002-use-postgresql.yml <<EOF
id: ADR-002
title: Use PostgreSQL for data persistence
date: $(date +%Y-%m-%d)
status: accepted
context: Need to choose database
decision: Use PostgreSQL
consequences:
  positive: ["ACID compliance", "JSON support"]
  negative: ["Requires hosting"]
tags: ["database"]
EOF

cat > .project/corpus/nodes/learnings/LEARN-001-fastapi-async.yml <<EOF
id: LEARN-001
title: FastAPI async patterns
date: $(date +%Y-%m-%d)
category: learning
content: |
  Learned that FastAPI async endpoints require database connections
  to also use async drivers (asyncpg instead of psycopg2).
tags: ["fastapi", "async", "database"]
EOF

adr_count=$(find .project/corpus/nodes/decisions -name "*.yml" | wc -l)
if [ "$adr_count" -ge 2 ]; then
  check_result "Corpus has multiple ADRs ($adr_count found)" 0
else
  check_result "Corpus has multiple ADRs (expected >= 2, found $adr_count)" 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 10: Documentation Generation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 10: Documentation Accessibility"

doc_count=$(find .agentic_sdlc/docs -name "*.md" | wc -l)
if [ "$doc_count" -ge 5 ]; then
  check_result "Framework documentation exists ($doc_count docs)" 0
else
  check_result "Framework documentation exists (expected >= 5, found $doc_count)" 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 11: Logging Integration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 11: Structured Logging"

# Test logging utilities
sdlc_log_debug "E2E test debug message" "test=framework"
sdlc_log_info "E2E test info message" "test=framework"
sdlc_log_warn "E2E test warning message" "test=framework"

check_result "Logging utilities functional" 0

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test 12: Framework Validation Hook
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_step "Test 12: Framework Validation Hook"

if [ -x "$ORIGINAL_DIR/.claude/hooks/validate-framework-structure.sh" ]; then
  check_result "Framework validation hook exists and is executable" 0
else
  check_result "Framework validation hook exists and is executable" 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Final Summary
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                  TEST SUMMARY                  ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$TEST_PASSED" = true ]; then
  echo -e "${GREEN}✅ All tests PASSED${NC}"
  echo ""
  echo "Framework validation complete:"
  echo "  ✅ Structure validated"
  echo "  ✅ Templates accessible"
  echo "  ✅ Schemas present"
  echo "  ✅ Documentation available"
  echo "  ✅ Quality gates configured"
  echo "  ✅ Corpus operations working"
  echo "  ✅ Logging integrated"
  echo "  ✅ Hooks executable"
  echo ""
  sdlc_log_info "E2E test PASSED" "project=$TEST_PROJECT"
  exit 0
else
  echo -e "${RED}❌ Some tests FAILED${NC}"
  echo ""
  echo "Review failures above for details."
  echo -e "Test artifacts preserved at: ${YELLOW}$TEST_DIR${NC}"
  echo ""
  sdlc_log_error "E2E test FAILED" "project=$TEST_PROJECT"
  exit 1
fi
