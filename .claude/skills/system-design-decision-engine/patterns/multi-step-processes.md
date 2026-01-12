# Pattern: Multi-step Processes (Processos Multi-etapa)

## Sinais de Identificacao

- Fluxo com varias etapas sequenciais
- Dependencia entre passos
- Falhas intermediarias possiveis
- Checkout, onboarding, pipelines

## Perguntas Obrigatorias

1. **Os passos sao reversiveis?**
   - Pode desfazer uma etapa?
   - Ou compensar de outra forma?

2. **Quanto tempo o fluxo pode durar?**
   - Segundos? Minutos? Dias?
   - Afeta persistencia de estado

3. **Estado precisa sobreviver a restart?**
   - Sistema pode reiniciar no meio?
   - Estado e efemero ou duravel?

## Opcoes de Decisao

### Saga com Compensacao
- **Como funciona**: Cada passo tem acao de compensacao (rollback)
- **Quando usar**: Transacoes distribuidas, microservices
- **Trade-off**: Flexivel mas complexidade de compensacoes

### Workflow Engine (Temporal, Step Functions)
- **Como funciona**: Engine gerencia estado e execucao
- **Quando usar**: Fluxos complexos, durabilidade critica
- **Trade-off**: Poderoso mas adiciona dependencia

### State Machine Manual
- **Como funciona**: Estados e transicoes no banco de dados
- **Quando usar**: Fluxos simples, controle total
- **Trade-off**: Simples mas reprojetado para cada caso

## Tipos de Saga

### Saga Coreografada
```
[Servico A] --evento--> [Servico B] --evento--> [Servico C]
```
- Cada servico escuta eventos e reage
- Descentralizado
- Dificil de rastrear fluxo completo

### Saga Orquestrada
```
[Orquestrador] --> [A] --> [B] --> [C]
      |             |       |       |
      +<--status----+-------+-------+
```
- Orquestrador central controla fluxo
- Facil de entender e monitorar
- Single point of failure no orquestrador

## Garantias Importantes

| Garantia | Implementacao |
|----------|---------------|
| Idempotencia | ID unico por passo, verificar antes de executar |
| Ordenacao | Sequence number ou depends_on explicito |
| Atomicidade | Transacao por passo ou compensacao |
| Visibilidade | Log de cada transicao de estado |

## Modos de Falha Comuns

| Falha | Causa | Mitigacao |
|-------|-------|-----------|
| Inconsistencia de dados | Passo 2 falhou, passo 1 commitado | Compensacao ou retry |
| Fluxos presos | Passo travou sem timeout | Timeouts + alertas |
| Falta de monitoramento | Nao sabe onde esta o fluxo | Dashboard de estados |
| Compensacao falha | Rollback nao funciona | Retry da compensacao + alerta manual |

## Padrao de Implementacao

```
1. Criar registro do fluxo (status: STARTED)
2. Para cada passo:
   a. Verificar se ja executou (idempotencia)
   b. Executar passo
   c. Atualizar status
   d. Se falhar: marcar para retry ou compensar
3. Ao completar: status = COMPLETED
4. Se falhar apos max retries: status = FAILED, executar compensacoes
```

## Exemplo de Decisao

**Cenario**: Checkout de e-commerce (reservar estoque, cobrar, enviar)

**Analise**:
- 3 passos: reserva, pagamento, envio
- Pagamento pode falhar (cartao recusado)
- Se falhar, precisa liberar estoque

**Decisao**: Saga orquestrada com compensacao
- Orquestrador coordena os 3 passos
- Cada passo tem compensacao:
  - Reserva -> Liberar estoque
  - Pagamento -> Estornar
  - Envio -> (sem compensacao, ja foi)
- Estado persistido em PostgreSQL
- Timeout de 30min para pagamento
- Trade-off aceito: complexidade de orquestrador em troca de consistencia
