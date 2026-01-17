#!/bin/bash
#
# Fallback Library - Funcoes para degradacao graciosa e resiliencia
#
# Uso:
#   source .claude/lib/fallback.sh
#
# Funcoes disponiveis:
#   retry_with_backoff <cmd> [max_attempts=3] [initial_delay=2]
#   check_service <service_name>
#   graceful_exec <cmd> <fallback_cmd>
#   log_with_fallback <level> <message>
#

# Configuracoes
FALLBACK_LOG_DIR="${HOME}/.sdlc/logs"
LOKI_URL="${LOKI_URL:-http://localhost:3100}"
RETRY_MAX_ATTEMPTS="${RETRY_MAX_ATTEMPTS:-3}"
RETRY_INITIAL_DELAY="${RETRY_INITIAL_DELAY:-2}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Garantir diretorio de logs existe
mkdir -p "$FALLBACK_LOG_DIR"

#######################################
# Executa comando com retry exponential backoff
# Arguments:
#   $1 - Comando a executar
#   $2 - Numero maximo de tentativas (default: 3)
#   $3 - Delay inicial em segundos (default: 2)
# Returns:
#   0 se sucesso, 1 se todas tentativas falharam
#######################################
retry_with_backoff() {
    local cmd="$1"
    local max_attempts="${2:-$RETRY_MAX_ATTEMPTS}"
    local delay="${3:-$RETRY_INITIAL_DELAY}"
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if eval "$cmd"; then
            return 0
        fi
        
        if [[ $attempt -lt $max_attempts ]]; then
            echo -e "${YELLOW}[WARN]${NC} Attempt $attempt/$max_attempts failed, retrying in ${delay}s..." >&2
            sleep "$delay"
            delay=$((delay * 2))
        fi
        
        ((attempt++))
    done
    
    echo -e "${RED}[ERROR]${NC} All $max_attempts attempts failed for: $cmd" >&2
    return 1
}

#######################################
# Verifica se estamos em um repositorio GitHub
# Returns:
#   0 se em repo GitHub, 1 caso contrario
#######################################
is_github_repo() {
    # Verificar se ha remote git
    if ! git remote get-url origin >/dev/null 2>&1; then
        return 1
    fi

    # Verificar se gh CLI consegue acessar o repo
    gh repo view --json nameWithOwner -q '.nameWithOwner' >/dev/null 2>&1
}

#######################################
# Verifica se um servico esta disponivel
# Arguments:
#   $1 - Nome do servico (github, loki, wiki, repo)
# Returns:
#   0 se disponivel, 1 se indisponivel
#######################################
check_service() {
    local service="$1"

    case "$service" in
        github)
            gh auth status >/dev/null 2>&1
            ;;
        repo)
            # Verifica se estamos em repositorio GitHub valido
            is_github_repo
            ;;
        loki)
            curl -s --connect-timeout 2 "${LOKI_URL}/ready" >/dev/null 2>&1
            ;;
        wiki)
            # Primeiro verificar se estamos em repo GitHub
            if ! is_github_repo; then
                return 1
            fi

            # Verificar se wiki do repo esta acessivel via git ls-remote
            local repo=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null)
            if [[ -n "$repo" ]]; then
                # Wiki Git URLs não respondem HTTP, usar git ls-remote
                git ls-remote "https://github.com/${repo}.wiki.git" HEAD >/dev/null 2>&1
            else
                return 1
            fi
            ;;
        network)
            ping -c 1 -W 2 github.com >/dev/null 2>&1 || ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Servico desconhecido: $service" >&2
            return 1
            ;;
    esac
}

#######################################
# Executa comando com fallback gracioso
# Arguments:
#   $1 - Comando primario
#   $2 - Comando de fallback
# Returns:
#   0 se algum comando teve sucesso
#######################################
graceful_exec() {
    local primary_cmd="$1"
    local fallback_cmd="$2"
    
    if eval "$primary_cmd" 2>/dev/null; then
        return 0
    fi
    
    echo -e "${YELLOW}[WARN]${NC} Primary command failed, trying fallback..." >&2
    
    if eval "$fallback_cmd" 2>/dev/null; then
        return 0
    fi
    
    echo -e "${RED}[ERROR]${NC} Both primary and fallback commands failed" >&2
    return 1
}

#######################################
# Log com fallback para arquivo local
# Se Loki disponivel, envia para Loki E arquivo
# Se Loki indisponivel, apenas arquivo
# Arguments:
#   $1 - Level (INFO, WARN, ERROR, DEBUG)
#   $2 - Message
#   $3 - Optional: component name
#######################################
log_with_fallback() {
    local level="${1:-INFO}"
    local message="$2"
    local component="${3:-sdlc}"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Criar linha de log JSON
    local log_line=$(cat <<EOF
{"timestamp":"$timestamp","level":"$level","message":"$message","component":"$component"}
EOF
)
    
    # Sempre escrever no arquivo local
    echo "$log_line" >> "${FALLBACK_LOG_DIR}/sdlc.jsonl"
    
    # Tentar enviar para Loki se disponivel
    if check_service loki; then
        local epoch_ns=$(($(date +%s) * 1000000000))
        curl -s -X POST "${LOKI_URL}/loki/api/v1/push" \
            -H "Content-Type: application/json" \
            -d "{\"streams\":[{\"stream\":{\"app\":\"sdlc\",\"component\":\"$component\",\"level\":\"$level\"},\"values\":[[\"$epoch_ns\",\"$log_line\"]]}]}" \
            >/dev/null 2>&1 || true
    fi
    
    # Output para terminal com cores
    case "$level" in
        INFO)  echo -e "${BLUE}[INFO]${NC} $message" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC} $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} $message" ;;
        DEBUG) [[ "${DEBUG:-false}" == "true" ]] && echo -e "[DEBUG] $message" ;;
    esac
}

#######################################
# Wrapper para GitHub API com retry
# Arguments:
#   $@ - Argumentos para gh api
# Returns:
#   Output da API ou erro
#######################################
gh_api_with_retry() {
    retry_with_backoff "gh api $*" 3 2
}

#######################################
# Wrapper para gh issue com retry
# Arguments:
#   $@ - Argumentos para gh issue
# Returns:
#   Output do comando ou erro
#######################################
gh_issue_with_retry() {
    retry_with_backoff "gh issue $*" 3 2
}

#######################################
# Wrapper para gh project com retry
# Arguments:
#   $@ - Argumentos para gh project
# Returns:
#   Output do comando ou erro
#######################################
gh_project_with_retry() {
    retry_with_backoff "gh project $*" 3 2
}

#######################################
# Verifica pre-requisitos antes de executar
# Arguments:
#   $@ - Lista de servicos a verificar
# Returns:
#   0 se todos disponiveis, 1 se algum falhou
#######################################
check_prerequisites() {
    local failed=0
    
    for service in "$@"; do
        if check_service "$service"; then
            log_with_fallback "DEBUG" "Service $service is available"
        else
            log_with_fallback "WARN" "Service $service is unavailable"
            failed=1
        fi
    done
    
    return $failed
}

#######################################
# Executa comando com timeout
# Arguments:
#   $1 - Timeout em segundos
#   $@ - Comando a executar
# Returns:
#   0 se sucesso, 124 se timeout, ou codigo de erro
#######################################
exec_with_timeout() {
    local timeout_secs="$1"
    shift
    
    if command -v timeout >/dev/null 2>&1; then
        timeout "$timeout_secs" "$@"
    elif command -v gtimeout >/dev/null 2>&1; then
        # GNU timeout no macOS via coreutils
        gtimeout "$timeout_secs" "$@"
    else
        # Fallback para sistemas sem timeout (macOS nativo)
        # Usa perl com sintaxe corrigida
        perl -e 'alarm $ARGV[0]; shift @ARGV; exec @ARGV' "$timeout_secs" "$@"
    fi
}

#######################################
# Cria lock file para evitar execucoes paralelas
# Arguments:
#   $1 - Nome do lock
#   $2 - Timeout em segundos (default: 60)
# Returns:
#   0 se lock adquirido, 1 se ja existe
#######################################
acquire_lock() {
    local lock_name="$1"
    local timeout="${2:-60}"
    local lock_file="${FALLBACK_LOG_DIR}/${lock_name}.lock"
    
    # Verificar se lock existe e nao expirou
    if [[ -f "$lock_file" ]]; then
        local lock_age=$(($(date +%s) - $(stat -c %Y "$lock_file" 2>/dev/null || stat -f %m "$lock_file" 2>/dev/null)))
        if [[ $lock_age -lt $timeout ]]; then
            log_with_fallback "WARN" "Lock $lock_name already held (age: ${lock_age}s)"
            return 1
        fi
    fi
    
    # Criar lock
    echo "$$" > "$lock_file"
    return 0
}

#######################################
# Libera lock file
# Arguments:
#   $1 - Nome do lock
#######################################
release_lock() {
    local lock_name="$1"
    local lock_file="${FALLBACK_LOG_DIR}/${lock_name}.lock"
    
    rm -f "$lock_file"
}

#######################################
# Salva estado para recuperacao posterior
# Arguments:
#   $1 - Nome do estado
#   $2 - Dados (JSON ou string)
#######################################
save_state() {
    local state_name="$1"
    local state_data="$2"
    local state_file="${FALLBACK_LOG_DIR}/state_${state_name}.json"
    
    echo "$state_data" > "$state_file"
    log_with_fallback "DEBUG" "State saved: $state_name"
}

#######################################
# Recupera estado salvo anteriormente
# Arguments:
#   $1 - Nome do estado
# Returns:
#   Conteudo do estado ou string vazia
#######################################
load_state() {
    local state_name="$1"
    local state_file="${FALLBACK_LOG_DIR}/state_${state_name}.json"
    
    if [[ -f "$state_file" ]]; then
        cat "$state_file"
    else
        echo ""
    fi
}

# Log de inicializacao se executado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Fallback Library v1.0.0"
    echo ""
    echo "Esta biblioteca deve ser importada com:"
    echo "  source .claude/lib/fallback.sh"
    echo ""
    echo "Funcoes disponiveis:"
    echo "  retry_with_backoff    - Retry com exponential backoff"
    echo "  check_service         - Verifica disponibilidade de servico"
    echo "  graceful_exec         - Executa com fallback"
    echo "  log_with_fallback     - Log para Loki + arquivo"
    echo "  gh_api_with_retry     - GitHub API com retry"
    echo "  check_prerequisites   - Verifica multiplos servicos"
    echo "  exec_with_timeout     - Executa com timeout"
    echo "  acquire_lock          - Lock para evitar parallelismo"
    echo "  save_state/load_state - Persistencia de estado"
fi
