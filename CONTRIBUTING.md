# Contributing to Agentic SDLC

Thank you for your interest in contributing! This document explains how to participate in development.

## How to Contribute

### 1. Report Bugs

Open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Claude Code version and operating system

### 2. Suggest Features

Before implementing, open an issue for discussion:
- Describe the use case
- Explain the expected benefit
- Propose an initial solution

### 3. Contribute Code

```bash
# 1. Fork and clone
git clone https://github.com/arbgjr/sdlc_agentico.git
cd sdlc_agentico

# 2. Create a branch
git checkout -b feat/feature-name

# 3. Make changes
# ... code ...

# 4. Test locally
./\.agentic_sdlc/scripts/setup-sdlc.sh
claude
/sdlc-start "test"

# 5. Commit following Conventional Commits
git commit -m "feat(agents): add new agent for X"

# 6. Push and open PR
git push origin feat/feature-name
```

## Code Standards

### Commits

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

**Allowed types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Refactoring without functional change
- `test` - Adding/modifying tests
- `chore` - Maintenance

**Common scopes:**
- `agents` - Agents (.claude/agents/)
- `skills` - Skills (.claude/skills/)
- `commands` - Commands (.claude/commands/)
- `hooks` - Hooks (.claude/hooks/)
- `gates` - Quality gates
- `docs` - Documentation

**Examples:**
```bash
feat(agents): add compliance-guardian agent
fix(hooks): correct phase detection regex
docs(readme): update installation instructions
```

### Agent Structure

Each agent must follow this template:

```markdown
---
name: agent-name
description: Brief description
model: sonnet | opus | haiku
skills:
  - skill-name
tools:
  - Read
  - Write
  - etc
---

# Agent Name

## Purpose
Detailed description of purpose.

## When to Use
- Situation 1
- Situation 2

## Expected Input
```yaml
input:
  field1: type
  field2: type
```

## Output
```yaml
output:
  field1: type
  field2: type
```

## Process
1. Step 1
2. Step 2
3. Step 3

## Checklist
- [ ] Item 1
- [ ] Item 2
```

### Skill Structure

```markdown
---
name: skill-name
description: Brief description
---

# Skill Name

## Purpose
What the skill does.

## How to Use
Usage instructions.

## Parameters
- `param1`: Description
- `param2`: Description

## Examples
```bash
# Example 1
```
```

### Command Structure

```markdown
---
name: /command-name
description: Brief description
arguments:
  - name: arg1
    required: true
    description: What it is
---

# /command-name

## Usage
```bash
/command-name <arg1> [options]
```

## Parameters
- `arg1` (required): Description

## What It Does
1. Step 1
2. Step 2

## Examples
```bash
/command-name value
```
```

## Adding New Components

### New Agent

1. Create file at `.claude/agents/agent-name.md`
2. Follow the template above
3. Add to `settings.json` in `agents.available_agents`
4. Add to `\.agentic_sdlc/docs/AGENTS.md`
5. Test: `"Use the agent-name for..."`

### New Skill

1. Create directory at `.claude/skills/skill-name/`
2. Create `SKILL.md` with the template
3. Add necessary scripts
4. Test by invoking from an agent

### New Command

1. Create file at `.claude/commands/name.md`
2. Follow the template above
3. Add to `\.agentic_sdlc/docs/COMMANDS.md`
4. Test: `/command-name`

### New Hook

1. Create script at `.claude/hooks/name.sh`
2. Make executable: `chmod +x .claude/hooks/name.sh`
3. Configure in `.claude/settings.json`
4. Test the trigger

### New Gate

1. Create file at `.claude/skills/gate-evaluator/gates/phase-X-to-Y.yml`
2. Define required artifacts
3. Define quality criteria
4. Add to `\.agentic_sdlc/docs/COMMANDS.md`

## Tests

### Manual Tests

```bash
# Test complete workflow
claude
/sdlc-start "Test feature"

# Test specific gate
/gate-check phase-2-to-3

# Test command
/security-scan
```

### PR Checklist

Before opening a PR, verify:

- [ ] Code follows established standards
- [ ] Documentation updated
- [ ] Tested locally
- [ ] No secrets in code
- [ ] Commits follow Conventional Commits
- [ ] PR has clear description

## Review Process

1. **Author**: Opens PR with clear description
2. **Reviewer**: Reviews code and documentation
3. **CI**: Validates hooks and formatting
4. **Merge**: Squash merge to main

## Governance

### Architectural Decisions

For significant changes:
1. Open discussion issue
2. If approved, create ADR
3. Implement after approval

### Breaking Changes

- Requires prior discussion
- Document migration
- Major version bump

## Contact

- Issues: [GitHub Issues](https://github.com/arbgjr/sdlc_agentico/issues)
- Discussions: [GitHub Discussions](https://github.com/arbgjr/sdlc_agentico/discussions)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

---

Thank you for contributing!
