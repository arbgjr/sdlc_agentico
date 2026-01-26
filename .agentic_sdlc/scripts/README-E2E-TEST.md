# End-to-End Framework Test

## Overview

**`test-framework-e2e.sh`** simulates a complete SDLC workflow with a real project example ("Todo App API") to validate all framework capabilities.

## What It Tests

### 12 Test Scenarios

1. **Framework Structure** - Validates `.agentic_sdlc/` directories (templates, schemas, docs, scripts)
2. **Project Structure** - Creates and validates `.project/` directories
3. **Phase 0 (Intake)** - Creates intake brief with business requirements
4. **Phase 1 (Discovery)** - Documents tech stack (Python, FastAPI, PostgreSQL)
5. **Phase 2 (Requirements)** - Writes user stories with acceptance criteria
6. **Phase 3 (Architecture)** - Creates ADRs, architecture diagrams, threat models
7. **Template Usage** - Validates templates are accessible
8. **Quality Gates** - Checks gate YAML files exist
9. **Corpus RAG** - Creates multiple ADRs and learnings
10. **Documentation** - Validates framework docs are accessible
11. **Logging** - Tests structured logging (DEBUG, INFO, WARN)
12. **Hooks** - Validates framework validation hook exists and is executable

### Simulated Project: "Todo App API"

**Tech Stack:**
- Language: Python
- Framework: FastAPI
- Database: PostgreSQL
- Tools: pytest, black, ruff
- Infrastructure: Docker, GitHub Actions

**Artifacts Created:**
- Intake brief
- Tech stack analysis
- User stories (US-001, US-002)
- ADRs (Use FastAPI, Use PostgreSQL)
- Architecture diagram (Mermaid)
- Threat model (3 threats: brute force, authorization, SQL injection)
- Learnings (FastAPI async patterns)

## Usage

### Quick Test (5 seconds)

```bash
./.agentic_sdlc/scripts/test-framework-e2e.sh
```

### Expected Output

```
╔════════════════════════════════════════════════╗
║   SDLC Agêntico - End-to-End Framework Test   ║
╚════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Test 1: Validate Framework Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PASS: Templates directory exists
✅ PASS: Schemas directory exists
✅ PASS: Docs directory exists
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  TEST SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All tests PASSED

Framework validation complete:
  ✅ Structure validated
  ✅ Templates accessible
  ✅ Schemas present
  ✅ Documentation available
  ✅ Quality gates configured
  ✅ Corpus operations working
  ✅ Logging integrated
  ✅ Hooks executable
```

### Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed (artifacts preserved for inspection)

### Logging to Loki

All test steps are logged to Loki with:
- `skill=framework-e2e-test`
- `phase=0`
- Correlation ID for tracing

**Grafana Query:**
```logql
{app="sdlc-agentico", skill="framework-e2e-test"}
```

## Integration with CI/CD

Add to GitHub Actions:

```yaml
- name: Run E2E Framework Test
  run: |
    ./.agentic_sdlc/scripts/test-framework-e2e.sh
```

## Troubleshooting

### Test Fails

If tests fail, artifacts are preserved in `/tmp/sdlc-test-XXXXXX`. Check:

```bash
ls /tmp/sdlc-test-*/.project/phases/
cat /tmp/sdlc-test-*/.project/corpus/nodes/decisions/*.yml
```

### Missing Dependencies

Ensure `.claude/lib/shell/logging_utils.sh` exists:

```bash
ls -la .claude/lib/shell/logging_utils.sh
```

### Permission Issues

Make script executable:

```bash
chmod +x .agentic_sdlc/scripts/test-framework-e2e.sh
```

## When to Run

- **Before releases** - Validate framework integrity
- **After refactoring** - Ensure no regressions
- **Post-migration** - Verify framework/project separation
- **CI/CD pipelines** - Automated validation

## Complementary Tests

| Test Type | File | Focus |
|-----------|------|-------|
| **Unit Tests** | `test_framework_integration.py` | Individual components |
| **E2E Test** | `test-framework-e2e.sh` | Complete workflow |
| **Smoke Test** | `test_smoke_test()` | Critical paths only |

Run all:

```bash
# Unit tests
pytest .claude/skills/gate-evaluator/tests/test_framework_integration.py -v

# E2E test
./.agentic_sdlc/scripts/test-framework-e2e.sh

# Smoke test
pytest .claude/skills/gate-evaluator/tests/test_framework_integration.py::test_smoke_test -v
```

## Benefits

✅ **Comprehensive** - Tests 12 different framework capabilities
✅ **Fast** - Completes in ~5 seconds
✅ **Realistic** - Simulates actual project workflow
✅ **Self-contained** - Uses temporary directory, cleans up
✅ **Observable** - Logs all steps to Loki
✅ **CI-friendly** - Returns proper exit codes
✅ **Debuggable** - Preserves artifacts on failure

## See Also

- `.claude/skills/gate-evaluator/tests/test_framework_integration.py` - Unit tests
- `.claude/hooks/validate-framework-structure.sh` - Framework validation hook
- `\.agentic_sdlc/docs/guides/quickstart.md` - Getting started guide
