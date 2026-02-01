# Demo Client Profile

**⚠️ THIS IS A DEMONSTRATION PROFILE FOR LEARNING PURPOSES ⚠️**

This client profile is intentionally **minimal** and **generic**. It demonstrates the mechanics of customization without specializing the framework for any specific industry.

## Purpose

This profile shows **HOW** to customize SDLC Agêntico, not **WHAT** to customize for your domain. Real client profiles (financial, healthcare, government, etc.) would have domain-specific customizations based on their requirements.

## What's Customized?

This demo includes **minimal examples** of each customization type:

### 1. Agent Override: code-reviewer

- **Base**: `.claude/agents/code-reviewer.md`
- **Override**: `clients/demo-client/agents/code-reviewer.md`
- **Change**: Adds ONE custom checklist item ("Check for TODOs")
- **Similarity**: 95% identical to base
- **Purpose**: Shows override mechanics without heavy customization

### 2. Custom Gate: demo-custom-gate

- **Location**: `clients/demo-client/skills/gate-evaluator/gates/demo-custom-gate.yml`
- **When**: After Phase 6 (Quality)
- **Validates**: ADRs have "Impact" section
- **Purpose**: Simple validation example (NOT domain-specific)

### 3. Template Override: adr-template-custom

- **Base**: `.agentic_sdlc/templates/adr-template.yml`
- **Override**: `clients/demo-client/templates/adr-template-custom.yml`
- **Change**: Adds ONE extra field ("Business Impact")
- **Purpose**: Shows template customization without major changes

## Activation

To use this demo client:

```bash
# Option 1: Manual activation
/set-client demo-client

# Option 2: Auto-detection (create marker file)
touch .demo-client
# Framework auto-detects on next workflow
```

## Testing

Run a full workflow to see customizations in action:

```bash
/set-client demo-client
/sdlc-start "Test feature for demo"
```

**Expected behavior**:
- Phase 5: Uses overridden `code-reviewer` (with custom checklist)
- Phase 6→7: Triggers `demo-custom-gate` (validates ADR impact)
- Phase 7: Uses custom ADR template (with extra field)
- **All other agents/skills**: Use base framework (generic)

## Important Notes

### This is NOT:
- ❌ A production-ready client profile
- ❌ Domain-specific (financial, healthcare, etc.)
- ❌ A replacement for your own client profile
- ❌ Heavily customized (intentionally minimal)

### This IS:
- ✅ A learning example
- ✅ A starting point for your own profile
- ✅ A demonstration of customization mechanics
- ✅ Generic and technology-agnostic

## Creating Your Own Client

After understanding this demo, create your own:

```bash
/create-client --name "Your Company" --domain "your-industry" --id yourco
```

Then customize based on **your specific requirements**:
- Compliance needs (SOX, HIPAA, PCI, LGPD, etc.)
- Organizational standards (code review, security, testing)
- Industry patterns (financial services, healthcare, government)
- Tool-specific integrations

## Learning Resources

- **Template**: `clients/_base/profile.yml` - Full schema
- **Guide**: `clients/_base/README.md` - Comprehensive onboarding
- **Framework Docs**: `.agentic_sdlc/docs/` - SDLC concepts
- **Agent Docs**: `.claude/agents/*.md` - Individual agent guides

## Questions?

- **Issues**: https://github.com/arbgjr/sdlc_agentico/issues
- **Discussions**: https://github.com/arbgjr/sdlc_agentico/discussions

---

**Remember**: This is a DEMO. Real clients customize for their domain, not for the sake of customization.
