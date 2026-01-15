#!/bin/bash
#
# Hook: Validate Commit
# Valida commit messages seguem Conventional Commits
# e nao contem secrets ou codigo proibido.
#

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_error() { echo -e "${RED}[BLOCKED]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }

# Obter mensagem do commit
COMMIT_MSG="${COMMIT_MSG:-$(cat .git/COMMIT_EDITMSG 2>/dev/null || echo '')}"

# Se nao tem mensagem, e dry run
if [[ -z "$COMMIT_MSG" ]]; then
    log_warn "Nenhuma mensagem de commit para validar (dry run)"
    exit 0
fi

ERRORS=0

# 1. Validar Conventional Commits
CONVENTIONAL_PATTERN="^(feat|fix|refactor|docs|test|chore|ci|perf|style)(\(.+\))?: .+"

if [[ ! "$COMMIT_MSG" =~ $CONVENTIONAL_PATTERN ]]; then
    log_error "Commit message nao segue Conventional Commits"
    echo "  Formato esperado: type(scope): description"
    echo "  Tipos validos: feat, fix, refactor, docs, test, chore, ci, perf, style"
    echo "  Exemplo: feat(orders): add order history endpoint"
    ERRORS=$((ERRORS + 1))
else
    log_ok "Conventional Commits: OK"
fi

# 2. Verificar tamanho da primeira linha
FIRST_LINE=$(echo "$COMMIT_MSG" | head -n1)
if [[ ${#FIRST_LINE} -gt 72 ]]; then
    log_warn "Primeira linha do commit muito longa (${#FIRST_LINE} > 72)"
    ERRORS=$((ERRORS + 1))
fi

# 3. Verificar palavras proibidas na mensagem
FORBIDDEN_WORDS="TODO|FIXME|WIP|DO NOT COMMIT|secret|password|api.key"

if echo "$COMMIT_MSG" | grep -iE "$FORBIDDEN_WORDS" > /dev/null; then
    log_error "Commit message contem palavras proibidas"
    echo "  Palavras detectadas: $(echo "$COMMIT_MSG" | grep -ioE "$FORBIDDEN_WORDS" | tr '\n' ', ')"
    ERRORS=$((ERRORS + 1))
else
    log_ok "Sem palavras proibidas: OK"
fi

# 4. Verificar arquivos staged por secrets
if command -v gitleaks &> /dev/null; then
    if ! gitleaks protect --staged --no-banner 2>/dev/null; then
        log_error "Secrets detectados nos arquivos staged"
        ERRORS=$((ERRORS + 1))
    else
        log_ok "Secrets scan: OK"
    fi
fi

# 5. Verificar se ha mocks em codigo de producao
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

for file in $STAGED_FILES; do
    # Ignorar diretorio de testes
    if [[ "$file" =~ ^tests?/ ]] || [[ "$file" =~ /tests?/ ]]; then
        continue
    fi

    # Verificar por mock patterns
    if [[ -f "$file" ]]; then
        if grep -iE "(mock|stub|fake|dummy)" "$file" > /dev/null 2>&1; then
            log_warn "Possivel mock em codigo de producao: $file"
            # Nao bloqueia, apenas avisa
        fi
    fi
done

# Resultado
echo ""
if [[ $ERRORS -gt 0 ]]; then
    log_error "Commit bloqueado: $ERRORS erro(s) encontrado(s)"
    exit 1
else
    log_ok "Commit validado com sucesso"
    exit 0
fi
