# Technical Plan - GitHub Metrics Collector

## Document Information

| Field | Value |
|-------|-------|
| Project | metrics-collector-20260212 |
| Version | 1.0 |
| Created | 2026-02-12 |
| Author | system-architect |
| Phase | 3 (Architecture) |

## Executive Summary

This technical plan describes the implementation approach for the GitHub Metrics Collector,
a system that extracts metrics from 2 GitHub Enterprise Cloud organizations and delivers
them to PowerBI via Import Mode (through SharePoint).

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     External Systems                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ GitHub       │  │ GitHub       │  │ SharePoint   │          │
│  │ Enterprise 1 │  │ Enterprise 2 │  │ Online       │          │
│  └──────┬───────┘  └──────┬───────┘  └──────▲───────┘          │
│         │                 │                 │                   │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │ HTTPS           │ HTTPS           │ Graph API
          │ PAT Auth        │ PAT Auth        │
          └────────┬────────┴────────┬────────┘
                   │                 │
┌──────────────────┼─────────────────┼────────────────────────────┐
│                  ▼                 │        Azure Cloud         │
│         ┌───────────────┐          │                            │
│         │Azure Functions│──────────┘                            │
│         │(Timer Trigger)│                                       │
│         └───────┬───────┘                                       │
│                 │                                                │
│    ┌────────────┼────────────┐                                  │
│    │            │            │                                  │
│    ▼            ▼            ▼                                  │
│ ┌──────┐   ┌──────┐   ┌──────────┐                             │
│ │Key   │   │Postgre│  │App       │                             │
│ │Vault │   │SQL    │  │Insights  │                             │
│ └──────┘   └──────┘   └──────────┘                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
          │
          │ Import Mode (Daily Refresh)
          ▼
┌──────────────────────────────────────────────────────────────────┐
│         ┌───────────────┐                                        │
│         │ PowerBI Online│         End Users                      │
│         └───────────────┘                                        │
└──────────────────────────────────────────────────────────────────┘
```

## Technology Choices

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Compute** | Azure Functions (Consumption) | Serverless, pay-per-execution |
| **Runtime** | Python 3.11 | GitHub API libraries, team skill |
| **Database** | PostgreSQL Flexible Server (B1ms) | Cost-effective, JSONB support |
| **Secrets** | Azure Key Vault | Secure, managed identity |
| **Monitoring** | Application Insights | Native Azure integration |
| **Export** | CSV (UTF-8 BOM) | Universal compatibility |
| **Storage** | SharePoint Online | Existing infrastructure |
| **BI** | PowerBI Online (Import Mode) | Existing platform |

## Components

### 1. Collector Service (Azure Functions)

**Purpose**: Extract data from GitHub APIs

**Functions**:

| Function | Trigger | Description |
|----------|---------|-------------|
| `main_orchestrator` | Timer (06:00 UTC) | Coordinates collection |
| `collect_copilot` | HTTP (internal) | Copilot Usage API |
| `collect_repos` | HTTP (internal) | Commits, PRs, Workflows |
| `calculate_dora` | HTTP (internal) | DORA metrics |
| `calculate_velocity` | HTTP (internal) | Velocity metrics |
| `export_csv` | HTTP (internal) | Generate CSV files |
| `upload_sharepoint` | HTTP (internal) | Upload to SharePoint |

**Dependencies**:
- `requests` or `httpx` - HTTP client
- `pandas` - Data processing
- `psycopg2` - PostgreSQL client
- `azure-identity` - Managed identity
- `azure-keyvault-secrets` - Key Vault access
- `msal` - Microsoft Graph auth

### 2. Database (PostgreSQL)

**Purpose**: Store historical data and audit trail

**Configuration**:
- SKU: Burstable B1ms (1 vCore, 2GB RAM)
- Storage: 32 GB (scalable)
- Backup: 7 days automatic retention
- SSL: Required

**Key Tables**:
- `copilot_daily_metrics` - Daily Copilot aggregates
- `copilot_user_metrics` - Per-user Copilot data
- `dora_metrics` - Weekly DORA metrics
- `velocity_metrics` - Weekly velocity metrics
- `collection_runs` - Audit trail

### 3. Export Service

**Purpose**: Generate CSV files for PowerBI

**Files Generated**:
- `copilot_metrics_YYYYMMDD.csv`
- `dora_metrics_YYYYMMDD.csv`
- `velocity_metrics_YYYYMMDD.csv`

**Format**:
- Encoding: UTF-8 with BOM
- Delimiter: Semicolon (;)
- Date format: YYYY-MM-DD

### 4. SharePoint Integration

**Purpose**: Store CSV files for PowerBI access

**Implementation**:
- Microsoft Graph API
- Application registration with delegated permissions
- Upload to document library

## NFR Approach

### Performance (NFR-PERF)

| Requirement | Approach |
|-------------|----------|
| Rate limit compliance | Client-side throttling, exponential backoff |
| Collection time < 4h | Parallel API calls, incremental collection |
| Volume 1K-100K/day | PostgreSQL indexing, batch processing |

### Security (NFR-SEC)

| Requirement | Approach |
|-------------|----------|
| Credential management | Azure Key Vault with managed identity |
| Data segregation | Column-based (enterprise_id) |
| Audit trail | collection_runs table + App Insights |
| Transport security | TLS 1.2+ for all connections |

### Availability (NFR-AVAIL)

| Requirement | Approach |
|-------------|----------|
| Retry on failure | Exponential backoff, 3 retries |
| No data loss | Transaction boundaries, idempotent writes |
| Alerting | Azure Monitor alerts |

### Scalability (NFR-SCALE)

| Requirement | Approach |
|-------------|----------|
| Add enterprises | Column-based segregation |
| Increase volume | PostgreSQL partitioning (future) |
| More repos | Pagination in API calls |

## Implementation Phases

### Phase 1: Infrastructure Setup (Sprint 1)

- [ ] Create Azure Functions App
- [ ] Create PostgreSQL Flexible Server
- [ ] Create Azure Key Vault
- [ ] Configure managed identities
- [ ] Set up Application Insights
- [ ] Create database schema

### Phase 2: Core Collection (Sprint 1-2)

- [ ] Implement Copilot metrics collection
- [ ] Implement repository metrics collection
- [ ] Implement DORA calculation
- [ ] Implement Velocity calculation
- [ ] Unit tests for collectors

### Phase 3: Export & Integration (Sprint 2)

- [ ] Implement CSV export
- [ ] Implement SharePoint upload
- [ ] Configure Timer trigger
- [ ] End-to-end testing
- [ ] PowerBI dataset setup

### Phase 4: Production Readiness (Sprint 2-3)

- [ ] Alerting configuration
- [ ] Documentation
- [ ] Runbook creation
- [ ] Security review
- [ ] Production deployment

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Copilot API deprecated April 2026 | Use new API from start, monitor announcements |
| Rate limits exceeded | Client-side throttling, distribute collection |
| PAT compromise | Key Vault, rotation every 90 days, audit logs |
| Collection timeout | Split into smaller functions, Premium plan if needed |

## Monitoring & Observability

### Metrics to Track

- Collection duration
- Records collected per run
- API calls per minute
- Error rate
- Rate limit usage

### Alerts

| Alert | Condition | Action |
|-------|-----------|--------|
| Collection failed | status = 'failed' | Notify on-call |
| Rate limit warning | usage > 80% | Notify team |
| Long collection | duration > 2 hours | Notify team |
| Export failed | SharePoint upload error | Notify on-call |

### Dashboards

- Collection status (last 7 days)
- API usage trends
- Error breakdown
- Data freshness

## Security Checklist

- [ ] No secrets in code or config files
- [ ] Key Vault with managed identity
- [ ] SSL/TLS for all connections
- [ ] Minimum privilege for PATs
- [ ] Audit logging enabled
- [ ] Secret rotation documented

## Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| Azure subscription | Platform Team | Available |
| GitHub PAT (Enterprise 1) | GitHub Admin | Pending |
| GitHub PAT (Enterprise 2) | GitHub Admin | Pending |
| SharePoint site | IT | Available |
| PowerBI workspace | BI Team | Available |

## Estimated Effort

| Component | Estimate |
|-----------|----------|
| Infrastructure setup | 4-8 hours |
| Copilot collector | 8-16 hours |
| Repository collector | 8-16 hours |
| DORA calculation | 8-16 hours |
| Velocity calculation | 8-16 hours |
| CSV export | 4-8 hours |
| SharePoint integration | 4-8 hours |
| Testing | 16-24 hours |
| Documentation | 4-8 hours |
| **Total** | **64-120 hours (8-15 days)** |

## Related Documents

- [Architecture Summary](../architecture/architecture-summary.md)
- [Component Diagram](../architecture/component-diagram.md)
- [Threat Model](../security/threat-model.yml)
- [Data Model](../data/data-model.md)
- [ADR-001: Database Selection](../decisions/ADR-001-database-selection.yml)
- [ADR-002: GitHub Authentication](../decisions/ADR-002-github-authentication.yml)
- [ADR-003: Export Format](../decisions/ADR-003-export-format.yml)
- [ADR-004: Collection Architecture](../decisions/ADR-004-collection-architecture.yml)
- [ADR-005: Data Segregation](../decisions/ADR-005-data-segregation.yml)

---

*Generated by SDLC Agentico - Phase 3 Architecture*
