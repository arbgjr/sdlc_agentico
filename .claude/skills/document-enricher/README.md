# document-enricher

**Version**: 1.9.0
**Status**: Active

Automatically enriches existing reference documents with research findings from any SDLC phase.

## What is Document Enrichment?

When agents perform research on a topic (e.g., "OAuth 2.1 migration best practices"), the system:
1. **Detects** if you already have documents related to that topic
2. **Extracts** content from the original document
3. **Merges** original content with new research findings
4. **Creates** a versioned enriched document (`.enriched.v1.md`)
5. **Indexes** the enrichment in the knowledge graph

## Why Use It?

**Problem**: You have valuable reference documents (specs, white papers, manuals) but they become outdated as technology evolves.

**Solution**: Automatically extend those documents with new research without modifying the originals.

**Benefits**:
- ✅ Preserve original documents (immutable)
- ✅ Cumulative knowledge (v1 → v2 → v3)
- ✅ Traceable sources (all research cited)
- ✅ Graph-indexed (related enrichments discoverable)

## Quick Start

### Automatic Enrichment

When any research agent receives a prompt, enrichment happens automatically:

```
User: "Research OAuth 2.1 migration best practices"

System:
1. [Step 0] Searches for documents matching "OAuth 2.1 migration"
2. Finds: DOC-001 (OAuth 2.0 Specification) - similarity: 0.85
3. Performs research focused on OAuth 2.0 → 2.1 changes
4. Creates: oauth2-spec.enriched.v1.md
5. Indexes: ENRICH-001.yml in corpus
6. Updates: graph.json with 'enriches' relation
```

### Manual Enrichment

You can also manually enrich documents:

```bash
# 1. Search for related documents
/doc-search OAuth 2.1 migration

# Output:
# [0.85] DOC-001: OAuth 2.0 Specification
#        Path: references/technical/oauth2-spec.pdf

# 2. Create research data JSON
cat > research.json <<EOF
{
  "prompt": "Research OAuth 2.1 migration",
  "topic": "OAuth 2.1 migration",
  "findings": "OAuth 2.1 consolidates OAuth 2.0 best practices...",
  "sources": [
    {
      "url": "https://oauth.net/2.1/",
      "title": "OAuth 2.1 Draft",
      "accessed_at": "2026-01-22T14:30:00Z"
    }
  ],
  "keywords": ["oauth", "oauth2.1", "migration"]
}
EOF

# 3. Enrich document
/doc-enrich DOC-001 research.json

# Output:
# ✅ Document enriched: OAuth 2.0 Specification
# 📝 Version: oauth2-spec.enriched.v1.md
# 🔗 Corpus: ENRICH-001.yml
```

## Directory Structure

```
.agentic_sdlc/
├── references/
│   └── technical/
│       ├── oauth2-spec.pdf              # Original (immutable)
│       ├── oauth2-spec.enriched.v1.md   # Enriched v1
│       └── oauth2-spec.enriched.v2.md   # Enriched v2 (if later)
├── corpus/
│   ├── nodes/
│   │   └── learnings/
│   │       ├── ENRICH-001.yml           # Enrichment metadata
│   │       └── ENRICH-002.yml
│   └── graph.json                       # Contains 'enriches' relations
```

## Enriched Document Format

```markdown
# OAuth 2.0 Specification - Enhanced Research Edition

**Original Document**: `references/technical/oauth2-spec.pdf`
**Enriched**: 2026-01-22 14:30:00 UTC
**Research Topic**: OAuth 2.1 migration
**Agent**: domain-researcher
**Phase**: 1
**Version**: v1
**Enrichment ID**: ENRICH-001

---

## Original Content Summary

[Summary of original document...]

---

## Research Findings

[New research results...]

### Sources
- [OAuth 2.1 Draft](https://oauth.net/2.1/) - Accessed 2026-01-22

---

## Synthesis

### Original Document Insights
[Original document key points...]

### New Research Findings
[New research key points...]

### Key Takeaways
- Original document provides foundational understanding
- New research extends knowledge with recent developments
- Combined, both sources offer comprehensive coverage

---

**🤖 Generated with SDLC Agêntico by @arbgjr**
```

## Scripts

### find_related.py

Finds documents related to a research topic using hybrid search.

```bash
python3 scripts/find_related.py "OAuth 2.1 migration" --min-similarity 0.6

# Options:
#   --index PATH             Path to _index.yml (default: .agentic_sdlc/references/_index.yml)
#   --min-similarity FLOAT   Minimum similarity threshold (default: 0.6)
#   --top-k INT              Maximum results (default: 5)
#   --output FORMAT          Output format: json|yaml|text (default: text)
```

**Similarity Algorithm**:
```
similarity = 0.40 * keyword_overlap
           + 0.30 * title_similarity
           + 0.20 * summary_similarity
           + 0.10 * category_match
```

### enrich.py

Enriches a document with research findings.

```bash
python3 scripts/enrich.py DOC-001 research.json --agent domain-researcher --phase 1

# Options:
#   --index PATH         Path to _index.yml
#   --agent NAME         Agent name (default: domain-researcher)
#   --phase INT          SDLC phase (default: 1)
#   --similarity FLOAT   Similarity score (default: 0.8)
#   --output-dir PATH    Output directory for enriched files
```

**Output**: JSON metadata for use with `update_index.py`

### update_index.py

Updates `_index.yml` and `graph.json` with enrichment metadata.

```bash
python3 scripts/update_index.py enrichment_metadata.json --validate

# Options:
#   --index PATH    Path to _index.yml
#   --graph PATH    Path to graph.json
#   --validate      Validate graph integrity after update
```

## Slash Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/doc-search` | Search for related documents | `/doc-search OAuth 2.1` |
| `/doc-enrich` | Manually enrich document | `/doc-enrich DOC-001 research.json` |

## Quality Gates

Enrichments are validated via `enrichment-quality.yml` gate:

**Critical Checks**:
- ✅ Research findings cite sources
- ✅ Original documents unchanged (hash check)
- ✅ Graph contains 'enriches' relation

**Warning Checks**:
- ⚠️ Versions increment sequentially
- ⚠️ Synthesis combines original + research
- ⚠️ No duplicate enrichments within 30 days

Run gate check:
```bash
python3 .claude/skills/gate-evaluator/scripts/evaluate_gate.py enrichment-quality
```

## Integration with Agents

Modified agents that use `document-enricher`:

### Phase 1 (Discovery)
- **domain-researcher** - Research academic/web sources
- **doc-crawler** - Extract and index documentation

### Phase 2 (Requirements)
- **requirements-analyst** - Analyze requirements

### Phase 3 (Architecture)
- **adr-author** - Document architecture decisions
- **threat-modeler** - Model security threats

Each agent includes **Step 0: Check for Related Documents** before research.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENRICHMENT_MIN_SIMILARITY` | 0.6 | Minimum similarity for document matching |
| `ENRICHMENT_MAX_VERSIONS` | 10 | Max enrichment versions per document |
| `ENRICHMENT_AUTO_ARCHIVE` | true | Auto-archive old enrichments (> 1 year) |

## Testing

Run unit tests:
```bash
pytest .claude/skills/document-enricher/tests/ -v
```

Run specific test:
```bash
pytest .claude/skills/document-enricher/tests/test_find_related.py -v
```

## Troubleshooting

### No documents found

**Symptom**: `/doc-search` returns no results

**Solutions**:
- Verify `_index.yml` exists and has documents
- Check that documents have keywords and summaries
- Lower `--min-similarity` threshold
- Add more keywords to document metadata

### Enrichment fails

**Symptom**: `/doc-enrich` errors out

**Solutions**:
- Verify document ID exists in `_index.yml`
- Check research JSON format (must include: prompt, topic, findings, sources, keywords)
- Ensure `document-processor` is available for content extraction

### Graph integrity violation

**Symptom**: `update_index.py --validate` fails

**Solutions**:
- Check that source document node exists in graph
- Verify enrichment ID is unique
- Manually inspect `graph.json` for orphan edges

## Examples

### Example 1: OAuth Spec Enrichment

```bash
# User request
"Research OAuth 2.1 migration best practices"

# Automatic enrichment
✅ Found related document: DOC-001 (similarity: 0.85)
✅ Performed research on OAuth 2.0 → 2.1 changes
✅ Created: oauth2-spec.enriched.v1.md
✅ Indexed: ENRICH-001.yml

# Result
.agentic_sdlc/references/technical/
├── oauth2-spec.pdf              # Original (unchanged)
└── oauth2-spec.enriched.v1.md   # Enriched with 2.1 info
```

### Example 2: Multiple Enrichments

```bash
# First enrichment (2026-01-22)
"Research OAuth 2.1 migration"
→ Creates: oauth2-spec.enriched.v1.md

# Second enrichment (2026-02-15)
"Research OAuth PKCE implementation"
→ Creates: oauth2-spec.enriched.v2.md

# Both versions preserved, both indexed in graph
```

## Related Documentation

- [SKILL.md](SKILL.md) - Full specification
- [Quality Gate](../gate-evaluator/gates/enrichment-quality.yml) - Validation rules
- [Agent Modifications](../../agents/domain-researcher.md) - Integration examples

## Version History

- **v1.9.0** (2026-01-22): Initial release
  - Hybrid search for document matching
  - Automatic enrichment workflow
  - Quality gate validation
  - Graph integration

## Support

For issues or questions:
- Check logs: `~/.claude/logs/` (structured logging with Loki)
- Run tests: `pytest .claude/skills/document-enricher/tests/ -v`
- Validate gate: `python3 .claude/skills/gate-evaluator/scripts/evaluate_gate.py enrichment-quality`
