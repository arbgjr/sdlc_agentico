# sdlc-import TODO List

## Implemented in v2.0.2
- ✅ Fix #1: Force LLM when llm.enabled=true
- ✅ Fix #2: Validate threat_modeling execution
- ✅ Fix #3: Populate phase-artifacts/
- ✅ Fix #7: Index original ADRs in references/
- ✅ Fix #8: Auto-push feature branch

## Planned for v2.1.0
- ⏳ Fix #4: Analyze Migrations (EF Core, Alembic, Flyway)
- ⏳ Fix #5: Cross-reference code vs ADR claims
- ⏳ Fix #6: Create corpus/graph.json
- ⏳ Fix #9: Auto-create GitHub issues with --create-issues

### Fix #4: Migration Analyzer
Create `migration_analyzer.py` to extract decisions from migrations:
- EF Core: `Migrations/*.cs`
- Alembic: `alembic/versions/*.py`
- Flyway: `db/migration/*.sql`

Extract: schema evolution, RLS policies, indexes, constraints

### Fix #5: ADR Claim Validator
Create `adr_validator.py` to validate claims:
- Check LGPD coverage (grep for DataSubjectRight classes)
- Check RLS implementation (grep for RLS policies in DB)
- Check compliance frameworks (verify code vs ADR statements)

### Fix #6: Knowledge Graph Generator
Create `graph_generator.py`:
- Extract relations between ADRs (supersedes, implements, addresses)
- Generate `.agentic_sdlc/corpus/graph.json`
- Generate `.agentic_sdlc/corpus/adjacency.json`

### Fix #9: GitHub Issue Creator
Enhance `documentation_generator.py`:
- When `--create-issues` flag is used:
  - Create issue for each P0/P1 tech debt item
  - Label: `sdlc-import`, `tech-debt`, `P0`/`P1`
  - Assign to project board if exists

## Notes
These features are complex and require:
- LLM integration (Fix #4, #5)
- Graph-navigator skill integration (Fix #6)
- GitHub GraphQL API (Fix #9)

Will be implemented in separate PRs for v2.1.0.
