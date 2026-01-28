# Troubleshooting - SDLC Agentico

Guia de resolucao de problemas comuns ao usar o SDLC Agentico.

---

## Indice

1. [Skill nao encontrada](#1-skill-nao-encontrada)
2. [Agente nao responde como esperado](#2-agente-nao-responde-como-esperado)
3. [Gate falha sem motivo claro](#3-gate-falha-sem-motivo-claro)
4. [Hook nao executa](#4-hook-nao-executa)
5. [Comando /sdlc-start nao funciona](#5-comando-sdlc-start-nao-funciona)
6. [Erro ao criar branch automaticamente](#6-erro-ao-criar-branch-automaticamente)
7. [Spec Kit nao instalado](#7-spec-kit-nao-instalado)
8. [Permissao negada em comandos](#8-permissao-negada-em-comandos)
9. [Fase do SDLC nao detectada](#9-fase-do-sdlc-nao-detectada)
10. [Arquivos de configuracao corrompidos](#10-arquivos-de-configuracao-corrompidos)
11. [Como habilitar logging detalhado](#11-como-habilitar-logging-detalhado)

---

## 1. Skill nao encontrada

**Sintoma**: Mensagem "skill not found" ou skill nao e invocada.

**Causas possiveis**:
- Skill nao registrada em `settings.json`
- Diretorio da skill nao existe em `.claude/skills/`
- Nome da skill digitado incorretamente

**Solucao**:
```bash
# Verificar skills registradas
jq '.skills.available_skills' .claude/settings.json

# Verificar skills em disco
ls .claude/skills/

# Adicionar skill faltante ao settings.json
# Editar .claude/settings.json e adicionar na lista available_skills
```

---

## 2. Agente nao responde como esperado

**Sintoma**: Agente ignora instrucoes ou responde de forma generica.

**Causas possiveis**:
- Agente e um "lightweight agent" (stubs de ~20 linhas)
- Modelo incorreto (sonnet vs opus)
- Skill referenciada no agente nao esta disponivel

**Solucao**:
```bash
# Verificar tamanho do agente
wc -l .claude/agents/NOME_DO_AGENTE.md

# Agentes lightweight (< 30 linhas):
# - failure-analyst
# - interview-simulator
# - requirements-interrogator
# - tradeoff-challenger

# Estes agentes dependem da skill system-design-decision-engine
# Verifique se a skill esta registrada
```

**Nota**: Lightweight agents sao intencionalmente minimalistas. Eles delegam logica para skills.

---

## 3. Gate falha sem motivo claro

**Sintoma**: Quality gate bloqueia avanco de fase sem explicacao.

**Causas possiveis**:
- Artefatos obrigatorios nao criados
- Checks de seguranca falhando silenciosamente
- Padroes glob nao encontrando arquivos

**Solucao**:
```bash
# Verificar definicao do gate
cat .claude/skills/gate-evaluator/gates/phase-X-to-Y.yml

# Verificar artefatos obrigatorios
# Procurar secao "required_artifacts" no YAML

# Executar gate check manualmente
/gate-check phase-X-to-Y
```

**Gates com seguranca obrigatoria**: 2-to-3, 3-to-4, 5-to-6, 6-to-7

---

## 4. Hook nao executa

**Sintoma**: Hook deveria executar mas nada acontece.

**Causas possiveis**:
- Hook nao registrado em `settings.json`
- Matcher nao corresponde ao comando
- Script sem permissao de execucao
- Erro silenciado com `|| true`

**Solucao**:
```bash
# Verificar hooks registrados
jq '.hooks' .claude/settings.json

# Verificar permissoes
ls -la .claude/hooks/

# Dar permissao de execucao
chmod +x .claude/hooks/*.sh

# Testar hook manualmente
.claude/hooks/NOME_DO_HOOK.sh
```

---

## 5. Comando /sdlc-start nao funciona

**Sintoma**: Comando nao e reconhecido ou falha ao iniciar.

**Causas possiveis**:
- Claude Code CLI nao instalado
- Arquivo do comando nao existe
- Dependencia (memory-manager) nao disponivel

**Solucao**:
```bash
# Verificar Claude Code CLI
claude --version

# Verificar comando existe
ls .claude/commands/sdlc-start.md

# Verificar skill memory-manager
ls .claude/skills/memory-manager/
```

---

## 6. Erro ao criar branch automaticamente

**Sintoma**: Auto-branch nao cria branch ou cria com nome errado.

**Causas possiveis**:
- Skill auto-branch nao registrada
- Tipo de trabalho nao reconhecido
- Conflito com branch existente

**Solucao**:
```bash
# Tipos de branch suportados:
# - feature/ (novas funcionalidades)
# - fix/ (correcoes de bugs)
# - hotfix/ (correcoes urgentes)
# - release/ (preparacao de release)
# - docs/ (documentacao)
# - refactor/ (refatoracao)
# - test/ (testes)

# Verificar branches existentes
git branch -a

# Criar branch manualmente se necessario
git checkout -b feature/nome-da-feature
```

---

## 7. Spec Kit nao instalado

**Sintoma**: Comando `specify` nao encontrado.

**Causas possiveis**:
- Spec Kit nao instalado
- PATH nao configurado
- Versao incompativel

**Solucao**:
```bash
# Instalar Spec Kit
npm install -g @anthropics/spec-kit

# Verificar instalacao
specify check

# Se falhar, verificar Node.js
node --version  # Requer 18+
```

---

## 8. Permissao negada em comandos

**Sintoma**: Comandos Bash sao bloqueados por permissao.

**Causas possiveis**:
- Comando nao esta na whitelist de `settings.local.json`
- Padrao do comando nao corresponde

**Solucao**:
```bash
# Verificar permissoes locais
cat .claude/settings.local.json

# Adicionar permissao (exemplo)
# Editar settings.local.json e adicionar:
# "Bash(COMANDO:*)" na lista allow
```

**Importante**: Nao adicione permissoes excessivamente amplas. Seja especifico.

---

## 9. Fase do SDLC nao detectada

**Sintoma**: Hook detect-phase.sh retorna fase incorreta ou vazia.

**Causas possiveis**:
- Artefatos de fase anteriores nao existem
- Estrutura de diretorios diferente do esperado
- Projeto nao inicializado com /sdlc-start

**Solucao**:
```bash
# Verificar fase atual manualmente
/phase-status

# Verificar artefatos existentes
ls .agentic_sdlc/projects/

# Iniciar workflow se necessario
/sdlc-start "Descricao do projeto"
```

---

## 10. Arquivos de configuracao corrompidos

**Sintoma**: JSON invalido em settings.json ou settings.local.json.

**Causas possiveis**:
- Edicao manual com erro de sintaxe
- Merge com conflitos nao resolvidos
- Encoding incorreto

**Solucao**:
```bash
# Validar JSON
jq . .claude/settings.json

# Se falhar, identificar erro
python3 -c "import json; json.load(open('.claude/settings.json'))"

# Restaurar do git se necessario
git checkout HEAD -- .claude/settings.json

# Ou restaurar versao limpa de settings.local.json
cat > .claude/settings.local.json << 'EOF'
{
  "permissions": {
    "allow": []
  }
}
EOF
```

---

## 11. Como habilitar logging detalhado

**Sintoma**: Precisa de logs detalhados para debug ou investigacao de bugs.

**Quando usar**:
- Investigar reconciliacao de ADRs (sdlc-import)
- Debug de quality gates
- Rastrear execucao de hooks
- Analisar performance de comandos

**IMPORTANTE**: Comandos slash do Claude Code (como `/sdlc-import`) **NAO** aceitam pipes bash (`|`, `>`, `tee`). Use as opcoes abaixo.

### Opcao 1: Via Claude Code (Temporario - 1 sessao) ✅ **RECOMENDADO**

Simplesmente escreva no chat do Claude Code:

```
/sdlc-import com logging detalhado
```

Ou:

```
Execute /sdlc-import com log level DEBUG
```

**Como funciona**: O Claude automaticamente define `SDLC_LOG_LEVEL=DEBUG` antes de executar.

**Vantagens**:
- ✅ Mais simples
- ✅ Logs ficam no historico do chat
- ✅ Sem configuracao necessaria

---

### Opcao 2: Via Variavel de Ambiente (Temporario - sessao do terminal)

Antes de executar comandos no Claude Code:

```bash
export SDLC_LOG_LEVEL=DEBUG
```

Depois execute o comando normalmente:
```
/sdlc-import
```

**Variaveis de ambiente disponiveis**:

| Variavel | Valores | Default | Descricao |
|----------|---------|---------|-----------|
| `SDLC_LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR, CRITICAL | INFO | Nivel de log |
| `SDLC_LOKI_ENABLED` | true, false | true | Enviar logs para Loki |
| `SDLC_LOKI_URL` | URL | http://localhost:3100 | URL do Loki |
| `SDLC_JSON_LOGS` | true, false | false | Formato JSON no console |

**Exemplo com multiplas variaveis**:
```bash
export SDLC_LOG_LEVEL=DEBUG
export SDLC_JSON_LOGS=true
export SDLC_LOKI_ENABLED=false

/sdlc-import
```

---

### Opcao 3: Via settings.json (Permanente)

Edite `.claude/settings.json` no projeto e adicione a secao `env`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "version": "1.0",
  "project": {
    "name": "meu_projeto",
    "description": "..."
  },

  "env": {
    "SDLC_LOG_LEVEL": "DEBUG",
    "SDLC_LOKI_ENABLED": "true",
    "SDLC_JSON_LOGS": "false"
  },

  "hooks": {
    ...
  }
}
```

**Vantagens**:
- ✅ Log DEBUG sempre ativo
- ✅ Configuracao persistente
- ✅ Compartilhavel via git

**Desvantagens**:
- ⚠️ Logs mais verbosos o tempo todo
- ⚠️ Pode impactar performance

---

### Opcao 4: Executar Script Python Diretamente (Avancado)

Se precisar redirecionar saida para arquivo:

```bash
cd /caminho/do/projeto

# Com logging DEBUG
SDLC_LOG_LEVEL=DEBUG python3 \
  .claude/skills/sdlc-import/scripts/project_analyzer.py \
  /caminho/do/projeto \
  2>&1 | tee import-debug.log

# Ver apenas logs de reconciliacao de ADRs
grep "Comparing inferred ADR\|DUPLICATE\|ENRICH\|NEW" import-debug.log

# Ver decisoes finais
grep "ADR reconciliation decision" import-debug.log
```

**Quando usar**: Quando precisa salvar logs em arquivo para analise posterior.

---

### Niveis de Log Disponiveis

| Nivel | Quando usar |
|-------|-------------|
| **DEBUG** | Investigacao profunda, rastrear cada passo |
| **INFO** | Fluxo normal, marcos importantes |
| **WARNING** | Alertas, comportamento inesperado |
| **ERROR** | Erros recuperaveis |
| **CRITICAL** | Erros fatais, sistema nao pode continuar |

---

### Exemplos de Uso

**Debug de reconciliacao de ADRs**:
```
/sdlc-import com log DEBUG
```

Procure no output:
- `🔍 Comparing inferred ADR` - Cada comparacao
- `vs '...'` - Similaridade calculada
- `✓ DUPLICATE`, `✓ ENRICH`, `✗ NEW` - Decisoes finais

**Debug de quality gate**:
```bash
export SDLC_LOG_LEVEL=DEBUG
/gate-check phase-5-to-6
```

**Debug de hooks**:
```bash
export SDLC_LOG_LEVEL=DEBUG
# Hooks serao executados com logging detalhado automaticamente
```

---

### Verificar Logs Estruturados (Loki/Grafana)

Se Loki estiver configurado:

1. **Acessar Grafana**: http://localhost:3003
2. **Explore > Loki**
3. **Query**:
   ```logql
   {app="sdlc-agentico", level="debug"}
   ```

**Filtros uteis**:
```logql
# Logs de uma skill especifica
{app="sdlc-agentico", skill="sdlc-import"}

# Logs de uma fase especifica
{app="sdlc-agentico", phase="5"}

# Logs de erro
{app="sdlc-agentico", level="error"}

# Logs de reconciliacao
{app="sdlc-agentico"} |= "reconciliation"
```

---

### Solucao de Problemas Comuns

**Logs nao aparecem**:
```bash
# Verificar nivel atual
echo $SDLC_LOG_LEVEL

# Forcar DEBUG
export SDLC_LOG_LEVEL=DEBUG

# Verificar se Loki esta rodando
curl http://localhost:3100/ready
```

**Logs muito verbosos**:
```bash
# Desabilitar DEBUG apos debug
unset SDLC_LOG_LEVEL
# Ou
export SDLC_LOG_LEVEL=INFO
```

**Pipes bash nao funcionam**:
```
❌ /sdlc-import 2>&1 | tee log.txt  # NAO FUNCIONA
✅ /sdlc-import com log DEBUG       # FUNCIONA
✅ Script Python direto | tee       # FUNCIONA (Opcao 4)
```

---

## Comandos Uteis de Diagnostico

```bash
# Status geral do projeto
git status
ls -la .claude/
ls -la .agentic_sdlc/

# Verificar configuracao
jq '.' .claude/settings.json | head -50

# Contar agentes
ls -1 .claude/agents/*.md | wc -l

# Contar skills
ls -1 .claude/skills/ | wc -l

# Verificar hooks
ls -la .claude/hooks/

# Verificar gates
ls -la .claude/skills/gate-evaluator/gates/
```

---

## Ainda com Problemas?

Se o problema persistir:

1. **Verifique a documentacao**: `\.agentic_sdlc/docs/` contem guias detalhados
2. **Consulte o playbook**: `\.agentic_sdlc/docs/playbook.md` tem principios e padroes
3. **Veja exemplos**: `\.agentic_sdlc/docs/SIMULATION-DUPLICATAS.md` mostra um caso real
4. **Reporte issue**: Documente o problema com logs e contexto

---

*Ultima atualizacao: 2026-01-28 (v2.2.0 - Adicionada secao 11: Como habilitar logging detalhado)*
