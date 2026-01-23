# sdlc-import Skill

**Version:** 2.1.0

Automatically reverse engineer existing codebases and generate complete SDLC Agêntico documentation.

## Quick Start

```bash
# Import existing project
/sdlc-import /path/to/project

# With GitHub issue creation
/sdlc-import /path/to/project --create-issues
```

## What It Does

1. **Creates feature branch** - `feature/import-{project-name}` for clean git history
2. **Detects languages** - **30 languages + frameworks** using LSP plugins (v2.1.0)
3. **Extracts decisions** - 5-15 ADRs with confidence scores
4. **Generates diagrams** - 3-5 architecture diagrams (Mermaid + DOT)
5. **Models threats** - STRIDE analysis with security-guidance plugin
6. **Identifies tech debt** - 10-50 items with P0-P3 priorities
7. **Creates documentation** - Complete `.agentic_sdlc/` structure

## Supported Technologies

**v2.1.0 - Massive Expansion: 30 Technologies**

**Programming Languages (14):**
- **Original (10):** Python, JavaScript, TypeScript, Java, C#, Go, Ruby, PHP, Rust, Kotlin
- **NEW (4):** C++, Gradle, Dart (Flutter), Swift (iOS)

**Backend Frameworks:**
- **Original:** Django, Flask, FastAPI, Spring, ASP.NET, Express, NestJS, Gin, Rails, Laravel, Symfony, Actix, Ktor
- **NEW:** CMake, Conan, vcpkg, Boost (C++), Tokio, async-std (Rust)

**Frontend Frameworks:**
- **Original:** React, Angular, Next.js
- **NEW:** Vue.js, Svelte, Tailwind CSS

**Mobile Development:**
- **NEW:** React Native, Flutter, SwiftUI/UIKit, Jetpack Compose (Android), Xamarin

**Infrastructure as Code:**
- **Original:** Terraform, Kubernetes
- **NEW:** Bicep (Azure), Ansible

**Configuration Management:**
- **NEW:** Chef, Puppet

**CI/CD:**
- **Original:** GitHub Actions, GitLab CI
- **NEW:** Jenkins

**Testing:**
- **Original:** pytest, jest, junit, mocha
- **NEW:** Selenium (multi-language), Playwright (multi-language)

**Build Tools:**
- **NEW:** Vite, Webpack

**Disambiguation:**
- Chef vs Ruby (via metadata.rb)
- Ansible vs YAML (via ansible.cfg)
- Gradle vs Kotlin (file-based)

## Architecture

```
┌──────────────────────────────────────────────┐
│         project_analyzer.py                  │
│            (Orchestrator)                    │
└──────────┬────────────────────────────┬──────┘
           │                            │
    ┌──────▼──────────┐        ┌───────▼────────┐
    │ language_       │        │ decision_      │
    │ detector.py     │        │ extractor.py   │
    │ (LSP plugins)   │        │ (Patterns+LLM) │
    └──────┬──────────┘        └───────┬────────┘
           │                            │
    ┌──────▼──────────┐        ┌───────▼────────┐
    │ architecture_   │        │ threat_        │
    │ visualizer.py   │        │ modeler.py     │
    │ (Mermaid/DOT)   │        │ (STRIDE)       │
    └──────┬──────────┘        └───────┬────────┘
           │                            │
    ┌──────▼──────────┐        ┌───────▼────────┐
    │ tech_debt_      │        │ documentation_ │
    │ detector.py     │        │ generator.py   │
    │ (code-review)   │        │ (Templates)    │
    └─────────────────┘        └────────────────┘
```

## Configuration

**Main config:** `.claude/skills/sdlc-import/config/import_config.yml`

```yaml
general:
  output_dir: ".agentic_sdlc"
  exclude_patterns: [".git", "node_modules", "__pycache__", "venv"]

language_detection:
  min_files: 3
  min_percentage: 5.0
  confidence_threshold: 0.7

decision_extraction:
  confidence:
    high: 0.8
    medium: 0.5
  llm:
    enabled: true
    model: "claude-sonnet-4-5"
```

## Confidence Scoring

```
confidence = 0.4 * evidence_quality +
             0.3 * evidence_quantity +
             0.2 * consistency +
             0.1 * llm_bonus
```

**Thresholds:**
- **HIGH** (>= 0.8) - Auto-accept, no review needed
- **MEDIUM** (0.5-0.8) - Needs validation
- **LOW** (< 0.5) - Create issue for manual review

## Plugin Integration

| Plugin | Purpose | Component |
|--------|---------|-----------|
| **pyright-lsp** | Python analysis | language_detector.py |
| **typescript-lsp** | JS/TS analysis | language_detector.py |
| **jdtls-lsp** | Java analysis | language_detector.py |
| **security-guidance** | Vulnerability scanning | threat_modeler.py |
| **code-review** | Code quality | tech_debt_detector.py |

## Output Structure

```
.agentic_sdlc/
├── corpus/nodes/decisions/
│   ├── ADR-INFERRED-001.yml  # Database decision
│   ├── ADR-INFERRED-002.yml  # Authentication decision
│   └── ...
├── security/
│   └── threat-model-inferred.yml  # STRIDE analysis
├── architecture/
│   ├── component-diagram.mmd      # Mermaid
│   ├── dependency-graph.dot       # Graphviz
│   └── data-flow.mmd              # Mermaid
└── reports/
    ├── tech-debt-inferred.md      # P0-P3 prioritized
    └── import-report.md           # Summary
```

## Quality Gate

**Gate:** `sdlc-import-gate.yml`

**Must pass:**
- ✅ Feature branch created
- ✅ Overall confidence >= 0.6
- ✅ Minimum 3 ADRs
- ✅ Zero CRITICAL threats
- ✅ Minimum 2 diagrams

## Examples

### Example 1: Django Project

```bash
/sdlc-import /path/to/django-blog

# Creates:
# - ADR-INFERRED-001: Use PostgreSQL as Primary Database (0.92)
# - ADR-INFERRED-002: Use JWT for API Authentication (0.85)
# - ADR-INFERRED-003: Use Redis for Session Caching (0.78)
# - component-diagram.mmd (Frontend → API → Database)
# - threat-model with 2 HIGH threats (JWT verification disabled)
# - tech-debt with 5 P0 items (Django 2.2 EOL)
```

### Example 2: React App

```bash
/sdlc-import /path/to/react-dashboard --create-issues

# Creates:
# - ADR-INFERRED-001: Use React 18 with TypeScript (0.95)
# - ADR-INFERRED-002: Use React Query for State Management (0.81)
# - component-diagram.mmd
# - GitHub issues for P0 tech debt
```

## Troubleshooting

**Issue:** "Overall confidence < 0.6"
- **Cause:** Not enough evidence found
- **Fix:** Enable LLM synthesis or add custom patterns to `decision_patterns.yml`

**Issue:** "No ADRs extracted"
- **Cause:** Project too small or unusual architecture
- **Fix:** Lower `min_files` threshold or add manual ADRs

**Issue:** "CRITICAL threats blocking gate"
- **Cause:** Security vulnerabilities detected
- **Fix:** Review threat model, fix vulnerabilities, re-run import

## Development

**Run tests:**
```bash
pytest .claude/skills/sdlc-import/tests/ -v
```

**Add custom patterns:**
Edit `.claude/skills/sdlc-import/config/decision_patterns.yml`

## References

- **ADR-022:** Automated Legacy Project Onboarding
- **awesome-copilot:** https://github.com/awesome-copilot/awesome-copilot
- **claude-plugins-official:** https://github.com/anthropics/claude-plugins-official

---

**Version:** 1.0.0
**Last Updated:** 2026-01-23
