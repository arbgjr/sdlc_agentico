# Security and Escalation Reference

Critical rules, escalation triggers, and security workflows.

## Overview

Security is integrated into every phase of the SDLC. The orchestrator enforces security gates, detects escalation triggers, and manages human-in-the-loop decisions.

---

## Critical Rules

### 1. Never Skip Quality Gates

- Each phase transition MUST pass through the corresponding gate
- Use `gate-evaluator` skill for validation
- Gates cannot be bypassed (except with explicit override and documentation)

**Enforcement**:
- Pre-commit hooks block commits without gate approval
- CI/CD pipelines fail if gates not passed
- Orchestrator logs all gate bypass attempts

---

### 2. Always Persist Decisions

- Before transitioning phases, save to ``
- Architecture decisions → ADRs (Architecture Decision Records)
- Business decisions → ODRs (Organizational Decision Records)
- Technical decisions → Decision log in RAG corpus

**Traceability**:
- Each decision linked to:
  - Phase where made
  - Agents involved
  - Alternatives considered
  - Rationale
  - Consequences (expected + actual)

---

### 3. Escalate to Humans When...

**Automatic Escalation Triggers**:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| **Budget** | > R$ 50,000 | Require CFO/budget owner approval |
| **Security** | CVSS >= 7.0 | Escalate to security team |
| **Architecture** | Affects >= 3 services | Architecture review board |
| **Production Deploy** | Any prod change | Require change manager approval |
| **Compliance** | Any LGPD/GDPR/SOC2 impact | Legal/compliance review |
| **PII Data** | New PII fields | Data protection officer approval |
| **Authentication** | Auth/authz changes | Security team review |
| **Cryptography** | New crypto implementation | Security team + external audit |
| **External API** | New external integration | Security + architecture review |
| **Database Schema** | Breaking schema changes | Database admin + stakeholders |

---

### 4. Maintain Audit Trail

- Log WHO decided WHAT and WHEN
- Link decisions to generated artifacts
- Preserve decision context for future reference
- Enable rollback with understanding of impact

**Audit Log Format**:
```yaml
decision_id: DEC-2026-02-023
timestamp: "2026-02-02T18:45:23Z"
phase: 3
agent: "system-architect"
human_approver: "john.doe@company.com"
decision: "Use Kafka for event streaming"
alternatives:
  - "RabbitMQ"
  - "AWS SQS"
rationale: "Kafka provides better throughput (100k msg/s) and event replay"
artifacts:
  - ".agentic_sdlc/architecture/adr-001.yml"
approval_timestamp: "2026-02-02T19:15:00Z"
```

---

### 5. Follow the Playbook

- Consult `playbook.md` for principles and standards
- Violations must be:
  - Documented as exceptions
  - Justified with rationale
  - Recorded as tech debt
  - Scheduled for remediation

**Playbook Violation Handling**:
```python
if detect_playbook_violation(code, playbook):
    severity = classify_violation(code, playbook)

    if severity == "CRITICAL":
        block_commit()
        escalate_to_human()
    elif severity == "HIGH":
        create_tech_debt_issue()
        warn_developer()
    else:
        log_violation()
```

---

## Escalation Workflow

### Detection

Orchestrator automatically detects escalation conditions:

```python
def should_escalate(context):
    """Check if decision requires human approval."""

    # Budget threshold
    if context.get("estimated_cost", 0) > 50000:
        return ("budget", ["CFO", "budget-owner"])

    # Security severity
    cvss = context.get("security", {}).get("cvss_score", 0)
    if cvss >= 7.0:
        return ("security", ["security-team"])

    # Architecture impact
    affected_services = len(context.get("affected_services", []))
    if affected_services >= 3:
        return ("architecture", ["architecture-review-board"])

    # Production deployment
    if context.get("target_env") == "production":
        return ("deployment", ["change-manager", "tech-lead"])

    # Compliance keywords
    compliance_keywords = ["LGPD", "GDPR", "PII", "SOC2", "HIPAA"]
    if any(kw in context.get("description", "") for kw in compliance_keywords):
        return ("compliance", ["legal", "compliance-officer"])

    return None  # No escalation needed
```

---

### Escalation Process

1. **Detect Trigger**
   - Orchestrator identifies escalation condition
   - Determines required approvers

2. **Create Approval Request**
   ```yaml
   escalation_id: ESC-2026-02-023
   timestamp: "2026-02-02T18:45:23Z"
   type: "security"
   severity: "HIGH"
   trigger: "CVSS 8.2 vulnerability in authentication"
   description: |
     Vulnerability CVE-2026-12345 detected in OAuth library (v2.1.0).
     CVSS Score: 8.2 (HIGH)
     Impact: Authentication bypass possible with crafted JWT
   required_approvers:
     - security-team@company.com
     - tech-lead@company.com
   decision_deadline: "2026-02-03T18:45:23Z"  # 24h
   ```

3. **Notify Approvers**
   - Email/Slack notification
   - Include context, impact, alternatives
   - Set deadline for decision

4. **Block Phase Advance**
   - Orchestrator pauses workflow
   - Logs blocked state
   - Tracks approval requests

5. **Collect Approvals**
   - Approvers review and respond
   - Record approval/rejection
   - Capture rationale

6. **Resume or Rollback**
   ```python
   if all_approvers_approved(escalation_id):
       resume_workflow(context)
       log_approval(escalation_id)
   else:
       rollback_changes(context)
       notify_rejection(escalation_id)
   ```

---

## Security Gate Integration

### Phase-Specific Security Checks

**Phase 0 (Intake)**:
- Compliance requirements identified
- Data classification performed
- Regulatory constraints documented

**Phase 2 (Requirements)**:
- Security requirements defined
- Authentication/authorization specified
- Data protection requirements documented

**Phase 3 (Architecture)**:
- **Threat modeling (STRIDE) REQUIRED**
- HIGH/CRITICAL threats mitigated
- Security controls documented in ADRs
- Secrets management strategy defined

**Phase 5 (Implementation)**:
- No hardcoded secrets in code
- Input validation on all user inputs
- SQL injection prevention
- XSS prevention
- CSRF tokens implemented

**Phase 6 (Quality)**:
- **SAST scan executed** (Snyk, Trivy, or similar)
- **SCA scan executed** (dependency vulnerabilities)
- **No CRITICAL/HIGH vulnerabilities** blocking release
- Security test cases passed

**Phase 7 (Release)**:
- Security checklist complete
- Secrets rotated if compromised
- Security monitoring enabled
- Incident response plan documented

---

## Security Checklist (Pre-Release)

Before releasing to production:

- [ ] **Threat model complete** (STRIDE analysis)
- [ ] **HIGH/CRITICAL threats mitigated**
- [ ] **SAST scan passed** (no CRITICAL/HIGH issues)
- [ ] **SCA scan passed** (no vulnerable dependencies)
- [ ] **Secrets in vault** (not in code/config)
- [ ] **Authentication tested** (positive + negative cases)
- [ ] **Authorization enforced** (least privilege principle)
- [ ] **Input validation implemented** (all user inputs)
- [ ] **SQL injection prevented** (parameterized queries)
- [ ] **XSS prevented** (output encoding)
- [ ] **CSRF protection** (tokens on state-changing requests)
- [ ] **HTTPS enforced** (no plaintext transmission)
- [ ] **Security headers set** (HSTS, CSP, X-Frame-Options)
- [ ] **Rate limiting implemented** (API endpoints)
- [ ] **Logging enabled** (security events, failed auth)
- [ ] **Incident response plan** (documented + tested)

---

## Secrets Management

### Rules

1. **NEVER commit secrets to Git**
   - No API keys, passwords, tokens in code
   - No secrets in PR descriptions or commit messages
   - No secrets in README or documentation

2. **Use environment variables or secret managers**
   - Azure Key Vault
   - AWS Secrets Manager
   - HashiCorp Vault
   - GitHub Secrets (for CI/CD)

3. **Rotate secrets regularly**
   - Quarterly for non-critical
   - Immediately if compromised
   - After team member departure

4. **Pre-commit hooks detect secrets**
   - git-secrets
   - truffleHog
   - gitleaks

### Secret Leak Response

If secret leaked to Git:

1. **REVOKE/ROTATE IMMEDIATELY**
2. **REMOVE FROM GIT HISTORY** (BFG Repo-Cleaner)
3. **CLEAN REMOTE REPOSITORY**
4. **DOCUMENT INCIDENT**
5. **NOTIFY SECURITY TEAM**
6. **REVIEW ACCESS LOGS** (was secret used?)

---

## Compliance Integration

### LGPD/GDPR Requirements

When PII (Personally Identifiable Information) is involved:

1. **Data Classification**
   - Identify all PII fields
   - Document data retention policy
   - Define deletion procedures

2. **User Rights Implementation**
   - Right to access (export data)
   - Right to deletion (GDPR Article 17)
   - Right to correction
   - Right to data portability

3. **Consent Management**
   - Explicit consent collection
   - Consent withdrawal mechanism
   - Consent audit trail

4. **Security Controls**
   - Encryption at rest (AES-256)
   - Encryption in transit (TLS 1.3)
   - Access logging
   - Regular security audits

---

## Incident Response Integration

### Detection

Orchestrator monitors for security incidents:
- Failed authentication attempts (rate)
- Unauthorized access attempts
- Suspicious patterns (SIEM integration)
- Security scan findings

### Response Workflow

1. **Detect Incident**
   ```python
   if security_incident_detected(event):
       severity = classify_incident(event)
       incident_id = create_incident(severity, event)
   ```

2. **Invoke Incident Commander**
   - `incident-commander` agent coordinates response
   - Create incident channel (Slack/Teams)
   - Notify on-call engineer
   - Start incident timeline

3. **Contain and Mitigate**
   - Isolate affected systems
   - Rotate compromised credentials
   - Block malicious IPs
   - Patch vulnerabilities

4. **Post-Incident Analysis**
   - `rca-analyst` performs root cause analysis
   - Document timeline and decisions
   - Extract learnings
   - Update playbook

5. **Follow-Up**
   - Implement preventive measures
   - Update security controls
   - Train team on lessons learned

---

## Security Metrics

Track security posture:

```yaml
security_metrics:
  vulnerability_response_time:
    critical: "< 24h"
    high: "< 72h"
    medium: "< 7 days"

  scan_coverage:
    sast: "100% of releases"
    sca: "100% of dependencies"
    dast: "100% of public APIs"

  secrets_management:
    secrets_in_vault: "100%"
    secrets_rotated_quarterly: "100%"

  incident_response:
    mean_time_to_detect: "< 15 min"
    mean_time_to_respond: "< 30 min"
    mean_time_to_recover: "< 4 hours"
```

---

**Version**: 3.0.0
**Last Updated**: 2026-02-02
