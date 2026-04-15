# Runbook — resilience_circuit_open_minutes_daily

**SLO target**: total minutes per day any named circuit breaker is open ≤ 5 min
**Owner**: resilience
**Priority**: P2 — a sick dependency becoming silent is worse than the dependency itself being sick

## Symptom

- Stat panel "Resilience circuits open minutes (24h)" crosses 5 minutes
- Loki emits `circuit.opened` events more than twice per hour
- Calls wrapped with `@resilient` raise `CircuitOpenError` downstream;
  operators see 503s propagated through the stack

## Triage (first 5 minutes)

1. **Which breakers are open?**
   ```logql
   {logger="resilience", message="circuit.opened"} | json
     | line_format "{{.breaker_name}} cooldown={{.cooldown_s}}s"
   ```
2. **What was the failure rate that tripped it?**
   ```logql
   {logger="resilience"} | json
     | line_format "{{.function}} {{.message}} {{.error_type}}"
   ```
3. **Is the underlying dependency actually sick?**
   Try a direct call (curl, sdk) outside the breaker. If it works →
   the breaker is too sensitive; if it also fails → the dependency is
   the root cause, not the breaker.

## Common causes (ranked by frequency)

1. **Dependency intermittently slow** — latency bursts trip the `window`
   before the dependency recovers. Fix = raise timeout, not raise
   failure_threshold.
2. **Transient DNS/TLS failure** — looks like a dependency outage but
   recovers within the cooldown. The breaker correctly prevented cascade.
3. **Bug in wrapped function** — the function raises a non-network
   exception that the retry layer keeps retrying, exhausting the
   window. Fix = add `give_up_on=(SomeDomainError,)` to the `@resilient`
   decorator.
4. **Load shedding working as designed** — the dependency is overloaded
   and the breaker is protecting it. In this case the breaker is healthy
   output, not a problem to fix.

## Mitigation

| Cause | Action |
|---|---|
| Slow dependency | Increase `timeout_s` on the `@resilient` decorator (per call-site); do NOT raise `failure_threshold` without thinking. |
| Transient failures | No action — breaker is working. Watch. |
| Wrapped function bug | Fix the function; add the domain exception to `give_up_on` so retries don't amplify. |
| Load shedding | No action — breaker is legitimate protection. Consider raising queue depth upstream. |

## Rollback

Circuit breakers are in-process state. A process restart resets every
named breaker. Use only if you know the dependency has recovered:

```bash
# Restart the service owning the breaker, NOT the dependency.
# The dependency's health is orthogonal.
```

## Escalation

- Any breaker open > 10 minutes consecutively → dependency incident.
  Open `.project/incidents/<date>-<dep>.md` and route to
  `incident-commander`.
- Breaker name `<orchestrator>.*` (affects orchestration core) → P1
  regardless of duration.

## Post-incident RCA

1. Which dependency was the root cause.
2. Whether the breaker config (threshold, window, cooldown) was
   well-tuned — neither too sensitive nor too permissive.
3. Whether any fallback path (e.g. `parallel_workers` when
   `copilot_cloud_agent` is degraded) fired correctly.

## Teach the framework

If a breaker opens on the same dependency ≥ 3 times per month:

- Implement a *canary call* before the real call so the breaker is
  tripped by a cheap probe, not by user-facing traffic.
- Add a Loki alert rule that fires on the 2nd open within 1h, before
  the daily SLO burns.
