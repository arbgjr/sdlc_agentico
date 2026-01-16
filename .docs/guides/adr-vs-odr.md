# ADR vs ODR: Quando Usar Cada Um

## Visão Geral

O SDLC Agêntico utiliza dois tipos de registros de decisão:

| Tipo | Nome Completo | Foco |
|------|---------------|------|
| **ADR** | Architecture Decision Record | Decisões **técnicas** |
| **ODR** | Organizational Decision Record | Decisões **organizacionais/negócio** |

## Quando Usar ADR

Use ADR para decisões que afetam a **arquitetura técnica** ou **implementação**:

### Exemplos de ADRs
- Escolha de banco de dados (PostgreSQL vs MongoDB)
- Padrão de autenticação (OAuth2 vs JWT)
- Arquitetura de microsserviços vs monolito
- Framework de frontend (React vs Vue)
- Estratégia de caching
- Padrão de API (REST vs GraphQL)
- Linguagem de programação para novo serviço

### Características de ADRs
- Decisor geralmente é **tech lead** ou **arquiteto**
- Impacto primário na **codebase**
- Reversibilidade geralmente **técnica** (refatoração, migração)
- Stakeholders são principalmente **técnicos**

## Quando Usar ODR

Use ODR para decisões que afetam a **organização, negócio ou recursos**:

### Exemplos de ODRs
- Mudança de budget do projeto (±10%)
- Alteração de timeline ou escopo
- Decisão de build vs buy
- Mudança de stakeholders chave
- Priorização entre features conflitantes
- Alocação/realocação de equipe
- Mudança de fornecedor ou parceiro
- Pivô de estratégia de produto
- Go/no-go para lançamento

### Características de ODRs
- Decisor geralmente é **PM**, **PO** ou **C-level**
- Impacto primário no **negócio**, **budget** ou **pessoas**
- Reversibilidade pode ter **custo organizacional**
- Stakeholders incluem **não-técnicos**

## Fluxo de Decisão

```
Necessidade de decisão identificada
            │
            ▼
    ┌───────────────────┐
    │  A decisão afeta  │
    │  principalmente:  │
    └───────┬───────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌───────┐     ┌───────────────┐
│Código │     │ Budget/Escopo/│
│Arquit.│     │ Timeline/Team │
│Sistema│     │ Estratégia    │
└───┬───┘     └───────┬───────┘
    │                 │
    ▼                 ▼
  ADR               ODR
```

## Relacionamentos

ODRs frequentemente **geram** ADRs:

```
ODR-001: Decidimos fazer build interno (vs comprar solução)
    │
    └─► ADR-015: Arquitetura do sistema interno
    └─► ADR-016: Stack tecnológica escolhida
    └─► ADR-017: Estratégia de deploy
```

ADRs podem **requerer** ODRs:

```
ADR proposto: Migrar para Kubernetes
    │
    └─► ODR necessário: Aprovação de budget para infra
    └─► ODR necessário: Treinamento da equipe
```

## Integração com Gates SDLC

### Gates que requerem ODRs (Level 2-3)

| Gate | Quando ODR é obrigatório |
|------|--------------------------|
| Phase 2→3 | Budget > R$100k |
| Phase 3→4 | 3+ stakeholders impactados |
| Phase 6→7 | Mudança de escopo significativa |
| Qualquer | Decisão estratégica identificada |

### Verificação Automática

O `gate-evaluator` verifica automaticamente se ODRs necessários foram criados:

```yaml
# gates/phase-2-to-3.yml
criteria:
  - name: "odr_check"
    type: conditional
    condition: "project.budget > 100000"
    required: "odr exists with category='resource' and status='approved'"
```

## Templates

### Localização dos Templates

| Tipo | Template |
|------|----------|
| ADR | `.agentic_sdlc/templates/adr-template.yml` |
| ODR | `.agentic_sdlc/templates/odr-template.yml` |

### Comandos

```bash
# Criar ADR
/adr-create "Título da decisão técnica"

# Criar ODR
/odr-create "Título da decisão organizacional"

# Ver status de decisões
/alignment-status
```

## Resumo Rápido

| Aspecto | ADR | ODR |
|---------|-----|-----|
| **Foco** | Técnico | Organizacional |
| **Decisor** | Tech Lead/Arquiteto | PM/PO/C-level |
| **Stakeholders** | Devs, Ops | Negócio, Finance, RH |
| **Impacto** | Codebase | Budget, Timeline, Pessoas |
| **Reversão** | Refatoração | Custo organizacional |
| **Gate** | Sempre relevante | Obrigatório em Level 2-3 |

---

> **Dica**: Na dúvida, pergunte: "Quem precisa aprovar isso?" 
> - Se for principalmente técnico → ADR
> - Se envolver negócio, budget ou pessoas → ODR
