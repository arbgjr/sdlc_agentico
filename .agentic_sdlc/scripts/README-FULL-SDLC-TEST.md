# Full SDLC End-to-End Test

## Overview

**`test-framework-full-sdlc.sh`** simulates a complete SDLC workflow through all 9 phases (0-8) with realistic project artifacts, validating backend, frontend, IaC, QA, and DevOps capabilities.

## Test Project: "E-Commerce API"

**Architecture:** Microservices with React frontend, deployed to Kubernetes

**Tech Stack:**
- Backend: Python + FastAPI
- Frontend: React + Playwright E2E
- Database: PostgreSQL (Azure)
- Infrastructure: Terraform + Azure Kubernetes Service (AKS)
- Testing: pytest, trivy, k6
- CI/CD: GitHub Actions
- Monitoring: Grafana + Prometheus

## What It Tests

### Phase 0 - Intake & Preparation
- Business requirements documentation
- Stakeholder identification
- Success criteria definition

### Phase 1 - Discovery
- Tech stack analysis (Python, FastAPI, React, PostgreSQL, K8s)
- External dependencies mapping
- Integration requirements

### Phase 2 - Requirements Analysis
- User stories with acceptance criteria
  - US-001: User can browse products
  - US-002: User can add items to cart

### Phase 3 - Architecture Design
- **ADR-001**: Use microservices architecture
- **Architecture Diagram**: Mermaid diagram of services
- **Threat Model**: STRIDE analysis with 3 threats
  - SQL injection in product catalog
  - Session hijacking
  - DDOS on API gateway

### Phase 4 - Delivery Planning
- Sprint plan with tasks
- Story point estimation
- Dependency mapping
- Task breakdown:
  - TASK-001: Setup PostgreSQL schemas (3 points)
  - TASK-002: Implement Catalog Service API (8 points)
  - TASK-003: Build React frontend (5 points)
  - TASK-004: Deploy to AKS (5 points)

### Phase 5 - Implementation
#### Backend Code
```python
from fastapi import FastAPI
app = FastAPI(title="Catalog Service")

@app.get("/api/v1/products")
async def list_products(category_id: int = None):
    return [{"id": 1, "name": "Laptop", "price": 999.99}]
```

#### Infrastructure as Code (Terraform)
```hcl
resource "azurerm_kubernetes_cluster" "ecommerce" {
  name     = "ecommerce-aks"
  location = "East US"
  default_node_pool {
    node_count = 3
    vm_size    = "Standard_D2_v2"
  }
}
```

#### Kubernetes Manifests
- Deployment for Catalog Service
- Service (ClusterIP)
- ConfigMap for environment variables

### Phase 6 - Quality Assurance
#### Unit Tests (pytest)
```python
def test_list_products_success():
    response = client.get("/api/v1/products?category_id=1")
    assert response.status_code == 200
```

#### Security Scan (trivy)
- Vulnerability scanning: 0 critical, 0 high
- Dependency analysis
- Container image scanning

#### E2E Tests (Playwright)
```javascript
test('user can browse products', async ({ page }) => {
  await page.goto('http://localhost:3000/products');
  await expect(page.locator('h1')).toContainText('Products');
});
```

#### Load Testing (k6)
- Test results: p95 < 200ms, success rate 100%
- 100 VUs, 10 minute duration

### Phase 7 - Release & Deployment
#### CI/CD Pipeline (GitHub Actions)
```yaml
name: Deploy to Production
on:
  push:
    tags:
      - 'v*'
jobs:
  deploy:
    steps:
      - Build Docker image
      - Security scan
      - Deploy to Kubernetes
```

#### Release Notes
- Version 1.0.0
- Features list
- Breaking changes
- Migration guide

### Phase 8 - Operations & Monitoring
#### Grafana Dashboard
- Request Rate panel
- Error Rate panel
- Response Time (p95) panel

#### Operations Runbook
- Deployment procedures
- Rollback procedures
- Incident response
- Health checks

## Usage

### Run Full SDLC Test

```bash
./.agentic_sdlc/scripts/test-framework-full-sdlc.sh
```

**Duration:** ~1 second

**Exit Codes:**
- `0` - All tests passed
- `1` - One or more tests failed (artifacts preserved)

### Expected Output

```
╔═══════════════════════════════════════════════════════╗
║   SDLC Agêntico - Full SDLC E2E Test (9 Phases)      ║
╚═══════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Phase 0: Intake & Preparation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PASS: Intake brief created

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              FULL SDLC TEST SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All phases PASSED

Complete SDLC validation:
  ✅ Phase 0 - Intake (business requirements)
  ✅ Phase 1 - Discovery (tech stack: Python/FastAPI/React/K8s)
  ✅ Phase 2 - Requirements (user stories)
  ✅ Phase 3 - Architecture (ADRs, diagrams, threat model)
  ✅ Phase 4 - Planning (sprint plan, tasks)
  ✅ Phase 5 - Implementation (backend code, IaC, K8s manifests)
  ✅ Phase 6 - Quality (unit tests, security scan, E2E, load test)
  ✅ Phase 7 - Release (CI/CD pipeline, release notes)
  ✅ Phase 8 - Operations (monitoring, runbooks)

Validated capabilities:
  ✅ Backend: FastAPI REST API
  ✅ Frontend: React + Playwright E2E
  ✅ IaC: Terraform (AKS, PostgreSQL)
  ✅ QA: pytest, trivy, k6
  ✅ DevOps: GitHub Actions, Kubernetes
  ✅ Operations: Grafana, Prometheus, runbooks

✅ Cleanup complete
```

### Logging to Loki

All test steps are logged with:
- `skill=framework-full-sdlc-test`
- `phase=0` (test phase, not SDLC phase)
- Correlation ID for tracing
- Test step details in extra fields

**Grafana Query:**
```logql
{app="sdlc-agentico", skill="framework-full-sdlc-test"}
```

## Integration with CI/CD

Add to GitHub Actions:

```yaml
- name: Run Full SDLC Test
  run: |
    ./.agentic_sdlc/scripts/test-framework-full-sdlc.sh
```

## Troubleshooting

### Test Fails

If tests fail, artifacts are preserved in `/tmp/sdlc-full-test-XXXXXX`. Check:

```bash
ls /tmp/sdlc-full-test-*/.project/phases/
cat /tmp/sdlc-full-test-*/src/backend/catalog_service.py
cat /tmp/sdlc-full-test-*/src/infrastructure/main.tf
```

### Missing Dependencies

Ensure logging utilities exist:

```bash
ls -la .claude/lib/shell/logging_utils.sh
```

### Permission Issues

Make script executable:

```bash
chmod +x .agentic_sdlc/scripts/test-framework-full-sdlc.sh
```

## When to Run

- **Before releases** - Validate complete SDLC workflow
- **After refactoring** - Ensure no regressions across phases
- **Post-migration** - Verify framework/project separation
- **CI/CD pipelines** - Automated validation

## Comparison: E2E vs Full SDLC Test

| Test | File | Phases | Duration | Focus |
|------|------|--------|----------|-------|
| **E2E Test** | `test-framework-e2e.sh` | 0-3 | ~5 sec | Framework structure, templates, schemas, docs |
| **Full SDLC Test** | `test-framework-full-sdlc.sh` | 0-8 | ~1 sec | Complete workflow, backend, frontend, IaC, QA, DevOps |

Run both:

```bash
# E2E test (Phases 0-3)
./.agentic_sdlc/scripts/test-framework-e2e.sh

# Full SDLC test (Phases 0-8)
./.agentic_sdlc/scripts/test-framework-full-sdlc.sh
```

## Benefits

✅ **Comprehensive** - Tests all 9 SDLC phases
✅ **Fast** - Completes in ~1 second
✅ **Realistic** - Simulates complete microservices project
✅ **Self-contained** - Uses temporary directory, cleans up
✅ **Observable** - Logs all steps to Loki
✅ **CI-friendly** - Returns proper exit codes
✅ **Debuggable** - Preserves artifacts on failure
✅ **Production-like** - Includes IaC, K8s, CI/CD, monitoring

## See Also

- `test-framework-e2e.sh` - Basic E2E test (Phases 0-3)
- `.claude/skills/gate-evaluator/tests/test_framework_integration.py` - Unit tests
- `.claude/hooks/validate-framework-structure.sh` - Framework validation hook
- `.agentic_sdlc/docs/guides/quickstart.md` - Getting started guide
