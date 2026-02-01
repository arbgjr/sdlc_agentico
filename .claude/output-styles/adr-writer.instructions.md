---
description: 'Output style for Architecture Decision Records. Use when documenting technical decisions, trade-offs, or architectural choices.'
applyTo: '**/{adr,decision,architecture,design}*'
---

# ADR Writer Output Style

When writing Architecture Decision Records:

## ADR Structure (MADR Format)

```yaml
decision:
  id: ADR-{XXX}
  title: "{Clear, actionable title}"
  status: [proposed|accepted|superseded|deprecated]

  context: |
    What is the issue we're addressing?
    What constraints exist?
    What requirements must be met?

  decision: |
    What are we doing?
    How will we implement it?

  consequences:
    positive:
      - Benefit 1 (quantified if possible)
      - Benefit 2
    negative:
      - Trade-off 1 (quantified if possible)
      - Cost 1
    risks:
      - Risk 1 and mitigation

  alternatives:
    - name: "Alternative A"
      rejected_because: "Specific reason"
    - name: "Alternative B"
      rejected_because: "Specific reason"
```

## Writing Principles

1. **Decision-First** - Start with what you decided, not the journey
2. **Quantify Trade-offs** - "20% slower, 50% less memory" not "slower but lighter"
3. **Future-Proof Context** - Explain why this mattered in 2026
4. **Reversibility Assessment** - Can we undo this? At what cost?

## Tone

- **Declarative** - "We will use X" not "We should use X"
- **Evidence-based** - Benchmarks, data, not opinions
- **Humble** - Acknowledge what we don't know
- **Accountable** - Name the decision-maker

## Decision Types

- **Architectural** - Affects system structure (database, frameworks)
- **Technical** - Implementation choice (library, pattern)
- **Process** - How we work (CI/CD, code review)
- **Tool** - What we use (IDE, monitoring)

## Example ADR

```yaml
decision:
  id: ADR-023
  title: "Use PostgreSQL over MongoDB for user data"
  status: accepted
  created_at: "2026-01-31T23:30:00Z"
  author: "team-backend"
  phase: 3

  context: |
    User data model has evolved from initially simple documents to complex
    relational data with 12 entity types and 20+ foreign key relationships.

    Requirements:
    - ACID transactions for payment processing
    - Complex JOIN queries for reporting
    - <100ms p95 latency for user profile reads
    - Support for 10M users within 2 years

    Constraints:
    - Team has 3 years PostgreSQL experience, 6 months MongoDB
    - Existing infrastructure uses RDS (relational DB as a service)

  decision: |
    Use PostgreSQL 15+ as primary database for all user data.

    Implementation:
    - RDS PostgreSQL instance (db.r6g.xlarge for production)
    - Read replicas for reporting queries
    - Connection pooling via PgBouncer
    - Partitioning on user_id for tables >10M rows

  consequences:
    positive:
      - ACID guarantees eliminate race conditions in payments (currently 0.1% error rate)
      - Complex reporting queries 4x faster (benchmark: 800ms → 200ms)
      - Team expertise reduces onboarding time
      - Leverages existing RDS infrastructure (zero new tooling)

    negative:
      - Schema migrations slower than schemaless (avg 30min downtime per migration)
      - Horizontal scaling more complex than MongoDB sharding
      - JSON queries less elegant than MongoDB aggregation pipelines

    risks:
      - Single-region RDS = SPOF
        Mitigation: Multi-AZ deployment + daily backups to S3
      - Connection pool exhaustion under load
        Mitigation: PgBouncer + autoscaling app tier

  alternatives:
    - name: "MongoDB with transactions"
      description: "Use MongoDB 5.0+ ACID transactions"
      rejected_because: |
        Transactions require replica sets, increasing infrastructure complexity.
        Team unfamiliarity risks delayed delivery.
        Benchmark showed 2x slower JOIN-equivalent queries.

    - name: "Hybrid: PostgreSQL + MongoDB"
      description: "PostgreSQL for transactional, MongoDB for analytics"
      rejected_because: |
        Dual-database increases operational complexity (backups, monitoring).
        Data synchronization adds failure modes.
        Not justified for current scale (10M users achievable in single DB).

  metadata:
    complexity: high
    reversible: false  # Data migration back to MongoDB = 2-3 weeks
    cost_impact: "+$500/month RDS vs MongoDB Atlas"
    performance_impact: "+4x faster reporting, -30% write throughput"
```

## Anti-Patterns

- ❌ Don't write ADRs for trivial decisions (variable naming, etc.)
- ❌ Don't skip alternatives (shows you didn't evaluate options)
- ❌ Don't use vague consequences ("better performance")
- ❌ Don't omit author/date (ADRs are historical records)
- ❌ Don't make decisions reversible=true if they're not (migrations are costly)
