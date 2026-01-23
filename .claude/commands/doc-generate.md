---
name: doc-generate
description: Generate CLAUDE.md and README.md for project with SDLC Agêntico signature
---

# Generate Project Documentation

Generate professional CLAUDE.md and README.md files by analyzing your project structure.

## What This Does

1. **Analyzes Project**: Detects languages, frameworks, directory structure
2. **Generates CLAUDE.md**: Creates Claude Code guidance document
3. **Generates README.md**: Creates project README with standard sections
4. **Adds Signature**: Includes "🤖 Generated with SDLC Agêntico by @arbgjr"

## Detection

The generator automatically detects:
- **Languages**: Python, JavaScript, TypeScript, Java, C#, Go, Rust, Ruby
- **Frameworks**: Django, Flask, FastAPI, React, Next.js, Vue, Angular, Express, .NET
- **Tests**: Test files and directories
- **Docker**: Dockerfile presence
- **CI/CD**: GitHub Actions workflows

## Usage

```bash
/doc-generate
```

## Options

You can also run the script directly with options:

```bash
# Generate with default settings
python3 .claude/skills/doc-generator/scripts/generate_docs.py

# Force overwrite existing files
python3 .claude/skills/doc-generator/scripts/generate_docs.py --force

# Generate in specific directory
python3 .claude/skills/doc-generator/scripts/generate_docs.py --output-dir /path/to/project
```

## Generated Files

### CLAUDE.md
- Project overview with detected technologies
- Architecture description
- Directory structure tree
- Development setup instructions
- Code standards and conventions
- Testing strategy
- Deployment guide

### README.md
- Project description
- Features list (placeholder - edit as needed)
- Tech stack
- Getting started guide
- Usage examples (placeholder - edit as needed)
- Development instructions
- Contributing guidelines

## Signature

Both files end with:

```markdown
---

🤖 *Generated with [SDLC Agêntico](https://github.com/arbgjr/sdlc_agentico) by [@arbgjr](https://github.com/arbgjr)*
```

## Next Steps

After generation:

1. **Review generated files** - Check for accuracy
2. **Customize placeholders** - Fill in features, usage examples
3. **Add project-specific details** - Architecture diagrams, API docs
4. **Commit to repository** - Include in version control

## Example Output

For a Python/Django project, generates:

**CLAUDE.md**:
```markdown
# CLAUDE.md

## Project Overview

my-django-app - A Python project

**Key Technologies:**
- **Languages**: Python
- **Frameworks**: Django

...

🤖 *Generated with [SDLC Agêntico](https://github.com/arbgjr/sdlc_agentico) by [@arbgjr](https://github.com/arbgjr)*
```

**README.md**:
```markdown
# my-django-app

A modern Python application

## Tech Stack

- **Python**
- **Django**

...

🤖 *Generated with [SDLC Agêntico](https://github.com/arbgjr/sdlc_agentico) by [@arbgjr](https://github.com/arbgjr)*
```

## Tips

- Run in project root directory for best results
- Use `--force` to regenerate after project changes
- Customize templates in `.claude/skills/doc-generator/templates/`
- Generated docs are starting points - always review and enhance

## Related Commands

- `/adr-create` - Create Architecture Decision Records
- `/release-prep` - Prepare release documentation
- `/wiki-sync` - Sync docs to GitHub Wiki
