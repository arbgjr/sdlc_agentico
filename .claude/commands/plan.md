---
name: plan
description: |
  Produces the technical plan for a spec that is already approved.
  Calls system-architect + data-architect + adr-author.
  Creates .specify/specs/<slug>/plan.md.

  Examples:
  - <example>
    user: "/plan pix-checkout"
    assistant: "Vou gerar o plano técnico com ADRs para pix-checkout"
    </example>
---

# Create a Technical Plan

## Invariants

1. `/plan <slug>` REQUIRES `.specify/specs/<slug>/spec.md` with
   `status: approved`. If missing, refuse with a clear error pointing to
   `/specify` and `/analyze`.
2. The plan does NOT touch application code. It produces design docs only.
3. Every significant choice (DB, messaging, protocol, auth) produces an
   ADR under `.project/corpus/nodes/decisions/ADR-XXX-...yml`.

## Steps

1. **Load Constitution + spec**: read
   `.specify/memory/constitution.md` and `.specify/specs/<slug>/spec.md`.
   Abort if spec status != approved.

2. **Invoke `system-architect`** to produce the plan skeleton:
   - Components touched (existing + new)
   - Integration boundaries
   - Technology choices (with explicit trade-off table)
   - NFR approach (how each NFR is satisfied)
   - Rollout strategy

3. **Invoke `data-architect`** for:
   - Data model deltas (entities, relationships, indexes)
   - API contracts (OpenAPI 3.1 for sync, AsyncAPI for events)
   - Event schemas
   - Migration plan if schema changes

4. **Invoke `adr-author`** to record decisions that satisfy Principle V
   (Decisions are ADRs). One ADR per decision, referenced from the plan.

5. **Invoke `threat-modeler`** for full STRIDE pass. Record in
   `.specify/specs/<slug>/threat-model.yml`.

6. **Invoke `tradeoff-challenger`** on the technology choices. Any choice
   without at least one explicit trade-off documented is a bad smell —
   reject and loop.

7. **Write** `.specify/specs/<slug>/plan.md` with frontmatter:
   ```yaml
   ---
   plan_id: <slug>-technical-plan
   spec_ref: <slug>
   status: draft
   adr_refs: [ADR-NNN, ADR-NNN+1]
   data_model: data-model.md
   api_contracts: api-contracts.yml
   threat_model: threat-model.yml
   ---
   ```

## Output

- `.specify/specs/<slug>/plan.md`
- `.specify/specs/<slug>/data-model.md`
- `.specify/specs/<slug>/api-contracts.yml` (OpenAPI)
- `.specify/specs/<slug>/threat-model.yml`
- `.project/corpus/nodes/decisions/ADR-NNN-*.yml` (one per decision)

## Gate interaction

- `phase-3-to-4` requires all of: plan.md, data-model.md, threat-model.yml,
  at least 1 ADR. Missing any → reject.

## Do NOT

- Do NOT skip the threat-modeler for features touching auth/PII/payments
  (auto-escalation triggers in `sdlc.security_by_design`).
- Do NOT pick a new technology without an ADR + trade-off row — that is
  exactly the pattern `tradeoff-challenger` catches.
