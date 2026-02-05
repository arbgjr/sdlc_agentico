# Copilot Coding Agent Instructions for Agentic SDLC

## Overview
This repository implements the **Agentic SDLC**: an AI agent-oriented development orchestration framework, covering all phases of the software lifecycle. The project is highly configurable, driven by files in `.claude/` and `\.agentic_sdlc/docs/`.

## How to be productive here
- **Never write "loose" code**: every implementation must be guided by specs, user stories, or documented decisions (ADRs).
- **Follow the SDLC flow**: use commands like `/sdlc-start`, `/sdlc-create-issues`, `/gate-check` to navigate between phases and ensure quality.
- **Respect quality gates**: each phase transition requires automatic validation (see `.claude/skills/gate-evaluator/gates/`).
- **Implement by agent**: each agent has clear responsibilities and YAML outputs (see `\.agentic_sdlc/docs/AGENTS.md`).
- **Document decisions**: every relevant architecture change must generate an ADR.

## Structure and Architecture
- `.claude/settings.json`: configures agents, phases, hooks, and gates.
- `.claude/agents/`, `\.agentic_sdlc/docs/AGENTS.md`: agent catalog and responsibilities.
- `.claude/skills/`: reusable skills (e.g., `rag-query`, `memory-manager`).
- `\.agentic_sdlc/docs/`: documentation, playbook, commands, and infrastructure.
- `\.agentic_sdlc/scripts/setup-sdlc.sh`: automated dependency installation.

## Workflows and Essential Commands
- `./\.agentic_sdlc/scripts/setup-sdlc.sh`: installs everything (Python, Node, CLI, etc).
- `claude`: main CLI for orchestration and SDLC commands.
- `/sdlc-start "New feature"`: starts workflow.
- `/sdlc-create-issues --assign-copilot`: creates issues and assigns to Copilot.
- `/gate-check`: validates phase transition.
- `/adr-create`: records architectural decision.

## Conventions and Standards
- **Commits and PRs**: must reference phases, agents, and YAML outputs.
- **Tests**: required for every feature (see `test-author` outputs).
- **Observability**: always include metrics and logs according to `observability-engineer` outputs.
- **Small changes**: prefer small and incremental PRs.
- **Copilot Integration**: issues can be assigned to Copilot for automatic implementation.

## YAML Output Examples
- User Story:
  ```yaml
  user_story:
    id: "US-001"
    story: "As a user, I want to..."
    acceptance_criteria:
      - given: "..."
        when: "..."
        then: "..."
  ```
- Quality Report:
  ```yaml
  quality_report:
    summary:
      status: approved
    test_execution:
      passed: 10
      failed: 0
  ```

## Integrations
- **GitHub Copilot Coding Agent**: issues can be assigned for automatic implementation.
- **Spec Kit**: requirements specification and validation.
- **Claude Code CLI**: agent orchestration and SDLC commands.

## References
- `\.agentic_sdlc/docs/AGENTS.md`: agent catalog and expected outputs
- `.claude/settings.json`: central configuration
- `\.agentic_sdlc/docs/playbook.md`: development principles and standards
- `\.agentic_sdlc/docs/COMMANDS.md`: command reference

> Always follow the SDLC flow, document decisions, and use agents according to their responsibilities.
