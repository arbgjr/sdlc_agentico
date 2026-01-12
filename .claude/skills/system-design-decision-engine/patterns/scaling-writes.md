# Pattern: Scaling Writes (Escalando Escritas)

## Sinais de Identificacao

- Alta taxa de escrita
- Picos de carga (eventos, promocoes)
- Contadores ou eventos (analytics, logs)
- Escritas que nao podem ser perdidas

## Perguntas Obrigatorias

1. **Qual o pico de escrita esperado?**
   - Requests por segundo no pico?
   - Quanto maior que o normal?

2. **Ordem e consistencia sao criticas?**
   - Eventos precisam estar em ordem?
   - Pode haver duplicatas?

3. **Escrita pode ser assincrona?**
   - Usuario precisa de confirmacao imediata?
   - Ou pode processar em background?

## Opcoes de Decisao

### Fila como Buffer (Queue)
- **Como funciona**: Escreve em fila, processa depois
- **Quando usar**: Picos de carga, processamento assincrono ok
- **Trade-off**: Absorve picos mas adiciona latencia

### Sharding
- **Como funciona**: Divide dados entre multiplos bancos
- **Quando usar**: Volume muito alto, dados particionaveis
- **Trade-off**: Escala horizontalmente mas queries cross-shard complexas

### Batching
- **Como funciona**: Agrupa escritas e executa em lote
- **Quando usar**: Muitas escritas pequenas
- **Trade-off**: Eficiente mas pode perder dados em crash

### Write-Ahead Log (WAL)
- **Como funciona**: Escreve em log primeiro, depois processa
- **Quando usar**: Durabilidade critica
- **Trade-off**: Duravel mas overhead de I/O

## Garantias de Entrega

| Garantia | Descricao | Uso |
|----------|-----------|-----|
| At-most-once | Pode perder, nunca duplica | Logs, metricas |
| At-least-once | Nunca perde, pode duplicar | Eventos de negocio |
| Exactly-once | Nem perde nem duplica | Transacoes financeiras |

## Modos de Falha Comuns

| Falha | Causa | Mitigacao |
|-------|-------|-----------|
| Perda de dados | Fila cheia ou crash | Dead letter queue, persistencia |
| Escritas fora de ordem | Processamento paralelo | Sequence numbers, ordenacao |
| Hotspots em shards | Sharding key mal escolhida | Analise de distribuicao |
| Racing conditions | Escritas concorrentes | Idempotencia, versioning |

## Idempotencia

Toda escrita deve ser idempotente quando possivel:
- Usar ID unico por operacao
- Verificar se ja foi processada antes de executar
- Retornar mesmo resultado para mesma entrada

## Exemplo de Decisao

**Cenario**: Sistema de analytics recebendo 100K eventos/segundo em pico

**Analise**:
- Pico 10x maior que media
- Ordem nao e critica
- Processamento pode ser assincrono
- Perder alguns eventos e aceitavel

**Decisao**: Kafka como buffer + processamento em batch
- Eventos vao para Kafka (absorve pico)
- Consumer processa em batches de 1000
- At-least-once delivery com dedup por event_id
- Trade-off aceito: latencia de segundos em troca de throughput alto
