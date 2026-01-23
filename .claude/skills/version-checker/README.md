# Version Checker Skill

Intelligent auto-update checker for SDLC Agêntico that automatically detects new releases, analyzes impact, and handles updates with user approval.

## Features

- **Automatic Version Detection**: Compares current version with latest GitHub release
- **Smart Caching**: Caches release data for 1 hour to avoid rate limiting
- **Impact Analysis**: Detects breaking changes, migrations, dependency updates, and security fixes
- **Dismissal Tracking**: Remembers user decisions to dismiss specific versions
- **Automated Updates**: Executes git operations to update repository with rollback support
- **Structured Logging**: Full observability with Loki integration

## Usage

### Check for Updates

```bash
python3 .claude/skills/version-checker/scripts/check_updates.py
```

Returns JSON with update status:
```json
{
  "update_available": true,
  "current": "1.7.16",
  "latest": "1.8.0",
  "dismissed": false,
  "changelog": "...",
  "impact": {
    "severity": "minor",
    "breaking_changes": [],
    "migrations": ["Run migration script"],
    "dependencies": {"Python": {"old": "3.9", "new": "3.11"}},
    "security_fixes": []
  },
  "notification": "..."
}
```

### Execute Update

```bash
python3 .claude/skills/version-checker/scripts/check_updates.py --execute
```

Automatically updates to latest version if available.

### Dismiss Update

```bash
python3 .claude/skills/version-checker/scripts/check_updates.py --dismiss 1.8.0
```

### Clear Cache

```bash
python3 .claude/skills/version-checker/scripts/check_updates.py --clear-cache
```

## Components

### Core Modules

| Module | Purpose |
|--------|---------|
| `version_comparator.py` | Semantic version parsing and comparison |
| `release_fetcher.py` | GitHub release fetching with caching (gh CLI) |
| `impact_analyzer.py` | Changelog parsing and impact analysis |
| `dismissal_tracker.py` | User dismissal state management |
| `check_updates.py` | Main orchestrator |
| `update_executor.py` | Automated git update operations |

### Integration

This skill is automatically invoked by the **orchestrator agent** when `/sdlc-start` is executed.

The orchestrator:
1. Calls `check_updates.py` to check for updates
2. If update available and not dismissed, shows notification to user via `AskUserQuestion`
3. Provides options: "Update now", "Show changelog", "Skip this version", "Remind me later"
4. If user chooses "Update now", executes automated update
5. If user chooses "Skip this version", records dismissal

## Impact Analysis

The skill detects the following in changelogs:

### Breaking Changes
- `BREAKING:` prefix
- `BREAKING CHANGE:` prefix
- `[BREAKING]` tag
- `⚠️` warning emoji

### Migrations
- `Migration:` prefix
- `Run:` prefix
- `Required:` prefix
- `Action required:` prefix
- `[MIGRATION]` tag

### Dependency Updates
- `Package: old → new` format
- `Package: old -> new` format
- `Package old to new` format

### Security Fixes
- `Security:` prefix
- `CVE-YYYY-NNNN` identifiers
- `[SECURITY]` tag
- `🔒` lock emoji
- `Vulnerability:` prefix

## State Management

### Cache Location
- **Path**: `~/.claude/simple-memory/latest_release.json`
- **TTL**: 1 hour
- **Format**: JSON with timestamp

### Dismissal Tracking
- **Path**: `~/.claude/simple-memory/dismissed_updates.json`
- **Persistence**: Until new release or manual clear
- **Format**: JSON with version, timestamp, check count

## Update Process

When executing an update:

1. **Save State**: Record current commit SHA for rollback
2. **Fetch**: Run `git fetch --tags`
3. **Checkout**: Run `git checkout v{version}`
4. **Migrations**: Execute `.scripts/migrate-to-v{version}.sh` if exists
5. **Verify**: Check VERSION file, directories, run setup verification
6. **Rollback**: If any step fails, rollback to saved commit

## Error Handling

The skill uses **graceful degradation**:

| Error | Behavior |
|-------|----------|
| GitHub API unreachable | Log warning, return "no update" |
| Invalid VERSION file | Log error, use fallback |
| Update fails | Automatic rollback to previous version |
| Migration fails | Log warning, continue (non-critical) |

**Updates never block workflow execution.**

## Testing

Run all tests:

```bash
python3 -m pytest .claude/skills/version-checker/tests/ -v
```

Run with coverage:

```bash
python3 -m pytest .claude/skills/version-checker/tests/ \
  --cov=.claude/skills/version-checker/scripts \
  --cov-report=html
```

### Test Coverage

| Module | Coverage |
|--------|----------|
| version_comparator.py | 95%+ |
| release_fetcher.py | 90%+ |
| impact_analyzer.py | 90%+ |
| dismissal_tracker.py | 95%+ |
| update_executor.py | 85%+ |
| check_updates.py | 90%+ |

## Logging

All operations use structured logging with Loki integration:

**Labels:**
- `skill`: version-checker
- `phase`: 0
- `level`: debug/info/warning/error

**Key Events:**
- Update check started/completed
- Version comparison result
- GitHub API calls (with timing)
- Dismissal actions
- Update execution steps
- Errors and warnings

View logs in Grafana:
```
{skill="version-checker"} | json
```

## Configuration

### Check Policy

Edit `.claude/skills/version-checker/config/check_policy.yml` to configure:

- Check frequency
- Auto-update behavior
- Notification preferences

## Troubleshooting

### "No releases found"
- Check if repository has any releases
- Verify `gh` CLI is authenticated: `gh auth status`

### "GitHub API timeout"
- Check network connectivity
- GitHub may be experiencing issues

### "Update failed"
- Check logs for specific error
- Rollback should happen automatically
- Manual rollback: `git checkout {previous_commit}`

### "Cache always stale"
- Clear cache: `check_updates.py --clear-cache`
- Check system time is correct

## Dependencies

- **Python 3.11+**
- **gh CLI** (GitHub CLI for API access)
- **git** (for update operations)
- **PyYAML** (for VERSION file parsing)

## Version

**Current**: v1.8.0

## Author

SDLC Agêntico Team

## License

Same as parent project
