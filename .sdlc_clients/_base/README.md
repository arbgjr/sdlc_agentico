# Client Profile Template

This directory contains the template for creating new SDLC Agêntico client profiles.

## What is a Client Profile?

A **client profile** is a set of customizations on top of the base SDLC Agêntico framework that enables:

- **Agent Overrides**: Replace or add agents specific to your industry/domain
- **Custom Quality Gates**: Add validation specific to your compliance requirements
- **Custom Templates**: Modify documentation templates to match your standards
- **Client-Specific Corpus**: Build domain knowledge without polluting base framework

## When to Create a Client Profile?

Create a client profile when:

1. **Regulatory Requirements**: Your industry requires specific validation (financial, healthcare, government)
2. **Organizational Standards**: Your company has strict coding/documentation standards
3. **Specialized Workflows**: Your domain requires unique SDLC steps
4. **Knowledge Isolation**: You want client-specific learnings/patterns separate from base

**DON'T create a profile if**: You only need project-specific customization (use `.project/` instead)

## Quick Start

### Step 1: Scaffold New Client

```bash
# Run the creation command
/create-client --name "Your Company" --domain "industry" --id yourco

# This creates:
# .sdlc_clients/yourco/
# ├── profile.yml (from template)
# ├── agents/ (empty)
# ├── skills/ (empty)
# ├── templates/ (empty)
# ├── corpus/ (empty)
# └── README.md (client-specific)
```

### Step 2: Configure Auto-Detection

Edit `.sdlc_clients/yourco/profile.yml`:

```yaml
client:
  detection:
    markers:
      # Option 1: File marker (simplest)
      - path: ".yourco-client"
        type: file

      # Option 2: Environment variable
      - env: "CLIENT_ID"
        value: "yourco"
        type: env

      # Option 3: Git remote pattern
      - remote: "github.com/yourco/"
        type: git_remote
```

**Best Practice**: Use file marker for simplicity. Create `.yourco-client` in your projects.

### Step 3: Add Customizations

Choose what to customize (start small!):

#### Option A: Override Agent

```bash
# Copy base agent to client directory
cp .claude/agents/code-reviewer.md .sdlc_clients/yourco/agents/

# Edit to add custom checklist
vim .sdlc_clients/yourco/agents/code-reviewer.md
```

Update `profile.yml`:

```yaml
agents:
  overrides:
    - name: "code-reviewer"
      path: "agents/code-reviewer.md"
      reason: "Adds XYZ-specific code review checks"
```

#### Option B: Add Custom Quality Gate

```bash
# Create new gate
cat > .sdlc_clients/yourco/skills/gate-evaluator/gates/custom-gate.yml << EOF
gate_name: "compliance-check"
phase_transition: "6-to-7"
checks:
  - id: "compliance-docs-present"
    type: "file_exists"
    path: "docs/COMPLIANCE.md"
    severity: "critical"
EOF
```

Update `profile.yml`:

```yaml
gates:
  additions:
    - name: "compliance-check"
      path: "skills/gate-evaluator/gates/custom-gate.yml"
      after_phase: 6
```

#### Option C: Custom Template

```bash
# Copy base template
cp .agentic_sdlc/templates/adr-template.yml .sdlc_clients/yourco/templates/

# Add custom fields
vim .sdlc_clients/yourco/templates/adr-template.yml
```

### Step 4: Test Your Profile

```bash
# Set active client
/set-client yourco

# Verify detection
cat .project/.client  # Should show: yourco

# Run workflow
/sdlc-start "Test feature"

# Check logs for client-specific loading
# Should see: "Loaded client-specific: yourco/code-reviewer"
```

### Step 5: Validate Profile

```bash
# Run validation suite
./.sdlc_clients/_base/validate-client.sh .sdlc_clients/yourco

# Should pass:
# ✅ Profile schema valid
# ✅ All overridden agents exist
# ✅ All custom gates valid YAML
# ✅ Framework version compatible
```

## Profile Structure

```
.sdlc_clients/yourco/
├── profile.yml              # Client configuration (REQUIRED)
├── README.md                # Client-specific documentation
│
├── agents/                  # Agent overrides/additions
│   ├── code-reviewer.md     # Override base agent
│   └── compliance-agent.md  # New agent (client-specific)
│
├── skills/                  # Skill overrides/additions
│   ├── gate-evaluator/
│   │   └── gates/
│   │       └── custom-gate.yml
│   └── custom-validator/
│       ├── SKILL.md
│       └── scripts/
│
├── templates/               # Template overrides
│   ├── adr-template.yml
│   └── compliance-report.yml
│
├── corpus/                  # Client-specific knowledge
│   └── nodes/
│       ├── decisions/       # Client ADRs
│       ├── patterns/        # Industry patterns
│       └── learnings/       # Client learnings
│
└── hooks/                   # Hook overrides (optional)
    └── validate-commit.sh
```

## Resolution Order

When SDLC Agêntico loads resources, it follows this priority:

1. **Client override** (if exists): `.sdlc_clients/yourco/agents/code-reviewer.md`
2. **Base framework** (fallback): `.claude/agents/code-reviewer.md`
3. **Error** (if not found anywhere)

**Example**:

```python
# Orchestrator resolution
def resolve_agent(agent_name: str) -> Path:
    client = os.getenv("SDLC_CLIENT", "generic")

    # Check client override
    if client != "generic":
        client_path = f".sdlc_clients/{client}/agents/{agent_name}.md"
        if os.path.exists(client_path):
            return client_path  # ✅ Use override

    # Fallback to base
    base_path = f".claude/agents/{agent_name}.md"
    if os.path.exists(base_path):
        return base_path  # ✅ Use base

    # Not found
    raise AgentNotFoundError(agent_name)
```

## Corpus Merging

When querying knowledge (RAG), SDLC Agêntico searches in order:

1. **Base corpus**: `.agentic_sdlc/corpus/` (generic patterns, always included)
2. **Client corpus**: `.sdlc_clients/yourco/corpus/` (industry-specific knowledge)
3. **Project corpus**: `.project/corpus/` (project-specific decisions)

**Example RAG query**: "What are the authentication patterns?"

**Results**:
- Base: Generic OAuth2, JWT patterns
- Client: Industry-specific MFA requirements
- Project: This project's auth implementation decisions

## Best Practices

### ✅ DO

- **Start small**: Override 1-2 agents initially, validate before adding more
- **Document overrides**: Always fill `reason` field in `profile.yml`
- **Version carefully**: Use framework min/max versions to avoid breaking changes
- **Test thoroughly**: Run full SDLC workflow before deploying to team
- **Keep base generic**: Client-specific logic goes in client profile, not base framework

### ❌ DON'T

- **Don't fork framework**: Use profiles instead of forking entire codebase
- **Don't override unnecessarily**: Only override when truly different from base
- **Don't break base**: Client customizations shouldn't require base framework changes
- **Don't share secrets**: Client profiles can be in git, but NO secrets in `profile.yml`

## Troubleshooting

### Client not detected

```bash
# Check detection markers
cat .sdlc_clients/yourco/profile.yml | yq '.client.detection'

# Manually set client
/set-client yourco

# Verify
echo $SDLC_CLIENT  # Should show: yourco
cat .project/.client  # Should show: yourco
```

### Agent override not loading

```bash
# Check file exists
ls -la .sdlc_clients/yourco/agents/code-reviewer.md

# Check profile configuration
cat .sdlc_clients/yourco/profile.yml | yq '.agents.overrides'

# Check orchestrator logs
# Should see: "Loading agent: code-reviewer from .sdlc_clients/yourco/agents/"
```

### Version compatibility error

```bash
# Check framework version
cat .claude/VERSION | yq '.version'  # e.g., 3.0.0

# Check client requirements
cat .sdlc_clients/yourco/profile.yml | yq '.client.framework'

# Update client if needed
# min_version: "3.0.0"
# max_version: "3.99.99"
```

## Examples

See these example clients:

- **`.sdlc_clients/demo-client/`**: Minimal example showing customization mechanics
- **`.sdlc_clients/generic/`**: Alias to base framework (default when no client set)

## Support

- **Issues**: https://github.com/arbgjr/sdlc_agentico/issues
- **Discussions**: https://github.com/arbgjr/sdlc_agentico/discussions
- **Documentation**: `.agentic_sdlc/docs/`

---

**Next Steps**:
1. Run `/create-client` to scaffold your profile
2. Add 1-2 customizations
3. Test with `/sdlc-start`
4. Iterate based on team feedback
