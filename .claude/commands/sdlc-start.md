---
description: "Inicia um novo workflow SDLC para um projeto ou feature"
argument-hint: "[descricao do projeto/feature]"
---

# Iniciar Workflow SDLC

Voce esta iniciando um novo workflow de desenvolvimento. Siga estes passos:

## 1. Detectar Nivel de Complexidade

Analise a descricao fornecida e classifique:

**Level 0 - Quick Flow** (~5 min)
- Bug fix, typo, correcao simples
- Pular para Fase 5 (Implementacao)

**Level 1 - Feature** (~15 min)
- Feature em servico existente
- Executar Fases 2, 5, 6

**Level 2 - Full SDLC** (~30 min+)
- Novo produto, servico ou integracao
- Executar todas as fases

**Level 3 - Enterprise** (variavel)
- Compliance, multi-team, critico
- Todas as fases + aprovacao humana em cada gate

## 2. Iniciar Memoria do Projeto

Use @memory-manager para:
- Criar registro do projeto
- Definir fase inicial
- Registrar complexidade detectada

## 3. Executar Fase Inicial

### Se Level 0:
- Va direto para implementacao
- Use @code-author e @code-reviewer

### Se Level 1:
- Inicie com @requirements-analyst
- Pule arquitetura detalhada

### Se Level 2+:
- Inicie com @intake-analyst (Fase 0)
- Siga o fluxo completo

## 4. Formato de Saida

```yaml
sdlc_initiated:
  project_id: string
  description: string
  complexity_level: number
  starting_phase: number
  agents_needed: list[string]
  estimated_duration: string
  next_steps:
    - step: string
      agent: string
```

## 5. Proximos Passos

Apos iniciar, use:
- `/phase-status` para ver progresso
- `/gate-check` para avaliar transicao de fase

---

Descricao do projeto/feature: $ARGUMENTS
