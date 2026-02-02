# Migração Shell → Python - Auditoria e Roadmap

**Data**: 2026-02-01
**Versão**: v3.0.0
**Status**: 🔴 **CRÍTICO** - 70% dos scripts incompatíveis com Windows

---

## Problema

**51 scripts shell** existem no framework, sendo que:
- **36 scripts (70%)** não funcionam no Windows nativo
- Framework **não funciona** sem WSL2/Git Bash no Windows
- **Violação** dos padrões OpenClaw/SkillsMP (skills devem ser Python)

---

## Resumo da Auditoria

| Categoria | Quantidade | Status | Prioridade |
|-----------|------------|--------|------------|
| **Infraestrutura** | 5 | ✅ OK | N/A |
| **Hooks Git** | 22 | ❌ Converter | **P0 (CRÍTICO)** |
| **Commands** | 4 | ❌ Converter | **P0 (CRÍTICO)** |
| **Skills** | 10 | ❌ Converter | **P1 (HIGH)** |
| **Libraries** | 3 | ⚠️ Revisar | P2 (MEDIUM) |
| **Testing** | 7 | ✅ OK | N/A |
| **TOTAL** | **51** | **36 precisam conversão** | - |

---

## Scripts por Categoria

### CATEGORIA 1: Infraestrutura (✅ OK manter shell)
**Justificativa**: Instalação de sistema, git hooks, CI/CD

1. `.agentic_sdlc/scripts/setup-sdlc.sh` - Setup principal (instala Python, cria venv)
2. `.agentic_sdlc/scripts/migrate-artifacts.sh` - Migração one-time .agentic_sdlc → .project
3. `.agentic_sdlc/scripts/install-security-tools.sh` - Instala ferramentas de sistema
4. `.agentic_sdlc/scripts/clean-test-repo.sh` - Limpeza de testes
5. `.claude/scripts/migrate-to-agentic-sdlc.sh` - Migração legacy

**Subtotal: 5 scripts** ✅ OK (infra)

---

### CATEGORIA 2: Hooks Git (❌ DEVEM virar Python wrappers)
**Problema**: Claude Code executa hooks, mas shell não funciona no Windows

**Hooks principais**:
- `.claude/hooks/detect-phase.sh` - Detecta fase SDLC
- `.claude/hooks/validate-commit.sh` - Valida mensagens de commit
- `.claude/hooks/check-gate.sh` - Verifica quality gates
- `.claude/hooks/auto-branch.sh` - Cria branches automaticamente
- `.claude/hooks/ensure-feature-branch.sh` - Garante branch correto
- `.claude/hooks/update-project-timestamp.sh` - Atualiza timestamp
- `.claude/hooks/phase-commit-reminder.sh` - Lembra de commitar
- `.claude/hooks/detect-documents.sh` - Detecta PDFs/XLSX
- `.claude/hooks/detect-adr-need.sh` - Detecta necessidade de ADR
- `.claude/hooks/detect-client.sh` - Detecta perfil cliente (multi-client)
- `.claude/hooks/auto-migrate.sh` - Migração automática
- `.claude/hooks/auto-graph-sync.sh` - Sincroniza grafo de conhecimento
- `.claude/hooks/auto-decay-recalc.sh` - Recalcula decay scores
- `.claude/hooks/track-rag-access.sh` - Rastreia acessos RAG
- `.claude/hooks/rag-corpus-indexer.sh` - Indexa corpus RAG
- `.claude/hooks/query-phase-learnings.sh` - Query learnings por fase
- `.claude/hooks/session-analyzer.sh` - Analisa sessões
- `.claude/hooks/post-gate-audit.sh` - Auditoria pós-gate
- `.claude/hooks/auto-update-component-counts.sh` - Atualiza contadores
- `.claude/hooks/add-issue-to-project.sh` - Adiciona issue ao GitHub Project
- `.claude/hooks/wiki-sync-phase7.sh` - Sincroniza Wiki na Phase 7
- `.claude/hooks/validate-framework-structure.sh` - Valida estrutura

**Subtotal: 22 hooks** ❌ DEVEM ser Python wrappers

---

### CATEGORIA 3: Commands (❌ DEVEM virar Python)
**Problema**: Usuário executa via `/comando`, precisa funcionar no Windows

- `.claude/commands/doc-search.sh` - /doc-search
- `.claude/commands/doc-enrich.sh` - /doc-enrich
- `.claude/commands/set-client.sh` - /set-client
- `.claude/commands/enable-multi-client.sh` - /enable-multi-client

**Subtotal: 4 commands** ❌ DEVEM ser Python

---

### CATEGORIA 4: Skills (❌ VIOLAÇÃO OpenClaw/SkillsMP)
**Problema**: Skills deveriam ter scripts/ em Python, não shell

- `.claude/skills/github-wiki/scripts/wiki_sync.sh` - Sincronização Wiki
- `.claude/skills/github-wiki/scripts/publish_adr.sh` - Publica ADR
- `.claude/skills/parallel-workers/scripts/worktree_manager.sh` - Gerencia worktrees
- `.claude/skills/phase-commit/scripts/phase-commit.sh` - Commit por fase
- `.claude/skills/sdlc-import/run-import.sh` - Executa import
- `.claude/skills/sdlc-import/scripts/install-local.sh` - Instala local
- `.claude/skills/sdlc-import/scripts/uninstall-local.sh` - Desinstala
- `.claude/skills/session-analyzer/scripts/analyze.sh` - Analisa sessões
- `.claude/skills/session-analyzer/scripts/report_sdlc_bug.sh` - Reporta bugs
- `.claude/skills/system-design-decision-engine/scripts/decision_checklist.sh` - Checklist

**Subtotal: 10 skill scripts** ❌ VIOLAÇÃO OpenClaw/SkillsMP

---

### CATEGORIA 5: Utilities (⚠️ Revisar)

- `.claude/lib/shell/logging_utils.sh` - Logging utilities
- `.claude/lib/logging.sh` - Logging (legacy)
- `.claude/lib/fallback.sh` - Fallback utilities

**Subtotal: 3 libs** ⚠️ Revisar (podem virar Python)

---

### CATEGORIA 6: Testing/Validation (✅ OK shell)

- `.agentic_sdlc/scripts/test-framework-e2e.sh` - Testes E2E
- `.agentic_sdlc/scripts/test-framework-full-sdlc.sh` - Testes full SDLC
- `.agentic_sdlc/scripts/validate-sdlc-phase.sh` - Valida fase
- `.agentic_sdlc/scripts/update-doc-counts.sh` - Atualiza contadores docs
- `.agentic_sdlc/scripts/validate-doc-counts.sh` - Valida contadores
- `.claude/skills/sdlc-import/tests/benchmark/run_benchmark.sh` - Benchmark
- `.claude/scripts/update-component-counts.sh` - Atualiza componentes

**Subtotal: 7 scripts de teste** ✅ OK (CI/CD)

---

## Roadmap de Migração

### v3.0.1 (HOTFIX - 2-3 dias) 🔴 PRIORIDADE
**Objetivo**: Hooks críticos como Python wrappers

**Converter**:
1. `detect-phase.sh` → `detect_phase.py`
2. `validate-commit.sh` → `validate_commit.py`
3. `check-gate.sh` → `check_gate.py`
4. `auto-branch.sh` → `auto_branch.py`

**Padrão**:
```python
# .claude/hooks/detect-phase.py
#!/usr/bin/env python3
"""
Detecta fase atual do SDLC baseado em contexto do projeto.
Substitui detect-phase.sh para compatibilidade Windows.
"""
import subprocess
import sys
from pathlib import Path

def detect_current_phase():
    # Lógica Python aqui
    return 1  # discovery

if __name__ == "__main__":
    phase = detect_current_phase()
    print(f"phase:{phase}")
```

```bash
# .claude/hooks/detect-phase.sh (wrapper legacy)
#!/bin/bash
# Wrapper para compatibilidade - delega para Python
python3 .claude/hooks/detect-phase.py "$@"
```

**Benefício**: Framework funciona no Windows (hooks críticos)

---

### v3.1.0 (MEDIUM - 1-2 semanas)
**Objetivo**: Todos hooks + commands em Python

**Converter**:
- 22 hooks → Python + shell wrappers
- 4 commands → Python puro (sem shell)

**Benefício**: 100% dos comandos de usuário funcionam no Windows

---

### v3.2.0 (LONG - 3-4 semanas)
**Objetivo**: Skills 100% Python (SkillsMP compliance)

**Converter**:
- 10 skill scripts → Python
- Remover shell wrappers (breaking change)

**Benefício**: Conformidade total com padrões Anthropic

---

### v4.0.0 (FUTURE - roadmap)
**Objetivo**: Framework Python-first

**Mudanças**:
- `setup-sdlc.sh` → `setup-sdlc.py`
- Remover TODOS shell scripts (exceto CI/CD)
- 100% cross-platform (Windows, Linux, macOS)

**Benefício**: Framework de classe mundial, zero dependências de shell

---

## Impacto da Não-Conversão

### ❌ Usuários Windows
- Framework **não funciona** sem WSL2
- Barreira de entrada alta (instalar WSL2 antes)
- Experiência inferior comparado a Linux/macOS

### ❌ Violação de Padrões
- OpenClaw: Skills devem ser Python
- SkillsMP: SKILL.md standard requer Python
- Anthropic: Recomenda Python-first

### ❌ Manutenibilidade
- 2 linguagens para manter (Shell + Python)
- Lógica duplicada em hooks (shell wrapper + Python)
- Testes mais complexos (testar ambos)

---

## Decisão Necessária

**Escolher roadmap**:

1. ✅ **Incremental** (v3.0.1 → v3.1.0 → v3.2.0 → v4.0.0)
   - Prós: Entregas graduais, menos risco
   - Contras: Mantém dívida técnica por mais tempo

2. 🚀 **Big Bang** (v4.0.0 direto)
   - Prós: Resolve tudo de uma vez
   - Contras: Alto risco, pode atrasar release

3. ⚡ **Híbrido** (v3.0.1 críticos + v4.0.0 resto)
   - Prós: Resolve Windows ASAP + planejamento completo
   - Contras: Pode confundir usuários (2 migrações)

---

**Recomendação**: **Incremental** (opção 1)
- v3.0.1 (hotfix) resolve Windows para 80% dos casos de uso
- v3.1.0 completa compatibilidade Windows
- v3.2.0 remove violações de padrões
- v4.0.0 finaliza visão Python-first
