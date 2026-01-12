# Pattern: Long Running Tasks (Tarefas de Longa Duracao)

## Sinais de Identificacao

- Operacoes que demoram mais que timeout HTTP (~30s)
- Processamento pesado (video, relatorios, ML)
- Timeout em requisicoes
- Usuario nao pode esperar bloqueado

## Perguntas Obrigatorias

1. **A pessoa usuaria pode esperar?**
   - Segundos? Minutos? Horas?
   - Define se precisa ser async

2. **O progresso precisa ser consultavel?**
   - Usuario quer ver % completo?
   - Ou so saber quando terminou?

3. **O job pode falhar parcialmente?**
   - Pode processar metade e parar?
   - Precisa de tudo ou nada?

## Opcoes de Decisao

### Modelo Assincrono (Request-Response)
- **Como funciona**: Request retorna job_id, cliente consulta status
- **Quando usar**: Qualquer task longa
- **Trade-off**: Padrao universal, polling necessario

### Webhook/Callback
- **Como funciona**: Sistema notifica ao completar
- **Quando usar**: Integracao entre sistemas
- **Trade-off**: Nao precisa polling mas precisa endpoint publico

### WebSocket para Progresso
- **Como funciona**: Conexao persistente com updates de progresso
- **Quando usar**: UI com barra de progresso
- **Trade-off**: UX melhor mas mais complexo

## Arquitetura Recomendada

```
[API] --> [Queue] --> [Workers]
  |                      |
  v                      v
[Job Status DB] <--------+
  ^
  |
[Cliente consulta status]
```

## Estados de Job

| Estado | Descricao |
|--------|-----------|
| PENDING | Na fila, aguardando worker |
| RUNNING | Em processamento |
| COMPLETED | Finalizado com sucesso |
| FAILED | Falhou (ver mensagem de erro) |
| CANCELLED | Cancelado pelo usuario |

## Modos de Falha Comuns

| Falha | Causa | Mitigacao |
|-------|-------|-----------|
| Jobs perdidos | Worker morreu sem ack | Visibility timeout + retry |
| Duplicacao de execucao | Retry sem idempotencia | Idempotency key por job |
| Falta de monitoramento | Jobs presos sem alerta | Health checks, alertas |
| Sem limite de retry | Retry infinito em job quebrado | Max retries + DLQ |

## Estrategias de Retry

1. **Exponential backoff**: 1s, 2s, 4s, 8s...
2. **Max retries**: Limitar tentativas (ex: 3)
3. **Dead Letter Queue**: Jobs que falharam demais vao para DLQ
4. **Circuit breaker**: Parar de tentar se muitos falhando

## Checkpointing

Para jobs muito longos:
- Salvar progresso periodicamente
- Se falhar, retomar do checkpoint
- Util para processamento de grandes datasets

## Exemplo de Decisao

**Cenario**: Geracao de relatorio PDF com milhoes de registros

**Analise**:
- Duracao: 5-30 minutos
- Usuario quer ver progresso
- Pode falhar no meio (memoria, timeout)

**Decisao**: Job assincrono com checkpointing
- API retorna job_id imediatamente
- Worker processa em chunks de 10K registros
- Checkpoint a cada chunk (pode retomar)
- WebSocket para progresso em tempo real
- DLQ para jobs que falharam 3x
- Trade-off aceito: complexidade de checkpointing em troca de reliability
