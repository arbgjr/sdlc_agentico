# Complexity Levels Reference

Adaptive workflow scaling based on task complexity (BMAD-inspired).

## Overview

The orchestrator automatically detects task complexity and adjusts the SDLC workflow accordingly. This ensures lightweight tasks don't go through unnecessary phases while critical projects get full rigor.

## Complexity Scale (0-3)

### Level 0: Quick Flow (Bug Fixes, Hotfixes)

**Trigger**:
- Bug fix
- Typo correction
- Simple configuration change
- Hotfix in production

**Workflow**:
```yaml
phases_executed: [5, 6]  # Implementation + Quality only
agents: [code-author, test-author, code-reviewer]
gates: [build_passing, tests_passing, code_reviewed]
estimated_time: "5-15 minutes"
```

**Commands**:
- `/quick-fix "Description of bug"`

**Example**:
```
User: "Fix null pointer exception in payment service"
→ Level 0 detected
→ Skip phases 0-4
→ Jump to Phase 5 (code fix)
→ Phase 6 (test + review)
→ Release
```

---

### Level 1: Feature (New Feature in Existing Service)

**Trigger**:
- New feature in existing service
- Enhancement to existing functionality
- Simple API endpoint addition

**Workflow**:
```yaml
phases_executed: [2, 5, 6]  # Requirements + Implementation + Quality
agents:
  - requirements-analyst
  - code-author
  - test-author
  - code-reviewer
  - qa-analyst
gates: [requirements_defined, build_passing, tests_passing, quality_validated]
estimated_time: "15-30 minutes"
```

**Commands**:
- `/new-feature "Feature name"`

**Example**:
```
User: "Add pagination to user list endpoint"
→ Level 1 detected
→ Skip phases 0, 1, 3, 4
→ Phase 2: requirements-analyst defines pagination spec
→ Phase 5: code-author implements
→ Phase 6: qa-analyst validates
→ Release
```

---

### Level 2: Full SDLC (New Service, Product, Integration)

**Trigger**:
- New product or service
- Major system integration
- New architecture component
- Multi-team project

**Workflow**:
```yaml
phases_executed: [0, 1, 2, 3, 4, 5, 6, 7]  # All phases
agents: "ALL"
gates: "ALL"
skip_phases: []
estimated_time: "30 minutes to several hours"
```

**Commands**:
- `/sdlc-start "Project description"`

**Example**:
```
User: "Build payment processing service with Stripe integration"
→ Level 2 detected
→ Execute all phases:
   Phase 0: intake-analyst classifies, compliance-guardian checks regulations
   Phase 1: domain-researcher studies Stripe, doc-crawler indexes docs
   Phase 2: product-owner defines MVP, requirements-analyst writes stories
   Phase 3: system-architect designs, threat-modeler runs STRIDE
   Phase 4: delivery-planner creates sprint plan
   Phase 5: code-author implements, iac-engineer generates Terraform
   Phase 6: qa-analyst validates, security-scanner runs SAST
   Phase 7: release-manager coordinates deploy
   Phase 8: observability-engineer sets up monitoring
```

---

### Level 3: Enterprise (Compliance-Critical, Multi-Team)

**Trigger**:
- Regulatory compliance required (LGPD, GDPR, SOC2)
- Multi-team coordination
- Production-critical system
- Financial transactions (> $50k impact)
- Security-sensitive (PII, authentication)

**Workflow**:
```yaml
phases_executed: [0, 1, 2, 3, 4, 5, 6, 7, 8]  # All phases + continuous ops
agents: "ALL + human approval at every gate"
gates: "ALL + compliance_gate + security_gate + architecture_review"
extra_requirements:
  - Human approval before phase advance
  - Legal review for compliance
  - Security team sign-off
  - Architecture review board
skip_phases: []
estimated_time: "variable (days to weeks)"
```

**Human-in-the-Loop**:
- Every gate requires explicit human approval
- Compliance decisions escalated
- Security vulnerabilities reviewed by security team
- Architecture changes reviewed by architects

**Example**:
```
User: "Implement LGPD-compliant data retention system"
→ Level 3 detected
→ Orchestrator escalates: "This requires compliance approval"
→ Execute all phases with gates:
   Phase 0: compliance-guardian validates LGPD requirements → Human approves
   Phase 1: domain-researcher studies LGPD precedents → Human approves
   Phase 2: requirements-analyst defines data retention rules → Legal reviews
   Phase 3: system-architect designs encryption → Security reviews
   (... human approval at each gate ...)
```

---

## Automatic Level Detection

The orchestrator uses heuristics to detect complexity:

### Level 0 Indicators
- Keywords: "fix", "bug", "typo", "hotfix", "patch"
- Affects 1 file
- No architecture changes
- No new dependencies

### Level 1 Indicators
- Keywords: "feature", "add", "enhancement", "improve"
- Affects 1 service
- No new services/databases
- No architecture changes

### Level 2 Indicators
- Keywords: "new service", "integration", "architecture"
- Creates new service/database
- Affects multiple services
- Requires ADRs

### Level 3 Indicators
- Keywords: "compliance", "LGPD", "GDPR", "financial", "PII", "authentication"
- Budget > $50k
- Multi-team coordination
- Production-critical
- Security-sensitive

---

## Overriding Detection

User can force a specific level:

```bash
# Force Level 0 (quick flow)
/quick-fix "Fix bug in auth service"

# Force Level 1 (feature)
/new-feature "Add pagination"

# Force Level 2 (full SDLC)
/sdlc-start "New API gateway" --level 2

# Force Level 3 (enterprise)
/sdlc-start "LGPD data retention" --level 3 --compliance
```

---

## Phase Skipping Logic

| Level | Phases Executed | Phases Skipped | Reason |
|-------|----------------|----------------|--------|
| 0     | 5, 6           | 0, 1, 2, 3, 4, 7, 8 | Simple fix, no design needed |
| 1     | 2, 5, 6        | 0, 1, 3, 4, 7, 8 | Feature in existing service, no architecture |
| 2     | 0-7            | 8 (optional)   | Full SDLC, all phases needed |
| 3     | 0-8            | None           | Enterprise, full rigor + ops |

---

## Escalation Triggers

Regardless of detected level, escalate to higher level if:

**Automatic Escalation to Level 2**:
- New ADR created (architecture decision)
- New service/database introduced
- Integration with external system

**Automatic Escalation to Level 3**:
- PII data handled
- Financial transactions (> $50k)
- Security vulnerability (CVSS >= 7.0)
- Compliance keyword detected (LGPD, GDPR, SOC2, HIPAA)
- Multi-team coordination required

---

## Parallel vs Sequential Execution

### Sequential (Default)
- Phases execute one at a time
- Each gate blocks until passed
- Safer for complex projects

### Parallel (Level 2/3 with parallel-workers enabled)
- Phase 5 tasks run in parallel (git worktrees)
- Up to 3 workers concurrently
- 2.5x speedup for independent tasks

**Decision Logic**:
```yaml
use_parallel_if:
  - level >= 2
  - phase == 5
  - tasks >= 3
  - tasks_are_independent: true
  - parallel_workers_enabled: true
```

See: `integrations.md` for parallel worker details.

---

**Version**: 3.0.3
**Last Updated**: 2026-02-02
