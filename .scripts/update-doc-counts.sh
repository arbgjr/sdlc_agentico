#!/usr/bin/env bash
#
# update-doc-counts.sh - Atualiza automaticamente as contagens de componentes na documentação
#
# Uso:
#   ./scripts/update-doc-counts.sh [--dry-run] [--verbose]
#
# Opções:
#   --dry-run    Mostra as mudanças sem aplicá-las
#   --verbose    Mostra saída detalhada
#
# Este script:
#   1. Conta agentes, skills, hooks e comandos automaticamente
#   2. Atualiza README.md e CLAUDE.md com as contagens corretas
#   3. Valida que as atualizações foram aplicadas corretamente
#
# Exemplo:
#   # Ver o que seria mudado
#   ./.scripts/update-doc-counts.sh --dry-run
#
#   # Aplicar as mudanças
#   ./.scripts/update-doc-counts.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DRY_RUN=false
VERBOSE=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    -h|--help)
      head -n 20 "$0" | tail -n +3 | sed 's/^# //'
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

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_verbose() {
  if [ "$VERBOSE" = true ]; then
    echo -e "${BLUE}[VERBOSE]${NC} $*"
  fi
}

# Count components
log_info "Counting framework components..."

AGENTS=$(find .claude/agents -name "*.md" 2>/dev/null | wc -l)
SKILLS=$(find .claude/skills -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l)
HOOKS=$(find .claude/hooks -name "*.sh" 2>/dev/null | wc -l)
COMMANDS=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l)

log_success "Component counts:"
echo "   - Agents: $AGENTS"
echo "   - Skills: $SKILLS"
echo "   - Hooks: $HOOKS"
echo "   - Commands: $COMMANDS"
echo ""

# Determine agent breakdown (orchestrated vs consultive)
# Lightweight agents: failure-analyst, interview-simulator, requirements-interrogator, tradeoff-challenger
CONSULTIVE=4
ORCHESTRATED=$((AGENTS - CONSULTIVE))

log_verbose "Agent breakdown: $ORCHESTRATED orchestrated + $CONSULTIVE consultive = $AGENTS total"

# Function to update file with sed
update_file() {
  local file=$1
  local pattern=$2
  local replacement=$3
  local description=$4

  log_verbose "Updating $file: $description"

  if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY-RUN]${NC} Would update $file:"
    echo "   Pattern: $pattern"
    echo "   Replace: $replacement"
    return
  fi

  if grep -q "$pattern" "$file"; then
    sed -i "s|$pattern|$replacement|g" "$file"
    log_success "Updated $file: $description"
  else
    log_warn "Pattern not found in $file: $pattern"
  fi
}

# Backup files if not dry-run
if [ "$DRY_RUN" = false ]; then
  log_info "Creating backups..."
  cp README.md README.md.bak
  cp CLAUDE.md CLAUDE.md.bak
  log_verbose "Backups created: README.md.bak, CLAUDE.md.bak"
fi

echo ""
log_info "Updating README.md..."

# Update README.md - Main description (line ~17)
update_file "README.md" \
  "\*\*[0-9]\+ agentes especializados\*\* ([0-9]\+ orquestrados + [0-9]\+ consultivos)" \
  "**$AGENTS agentes especializados** ($ORCHESTRATED orquestrados + $CONSULTIVE consultivos)" \
  "Main description agent count"

# Update README.md - ASCII diagram (line ~28)
update_file "README.md" \
  "│  [0-9]\+ Agentes" \
  "│  $AGENTS Agentes" \
  "ASCII diagram agent count"

# Update README.md - Structure section - Agents (line ~308)
update_file "README.md" \
  "├── agents/.*# [0-9]\+ agentes especializados" \
  "├── agents/           # $AGENTS agentes especializados ($ORCHESTRATED + $CONSULTIVE consultivos)" \
  "Structure section agent count"

# Update README.md - Structure section - Skills (line ~309)
update_file "README.md" \
  "├── skills/.*# [0-9]\+ skills reutilizáveis" \
  "├── skills/           # $SKILLS skills reutilizáveis" \
  "Structure section skill count"

# Update README.md - Structure section - Commands (line ~310)
update_file "README.md" \
  "├── commands/.*# [0-9]\+ comandos do usuário" \
  "├── commands/         # $COMMANDS comandos do usuário" \
  "Structure section command count"

# Update README.md - Structure section - Hooks (line ~311)
update_file "README.md" \
  "├── hooks/.*# [0-9]\+ hooks de automação" \
  "├── hooks/            # $HOOKS hooks de automação" \
  "Structure section hook count"

echo ""
log_info "Updating CLAUDE.md..."

# Update CLAUDE.md - Main description (line ~7)
update_file "CLAUDE.md" \
  "\*\*[0-9]\+ specialized agents ([0-9]\+ orchestrated + [0-9]\+ consultive)\*\*" \
  "**$AGENTS specialized agents ($ORCHESTRATED orchestrated + $CONSULTIVE consultive)**" \
  "Main description agent count"

# Update CLAUDE.md - Configuration section (line ~93)
update_file "CLAUDE.md" \
  "- [0-9]\+ agents organized by SDLC phase ([0-9]\+ orchestrated + [0-9]\+ consultive)" \
  "- $AGENTS agents organized by SDLC phase ($ORCHESTRATED orchestrated + $CONSULTIVE consultive)" \
  "Configuration section agent count"

# Update CLAUDE.md - Structure section (line ~102)
update_file "CLAUDE.md" \
  "├── agents/.*# Agent specs (markdown) - [0-9]\+ specialized roles" \
  "├── agents/           # Agent specs (markdown) - $AGENTS specialized roles" \
  "Structure section agent count"

# Update CLAUDE.md - Agent Types table (line ~183-186)
update_file "CLAUDE.md" \
  "| \*\*Orchestrated\*\* | [0-9]\+ |" \
  "| **Orchestrated** | $ORCHESTRATED |" \
  "Agent types table orchestrated count"

echo ""

# Validate updates
if [ "$DRY_RUN" = false ]; then
  log_info "Validating updates..."
  VALIDATION_ERRORS=0

  # Check README.md
  if ! grep -q "$AGENTS agentes especializados" README.md; then
    log_error "Validation failed: Agent count not updated in README.md main description"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  fi

  if ! grep -q "$AGENTS Agentes" README.md; then
    log_error "Validation failed: Agent count not updated in README.md ASCII diagram"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  fi

  if ! grep -q "# $AGENTS agentes especializados" README.md; then
    log_error "Validation failed: Agent count not updated in README.md structure"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  fi

  if ! grep -q "# $SKILLS skills reutilizáveis" README.md; then
    log_error "Validation failed: Skill count not updated in README.md"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  fi

  if ! grep -q "# $COMMANDS comandos do usuário" README.md; then
    log_error "Validation failed: Command count not updated in README.md"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  fi

  if ! grep -q "# $HOOKS hooks de automação" README.md; then
    log_error "Validation failed: Hook count not updated in README.md"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  fi

  # Check CLAUDE.md
  if ! grep -q "$AGENTS specialized agents" CLAUDE.md; then
    log_error "Validation failed: Agent count not updated in CLAUDE.md main description"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  fi

  if ! grep -q "$AGENTS agents organized by SDLC phase" CLAUDE.md; then
    log_error "Validation failed: Agent count not updated in CLAUDE.md configuration"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  fi

  if ! grep -q "# $AGENTS specialized roles" CLAUDE.md; then
    log_error "Validation failed: Agent count not updated in CLAUDE.md structure"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
  fi

  if [ $VALIDATION_ERRORS -gt 0 ]; then
    log_error "Found $VALIDATION_ERRORS validation errors"
    log_warn "Restoring backups..."
    mv README.md.bak README.md
    mv CLAUDE.md.bak CLAUDE.md
    exit 1
  fi

  log_success "All validations passed!"

  # Remove backups
  rm -f README.md.bak CLAUDE.md.bak
  log_verbose "Removed backup files"
fi

echo ""
log_success "Documentation counts updated successfully!"
echo ""
echo "Summary of changes:"
echo "  - Agents: $AGENTS ($ORCHESTRATED orchestrated + $CONSULTIVE consultive)"
echo "  - Skills: $SKILLS"
echo "  - Hooks: $HOOKS"
echo "  - Commands: $COMMANDS"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}This was a dry-run. No files were modified.${NC}"
  echo "Run without --dry-run to apply changes."
else
  echo -e "${GREEN}Files updated: README.md, CLAUDE.md${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Review changes: git diff README.md CLAUDE.md"
  echo "  2. Commit if satisfied: git add README.md CLAUDE.md && git commit -m 'docs: update component counts'"
fi
