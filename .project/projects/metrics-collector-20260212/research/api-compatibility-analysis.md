# Análise de Compatibilidade: Métricas Git em TFS 2018, Azure DevOps Server e Azure DevOps Service

## Contexto

O projeto **GitHub Metrics Collector** (`.project/projects/metrics-collector-20260212/`) foi desenhado para extrair métricas GitHub de 2 organizações Enterprise Cloud:

**Métricas DORA:**
- Deployment Frequency (de GitHub Actions workflow runs)
- Lead Time for Changes (PRs + commits + deploys)
- Mean Time to Recovery (issues com label 'incident')
- Change Failure Rate (rollbacks, falhas)

**Métricas Velocity:**
- Commit frequency (git commits)
- Pull Request throughput (criação/merge de PRs)
- Review time (tempo até primeiro review)
- Code churn (linhas adicionadas/deletadas)

**Questão:** Qual o nível de incompatibilidade dessas métricas com TFS 2018, Azure DevOps Server e Azure DevOps Service?

---

## Resumo Executivo

| Plataforma | Compatibilidade | Esforço | Limitações Críticas |
|------------|-----------------|---------|---------------------|
| **Azure DevOps Service (Cloud)** | ⚠️ ALTA com restrições | Médio | PAT deprecation 2026, sem GraphQL, rate limiting agressivo (5min vs 1h) |
| **Azure DevOps Server (On-Premise)** | ⚠️ ALTA com restrições | Médio-Alto | Sem OAuth, sem GraphQL, rate limiting conservador |
| **TFS 2018** | ⚠️ BAIXA-MÉDIA | Alto | APIs antigas (v1.0-2.0), sem GraphQL, rate limits não documentados, PAT limitado |

**Incompatibilidade GitHub Copilot:** ❌ **100% incompatível** - Copilot é exclusivo do GitHub.

---

## 1. Matriz de Compatibilidade Detalhada

### 1.1 APIs REST

| Endpoint | GitHub | Azure DevOps Service | Azure DevOps Server | TFS 2018 |
|----------|--------|---------------------|-------------------|----------|
| **Commits** | ✅ `GET /repos/{owner}/{repo}/commits` | ✅ `GET /_apis/git/repositories/{repoId}/commits` | ✅ Idêntico | ⚠️ `api-version=1.0` |
| **Pull Requests** | ✅ `GET /repos/{owner}/{repo}/pulls` | ✅ `GET /_apis/git/repositories/{repoId}/pullrequests` | ✅ Idêntico | ⚠️ `api-version=1.0` |
| **PR Reviews** | ✅ `GET /pulls/{pr}/reviews` | ⚠️ `GET /pullrequests/{prId}/reviewers` (estrutura diferente) | ⚠️ Idêntico | ⚠️ `api-version=1.0` |
| **Workflow/Builds** | ✅ `GET /actions/runs` | ⚠️ `GET /_apis/build/builds` (separado de releases) | ⚠️ Idêntico | ⚠️ `api-version=2.0` |
| **Releases** | ✅ `GET /repos/{owner}/{repo}/releases` | ⚠️ `GET /_apis/release/deployments` (host diferente: `vsrm.dev.azure.com`) | ⚠️ Idêntico | ⚠️ `api-version=4.0-preview`, separado em Release Management |
| **Issues/Work Items** | ✅ `GET /repos/{owner}/{repo}/issues` | ⚠️ `GET /_apis/wit/workitems` (estrutura completamente diferente) | ⚠️ Idêntico | ⚠️ `api-version=1.0` |
| **Code Stats** | ✅ `GET /stats/code_frequency` (nativo) | ❌ Não existe - precisa iterar commits | ❌ Não existe | ❌ Não existe |

**Legenda:**
- ✅ Compatível direto
- ⚠️ Compatível com adaptação
- ❌ Incompatível ou não disponível

### 1.2 GraphQL

| Plataforma | Suporte GraphQL | Impacto |
|------------|-----------------|---------|
| **GitHub** | ✅ Nativo (`POST /graphql`) | Reduz 5-10x chamadas de API |
| **Azure DevOps Service** | ❌ Sem suporte oficial (wrapper de 3rd-party disponível) | Requer múltiplas chamadas REST |
| **Azure DevOps Server** | ❌ Sem suporte | Requer múltiplas chamadas REST |
| **TFS 2018** | ❌ Sem suporte | Requer múltiplas chamadas REST |

**Conclusão:** GraphQL do GitHub proporciona **eficiência substancial**. Azure DevOps/TFS requerem múltiplas chamadas REST para obter dados equivalentes.

---

## 2. Rate Limits e Autenticação

### 2.1 Rate Limits

| Plataforma | Limite | Janela | Headers | Impacto |
|------------|--------|--------|---------|---------|
| **GitHub** | 5,000 req/hour | 1 hora (sliding) | `X-RateLimit-Remaining`, `Retry-After` | Generoso para coleta diária |
| **Azure DevOps Service** | 200 TSTUs / 5min | 5 minutos (rolling) | `X-RateLimit-Delay`, `Retry-After` | **Muito mais restritivo** - requer cache agressivo |
| **Azure DevOps Server** | 200 TSTUs / 5min | 5 minutos (rolling) | Limitado | Requer cache agressivo |
| **TFS 2018** | Não documentado | Não documentado | Não disponível | Backoff exponencial conservador necessário |

**TSTU (Azure DevOps Throughput Unit):** 1 TSTU = carga média de usuário típico em 5 minutos. Spikes até 100 TSTUs tolerados, mas **janela de 5 minutos é 12x mais curta que GitHub**.

**Recomendação:** Implementar **cache local agressivo** e **batching** para Azure DevOps/TFS.

### 2.2 Autenticação

| Plataforma | Métodos | Status | Deadline Crítico |
|------------|---------|--------|------------------|
| **GitHub** | PAT, GitHub App, OAuth | ✅ Estável | N/A |
| **Azure DevOps Service** | PAT (**deprecated**), Entra ID OAuth, Managed Identity | ⚠️ PAT ending April 2, 2026 | **CRÍTICO: Migrar para Entra ID OAuth antes de abril/2025** |
| **Azure DevOps Server** | PAT (estável), NTLM, Windows Auth | ✅ Estável (on-premise) | N/A |
| **TFS 2018** | NTLM, Basic Auth, PAT (limitado) | ⚠️ Legacy | PAT introduzido em TFS 2017 U2, funcionalidade limitada |

**ALERTA CRÍTICO:** Azure DevOps Service está **deprecando PATs em abril de 2026**. Organizações usando Service precisam migrar para **Entra ID OAuth ou Managed Identity** antes dessa data.

---

## 3. Compatibilidade de Métricas Específicas

### 3.1 DORA Metrics

#### **Deployment Frequency**

| Plataforma | Fonte de Dados | Compatibilidade | Notas |
|------------|----------------|-----------------|-------|
| **GitHub** | `GET /actions/runs?branch=main&status=success` | ✅ Nativo | Workflow runs unificados |
| **Azure DevOps Service** | `GET /_apis/build/builds` + `GET /_apis/release/deployments` | ⚠️ Requer 2 endpoints | Builds e Releases são separados |
| **Azure DevOps Server** | Idêntico ao Service | ⚠️ Requer 2 endpoints | Builds e Releases são separados |
| **TFS 2018** | `GET /_apis/build/builds?api-version=2.0` + `GET /_apis/rm/releases?api-version=4.0` | ⚠️ Requer 2 endpoints + Release Management | Releases em host separado, API v4.0-preview |

**Diferença Chave:**
- **GitHub:** Workflow único com stages (build → test → deploy)
- **Azure/TFS:** Build (CI) e Release (CD) são **processos separados**, requer juntar dados de 2 APIs

**Workaround:** Implementar lógica para correlacionar BuildId → ReleaseId via deployment pipeline.

---

#### **Lead Time for Changes**

| Plataforma | Fonte de Dados | Compatibilidade | Notas |
|------------|----------------|-----------------|-------|
| **GitHub** | `GET /pulls` + `GET /actions/runs` | ✅ Direto | PR merge time + workflow start time |
| **Azure DevOps Service** | `GET /pullrequests` + `GET /build/builds` + `GET /release/deployments` | ⚠️ Requer 3 endpoints | Precisa correlacionar PRId → BuildId → DeploymentId |
| **Azure DevOps Server** | Idêntico | ⚠️ Requer 3 endpoints | Idêntico |
| **TFS 2018** | Idêntico | ⚠️ Requer 3 endpoints | APIs v1.0-2.0, estrutura legada |

**Cálculo:**
```
Lead Time = (PR merge time - first commit time) + (deployment time - merge time)
```

**Desafio:** Azure DevOps/TFS requerem **tracking manual** de qual Build foi deployado (via Release) após merge do PR. GitHub faz isso automaticamente.

---

#### **Mean Time to Recovery (MTTR)**

| Plataforma | Fonte de Dados | Compatibilidade | Notas |
|------------|----------------|-----------------|-------|
| **GitHub** | `GET /issues` filtrado por label 'incident' | ⚠️ Aproximação | Não há tracking nativo de incidentes em produção |
| **Azure DevOps Service** | `GET /_apis/wit/workitems` filtrado por type 'Bug' ou 'Issue' | ⚠️ Aproximação | Não há tracking nativo de incidentes em produção |
| **Azure DevOps Server** | Idêntico | ⚠️ Aproximação | Idêntico |
| **TFS 2018** | Idêntico | ⚠️ Aproximação | Idêntico |

**Conclusão:** MTTR **não é nativo em nenhuma plataforma Git**. Todas requerem:
1. Integração com sistema de incident management (PagerDuty, OpsGenie, etc.)
2. OU convenção de labels/work item types para marcar incidentes

**Recomendação:** Definir convenção de labels consistente em todas as plataformas (ex: `incident`, `production-issue`).

---

#### **Change Failure Rate (CFR)**

| Plataforma | Fonte de Dados | Compatibilidade | Notas |
|------------|----------------|-----------------|-------|
| **GitHub** | Detecção de rollbacks em `GET /actions/runs` ou issues linkadas | ⚠️ Requer lógica customizada | Não há detecção automática |
| **Azure DevOps Service** | Detecção de rollbacks em `GET /release/deployments` ou work items linkados | ⚠️ Requer lógica customizada | Não há detecção automática |
| **Azure DevOps Server** | Idêntico | ⚠️ Requer lógica customizada | Idêntico |
| **TFS 2018** | Idêntico | ⚠️ Requer lógica customizada | Idêntico |

**Estratégias de Detecção:**
1. **Rollback Detection:** Detectar commits com mensagens tipo `revert`, `rollback`
2. **Linked Issues:** Issues/work items com label `hotfix`, `incident` linkados a releases
3. **Build Failures:** Deploys seguidos de rollback imediato

**Conclusão:** CFR requer **lógica customizada** em todas as plataformas.

---

### 3.2 Velocity Metrics

#### **Commit Frequency**

| Plataforma | Fonte de Dados | Compatibilidade | Notas |
|------------|----------------|-----------------|-------|
| **GitHub** | `GET /repos/{owner}/{repo}/commits` | ✅ Direto | Inclui stats por autor |
| **Azure DevOps Service** | `GET /_apis/git/repositories/{repoId}/commits` | ✅ Direto | Estrutura JSON diferente (camelCase) |
| **Azure DevOps Server** | Idêntico | ✅ Direto | Idêntico |
| **TFS 2018** | `GET /_apis/git/repositories/{repoId}/commits?api-version=1.0` | ✅ Direto | API v1.0, estrutura legada |

**Diferença de Formato:**
- **GitHub:** `author.login`, `commit.author.date`, `stats.additions`, `stats.deletions`
- **Azure/TFS:** `author.name`, `author.email`, `committer.date` (sem stats direto)

**Workaround:** Normalizar campos em camada de abstração.

---

#### **PR Throughput**

| Plataforma | Fonte de Dados | Compatibilidade | Notas |
|------------|----------------|-----------------|-------|
| **GitHub** | `GET /pulls?state=closed` filtrado por `merged_at IS NOT NULL` | ✅ Direto | Campo `merged_at` presente |
| **Azure DevOps Service** | `GET /_apis/git/pullrequests?status=completed` | ✅ Direto | Campo `status: "completed"` indica merge |
| **Azure DevOps Server** | Idêntico | ✅ Direto | Idêntico |
| **TFS 2018** | Idêntico | ✅ Direto | API v1.0 |

**Diferença de Nomenclatura:**
- **GitHub:** `merged_at` (timestamp)
- **Azure/TFS:** `closedDate` (timestamp) + `status: "completed"` (indica merge)

---

#### **Review Time (Time to First Review)**

| Plataforma | Fonte de Dados | Compatibilidade | Notas |
|------------|----------------|-----------------|-------|
| **GitHub** | `GET /pulls/{pr}/reviews` | ✅ Direto | Retorna lista de reviews com `submitted_at` |
| **Azure DevOps Service** | `GET /pullrequests/{prId}/reviewers` | ⚠️ Requer cálculo | Retorna reviewers com `votedFor` (array), precisa encontrar primeiro review |
| **Azure DevOps Server** | Idêntico | ⚠️ Requer cálculo | Idêntico |
| **TFS 2018** | Idêntico | ⚠️ Requer cálculo | API v1.0 |

**Cálculo:**
```
GitHub: first_review_time = min(reviews[].submitted_at)
Azure:  first_review_time = min(reviewers[].votedFor[].date)
```

**Diferença:** GitHub retorna reviews em ordem cronológica com timestamp direto. Azure/TFS retorna **reviewers** com array `votedFor` que precisa ser parseado.

---

#### **Code Churn (Lines Added/Deleted)**

| Plataforma | Fonte de Dados | Compatibilidade | Notas |
|------------|----------------|-----------------|-------|
| **GitHub** | `GET /repos/{owner}/{repo}/stats/code_frequency` | ✅ Nativo | Retorna `[timestamp, additions, deletions]` por semana |
| **Azure DevOps Service** | ❌ Não existe endpoint direto | ❌ Requer iteração | Precisa iterar commits: `GET /commits/{commitId}` → `changes[]` → somar |
| **Azure DevOps Server** | ❌ Não existe endpoint direto | ❌ Requer iteração | Idêntico |
| **TFS 2018** | ❌ Não existe endpoint direto | ❌ Requer iteração | Idêntico |

**Workaround:** Para Azure/TFS, **iterar por todos os commits** no período e somar `additions`/`deletions` de cada commit.

**Impacto de Performance:**
- **GitHub:** 1 chamada de API retorna agregado semanal
- **Azure/TFS:** N chamadas (1 por commit) + parsing de `changes[]` array

**Recomendação:** Para Azure/TFS, implementar **cache local** de stats de commits para evitar reprocessamento.

---

## 4. Incompatibilidades Críticas

### 4.1 GitHub Copilot Metrics

| Métrica | GitHub | Azure DevOps | TFS 2018 |
|---------|--------|--------------|----------|
| **Copilot Usage API** | ✅ Nativo (`GET /enterprises/{enterprise}/copilot/metrics`) | ❌ Não existe | ❌ Não existe |
| **Acceptance Rate** | ✅ Direto | ❌ N/A | ❌ N/A |
| **Active Users** | ✅ Direto | ❌ N/A | ❌ N/A |
| **Usage by Language/Editor** | ✅ Direto | ❌ N/A | ❌ N/A |
| **Premium vs Standard Requests** | ✅ Direto | ❌ N/A | ❌ N/A |

**Conclusão:** GitHub Copilot é **exclusivo do GitHub**. Azure DevOps e TFS não possuem produto equivalente. Métricas Copilot são **100% incompatíveis**.

---

### 4.2 Formato de Resposta JSON

#### Pull Request Comparison

**GitHub:**
```json
{
  "id": 1,
  "number": 1347,
  "state": "closed",
  "created_at": "2011-01-26T19:01:12Z",
  "merged_at": "2011-01-26T19:01:12Z",
  "merge_commit_sha": "e5bd3914e2e596debea16f433f57c7331bc38d02",
  "additions": 100,
  "deletions": 3,
  "changed_files": 5
}
```

**Azure DevOps / TFS:**
```json
{
  "pullRequestId": 22,
  "status": "completed",
  "creationDate": "2016-01-27T10:28:09.226Z",
  "closedDate": "2016-01-27T10:28:15.996Z",
  "mergeStatus": "succeeded"
}
```

**Diferenças:**
1. **Naming:** `snake_case` (GitHub) vs `camelCase` (Azure)
2. **Identification:** `number` (GitHub) vs `pullRequestId` (Azure)
3. **Stats:** `additions`, `deletions`, `changed_files` inclusos (GitHub) vs precisam de chamada separada (Azure)
4. **Merge Info:** `merge_commit_sha` + `merged_by` (GitHub) vs `mergeStatus` (Azure)

---

### 4.3 URL Structure

| Plataforma | Base URL | Estrutura |
|------------|----------|-----------|
| **GitHub** | `https://api.github.com` | `/repos/{owner}/{repo}/...` |
| **Azure DevOps Service** | `https://dev.azure.com` | `/{org}/{project}/_apis/git/repositories/{repoId}/...` |
| **Azure DevOps Server** | `https://{server}:8080/tfs` | `/{collection}/{project}/_apis/git/repositories/{repoId}/...` |
| **TFS 2018** | `https://{server}:8080/tfs` | `/{collection}/{project}/_apis/git/repositories/{repoId}/...` |

**Releases endpoint especial (Azure/TFS):**
```
Azure: https://vsrm.dev.azure.com/{org}/{project}/_apis/release/deployments
TFS:   https://{server}:8080/tfs/{collection}/{project}/_apis/rm/releases
```

**Nota:** Release Management usa **host diferente** no Azure DevOps Service (`vsrm.dev.azure.com`).

---

## 5. Cenários de Migração

### 5.1 TFS 2018 → Azure DevOps Server (On-Premise)

**Compatibilidade:** ⚠️ ALTA (85-90%)

**Breaking Changes:**
- API version bump: `api-version=1.0` → `api-version=3.0+`
- Alguns campos JSON renomeados (minor)
- Rate limiting mais formal (TSTU model)

**Esforço:** 🔧 BAIXO (1-2 semanas)

**Estratégia:**
```python
# Adapter layer
if api_version < 3.0:
    # TFS 2018 legacy path
    url = f"https://{server}:8080/tfs/{collection}/{project}/_apis/git/..."
else:
    # Azure DevOps Server path
    url = f"https://{server}/{collection}/{project}/_apis/git/..."
```

---

### 5.2 TFS 2018 → Azure DevOps Service (Cloud)

**Compatibilidade:** ⚠️ MÉDIA (70-75%)

**Breaking Changes:**
1. **Authentication:** PAT → Entra ID OAuth (obrigatório até abril/2026)
2. **URL Structure:** `{server}:8080/tfs/{collection}` → `dev.azure.com/{org}`
3. **Rate Limiting:** Legacy throttling → TSTU model (200/5min)
4. **Releases:** Host diferente (`vsrm.dev.azure.com`)

**Esforço:** 🔧 MÉDIO (3-6 semanas)

**Timeline Crítico:**
- **2024-2025:** PAT ainda funciona
- **Abril 2026:** PAT deprecation - obrigatório usar Entra ID OAuth

**Estratégia:**
```python
# Dual authentication during migration
if platform == "tfs_2018":
    auth = PATAuth(token)
elif platform == "azure_devops_service":
    if datetime.now() < datetime(2026, 4, 1):
        auth = PATAuth(token)  # Still works
    else:
        auth = EntraIDAuth(client_id, client_secret)  # Required
```

---

### 5.3 Azure DevOps (any) → GitHub

**Compatibilidade:** ⚠️ BAIXA (30-40%)

**Fundamental Architecture Differences:**
1. **Work Items → Issues:** Estrutura completamente diferente (fields, states, types)
2. **Builds + Releases → GitHub Actions:** Requer reescrita de pipelines
3. **Projects:** Azure DevOps tem hierarquia `org/project/repo`; GitHub tem `org/repo` (flat)
4. **Releases:** Azure tem stages/environments; GitHub tem releases simples

**Esforço:** 🔧 ALTO (2-3 meses)

**Não Recomendado:** Migração direta de código não é viável. Requer ETL customizado e reescrita de pipelines.

---

## 6. Recomendações para o Projeto

### 6.1 Cenário Atual: GitHub Metrics Collector

**Status:** Projeto em Phase 4 (Planning), desenhado para GitHub Enterprise Cloud.

**Se precisar suportar Azure DevOps/TFS:**

#### **Opção A: Adaptar Collector Existente (Multi-Platform)**

**Pros:**
- Reutiliza lógica DORA/Velocity existente
- Single codebase para todas as plataformas

**Cons:**
- Esforço médio-alto (4-8 semanas)
- Complexidade aumenta significativamente
- GraphQL só funciona para GitHub (precisa fallback REST para Azure)

**Arquitetura:**
```python
class MetricsCollectorFactory:
    @staticmethod
    def create(platform_type: str, config: dict):
        if platform_type == "github":
            return GitHubCollector(config)
        elif platform_type == "azure_devops_service":
            return AzureDevOpsServiceCollector(config)
        elif platform_type == "azure_devops_server":
            return AzureDevOpsServerCollector(config)
        elif platform_type == "tfs_2018":
            return TFS2018Collector(config)

# Common interface
class BaseCollector(ABC):
    @abstractmethod
    def get_deployment_frequency(self, start, end): pass

    @abstractmethod
    def get_lead_time(self, start, end): pass

    @abstractmethod
    def get_commit_frequency(self, start, end): pass
```

**Camada de Normalização:**
```python
# Normalize JSON responses
class ResponseNormalizer:
    def normalize_pr(self, platform, raw_pr):
        if platform == "github":
            return {
                "id": raw_pr["number"],
                "created_at": raw_pr["created_at"],
                "merged_at": raw_pr["merged_at"],
                "additions": raw_pr["additions"],
                "deletions": raw_pr["deletions"]
            }
        elif platform in ["azure_devops_service", "azure_devops_server", "tfs_2018"]:
            return {
                "id": raw_pr["pullRequestId"],
                "created_at": raw_pr["creationDate"],
                "merged_at": raw_pr["closedDate"] if raw_pr["status"] == "completed" else None,
                "additions": None,  # Requires separate API call
                "deletions": None
            }
```

---

#### **Opção B: Collectors Separados por Plataforma**

**Pros:**
- Cada collector otimizado para sua plataforma
- GitHub usa GraphQL (eficiente)
- Azure/TFS usam REST com cache agressivo
- Mais simples de manter

**Cons:**
- Código duplicado (lógica DORA/Velocity replicada)
- Precisa manter múltiplos codebases

**Estrutura:**
```
collectors/
├── github/
│   ├── github_collector.py        # Uses GraphQL + REST
│   ├── github_auth.py              # PAT, GitHub App
│   └── github_rate_limiter.py      # 5000/hour
├── azure_devops/
│   ├── azdo_collector.py           # Uses REST only
│   ├── azdo_auth.py                # PAT (→2026), Entra ID OAuth
│   └── azdo_rate_limiter.py        # 200 TSTU/5min
├── tfs_2018/
│   ├── tfs_collector.py            # Uses legacy REST
│   ├── tfs_auth.py                 # NTLM, PAT (limited)
│   └── tfs_rate_limiter.py         # Conservative backoff
└── shared/
    ├── dora_calculator.py          # Shared DORA logic
    ├── velocity_calculator.py      # Shared Velocity logic
    └── database.py                 # Common storage
```

---

### 6.2 Decisões Críticas

#### **Se TFS 2018 é Requirement:**

1. **Planeje para APIs Legacy:**
   - Use `api-version=1.0` para commits/PRs
   - Use `api-version=2.0` para builds
   - Use `api-version=4.0` para Release Management

2. **Rate Limiting Conservador:**
   - Implemente exponential backoff (2s, 4s, 8s, 16s, 32s)
   - Cache agressivamente (Redis ou SQLite local)
   - Nunca assume rate limit headers (não existem no TFS)

3. **Code Churn:**
   - **Não tente** calcular code churn em tempo real (muito custoso)
   - Cache stats de commits localmente
   - Recalcule apenas incrementalmente

---

#### **Se Azure DevOps Service é Requirement:**

1. **Migração de Autenticação (URGENTE):**
   - **Antes de abril/2025:** Teste Entra ID OAuth
   - **abril/2026:** PAT deprecation - migração obrigatória

2. **Rate Limiting TSTU:**
   - Monitore `X-RateLimit-Remaining` header
   - Janela de 5 minutos é **12x mais curta** que GitHub
   - Implemente request queue com pacing

3. **Releases:**
   - Use host separado: `vsrm.dev.azure.com`
   - Endpoint: `GET /_apis/release/deployments`
   - Correlacione BuildId → ReleaseId

---

#### **Se Azure DevOps Server (On-Premise) é Requirement:**

1. **PAT Authentication:**
   - PAT funciona indefinidamente (on-premise)
   - Sem OAuth (não há Entra ID on-premise)

2. **Rate Limiting:**
   - TSTU model ativo (200/5min)
   - Mesmas estratégias que Service

3. **Network:**
   - Considere latência de rede (on-premise pode ser lento)
   - Implemente timeouts agressivos (5-10s)

---

### 6.3 Workarounds Obrigatórios

#### **1. MTTR em Todas as Plataformas**

**Problema:** Nenhuma plataforma rastreia incidentes de produção nativamente.

**Solução:**
```yaml
# Convention: Label/Work Item Type for incidents
GitHub:
  - Use label: "incident" OR "production-issue"
  - Calculate MTTR: closed_at - created_at

Azure DevOps:
  - Use Work Item Type: "Bug" with Severity = "1 - Critical"
  - OR custom tag: "incident"
  - Calculate MTTR: ClosedDate - CreatedDate

TFS 2018:
  - Use Work Item Type: "Bug" with Priority = 1
  - Calculate MTTR: ClosedDate - CreatedDate
```

**Alternativa:** Integrar com PagerDuty, OpsGenie, ServiceNow para MTTR real.

---

#### **2. Change Failure Rate em Todas as Plataformas**

**Problema:** Nenhuma plataforma detecta rollbacks automaticamente.

**Solução 1: Commit Message Detection**
```python
def is_rollback_commit(commit_message):
    keywords = ["revert", "rollback", "hotfix", "emergency"]
    return any(kw in commit_message.lower() for kw in keywords)
```

**Solução 2: Linked Issues**
```python
def is_failed_deployment(deployment, issues):
    # Check if deployment has linked hotfix/incident issue within 24h
    linked_issues = get_linked_issues(deployment.id)
    return any(
        issue.labels.contains("hotfix") or issue.labels.contains("incident")
        for issue in linked_issues
        if issue.created_at < deployment.finished_at + timedelta(hours=24)
    )
```

**Solução 3: Manual Classification**
```yaml
# Require team to label releases
release_labels:
  - "successful"
  - "failed"
  - "rolled-back"
```

---

#### **3. Code Churn para Azure/TFS**

**Problema:** Não há endpoint `/stats/code_frequency` equivalente.

**Solução: Cache Local + Incremental Processing**
```python
# SQLite local cache
class CodeChurnCache:
    def get_or_compute(self, repo_id, commit_sha):
        # Check cache first
        cached = self.db.get(repo_id, commit_sha)
        if cached:
            return cached

        # Fetch from API
        commit = api.get_commit(repo_id, commit_sha)
        stats = {
            "additions": sum(c["add"] for c in commit["changes"]),
            "deletions": sum(c["delete"] for c in commit["changes"])
        }

        # Cache for future
        self.db.save(repo_id, commit_sha, stats)
        return stats

    def aggregate_weekly(self, repo_id, start_date, end_date):
        commits = api.get_commits(repo_id, start_date, end_date)
        weekly_stats = defaultdict(lambda: {"additions": 0, "deletions": 0})

        for commit in commits:
            week = get_iso_week(commit["date"])
            stats = self.get_or_compute(repo_id, commit["sha"])
            weekly_stats[week]["additions"] += stats["additions"]
            weekly_stats[week]["deletions"] += stats["deletions"]

        return weekly_stats
```

**Performance:**
- GitHub: 1 API call
- Azure/TFS: N API calls (first run) → 0 API calls (subsequent runs, cache hit)

---

## 7. Matriz de Esforço de Implementação

| Tarefa | GitHub | Azure DevOps Service | Azure DevOps Server | TFS 2018 |
|--------|--------|---------------------|-------------------|----------|
| **Setup API Client** | ✅ 1 dia | ⚠️ 2-3 dias | ⚠️ 2-3 dias | ⚠️ 3-5 dias |
| **Authentication** | ✅ 1 dia (PAT) | ⚠️ 3-5 dias (Entra ID OAuth) | ✅ 1 dia (PAT) | ⚠️ 2-3 dias (NTLM/PAT) |
| **Rate Limiting** | ✅ 2 dias | ⚠️ 5 dias (TSTU + cache) | ⚠️ 5 dias (TSTU + cache) | ⚠️ 7 dias (conservative backoff) |
| **Commits Endpoint** | ✅ 1 dia | ✅ 2 dias | ✅ 2 dias | ⚠️ 3 dias |
| **PR Endpoint** | ✅ 1 dia | ⚠️ 3 dias (reviewers parsing) | ⚠️ 3 dias | ⚠️ 4 dias |
| **Builds/Workflows** | ✅ 2 dias | ⚠️ 4 dias (2 APIs) | ⚠️ 4 dias | ⚠️ 5 dias (legacy) |
| **Releases** | ✅ 1 dia | ⚠️ 5 dias (separate host) | ⚠️ 5 dias | ⚠️ 7 dias (RM API) |
| **Work Items/Issues** | ✅ 1 dia | ⚠️ 3 dias | ⚠️ 3 dias | ⚠️ 4 dias |
| **Code Churn** | ✅ 1 dia | ⚠️ 10 dias (cache + iteration) | ⚠️ 10 dias | ⚠️ 15 dias |
| **DORA Calculations** | ✅ 5 dias | ⚠️ 10 dias | ⚠️ 10 dias | ⚠️ 12 dias |
| **Velocity Calculations** | ✅ 3 dias | ⚠️ 5 dias | ⚠️ 5 dias | ⚠️ 7 dias |
| **Testing & QA** | ✅ 5 dias | ⚠️ 10 dias | ⚠️ 10 dias | ⚠️ 15 dias |
| **TOTAL** | ✅ **4-5 semanas** | ⚠️ **8-12 semanas** | ⚠️ **8-12 semanas** | ⚠️ **12-16 semanas** |

**Nota:** Estimativas assumem 1 developer full-time.

---

## 8. Decisão Recomendada

### **Cenário 1: GitHub Only (Recomendado)**

**Quando:**
- Organização usa apenas GitHub Enterprise Cloud
- Quer métricas Copilot (exclusivo do GitHub)
- Quer eficiência máxima (GraphQL)

**Esforço:** ✅ **4-5 semanas** (já planejado no projeto atual)

**Compatibilidade:** ✅ **100%**

---

### **Cenário 2: GitHub + Azure DevOps Service**

**Quando:**
- Organização usa ambas plataformas
- GitHub para novos projetos, Azure para legado
- Precisa consolidar métricas

**Esforço:** ⚠️ **12-16 semanas** (4-5 GitHub + 8-12 Azure)

**Compatibilidade:** ⚠️ **75-80%**

**Riscos:**
- PAT deprecation em 2026 (requer migração para Entra ID OAuth)
- Rate limiting muito mais restritivo (5min vs 1h)
- Code churn custoso (requer cache)

**Recomendação:** Implementar GitHub primeiro, adicionar Azure DevOps em Phase 2 se necessário.

---

### **Cenário 3: GitHub + TFS 2018**

**Quando:**
- Organização ainda usa TFS 2018 on-premise
- Migração para Azure DevOps planejada mas não iniciada
- Precisa métricas de ambos durante transição

**Esforço:** ⚠️ **16-20 semanas** (4-5 GitHub + 12-16 TFS)

**Compatibilidade:** ⚠️ **50-60%**

**Riscos:**
- APIs legacy (v1.0-2.0) com limitações
- Rate limits não documentados
- Code churn extremamente custoso
- NTLM authentication complexo

**Recomendação:** **Não recomendado** a menos que absolutamente necessário. Considere:
1. Priorizar migração TFS → Azure DevOps primeiro
2. OU coletar métricas apenas do GitHub para novos projetos
3. OU usar ferramenta de 3rd-party para TFS (ex: Azure DevOps Analytics)

---

## 9. Alternativas para TFS/Azure DevOps

Se o requisito é ter métricas de TFS/Azure DevOps, considere:

### **Opção A: Azure DevOps Analytics Service**

**Descrição:** Serviço nativo do Azure DevOps para analytics.

**Pros:**
- Nativo, mantido pela Microsoft
- OData API para queries customizadas
- PowerBI DirectQuery support

**Cons:**
- Apenas Azure DevOps Service (cloud)
- Não disponível para TFS 2018 / Azure DevOps Server on-premise
- Requer licença Azure DevOps

**Endpoint:**
```
https://analytics.dev.azure.com/{org}/{project}/_odata/v3.0/
```

---

### **Opção B: Ferramentas de 3rd-Party**

| Ferramenta | Plataformas | Métricas DORA | Preço |
|------------|-------------|---------------|-------|
| **Haystack** | GitHub, Azure DevOps, GitLab | ✅ Completo | $$ |
| **LinearB** | GitHub, Azure DevOps, GitLab, Bitbucket | ✅ Completo | $$$ |
| **Pluralsight Flow** | GitHub, Azure DevOps, GitLab | ✅ Completo | $$$ |
| **Sleuth** | GitHub, Azure DevOps, GitLab, Bitbucket | ✅ Completo | $$ |

**Pros:**
- Multi-platform support nativo
- DORA dashboards prontos
- Menos esforço de desenvolvimento

**Cons:**
- Custo recorrente
- Vendor lock-in
- Menos customizável

---

### **Opção C: Power BI com Azure DevOps Analytics**

**Descrição:** Usar Power BI connector para Azure DevOps.

**Pros:**
- Native integration
- No custom code needed
- Works with Azure DevOps Service and Server

**Cons:**
- Limited to Azure DevOps only
- No GitHub Copilot metrics
- Requires Power BI Premium for large datasets

**Setup:**
```
Power BI Desktop
→ Get Data
→ Online Services
→ Azure DevOps (Boards only / Server)
→ Connect to Analytics
```

---

## 10. Conclusão e Próximos Passos

### **Resumo de Incompatibilidades**

| Categoria | Nível de Incompatibilidade | Impacto |
|-----------|---------------------------|---------|
| **GitHub Copilot Metrics** | ❌ 100% incompatível | Azure/TFS não possuem produto equivalente |
| **GraphQL** | ❌ Não disponível | Azure/TFS requerem 5-10x mais chamadas REST |
| **Rate Limits** | ⚠️ Significativo | Azure: 12x janela mais curta (5min vs 1h) |
| **Code Churn** | ⚠️ Alto custo | Azure/TFS requerem iteração por commit + cache |
| **Deployment Frequency** | ⚠️ Arquitetura diferente | Azure/TFS: Builds + Releases separados |
| **Lead Time** | ⚠️ Requer correlação | Azure/TFS: PRId → BuildId → ReleaseId manual |
| **MTTR** | ⚠️ Nenhuma plataforma nativa | Requer convenção de labels ou external incident tracking |
| **Change Failure Rate** | ⚠️ Nenhuma plataforma nativa | Requer detecção de rollbacks ou classificação manual |
| **Authentication (Azure Service)** | ⚠️ PAT deprecation 2026 | Migração obrigatória para Entra ID OAuth |

---

### **Recomendação Final**

**Para o projeto atual (`.project/projects/metrics-collector-20260212/`):**

1. **Manter foco em GitHub** (Phase 4-7 como planejado)
   - Implementar métricas Copilot (exclusivo)
   - Usar GraphQL para eficiência
   - Completar MVP em 4 sprints

2. **Se Azure DevOps é requirement futuro:**
   - Adicionar em Phase 2 do projeto (após MVP GitHub)
   - Implementar adapter layer para multi-platform
   - Priorizar Azure DevOps Service (cloud) sobre TFS 2018

3. **Se TFS 2018 é requirement:**
   - Avaliar custo-benefício vs migração TFS → Azure DevOps
   - Considerar ferramentas de 3rd-party
   - OU adiar até migração para Azure DevOps

---

### **Próximos Passos Sugeridos**

Se decidir suportar Azure DevOps/TFS:

1. **Phase 1: Arquitetura (2 semanas)**
   - Definir adapter pattern para multi-platform
   - Criar camada de normalização de dados
   - Projetar schema de banco comum

2. **Phase 2: Azure DevOps Service (8-10 semanas)**
   - Implementar cliente REST
   - Implementar Entra ID OAuth
   - Implementar rate limiting TSTU
   - Implementar cache para code churn
   - Testes end-to-end

3. **Phase 3: TFS 2018 (se necessário) (12-14 semanas)**
   - Implementar cliente REST legacy
   - Implementar NTLM authentication
   - Implementar backoff conservador
   - Cache agressivo para code churn
   - Testes end-to-end

---

## Referências

- [Azure DevOps REST API Documentation](https://learn.microsoft.com/en-us/rest/api/azure/devops/)
- [TFS 2018 REST API Documentation](https://learn.microsoft.com/en-us/previous-versions/azure/devops/integrate/previous-apis/overview?view=tfs-2017)
- [Azure DevOps Rate Limits](https://learn.microsoft.com/en-us/azure/devops/integrate/concepts/rate-limits)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [GitHub GraphQL API Documentation](https://docs.github.com/en/graphql)
- [Azure DevOps Analytics Documentation](https://learn.microsoft.com/en-us/azure/devops/report/powerbi/what-is-analytics)
- [DORA Metrics Implementation Guide](https://github.com/DeveloperMetrics/DevOpsMetrics)
- [Microsoft Entra ID OAuth 2.0](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
