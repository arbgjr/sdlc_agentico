# Parallel Workers - Plano de Testes v2.0

## Objetivo

Validar a integração completa do Epic #33 (parallel-workers) no SDLC Agêntico.

## Pré-requisitos

- [x] Branch: `feature/epic-33-claude-orchestrator`
- [ ] Git worktree disponível (git >= 2.25)
- [ ] gh CLI autenticado (`gh auth status`)
- [ ] Python 3.11+ com dependências
- [ ] Observabilidade rodando (Loki/Grafana - opcional)

## Testes Unitários

### 1. Integration Test (Básico)

```bash
# Executar test suite
python3 .claude/skills/parallel-workers/tests/integration_test.py
```

**Resultado esperado:**
```
✅ All tests passed!
- Worker lifecycle: spawn → state tracking → cleanup
- Simple memory: add fact → recall → search
```

### 2. State Tracker

```bash
# Criar worker de teste
python3 .claude/skills/parallel-workers/scripts/worker_manager.py spawn \
  --task-id "TEST-001" \
  --description "Test worker" \
  --agent "code-author" \
  --base-branch "main"

# Verificar estado
python3 .claude/skills/parallel-workers/scripts/state_tracker.py get <worker-id>

# Listar todos
python3 .claude/skills/parallel-workers/scripts/state_tracker.py list

# Cleanup
python3 .claude/skills/parallel-workers/scripts/worker_manager.py terminate <worker-id> --force
```

**Resultado esperado:**
- Worker criado com state NEEDS_INIT
- Worktree criado em `~/.worktrees/mice_dolphins/TEST-001/`
- Estado salvo em `~/.claude/worker-states/<worker-id>.json`
- Cleanup remove worktree e estado

### 3. Simple Memory

```bash
# Adicionar fact
python3 .claude/skills/memory-manager/scripts/simple_store.py add-fact \
  "Test parallel workers integration" \
  --tags test parallel-workers \
  --project mice_dolphins

# Recall
python3 .claude/skills/memory-manager/scripts/simple_store.py recall "parallel"

# Adicionar tool
python3 .claude/skills/memory-manager/scripts/simple_store.py add-tool test-tool \
  --repo "https://github.com/test/test" \
  --version "1.0.0"

# Search
python3 .claude/skills/memory-manager/scripts/simple_store.py search "test"
```

**Resultado esperado:**
- Fact salvo em `~/.claude/simple-memory/facts.json`
- Recall retorna fact com tags corretos
- Search encontra tanto fact quanto tool

### 4. Session Handoff

```bash
# Gerar handoff (se houver sessão recente)
python3 .claude/skills/session-analyzer/scripts/handoff.py

# Verificar output
ls -la .agentic_sdlc/sessions/
```

**Resultado esperado:**
- Arquivo gerado: `.agentic_sdlc/sessions/YYYYMMDD-HHMMSS-mice_dolphins.md`
- Seções: Metadata, Completed, Pending, Context

## Testes de Integração (Workflow)

### 5. Batch Worker Spawn

```bash
# Criar spec de teste
cat > /tmp/test-tasks.yml <<'EOF'
project: mice_dolphins
base_branch: main

tasks:
  - id: TEST-001
    description: "Test task 1"
    agent: code-author
    priority: 10
    dependencies: []

  - id: TEST-002
    description: "Test task 2"
    agent: test-author
    priority: 9
    dependencies: []

  - id: TEST-003
    description: "Test task 3"
    agent: iac-engineer
    priority: 8
    dependencies: []
EOF

# Spawn batch
python3 .claude/skills/parallel-workers/scripts/worker_manager.py spawn-batch \
  --spec-file /tmp/test-tasks.yml

# Verificar workers
python3 .claude/skills/parallel-workers/scripts/state_tracker.py list
```

**Resultado esperado:**
- 3 workers criados
- Todos em estado NEEDS_INIT
- 3 worktrees em `~/.worktrees/mice_dolphins/`

### 6. Automation Loop (Curto)

```bash
# Iniciar loop por 30s (6 iterações)
timeout 30 python3 .claude/skills/parallel-workers/scripts/loop.py \
  --project mice_dolphins \
  --poll-interval 5 || true

# Verificar transições
python3 .claude/skills/parallel-workers/scripts/state_tracker.py list
```

**Resultado esperado:**
- Loop executa 6 iterações
- Workers transicionam NEEDS_INIT → WORKING (auto-transition)
- Logs em stdout (se Loki não disponível)

### 7. Cleanup All

```bash
# Cleanup todos workers
python3 .claude/skills/parallel-workers/scripts/worker_manager.py cleanup

# Verificar limpeza
ls ~/.worktrees/mice_dolphins/ 2>/dev/null || echo "Worktrees removidos ✓"
ls ~/.claude/worker-states/ | wc -l  # Deve ser 0
```

**Resultado esperado:**
- Todos worktrees removidos
- Todos estados removidos
- Nenhum erro

## Testes de Observabilidade (Opcional)

### 8. Loki Logs

Se Loki rodando em http://localhost:3100:

```bash
# Verificar logs enviados
curl -s "http://localhost:3100/loki/api/v1/query?query={skill=\"parallel-workers\"}" | jq .

# Ou via LogCLI
logcli query '{skill="parallel-workers"}' --limit=50
```

**Resultado esperado:**
- Logs com labels corretos: skill, phase, worker_id
- Timestamps corretos
- JSON parsing válido

### 9. Grafana Dashboard

1. Abrir http://localhost:3003
2. Import dashboard: `.claude/config/logging/dashboards/parallel-workers.json`
3. Verificar painéis:
   - Active Workers
   - State Distribution
   - Task Completion Rate
   - Worker Errors

**Resultado esperado:**
- Dashboard importado com sucesso
- Painéis populados com dados (se workers executaram)

## Testes de Integração com Agents

### 10. delivery-planner Integration

```bash
# Verificar se agent foi atualizado
grep -A 20 "## Parallel Workers" .claude/agents/delivery-planner.md
```

**Resultado esperado:**
- Seção "Parallel Workers (v2.0)" existe
- Formato de task spec documentado
- Checklist atualizado

### 11. orchestrator Integration

```bash
# Verificar se agent foi atualizado
grep -A 30 "## Parallel Workers" .claude/agents/orchestrator.md
```

**Resultado esperado:**
- Seção "Parallel Workers (v2.0)" existe
- Workflow automático documentado
- Gate 5→6 com workers documentado

### 12. /parallel-spawn Command

```bash
# Verificar comando criado
ls -la .claude/commands/parallel-spawn.md
```

**Resultado esperado:**
- Arquivo existe
- Frontmatter correto (name, description, phase, complexity)
- Exemplos de uso incluídos

## Testes End-to-End (Simulação Real)

### 13. Simular Phase 4→5 Transition

**Pré-condição:** Criar um tasks.yml mock

```bash
mkdir -p .agentic_sdlc/projects/current
cat > .agentic_sdlc/projects/current/tasks.yml <<'EOF'
project: mice_dolphins
base_branch: main

tasks:
  - id: FEAT-001
    description: "Implement login endpoint"
    agent: code-author
    priority: 10
    dependencies: []

  - id: FEAT-002
    description: "Add auth tests"
    agent: test-author
    priority: 9
    dependencies:
      - FEAT-001

metadata:
  sprint: "Sprint 1"
  epic: "#33"
  complexity_level: 2
  phase: 5
EOF
```

**Teste:** Spawnar e monitorar

```bash
# Spawn workers
python3 .claude/skills/parallel-workers/scripts/worker_manager.py spawn-batch \
  --spec-file .agentic_sdlc/projects/current/tasks.yml

# Iniciar loop em background
python3 .claude/skills/parallel-workers/scripts/loop.py \
  --project mice_dolphins \
  --max-iterations 20 &
LOOP_PID=$!

# Aguardar
sleep 10

# Verificar progresso
python3 .claude/skills/parallel-workers/scripts/state_tracker.py list

# Parar loop
kill $LOOP_PID 2>/dev/null || true

# Cleanup
python3 .claude/skills/parallel-workers/scripts/worker_manager.py cleanup
```

**Resultado esperado:**
- FEAT-001 spawna imediatamente (sem dependencies)
- FEAT-002 fica pendente (aguarda FEAT-001)
- Loop monitora e transiciona estados
- Cleanup funciona corretamente

## Checklist de Validação

### Funcionalidades Implementadas

- [ ] Worker spawn (single)
- [ ] Worker spawn (batch)
- [ ] State tracking (get/set/list/transition)
- [ ] Worktree management (create/remove/prune)
- [ ] Automation loop (polling, transitions)
- [ ] Simple memory (facts/tools/repos/search)
- [ ] Session handoff (geração automática)
- [ ] Integration tests passando

### Integração com SDLC

- [ ] delivery-planner gera tasks.yml
- [ ] orchestrator detecta e spawna
- [ ] /parallel-spawn command funcional
- [ ] Hooks atualizados
- [ ] Documentação atualizada

### Observabilidade

- [ ] Logs estruturados (Loki labels)
- [ ] Grafana dashboard importável
- [ ] Correlation IDs gerados
- [ ] Errors logados corretamente

### Segurança

- [ ] Secrets não em worktrees
- [ ] Env sanitizado para workers
- [ ] Validation before merge
- [ ] Audit trail completo

## Problemas Conhecidos / Limitações

1. **gh CLI requerido**: Automation loop precisa do gh para detectar PRs
   - Workaround: Transições manuais via state_tracker.py

2. **Disk usage**: Cada worktree = repo size
   - Recomendação: Max 3-5 workers

3. **Platform**: Testado em Linux/WSL, pode precisar ajustes em macOS

## Próximos Passos após Testes

1. [ ] Todos testes passaram → Merge PR
2. [ ] Criar tag v2.0.0
3. [ ] Gerar GitHub Release
4. [ ] Atualizar Wiki com novidades
5. [ ] Close Epic #33 e sub-issues
