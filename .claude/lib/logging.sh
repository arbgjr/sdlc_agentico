#!/bin/bash
#
# Logging Library - Funcoes para logging estruturado com suporte a Loki
#
# Uso:
#   source .claude/lib/logging.sh
#
# Funcoes disponiveis:
#   log_info <message> [component]
#   log_warn <message> [component]
#   log_error <message> [component]
#   log_debug <message> [component]
#   log_event <event_type> <event_data> [component]
#

# Dependencia
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/fallback.sh" ]]; then
    source "${SCRIPT_DIR}/fallback.sh"
fi

# Configuracoes adicionais
LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_FORMAT="${LOG_FORMAT:-json}"  # json ou text

# Niveis de log
declare -A LOG_LEVELS
LOG_LEVELS[DEBUG]=0
LOG_LEVELS[INFO]=1
LOG_LEVELS[WARN]=2
LOG_LEVELS[ERROR]=3

#######################################
# Verifica se nivel de log deve ser exibido
# Arguments:
#   $1 - Nivel do log
# Returns:
#   0 se deve exibir, 1 se nao
#######################################
should_log() {
    local level="$1"
    local current_level="${LOG_LEVELS[$LOG_LEVEL]:-1}"
    local msg_level="${LOG_LEVELS[$level]:-1}"
    
    [[ $msg_level -ge $current_level ]]
}

#######################################
# Log de nivel INFO
#######################################
log_info() {
    local message="$1"
    local component="${2:-sdlc}"
    
    if should_log INFO; then
        log_with_fallback "INFO" "$message" "$component"
    fi
}

#######################################
# Log de nivel WARN
#######################################
log_warn() {
    local message="$1"
    local component="${2:-sdlc}"
    
    if should_log WARN; then
        log_with_fallback "WARN" "$message" "$component"
    fi
}

#######################################
# Log de nivel ERROR
#######################################
log_error() {
    local message="$1"
    local component="${2:-sdlc}"
    
    if should_log ERROR; then
        log_with_fallback "ERROR" "$message" "$component"
    fi
}

#######################################
# Log de nivel DEBUG
#######################################
log_debug() {
    local message="$1"
    local component="${2:-sdlc}"
    
    if should_log DEBUG; then
        log_with_fallback "DEBUG" "$message" "$component"
    fi
}

#######################################
# Log de evento estruturado
# Arguments:
#   $1 - Tipo do evento (phase_start, gate_check, etc)
#   $2 - Dados do evento (JSON)
#   $3 - Componente
#######################################
log_event() {
    local event_type="$1"
    local event_data="$2"
    local component="${3:-sdlc}"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Criar evento JSON completo
    local event_json=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "event_type": "$event_type",
  "component": "$component",
  "data": $event_data
}
EOF
)
    
    # Salvar em arquivo de eventos
    echo "$event_json" >> "${FALLBACK_LOG_DIR}/events.jsonl"
    
    # Log regular
    log_info "Event: $event_type" "$component"
}

#######################################
# Inicia trace de execucao
# Arguments:
#   $1 - Nome do trace
# Returns:
#   ID do trace
#######################################
trace_start() {
    local trace_name="$1"
    local trace_id=$(date +%s%N | md5sum | cut -c1-8)
    local start_time=$(date +%s%N)
    
    # Salvar estado do trace
    save_state "trace_${trace_id}" "{\"name\":\"$trace_name\",\"start\":$start_time}"
    
    log_debug "Trace started: $trace_name (ID: $trace_id)"
    echo "$trace_id"
}

#######################################
# Finaliza trace de execucao
# Arguments:
#   $1 - ID do trace
#   $2 - Status (success, error, timeout)
#######################################
trace_end() {
    local trace_id="$1"
    local status="${2:-success}"
    local end_time=$(date +%s%N)
    
    # Carregar estado do trace
    local trace_data=$(load_state "trace_${trace_id}")
    
    if [[ -n "$trace_data" ]]; then
        local trace_name=$(echo "$trace_data" | jq -r '.name // "unknown"')
        local start_time=$(echo "$trace_data" | jq -r '.start // 0')
        local duration_ns=$((end_time - start_time))
        local duration_ms=$((duration_ns / 1000000))
        
        log_event "trace_complete" "{\"trace_id\":\"$trace_id\",\"name\":\"$trace_name\",\"status\":\"$status\",\"duration_ms\":$duration_ms}"
        
        # Limpar estado
        rm -f "${FALLBACK_LOG_DIR}/state_trace_${trace_id}.json"
        
        log_debug "Trace completed: $trace_name (${duration_ms}ms, status: $status)"
    fi
}

#######################################
# Log de metricas
# Arguments:
#   $1 - Nome da metrica
#   $2 - Valor
#   $3 - Tipo (counter, gauge, histogram)
#   $4 - Labels (JSON)
#######################################
log_metric() {
    local metric_name="$1"
    local value="$2"
    local metric_type="${3:-gauge}"
    local labels="${4:-{}}"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    local metric_json=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "metric": "$metric_name",
  "value": $value,
  "type": "$metric_type",
  "labels": $labels
}
EOF
)
    
    echo "$metric_json" >> "${FALLBACK_LOG_DIR}/metrics.jsonl"
}

#######################################
# Rotaciona logs antigos
# Arguments:
#   $1 - Dias para manter (default: 7)
#######################################
rotate_logs() {
    local days_to_keep="${1:-7}"
    
    find "$FALLBACK_LOG_DIR" -name "*.jsonl" -mtime "+$days_to_keep" -exec gzip {} \; 2>/dev/null
    find "$FALLBACK_LOG_DIR" -name "*.jsonl.gz" -mtime "+$((days_to_keep * 2))" -delete 2>/dev/null
    
    log_info "Logs rotated (keeping ${days_to_keep} days)"
}

# Exportar funcoes
export -f log_info log_warn log_error log_debug log_event
export -f trace_start trace_end log_metric rotate_logs
