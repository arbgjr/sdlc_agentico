---
description: 'Output style for developing, modifying, or debugging SDLC agents. Use when working with .claude/agents/*.md files.'
applyTo: '.claude/agents/**'
---

# Agent Developer Output Style

When developing or modifying SDLC agents:

## Agent Design Principles

1. **Single Responsibility** - One agent, one job
2. **Conciseness** - Max 500 lines per agent
3. **Progressive Disclosure** - Show details on demand
4. **Tool Minimalism** - Only necessary tools
5. **Skill Reuse** - Prefer skills over inline logic

## Output Structure

### When Creating Agents

```markdown
# Agent: {name}

## Purpose
[One sentence - what problem does this solve?]

## Responsibilities
- [Specific task 1]
- [Specific task 2]

## Frontmatter Design
- model: [sonnet|opus] (use opus only for complex reasoning)
- skills: [list of reusable skills]
- tools: [minimal set]

## Integration Points
- Phase: [which SDLC phase]
- Dependencies: [which agents must run first]
- Outputs: [what artifacts this creates]
```

### When Modifying Agents

```markdown
## Modification: {agent-name}

**Change Type**: [override|addition|refactor]

**Rationale**:
[Why this change is needed]

**Impact Analysis**:
- Agents affected: [list]
- Gates affected: [list]
- Backward compatibility: [yes|no - explain]

**Testing**:
- [ ] Agent loads successfully
- [ ] Frontmatter valid
- [ ] Skills available
- [ ] Integration with orchestrator works
```

## Tone

- **Technical and precise** - Agent specs are contracts
- **Questioning** - Challenge unnecessary complexity
- **Pattern-aware** - Reference similar agents for consistency

## Anti-Patterns

- ❌ Don't create agents > 500 lines (use skills instead)
- ❌ Don't duplicate logic across agents
- ❌ Don't use opus model unless truly needed
- ❌ Don't add tools without justification
