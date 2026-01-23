# Plano de Implementação - Três Epics SDLC Agêntico

**Data de Criação:** 2026-01-23
**Status:** ✅ Planejamento Completo | ⏳ Aguardando Implementação
**Versão:** 1.0

---

## 📋 Sumário Executivo

Três evoluções significativas para o SDLC Agêntico:

1. **Epic #1: Multi-Model Configuration System** - Otimização de custos via seleção dinâmica de modelos
2. **Epic #2: Leigo-Friendly Mode** - Democratização para usuários não-técnicos
3. **Epic #3: Legacy Project Onboarding** - Engenharia reversa automatizada de projetos legados

**Estimativa Total:** 277 horas (~7 semanas com 1 dev, ~2.5 semanas com 3 devs)
**ROI Esperado:** $400/mês economia (Epic #1), 100x expansão user base (Epic #2), $5k-$10k economia por projeto (Epic #3)

---

## 🎯 Epics e ADRs

### Epic #1: Multi-Model Configuration System
- **GitHub Issue:** [#50](https://github.com/arbgjr/sdlc_agentico/issues/50)
- **ADR:** [ADR-020](../../corpus/nodes/decisions/ADR-020-multi-model-strategy.yml)
- **Tasks:** 8 issues (#53-58, #75-76)
- **Estimativa:** 64h (40h dev, 16h tests, 8h docs)

**Objetivo:** Sistema hierárquico de seleção de modelos Claude (Haiku/Sonnet/Opus) baseado em complexidade, conteúdo e budget.

**Benefícios:**
- 40% economia em custos (~$400/mês)
- Auto-upgrade transparente
- Visibilidade completa via Grafana
- Budget enforcement

### Epic #2: Leigo-Friendly Mode (No-Code SDLC)
- **GitHub Issue:** [#51](https://github.com/arbgjr/sdlc_agentico/issues/51)
- **ADR:** [ADR-021](../../corpus/nodes/decisions/ADR-021-leigo-wizard.yml)
- **Tasks:** 8 issues (#59-65, #77)
- **Estimativa:** 115h (80h dev, 20h tests, 15h docs)

**Objetivo:** Wizard conversacional que permite usuários não-técnicos criarem apps completos respondendo perguntas simples.

**Benefícios:**
- Democratiza desenvolvimento (100x mais usuários)
- Time-to-market 10x mais rápido (2h vs 2 meses)
- Custo 100x menor ($0 vs $5k-$20k)

**Templates:**
1. Blog - Next.js + MDX + Vercel
2. E-commerce - Next.js + Stripe + Supabase
3. Portfolio - Astro + Tailwind + Netlify
4. Directory - Next.js + Supabase + Vercel
5. SaaS - Next.js + Supabase + Stripe + Clerk
6. Internal Tool - Next.js + Supabase + Railway

### Epic #3: Legacy Project Onboarding
- **GitHub Issue:** [#52](https://github.com/arbgjr/sdlc_agentico/issues/52)
- **ADR:** [ADR-022](../../corpus/nodes/decisions/ADR-022-legacy-onboarding.yml)
- **Tasks:** 9 issues (#66-74)
- **Estimativa:** 98h (68h dev, 20h tests, 10h docs)

**Objetivo:** Comando `/onboard-legacy` que realiza engenharia reversa automatizada de projetos existentes.

**Benefícios:**
- Economiza 1-2 semanas (~$5k-$10k) de trabalho manual
- Captura decisões implícitas antes de serem perdidas
- Gera roadmap de modernização automaticamente
- Threat modeling sistemático (STRIDE)

**Languages Support (Phase 1):** Python, JavaScript/TypeScript, Java, C#, Go, Ruby, PHP, Rust, Kotlin, Swift

**✨ IaC/DevOps/QA Detection (Novo):**
- Infrastructure as Code: Terraform, Bicep, CloudFormation, K8s, Helm, Pulumi, Ansible
- CI/CD Pipelines: GitHub Actions, GitLab CI, Jenkins, Azure Pipelines, CircleCI, Travis CI
- Containerization: Docker, Podman, docker-compose
- Testing Infrastructure: pytest, jest, mocha, playwright, cypress, coverage
- Quality & Linting: pylint, flake8, mypy, black, eslint, prettier, pre-commit
- Monitoring: Prometheus, Grafana, OpenTelemetry
- Database Migrations: Alembic, Flyway, Liquibase
- API Documentation: OpenAPI/Swagger, AsyncAPI, GraphQL

---

## 📊 Estimativa Consolidada

### Estimativa Original (Sem awesome-copilot)

| Epic | Desenvolvimento | Testes | Documentação | Total |
|------|----------------|--------|--------------|-------|
| #1 Multi-Model Config | 40h | 16h | 8h | **64h** |
| #2 Leigo-Friendly Mode | 80h | 20h | 15h | **115h** |
| #3 Legacy Onboarding | 68h | 20h | 10h | **98h** |
| **TOTAL** | **188h** | **56h** | **33h** | **277h** |

### ⭐ Estimativa Revisada (Com awesome-copilot)

| Epic | Original | Com Reuso | Time Saving | % Saving |
|------|----------|-----------|-------------|----------|
| #1 Multi-Model Config | 64h | **~48h** | 16h | 25% |
| #2 Leigo-Friendly Mode | 115h | **~75h** | 40h | 35% |
| #3 Legacy Onboarding | 98h | **~55h** | 43h | 44% |
| **TOTAL** | **277h** | **~178h** | **~99h** | **36%** |

**Nova estimativa total:** ~178 horas (~4.5 semanas sequencial, ~2 semanas paralelo)

---

## 🗓️ Timeline de Implementação

### Opção 1: Sequencial (Recomendado - Menor Risco)

**Semanas 1-2: Epic #1 (Multi-Model Config)**
- Fundação de otimização que beneficia outros epics
- Testes e documentação completos antes de prosseguir

**Semanas 3-4: Epic #3 (Legacy Onboarding)**
- Leverage multi-model config para economizar custos
- Valida arquitetura de detecção antes de Epic #2

**Semanas 5-7: Epic #2 (Leigo-Friendly Mode)**
- Leverage tudo construído anteriormente
- Maior complexidade UX/UI requer mais tempo

**Total:** ~7 semanas (1 desenvolvedor full-time)

### Opção 2: Paralela (Mais Rápido - Maior Coordenação)

**Track A:** Epic #1 (Dev 1) - 2 semanas
**Track B:** Epic #3 (Dev 2) - 2.5 semanas
**Track C:** Epic #2 (Dev 3 + UX Designer) - 3 semanas

**Total:** ~3 semanas (3 desenvolvedores + 1 UX designer)

---

## 📝 Breakdown Detalhado de Tasks

### Epic #1: Multi-Model Configuration System

| # | Task | Estimativa | Labels |
|---|------|-----------|--------|
| [#53](https://github.com/arbgjr/sdlc_agentico/issues/53) | Design Model Selection Strategy (ADR-020) | 2h | phase:3, complexity:2 |
| [#54](https://github.com/arbgjr/sdlc_agentico/issues/54) | Implement Model Configuration Schema | 3h | phase:5, complexity:1 |
| [#55](https://github.com/arbgjr/sdlc_agentico/issues/55) | Implement Model Selector Library | 6h | phase:5, complexity:2 |
| [#56](https://github.com/arbgjr/sdlc_agentico/issues/56) | Integrate with Agent Execution | 8h | phase:5, complexity:3 |
| [#57](https://github.com/arbgjr/sdlc_agentico/issues/57) | Implement Cost Tracking Dashboard | 5h | phase:5, complexity:2 |
| [#58](https://github.com/arbgjr/sdlc_agentico/issues/58) | Create Model Selection Quality Gate | 2h | phase:6, complexity:1 |
| [#75](https://github.com/arbgjr/sdlc_agentico/issues/75) | Migration Documentation | 3h | phase:7, complexity:1 |
| [#76](https://github.com/arbgjr/sdlc_agentico/issues/76) | Integration Testing | 4h | phase:6, complexity:2 |

### Epic #2: Leigo-Friendly Mode

| # | Task | Estimativa | Labels |
|---|------|-----------|--------|
| [#59](https://github.com/arbgjr/sdlc_agentico/issues/59) | Design Leigo Wizard UX/Architecture (ADR-021) | 6h | phase:3, complexity:2 |
| [#60](https://github.com/arbgjr/sdlc_agentico/issues/60) | Create 6 Application Templates | 20h | phase:5, complexity:3 |
| [#61](https://github.com/arbgjr/sdlc_agentico/issues/61) | Implement Natural Language Question Engine | 10h | phase:5, complexity:2 |
| [#62](https://github.com/arbgjr/sdlc_agentico/issues/62) | Implement Auto-Stack Selection | 6h | phase:5, complexity:2 |
| [#63](https://github.com/arbgjr/sdlc_agentico/issues/63) | Implement GitHub Operations Abstraction | 5h | phase:5, complexity:2 |
| [#64](https://github.com/arbgjr/sdlc_agentico/issues/64) | Implement One-Click Deployment | 12h | phase:5, complexity:3 |
| [#77](https://github.com/arbgjr/sdlc_agentico/issues/77) | Create Leigo Documentation Portal | 10h | phase:7, complexity:2 |
| [#65](https://github.com/arbgjr/sdlc_agentico/issues/65) | Implement /leigo-start Command | 6h | phase:5, complexity:2 |

### Epic #3: Legacy Project Onboarding

| # | Task | Estimativa | Labels |
|---|------|-----------|--------|
| [#66](https://github.com/arbgjr/sdlc_agentico/issues/66) | Design Reverse Engineering Architecture (ADR-022) | 6h | phase:3, complexity:2 |
| [#67](https://github.com/arbgjr/sdlc_agentico/issues/67) | Implement Language Detection (10 languages) | 8h | phase:5, complexity:2 |
| [#68](https://github.com/arbgjr/sdlc_agentico/issues/68) | Implement IaC/DevOps/QA Detection ⭐ NEW | 8h | phase:5, complexity:3 |
| [#69](https://github.com/arbgjr/sdlc_agentico/issues/69) | Implement Decision Extractor | 12h | phase:5, complexity:3 |
| [#70](https://github.com/arbgjr/sdlc_agentico/issues/70) | Implement Architecture Visualizer | 10h | phase:5, complexity:2 |
| [#71](https://github.com/arbgjr/sdlc_agentico/issues/71) | Implement Threat Model Generator (STRIDE) | 10h | phase:5, complexity:3 |
| [#72](https://github.com/arbgjr/sdlc_agentico/issues/72) | Implement Tech Debt Detector | 8h | phase:5, complexity:2 |
| [#73](https://github.com/arbgjr/sdlc_agentico/issues/73) | Implement /onboard-legacy Command | 10h | phase:5, complexity:3 |
| [#74](https://github.com/arbgjr/sdlc_agentico/issues/74) | Create Validation Quality Gate | 3h | phase:6, complexity:1 |

---

## 🔄 Feedback Incorporado

**Feedback do Usuário (2026-01-23):**
> "senti falta de algo voltado pra identificar IaC, devops, QA e afins no legacy detector"

**Ação Tomada:**
✅ **Task 3.2b criada:** [#68](https://github.com/arbgjr/sdlc_agentico/issues/68) - Implement IaC/DevOps/QA Detection (8h)
✅ **ADR-022 atualizado** com seção completa de detecção (70+ linhas)
✅ **Epic #3 atualizado** no GitHub com nova task e estimativa ajustada (+8h = 98h total)
✅ **Output expandido:** +1-3 IaC ADRs, +1-2 DevOps ADRs, +1-2 QA ADRs, seção "DevOps & Infrastructure" em ARCHITECTURE.md

---

## 📦 Artefatos Criados

### ADRs (3 total)
- [ADR-020: Multi-Model Configuration System](../../corpus/nodes/decisions/ADR-020-multi-model-strategy.yml)
- [ADR-021: Leigo-Friendly Mode](../../corpus/nodes/decisions/ADR-021-leigo-wizard.yml)
- [ADR-022: Legacy Project Onboarding](../../corpus/nodes/decisions/ADR-022-legacy-onboarding.yml)

### GitHub Issues (28 total)
- **Epics:** 3 ([#50](https://github.com/arbgjr/sdlc_agentico/issues/50), [#51](https://github.com/arbgjr/sdlc_agentico/issues/51), [#52](https://github.com/arbgjr/sdlc_agentico/issues/52))
- **Tasks:** 25 ([#53-77](https://github.com/arbgjr/sdlc_agentico/issues))

---

## ⚠️ Riscos e Mitigações

### Epic #1: Multi-Model Config
| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Overhead de seleção impacta performance | Média | Baixo | Cachear decisões, otimizar para <50ms |
| Configuração complexa demais | Baixa | Médio | Sane defaults, wizard de setup |

### Epic #2: Leigo-Friendly Mode
| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Templates não cobrem todos casos | Alta | Médio | Iniciar com 6 comuns, expandir via feedback |
| Leigos confusos apesar do wizard | Média | Alto | User testing com 10+ leigos, iterar UX |

### Epic #3: Legacy Project Onboarding
| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Accuracy de decisão extraction <80% | Média | Médio | Confidence scoring, human review para low-confidence |
| Suporte multi-linguagem complexo | Alta | Médio | Fase 1 com top 10 linguagens, expandir gradualmente |

---

## 🔗 Recursos de Implementação

### Repositórios de Referência (OBRIGATÓRIOS)

#### 1. awesome-copilot (Community-Tested)
**Repository:** https://github.com/github/awesome-copilot

**⚠️ IMPORTANTE:** Ao criar skills, agents, commands, templates e detectors, SEMPRE consultar o awesome-copilot PRIMEIRO. O repositório já possui várias implementações prontas que funcionam e devem ser usadas como base e exemplos.

#### 2. claude-plugins-official (Official Anthropic)
**Repository:** https://github.com/anthropics/claude-plugins-official

**⚠️ IMPORTANTE:** Repositório oficial de plugins do Claude/Anthropic. Consultar para padrões oficiais de implementação de plugins, conversational flows, code analysis e integrações.

#### Recursos Relevantes por Epic

**Epic #1 (Multi-Model Config):**

*awesome-copilot:*
- Cost tracking patterns e scripts
- Configuration management examples
- Dashboard templates (Grafana)
- Model selection heuristics
- Budget enforcement scripts

*claude-plugins-official:*
- Plugin architecture patterns
- Configuration management (official patterns)
- Cost tracking integrations
- Official Anthropic SDK usage examples
- Model selection APIs

**Epic #2 (Leigo-Friendly Mode):**

*awesome-copilot:*
- Wizards conversacionais existentes
- Templates de projetos (chatmodes)
- Question flows e branching logic
- Natural language processing patterns
- Deployment automation scripts

*claude-plugins-official:*
- Conversational plugin architecture
- Multi-step wizard patterns (official)
- Natural language understanding integrations
- Template generation plugins
- External service integrations
- User input validation patterns

**Epic #3 (Legacy Onboarding):**

*awesome-copilot:*
- `reverse-project-analysis.prompt` - Análise reversa de projetos
- `architecture-blueprint-generator.prompt` - Geração de diagramas
- `code-gap-audit.prompt` - Detecção de tech debt
- Threat modeling patterns (STRIDE analysis)
- Documentation generators (README, ARCHITECTURE)
- Language/framework detection heuristics

*claude-plugins-official:*
- Code analysis plugins (official patterns)
- AST parsing integrations
- Language detection plugins
- Security scanning integrations
- Diagram generation plugins (Mermaid/DOT)
- Documentation generation templates
- Static analysis tool integrations

#### Workflow Recomendado

1. **Buscar** em awesome-copilot por funcionalidade similar (community-tested)
2. **Buscar** em claude-plugins-official por padrões oficiais (Anthropic)
3. **Analisar** implementações existentes em ambos repositórios
4. **Priorizar:**
   - claude-plugins-official para arquitetura e padrões oficiais
   - awesome-copilot para implementações community-tested
5. **Adaptar** para SDLC Agêntico (manter compatibilidade quando possível)
6. **Citar** fontes no código:
   ```python
   # Adapted from awesome-copilot: <URL>
   # Based on claude-plugins-official: <URL>
   ```
7. **Contribuir** melhorias de volta (se aplicável)

#### Benefícios

- ✅ Evita reinventar a roda
- ✅ Aproveita battle-tested implementations
- ✅ Mantém compatibilidade com ecossistema GitHub
- ✅ Acelera desenvolvimento (30-50% time saving estimado)
- ✅ Prompts refinados pela community (maior accuracy)

---

## ✅ Próximos Passos Imediatos

1. **Aprovação do Plano** - Confirmar abordagem sequencial vs. paralela
2. **Alocação de Recursos** - Definir desenvolvedores e timeline
3. **Setup de Ambiente** - Instalar dependências adicionais (se necessário)
4. **⭐ Review awesome-copilot** - Identificar recursos reutilizáveis por epic
5. **Kick-off Epic #1** - Iniciar Task #53 (Design Model Selection Strategy)
6. **Configurar Tracking** - Setup GitHub Projects board para tracking

---

## 📚 Referências

- **Plano Original:** Fornecido pelo usuário em 2026-01-23
- **SDLC Agêntico Docs:** `.docs/` directory
- **CLAUDE.md:** Instruções do projeto
- **ADRs Relacionados:**
  - ADR-007: Structured Logging with Loki
  - ADR-claude-orchestrator-integration: Multi-agent workflows

---

**Status:** ✅ Planejamento 100% completo | ⏳ Aguardando aprovação para implementação
**Criado por:** Claude Sonnet 4.5
**Data:** 2026-01-23
