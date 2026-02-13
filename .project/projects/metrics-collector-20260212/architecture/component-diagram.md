# Component Diagram - GitHub Metrics Collector

## System Context (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              External Systems                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ GitHub           │  │ GitHub           │  │ SharePoint       │          │
│  │ Enterprise 1     │  │ Enterprise 2     │  │ Online           │          │
│  │                  │  │                  │  │                  │          │
│  │ - Copilot API    │  │ - Copilot API    │  │ - Document       │          │
│  │ - REST API       │  │ - REST API       │  │   Library        │          │
│  │ - GraphQL API    │  │ - GraphQL API    │  │                  │          │
│  └────────┬─────────┘  └────────┬─────────┘  └────────▲─────────┘          │
│           │                     │                     │                     │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────┘
            │                     │                     │
            │ PAT Auth            │ PAT Auth            │ Graph API
            │                     │                     │
┌───────────┼─────────────────────┼─────────────────────┼─────────────────────┐
│           ▼                     ▼                     │                     │
│  ┌────────────────────────────────────────┐          │                     │
│  │       GitHub Metrics Collector         │          │                     │
│  │       (Azure Functions)                │──────────┘                     │
│  │                                        │                                │
│  │  ┌─────────────┐  ┌─────────────┐     │                                │
│  │  │ Copilot     │  │ Repo        │     │                                │
│  │  │ Collector   │  │ Collector   │     │                                │
│  │  └──────┬──────┘  └──────┬──────┘     │                                │
│  │         │                │            │                                │
│  │         ▼                ▼            │                                │
│  │  ┌─────────────────────────────┐      │                                │
│  │  │     DORA Calculator         │      │                                │
│  │  └──────────────┬──────────────┘      │                                │
│  │                 │                     │                                │
│  │                 ▼                     │                                │
│  │  ┌─────────────────────────────┐      │                                │
│  │  │     CSV Exporter            │──────┘                                │
│  │  └─────────────────────────────┘                                       │
│  └────────────────────────────────────────┘                                │
│                    │                                                       │
│                    │ SQL                                                   │
│                    ▼                                                       │
│  ┌────────────────────────────────────────┐                                │
│  │       PostgreSQL                       │                                │
│  │       (Azure Flexible Server)          │                                │
│  │                                        │                                │
│  │  - Historico de coletas                │                                │
│  │  - Audit trail                         │                                │
│  │  - Segregacao por enterprise_id        │                                │
│  └────────────────────────────────────────┘                                │
│                                                                             │
│                          Azure Cloud                                        │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            │ Import Mode (Daily Refresh)
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌────────────────────────────────────────┐                                │
│  │       PowerBI Online                   │                                │
│  │                                        │                                │
│  │  - Dashboards Copilot                  │                                │
│  │  - Dashboards DORA                     │                                │
│  │  - Dashboards Velocity                 │                                │
│  └────────────────────────────────────────┘                                │
│                          End Users                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Container Diagram (C4 Level 2)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     GitHub Metrics Collector System                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    Azure Functions App                              │    │
│  │                    (Consumption Plan)                               │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │    │
│  │  │ TimerTrigger    │  │ collect_copilot │  │ collect_repos   │    │    │
│  │  │ (06:00 UTC)     │─▶│                 │─▶│                 │    │    │
│  │  │                 │  │ - Usage API     │  │ - Commits       │    │    │
│  │  │ Orchestrator    │  │ - Metrics/day   │  │ - PRs           │    │    │
│  │  │                 │  │ - Per-user      │  │ - Workflows     │    │    │
│  │  └─────────────────┘  └─────────────────┘  └────────┬────────┘    │    │
│  │                                                      │            │    │
│  │                                                      ▼            │    │
│  │                       ┌─────────────────┐  ┌─────────────────┐    │    │
│  │                       │ calculate_dora  │  │ export_csv      │    │    │
│  │                       │                 │─▶│                 │    │    │
│  │                       │ - Lead Time     │  │ - Generate CSV  │    │    │
│  │                       │ - Deploy Freq   │  │ - Upload        │    │    │
│  │                       │ - MTTR          │  │   SharePoint    │    │    │
│  │                       │ - CFR           │  │                 │    │    │
│  │                       └─────────────────┘  └─────────────────┘    │    │
│  │                                                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐                          │
│  │ Azure Key Vault     │  │ Application         │                          │
│  │                     │  │ Insights            │                          │
│  │ - GitHub PATs       │  │                     │                          │
│  │ - DB Connection     │  │ - Logs              │                          │
│  │ - SharePoint creds  │  │ - Metrics           │                          │
│  │                     │  │ - Alerts            │                          │
│  └─────────────────────┘  └─────────────────────┘                          │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    PostgreSQL Flexible Server                       │    │
│  │                    (Burstable B1ms)                                 │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │    │
│  │  │ copilot_     │  │ dora_        │  │ velocity_    │             │    │
│  │  │ metrics      │  │ metrics      │  │ metrics      │             │    │
│  │  │              │  │              │  │              │             │    │
│  │  │ enterprise_id│  │ enterprise_id│  │ enterprise_id│             │    │
│  │  │ metric_date  │  │ metric_date  │  │ metric_date  │             │    │
│  │  │ ...          │  │ ...          │  │ ...          │             │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │    │
│  │                                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐                               │    │
│  │  │ collection_  │  │ audit_log    │                               │    │
│  │  │ runs         │  │              │                               │    │
│  │  │              │  │ operation    │                               │    │
│  │  │ status       │  │ timestamp    │                               │    │
│  │  │ duration     │  │ details      │                               │    │
│  │  └──────────────┘  └──────────────┘                               │    │
│  │                                                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Daily Collection Flow                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  06:00 UTC                                                                  │
│      │                                                                      │
│      ▼                                                                      │
│  ┌──────────┐                                                               │
│  │ Timer    │                                                               │
│  │ Trigger  │                                                               │
│  └────┬─────┘                                                               │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ 1. Collect Copilot Metrics                                        │      │
│  │    ├─ GET /enterprises/{enterprise}/copilot/usage                 │      │
│  │    ├─ For each enterprise (2)                                     │      │
│  │    └─ Store in PostgreSQL (copilot_metrics)                       │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ 2. Collect Repository Metrics                                     │      │
│  │    ├─ GET /repos/{owner}/{repo}/commits                           │      │
│  │    ├─ GET /repos/{owner}/{repo}/pulls                             │      │
│  │    ├─ GET /repos/{owner}/{repo}/actions/workflows                 │      │
│  │    ├─ For each active repository                                  │      │
│  │    └─ Store in PostgreSQL (commits, pull_requests, workflows)     │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ 3. Calculate DORA Metrics                                         │      │
│  │    ├─ Lead Time = deploy_time - first_commit_time                 │      │
│  │    ├─ Deploy Frequency = count(deploys) / period                  │      │
│  │    ├─ MTTR = avg(incident_resolution_time)                        │      │
│  │    ├─ Change Failure Rate = failed_deploys / total_deploys        │      │
│  │    └─ Store in PostgreSQL (dora_metrics)                          │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ 4. Calculate Velocity Metrics                                     │      │
│  │    ├─ Commit frequency per developer                              │      │
│  │    ├─ PR throughput per team                                      │      │
│  │    ├─ Review time (PR open → merged)                              │      │
│  │    ├─ Code churn (lines added/removed)                            │      │
│  │    └─ Store in PostgreSQL (velocity_metrics)                      │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ 5. Export to CSV                                                  │      │
│  │    ├─ Generate copilot_metrics_YYYYMMDD.csv                       │      │
│  │    ├─ Generate dora_metrics_YYYYMMDD.csv                          │      │
│  │    ├─ Generate velocity_metrics_YYYYMMDD.csv                      │      │
│  │    └─ UTF-8 BOM, semicolon delimiter                              │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ 6. Upload to SharePoint                                           │      │
│  │    ├─ Microsoft Graph API                                         │      │
│  │    ├─ PUT /sites/{site}/drive/root:/{path}:/content               │      │
│  │    └─ Overwrite daily files                                       │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ 7. Log Collection Run                                             │      │
│  │    ├─ Record in collection_runs table                             │      │
│  │    ├─ Status: success/partial/failed                              │      │
│  │    ├─ Duration, records collected                                 │      │
│  │    └─ Send alert if failed                                        │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ~06:30 UTC (estimated completion)                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          PowerBI Refresh Flow                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  08:00 UTC (configurable)                                                   │
│      │                                                                      │
│      ▼                                                                      │
│  ┌──────────┐     ┌──────────────┐     ┌────────────────┐                  │
│  │ PowerBI  │────▶│ SharePoint   │────▶│ CSV Files      │                  │
│  │ Refresh  │     │ Connector    │     │ (Import Mode)  │                  │
│  │ Schedule │     │              │     │                │                  │
│  └──────────┘     └──────────────┘     └────────────────┘                  │
│                                                                             │
│  Dashboards updated with previous day's data                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Network Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Network Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                           Internet                                          │
│                              │                                              │
│           ┌──────────────────┼──────────────────┐                          │
│           │                  │                  │                          │
│           ▼                  ▼                  ▼                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                    │
│  │ GitHub       │   │ GitHub       │   │ Microsoft    │                    │
│  │ Enterprise 1 │   │ Enterprise 2 │   │ Graph API    │                    │
│  │ api.github   │   │ api.github   │   │ (SharePoint) │                    │
│  │ .com         │   │ .com         │   │              │                    │
│  └──────────────┘   └──────────────┘   └──────────────┘                    │
│           │                  │                  │                          │
│           │ HTTPS/443        │ HTTPS/443        │ HTTPS/443                │
│           │ PAT Auth         │ PAT Auth         │ OAuth2                   │
│           │                  │                  │                          │
│           └──────────────────┼──────────────────┘                          │
│                              │                                              │
│                              ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                     Azure Virtual Network                         │      │
│  │                     (Optional - for enhanced security)            │      │
│  │                                                                   │      │
│  │  ┌─────────────────────────────────────────────────────────┐     │      │
│  │  │                 Azure Functions Subnet                   │     │      │
│  │  │                                                         │     │      │
│  │  │  ┌───────────────────────────────────────────────────┐  │     │      │
│  │  │  │ Azure Functions App                               │  │     │      │
│  │  │  │ (metrics-collector-func)                          │  │     │      │
│  │  │  │                                                   │  │     │      │
│  │  │  │ Outbound: GitHub APIs, MS Graph                   │  │     │      │
│  │  │  │ Inbound: None (Timer triggered)                   │  │     │      │
│  │  │  └───────────────────────────────────────────────────┘  │     │      │
│  │  │                                                         │     │      │
│  │  └─────────────────────────────────────────────────────────┘     │      │
│  │                              │                                   │      │
│  │                              │ Private Endpoint                  │      │
│  │                              ▼ (PostgreSQL)                      │      │
│  │  ┌─────────────────────────────────────────────────────────┐     │      │
│  │  │                 Database Subnet                          │     │      │
│  │  │                                                         │     │      │
│  │  │  ┌───────────────────────────────────────────────────┐  │     │      │
│  │  │  │ PostgreSQL Flexible Server                        │  │     │      │
│  │  │  │ (metrics-collector-db)                            │  │     │      │
│  │  │  │                                                   │  │     │      │
│  │  │  │ Port: 5432                                        │  │     │      │
│  │  │  │ Firewall: Azure services only                     │  │     │      │
│  │  │  └───────────────────────────────────────────────────┘  │     │      │
│  │  │                                                         │     │      │
│  │  └─────────────────────────────────────────────────────────┘     │      │
│  │                                                                   │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                     Azure Key Vault                               │      │
│  │                     (metrics-collector-kv)                        │      │
│  │                                                                   │      │
│  │  Secrets:                                                         │      │
│  │  - GITHUB_PAT_ENTERPRISE_1                                        │      │
│  │  - GITHUB_PAT_ENTERPRISE_2                                        │      │
│  │  - POSTGRESQL_CONNECTION_STRING                                   │      │
│  │  - SHAREPOINT_CLIENT_SECRET                                       │      │
│  │                                                                   │      │
│  │  Access: Managed Identity (Functions App)                         │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Compute** | Azure Functions (Consumption) | Serverless, pay-per-execution, native timer trigger |
| **Runtime** | Python 3.11 | GitHub API libraries available, team familiarity |
| **Database** | PostgreSQL Flexible Server | Cost-effective, JSONB support, no Direct Query needed |
| **Secrets** | Azure Key Vault | Secure secret storage, managed identity access |
| **Monitoring** | Application Insights | Native Azure integration, alerts, dashboards |
| **Export** | CSV (UTF-8 BOM) | Universal compatibility, PowerBI import, debug-friendly |
| **Storage** | SharePoint Online | Existing infrastructure, PowerBI connector |
| **BI** | PowerBI Online (Import Mode) | Existing platform, scheduled refresh |

## Architecture Decision Records

| ADR | Title | Decision |
|-----|-------|----------|
| ADR-001 | Database Selection | PostgreSQL Flexible Server |
| ADR-002 | GitHub Authentication | Classic PAT (required for Copilot API) |
| ADR-003 | Export Format | CSV with UTF-8 BOM, semicolon delimiter |
| ADR-004 | Collection Architecture | Azure Functions Timer Trigger |
| ADR-005 | Data Segregation | Column-based (enterprise_id) |

---

*Generated by SDLC Agentico - Phase 3 Architecture*
