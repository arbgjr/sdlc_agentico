---
name: logs-query
description: |
  Consulta logs do SDLC Agentico.
  Suporta Loki (se disponivel) e fallback para arquivo local.
  Use para: debugging, analise de erros, auditoria.
hooks:
  - UserPromptSubmit
---

# Logs Query Command

Consulta logs estruturados do SDLC Agentico.

## Uso

```
/logs-query [--level LEVEL] [--last TIME] [--component COMPONENT] [--grep PATTERN]
```

## Parametros

| Parametro | Descricao | Default |
|-----------|-----------|---------|
| `--level` | Filtrar por nivel (INFO, WARN, ERROR, DEBUG) | Todos |
| `--last` | Periodo (1h, 24h, 7d) | 1h |
| `--component` | Filtrar por componente | Todos |
| `--grep` | Buscar padrao no message | - |
| `--json` | Output em JSON | false |
| `--tail N` | Ultimas N linhas | 50 |

## Exemplos

### Ver ultimos erros
```bash
/logs-query --level ERROR --last 24h
```

### Ver logs do gate-evaluator
```bash
/logs-query --component gate-evaluator --tail 100
```

### Buscar por padrao
```bash
/logs-query --grep "phase transition" --last 7d
```

### Output JSON para processamento
```bash
/logs-query --level WARN --json | jq '.message'
```

## Implementacao

```bash
#!/bin/bash
# Implementacao do comando logs-query

LOG_DIR="${HOME}/.sdlc/logs"
LOKI_URL="${LOKI_URL:-http://localhost:3100}"

# Defaults
LEVEL=""
LAST="1h"
COMPONENT=""
GREP_PATTERN=""
JSON_OUTPUT=false
TAIL_LINES=50

# Parse argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --level) LEVEL="$2"; shift 2 ;;
        --last) LAST="$2"; shift 2 ;;
        --component) COMPONENT="$2"; shift 2 ;;
        --grep) GREP_PATTERN="$2"; shift 2 ;;
        --json) JSON_OUTPUT=true; shift ;;
        --tail) TAIL_LINES="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Converter periodo para segundos
case "$LAST" in
    *h) SECONDS_AGO=$((${LAST%h} * 3600)) ;;
    *d) SECONDS_AGO=$((${LAST%d} * 86400)) ;;
    *m) SECONDS_AGO=$((${LAST%m} * 60)) ;;
    *) SECONDS_AGO=3600 ;;
esac

# Calcular timestamp minimo
MIN_TIMESTAMP=$(date -d "@$(($(date +%s) - SECONDS_AGO))" -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || \
                date -r $(($(date +%s) - SECONDS_AGO)) -u +"%Y-%m-%dT%H:%M:%SZ")

# Tentar Loki primeiro
if curl -s --connect-timeout 2 "${LOKI_URL}/ready" >/dev/null 2>&1; then
    echo "Consultando Loki..."
    
    # Construir query LogQL
    QUERY='{app="sdlc"}'
    [[ -n "$COMPONENT" ]] && QUERY="{app=\"sdlc\",component=\"$COMPONENT\"}"
    [[ -n "$LEVEL" ]] && QUERY="$QUERY | level=\"$LEVEL\""
    [[ -n "$GREP_PATTERN" ]] && QUERY="$QUERY |~ \"$GREP_PATTERN\""
    
    # Executar query
    curl -s "${LOKI_URL}/loki/api/v1/query_range" \
        --data-urlencode "query=$QUERY" \
        --data-urlencode "start=$MIN_TIMESTAMP" \
        --data-urlencode "limit=$TAIL_LINES" | \
        jq -r '.data.result[].values[][1]' 2>/dev/null
else
    echo "Loki indisponivel. Consultando arquivo local..."
    
    # Usar arquivo local
    LOG_FILE="${LOG_DIR}/sdlc.jsonl"
    
    if [[ ! -f "$LOG_FILE" ]]; then
        echo "Nenhum log encontrado em $LOG_FILE"
        exit 1
    fi
    
    # Filtrar logs
    FILTER_CMD="cat \"$LOG_FILE\""
    
    [[ -n "$LEVEL" ]] && FILTER_CMD="$FILTER_CMD | jq -c 'select(.level==\"$LEVEL\")'"
    [[ -n "$COMPONENT" ]] && FILTER_CMD="$FILTER_CMD | jq -c 'select(.component==\"$COMPONENT\")'"
    [[ -n "$GREP_PATTERN" ]] && FILTER_CMD="$FILTER_CMD | grep -i \"$GREP_PATTERN\""
    
    FILTER_CMD="$FILTER_CMD | tail -n $TAIL_LINES"
    
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        eval "$FILTER_CMD"
    else
        eval "$FILTER_CMD" | while read -r line; do
            ts=$(echo "$line" | jq -r '.timestamp // "N/A"')
            level=$(echo "$line" | jq -r '.level // "INFO"')
            msg=$(echo "$line" | jq -r '.message // ""')
            comp=$(echo "$line" | jq -r '.component // "sdlc"')
            
            case "$level" in
                ERROR) echo -e "\033[0;31m[$ts] [$level] [$comp] $msg\033[0m" ;;
                WARN)  echo -e "\033[1;33m[$ts] [$level] [$comp] $msg\033[0m" ;;
                INFO)  echo -e "\033[0;34m[$ts] [$level] [$comp] $msg\033[0m" ;;
                DEBUG) echo "[$ts] [$level] [$comp] $msg" ;;
            esac
        done
    fi
fi
```

## Output Esperado

```
Consultando arquivo local...

[2026-01-16T10:30:00Z] [INFO] [orchestrator] Phase transition: 4 -> 5
[2026-01-16T10:30:05Z] [INFO] [gate-evaluator] Gate check started: phase-4-to-5
[2026-01-16T10:30:10Z] [INFO] [gate-evaluator] Gate PASSED: all criteria met
[2026-01-16T10:30:15Z] [WARN] [github-sync] GitHub API rate limit warning
[2026-01-16T10:35:00Z] [ERROR] [wiki-sync] Wiki clone failed: repository not initialized
```

## Arquivos de Log

| Arquivo | Conteudo |
|---------|----------|
| `~/.sdlc/logs/sdlc.jsonl` | Logs gerais |
| `~/.sdlc/logs/events.jsonl` | Eventos estruturados |
| `~/.sdlc/logs/metrics.jsonl` | Metricas |

## Integracao com Loki

Se Loki estiver disponivel (`LOKI_URL` configurado e servico respondendo), 
os logs sao consultados via LogQL, oferecendo:

- Busca mais rapida
- Agregacoes e estatisticas
- Dashboards no Grafana

## Fallback

Se Loki nao estiver disponivel, a consulta usa os arquivos locais JSONL,
mantendo a funcionalidade mesmo em ambientes sem infraestrutura de observabilidade.
