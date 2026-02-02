# SDLC Phases Reference

Complete reference for all 8 phases of the SDLC Agêntico workflow.

## Overview

The SDLC Agêntico consists of 8 sequential phases, each with specific agents, deliverables, and quality gates.

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8
  ↓         ↓         ↓         ↓         ↓         ↓         ↓         ↓         ↓
 Gate     Gate      Gate      Gate      Gate      Gate      Gate      Gate    Continuous
```

## Phase Definitions

### Phase 0: Preparação e Alinhamento (Intake)

**Purpose**: Validate project readiness and compliance requirements.

**Agents**:
- `intake-analyst`: Analyzes incoming requests, classifies work type
- `compliance-guardian`: Validates regulatory and compliance requirements

**Deliverables**:
- Project classification (Level 0-3)
- Compliance checklist
- Initial risk assessment
- Stakeholder identification

**Quality Gate**: Compliance readiness validated

---

### Phase 1: Descoberta e Pesquisa (Discovery)

**Purpose**: Gather domain knowledge and establish knowledge base.

**Agents**:
- `domain-researcher`: Researches domain concepts, patterns, best practices
- `doc-crawler`: Extracts and indexes technical documentation
- `rag-curator`: Organizes knowledge in RAG corpus

**Deliverables**:
- Domain research report
- Technical documentation indexed
- RAG corpus populated
- Reference architecture patterns identified

**Quality Gate**: Knowledge registered, RAG ready for consumption

---

### Phase 2: Produto e Requisitos (Requirements)

**Purpose**: Define product vision and testable requirements.

**Agents**:
- `product-owner`: Defines product vision, prioritizes features
- `requirements-analyst`: Writes user stories with acceptance criteria
- `ux-writer`: Defines UI copy, states, and user flows

**Deliverables**:
- Product vision document
- User stories with acceptance criteria
- Non-functional requirements (NFRs)
- UI/UX specifications
- Success metrics defined

**Quality Gate**: Requirements testable, NFRs defined, no ambiguity

---

### Phase 3: Arquitetura e Design (Architecture)

**Purpose**: Design system architecture and make technical decisions.

**Agents**:
- `system-architect`: Defines high-level architecture, technology choices
- `adr-author`: Documents Architecture Decision Records
- `data-architect`: Models data, defines API contracts
- `threat-modeler`: Performs STRIDE threat modeling
- `api-designer`: Designs API contracts (OpenAPI, GraphQL)

**Deliverables**:
- Architecture diagrams (C4 model)
- Architecture Decision Records (ADRs)
- Data models and API contracts
- Threat model (STRIDE analysis)
- Technology stack selected

**Quality Gate**: ADRs complete, threats mitigated (HIGH/CRITICAL), architecture reviewed

---

### Phase 4: Planejamento de Entrega (Planning)

**Purpose**: Break down work into executable tasks with estimates.

**Agents**:
- `delivery-planner`: Creates sprint plan, identifies dependencies
- `estimation-engine`: Estimates effort using historical data

**Deliverables**:
- Sprint plan (tasks, stories)
- Effort estimates (story points, hours)
- Dependency graph
- Milestone definitions
- Risk mitigation plan

**Quality Gate**: Plan executable, dependencies resolved, realistic timeline

---

### Phase 5: Implementação (Implementation)

**Purpose**: Write code, tests, and documentation.

**Agents**:
- `code-author`: Implements features following specs
- `code-reviewer`: Reviews code for quality, security
- `test-author`: Writes unit, integration, E2E tests
- `refactoring-advisor`: Suggests code improvements
- `iac-engineer`: Generates Infrastructure as Code (Terraform, Bicep)

**Deliverables**:
- Source code (feature complete)
- Unit tests (>80% coverage)
- Integration tests
- Infrastructure as Code
- Technical documentation

**Quality Gate**: Build passing, coverage minimum, code reviewed, no secrets committed

---

### Phase 6: Qualidade, Segurança e Conformidade (Quality)

**Purpose**: Validate quality, security, and performance.

**Agents**:
- `qa-analyst`: Executes test plan, validates acceptance criteria
- `security-scanner`: Runs SAST/SCA scans (Snyk, Trivy)
- `performance-analyst`: Load testing, latency analysis

**Deliverables**:
- Test execution report
- Security scan results (no CRITICAL/HIGH vulnerabilities)
- Performance test results
- Quality metrics (code coverage, defect density)
- Compliance validation

**Quality Gate**: Quality validated, no security blockers, performance acceptable

---

### Phase 7: Release e Deploy (Release)

**Purpose**: Deploy to production safely with rollback plan.

**Agents**:
- `release-manager`: Coordinates release process
- `cicd-engineer`: Maintains CI/CD pipelines
- `change-manager`: Manages change communication, approvals
- `doc-generator`: Generates release notes, API docs

**Deliverables**:
- Release notes
- Deployment plan
- Rollback plan
- Change approvals
- Production deployment
- GitHub Wiki sync
- GitHub Milestone closed

**Quality Gate**: Deploy successful, smoke tests pass, rollback validated

---

### Phase 8: Operação e Aprendizagem (Operations)

**Purpose**: Monitor production, respond to incidents, extract learnings.

**Agents**:
- `observability-engineer`: Configures dashboards, alerts (Loki, Grafana)
- `incident-commander`: Coordinates incident response
- `rca-analyst`: Performs root cause analysis
- `metrics-analyst`: Tracks DORA metrics, SPACE metrics
- `memory-curator`: Extracts learnings, updates RAG corpus

**Deliverables**:
- Observability dashboards
- Incident reports
- Root Cause Analysis (RCA)
- Post-mortem documents
- Learnings extracted to RAG
- DORA metrics tracked

**Quality Gate**: No gate (continuous operation)

---

## Phase Transitions

### Advancing Phases

1. Current phase work complete
2. Gate evaluation executed (`gate-evaluator` skill)
3. All gate criteria met
4. Adversarial audit passed (if enabled for phase)
5. Phase commit executed (artifacts committed)
6. State updated (`memory-manager`)

### Blocking Conditions

Phase advance blocked if:
- Gate criteria not met
- Security vulnerabilities (CRITICAL/HIGH)
- Compliance issues
- Missing required artifacts
- Adversarial audit failure

### Rollback

If phase advancement causes issues:
- Revert to previous phase state
- Re-evaluate gate with fixes
- Document rollback reason

---

## Client-Specific Phase Behavior

When multi-client mode enabled (v3.0.0):
- Each client may have custom phase definitions
- Client-specific gates in `.sdlc_clients/{client}/gates/`
- Phase agents resolved per client profile

See: `coordination.md` for client resolution logic.

---

**Version**: 3.0.0
**Last Updated**: 2026-02-02
