---
name: token-status
description: Shows current token budget usage and recommendations
---

# Token Budget Status

Display current token usage, budget limits, and recommendations for optimization.

## Usage

```bash
/token-status
```

## What it does

1. **Calculates token usage** across:
   - Bootstrap files (orchestrator, agents, skills)
   - Tool schemas
   - Conversation history (estimated)
   - Corpus nodes (recent ADRs, patterns)

2. **Compares against budget**:
   - Global max: 200,000 tokens (Sonnet 4.5 limit)
   - Per-agent max: 50,000 tokens
   - Orchestrator max: 80,000 tokens

3. **Provides recommendations**:
   - Warns if files exceed 5KB (OpenClaw guideline)
   - Suggests progressive disclosure for large files
   - Recommends just-in-time skill loading

## Output Example

```
📊 TOKEN BUDGET STATUS

Budget: 200,000 tokens (global max)
Per-agent max: 50,000 tokens
Orchestrator max: 80,000 tokens

Known Usage: 23,450 tokens
Estimated Total: 63,450 tokens (31.7%)
Status: OK

Breakdown:
  Bootstrap Files: 12,300 tokens
  Tool Schemas: 3,000 tokens
  Skills Metadata: 3,000 tokens
  Agents Metadata: 2,000 tokens
  Corpus: 3,150 tokens
  Conversation History: 40,000 tokens (estimated)

Recommendations:
  ⚠️ orchestrator.md is 8,234 tokens (target: <5,000). Apply progressive disclosure pattern.
  ✅ Token usage is healthy
```

## When to Use

- **Before major operations**: Check budget before spawning parallel workers
- **When experiencing slowness**: High token usage can impact performance
- **During development**: Monitor impact of new agents/skills
- **After context overflow errors**: Diagnose which components are heavy

## Related

- `/prune-context` - Manually prune conversation history (future)
- `.claude/lib/python/token_counter.py` - Token counting library
- `.claude/settings.json` - `sdlc.token_budget` configuration

## Notes

- **Conversation history** is estimated (not measurable without API access)
- **Just-in-time loading** (not yet implemented) can reduce bootstrap tokens
- **Progressive disclosure** for orchestrator.md can save ~40% tokens

Based on OpenClaw pattern: https://github.com/openclaw/openclaw/issues/4561
