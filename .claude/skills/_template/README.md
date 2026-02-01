# Skill Template

This is the official template for creating new SDLC Agêntico skills following Anthropic best practices.

## Philosophy: Natural Language First

**Before creating a script, ask**:
> "Can Claude do this with natural language instructions?"

If **YES** → Use natural language
If **NO** → Justify why script is needed

## When to Use Scripts

Scripts are ONLY justified for:

| Category | Examples | Why |
|----------|----------|-----|
| **Deterministic Validation** | Schema validation, syntax checking | Must be 100% consistent |
| **External API Integration** | GitHub API, third-party services | Authentication, retries, error handling |
| **Complex I/O** | Scanning thousands of files, binary parsing | Performance, memory efficiency |
| **Safety-Critical Operations** | Git worktree, database migrations | Side effects must be deterministic |

**NOT for**:
- ❌ Pattern matching (Claude is better)
- ❌ Text analysis (Claude is better)
- ❌ Conditional workflows (Claude is better)
- ❌ Looping over files (Bash + Claude is sufficient)

## How to Use This Template

### 1. Copy Template

```bash
cp -r .claude/skills/_template .claude/skills/your-skill-name
```

### 2. Customize SKILL.md

- Update frontmatter (name, description, allowed-tools)
- Write Quick Start section
- Define workflows in natural language
- Add scripts ONLY if justified (with "Why needed" section)

### 3. Add Reference Files (if needed)

```bash
# For skills approaching 500 lines, split into reference files
.claude/skills/your-skill/
├── SKILL.md (< 500 lines - overview)
└── reference/
    ├── topic-a.md (loaded only when needed)
    ├── topic-b.md
    └── api.md
```

### 4. Test with Claude

1. Load skill with Claude
2. Execute workflows using ONLY natural language instructions
3. If Claude struggles → Add MORE CONTEXT (not scripts)
4. If operation is truly deterministic → Add justified script

## Progressive Disclosure Pattern

**Bad** (500+ lines in SKILL.md):
```
skills/bigquery/
└── SKILL.md (800 lines - ALL schemas, ALL queries)
```

**Good** (< 500 lines + references):
```
skills/bigquery/
├── SKILL.md (< 500 lines - overview, navigation)
└── reference/
    ├── finance.md (revenue, billing - loaded when needed)
    ├── sales.md (opportunities, pipeline)
    └── product.md (API usage, features)
```

Claude loads reference files ONLY when user asks about that domain → Zero token overhead until used.

## Template Structure

```
_template/
├── SKILL.md              # Main skill file (< 500 lines)
├── README.md             # This file (template documentation)
├── reference/            # Progressive disclosure files
│   ├── topic-a.md        # Detailed info on topic A
│   ├── topic-b.md        # Detailed info on topic B
│   └── api.md            # API reference
├── scripts/              # Scripts (ONLY if justified)
│   ├── script.py         # With "Why needed" justification
│   └── validate.sh       # Bash for simple operations
└── tests/
    ├── unit/             # Unit tests
    └── integration/      # Integration tests
```

## Checklist Before Publishing Skill

- [ ] SKILL.md < 500 lines (or uses progressive disclosure)
- [ ] Description is specific and includes key terms
- [ ] Workflows use natural language (not pseudocode)
- [ ] All scripts have "Why this script is needed" section
- [ ] No scripts for pattern matching or text analysis
- [ ] Examples are concrete (not abstract)
- [ ] Reference files are one level deep (not nested)
- [ ] Tested with Claude (not just assumed it works)

## Common Mistakes

### ❌ Mistake 1: Documenting API That Doesn't Exist

```python
# Bad - This function doesn't exist
result = process_document(path, options)
```

**Fix**: Use natural language instructions that Claude can execute:
```markdown
1. Read document: `cat document.txt`
2. Search for patterns: Look for "error", "warning"
3. Summarize findings
```

---

### ❌ Mistake 2: Scripts for Simple Loops

```python
# Bad - Unnecessary script
for file in glob("*.txt"):
    process(file)
```

**Fix**: Natural language → Claude generates Bash dynamically:
```markdown
Process all .txt files:

```bash
for file in *.txt; do
  echo "Processing: $file"
  # Claude will generate appropriate processing
done
```
```

---

### ❌ Mistake 3: Over-Explaining

```markdown
# Bad - Too verbose
PDF (Portable Document Format) files are a common format that contains text.
To extract text, you need a library. There are many libraries available...
```

**Fix**: Assume Claude is smart:
```markdown
# Good - Concise
Extract text with pdfplumber:

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

---

### ❌ Mistake 4: Nested References

```markdown
# Bad - Too deep
# SKILL.md
See [advanced.md](advanced.md)

# advanced.md
See [details.md](details.md)

# details.md
Here's the actual info...
```

**Fix**: Keep references one level deep:
```markdown
# Good - One level
# SKILL.md
- [Advanced Details](reference/advanced.md)
- [API Reference](reference/api.md)
- [Examples](reference/examples.md)
```

## Examples of Good Skills

### Example 1: iac-generator (Scripts Justified)

**What it does**: Generates Terraform, Bicep, K8s manifests

**Scripts**:
- ✅ `terraform_validator.py` - **Why**: Deterministic HCL syntax validation
- ✅ `kubernetes_schema.py` - **Why**: YAML schema validation (PodSecurityStandards)

**Natural Language**:
- Workflow instructions
- Template selection logic
- Output formatting

---

### Example 2: gate-evaluator (NO Scripts Needed)

**What it does**: Validates quality gates between phases

**Natural Language Only**:
```markdown
## Phase 2 → 3 Gate

Check:
- [ ] Requirements documented in docs/requirements.md
- [ ] At least 1 ADR in .agentic_sdlc/corpus/nodes/decisions/
- [ ] All requirements have acceptance criteria

```bash
ls .agentic_sdlc/corpus/nodes/decisions/ADR-*.yml | wc -l  # > 0
```

If all checks pass: APPROVE
If any fail: BLOCK with specific reason
```

**No Python needed** - Claude can execute Bash and make decision.

---

## Anti-Patterns from Anthropic Documentation

### ❌ Don't: Assume Tools Are Installed

```markdown
# Bad
Use the pdf library to process the file.
```

### ✅ Do: Explicit Dependencies

```markdown
# Good
Install required package:

```bash
pip install pypdf
```

Then use it:
```python
from pypdf import PdfReader
```
```

---

### ❌ Don't: Offer Too Many Options

```markdown
# Bad
You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image...
```

### ✅ Do: Provide Default with Escape Hatch

```markdown
# Good
Use pdfplumber for text extraction:

```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image + pytesseract instead.
```

---

## References

- [Anthropic: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [LEARN-natural-language-first-principle.md](../../../.agentic_sdlc/corpus/nodes/learnings/LEARN-natural-language-first-principle.md)
- [Script Audit Report](../../../.agentic_sdlc/reports/script-audit-2026-01-31.md)

---

**Template Version**: 1.0.0
**Last Updated**: 2026-01-31
**Maintained By**: SDLC Agêntico Core Team
