---
name: simulate
description: |
  Executa simulação estratégica para apoio a decisões.
  Gera cenários, análise what-if e matriz de trade-offs.
  
  Examples:
  - <example>
    Context: Comparar opções de tecnologia
    user: "/simulate --type trade_off PostgreSQL vs MongoDB vs CockroachDB"
    assistant: "Vou simular os cenários e gerar matriz de trade-offs"
    </example>
allowed-tools:
  - Read
  - Write
user-invocable: true
version: "1.0.0"
---

# /simulate

Executa simulação estratégica para apoio a decisões arquiteturais.

## Uso

```
/simulate [--type TYPE] [opções ou contexto]
```

## Tipos de Simulação

| Tipo | Descrição |
|------|-----------|
| `trade_off` | Matriz de trade-offs entre opções |
| `what_if` | Análise de impacto de mudanças |
| `scenario` | Geração de cenários alternativos |
| `risk` | Análise de riscos |

## Exemplos

### Matriz de Trade-offs
```
/simulate --type trade_off PostgreSQL vs MongoDB para e-commerce
```

### Análise What-If
```
/simulate --type what_if "E se usarmos microserviços em vez de monolito?"
```

### Geração de Cenários
```
/simulate --type scenario "Migração para cloud"
```

### Análise de Riscos
```
/simulate --type risk "Adotar Kubernetes em produção"
```

## Processo

1. **Coletar Contexto**
   - Ler requisitos e constraints
   - Buscar decisões anteriores (RAG)
   - Identificar stakeholders

2. **Definir Opções**
   - Listar alternativas viáveis
   - Documentar prós e contras

3. **Definir Critérios**
   - Identificar métricas de sucesso
   - Atribuir pesos de importância

4. **Simular Cenários**
   - Best case / Worst case / Most likely
   - Variações de parâmetros

5. **Avaliar Riscos**
   - Mapear riscos por opção
   - Definir mitigações

6. **Sintetizar Resultados**
   - Gerar ranking
   - Recomendar com justificativa

## Output Esperado

```yaml
simulation_result:
  summary:
    recommendation: string
    confidence: float (0-1)
    key_trade_offs: list
    
  trade_off_matrix:
    # scores por opção e critério
    
  risk_assessment:
    # riscos por opção
    
  next_steps:
    # ações recomendadas
```

## Templates Disponíveis

- **tech_decision**: Escolha de tecnologia
- **architecture_change**: Mudança arquitetural
- **vendor_selection**: Seleção de fornecedor
- **build_vs_buy**: Construir vs comprar
- **migration**: Migração de sistema

## Visualizações

O comando pode gerar:
- Matriz de decisão (tabela)
- Radar chart (critérios)
- Heat map (riscos)
- Decision tree (cenários)

## Integração

- Salva resultados em `.agentic_sdlc/simulations/`
- Pode gerar ADR automaticamente
- Alimenta RAG corpus para consultas futuras

## Relacionado

- `@strategic-simulator` - Agente de simulação
- `/adr-create` - Criar ADR da decisão
- `/rag-query` - Consultar decisões anteriores
