# Pattern: Scaling Reads (Escalando Leituras)

## Sinais de Identificacao

- Alta proporcao de leituras vs escritas (ex: 100:1)
- Leituras repetidas dos mesmos dados
- Latencia sensivel (usuarios esperando resposta)
- Conteudo que muda pouco frequentemente

## Perguntas Obrigatorias

1. **Qual a proporcao leitura vs escrita?**
   - 10:1? 100:1? 1000:1?
   - Quanto maior, mais cache ajuda

2. **Qual tolerancia a dados levemente desatualizados?**
   - Segundos? Minutos? Horas?
   - Define TTL do cache

3. **Existe conteudo estatico ou altamente cacheavel?**
   - Imagens, CSS, JS?
   - Dados de catalogo que mudam raramente?

## Opcoes de Decisao

### Cache Local (In-Memory)
- **Como funciona**: Cache na memoria da aplicacao
- **Quando usar**: Dados pequenos, latencia critica
- **Trade-off**: Rapido mas inconsistente entre instancias

### Cache Distribuido (Redis/Memcached)
- **Como funciona**: Cache compartilhado entre instancias
- **Quando usar**: Multiplas instancias, dados medios
- **Trade-off**: Consistente mas adiciona hop de rede

### Read Replicas (Database)
- **Como funciona**: Replicas do banco apenas para leitura
- **Quando usar**: Queries complexas, dados grandes
- **Trade-off**: Escalavel mas com replication lag

### CDN
- **Como funciona**: Cache geograficamente distribuido
- **Quando usar**: Conteudo estatico, usuarios globais
- **Trade-off**: Muito rapido mas invalidacao complexa

## Estrategias de Invalidacao

| Estrategia | Descricao | Uso |
|------------|-----------|-----|
| TTL fixo | Cache expira apos tempo | Dados que podem estar stale |
| Write-through | Atualiza cache na escrita | Consistencia importante |
| Write-behind | Atualiza cache, depois DB | Performance de escrita |
| Cache-aside | App gerencia cache | Controle fino |

## Modos de Falha Comuns

| Falha | Causa | Mitigacao |
|-------|-------|-----------|
| Cache sem invalidacao | Dados stale eternamente | TTL obrigatorio |
| Cache stampede | Muitos requests quando cache expira | Locking ou jitter no TTL |
| Replicas sem roteamento | Leituras indo pro primary | Configuracao de connection pool |
| Hot keys | Uma key muito acessada | Sharding da key ou cache local |

## Exemplo de Decisao

**Cenario**: Catalogo de produtos com 1M de itens, 10K req/s de leitura

**Analise**:
- Proporcao leitura/escrita: 1000:1
- Tolerancia a stale: 5 minutos aceitavel
- Produtos mudam raramente

**Decisao**: Cache distribuido (Redis) + CDN para imagens
- Redis com TTL de 5 minutos para dados de produto
- CDN para imagens com TTL de 24h
- Write-through na atualizacao de produto
- Trade-off aceito: 5 min de delay em updates em troca de latencia sub-10ms
