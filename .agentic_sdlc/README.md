# Agentic SDLC - Framework Assets

This directory contains all Agentic SDLC framework assets, which are **reusable** across multiple projects.

## Structure

```
.agentic_sdlc/
├── templates/         # Reusable templates (ADR, spec, threat-model)
├── schemas/           # JSON Schemas for data validation
├── examples/          # Artifact examples
├── docs/              # Framework documentation
│   ├── guides/        # Usage guides (quickstart, troubleshooting)
│   ├── sdlc/          # SDLC documentation (agents, commands)
│   └── engineering-playbook/  # Standards and practices
├── scripts/           # Setup and utility scripts
└── logo.png           # Framework logo
```

## Installation

The framework is installed via setup script:

```bash
./.agentic_sdlc/scripts/setup-sdlc.sh
```

## Reuse Across Multiple Projects

To use the same framework in multiple projects, create symlinks:

```bash
cd ~/projects/my-project
ln -s ~/sdlc-agentico/.claude .claude
ln -s ~/sdlc-agentico/.agentic_sdlc .agentic_sdlc
mkdir -p .project
```

## Framework vs Project Separation

- **Framework** (`.agentic_sdlc/`): Reusable assets, versioned in this repository
- **Project** (`.project/`): Project-specific artifacts (corpus, decisions, reports)

This separation enables:
- ✅ Reuse framework across N projects
- ✅ Portability (copy 2 directories = ready framework)
- ✅ Selective gitignore (version decisions, ignore sessions)
- ✅ Clarity (developer knows what is framework vs project)

## Versioning

The framework follows [Semantic Versioning](https://semver.org/):
- **Major**: Breaking changes, architectural changes
- **Minor**: New features, new agents
- **Patch**: Bug fixes, documentation

See `.claude/VERSION` for the current version.
