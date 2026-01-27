#!/bin/bash
#
# System Design Decision Checklist
# Interactive checklist to ensure all critical decisions are made
#
# Usage:
#   ./decision_checklist.sh
#   ./decision_checklist.sh --quick
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
ANSWERED=0
PENDING=0

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  SYSTEM DESIGN DECISION CHECKLIST${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${YELLOW}▶ $1${NC}"
    echo -e "${YELLOW}─────────────────────────────────────────${NC}"
}

ask_question() {
    local question="$1"
    local hint="$2"

    TOTAL=$((TOTAL + 1))

    echo ""
    echo -e "  ${BLUE}[$TOTAL]${NC} $question"
    if [ -n "$hint" ]; then
        echo -e "      ${YELLOW}Hint: $hint${NC}"
    fi

    read -p "      Answer (y=yes/n=no/s=skip): " answer

    case "$answer" in
        y|Y|yes|YES)
            echo -e "      ${GREEN}✓ Decided${NC}"
            ANSWERED=$((ANSWERED + 1))
            ;;
        n|N|no|NO)
            echo -e "      ${RED}✗ Not yet decided${NC}"
            PENDING=$((PENDING + 1))
            ;;
        *)
            echo -e "      ${YELLOW}⊘ Skipped${NC}"
            ;;
    esac
}

quick_check() {
    local question="$1"
    TOTAL=$((TOTAL + 1))
    echo -e "  [ ] $question"
}

print_summary() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  SUMMARY${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Total questions:  $TOTAL"
    echo -e "  ${GREEN}Decided:${NC}          $ANSWERED"
    echo -e "  ${RED}Pending:${NC}          $PENDING"
    echo -e "  Skipped:          $((TOTAL - ANSWERED - PENDING))"
    echo ""

    if [ $PENDING -eq 0 ] && [ $ANSWERED -gt 0 ]; then
        echo -e "  ${GREEN}✓ All critical decisions have been made!${NC}"
    elif [ $PENDING -gt 0 ]; then
        echo -e "  ${RED}⚠ There are $PENDING pending decisions that need attention.${NC}"
    fi
    echo ""
}

run_interactive() {
    print_header

    print_section "REQUIREMENTS"
    ask_question "Functional requirements are clearly defined?" "What does the system do?"
    ask_question "Non-functional requirements are specified?" "Latency, throughput, availability targets"
    ask_question "Scale requirements are quantified?" "Users, requests/sec, data volume"
    ask_question "Constraints are identified?" "Budget, team size, technology restrictions"

    print_section "DATA"
    ask_question "Data model is defined?" "Entities, relationships, access patterns"
    ask_question "Database technology is chosen and justified?" "SQL vs NoSQL, specific product"
    ask_question "Data consistency requirements are explicit?" "Strong vs eventual consistency"
    ask_question "Data retention and archival strategy is defined?" "How long to keep data"

    print_section "SCALABILITY"
    ask_question "Read scaling strategy is defined?" "Cache, replicas, CDN"
    ask_question "Write scaling strategy is defined?" "Sharding, queues, batching"
    ask_question "Horizontal scaling approach is clear?" "Stateless services, load balancing"

    print_section "RELIABILITY"
    ask_question "Single points of failure are identified?" "What breaks if X fails?"
    ask_question "Failure modes and recovery strategies are defined?" "Retry, circuit breaker, fallback"
    ask_question "Data backup and disaster recovery plan exists?" "RPO, RTO defined"
    ask_question "Monitoring and alerting strategy is defined?" "Metrics, logs, alerts"

    print_section "COMMUNICATION"
    ask_question "Sync vs async communication is decided per interaction?" "HTTP vs queue vs events"
    ask_question "API contracts are defined?" "REST, gRPC, GraphQL"
    ask_question "Real-time requirements are addressed?" "WebSocket, SSE, polling"

    print_section "SECURITY"
    ask_question "Authentication mechanism is chosen?" "JWT, OAuth, session"
    ask_question "Authorization model is defined?" "RBAC, ABAC, permissions"
    ask_question "Data encryption strategy is defined?" "At rest, in transit"

    print_section "TRADE-OFFS"
    ask_question "Main trade-offs are explicitly documented?" "What did we give up and why"
    ask_question "Alternatives were considered and documented?" "Why not X instead of Y"

    print_summary
}

run_quick() {
    print_header
    echo -e "${YELLOW}Quick checklist - print and check manually:${NC}"
    echo ""

    echo "REQUIREMENTS"
    quick_check "Functional requirements defined"
    quick_check "Non-functional requirements specified (latency, throughput, availability)"
    quick_check "Scale requirements quantified (users, RPS, data volume)"
    quick_check "Constraints identified (budget, team, technology)"

    echo ""
    echo "DATA"
    quick_check "Data model defined"
    quick_check "Database technology chosen and justified"
    quick_check "Consistency requirements explicit"
    quick_check "Retention strategy defined"

    echo ""
    echo "SCALABILITY"
    quick_check "Read scaling strategy (cache, replicas, CDN)"
    quick_check "Write scaling strategy (sharding, queues)"
    quick_check "Horizontal scaling approach"

    echo ""
    echo "RELIABILITY"
    quick_check "Single points of failure identified"
    quick_check "Failure recovery strategies defined"
    quick_check "Backup and DR plan exists"
    quick_check "Monitoring and alerting defined"

    echo ""
    echo "COMMUNICATION"
    quick_check "Sync vs async decided per interaction"
    quick_check "API contracts defined"
    quick_check "Real-time requirements addressed"

    echo ""
    echo "SECURITY"
    quick_check "Authentication mechanism chosen"
    quick_check "Authorization model defined"
    quick_check "Encryption strategy defined"

    echo ""
    echo "TRADE-OFFS"
    quick_check "Main trade-offs documented"
    quick_check "Alternatives considered and documented"

    echo ""
    echo -e "${BLUE}Total: $TOTAL items to verify${NC}"
    echo ""
}

# Main
case "${1:-}" in
    --quick|-q)
        run_quick
        ;;
    --help|-h)
        echo "Usage: $0 [--quick|--help]"
        echo ""
        echo "Options:"
        echo "  --quick, -q    Print quick checklist (non-interactive)"
        echo "  --help, -h     Show this help"
        echo ""
        echo "Without options, runs interactive checklist."
        ;;
    *)
        run_interactive
        ;;
esac
