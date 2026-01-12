# Matriz de Trade-offs em System Design

Este documento apresenta os trade-offs mais comuns em decisoes de arquitetura. Todo trade-off deve ser explicitado e aceito conscientemente.

## Regra de Ouro

> **Nao existe almoco gratis em arquitetura de sistemas.**
> Toda decisao tem custo. O objetivo e escolher o custo que voce pode pagar.

## Trade-offs Fundamentais

### Consistencia vs Latencia

| Escolha | Ganha | Perde |
|---------|-------|-------|
| Consistencia forte | Dados sempre corretos | Latencia maior, menos throughput |
| Eventual consistency | Baixa latencia, alta escala | Dados temporariamente incorretos |

**Quando escolher consistencia forte:**
- Transacoes financeiras
- Inventario/estoque
- Qualquer operacao onde erro custa dinheiro

**Quando escolher eventual consistency:**
- Feeds de redes sociais
- Analytics e metricas
- Caches de leitura

### Disponibilidade vs Consistencia (CAP Theorem)

Em caso de particao de rede, escolher:

| Escolha | Comportamento | Exemplo |
|---------|---------------|---------|
| CP (Consistency) | Sistema recusa operacoes | Banco de dados tradicional |
| AP (Availability) | Sistema responde com dados potencialmente stale | DNS, CDN |

### Sincrono vs Assincrono

| Escolha | Ganha | Perde |
|---------|-------|-------|
| Sincrono | Simplicidade, feedback imediato | Acoplamento, menos resiliente |
| Assincrono | Desacoplamento, absorve picos | Complexidade, debugging mais dificil |

**Sincrono quando:**
- Resposta e necessaria imediatamente
- Fluxo simples e linear
- Sistema pequeno

**Assincrono quando:**
- Operacao pode falhar e precisa retry
- Picos de carga esperados
- Multiplos consumidores do mesmo evento

### Custo vs Complexidade vs Resiliencia

```
Simples & Barato --> Menos resiliente
Resiliente --> Mais complexo e caro
```

| Nivel | Arquitetura | Custo | Complexidade |
|-------|-------------|-------|--------------|
| Basico | Single server | $ | Baixa |
| Medio | Multi-AZ | $$ | Media |
| Alto | Multi-region | $$$ | Alta |

### Latencia vs Throughput

| Otimizar para | Estrategia | Trade-off |
|---------------|------------|-----------|
| Latencia | Mais recursos, menos batching | Custo maior |
| Throughput | Batching, filas | Latencia maior |

### Flexibilidade vs Performance

| Escolha | Exemplo | Trade-off |
|---------|---------|-----------|
| Flexivel | Schemaless (MongoDB) | Queries mais lentas |
| Otimizado | Schema rigido com indices | Mudancas mais dificeis |

## Trade-offs por Dominio

### Banco de Dados

| SQL vs NoSQL |
|--------------|
| SQL: Consistencia, transacoes, queries complexas |
| NoSQL: Escala horizontal, schema flexivel, latencia |

| Normalizacao vs Denormalizacao |
|-------------------------------|
| Normalizado: Menos redundancia, updates simples |
| Denormalizado: Leituras rapidas, updates complexos |

### Cache

| Cache-aside vs Write-through |
|-----------------------------|
| Cache-aside: Simples, pode ter cache miss |
| Write-through: Sempre atualizado, mais lento na escrita |

### Mensageria

| Push vs Pull |
|--------------|
| Push: Latencia baixa, precisa gerenciar backpressure |
| Pull: Consumer controla ritmo, latencia maior |

| At-least-once vs Exactly-once |
|------------------------------|
| At-least-once: Mais simples, precisa de idempotencia |
| Exactly-once: Mais complexo, overhead de coordenacao |

## Framework de Decisao

Para cada decisao arquitetural, responder:

1. **Qual o requisito principal?** (latencia, throughput, consistencia, custo)
2. **Qual o custo aceitavel?** (dinheiro, complexidade, pessoas)
3. **Qual falha e toleravel?** (dados stale, indisponibilidade temporaria)
4. **Quanto tempo tenho?** (MVP vs solucao definitiva)

## Anti-patterns de Trade-off

### "Queremos tudo"
- Nao existe sistema com maxima consistencia, disponibilidade, latencia minima E custo baixo
- Forcar priorizacao

### "Vamos ver depois"
- Trade-offs nao explicitados viram divida tecnica
- Documentar decisoes

### "Sempre funcionou"
- Contexto muda, trade-offs mudam
- Revisar periodicamente

### "O framework resolve"
- Frameworks sao ferramentas, nao magica
- Entender o que acontece por baixo
