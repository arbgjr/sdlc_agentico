# Guia de Teste - v2.1.9 Sprint 1 Fixes

**Versão:** v2.1.9 (alpha)
**Data:** 2026-01-27
**Objetivo:** Validar fixes C1, C4, C3 em projeto real (Autoritas)

---

## Pré-requisitos

- ✅ Código do framework em: `~/source/repos/arbgjr/mice_dolphins`
- ✅ Projeto Autoritas em: `~/source/repos/tripla/autoritas`
- ✅ Sprint 1 commit aplicado: `2c2f33e`

---

## Instalação Local para Testes

### Opção A: Script Automático (Recomendado)

```bash
# Instala versão local com symlink
~/source/repos/arbgjr/mice_dolphins/.claude/skills/sdlc-import/scripts/install-local.sh

# Verifica instalação
ls -la ~/.claude/skills/sdlc-import
# Deve mostrar: sdlc-import -> /home/armando_jr/source/repos/arbgjr/mice_dolphins/.claude/skills/sdlc-import
```

### Opção B: Manual

```bash
# Backup da versão atual (se existir)
if [ -d ~/.claude/skills/sdlc-import ]; then
    mv ~/.claude/skills/sdlc-import ~/.claude/skills/sdlc-import.backup-$(date +%Y%m%d)
fi

# Symlink para código local
ln -sf ~/source/repos/arbgjr/mice_dolphins/.claude/skills/sdlc-import ~/.claude/skills/sdlc-import
```

---

## Testes de Validação

### Teste 1: Verificar C1 Fix (Output Directory)

**Objetivo:** Confirmar que artefatos vão para `.project/` e não `.agentic_sdlc/`

```bash
cd ~/source/repos/tripla/autoritas

# Executar import
python3 ~/.claude/skills/sdlc-import/scripts/sdlc_import.py \
  --no-llm \
  --no-interactive

# VERIFICAR:
# 1. Mensagem de log: "✓ Resolved output_dir: .project (propagated to config)"
# 2. Artefatos criados em: autoritas/.project/
# 3. NÃO criados em: autoritas/.agentic_sdlc/
```

**Verificação Detalhada:**
```bash
# Ver log de output_dir
grep "Resolved output_dir" ~/.sdlc-import.log | tail -5

# Verificar estrutura criada
ls -la ~/source/repos/tripla/autoritas/.project/
# Deve existir: corpus/, architecture/, security/, reports/

# Verificar que .agentic_sdlc/ NÃO foi criado no projeto
ls -la ~/source/repos/tripla/autoritas/.agentic_sdlc/
# Deve retornar: No such file or directory
```

**Resultado Esperado:**
```
✓ Resolved output_dir: .project (propagated to config)
✓ Artefatos em: autoritas/.project/corpus/nodes/decisions/
✓ Artefatos em: autoritas/.project/reports/import-report.md
✗ Nenhum artefato em: autoritas/.agentic_sdlc/
```

---

### Teste 2: Verificar C3 Fix (ADR Detection)

**Objetivo:** Confirmar que os 21 ADRs existentes são detectados

```bash
cd ~/source/repos/tripla/autoritas

# Executar import com logging DEBUG
SDLC_LOG_LEVEL=DEBUG python3 ~/.claude/skills/sdlc-import/scripts/sdlc_import.py \
  --interactive 2>&1 | tee /tmp/autoritas-import-debug.log

# VERIFICAR LOG:
# 1. "Searching pattern: **/docs/adr/*.md"
# 2. "Found 21 files matching pattern"
# 3. "✓ Detected ADR: ADR-XXX - Title"
```

**Verificação Detalhada:**
```bash
# Procurar detecção de ADRs no log
grep "Searching pattern" /tmp/autoritas-import-debug.log
grep "Found .* files matching pattern" /tmp/autoritas-import-debug.log
grep "✓ Detected ADR" /tmp/autoritas-import-debug.log | wc -l
# Deve retornar: 21

# Verificar reconciliation no import report
cat ~/source/repos/tripla/autoritas/.project/reports/import-report.md
# Deve conter seção: "## 📚 ADR Reconciliation"
```

**Resultado Esperado:**
```
Searching pattern: **/docs/adr/*.md
  Found 21 files matching pattern
  Parsing: autoritas-common/docs/adr/0001-*.md
  ✓ Detected ADR: ADR-001 - Architecture
  ... (21 linhas)

## 📚 ADR Reconciliation
- **Existing ADRs found:** 21
- **Inferred ADRs:** 7
- **Duplicates skipped:** 3-5
- **New unique ADRs:** 2-4
```

---

### Teste 3: Verificar C4 Fix (No Crash)

**Objetivo:** Confirmar que gera ADR index sem crash

```bash
cd ~/source/repos/tripla/autoritas

# Executar import completo
python3 ~/.claude/skills/sdlc-import/scripts/sdlc_import.py \
  --interactive

# VERIFICAR:
# 1. Sem NameError no log
# 2. Arquivo adr_index.yml criado
```

**Verificação Detalhada:**
```bash
# Procurar por NameError no log
grep -i "NameError\|config.*not defined" /tmp/autoritas-import-debug.log
# Deve retornar: (vazio - sem erros)

# Verificar que adr_index.yml foi criado
cat ~/source/repos/tripla/autoritas/.project/corpus/adr_index.yml
# Deve conter: lista de ADRs com migrated_to: .project/corpus/...
```

**Resultado Esperado:**
```
✓ Nenhum NameError no log
✓ adr_index.yml criado com sucesso
✓ Paths corretos (.project/corpus/... ao invés de .agentic_sdlc/...)
```

---

## Checklist de Validação

### Fix C1: Output Directory
- [ ] Log mostra "✓ Resolved output_dir: .project (propagated to config)"
- [ ] Artefatos criados em `autoritas/.project/`
- [ ] Nenhum artefato em `autoritas/.agentic_sdlc/`
- [ ] Todos componentes usam mesmo diretório

### Fix C3: ADR Detection
- [ ] Log mostra "Searching pattern: **/docs/adr/*.md"
- [ ] Log mostra "Found 21 files matching pattern"
- [ ] Log mostra 21x "✓ Detected ADR: ..."
- [ ] Import report contém seção "## 📚 ADR Reconciliation"
- [ ] Report mostra "Existing ADRs found: 21"
- [ ] Report lista duplicates detectados

### Fix C4: No Crash
- [ ] Nenhum NameError no log
- [ ] `adr_index.yml` criado com sucesso
- [ ] Paths no index usam `.project/` (não `.agentic_sdlc/`)

---

## Comparação Antes/Depois

### Antes (v2.1.8)
```
❌ Artefatos em: autoritas/.agentic_sdlc/
❌ ADRs existentes: 0 detectados (21 ignorados)
❌ Crash ao gerar ADR index (NameError)
❌ Import report sem reconciliation
```

### Depois (v2.1.9)
```
✅ Artefatos em: autoritas/.project/
✅ ADRs existentes: 21 detectados corretamente
✅ ADR index gerado sem erros
✅ Import report com reconciliation completa
```

---

## Troubleshooting

### Problema: Ainda grava em `.agentic_sdlc/`

**Diagnóstico:**
```bash
# Verificar que está usando código local
ls -la ~/.claude/skills/sdlc-import
# Deve mostrar symlink para mice_dolphins

# Verificar commit aplicado
cd ~/source/repos/arbgjr/mice_dolphins
git log --oneline -1
# Deve mostrar: 2c2f33e fix(sdlc-import): Sprint 1
```

**Solução:**
```bash
# Reinstalar local
~/source/repos/arbgjr/mice_dolphins/.claude/skills/sdlc-import/scripts/install-local.sh
```

### Problema: ADRs não detectados

**Diagnóstico:**
```bash
# Executar com DEBUG logging
SDLC_LOG_LEVEL=DEBUG python3 ~/.claude/skills/sdlc-import/scripts/sdlc_import.py

# Verificar patterns de busca
grep "Searching pattern" /tmp/sdlc-import-debug.log
```

**Solução:**
- Verificar que ADRs estão em `docs/adr/*.md`
- Verificar que não estão em `.sdlcignore`
- Verificar permissões dos arquivos

### Problema: NameError persiste

**Diagnóstico:**
```bash
# Verificar linha 122 do documentation_generator.py
grep -n "self.config\['general'\]" ~/.claude/skills/sdlc-import/scripts/documentation_generator.py | grep 122
```

**Solução:**
- Verificar que código local está atualizado
- Verificar que symlink aponta para lugar certo

---

## Reverter para Versão Stable

Se os testes falharem e você precisar voltar:

```bash
# Remover symlink
rm ~/.claude/skills/sdlc-import

# Restaurar backup
mv ~/.claude/skills/sdlc-import.backup-* ~/.claude/skills/sdlc-import

# Ou reinstalar versão stable via setup-sdlc.sh
curl -fsSL https://raw.githubusercontent.com/arbgjr/sdlc_agentico/main/\.agentic_sdlc/scripts/setup-sdlc.sh | bash
```

---

## Relatório de Resultados

**Após executar os testes, preencha:**

### Ambiente
- Data do teste: ___________
- Projeto: Autoritas
- Versão testada: v2.1.9
- Commit: 2c2f33e

### Resultados

**C1 (Output Directory):**
- [ ] PASS
- [ ] FAIL - Motivo: _________________

**C3 (ADR Detection):**
- [ ] PASS - ADRs detectados: _____
- [ ] FAIL - Motivo: _________________

**C4 (No Crash):**
- [ ] PASS
- [ ] FAIL - Motivo: _________________

### Observações
```
[Adicione observações, logs relevantes, ou comportamentos inesperados]
```

---

## Próximos Passos Após Validação

Se todos testes **PASS**:
1. ✅ Criar tag `v2.1.9`
2. ✅ Gerar release notes
3. ✅ Publicar release no GitHub
4. ✅ Atualizar README com v2.1.9
5. ✅ Iniciar Sprint 2 (C2 - Framework/Project Separation)

Se algum teste **FAIL**:
1. ❌ Não criar tag
2. ❌ Investigar falha
3. ❌ Corrigir e re-testar
4. ❌ Manter como v2.1.9-alpha até validação
