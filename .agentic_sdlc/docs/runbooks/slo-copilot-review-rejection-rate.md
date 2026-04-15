# Runbook — copilot_review_rejection_rate

**SLO target**: first-pass review rejection rate ≤ 20%
**Owner**: copilot-cloud-agent
**Priority**: P2 — sustained breach means upstream (Planning Phase) is underspecified

## Symptom

- Gauge "Copilot review rejection rate" crosses 20%
- review_relay posts CRITICAL/HIGH findings on more than 1 in 5 PRs
- Copilot retry count per task is climbing

## Triage (first 5 minutes)

1. **Bucket findings by rule**:
   ```bash
   grep -rE 'review_relay|severity' .project/reports/*.yml \
     | jq 'group_by(.rule) | map({rule: .[0].rule, count: length})' 2>/dev/null
   ```
2. **Identify the loudest rule** — one rule typically accounts for >50%
   of rejections in a burn window.
3. **Correlate to spec slugs** — is the burn concentrated in a single
   feature or spread across all features?

## Common causes (ranked by frequency)

1. **Story-context omits a repeated constraint** — e.g. stories don't
   mention "no hardcoded secrets", so Copilot ships env-defaulted config
   strings that look like credentials, and the secret scanner flags them.
2. **Pattern library drift** — a new pattern was added to
   `.agentic_sdlc/corpus/patterns/` but the story-context template
   doesn't link it, so Copilot doesn't know about it.
3. **Tool false-positive surge** — bandit/ruff version bump introduced
   new rules that fire on legitimate code. Review relay is correct;
   the signal is noisy.
4. **Copilot regression in the cloud agent** — rare, but possible. Tell
   by: same input + same PR produces different findings across time.

## Mitigation

| Cause | Action |
|---|---|
| Story-context gap | Edit `.agentic_sdlc/templates/story-context.md` to surface the missing constraint; re-run `/tasks <slug>` for in-flight specs. |
| Pattern drift | Author the pattern link into story-context; if pattern is truly new, propose a Constitution amendment via `/constitution amend`. |
| Tool noise | Pin bandit/ruff versions in CI; tag noisy rules as INFO instead of HIGH until reviewed. |
| Copilot regression | Temporarily flip `sdlc.parallelization.default_strategy` to `parallel_workers`; file issue with GitHub. |

## Rollback

No direct rollback; rejection rate improves by the next PR, not by
undoing a prior one. If the root cause is a bad template change, revert
the template commit.

## Escalation

- Rejection rate > 40% sustained 24h → P1: something fundamental is
  wrong with the Planning Phase output. Stop Dev Cycle, run adversarial
  validator on the most recent Plan.
- Same rule rejected 10+ PRs → automate: promote the rule into a
  pre-commit hook or a `/tasks` template check, so Copilot never
  produces violating code in the first place.

## Post-incident RCA

Mandatory:

1. Which rule drove the rejections.
2. Whether the rule is legitimate (keep and teach) or noise (suppress
   and document in ADR).
3. Whether Planning Phase would have caught this — if yes, patch the
   Planning stage. If no, the rule is purely Dev Cycle concern.

## Teach the framework

Rejection rules that fire > 10 times without rule tuning must either:
- migrate into the story-context template (preventive), or
- be added to the adversarial-validator (caught earlier in Plan review),
- or be suppressed in bandit/ruff config with ADR justification.
