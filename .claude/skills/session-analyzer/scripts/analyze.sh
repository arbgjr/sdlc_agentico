#!/bin/bash
#
# Session Analyzer - Script wrapper para análise de sessões
#
# Uso:
#   ./analyze.sh                    # Analisar sessão mais recente
#   ./analyze.sh --persist          # Analisar e persistir
#   ./analyze.sh --extract-learnings # Extrair e salvar learnings no RAG
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Script está em .claude/skills/session-analyzer/scripts/
# Precisa subir 4 níveis para chegar ao root do projeto
PROJECT_ROOT="${SCRIPT_DIR}/../../../.."

# Carregar biblioteca de fallback
if [[ -f "${PROJECT_ROOT}/.claude/lib/fallback.sh" ]]; then
    source "${PROJECT_ROOT}/.claude/lib/fallback.sh"
fi

# Defaults
PERSIST=false
EXTRACT_LEARNINGS=false
PROJECT_PATH=$(pwd)
OUTPUT_DIR="${PROJECT_ROOT}/.agentic_sdlc/sessions"
CORPUS_DIR="${PROJECT_ROOT}/.agentic_sdlc/corpus/learnings"

# Parse argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --persist)
            PERSIST=true
            shift
            ;;
        --extract-learnings)
            EXTRACT_LEARNINGS=true
            PERSIST=true
            shift
            ;;
        --project)
            PROJECT_PATH="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

log_with_fallback "INFO" "Iniciando análise de sessão" "session-analyzer" 2>/dev/null || echo "[INFO] Iniciando análise de sessão"

# Executar script Python
PYTHON_SCRIPT="${SCRIPT_DIR}/extract_learnings.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    log_with_fallback "ERROR" "Script extract_learnings.py não encontrado" "session-analyzer" 2>/dev/null
    exit 1
fi

# Construir comando
CMD="python3 \"$PYTHON_SCRIPT\" --project \"$PROJECT_PATH\""

if [[ "$PERSIST" == "true" ]]; then
    CMD="$CMD --persist --output-dir \"$OUTPUT_DIR\""
fi

# Executar
eval "$CMD"
RESULT=$?

if [[ $RESULT -ne 0 ]]; then
    log_with_fallback "WARN" "Análise de sessão falhou ou não encontrou sessões" "session-analyzer" 2>/dev/null
    exit $RESULT
fi

# Se extract-learnings, copiar para corpus do RAG
if [[ "$EXTRACT_LEARNINGS" == "true" ]]; then
    log_with_fallback "INFO" "Extraindo learnings para RAG corpus" "session-analyzer" 2>/dev/null || echo "[INFO] Extraindo learnings para RAG corpus"
    
    # Criar diretório do corpus se não existe
    mkdir -p "$CORPUS_DIR"
    
    # Encontrar arquivo de análise mais recente
    LATEST_ANALYSIS=$(ls -t "$OUTPUT_DIR"/session-*.yml 2>/dev/null | head -1)
    
    if [[ -n "$LATEST_ANALYSIS" ]]; then
        # Extrair learnings do arquivo YAML
        if command -v yq >/dev/null 2>&1; then
            # Usar yq se disponível
            yq '.session_analysis.learnings' "$LATEST_ANALYSIS" > "${CORPUS_DIR}/learnings-$(date +%Y%m%d).yml"
        else
            # Fallback: copiar arquivo completo
            cp "$LATEST_ANALYSIS" "${CORPUS_DIR}/"
        fi
        
        log_with_fallback "INFO" "Learnings salvos em $CORPUS_DIR" "session-analyzer" 2>/dev/null || echo "[INFO] Learnings salvos em $CORPUS_DIR"
    fi
fi

log_with_fallback "INFO" "Análise de sessão concluída" "session-analyzer" 2>/dev/null || echo "[INFO] Análise de sessão concluída"
exit 0
