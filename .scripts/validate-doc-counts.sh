#!/usr/bin/env bash
#
# validate-doc-counts.sh - Valida que as contagens na documentação estão corretas
#
# Uso:
#   ./scripts/validate-doc-counts.sh [--verbose]
#
# Este script:
#   1. Conta agentes, skills, hooks e comandos automaticamente
#   2. Valida que README.md e CLAUDE.md têm as contagens corretas
#   3. Verifica referências ao nome antigo do repositório
#   4. Valida links e arquivos documentados
#   5. Verifica consistência de versão Python
#
# Exit codes:
#   0 - Todas as validações passaram
#   1 - Uma ou mais validações falharam
#
# Exemplo:
#   ./.scripts/validate-doc-counts.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERBOSE=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose)
      VERBOSE=true
      shift
      ;;
    -h|--help)
      head -n 18 "$0" | tail -n +3 | sed 's/^# //'
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}" >&2
      exit 1
      ;;
  esac
done

cd "$PROJECT_ROOT"

# Logging functions
log_info() {
  echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
  echo -e "${GREEN}[✓]${NC} $*"
}

log_error() {
  echo -e "${RED}[✗]${NC} $*" >&2
}

log_verbose() {
  if [ "$VERBOSE" = true ]; then
    echo -e "${BLUE}[VERBOSE]${NC} $*"
  fi
}

VALIDATION_ERRORS=0

# Count components
log_info "Counting framework components..."

AGENTS=$(find .claude/agents -name "*.md" 2>/dev/null | wc -l)
SKILLS=$(find .claude/skills -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l)
HOOKS=$(find .claude/hooks -name "*.sh" 2>/dev/null | wc -l)
COMMANDS=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l)

log_verbose "Found: $AGENTS agents, $SKILLS skills, $HOOKS hooks, $COMMANDS commands"
echo ""

# Validate README.md
log_info "Validating README.md..."

if ! grep -q "$AGENTS agentes especializados" README.md; then
  log_error "Agent count mismatch in README.md main description (expected: $AGENTS)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if ! grep -q "$AGENTS Agentes" README.md; then
  log_error "Agent count mismatch in README.md ASCII diagram (expected: $AGENTS)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if ! grep -q "# $AGENTS agentes especializados" README.md; then
  log_error "Agent count mismatch in README.md structure section (expected: $AGENTS)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if ! grep -q "# $SKILLS skills reutilizáveis" README.md; then
  log_error "Skill count mismatch in README.md (expected: $SKILLS)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if ! grep -q "# $COMMANDS comandos do usuário" README.md; then
  log_error "Command count mismatch in README.md (expected: $COMMANDS)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if ! grep -q "# $HOOKS hooks de automação" README.md; then
  log_error "Hook count mismatch in README.md (expected: $HOOKS)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if [ $VALIDATION_ERRORS -eq 0 ]; then
  log_success "README.md counts are correct"
fi
echo ""

# Validate CLAUDE.md
log_info "Validating CLAUDE.md..."

if ! grep -q "$AGENTS specialized agents" CLAUDE.md; then
  log_error "Agent count mismatch in CLAUDE.md main description (expected: $AGENTS)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if ! grep -q "$AGENTS agents organized by SDLC phase" CLAUDE.md; then
  log_error "Agent count mismatch in CLAUDE.md configuration section (expected: $AGENTS)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if ! grep -q "Agent specs (markdown) - $AGENTS specialized roles" CLAUDE.md; then
  log_error "Agent count mismatch in CLAUDE.md structure section (expected: $AGENTS)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if [ $VALIDATION_ERRORS -eq 0 ]; then
  log_success "CLAUDE.md counts are correct"
fi
echo ""

# Check for old repository name
log_info "Checking for old repository name..."

if grep -r "mice_dolphins" \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude="clean-test-repo.sh" \
  --exclude="validate-doc-counts.sh" \
  --exclude="validate-docs.yml" \
  --exclude="settings.local.json" \
  --exclude="README.md" \
  .scripts/ .claude/ .docs/ *.md 2>/dev/null; then
  log_error "Found old repository name 'mice_dolphins' in the codebase"
  log_error "All references should use 'sdlc_agentico'"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
  log_success "No old repository name references found"
fi
echo ""

# Validate links
log_info "Validating documentation links..."

if ! test -f .docs/guides/troubleshooting.md; then
  log_error "Referenced file .docs/guides/troubleshooting.md does not exist"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if ! test -d .docs/engineering-playbook/manual-desenvolvimento; then
  log_error "Referenced directory .docs/engineering-playbook/manual-desenvolvimento does not exist"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if test -d .docs/examples; then
  log_error "Directory .docs/examples exists but should not be in repository"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if [ $VALIDATION_ERRORS -eq 0 ]; then
  log_success "All documentation links are valid"
fi
echo ""

# Check Python version consistency
log_info "Checking Python version consistency..."

if ! grep -q "python-3\.11" README.md; then
  log_error "Python badge should declare 3.11+ (found different version)"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if ! grep -q "Python.*3\.11+" README.md; then
  log_error "Python requirement should be 3.11+"
  VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if [ $VALIDATION_ERRORS -eq 0 ]; then
  log_success "Python version is consistent (3.11+)"
fi
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════════"
if [ $VALIDATION_ERRORS -eq 0 ]; then
  echo -e "${GREEN}✓ All validations passed!${NC}"
  echo ""
  echo "Component counts:"
  echo "  - Agents: $AGENTS"
  echo "  - Skills: $SKILLS"
  echo "  - Hooks: $HOOKS"
  echo "  - Commands: $COMMANDS"
  echo ""
  exit 0
else
  echo -e "${RED}✗ Found $VALIDATION_ERRORS validation error(s)${NC}"
  echo ""
  echo "To fix automatically, run:"
  echo "  ./.scripts/update-doc-counts.sh"
  echo ""
  exit 1
fi
