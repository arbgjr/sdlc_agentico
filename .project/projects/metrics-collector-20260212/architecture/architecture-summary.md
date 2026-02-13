# Architecture Summary - GitHub Metrics Collector

## Executive Summary

This document summarizes the architecture for the GitHub Metrics Collector system,
which extracts metrics from 2 GitHub Enterprise Cloud organizations and delivers
them to PowerBI via Import Mode.

**REVISED**: Architecture changed from cloud-based (Azure Functions + PostgreSQL) to
**local-first** (Python + Task Scheduler + SQLite + OneDrive) per user constraints.

## Key Architectural Decisions

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| ADR-001 | Database | **SQLite Local** | Zero cost, no approvals, queries for DORA |
| ADR-002 | Authentication | Classic PAT | Required for Copilot enterprise endpoints |
| ADR-003 | Export Format | **CSV.GZ (GZIP)** | 80% smaller, PowerBI native support |
| ADR-004 | Collection | **Local Python + Task Scheduler** | Zero cost, works immediately |
| ADR-005 | Data Segregation | Column-based (enterprise_id) | Simple queries, one PowerBI connection |
| ADR-006 | Backup | **Daily SQLite + Weekly SQL dump** | Zero cost, OneDrive storage |

## Architecture Overview

```
GitHub Enterprise 1 ──┐
                      ├──→ Local Python Script ──→ SQLite (data/metrics.db)
GitHub Enterprise 2 ──┘         │                        │
                                │                        │
                         Windows Task                    │
                         Scheduler (8:00 AM)             │
                                │                        │
                                ▼                        │
                           CSV.GZ Export                 │
                                │                        │
                                ▼                        │
                           OneDrive ◄────────────────────┘
                                │              (daily backup)
                                ▼
                      Power Automate Trigger
                                │
                                ▼
                        PowerBI (Import Mode)
```

## Components

### 1. Local Python Script (collector.py)

- **Runtime**: Python 3.11+
- **Trigger**: Windows Task Scheduler (8:00 AM daily)
- **Location**: Corporate machine (VPN)
- **Modules**:
  - `collectors/` - GitHub API collectors
    - `copilot_collector.py` - Copilot Usage API
    - `premium_collector.py` - Premium requests
    - `repo_collector.py` - Commits, PRs, Workflows
  - `calculators/` - Metrics calculation
    - `dora_calculator.py` - DORA metrics (SQL queries)
    - `velocity_calculator.py` - Velocity metrics
  - `storage/` - Data persistence
    - `storage_manager.py` - SQLite + JSON dual storage
    - `backup_manager.py` - Backup automation
  - `export/` - Output generation
    - `csv_exporter.py` - GZIP CSV export
    - `onedrive_copier.py` - File copy to OneDrive

### 2. SQLite Database (data/metrics.db)

- **Purpose**: Historical data, queries, and audit trail
- **Size**: ~10MB/year estimated
- **Backup**: Daily copy to OneDrive + Weekly SQL dump
- **Tables**:
  - `copilot_daily_metrics` - Org-level Copilot usage
  - `copilot_user_metrics` - Per-user Copilot usage
  - `copilot_premium_requests` - Premium vs standard requests
  - `dora_metrics` - DORA metrics per repo
  - `velocity_metrics` - Velocity metrics per developer
  - `collection_runs` - Audit trail

### 3. JSON Files (data/output/)

- **Purpose**: Backup and debugging
- **Retention**: 90 days
- **Files**: Raw API responses per collection

### 4. OneDrive

- **Purpose**: Intermediate storage for PowerBI
- **Files**: Daily CSV.GZ exports + SQLite backups
- **Integration**: shutil.copy2 (direct file copy)

### 5. PowerBI Online

- **Mode**: Import (NOT Direct Query)
- **Refresh**: Daily scheduled via Power Automate trigger
- **Dashboards**: Copilot adoption, Premium usage, DORA metrics, Velocity metrics

## Data Flow

1. **08:00 Local**: Task Scheduler triggers collector.py
2. **08:00-08:30**: Collect data from GitHub APIs (2 enterprises)
3. **08:30-08:35**: Calculate DORA and Velocity metrics (SQL queries)
4. **08:35-08:40**: Export CSV.GZ + backup SQLite to OneDrive
5. **08:40**: Power Automate detects new files, triggers refresh
6. **09:00**: PowerBI import completes

## Security Architecture

### Threat Model Summary

| Category | Threats | Critical Mitigations |
|----------|---------|---------------------|
| **Spoofing** | Stolen PAT | Environment variable + 90-day rotation |
| **Tampering** | Data modification | SSL/TLS + local-only access |
| **Repudiation** | No audit trail | collection_runs table + JSON files |
| **Info Disclosure** | PAT exposure | Never log secrets, env var only |
| **DoS** | Rate limits | Backoff + retry decorator |
| **Elevation** | Excessive scopes | Minimum privilege PAT |

### Security Requirements

1. PAT stored in environment variable (not code)
2. SSL/TLS for all GitHub API connections
3. Audit trail for all collections (SQLite + JSON)
4. Minimum privilege for PATs (read-only scopes)
5. 90-day credential rotation
6. Local execution only (no cloud exposure)

## Cost Estimate (Monthly)

| Component | Cost |
|-----------|------|
| Python Script | $0 |
| SQLite | $0 |
| Task Scheduler | $0 |
| OneDrive | $0 (corporate) |
| **Total** | **$0/month** |

**Savings vs. Original Architecture**: $20/month (~$240/year)

## Non-Functional Requirements

| Requirement | Target | Architecture Support |
|-------------|--------|---------------------|
| Availability | 99% | Machine uptime (corporate 24/7) |
| Collection Time | < 1 hour | Sequential API calls + local processing |
| Data Retention | 3 years | SQLite continuous + JSON 90 days |
| Rate Limits | 5000 req/hr | Retry decorator with backoff |
| Backup | Daily | SQLite copy + weekly SQL dump |

## Operational Procedures

### Daily Operations (Automated)

1. Task Scheduler triggers at 8:00 AM
2. Collector runs with retry logic
3. Export CSV.GZ to OneDrive
4. Backup SQLite to OneDrive
5. Cleanup old files (JSON > 90d, logs > 30d)

### Weekly Operations (Automated)

1. SQL dump on Sunday 23:00
2. Upload dump to OneDrive

### Manual Operations

| Task | Frequency | Procedure |
|------|-----------|-----------|
| PAT Rotation | Every 90 days | Update env variable, test collection |
| Add new org | As needed | Update config.yml, test collection |
| Debug failures | As needed | Check logs, JSON files, collection_runs |

## Future Considerations

1. **More enterprises**: Just add PAT and config, no architecture change
2. **Real-time**: Would require webhook + Azure Functions (major change)
3. **Multi-machine**: Could run on multiple machines with file-based locking
4. **Cloud migration**: If needed later, SQLite easily exports to PostgreSQL

## Related Documents

- [Component Diagram](component-diagram.md)
- [Threat Model](threat-model.yml)
- [Data Model](../data/data-model.md)
- [ADR-001: Database Selection - SQLite](../decisions/ADR-001-database-selection.yml)
- [ADR-002: GitHub Authentication](../decisions/ADR-002-github-authentication.yml)
- [ADR-003: Export Format - GZIP](../decisions/ADR-003-export-format.yml)
- [ADR-004: Collection Architecture - Local](../decisions/ADR-004-collection-architecture.yml)
- [ADR-005: Data Segregation](../decisions/ADR-005-data-segregation.yml)
- [ADR-006: Backup Strategy](../decisions/ADR-006-backup-strategy.yml)

---

*Revised: 2026-02-12 - Changed to local-first architecture per user feedback*

*Generated by SDLC Agentico - Phase 3 Architecture*
