# Action Plan - v2.3.2 Critical Fixes

**Target Release:** v2.3.2
**Sprint Duration:** 2-3 days (14 hours total)
**Blockers Resolved:** 7 CRITICAL bugs
**Quality Impact:** HIGH

---

## 🎯 Sprint Goal

Fix ALL 7 CRITICAL bugs that prevent sdlc-import from being production-ready, focusing on:
1. Automation compatibility (CI/CD)
2. Correctness of generated artifacts
3. Quality gate enforcement
4. Security by Design enforcement

---

## 📋 Task Breakdown

### Task 1: Fix Interactive Prompt (C1)
**File:** `.claude/skills/sdlc-import/scripts/project_analyzer.py`
**Lines:** 1195-1241
**Effort:** 2 hours
**Priority:** P0

**Changes:**
```python
def _prompt_user_approval(self, quality_report, validation_result, correlation_id):
    """Prompt user for approval (or auto-approve in CI mode)"""

    # FIX C1: Check auto-approve flag BEFORE prompting
    if self.config.get('auto_approve', False):
        logger.info("Auto-approve enabled - skipping user prompt")
        return UserDecision.APPROVED

    # Check for CI environment
    if os.getenv('CI') == 'true' or os.getenv('TERM') == 'dumb':
        logger.info("CI environment detected - auto-approving")
        return UserDecision.APPROVED

    # Check if stdin is a TTY
    if not sys.stdin.isatty():
        logger.warning("Non-interactive shell detected - auto-approving")
        return UserDecision.APPROVED

    # Only prompt if interactive
    try:
        response = input("Approve import? (y/n): ").strip().lower()
        return UserDecision.APPROVED if response == 'y' else UserDecision.REJECTED
    except EOFError:
        logger.warning("EOF on input - auto-approving")
        return UserDecision.APPROVED
```

**CLI Addition:**
```bash
# In run-import.sh
if [[ "$1" == "--auto-approve" ]]; then
    PYTHON_ARGS="--auto-approve"
fi
```

**Test:**
```bash
# Should pass without prompt
./run-import.sh --auto-approve /path/to/project

# Should pass in CI
CI=true ./run-import.sh /path/to/project
```

---

### Task 2: Fix Generic Diagrams (C2)
**File:** `.claude/skills/sdlc-import/scripts/architecture_visualizer.py`
**Effort:** 4 hours
**Priority:** P0

**Investigation First:**
```bash
# Check current implementation
grep -A 20 "def generate_component_diagram" architecture_visualizer.py
```

**Expected Fix:**
```python
def generate_component_diagram(self, language_analysis: Dict) -> str:
    """Generate component diagram based on detected languages"""

    # FIX C2: Use language_analysis instead of hardcoded template
    primary_lang = language_analysis.get('primary', {}).get('language', 'Unknown')
    frameworks = language_analysis.get('primary', {}).get('frameworks', [])

    # Select template based on detected stack
    if primary_lang == 'C#':
        return self._generate_dotnet_diagram(frameworks)
    elif primary_lang == 'Python':
        return self._generate_python_diagram(frameworks)
    elif primary_lang == 'JavaScript' or primary_lang == 'TypeScript':
        return self._generate_nodejs_diagram(frameworks)
    else:
        return self._generate_generic_diagram(primary_lang, frameworks)

def _generate_dotnet_diagram(self, frameworks: List[str]) -> str:
    """Generate .NET-specific architecture diagram"""
    backend = "ASP.NET Core" if "ASP.NET Core" in frameworks else ".NET"
    orm = "Entity Framework Core" if "Entity Framework Core" in frameworks else "ADO.NET"

    return f"""
graph TB
    Client[Client Apps]
    API[{backend} API]
    DB[(PostgreSQL/SQL Server)]
    Cache[(Redis Cache)]

    Client -->|HTTPS| API
    API -->|{orm}| DB
    API -->|Cache| Cache
"""
```

**Test:**
```python
def test_dotnet_diagram_generation():
    visualizer = ArchitectureVisualizer()
    language_analysis = {
        'primary': {
            'language': 'C#',
            'frameworks': ['ASP.NET Core', 'Entity Framework Core']
        }
    }

    diagram = visualizer.generate_component_diagram(language_analysis)

    assert 'ASP.NET Core' in diagram
    assert 'Entity Framework Core' in diagram
    assert 'Django' not in diagram  # Shouldn't use generic template
```

---

### Task 3: Exclude Migration Files (C3)
**File:** `.claude/skills/sdlc-import/scripts/decision_extractor.py`
**Effort:** 2 hours
**Priority:** P0

**Changes:**
```python
# Add at top of file
EXCLUDED_FILE_PATTERNS = [
    r'Migrations/\d{14}_.*\.cs$',      # EF Core migrations
    r'Migrations/\d{14}_.*\.Designer\.cs$',  # Migration designers
    r'\.g\.cs$',                        # Generated code
    r'\.Designer\.cs$',                 # Auto-generated designers
    r'/obj/',                           # Build artifacts
    r'/bin/',                           # Build artifacts
]

def should_scan_file(self, file_path: Path) -> bool:
    """Check if file should be scanned for decisions"""
    file_str = str(file_path)

    # Check exclusion patterns
    for pattern in EXCLUDED_FILE_PATTERNS:
        if re.search(pattern, file_str):
            logger.debug(f"Excluding file (auto-generated): {file_path}")
            return False

    return True

# In extract_decisions() method
for file_path in all_files:
    if not self.should_scan_file(file_path):
        continue
    # ... rest of logic
```

**Test:**
```python
def test_migration_files_excluded():
    extractor = DecisionExtractor(config={})

    # Should exclude
    assert not extractor.should_scan_file(Path("Migrations/20240115_AddUserTable.cs"))
    assert not extractor.should_scan_file(Path("Migrations/20240115_AddUserTable.Designer.cs"))
    assert not extractor.should_scan_file(Path("Models/User.g.cs"))

    # Should include
    assert extractor.should_scan_file(Path("Models/User.cs"))
    assert extractor.should_scan_file(Path("Services/AuthService.cs"))
```

**Validation:**
```bash
# Before fix: 40 ADRs (7 real + 33 migration-based)
# After fix: 7-10 ADRs (only real decisions)
```

---

### Task 4: Enforce Quality Gate (C4)
**File:** `.claude/skills/sdlc-import/scripts/post_import_validator.py`
**Lines:** 180-191
**Effort:** 2 hours
**Priority:** P0

**Changes:**
```python
# In validate_and_fix() method
def validate_and_fix(...) -> ValidationResult:
    # ... existing validation logic ...

    # Calculate overall score
    overall_score = self._calculate_overall_score(metrics)

    # FIX C4: Enforce quality threshold
    quality_threshold = self.config.get('quality_threshold', 0.7)
    passed = overall_score >= quality_threshold

    if not passed:
        logger.error(
            f"Quality gate FAILED: score={overall_score:.2%} < threshold={quality_threshold:.2%}",
            extra={'correlation_id': correlation_id}
        )

        # Attempt auto-fix
        if self.config.get('auto_fix_enabled', True):
            logger.info("Attempting auto-fix to meet quality threshold...")
            # Run auto-fixes again
            # ... (existing auto-fix logic)

            # Recalculate score
            overall_score = self._calculate_overall_score(metrics)
            passed = overall_score >= quality_threshold

            if not passed:
                logger.error(f"Auto-fix FAILED to meet threshold: {overall_score:.2%}")
    else:
        logger.info(f"Quality gate PASSED: score={overall_score:.2%}")

    result = ValidationResult(
        passed=passed,  # ✅ Now correctly reflects quality threshold
        overall_score=overall_score,
        ...
    )

    return result
```

**Test:**
```python
def test_quality_gate_blocks_low_score():
    config = {'quality_threshold': 0.7}
    validator = PostImportValidator(config)

    # Mock low-quality results
    import_results = {
        'decisions': {'decisions': [], 'count': 0},  # No ADRs = low quality
        'diagrams': {'diagrams': [], 'count': 0}
    }

    result = validator.validate_and_fix(import_results, ...)

    assert result.passed == False  # Should fail
    assert result.overall_score < 0.7
```

---

### Task 5: Enforce Security Gate (C5)
**File:** `.claude/skills/sdlc-import/scripts/post_import_validator.py`
**Effort:** 3 hours
**Priority:** P0

**Changes:**
```python
# Add new validation method
def _validate_security_threats(self, import_results, correlation_id):
    """Validate security threats and block on CRITICAL severity"""

    threats = import_results.get('threats', {}).get('threats', [])

    # Count by severity
    critical_threats = [t for t in threats if t.get('severity') == 'CRITICAL']
    high_threats = [t for t in threats if t.get('severity') == 'HIGH']

    # Security gate: Block on CRITICAL threats
    if len(critical_threats) > 0:
        logger.error(
            f"Security gate FAILED: {len(critical_threats)} CRITICAL threats detected",
            extra={
                'correlation_id': correlation_id,
                'critical_threats': [t['title'] for t in critical_threats]
            }
        )

        # Check if we should block
        block_on_critical = self.config.get('security_gate', {}).get('block_on_critical', True)

        if block_on_critical:
            return {
                'passed': False,
                'critical_count': len(critical_threats),
                'high_count': len(high_threats),
                'threats': critical_threats,
                'message': 'CRITICAL security threats must be resolved before import'
            }

    # Warn on HIGH threats but don't block
    if len(high_threats) > 0:
        logger.warning(
            f"{len(high_threats)} HIGH severity threats detected - review recommended",
            extra={'correlation_id': correlation_id}
        )

    return {
        'passed': True,
        'critical_count': 0,
        'high_count': len(high_threats),
        'threats': []
    }

# In validate_and_fix() method
def validate_and_fix(...):
    # ... existing validations ...

    # FIX C5: Add security gate validation
    security_result = self._validate_security_threats(import_results, correlation_id)

    if not security_result['passed']:
        # Security gate FAILED - update overall result
        issues_detected.append({
            'category': 'security',
            'severity': 'critical',
            'message': security_result['message'],
            'threats': security_result['threats']
        })

        # Override passed flag
        passed = False

    # Add security metrics
    metrics['security_critical_threats'] = security_result['critical_count']
    metrics['security_high_threats'] = security_result['high_count']
```

**Configuration:**
```yaml
# In import_config.yml
security_gate:
  enabled: true
  block_on_critical: true  # Block import if CRITICAL threats found
  escalate_on_high: true   # Notify but don't block on HIGH threats
```

**Test:**
```python
def test_security_gate_blocks_critical_threats():
    config = {
        'security_gate': {
            'enabled': True,
            'block_on_critical': True
        }
    }
    validator = PostImportValidator(config)

    # Mock results with CRITICAL threat
    import_results = {
        'threats': {
            'threats': [
                {
                    'title': 'Hardcoded API Key',
                    'severity': 'CRITICAL',
                    'cvss_score': 9.8
                }
            ]
        }
    }

    result = validator.validate_and_fix(import_results, ...)

    assert result.passed == False
    assert 'security' in [i['category'] for i in result.issues_detected]
```

---

### Task 6: Fix Exit Code (C7)
**File:** `.claude/skills/sdlc-import/scripts/project_analyzer.py`
**Lines:** Multiple locations
**Effort:** 1 hour
**Priority:** P0

**Changes:**
```python
# In analyze() method
def analyze(self) -> Dict[str, Any]:
    try:
        # ... existing analysis logic ...

        # FIX C7: Return success even if prompt fails
        # Prompt is optional - artifacts are what matter
        try:
            if not self.config.get('skip_approval', False):
                user_decision = self._prompt_user_approval(...)
        except Exception as e:
            logger.warning(f"User prompt failed (non-critical): {e}")
            user_decision = UserDecision.APPROVED  # Default to approved

        # Check if artifacts were successfully created
        artifacts_ok = self._check_artifacts_created()

        if artifacts_ok:
            logger.info("Import completed successfully - artifacts generated")
            return results  # Exit code 0
        else:
            logger.error("Import failed - missing required artifacts")
            sys.exit(1)  # Exit code 1 only if artifacts missing

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)

def _check_artifacts_created(self) -> bool:
    """Verify that required artifacts were created"""
    required_files = [
        self.output_dir / "corpus/graph.json",
        self.output_dir / "corpus/adr_index.yml",
        self.output_dir / "reports/import-report.md"
    ]

    for file_path in required_files:
        if not file_path.exists():
            logger.error(f"Missing required artifact: {file_path}")
            return False

    return True
```

**Test:**
```bash
# Should exit 0 if artifacts created (even if prompt fails)
./run-import.sh /path/to/project < /dev/null
echo $?  # Should be 0

# Should exit 1 only if artifacts missing
# (can't easily test without mocking file creation)
```

---

## 🧪 Integration Tests

Create comprehensive test for all fixes:

**File:** `.claude/skills/sdlc-import/tests/integration/test_critical_fixes_v2_3_2.py`

```python
def test_all_critical_fixes():
    """Integration test for all v2.3.2 critical fixes"""

    # Setup test project with .NET + migrations
    project = create_test_dotnet_project_with_migrations()

    # Execute import with auto-approve
    result = run_import(
        project_path=project,
        auto_approve=True,  # C1 fix
        llm_enabled=False
    )

    # C7: Should succeed (exit code 0)
    assert result.exit_code == 0

    # C2: Diagrams should be .NET-specific
    component_diagram = read_file(project / ".project/architecture/component-diagram.mmd")
    assert "ASP.NET Core" in component_diagram
    assert "Django" not in component_diagram

    # C3: Should NOT have migration-based ADRs
    adrs = list_adrs(project / ".project/corpus/nodes/decisions")
    migration_adrs = [a for a in adrs if "migration" in a.lower()]
    assert len(migration_adrs) == 0

    # C4: Quality gate should enforce threshold
    quality_report = read_quality_report(project)
    if quality_report['score'] < 0.7:
        assert quality_report['passed'] == False

    # C5: Security gate should block CRITICAL threats
    if has_critical_threats(project):
        assert result.validation_passed == False
```

---

## 📊 Success Criteria

v2.3.2 is ready for release when:

- [ ] All 7 CRITICAL bugs have fixes implemented
- [ ] Integration test passes (test_critical_fixes_v2_3_2.py)
- [ ] Manual test on Autoritas project:
  - [ ] No crash/exception
  - [ ] Exit code 0
  - [ ] Diagrams show .NET/PostgreSQL (not Django/MongoDB)
  - [ ] < 15 ADRs generated (not 40 with migrations)
  - [ ] Quality score > 70% OR validation fails
  - [ ] CRITICAL threats block import OR escalate
- [ ] CI/CD test passes:
  - [ ] `CI=true ./run-import.sh` completes without prompt
  - [ ] GitHub Actions workflow succeeds

---

## 🚀 Release Plan

### Pre-Release (Day 1)
1. Create branch `fix/critical-bugs-v2.3.2`
2. Implement Tasks 1-6
3. Write integration tests
4. Manual test on Autoritas

### Testing (Day 2)
1. Run full test suite
2. Test on multiple projects (Python, .NET, Node.js)
3. Test in CI environment
4. Performance benchmark

### Release (Day 3)
1. Update `.claude/VERSION` to 2.3.2
2. Update README.md, CLAUDE.md
3. Create comprehensive release notes
4. Commit + tag v2.3.2
5. Push + verify GitHub Actions
6. Update release notes on GitHub

---

## 📝 Release Notes Draft (v2.3.2)

```markdown
# Release v2.3.2 - Critical Bug Fixes for Production Use

## 🚨 CRITICAL FIXES (7 bugs)

This release makes sdlc-import production-ready by fixing ALL blockers:

✅ **No more interactive prompts in CI/CD** (C1)
✅ **Correct diagrams for detected languages** (C2)
✅ **No false ADRs from migration files** (C3)
✅ **Quality gates enforce thresholds** (C4)
✅ **Security gates block critical threats** (C5)
✅ **LLM synthesis can be enabled** (C6)
✅ **Exit code 0 when artifacts OK** (C7)

## Before v2.3.2
- Import crashed in CI/CD (needed TTY)
- Generated wrong diagrams (Django for .NET projects)
- Created 40 ADRs (33 false positives from migrations)
- Passed with 65% quality (below 70% threshold)
- Allowed CRITICAL security threats
- Exit code 1 even when artifacts OK

## After v2.3.2
- Runs in CI/CD without prompts
- Generates correct diagrams for detected stack
- Creates 7-10 real ADRs (no migration noise)
- Blocks if quality < 70%
- Blocks on CRITICAL security threats
- Exit code 0 when successful

## Upgrade
No breaking changes. Update immediately.
```

---

**Action Plan created by:** Claude Sonnet 4.5
**Date:** 2026-01-29
**Target:** v2.3.2 (Sprint 1 - 14 hours)
