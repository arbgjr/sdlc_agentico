---
name: clarify
description: |
  Interrogates an existing spec to eliminate ambiguity. Invokes
  requirements-interrogator to surface missing numbers, limits, NFRs,
  and edge cases. Loops until the spec is unambiguous.

  Examples:
  - <example>
    user: "/clarify pix-checkout"
    assistant: "Vou questionar o spec para eliminar ambiguidades"
    </example>
---

# Clarify a Specification

## Purpose

Specs written too quickly have ambiguities that surface as rework in
Phase 3 or Phase 6 — much more expensive. `/clarify` runs the spec
through adversarial questioning BEFORE architecture to kill ambiguity
early.

## Steps

1. **Read** `.specify/specs/<slug>/spec.md`.

2. **Invoke `requirements-interrogator`** with the spec contents. The
   agent produces a list of questions the spec does not answer:
   - Missing numbers ("latency should be low" → what p99?)
   - Missing limits ("many users" → how many, when does it break?)
   - Missing NFRs (availability, durability, compliance)
   - Missing error behavior ("if payment fails" → retry? user message?)
   - Missing edge cases (empty lists, concurrent updates, clock skew)

3. **Present questions** to the human as a numbered list. Wait for answers.

4. **Update** the spec with the answers, incrementing a `clarify_round`
   counter in the frontmatter.

5. **Re-invoke** `requirements-interrogator` on the updated spec. If it
   finds new questions, repeat. If it returns zero questions, the spec
   is unambiguous — proceed.

6. **Update frontmatter**:
   ```yaml
   clarify_rounds_completed: 3
   last_clarified_at: <ISO8601>
   ambiguity_count: 0
   ```

## Stopping condition

Zero questions returned in a round, OR 5 rounds reached (escalate to human
if round 5 still produces questions — the spec may be fundamentally ill-defined).

## Do NOT

- Do NOT answer the questions yourself to get unstuck. The point is to
  force the human / product-owner to pin down the ambiguity.
- Do NOT let the interrogator ask philosophical questions. It must produce
  actionable, testable questions.
