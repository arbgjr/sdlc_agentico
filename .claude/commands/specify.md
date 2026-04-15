---
name: specify
description: |
  Creates a Spec-Driven Development specification for a new feature.
  Produces .specify/specs/<slug>/spec.md with acceptance criteria,
  anchored in the project Constitution.

  Examples:
  - <example>
    user: "/specify implement PIX checkout"
    assistant: "Vou criar .specify/specs/pix-checkout/spec.md com a spec completa"
    </example>
---

# Create a Feature Specification

## Invariants

1. A spec MUST exist before any code is written for the feature (Principle VIII).
2. Every spec carries `status: draft | approved | superseded` in frontmatter.
3. `/specify` NEVER writes code. It produces a spec. Period.

## Input

Free-form feature description after the command:
- `/specify PIX checkout`
- `/specify add multi-tenant support to orders service`
- `/specify dark mode toggle for dashboard`

## Steps

1. **Load the Constitution**: run `/constitution` mentally and quote the
   principles that apply to this feature (especially II, III, VIII).

2. **Derive a slug**: kebab-case, max 40 chars. Examples:
   - "PIX checkout" → `pix-checkout`
   - "add multi-tenant support" → `multi-tenant-support`

3. **Invoke `product-owner`** to scope the feature:
   - Value hypothesis
   - Target users / stakeholders
   - Success metrics (quantified)
   - Out of scope (explicit)

4. **Invoke `requirements-analyst`** to produce:
   - User stories (Given/When/Then format)
   - Acceptance criteria — every `then` must be testable
   - Non-functional requirements (latency, availability, security, LGPD)

5. **Invoke `threat-modeler`** if the feature touches auth/PII/payments:
   - STRIDE quick-pass
   - Record threats in `.specify/specs/<slug>/threats-preview.md`
   - Flag this feature for full threat model at Phase 3

6. **Write** `.specify/specs/<slug>/spec.md` using the template at
   `.agentic_sdlc/templates/spec-template.md`, with frontmatter:
   ```yaml
   ---
   spec_id: <slug>
   status: draft
   created_at: <ISO8601>
   constitution_version: "1.0.0"
   applicable_principles: [II, III, VIII]
   ---
   ```

7. **Invoke `/auto-branch`** to create the feature branch:
   `feature/<slug>` from current base.

## Output

- File: `.specify/specs/<slug>/spec.md` (status: draft)
- Branch: `feature/<slug>` (if auto_branch enabled)
- Report:
  ```yaml
  spec_created:
    path: .specify/specs/pix-checkout/spec.md
    slug: pix-checkout
    status: draft
    next_command: /clarify pix-checkout
    principles_applied: [II, III, VIII]
  ```

## Gate interaction

- `phase-2-to-3` blocks transition to Architecture until this spec exists AND
  `status: approved`. To approve, run `/analyze <slug>` which validates
  completeness and flips status to `ready-for-approval`.

## Do NOT

- Do NOT invoke `system-architect` here. Architecture is Phase 3.
- Do NOT write implementation details (classes, SQL, API routes). That's
  `/plan`. Confusing the two is a bad smell.
- Do NOT mark `status: approved` without going through `/analyze`.
