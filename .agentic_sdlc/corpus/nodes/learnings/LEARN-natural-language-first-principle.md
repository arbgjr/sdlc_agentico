# Natural Language First: Análise Profunda do SDLC Agêntico

**Created**: 2026-01-31
**Type**: Learning / Best Practices
**Status**: Active
**Confidence**: 0.95

---

## Contexto

Após 2 meses de desenvolvimento do SDLC Agêntico, chegamos a um ponto crítico: temos **124 scripts Python** em 30 skills e **13.894 linhas** em 38 agents. Análise das boas práticas oficiais da Anthropic revelou que estamos **sobre-automatizando com scripts quando linguagem natural seria suficiente e mais eficaz**.

## O Problema: Script Creep

### Sintomas Observados

1. **gate-evaluator (360 linhas)**:
   - Documenta API Python: `evaluate_gate()`, `check_artifact()`, `get_gate_criteria()`
   - **Diretório scripts/ VAZIO** (só tem .gitkeep)
   - API fantasma que nunca foi implementada
   - Claude está fazendo tudo via instruções naturais

2. **orchestrator (1.267 linhas)**:
   - **154% acima do limite de 500 linhas** recomendado pela Anthropic
   - Mistura instruções de alto nível com detalhes de implementação
   - Deveria usar progressive disclosure (separar em arquivos)

3. **session-analyzer (351 linhas + 6 scripts Python)**:
   - `extract_learnings.py` (11KB)
   - `handoff.py` (12KB)
   - `classify_error.py` (6KB)
   - **Muitas dessas operações são pattern matching que Claude faz naturalmente**

### Estatísticas Alarmantes

| Métrica | Valor | Recomendação Anthropic |
|---------|-------|------------------------|
| **orchestrator.md** | 1.267 linhas | < 500 linhas |
| **Scripts Python** | 124 arquivos | "Only when truly necessary" |
| **SKILL.md médio** | ~300 linhas | < 500 (ok, mas próximo do limite) |
| **Agents > 400 linhas** | 19 de 38 (50%) | Deveriam usar progressive disclosure |

## A Revelação: Boas Práticas da Anthropic

### Princípio Fundamental

> **"Default assumption: Claude is already very smart. Only add context Claude doesn't already have."**

### Quando Usar Natural Language vs Scripts

#### ✅ Use Natural Language (High Freedom) quando:

- **Múltiplas abordagens são válidas**
- **Decisões dependem do contexto**
- **Heurísticas guiam a abordagem**
- **Pattern matching e análise**

**Exemplo da Anthropic:**
```markdown
## Code review process

1. Analyze the code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability
4. Verify adherence to project conventions
```

**NÃO precisa de script Python!**

#### ⚠️ Use Scripts (Low Freedom) APENAS quando:

- **Operações são frágeis e propensas a erro**
- **Consistência é CRÍTICA**
- **Sequência específica DEVE ser seguida**
- **Operações determinísticas (build, deploy, validação de schema)**

**Exemplo da Anthropic:**
```markdown
## Database migration

Run exactly this script:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command.
```

### Progressive Disclosure Pattern

Para agents/skills > 500 linhas:

```
skill-name/
├── SKILL.md              # Overview (< 500 lines)
├── reference/
│   ├── finance.md        # Loaded only when needed
│   ├── sales.md
│   └── product.md
└── scripts/
    └── validate.py       # Only for deterministic ops
```

**Claude carrega reference/*.md APENAS quando necessário** → Zero token overhead até usar.

## Padrões dos Repos Open Source

### steipete/agent-scripts (Pointer Pattern)

**Filosofia**: Single canonical source, byte-identical sync

```markdown
# Downstream repo AGENTS.MD
READ ~/Projects/agent-scripts/AGENTS.MD BEFORE ANYTHING (skip if missing)

# Repo-specific rules here (if truly needed)
```

**Benefícios**:
- DRY (Don't Repeat Yourself) global
- Atualizações propagam automaticamente
- Repos locais focam no específico

### openclaw (Hybrid Approach)

**Natural Language para**:
- Configuration and onboarding
- Release workflows
- Security procedures
- Multi-agent safety protocols

**Scripts/Code para**:
- Build execution (`bun run build`)
- Pre-commit hooks (`prek install`)
- Status checks (`openclaw channels status --probe`)

**NÃO para**: Lógica que Claude pode inferir

## Análise Crítica do SDLC Agêntico

### ❌ O Que Estamos Fazendo ERRADO

#### 1. Scripts Python Desnecessários

**gate-evaluator**: API Python documentada que NÃO EXISTE
```python
# Isso NÃO DEVERIA existir em SKILL.md:
gate_result = evaluate_gate(
    from_phase=2,
    to_phase=3,
    project_context={...}
)
```

**Deveria ser**:
```markdown
## Avaliar Gate 2→3

1. Verifique se requisitos estão documentados em `docs/requirements.md`
2. Confirme que ADRs existem em `.agentic_sdlc/corpus/nodes/decisions/`
3. Valide que todos os requisitos têm acceptance criteria
4. Se tudo OK, aprove a transição
```

**Claude faz isso PERFEITAMENTE com linguagem natural!**

#### 2. Agents Monolíticos

**orchestrator.md (1.267 linhas)** deveria ser:

```
orchestrator/
├── SKILL.md (< 500 lines - overview)
├── reference/
│   ├── phase-transitions.md
│   ├── gate-evaluation.md
│   ├── client-resolution.md (v3.0.0)
│   └── error-handling.md
└── workflows/
    ├── phase-0-to-1.md
    ├── phase-1-to-2.md
    └── ...
```

Claude carrega `reference/client-resolution.md` APENAS quando detectar cliente multi-tenancy.

#### 3. Over-Engineering em Pattern Matching

**session-analyzer** tem:
- `classify_error.py` (6KB) - Pattern matching de erros
- `extract_learnings.py` (11KB) - Pattern matching de decisões

**Claude é MELHOR em pattern matching que regex!**

```markdown
## Extract learnings from session

1. Read session transcript from ~/.claude/projects/{project}/{session-id}.jsonl
2. Look for:
   - Decision points: Where choices were made (search for "decided", "chose", "went with")
   - Blockers: Problems encountered (search for "error", "failed", "blocked")
   - Resolutions: How blockers were solved (next message after blocker)
   - Trade-offs: Pros/cons discussed (search for "advantage", "disadvantage", "trade-off")
3. Create learning node in `.project/corpus/nodes/learnings/LEARN-{topic}.yml`
4. Update knowledge graph with 'learned_from' relation
```

**Zero Python necessário!**

### ✅ O Que Estamos Fazendo CERTO

#### 1. iac-generator (scripts justified)

```python
# terraform_validator.py - JUSTIFIED
# Validação de sintaxe Terraform é determinística e frágil
terraform validate
```

**Correto**: Claude NÃO deve adivinhar sintaxe HCL.

#### 2. parallel-workers (complex state management)

```python
# worker_manager.py - JUSTIFIED
# Git worktree operations são perigosas
# State machine (NEEDS_INIT → WORKING → PR_OPEN) requer consistência
```

**Correto**: Operação com side effects críticos.

#### 3. doc-generator (template processing)

```python
# generate_docs.py - JUSTIFIED
# Detecção de stack (frameworks, languages) via file scanning
# Substituição de templates com variáveis
```

**Correto**: Scanning de diretório é mais rápido em Python.

## Recomendações Específicas

### Fase 1: Auditoria (Imediato)

Categorizar cada script Python:

| Categoria | Ação | Exemplo |
|-----------|------|---------|
| **❌ Desnecessário** | Deletar, reescrever em natural language | classify_error.py, extract_learnings.py |
| **⚠️ Questionável** | Avaliar se Claude faz melhor | analyze_form.py (pdfplumber ok, mas lógica não) |
| **✅ Necessário** | Manter e documentar justificativa | terraform_validator.py, worker_manager.py |

### Fase 2: Refatoração do orchestrator.md

**Antes (1.267 linhas)**:
```
orchestrator.md
```

**Depois (< 500 linhas + progressive disclosure)**:
```
orchestrator/
├── SKILL.md (overview, core workflow)
├── reference/
│   ├── phase-0-intake.md
│   ├── phase-1-discovery.md
│   ├── ...
│   ├── gate-evaluation.md
│   ├── client-resolution-v3.md
│   └── error-recovery.md
└── examples/
    └── full-sdlc-walkthrough.md
```

**SKILL.md aponta para reference/ files** → Claude carrega sob demanda.

### Fase 3: Simplificação das Skills

#### gate-evaluator (ANTES):

```markdown
---
name: gate-evaluator
---

## Scripts Disponíveis

### evaluate_gate.py
```python
gate_result = evaluate_gate(...)
```
```

#### gate-evaluator (DEPOIS):

```markdown
---
name: gate-evaluator
---

# Gate Evaluation Workflow

## Phase 2 → Phase 3 Gate

Check these artifacts exist:
- [ ] `docs/requirements.md` with acceptance criteria
- [ ] `.agentic_sdlc/corpus/nodes/decisions/ADR-*.yml` (at least 1)
- [ ] All requirements have testable acceptance criteria

Run validation:
```bash
# Check for ADRs
ls .agentic_sdlc/corpus/nodes/decisions/ADR-*.yml | wc -l
# Should be > 0

# Check requirements have criteria
grep -c "acceptance_criteria:" docs/requirements.md
# Should match number of requirements
```

If ALL checks pass: **APPROVE**
If ANY check fails: **BLOCK** and explain what's missing

For gate definitions, see [gates/phase-2-to-3.yml](gates/phase-2-to-3.yml)
```

**Zero Python. Claude executa bash commands e decide.**

### Fase 4: Skill Template

Criar template para novas skills seguindo Anthropic guidelines:

```markdown
---
name: skill-name
description: |
  What it does AND when to use it.
  Include key terms for discovery.
allowed-tools:
  - Read
  - Bash
  - (others only if TRULY needed)
user-invocable: true/false
---

# Skill Name

## Quick Start

[Concise example - assume Claude is smart]

## Workflows

### Workflow Name

1. Step 1 (natural language)
2. Step 2
3. If X, then Y; else Z

## Reference

For detailed information, see:
- [Topic A](reference/topic-a.md)
- [Topic B](reference/topic-b.md)

## Scripts (ONLY if truly necessary)

### script-name.py

**Why this script is needed**: [Justify - deterministic operation, fragile, etc.]

```bash
python scripts/script-name.py --arg value
```
```

### Fase 5: Pointer Pattern para Compartilhamento

Para compartilhar guardrails entre projetos:

```markdown
# Projeto A AGENTS.MD
READ ~/Projects/sdlc-agentico-core/AGENTS.MD BEFORE ANYTHING

# Project-specific additions (if any)
```

**Benefícios**:
- Atualizações do framework propagam automaticamente
- Projetos mantêm apenas customizações locais
- DRY principle

## Métricas de Sucesso

### Antes da Refatoração

| Métrica | Valor Atual |
|---------|-------------|
| Scripts Python | 124 |
| Agents > 500 linhas | 19 (50%) |
| orchestrator.md | 1.267 linhas |
| Token overhead médio | ~8.000 tokens/skill load |

### Após Refatoração (Meta)

| Métrica | Valor Alvo |
|---------|------------|
| Scripts Python | < 40 (apenas ops críticas) |
| Agents > 500 linhas | 0 (progressive disclosure) |
| orchestrator.md | < 500 linhas (+ reference/) |
| Token overhead médio | < 3.000 tokens/skill load |

**Redução esperada**: 60-70% em token usage, 70% em scripts Python.

## Princípios para o Futuro

### 1. Default to Natural Language

**Pergunta antes de criar script Python**:
> "Claude consegue fazer isso com instruções em linguagem natural?"

Se resposta for "sim" → **NÃO CRIE SCRIPT**.

### 2. Progressive Disclosure Always

**Pergunta antes de adicionar conteúdo a SKILL.md**:
> "Isso é necessário para TODAS as invocações ou apenas para casos específicos?"

Se "casos específicos" → **SEPARATE FILE**.

### 3. Scripts Only for Determinism

**Scripts Python justificados apenas para**:
- Validação de schema/sintaxe (Terraform, YAML, JSON)
- Operações com side effects críticos (git worktree, deploys)
- Processamento de dados estruturados (parsing de PDFs com OCR)
- Operações de I/O pesadas (scanning de milhares de arquivos)

**NÃO para**:
- Pattern matching (Claude é MELHOR)
- Análise de texto (Claude é MELHOR)
- Decisões heurísticas (Claude é MELHOR)
- Workflows condicionais (Claude é MELHOR)

### 4. Test with Claude First

Antes de criar skill complexa:
1. Faça a tarefa com Claude usando apenas prompts naturais
2. Observe o que você repete várias vezes
3. Documente APENAS isso
4. Teste com Claude fresco
5. Itere baseado em observação real

## Referências

### Anthropic Official

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### Open Source References

- [steipete/agent-scripts](https://github.com/steipete/agent-scripts) - Pointer pattern
- [openclaw/openclaw](https://github.com/openclaw/openclaw) - Hybrid approach
- [anthropics/skills](https://github.com/anthropics/skills) - Official skill repository

## Ação Imediata

1. **Auditar todos os 124 scripts Python**:
   - ❌ Deletar os desnecessários
   - ⚠️ Reavaliar os questionáveis
   - ✅ Manter apenas os justificados

2. **Refatorar orchestrator.md**:
   - Separar em orchestrator/ com progressive disclosure
   - SKILL.md < 500 linhas
   - reference/ com detalhes específicos

3. **Criar template para novas skills**:
   - Linguagem natural first
   - Progressive disclosure
   - Scripts apenas quando justificado

4. **Documentar justificativas**:
   - Cada script Python DEVE ter seção "Why this script is needed"
   - Se não conseguir justificar → deletar

## Conclusão

**Estamos desenvolvendo um framework de orquestração de agentes, não uma biblioteca Python.**

O poder do SDLC Agêntico está em:
- ✅ **Instruções claras em linguagem natural**
- ✅ **Workflows bem definidos**
- ✅ **Progressive disclosure eficiente**
- ❌ **NÃO em ter 124 scripts Python**

**Claude é smart. Confie nele. Use scripts apenas quando Claude NÃO PODE fazer.**

---

**Next Steps**: Implementar Fase 1 (Auditoria) imediatamente, criar issue #XXXX para tracking.
