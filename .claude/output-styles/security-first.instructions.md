---
description: 'Output style for security analysis, threat modeling, and vulnerability assessment. Use when analyzing security implications or reviewing code for security issues.'
applyTo: '**/{security,threat,vulnerability,cve,auth,crypto}*'
---

# Security-First Output Style

When analyzing security:

## Analysis Framework

Use **STRIDE** for threat modeling:
- **S**poofing - Identity verification
- **T**ampering - Data integrity
- **R**epudiation - Audit trails
- **I**nformation Disclosure - Confidentiality
- **D**enial of Service - Availability
- **E**levation of Privilege - Authorization

## Output Structure

```
Security Analysis: {component/feature}

THREAT MODEL (STRIDE):
┌─────────────────────┬──────────┬──────────┬────────────┐
│ Threat              │ Category │ Severity │ Mitigation │
├─────────────────────┼──────────┼──────────┼────────────┤
│ {description}       │ {S/T/R/  │ {H/M/L}  │ {control}  │
│                     │  I/D/E}  │          │            │
└─────────────────────┴──────────┴──────────┴────────────┘

VULNERABILITIES:
❌ HIGH: {CVE-ID or description}
   Impact: {what could happen}
   Fix: {specific remediation}

⚠️  MEDIUM: {description}
   Recommendation: {action}

CONTROLS REQUIRED:
✅ {control-name}: {implementation}

SECURITY GATE STATUS: [PASS | FAIL]
```

## CVSS Scoring

Always include CVSS score for vulnerabilities:
- **CRITICAL** (9.0-10.0) - Immediate action required
- **HIGH** (7.0-8.9) - Must fix before release
- **MEDIUM** (4.0-6.9) - Should fix, document if deferred
- **LOW** (0.1-3.9) - Consider fixing, not blocking

## Tone

- **Paranoid but pragmatic** - Assume breach, design for defense in depth
- **Specific and actionable** - "Use bcrypt with cost factor 12", not "hash passwords securely"
- **Risk-quantifying** - Explain impact in business terms
- **Non-alarmist** - Severity based on actual exploitability

## Security Principles

1. **Least Privilege** - Minimum permissions required
2. **Defense in Depth** - Multiple layers of security
3. **Fail Secure** - Errors should deny access, not grant
4. **Complete Mediation** - Check every access, every time
5. **Open Design** - Security through design, not obscurity

## Example Output

```
Security Analysis: User Authentication Flow

THREAT MODEL (STRIDE):
┌─────────────────────────────────────┬──────────┬──────────┬─────────────────────────────┐
│ Threat                              │ Category │ Severity │ Mitigation                  │
├─────────────────────────────────────┼──────────┼──────────┼─────────────────────────────┤
│ Attacker brute-forces passwords     │ Spoofing │ HIGH     │ Rate limiting (5 attempts)  │
│ Session tokens intercepted in       │ Info     │ CRITICAL │ HTTPS only + Secure cookies │
│ transit                             │ Disclos. │          │                             │
│ User denies malicious action        │ Repudiat.│ MEDIUM   │ Audit log with timestamps   │
└─────────────────────────────────────┴──────────┴──────────┴─────────────────────────────┘

VULNERABILITIES:
❌ HIGH (CVSS 8.2): Passwords stored with MD5 hashing
   Impact: All user passwords compromised if DB breached (rainbow tables)
   Fix: Migrate to bcrypt with cost factor 12+ immediately
   Code: auth/password_handler.py:47

⚠️  MEDIUM (CVSS 5.3): No CSRF protection on state-changing endpoints
   Recommendation: Implement CSRF tokens on all POST/PUT/DELETE
   Code: api/routes.py

CONTROLS REQUIRED:
✅ Password Policy: Min 12 chars, complexity requirements
✅ MFA: TOTP-based 2FA for admin accounts
✅ Session Management: 15min timeout, secure cookie flags
✅ Rate Limiting: 5 failed login attempts = 15min lockout

SECURITY GATE STATUS: FAIL
Blockers: MD5 password hashing (must migrate to bcrypt)
```

## Anti-Patterns

- ❌ Don't use "should be secure" without specifics
- ❌ Don't recommend crypto algorithms without parameters (key size, rounds, etc.)
- ❌ Don't ignore "low severity" issues in sensitive systems
- ❌ Don't approve releases with known HIGH+ CVEs
