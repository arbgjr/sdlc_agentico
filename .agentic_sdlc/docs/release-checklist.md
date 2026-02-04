# Release Checklist

**CRITICAL**: Before creating any release tag, ALL these items MUST be verified and updated.

## 1. Version Files Update

**Files that MUST be updated with new version:**

- [ ] `.claude/VERSION` - Update `version:` and `build_date:` fields

  ```yaml
  version: "X.Y.Z"  # ← UPDATE THIS
  build_date: "YYYY-MM-DD"  # ← UPDATE THIS
  ```

- [ ] `.claude/VERSION` - Add new changelog entry at the TOP

  ```yaml
  changelog:
    - version: "X.Y.Z"  # ← ADD NEW ENTRY HERE
      date: "YYYY-MM-DD"
      changes:
        - "feat: Description"
  ```

## 2. README.md Updates

**Files that MUST be updated:**

- [ ] **README.md Line 3** - Version badge

  ```markdown
  [![Version](https://img.shields.io/badge/version-X.Y.Z-red.svg)](https://github.com/arbgjr/sdlc_agentico/releases/tag/vX.Y.Z)
  ```

- [ ] **README.md Line 41** - ASCII art header

  ```
  │                         SDLC AGÊNTICO vX.Y.Z                            │
  ```

- [ ] **README.md Lines 44-56** - Feature timeline (add new version line if major feature)

  ```
  │  Feature Name | Description | Component Name (vX.Y.Z)        │
  ```

- [ ] **README.md Line 75** - Installation example VERSION variable

  ```bash
  VERSION="vX.Y.Z"  # ← UPDATE THIS
  ```

- [ ] **README.md Line 96** - Script installation example

  ```bash
  --version vX.Y.Z  # ← UPDATE THIS
  ```

## 3. Skill/Module Versions (if applicable)

If releasing a new skill or major skill update:

- [ ] Update skill `SKILL.md` metadata:

  ```yaml
  version: X.Y.Z  # Skill version
  ```

- [ ] Update skill README.md references
- [ ] Update IMPLEMENTATION_SUMMARY.md (if exists)

## 4. Pre-Release Verification

**Before creating tag:**

- [ ] Run all tests: `pytest .claude/skills/*/tests/ -v`
- [ ] Verify no uncommitted changes: `git status`
- [ ] Verify current branch is `main`: `git branch --show-current`
- [ ] Pull latest changes: `git pull origin main`
- [ ] Check last commit includes version updates: `git log -1`

## 5. Tag Creation

**Create annotated tag with proper message:**

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z - Feature Name

Brief description of release.

Features:
- Feature 1
- Feature 2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Push tag:**

```bash
git push origin vX.Y.Z
```

## 6. Release Automation

**The GitHub Action will automatically:**

- ✅ Create draft release
- ✅ Generate `.tar.gz` and `.zip` packages
- ✅ Attach assets to release

**You MUST manually:**

- [ ] Edit draft release on GitHub
- [ ] Update release notes (copy from tag message or enhance)
- [ ] Mark as "Latest Release"
- [ ] Publish release (remove draft status)

## 7. Post-Release Verification

**After publishing release:**

- [ ] Verify release is marked as "Latest": `gh release list | head -1`
- [ ] Verify assets were uploaded: `gh release view vX.Y.Z`
- [ ] Test installation from release:

  ```bash
  curl -fsSL "https://github.com/arbgjr/sdlc_agentico/releases/download/vX.Y.Z/sdlc-agentico-vX.Y.Z.tar.gz" | tar -tzf - | head
  ```

- [ ] Check badges in README.md are working (visit GitHub repo page)

## 8. Common Mistakes to Avoid

❌ **DO NOT:**

- Create tag before updating `.claude/VERSION`
- Forget to update README.md badges and examples
- Use version numbers that don't match git tag
- Skip updating changelog in `.claude/VERSION`
- Reference non-existent release URLs in README
- Create release without proper tag message

✅ **ALWAYS:**

- Update ALL version references in one commit BEFORE tagging
- Use semantic versioning (major.minor.patch)
- Add Co-Authored-By line in tag messages
- Test release package before announcing
- Update feature timeline in README for major features

## 9. Release Types

**Version Numbering Guide:**

- **Major (X.0.0)**: Breaking changes, major architecture changes
- **Minor (x.Y.0)**: New features, new skills, significant enhancements
- **Patch (x.y.Z)**: Bug fixes, documentation updates, minor improvements

**Examples:**

- v1.8.0 → v1.8.1: Bug fix (patch)
- v1.8.1 → v1.9.0: New skill added (minor)
- v1.9.0 → v2.0.0: Breaking changes to SDLC workflow (major)

## 10. Rollback Procedure

**If release has critical issues:**

```bash
# 1. Delete release
gh release delete vX.Y.Z --yes

# 2. Delete tag locally and remotely
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z

# 3. Fix issues in new commit
git add .
git commit -m "fix: critical issue"

# 4. Create new patch version (X.Y.Z+1)
# Follow checklist from step 1
```

---

**Last Updated**: 2026-02-04
