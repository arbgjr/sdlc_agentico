# Document Enrichment Guide

**Version**: 1.9.0
**Last Updated**: 2026-01-23

## Table of Contents

1. [Overview](#overview)
2. [When to Use Document Enrichment](#when-to-use-document-enrichment)
3. [How It Works](#how-it-works)
4. [User Workflow](#user-workflow)
5. [Agent Workflow](#agent-workflow)
6. [Directory Structure](#directory-structure)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Overview

Document enrichment is an automatic process that extends existing reference documents with new research findings. When any research agent performs a search, the system:

1. **Detects** if you already have documents related to the topic
2. **Extracts** content from the original document
3. **Merges** original content with new research findings
4. **Creates** a versioned enriched document (`.enriched.vN.md`)
5. **Indexes** the enrichment in the knowledge graph

### Key Benefits

- ✅ **Cumulative Knowledge**: Documents grow over time (v1 → v2 → v3)
- ✅ **Immutable Originals**: Original documents never modified
- ✅ **Traceable Sources**: All research cited with URLs and dates
- ✅ **Graph-Indexed**: Related enrichments are discoverable
- ✅ **Automatic**: Happens transparently during research phases

---

## When to Use Document Enrichment

### Automatic Enrichment (Recommended)

Enrichment happens automatically when:
- Any research agent receives a prompt
- Documents in `.agentic_sdlc/references/` match the topic (similarity >= 0.6)
- The agent is in Phase 1 (Discovery), 2 (Requirements), or 3 (Architecture)

**Supported Agents:**
- `domain-researcher` - Research academic/web sources
- `doc-crawler` - Extract and index documentation
- `requirements-analyst` - Analyze requirements
- `adr-author` - Document architecture decisions
- `threat-modeler` - Model security threats

### Manual Enrichment

Use manual enrichment when:
- You want to add research to a specific document
- Automatic enrichment didn't trigger (similarity < 0.6)
- You have custom research data to add

```bash
# 1. Search for related documents
/doc-search OAuth 2.1 migration

# 2. Prepare research data JSON
cat > research.json <<EOF
{
  "prompt": "Research OAuth 2.1 migration",
  "topic": "OAuth 2.1 migration",
  "findings": "OAuth 2.1 consolidates...",
  "sources": [
    {
      "url": "https://oauth.net/2.1/",
      "title": "OAuth 2.1 Draft",
      "accessed_at": "2026-01-22T14:30:00Z"
    }
  ],
  "keywords": ["oauth2.1", "migration"]
}
EOF

# 3. Enrich document
/doc-enrich DOC-001 research.json
```

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────┐
│ Agent receives prompt (any research phase)      │
│ "Research OAuth 2.1 migration best practices"   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ Step 0: Check for Related Documents             │
│ - Extract keywords from prompt                  │
│ - Query /doc-search (hybrid search)             │
│ - Filter by similarity > 0.6                    │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   Found            Not Found
   similarity >= 0.6    │
        │                 │
        ▼                 ▼
┌──────────────┐   ┌──────────────┐
│ Extract doc  │   │ Research     │
│ content      │   │ normal       │
└──────┬───────┘   └──────┬───────┘
       │                  │
       └────────┬─────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│ Execute research (web, academic, community)     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ Enrich document (if related doc found)          │
│ - Merge: original + research findings           │
│ - Create .enriched.vN.md                        │
│ - Create ENRICH-{id}.yml corpus node            │
│ - Update _index.yml                             │
│ - Update graph.json with 'enriches' relation    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ Notify user                                     │
│ "✅ Document enriched: {title}"                 │
│ "📝 Version: .enriched.v1.md"                   │
│ "🔗 Corpus: ENRICH-001.yml"                     │
└─────────────────────────────────────────────────┘
```

### Similarity Algorithm

Hybrid score combining multiple factors:

```
similarity = 0.40 * keyword_overlap     # Jaccard similarity of keywords
           + 0.30 * title_similarity    # Text similarity of titles
           + 0.20 * summary_similarity  # Text similarity of summaries
           + 0.10 * category_match      # Exact category match
```

**Threshold**: 0.6 (configurable via `ENRICHMENT_MIN_SIMILARITY` env var)

---

## User Workflow

### Scenario: Research OAuth 2.1 Migration

**Step 1: User Request**
```
User: "Research OAuth 2.1 migration best practices"
```

**Step 2: Automatic Detection**
```
System:
✓ Searching for related documents...
✓ Found: DOC-001 (OAuth 2.0 Specification) - similarity: 0.85
✓ Extracting original content...
```

**Step 3: Research Execution**
```
System:
✓ Performing web search for "OAuth 2.1 migration"...
✓ Found 5 relevant sources
✓ Extracting key findings...
```

**Step 4: Enrichment Creation**
```
System:
✅ Document enriched: OAuth 2.0 Specification
📝 Version: oauth2-spec.enriched.v1.md
🔗 Corpus: ENRICH-001.yml
```

**Step 5: View Enriched Document**
```bash
cat .agentic_sdlc/references/technical/oauth2-spec.enriched.v1.md
```

---

## Agent Workflow

### Modified Agent Behavior (v1.9.0)

All research agents now include **Step 0** before research:

#### Example: domain-researcher

```markdown
## Your Task

### Step 0: Check for Related Documents (NEW)

Before starting research, check if existing documents relate to this topic:

1. Use /doc-search with extracted keywords from prompt
2. If similarity > 0.6:
   - Extract content from original document
   - Note key points to complement (not duplicate) in research
3. If no documents found:
   - Proceed with standard research

### Step 1: Execute Research
[... existing research steps ...]

### Final Step: Enrich Documents

If related documents were found in Step 0:
1. Use /doc-enrich to merge original + research findings
2. Verify enriched version was created
3. Notify user with enrichment details
```

### Agent Integration Points

| Agent | Phase | When Enriches | Example |
|-------|-------|---------------|---------|
| **domain-researcher** | 1 | After web/academic research | OAuth specs, framework docs |
| **doc-crawler** | 1 | After crawling external docs | API documentation versions |
| **requirements-analyst** | 2 | After analyzing requirements | Requirement specifications |
| **adr-author** | 3 | After researching alternatives | Architecture decision records |
| **threat-modeler** | 3 | After STRIDE analysis | Threat models with new CVEs |

---

## Directory Structure

```
.agentic_sdlc/
├── references/
│   ├── _index.yml                     # Document index with enrichment metadata
│   ├── technical/
│   │   ├── oauth2-spec.pdf            # Original (immutable)
│   │   ├── oauth2-spec.enriched.v1.md # Enriched v1
│   │   └── oauth2-spec.enriched.v2.md # Enriched v2 (if later)
│   ├── business/
│   └── legal/
├── corpus/
│   ├── nodes/
│   │   └── learnings/
│   │       ├── ENRICH-001.yml         # Enrichment metadata
│   │       └── ENRICH-002.yml
│   └── graph.json                     # Contains 'enriches' relations
└── templates/
```

### File Formats

#### _index.yml

```yaml
documents:
  - id: DOC-001
    path: "references/technical/oauth2-spec.pdf"
    title: "OAuth 2.0 Specification"
    keywords: ["oauth", "authentication"]

    enrichments:  # Enrichment history
      - enrichment_id: ENRICH-001
        enriched_at: "2026-01-22T14:30:00Z"
        research_topic: "OAuth 2.1 migration"
        agent: "domain-researcher"
        phase: 1
        corpus_node: "corpus/nodes/learnings/ENRICH-001.yml"
        enriched_file: "oauth2-spec.enriched.v1.md"
        version: 1
        similarity: 0.85
```

#### ENRICH-{id}.yml (Corpus Node)

```yaml
id: ENRICH-001
type: enrichment
title: "OAuth 2.0 Specification - Enhanced with OAuth 2.1 migration"
created_at: "2026-01-22T14:30:00Z"
agent: "domain-researcher"

source_document:
  id: DOC-001
  path: "references/technical/oauth2-spec.pdf"

research_context:
  prompt: "Research OAuth 2.1 migration best practices"
  phase: 1
  similarity: 0.85

content:
  original_summary: |
    Summary of original document content
  research_findings: |
    New research results from web, academic sources
  synthesis: |
    Combined analysis merging original + research
  sources:
    - url: "https://oauth.net/2.1/"
      title: "OAuth 2.1 Draft"
      accessed_at: "2026-01-22T14:30:00Z"

relations:
  - type: enriches
    target: DOC-001

decay_metadata:
  last_validated_at: "2026-01-22T14:30:00Z"
  decay_score: 1.0
  decay_status: fresh

tags: ["oauth", "authentication", "migration", "oauth2.1"]
```

---

## Examples

### Example 1: OAuth Spec Enrichment

**Initial State:**
```
.agentic_sdlc/references/technical/
└── oauth2-spec.pdf (OAuth 2.0 original spec)
```

**User Request:**
```
"Research OAuth 2.1 migration best practices"
```

**System Actions:**
1. Searches documents → finds oauth2-spec.pdf (similarity: 0.85)
2. Performs web research on OAuth 2.1
3. Creates enriched version with migration guide
4. Updates graph with enrichment relation

**Final State:**
```
.agentic_sdlc/
├── references/technical/
│   ├── oauth2-spec.pdf (unchanged)
│   └── oauth2-spec.enriched.v1.md (new)
└── corpus/nodes/learnings/
    └── ENRICH-001.yml (new)
```

### Example 2: Multiple Enrichments Over Time

**Timeline:**

**2026-01-22**: Initial enrichment
```bash
User: "Research OAuth 2.1 migration"
Result: oauth2-spec.enriched.v1.md (migration guide)
```

**2026-02-15**: Second enrichment
```bash
User: "Research OAuth PKCE implementation patterns"
Result: oauth2-spec.enriched.v2.md (PKCE patterns added)
```

**2026-03-10**: Third enrichment
```bash
User: "Research OAuth token introspection"
Result: oauth2-spec.enriched.v3.md (introspection added)
```

**Benefits:**
- All versions preserved
- Each enrichment tracked separately in graph
- Cumulative knowledge builds up
- Original document unchanged

---

## Troubleshooting

### No documents found during search

**Symptom:** `/doc-search` returns no results

**Solutions:**
1. Verify `_index.yml` exists and has documents
2. Check document metadata has keywords and summary
3. Lower similarity threshold: `--min-similarity 0.4`
4. Add more keywords to document metadata

### Enrichment fails with path errors

**Symptom:** `Corpus node not found` error

**Solutions:**
1. Verify directory structure matches expected layout
2. Check corpus node was created by `enrich.py`
3. Ensure paths are relative to `.agentic_sdlc/`
4. Run tests to verify path resolution

### Graph integrity violation

**Symptom:** `update_index.py --validate` fails

**Solutions:**
1. Check source document exists in graph
2. Verify enrichment ID is unique
3. Manually inspect `graph.json` for orphan edges
4. Re-run graph build: `graph_builder.py --rebuild`

### Similarity too low

**Symptom:** Related documents not detected (similarity < 0.6)

**Solutions:**
1. Improve document keywords (more specific)
2. Add better summary to document metadata
3. Use manual enrichment: `/doc-enrich DOC-ID research.json`
4. Lower `ENRICHMENT_MIN_SIMILARITY` environment variable

---

## Best Practices

### For Users

1. **Add quality metadata** when indexing documents:
   - Use specific, relevant keywords
   - Write clear, comprehensive summaries
   - Set appropriate categories

2. **Review enrichments** periodically:
   - Check enriched versions for accuracy
   - Validate sources are still accessible
   - Update when information becomes outdated

3. **Use consistent terminology** in prompts:
   - Use same keywords as document metadata
   - Be specific about what you're researching
   - Include technology versions when relevant

### For Agents

1. **Focus research on gaps**:
   - Read original document first
   - Identify what's missing or outdated
   - Research complementary information only

2. **Cite all sources**:
   - Include URL, title, and access date
   - Prefer official documentation
   - Note if information is from draft specs

3. **Create quality synthesis**:
   - Combine original + research coherently
   - Highlight what's new vs. original
   - Note any conflicts or discrepancies

### For Maintenance

1. **Regular cleanup**:
   - Archive enrichments > 1 year old
   - Remove obsolete enrichments
   - Update decay scores periodically

2. **Quality gates**:
   - Run `enrichment-quality.yml` gate before releases
   - Verify graph integrity after bulk operations
   - Check for duplicate enrichments

3. **Documentation**:
   - Keep `_index.yml` updated
   - Document major enrichments in changelog
   - Update ADRs when enriching architecture decisions

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENRICHMENT_MIN_SIMILARITY` | 0.6 | Minimum similarity for automatic enrichment |
| `ENRICHMENT_MAX_VERSIONS` | 10 | Maximum enrichment versions per document |
| `ENRICHMENT_AUTO_ARCHIVE` | true | Auto-archive old enrichments (> 1 year) |

---

## Related Documentation

- [SKILL.md](../.claude/skills/document-enricher/SKILL.md) - Technical specification
- [README.md](../.claude/skills/document-enricher/README.md) - Quick start guide
- [enrichment-quality.yml](../.claude/skills/gate-evaluator/gates/enrichment-quality.yml) - Quality gate definition

---

**Version History:**
- v1.9.0 (2026-01-23): Initial release with automatic enrichment
