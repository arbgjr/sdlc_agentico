# /create-client

**Purpose**: Create a new SDLC Agêntico client profile from template.

**Usage**: `/create-client --name "Company Name" --domain "industry" --id client-id`

**Arguments**:
- `--name`: Client display name (e.g., "Acme Corporation")
- `--domain`: Industry domain (e.g., "financial-services", "healthcare", "government")
- `--id`: Client ID (lowercase, hyphens, e.g., "acme-corp")

**Examples**:
```bash
# Financial services client
/create-client --name "Acme Financial" --domain "financial-services" --id acme-financial

# Healthcare client
/create-client --name "MedTech Inc" --domain "healthcare" --id medtech

# Government client
/create-client --name "Gov Agency" --domain "government" --id gov-agency
```

**What it creates**:
```
clients/your-id/
├── profile.yml              # Client configuration
├── README.md                # Client-specific docs
├── agents/                  # Agent overrides (empty)
├── skills/
│   └── gate-evaluator/
│       └── gates/           # Custom gates (empty)
├── templates/               # Template overrides (empty)
└── corpus/
    └── nodes/
        ├── decisions/       # Client ADRs (empty)
        ├── patterns/        # Client patterns (empty)
        └── learnings/       # Client learnings (empty)
```

**Next Steps After Creation**:
1. Review `clients/your-id/profile.yml`
2. Add customizations:
   - Override agents (copy from `.claude/agents/`)
   - Add custom gates (create in `skills/gate-evaluator/gates/`)
   - Override templates (copy from `.agentic_sdlc/templates/`)
3. Activate client: `/set-client your-id`
4. Test workflow: `/sdlc-start "Test feature"`

**Related Commands**:
- `/set-client` - Activate a client profile
- `/sdlc-start` - Run workflow with active client

**See Also**:
- `clients/_base/README.md` - Comprehensive onboarding guide
- `clients/demo-client/` - Example client profile
- `clients/_base/profile.yml` - Full template with all options
