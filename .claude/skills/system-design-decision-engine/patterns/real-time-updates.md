# Pattern: Real-time Updates (Atualizacoes em Tempo Real)

## Sinais de Identificacao

- Notificacoes imediatas necessarias
- Interacao bidirecional
- Estado compartilhado entre usuarios
- Dashboards ao vivo, chat, jogos

## Perguntas Obrigatorias

1. **Qual a latencia maxima aceitavel?**
   - Milissegundos? Segundos?
   - Define tecnologia viavel

2. **Quantas conexoes simultaneas?**
   - Centenas? Milhares? Milhoes?
   - Afeta arquitetura de servidores

3. **Mensagens precisam ser persistidas?**
   - Pode perder se usuario offline?
   - Precisa de replay ao reconectar?

## Opcoes de Decisao

### Polling
- **Como funciona**: Cliente faz requests periodicos
- **Quando usar**: Latencia de segundos aceitavel, poucos clientes
- **Trade-off**: Simples mas ineficiente e com delay

### Long Polling
- **Como funciona**: Request fica aberto ate ter dados
- **Quando usar**: Latencia sub-segundo, compatibilidade com firewalls
- **Trade-off**: Melhor que polling mas ainda ineficiente

### Server-Sent Events (SSE)
- **Como funciona**: Conexao unidirecional server->client
- **Quando usar**: Updates unidirecionais (notificacoes, feeds)
- **Trade-off**: Simples, HTTP nativo, mas so server->client

### WebSocket
- **Como funciona**: Conexao bidirecional persistente
- **Quando usar**: Chat, jogos, colaboracao real-time
- **Trade-off**: Mais eficiente mas precisa de infra especifica

## Arquitetura de Pub/Sub

Para escalar real-time, usar pub/sub:

```
[Clientes] <--WebSocket--> [Servidores WS] <--Pub/Sub--> [Redis/Kafka]
                                ^
                                |
                         [Load Balancer]
```

- Servidores WS mantem conexoes
- Pub/Sub distribui mensagens entre servidores
- Sticky sessions ou broadcast pattern

## Modos de Falha Comuns

| Falha | Causa | Mitigacao |
|-------|-------|-----------|
| Conexoes perdidas | Rede instavel | Reconexao automatica com backoff |
| Mensagens fora de ordem | Rede ou processamento | Sequence numbers |
| Sobrecarga do servidor | Muitas conexoes | Horizontal scaling, connection limits |
| Mensagens perdidas | Desconexao | Persistencia + replay |

## Estrategias de Reconexao

1. **Exponential backoff**: Aumentar delay entre tentativas
2. **Jitter**: Adicionar aleatoriedade para evitar thundering herd
3. **Last event ID**: Retomar de onde parou
4. **Heartbeat**: Detectar conexao morta rapidamente

## Exemplo de Decisao

**Cenario**: Chat para aplicativo com 100K usuarios simultaneos

**Analise**:
- Latencia: sub-100ms desejavel
- Conexoes: 100K simultaneas
- Mensagens precisam ser persistidas para historico

**Decisao**: WebSocket + Redis Pub/Sub + PostgreSQL
- WebSocket para conexao bidirecional
- Redis Pub/Sub para distribuir entre servidores
- PostgreSQL para persistir historico
- Reconexao com last_message_id para replay
- Trade-off aceito: complexidade de infra em troca de experiencia real-time
