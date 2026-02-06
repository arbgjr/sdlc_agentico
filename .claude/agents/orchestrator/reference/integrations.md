# External Integrations Reference

GitHub, Spec Kit, parallel workers, and auto-update integrations.

## Overview

The orchestrator integrates with external systems to automate project management, documentation, and deployment workflows.

---

## Auto-Update System (v1.8.1+)

### When to Check

At the start of EVERY SDLC workflow:
- `/sdlc-start`
- `/quick-fix`
- `/new-feature`
- Phase 0 transition

### Update Workflow

```python
# 1. Check for updates
import subprocess
import json

result = subprocess.run(
    ["python3", ".claude/skills/version-checker/scripts/check_updates.py"],
    capture_output=True,
    text=True,
    timeout=10
)

update_info = json.loads(result.stdout)

# 2. If update available and not dismissed
if update_info.get("update_available") and not update_info.get("dismissed"):
    # Present options via AskUserQuestion
    response = AskUserQuestion({
        "questions": [{
            "question": "Nova versão disponível do SDLC Agêntico. O que deseja fazer?",
            "header": "Update",
            "multiSelect": False,
            "options": [
                {
                    "label": "Update now (Recomendado)",
                    "description": f"Atualizar para v{update_info['latest']} agora"
                },
                {
                    "label": "Show full changelog",
                    "description": "Ver changelog completo antes de decidir"
                },
                {
                    "label": "Skip this version",
                    "description": "Não atualizar esta versão (não pergunta novamente)"
                },
                {
                    "label": "Remind me later",
                    "description": "Perguntar novamente no próximo workflow"
                }
            ]
        }]
    })

    # 3. Process response
    if response["Update"] == "Update now (Recomendado)":
        logger.info(f"Executando update para v{update_info['latest']}")

        update_result = subprocess.run(
            ["python3", ".claude/skills/version-checker/scripts/check_updates.py", "--execute"],
            capture_output=True,
            text=True,
            timeout=300
        )

        exec_result = json.loads(update_result.stdout)

        if exec_result.get("success"):
            logger.info("Update completed successfully")
            # Workflow STOPS - user must restart session
            return {
                "status": "update_completed",
                "message": "SDLC Agêntico atualizado com sucesso. Por favor, reinicie a sessão."
            }
        else:
            logger.error(f"Update failed: {exec_result.get('error')}")
            # Continue with current version

    elif response["Update"] == "Skip this version":
        # Dismiss permanently
        subprocess.run(
            ["python3", ".claude/skills/version-checker/scripts/check_updates.py",
             "--dismiss", update_info["latest"]],
            timeout=5
        )
```

### Error Handling

If `check_updates.py` fails (GitHub unreachable, etc):

```python
try:
    result = check_updates()
except subprocess.TimeoutExpired:
    logger.warning("Update check timeout - continuing workflow")
    # Continue normally
except Exception as e:
    logger.warning(f"Update check failed: {e} - continuing workflow")
    # Continue normally
```

**CRITICAL RULE**: Update check failure NEVER blocks workflow execution.

---

## GitHub Integration

### Phase 0 (Intake) - Create Project and Milestone

When starting workflow with `/sdlc-start`:

```bash
# 1. Ensure SDLC labels exist
python3 .claude/skills/github-sync/scripts/label_manager.py ensure

# 2. Create GitHub Project V2
python3 .claude/skills/github-projects/scripts/project_manager.py create \
  --title "SDLC: {feature_name}"

# 3. Configure custom fields (Phase, Sprint, Story Points)
python3 .claude/skills/github-projects/scripts/project_manager.py configure-fields \
  --project-number {N}

# 4. Create first Milestone (Sprint 1)
python3 .claude/skills/github-sync/scripts/milestone_sync.py create \
  --title "Sprint 1" \
  --description "Sprint inicial" \
  --due-date "$(date -d '+14 days' +%Y-%m-%d)"
```

---

### Phase Transition - Update Project

When advancing phases:

```bash
# Update Phase field on issues in Project
python3 .claude/skills/github-projects/scripts/project_manager.py update-field \
  --project-number {N} \
  --item-id {item_id} \
  --field "Phase" \
  --value "{new_phase_name}"
```

---

### Phase 7 (Release) - Close and Synchronize

When release gate passes:

```bash
# 1. Generate professional documentation (if needed)
python3 .claude/skills/doc-generator/scripts/generate_docs.py

# 2. Close current sprint Milestone
python3 .claude/skills/github-sync/scripts/milestone_sync.py close \
  --title "{current_sprint}"

# 3. Synchronize documentation with Wiki
.claude/skills/github-wiki/scripts/wiki_sync.sh

# 4. If tag exists, create GitHub Release
gh release create v{version} \
  --title "Release v{version}" \
  --notes-file CHANGELOG.md
```

---

### Documentation Generator (doc-generator v1.8.1)

**When to Generate**:
- Start of new project (Phase 0 or 1)
- Before release (Phase 7)
- Significant technology stack changes
- On-demand via `/doc-generate`

**What It Generates**:
- `CLAUDE.md` - Guide for Claude Code with stack, architecture, commands
- `README.md` - Project documentation with features, installation, usage
- **Automatic signature**: `🤖 Generated with SDLC Agêntico by @arbgjr`

**Auto-Detection**:
- Languages (Python, JS, TS, Java, C#, Go, Rust, Ruby)
- Frameworks (Django, Flask, React, Next.js, Vue, Angular, Express, .NET)
- Directory structure (tree up to 3 levels)
- Tests (detects test files and directories)
- Docker (detects Dockerfile)
- CI/CD (detects GitHub Actions)

**Invocation**:
```bash
# Via direct command
python3 .claude/skills/doc-generator/scripts/generate_docs.py

# Force overwrite existing files
python3 .claude/skills/doc-generator/scripts/generate_docs.py --force

# Generate in specific directory
python3 .claude/skills/doc-generator/scripts/generate_docs.py --output-dir /path/to/project
```

**Post-Generation**:
- Review generated files
- Customize placeholders (features, usage examples)
- Add project-specific details
- Commit with message: `docs: generate CLAUDE.md and README.md with SDLC signature`

---

### Phase → Project Column Mapping

| SDLC Phase | Project Column |
|------------|----------------|
| Phase 0-1 | Backlog |
| Phase 2 | Requirements |
| Phase 3 | Architecture |
| Phase 4 | Planning |
| Phase 5 | In Progress |
| Phase 6 | QA |
| Phase 7 | Release |
| Complete | Done |

---

### Useful Commands

- `/github-dashboard` - View consolidated status
- `/wiki-sync` - Sync docs with Wiki manually
- `/sdlc-create-issues` - Create issues from tasks
- `/parallel-spawn` - Spawn parallel workers (Phase 5, Complexity 2+)
- `/doc-generate` - Generate CLAUDE.md and README.md with SDLC signature

---

## Spec Kit Integration

When complexity >= 2, use Spec Kit templates:

1. **Phase 2 (Requirements)** → Generate Spec using `/spec-create`
2. **Phase 3 (Architecture)** → Generate Technical Plan via `/spec-plan`
3. **Phase 4 (Planning)** → Break into Tasks via `/spec-tasks`
4. **Phase 5 (Implementation)** → Execute Tasks, not Stories

---

## Parallel Workers (v2.0)

**NEW**: When entering Phase 5 (Implementation), spawn parallel workers to accelerate execution.

### When to Use

- **Phase**: 5 (Implementation)
- **Complexity**: Level 2 or 3
- **Condition**: Task spec exists (`.agentic_sdlc/projects/current/tasks.yml`)
- **Benefit**: 2.5x speedup for 3 workers

---

### Automatic Workflow

```
Phase 4 (Planning) Complete
  ↓
Gate 4→5 Approved
  ↓
Orchestrator detects:
  - complexity_level >= 2
  - tasks.yml exists
  - independent tasks > 1
  ↓
Decision: Use parallel-workers?
  ↓
YES → Spawn workers automatically
  ↓
python3 .claude/skills/parallel-workers/scripts/worker_manager.py spawn-batch \
  --spec-file .agentic_sdlc/projects/current/tasks.yml
  ↓
python3 .claude/skills/parallel-workers/scripts/loop.py --project {project-name} &
  ↓
Monitor progress via Loki/Grafana
  ↓
When all workers MERGED → Gate 5→6
```

---

### Decision: Parallel vs Sequential

**Use parallel when**:
- ✅ Complexity 2+
- ✅ 3+ independent tasks (no blocking dependencies)
- ✅ Team size >= 2
- ✅ Well-defined tasks (not ambiguous)

**Use sequential when**:
- ❌ Complexity 0-1
- ❌ Dependent tasks (single critical path)
- ❌ Ambiguous tasks (need discovery)
- ❌ Single developer

---

### Monitoring

During Phase 5 with parallel workers:

1. **Loki queries for tracking**:
```logql
{skill="parallel-workers", phase="5"}
{skill="parallel-workers", state="WORKING"}
{skill="parallel-workers", level="error"}
```

2. **State tracker for status**:
```bash
python3 .claude/skills/parallel-workers/scripts/state_tracker.py list
```

3. **Worker manager for intervention**:
```bash
# If worker stuck
python3 .claude/skills/parallel-workers/scripts/worker_manager.py terminate worker-abc123 --force

# Respawn
python3 .claude/skills/parallel-workers/scripts/worker_manager.py spawn ...
```

---

### Gate 5→6 with Parallel Workers

Before approving gate 5→6:

```yaml
checks:
  - all_workers_state: MERGED
  - no_open_prs: true
  - worktrees_cleaned: true
  - code_quality: passed
  - tests_passed: passed
```

**If workers still active**:
- WAIT: "Workers still executing. Awaiting completion..."
- MONITOR: Show progress via state tracker
- ESCALATE: If blocked > 1h, notify user

---

### Human-in-the-Loop

**When to escalate to user**:
- Worker in ERROR state > 30min
- PR created but not merged > 24h
- Merge conflicts detected
- Security gate failed

**Escalation message**:
```
⚠️  Parallel worker {worker-id} needs attention:
- Task: {task-id}
- State: {state}
- Issue: {error-description}
- Action needed: {suggested-action}
```

---

## Research and Governance

### Research Points

When encountering new scenarios, research:
- "multi-agent orchestration patterns" for new patterns
- "quality gates best practices" to improve gates
- arXiv papers on LLM-based agents for new techniques

### Governance

Monitor and report to `playbook-governance`:
- Exceptions to playbook rules
- Undocumented emerging patterns
- Improvement suggestions based on metrics

---

## Impact Analysis Before Updates

Before executing any update, ALWAYS show user:

1. **Breaking Changes** - Complete list
2. **Migrations Required** - Scripts that will execute
3. **Security Fixes** - CVEs fixed
4. **Dependency Updates** - Version changes

### Example Notification

```markdown
🟡 Update Available: v2.1.0

**Upgrade type:** MINOR
**Released:** 2026-01-24
**Impact Analysis:**

✅ New Features (3):
  - Multi-client architecture
  - Enhanced RAG corpus
  - Parallel worker support

⚠️ Breaking Changes (1):
  - CRITICAL: .claude/memory/ → .agentic_sdlc/ migration
  - Action: Run migration script

🔒 Security Fixes (2):
  - CVE-2026-001: Path traversal in file upload
  - CVE-2026-002: XSS in markdown renderer

📦 Dependency Updates:
  - pyyaml: 6.0.1 → 6.0.2
  - requests: 2.31.0 → 2.32.0

🔄 Migrations:
  - [REQUIRED] Migrate artifacts to .agentic_sdlc/
  - [OPTIONAL] Update gate YAML format

Estimated update time: 2-5 minutes
```

---

**Version**: 3.0.3
**Last Updated**: 2026-02-02
