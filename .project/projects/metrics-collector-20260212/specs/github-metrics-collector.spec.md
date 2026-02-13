# Spec: GitHub Metrics Collector

## Overview

Aplicacao para extracao automatizada de metricas de uso do GitHub Copilot
e metricas de engenharia (DORA, Velocity) de 2 organizacoes GitHub Enterprise Cloud,
com exportacao de dados estruturados para consumo no PowerBI via Import Mode.

**Arquitetura de Integracao PowerBI (atualizado Phase 3):**
```
GitHub APIs (2 enterprises)
  -> Aplicacao Coletora (Python)
  -> Banco de Dados (Azure SQL/PostgreSQL) [historico + auditoria]
  -> Export Diario (CSV/Parquet)
  -> SharePoint (storage intermediario existente)
  -> PowerBI Online Import (refresh agendado diario)
```

## Problem Statement

A organizacao precisa de visibilidade sobre:
1. **Adocao do GitHub Copilot**: Medir ROI do investimento em AI coding assistant
2. **Metricas de engenharia (DORA)**: Avaliar performance de entrega de software
3. **Metricas de Velocity**: Identificar gargalos no ciclo de desenvolvimento

Atualmente, nao existe uma ferramenta consolidada que colete estas metricas
de multiplas organizacoes GitHub Enterprise Cloud e as disponibilize para
analise no PowerBI.

## Proposed Solution

Sistema composto por:
1. **Collector**: Aplicacao Python que extrai dados das APIs do GitHub
2. **Storage**: Banco de dados relacional (Azure SQL ou PostgreSQL) para historico e auditoria
3. **Exporter**: Modulo de export para CSV/Parquet
4. **Integration**: SharePoint como storage intermediario -> PowerBI Import Mode

### User Decisions

| Decision | Value | Rationale |
|----------|-------|-----------|
| Anonimizacao | NAO | Metricas individuais necessarias por desenvolvedor/time |
| Frequencia | Diaria | Balance entre freshness e rate limits |
| Historico | Desde 2023 | Usuario possui extractions, importar posteriormente |
| Infraestrutura | Nova | Comecar do zero, sem DW existente |
| Volume | Medio | 1K-100K registros/dia |
| Organizations | 2 | GitHub Enterprise Cloud |

## Requirements

### Functional Requirements

#### FR-001: Coleta de Metricas Copilot
- Sistema deve coletar metricas de uso do Copilot via API
- Metricas: acceptance rate, active users, usage by language/editor
- Granularidade: por usuario, por dia
- Organizacoes: 2 GitHub Enterprise Cloud

#### FR-002: Coleta de Metricas DORA
- Sistema deve calcular metricas DORA a partir de dados do GitHub
- Metricas: Lead Time, Deploy Frequency, MTTR (aproximado), Change Failure Rate
- Granularidade: por repositorio, por periodo

#### FR-003: Coleta de Metricas Velocity
- Sistema deve coletar metricas de velocidade de desenvolvimento
- Metricas: commit frequency, PR throughput, review time, code churn
- Granularidade: por desenvolvedor, por repositorio, por periodo

#### FR-004: Armazenamento Estruturado
- Sistema deve armazenar dados em banco relacional
- Schema otimizado para Direct Query do PowerBI
- Segregacao logica de dados por organizacao

#### FR-005: Execucao Automatica
- Sistema deve executar coleta automatica diaria
- Scheduling flexivel (configuravel por organizacao)
- Logging detalhado de execucoes

#### FR-006: Importacao de Dados Historicos
- Sistema deve suportar importacao de dados desde 2023
- Formato de entrada: arquivos existentes do usuario
- Validacao e deduplicacao de dados

#### FR-007: Integracao PowerBI (Import Mode)
- Sistema deve exportar dados em CSV/Parquet apos coleta
- Arquivos devem ser enviados automaticamente para SharePoint
- PowerBI consome via Import Mode com refresh diario agendado
- Manter fluxo existente do usuario (SharePoint -> PowerBI)

### Non-Functional Requirements

#### NFR-SEC-001: Gestao de Credenciais
- Tokens de API armazenados em Azure Key Vault ou equivalente
- Nunca em codigo fonte ou arquivos de configuracao
- Rotacao de tokens suportada

#### NFR-SEC-002: Segregacao de Dados
- Dados de cada organizacao em schema/namespace separado
- Controle de acesso por organizacao
- Labels de origem em todos os registros

#### NFR-SEC-003: Audit Trail
- Log de todas as coletas (timestamp, org, metricas)
- Log de acessos aos dados
- Retencao de logs por 1 ano

#### NFR-PERF-001: Rate Limit Compliance
- Respeitar limites de API do GitHub (5000 req/hour)
- Implementar exponential backoff
- Distribuir coleta ao longo do dia se necessario

#### NFR-PERF-002: Tempo de Coleta
- Coleta diaria completa em < 4 horas
- Suportar coleta incremental (desde ultima execucao)

#### NFR-AVAIL-001: Resiliencia
- Retry automatico em caso de falha
- Alertas em caso de falha persistente
- Nao perder dados coletados em caso de crash

#### NFR-SCALE-001: Volume de Dados
- Suportar 1K-100K registros/dia
- Dezenas de repositorios
- Centenas de usuarios

#### NFR-DATA-001: Retencao
- Dados de metricas retidos por 3 anos
- Dados de logs retidos por 1 ano
- Purge automatico de dados antigos

## User Stories

Ver arquivo: `requirements/user-stories.yml`

## Acceptance Criteria

- [ ] AC-001: Metricas Copilot coletadas diariamente de 2 orgs
- [ ] AC-002: Metricas DORA calculadas para todos os repositorios ativos
- [ ] AC-003: Metricas Velocity disponiveis por desenvolvedor e time
- [ ] AC-004: Dados exportados para SharePoint e acessiveis no PowerBI via Import
- [ ] AC-005: Credenciais armazenadas em Key Vault
- [ ] AC-006: Dados segregados por organizacao
- [ ] AC-007: Coleta automatica configurada e funcionando
- [ ] AC-008: Dados historicos desde 2023 importados

## Out of Scope

- GitHub Enterprise Server (GHES) - apenas Enterprise Cloud
- Integracao real-time / streaming
- Metricas de outras plataformas (GitLab, Bitbucket, Azure DevOps)
- Self-service configuration UI (futuro)
- Alertas automaticos (futuro)
- Machine learning / predictions (futuro)

## Dependencies

- Acesso admin as 2 organizacoes GitHub Enterprise Cloud
- Licenca GitHub Copilot Enterprise
- Tokens de API com permissoes adequadas
- Azure Key Vault ou equivalente para secrets
- Azure SQL Database ou PostgreSQL
- SharePoint site com permissoes de escrita
- PowerBI Online com refresh agendado

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API Copilot deprecated April 2026 | High | High | Usar nova API desde o inicio |
| Rate limits impactam coleta | Medium | Medium | Distribuir coleta, usar caching |
| Dados historicos inconsistentes | Medium | Low | Validacao na importacao |
| SharePoint upload falha | Low | Medium | Retry com exponential backoff |

## Open Questions

1. ~~Quais sao as 2 organizacoes?~~ (Deferred to configuration)
2. Qual o formato dos dados historicos existentes?
3. Quem sao os responsaveis por aprovar acesso aos dados?
4. Existe budget definido para Azure SQL?

---

*Generated by SDLC Agentico - Phase 2 Requirements*
