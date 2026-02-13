# Data Model - GitHub Metrics Collector

## Overview

This document describes the data model for the GitHub Metrics Collector system.
Data is stored in **SQLite local** (data/metrics.db) and exported daily to **CSV.GZ** for PowerBI Import Mode via OneDrive.

**REVISED**: Changed from PostgreSQL cloud to SQLite local per user feedback (ADR-001 v2).

**Data Segregation Strategy**: Column-based with `enterprise_id` (ADR-005)

## Database: SQLite Local

- **File**: `data/metrics.db`
- **Version**: SQLite 3.x (built-in Python)
- **Backup**: Daily to OneDrive + Weekly SQL dump (ADR-006)

## Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SQLite Database                                    │
│                        (data/metrics.db)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐         ┌─────────────────────┐                   │
│  │   organizations     │         │   repositories      │                   │
│  ├─────────────────────┤         ├─────────────────────┤                   │
│  │ PK id (INTEGER)     │◄───────┐│ PK id (INTEGER)     │                   │
│  │    enterprise_id    │        ││    enterprise_id    │                   │
│  │    github_org_id    │        ││ FK org_id           │───────────────────│
│  │    github_org_login │        ││    name             │                   │
│  │    display_name     │        ││    full_name        │                   │
│  │    created_at       │        ││    default_branch   │                   │
│  └─────────────────────┘        ││    is_active        │                   │
│           │                     │└─────────────────────┘                   │
│           │                     │         │                                │
│           ▼                     │         ▼                                │
│  ┌─────────────────────┐        │┌─────────────────────┐                   │
│  │ copilot_daily_      │        ││ commits             │                   │
│  │ metrics             │        │├─────────────────────┤                   │
│  ├─────────────────────┤        ││ PK sha (TEXT)       │                   │
│  │ PK id (INTEGER)     │        ││    enterprise_id    │                   │
│  │    enterprise_id    │        ││ FK repo_id          │                   │
│  │    org_id           │────────┘│    author_login     │                   │
│  │    metric_date      │         │    committed_at     │                   │
│  │    total_active_    │         │    lines_added      │                   │
│  │      users          │         │    lines_deleted    │                   │
│  │    acceptance_rate  │         └─────────────────────┘                   │
│  └─────────────────────┘                  │                                │
│           │                               │                                │
│           ▼                               ▼                                │
│  ┌─────────────────────┐         ┌─────────────────────┐                   │
│  │ copilot_user_       │         │ pull_requests       │                   │
│  │ metrics             │         ├─────────────────────┤                   │
│  ├─────────────────────┤         │ PK id (INTEGER)     │                   │
│  │ PK id (INTEGER)     │         │    enterprise_id    │                   │
│  │    enterprise_id    │         │ FK repo_id          │                   │
│  │    org_id           │         │    number           │                   │
│  │    metric_date      │         │    author_login     │                   │
│  │    github_user_id   │         │    created_at       │                   │
│  │    github_login     │         │    merged_at        │                   │
│  │    suggestions_     │         │    state            │                   │
│  │      shown          │         └─────────────────────┘                   │
│  │    acceptance_rate  │                                                   │
│  └─────────────────────┘                                                   │
│           │                                                                │
│           ▼                                                                │
│  ┌─────────────────────┐                                                   │
│  │ copilot_premium_    │                                                   │
│  │ requests            │                                                   │
│  ├─────────────────────┤                                                   │
│  │ PK id (INTEGER)     │                                                   │
│  │    enterprise_id    │                                                   │
│  │    org_id           │                                                   │
│  │    metric_date      │                                                   │
│  │    github_user_id   │                                                   │
│  │    premium_requests │                                                   │
│  │    standard_requests│                                                   │
│  │    total_tokens     │                                                   │
│  │    model_used       │                                                   │
│  └─────────────────────┘                                                   │
│                                                                             │
│  ┌─────────────────────┐         ┌─────────────────────┐                   │
│  │ dora_metrics        │         │ velocity_metrics    │                   │
│  ├─────────────────────┤         ├─────────────────────┤                   │
│  │ PK id (INTEGER)     │         │ PK id (INTEGER)     │                   │
│  │    enterprise_id    │         │    enterprise_id    │                   │
│  │ FK repo_id          │         │ FK repo_id          │                   │
│  │    week_start       │         │    week_start       │                   │
│  │    deploy_freq      │         │    commits_count    │                   │
│  │    lead_time_hours  │         │    prs_merged       │                   │
│  │    mttr_hours       │         │    avg_review_time  │                   │
│  │    change_failure_  │         │    code_churn_rate  │                   │
│  │      rate           │         │    active_devs      │                   │
│  └─────────────────────┘         └─────────────────────┘                   │
│                                                                             │
│  ┌─────────────────────┐                                                   │
│  │ collection_runs     │                                                   │
│  ├─────────────────────┤                                                   │
│  │ PK id (INTEGER)     │                                                   │
│  │    enterprise_id    │                                                   │
│  │    started_at       │                                                   │
│  │    completed_at     │                                                   │
│  │    status           │                                                   │
│  │    records_count    │                                                   │
│  │    error_message    │                                                   │
│  └─────────────────────┘                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## SQLite Schema (DDL)

```sql
-- Organizations
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enterprise_id TEXT NOT NULL,
    github_org_id INTEGER NOT NULL,
    github_org_login TEXT NOT NULL UNIQUE,
    display_name TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_org_enterprise ON organizations(enterprise_id);

-- Repositories
CREATE TABLE repositories (
    id INTEGER PRIMARY KEY,  -- GitHub repo ID
    enterprise_id TEXT NOT NULL,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    full_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    is_active INTEGER NOT NULL DEFAULT 1,
    first_seen_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_activity_at TEXT
);
CREATE INDEX idx_repo_enterprise ON repositories(enterprise_id);

-- Copilot Daily Metrics
CREATE TABLE copilot_daily_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enterprise_id TEXT NOT NULL,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    metric_date TEXT NOT NULL,  -- YYYY-MM-DD
    total_active_users INTEGER,
    total_suggestions_shown INTEGER,
    total_suggestions_accepted INTEGER,
    acceptance_rate REAL,  -- 0.0 to 1.0
    collected_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(enterprise_id, metric_date)
);
CREATE INDEX idx_copilot_daily_date ON copilot_daily_metrics(metric_date);

-- Copilot User Metrics
CREATE TABLE copilot_user_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enterprise_id TEXT NOT NULL,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    metric_date TEXT NOT NULL,
    github_user_id INTEGER NOT NULL,
    github_login TEXT NOT NULL,
    suggestions_shown INTEGER,
    suggestions_accepted INTEGER,
    acceptance_rate REAL,
    lines_suggested INTEGER,
    lines_accepted INTEGER,
    collected_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(enterprise_id, metric_date, github_user_id)
);
CREATE INDEX idx_copilot_user_date ON copilot_user_metrics(metric_date);

-- Copilot Premium Requests
CREATE TABLE copilot_premium_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enterprise_id TEXT NOT NULL,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    metric_date TEXT NOT NULL,
    github_user_id INTEGER,  -- NULL = org aggregate
    github_login TEXT,
    premium_requests_count INTEGER,
    standard_requests_count INTEGER,
    total_requests_count INTEGER,
    total_tokens_consumed INTEGER,
    model_used TEXT,  -- gpt-4, claude-3, etc.
    premium_percentage REAL,  -- (premium/total)*100
    collected_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(enterprise_id, metric_date, github_user_id)
);
CREATE INDEX idx_copilot_premium_date ON copilot_premium_requests(metric_date);

-- DORA Metrics
CREATE TABLE dora_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enterprise_id TEXT NOT NULL,
    repo_id INTEGER NOT NULL REFERENCES repositories(id),
    week_start TEXT NOT NULL,  -- YYYY-MM-DD (Monday)
    deployment_frequency REAL,
    deployment_freq_rating TEXT,  -- Elite/High/Medium/Low
    lead_time_hours REAL,
    lead_time_p50_hours REAL,
    lead_time_p95_hours REAL,
    lead_time_rating TEXT,
    change_failure_rate REAL,
    change_failure_rating TEXT,
    mttr_hours REAL,
    mttr_rating TEXT,
    calculated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(enterprise_id, repo_id, week_start)
);
CREATE INDEX idx_dora_week ON dora_metrics(week_start);

-- Velocity Metrics
CREATE TABLE velocity_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enterprise_id TEXT NOT NULL,
    repo_id INTEGER REFERENCES repositories(id),  -- NULL = aggregated
    week_start TEXT NOT NULL,
    commits_count INTEGER,
    commits_per_dev_day REAL,
    prs_opened INTEGER,
    prs_merged INTEGER,
    avg_review_time_hours REAL,
    p50_review_time_hours REAL,
    p95_review_time_hours REAL,
    lines_added INTEGER,
    lines_deleted INTEGER,
    code_churn_rate REAL,
    active_developers INTEGER,
    calculated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(enterprise_id, repo_id, week_start)
);
CREATE INDEX idx_velocity_week ON velocity_metrics(week_start);

-- Collection Runs (Audit)
CREATE TABLE collection_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enterprise_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',  -- running/success/failed/partial
    metrics_type TEXT NOT NULL,  -- copilot/dora/velocity/all
    records_collected INTEGER DEFAULT 0,
    error_message TEXT
);
CREATE INDEX idx_collection_started ON collection_runs(started_at);
```

## CSV Export Schema (GZIP Compressed)

All exports use: UTF-8 BOM, semicolon delimiter, GZIP compression (.csv.gz)

### copilot_metrics_YYYYMMDD.csv.gz

```csv
enterprise_id;org_login;metric_date;total_active_users;total_suggestions_shown;total_suggestions_accepted;acceptance_rate
enterprise-1;SU-AIOFFICE;2026-02-11;42;15234;11876;0.7796
enterprise-2;OtherOrg;2026-02-11;38;12456;9876;0.7928
```

### copilot_premium_requests_YYYYMMDD.csv.gz

```csv
enterprise_id;org_login;metric_date;github_login;premium_requests_count;standard_requests_count;total_requests_count;total_tokens_consumed;model_used;premium_percentage
enterprise-1;SU-AIOFFICE;2026-02-11;;1250;8750;10000;125000;gpt-4;12.50
enterprise-1;SU-AIOFFICE;2026-02-11;developer1;150;450;600;7500;gpt-4;25.00
enterprise-1;SU-AIOFFICE;2026-02-11;developer2;50;550;600;6000;claude-3;8.33
```

**Notes on Premium Requests CSV**:
- First row with empty github_login = org-level aggregate
- Subsequent rows = per-user breakdown
- premium_percentage = (premium_requests_count / total_requests_count) * 100
- model_used = most frequently used premium model that day

### dora_metrics_YYYYMMDD.csv.gz

```csv
enterprise_id;repo_name;week_start;deployment_frequency;deployment_freq_rating;lead_time_hours;lead_time_rating;change_failure_rate;change_failure_rating;mttr_hours;mttr_rating
enterprise-1;service-a;2026-02-10;2.5;Elite;4.2;Elite;0.05;Elite;0.8;Elite
enterprise-1;service-b;2026-02-10;0.8;High;12.5;High;0.12;Medium;2.5;High
```

### velocity_metrics_YYYYMMDD.csv.gz

```csv
enterprise_id;repo_name;week_start;commits_count;prs_merged;avg_review_time_hours;active_developers;code_churn_rate
enterprise-1;service-a;2026-02-10;45;12;3.5;8;0.15
enterprise-1;service-b;2026-02-10;32;8;6.2;5;0.22
```

## Data Retention (ADR-006)

| Data Type | Local Retention | OneDrive Retention |
|-----------|-----------------|-------------------|
| SQLite database | Continuous | 30 days (daily backup) |
| SQL dumps | 30 days | 30 days |
| JSON raw files | 90 days | N/A |
| CSV.GZ exports | N/A | 90 days |
| Logs | 30 days | N/A |

## PowerBI Integration

**Mode**: Import (NOT Direct Query)

**Data Flow**:
1. Windows Task Scheduler triggers collector.py (8:00 AM local)
2. Data collected from GitHub APIs (2 enterprises)
3. Data stored in SQLite (historical + audit)
4. DORA/Velocity calculated via SQL queries
5. Export to CSV.GZ files
6. Copy to OneDrive via shutil.copy2
7. Power Automate trigger on new file
8. PowerBI scheduled refresh imports CSV.GZ

**Recommended Refresh Schedule**: Daily at 10:00 AM (after collection completes ~09:00 AM)

**Tables for Import**:
- `copilot_metrics_YYYYMMDD.csv.gz` - Copilot adoption metrics
- `copilot_premium_requests_YYYYMMDD.csv.gz` - Premium vs standard requests
- `dora_metrics_YYYYMMDD.csv.gz` - DORA metrics per repository
- `velocity_metrics_YYYYMMDD.csv.gz` - Velocity metrics per team

## File Structure

```
data/
├── metrics.db              # SQLite database (main)
├── output/                 # JSON raw files (90 days retention)
│   ├── copilot_2026-02-12.json
│   ├── dora_2026-02-12.json
│   └── velocity_2026-02-12.json
├── export/                 # CSV.GZ exports (copied to OneDrive)
│   ├── copilot_metrics_20260212.csv.gz
│   ├── copilot_premium_requests_20260212.csv.gz
│   ├── dora_metrics_20260212.csv.gz
│   └── velocity_metrics_20260212.csv.gz
├── backup/                 # Local backups
│   ├── metrics_20260212.db
│   └── metrics_dump_20260209.sql.gz
└── logs/                   # Log files (30 days retention)
    └── collector_20260212.log
```

---

*Updated: 2026-02-12 - Revised for SQLite local architecture (ADR-001 v2)*

*Generated by SDLC Agentico - Phase 3 Architecture*
