# Pattern: Contention (Contencao de Recursos)

## Sinais de Identificacao

- Concorrencia sobre o mesmo recurso
- Leitura seguida de escrita (read-modify-write)
- Sistemas de estoque ou reserva
- Multiplos usuarios disputando item limitado

## Perguntas Obrigatorias

1. **Quantas pessoas disputam o mesmo recurso simultaneamente?**
   - Dezenas? Centenas? Milhares?
   - Isso define se locking e viavel

2. **Consistencia forte e obrigatoria?**
   - Pode haver overbooking temporario?
   - Qual o custo de uma venda duplicada?

3. **Erro pode ser devolvido para a pessoa usuaria?**
   - Usuario pode tentar novamente?
   - Ou precisa de garantia de sucesso?

## Opcoes de Decisao

### Optimistic Concurrency
- **Como funciona**: Leitura sem lock, validacao no momento da escrita (versioning)
- **Quando usar**: Baixa contencao, conflitos raros
- **Trade-off**: Simples mas pode ter muitos retries sob alta carga

### Pessimistic Locking
- **Como funciona**: Lock no recurso antes da leitura
- **Quando usar**: Alta contencao, conflitos frequentes
- **Trade-off**: Seguro mas pode causar deadlocks e reducao de throughput

### Reservation Pattern
- **Como funciona**: Reserva temporaria com expiracao (TTL)
- **Quando usar**: Carrinho de compras, reserva de assento
- **Trade-off**: Complexidade adicional, precisa de cleanup de reservas expiradas

## Modos de Falha Comuns

| Falha | Causa | Mitigacao |
|-------|-------|-----------|
| Deadlocks | Locks em ordem diferente | Ordenar aquisicao de locks |
| Starvation | Requests sempre perdendo | Filas com prioridade/fairness |
| Lost Updates | Race condition na escrita | Versionamento ou CAS |
| Racing Conditions | Verificacao e acao nao-atomicas | Transacoes ou locks |

## Exemplo de Decisao

**Cenario**: Sistema de venda de ingressos para show popular

**Analise**:
- 10.000 pessoas disputando 100 ingressos
- Consistencia forte obrigatoria (nao pode vender mais que tem)
- Usuario pode receber erro e tentar novamente

**Decisao**: Reservation Pattern com TTL de 10 minutos
- Usuario "reserva" ingresso temporariamente
- Tem 10 minutos para completar pagamento
- Se expirar, ingresso volta ao pool
- Trade-off aceito: complexidade de cleanup em troca de UX melhor
