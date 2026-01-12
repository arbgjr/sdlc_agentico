# Simulação Detalhada: Sistema de Duplicatas Eletrônicas

**Documento**: Walkthrough completo do SDLC Agêntico
**Projeto**: Sistema de Duplicatas Eletrônicas (Lei 13.775/2018)
**Data**: 2026-01-12

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Fase 0: Intake](#fase-0-intake)
3. [Fase 1: Descoberta](#fase-1-descoberta)
4. [Fase 2: Produto](#fase-2-produto)
5. [Fase 3: Arquitetura](#fase-3-arquitetura)
6. [Fase 4: Planejamento](#fase-4-planejamento)
7. [Fase 5: Implementação](#fase-5-implementação)
8. [Fase 6: Qualidade](#fase-6-qualidade)
9. [Fase 7: Release](#fase-7-release)
10. [Fase 8: Operação](#fase-8-operação)
11. [Resumo de Interações](#resumo-de-interações)
12. [Métricas Finais](#métricas-finais)

---

## Visão Geral

### O que é o Sistema de Duplicatas Eletrônicas?

Duplicatas eletrônicas (ou escriturais) são títulos de crédito digitais regulamentados pela Lei 13.775/2018. O sistema permite:

- Emissão digital de duplicatas mercantis e de serviço
- Registro em escrituradoras autorizadas pelo BACEN
- Assinatura digital com certificado ICP-Brasil
- Endosso e cessão eletrônica
- Integração com registradoras (CERC, TAG, B3)
- Consulta de lastro e duplicidade

### Complexidade Detectada

```yaml
bmad_level: 3  # Enterprise
razões:
  - Regulamentação financeira (BACEN, Lei 13.775)
  - Compliance obrigatório (LGPD, sigilo bancário)
  - Integração com múltiplos sistemas externos
  - Assinatura digital ICP-Brasil
  - Alta criticidade (títulos de crédito)
  - Multi-tenant (múltiplas empresas)
```

### Agentes Envolvidos (32 total)

| Fase | Agentes |
|------|---------|
| 0 | intake-analyst, compliance-guardian |
| 1 | domain-researcher, doc-crawler, rag-curator |
| 2 | product-owner, requirements-analyst, ux-writer |
| 3 | system-architect, adr-author, data-architect, threat-modeler |
| 4 | delivery-planner |
| 5 | code-author, code-reviewer, test-author, refactoring-advisor |
| 6 | qa-analyst, security-scanner, performance-analyst |
| 7 | release-manager, cicd-engineer, change-manager |
| 8 | incident-commander, rca-analyst, metrics-analyst, observability-engineer, memory-curator |
| Cross | orchestrator, playbook-governance |

---

## Fase 0: Intake

### Comando Inicial

```bash
/sdlc-start "Sistema de Duplicatas Eletrônicas"
```

### Agente: intake-analyst

**Entrada do usuário:**
> "Preciso de um sistema para emitir e gerenciar duplicatas eletrônicas conforme a Lei 13.775/2018, com integração às registradoras autorizadas pelo BACEN."

**Análise inicial:**

```yaml
intake_analysis:
  request_id: "REQ-2026-001"
  title: "Sistema de Duplicatas Eletrônicas"

  classification:
    type: "new_product"
    domain: "fintech/credit"
    complexity: "high"

  stakeholders_identified:
    - role: "Empresas emissoras"
      interest: "Emitir duplicatas digitalmente"
    - role: "Sacados"
      interest: "Receber e aceitar duplicatas"
    - role: "Bancos/Factorings"
      interest: "Descontar duplicatas"
    - role: "Registradoras"
      interest: "Registrar e consultar duplicatas"
    - role: "BACEN"
      interest: "Regulamentação e fiscalização"

  initial_scope:
    in_scope:
      - "Emissão de duplicatas mercantis e de serviço"
      - "Assinatura digital ICP-Brasil"
      - "Registro em escrituradoras"
      - "Endosso eletrônico"
      - "Consulta de lastro"
      - "Integração com registradoras (CERC, TAG)"
    out_of_scope:
      - "Cobrança bancária"
      - "Protesto eletrônico"
      - "Custódia de títulos"

  risks_identified:
    - risk: "Compliance regulatório"
      severity: "critical"
      mitigation: "Consultar jurídico especializado"
    - risk: "Integração com registradoras"
      severity: "high"
      mitigation: "Homologação em sandbox"
    - risk: "Certificação digital"
      severity: "high"
      mitigation: "Parceria com AC credenciada"
```

### Agente: compliance-guardian

**Verificação de compliance:**

```yaml
compliance_check:
  request_id: "REQ-2026-001"

  regulations_applicable:
    - regulation: "Lei 13.775/2018"
      description: "Duplicatas escriturais"
      status: "mandatory"

    - regulation: "Circular BACEN 3.952/2019"
      description: "Registro de duplicatas"
      status: "mandatory"

    - regulation: "LGPD (Lei 13.709/2018)"
      description: "Proteção de dados pessoais"
      status: "mandatory"

    - regulation: "Lei do Sigilo Bancário"
      description: "Sigilo de operações financeiras"
      status: "mandatory"

    - regulation: "MP 2.200-2/2001"
      description: "ICP-Brasil e assinatura digital"
      status: "mandatory"

  compliance_requirements:
    data_retention:
      duplicatas: "5 anos após vencimento"
      logs_auditoria: "10 anos"
      dados_pessoais: "Conforme LGPD"

    security_requirements:
      - "Criptografia em trânsito (TLS 1.3)"
      - "Criptografia em repouso (AES-256)"
      - "Certificação digital ICP-Brasil"
      - "Logs de auditoria imutáveis"
      - "Segregação de ambientes"

    audit_requirements:
      - "Trilha de auditoria completa"
      - "Não-repúdio de transações"
      - "Backup georredundante"

  blockers: []
  warnings:
    - "Necessário DPO designado para LGPD"
    - "Contrato com registradora deve prever SLA"

  gate_status: "APPROVED"
```

---

### 🔴 INTERAÇÃO HUMANA #1: Aprovação de Compliance

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  APROVAÇÃO REQUERIDA: Gate 0 → 1 (Intake → Descoberta)       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Projeto: Sistema de Duplicatas Eletrônicas                  ║
║  Complexidade: Level 3 (Enterprise)                          ║
║                                                              ║
║  Regulamentações identificadas:                              ║
║  • Lei 13.775/2018 (Duplicatas escriturais)                  ║
║  • Circular BACEN 3.952/2019                                 ║
║  • LGPD                                                      ║
║  • Lei do Sigilo Bancário                                    ║
║  • ICP-Brasil                                                ║
║                                                              ║
║  Warnings:                                                   ║
║  ⚠️  Necessário DPO designado para LGPD                      ║
║  ⚠️  Contrato com registradora deve prever SLA               ║
║                                                              ║
║  Você confirma que:                                          ║
║  1. As regulamentações foram compreendidas?                  ║
║  2. A empresa possui DPO ou irá designar?                    ║
║  3. O escopo está correto?                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Aprovar] [Rejeitar] [Solicitar alterações]
```

**Resposta esperada do usuário:**
> "Aprovar. Já temos DPO designado e contrato em negociação com a CERC."

---

## Fase 1: Descoberta

### Agente: domain-researcher

**Pesquisa de domínio:**

```yaml
domain_research:
  topic: "Duplicatas Eletrônicas Brasil"

  sources_consulted:
    - source: "planalto.gov.br"
      content: "Lei 13.775/2018 - texto integral"
      relevance: "critical"

    - source: "bcb.gov.br"
      content: "Circular 3.952/2019 e FAQ"
      relevance: "critical"

    - source: "cerc.inf.br"
      content: "Documentação técnica de integração"
      relevance: "high"

    - source: "tag.com.br"
      content: "API de registro de duplicatas"
      relevance: "high"

    - source: "arxiv.org"
      papers:
        - "Blockchain for Trade Finance (2024)"
        - "Digital Signatures in Financial Systems (2023)"
      relevance: "medium"

  key_findings:
    legal:
      - "Duplicata escritural tem mesma validade da cartular"
      - "Registro em escrituradora é obrigatório para oponibilidade"
      - "Assinatura digital substitui aceite físico"
      - "Endosso eletrônico deve ser registrado"

    technical:
      - "Integração via API REST com registradoras"
      - "XMLDSig para assinatura de documentos"
      - "Formato CNAB para remessa de títulos"
      - "Webhook para notificações de eventos"

    market:
      - "CERC: maior registradora, 70% do mercado"
      - "TAG: focada em agronegócio"
      - "B3: integração com mercado de capitais"

  competitors_analysis:
    - name: "Fintech A"
      strengths: ["UX", "Integração rápida"]
      weaknesses: ["Sem endosso", "Apenas CERC"]

    - name: "Banco Digital B"
      strengths: ["Base de clientes", "Crédito integrado"]
      weaknesses: ["Caro", "Burocrático"]
```

### Agente: doc-crawler

**Documentação extraída:**

```yaml
documentation_index:
  created_at: "2026-01-12"

  official_docs:
    - source: "Lei 13.775/2018"
      version: "Original"
      url: "planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/L13775.htm"
      extracted:
        - "Art. 1º - Definição de duplicata escritural"
        - "Art. 3º - Requisitos de emissão"
        - "Art. 8º - Aceite eletrônico"
        - "Art. 12º - Endosso e cessão"

    - source: "Circular BACEN 3.952/2019"
      version: "Consolidada 2024"
      url: "bcb.gov.br/estabilidadefinanceira/exibenormativo"
      extracted:
        - "Requisitos de escrituradoras"
        - "Formato de registro"
        - "Prazos e obrigações"

    - source: "CERC API Documentation"
      version: "v3.2.1"
      url: "developers.cerc.inf.br"
      extracted:
        - "Endpoints de registro"
        - "Autenticação mTLS"
        - "Schemas JSON"
        - "Códigos de erro"

    - source: "TAG API Documentation"
      version: "v2.0.0"
      url: "api.tag.com.br/docs"
      extracted:
        - "Endpoints REST"
        - "Webhooks"
        - "Sandbox de testes"

  changelogs:
    - source: "CERC"
      recent_changes:
        - date: "2025-11-01"
          change: "Novo endpoint de consulta em lote"
        - date: "2025-09-15"
          change: "Suporte a assinatura XAdES-BES"

  versions_to_support:
    cerc_api: "v3.2.x"
    tag_api: "v2.0.x"
    xmldsig: "1.1"
    tls: "1.3"
```

### Agente: rag-curator

**Corpus RAG criado:**

```yaml
rag_corpus:
  project: "duplicatas-eletronicas"

  documents_indexed:
    count: 47
    categories:
      legal: 12
      technical: 18
      business: 8
      security: 9

  embeddings:
    model: "text-embedding-3-large"
    dimensions: 3072

  chunks:
    total: 1247
    avg_size: 512 tokens

  retrieval_tests:
    - query: "Como assinar duplicata digitalmente?"
      top_result: "Lei 13.775/2018, Art. 8º - Aceite eletrônico"
      relevance_score: 0.94

    - query: "Prazo para registro de duplicata"
      top_result: "Circular 3.952, Art. 5º - 3 dias úteis"
      relevance_score: 0.91

    - query: "Formato de integração CERC"
      top_result: "CERC API v3.2 - POST /duplicatas"
      relevance_score: 0.96
```

---

### Gate 1 → 2: Descoberta → Produto

**Artefatos verificados:**
- ✅ Domain Research Report
- ✅ Documentation Index
- ✅ RAG Corpus

**Status:** APROVADO (automático, sem bloqueios)

---

## Fase 2: Produto

### Agente: product-owner

**Visão do produto:**

```yaml
product_vision:
  project: "duplicatas-eletronicas"

  vision_statement: |
    Ser a plataforma líder em gestão de duplicatas eletrônicas no Brasil,
    oferecendo emissão, registro e negociação de títulos de forma simples,
    segura e totalmente digital.

  target_personas:
    - persona: "Gerente Financeiro PME"
      pain_points:
        - "Processo manual de emissão de duplicatas"
        - "Dificuldade em consultar lastro"
        - "Risco de duplicidade de títulos"
      goals:
        - "Automatizar emissão de duplicatas"
        - "Antecipar recebíveis com segurança"
        - "Reduzir inadimplência"

    - persona: "Analista de Crédito Banco"
      pain_points:
        - "Verificação manual de lastro"
        - "Risco de fraude em duplicatas"
        - "Processo lento de desconto"
      goals:
        - "Consulta automática de duplicidade"
        - "Verificação de assinatura digital"
        - "Integração com sistemas internos"

  mvp_definition:
    must_have:
      - "Emissão de duplicata mercantil"
      - "Assinatura digital ICP-Brasil"
      - "Registro na CERC"
      - "Consulta de duplicatas"
      - "Aceite eletrônico"

    should_have:
      - "Duplicata de serviço"
      - "Endosso eletrônico"
      - "Integração TAG"
      - "Dashboard de títulos"

    could_have:
      - "App mobile"
      - "Integração ERP"
      - "Antecipação automática"

    wont_have_now:
      - "Protesto eletrônico"
      - "Cobrança bancária"
      - "Marketplace de títulos"

  prioritization:
    method: "WSJF (Weighted Shortest Job First)"
    top_5_features:
      1: "Emissão de duplicata" # CoD: 10, Time: 3
      2: "Assinatura digital"   # CoD: 10, Time: 5
      3: "Registro CERC"        # CoD: 9, Time: 8
      4: "Consulta duplicatas"  # CoD: 8, Time: 2
      5: "Aceite eletrônico"    # CoD: 8, Time: 3
```

### Agente: requirements-analyst

**Documento de requisitos:**

```yaml
requirements_document:
  version: "1.0"
  status: "draft"

  functional_requirements:
    - id: "FR-001"
      title: "Emissão de Duplicata"
      description: |
        O sistema deve permitir a emissão de duplicatas mercantis e de
        serviço conforme Lei 13.775/2018.
      acceptance_criteria:
        - "Usuário pode criar duplicata com dados obrigatórios"
        - "Sistema valida CNPJ de sacador e sacado"
        - "Sistema gera número único de duplicata"
        - "Duplicata contém todos os campos da Lei 13.775"
      priority: "must"
      story_points: 8

    - id: "FR-002"
      title: "Assinatura Digital"
      description: |
        O sistema deve permitir assinatura digital com certificado
        ICP-Brasil (A1 ou A3).
      acceptance_criteria:
        - "Suporte a certificado A1 (arquivo)"
        - "Suporte a certificado A3 (token/smartcard)"
        - "Validação de cadeia de certificação"
        - "Verificação de revogação (CRL/OCSP)"
        - "Assinatura no padrão XMLDSig"
      priority: "must"
      story_points: 13

    - id: "FR-003"
      title: "Registro em Escrituradora"
      description: |
        O sistema deve registrar duplicatas na CERC automaticamente
        após emissão.
      acceptance_criteria:
        - "Integração com API CERC v3.2"
        - "Autenticação mTLS"
        - "Retry automático em caso de falha"
        - "Notificação de status de registro"
        - "Armazenamento de comprovante"
      priority: "must"
      story_points: 13

    - id: "FR-004"
      title: "Consulta de Duplicatas"
      description: |
        O sistema deve permitir consulta de duplicatas emitidas
        e recebidas.
      acceptance_criteria:
        - "Filtro por período, status, sacado"
        - "Exportação em CSV e PDF"
        - "Paginação de resultados"
        - "Consulta por número da duplicata"
      priority: "must"
      story_points: 5

    - id: "FR-005"
      title: "Aceite Eletrônico"
      description: |
        O sacado deve poder aceitar ou recusar a duplicata
        digitalmente.
      acceptance_criteria:
        - "Notificação por email ao sacado"
        - "Link seguro para aceite"
        - "Assinatura digital do aceite"
        - "Prazo configurável para aceite"
        - "Registro de recusa com motivo"
      priority: "must"
      story_points: 8

  non_functional_requirements:
    - id: "NFR-001"
      category: "Performance"
      requirement: "Tempo de resposta < 2s para 95% das requisições"
      validation: "Teste de carga com 1000 usuários simultâneos"

    - id: "NFR-002"
      category: "Disponibilidade"
      requirement: "SLA de 99.9% de disponibilidade"
      validation: "Monitoramento 24x7 com alertas"

    - id: "NFR-003"
      category: "Segurança"
      requirement: "Criptografia TLS 1.3 em trânsito"
      validation: "Scan de vulnerabilidades semanal"

    - id: "NFR-004"
      category: "Segurança"
      requirement: "Dados sensíveis criptografados em repouso (AES-256)"
      validation: "Auditoria de segurança trimestral"

    - id: "NFR-005"
      category: "Auditoria"
      requirement: "Log de todas as operações com timestamp e usuário"
      validation: "Revisão de logs em incidentes"

    - id: "NFR-006"
      category: "Escalabilidade"
      requirement: "Suportar 10.000 duplicatas/dia"
      validation: "Teste de stress"
```

### Agente: ux-writer

**Especificação de UX:**

```yaml
ux_writing_spec:
  project: "duplicatas-eletronicas"

  screens:
    - screen: "Emissão de Duplicata"
      route: "/duplicatas/nova"
      elements:
        - type: "page_title"
          text: "Emitir Nova Duplicata"

        - type: "field_label"
          field: "sacado_cnpj"
          text: "CNPJ do Sacado"
          helper: "Informe o CNPJ da empresa que receberá a cobrança"

        - type: "field_label"
          field: "valor"
          text: "Valor da Duplicata"
          helper: "Valor em reais (R$)"

        - type: "field_label"
          field: "vencimento"
          text: "Data de Vencimento"
          helper: "Mínimo 1 dia útil a partir de hoje"

        - type: "button_primary"
          text: "Emitir e Assinar"

        - type: "button_secondary"
          text: "Salvar Rascunho"

    - screen: "Aceite do Sacado"
      route: "/aceite/{token}"
      elements:
        - type: "page_title"
          text: "Aceite de Duplicata"

        - type: "info_box"
          text: |
            Você recebeu uma duplicata de {sacador_nome}.
            Revise os dados abaixo e confirme o aceite.

        - type: "button_primary"
          text: "Aceitar Duplicata"

        - type: "button_danger"
          text: "Recusar Duplicata"

  states:
    duplicata_status:
      - status: "rascunho"
        label: "Rascunho"
        color: "gray"
        description: "Duplicata ainda não emitida"

      - status: "emitida"
        label: "Emitida"
        color: "blue"
        description: "Duplicata emitida, aguardando registro"

      - status: "registrada"
        label: "Registrada"
        color: "green"
        description: "Duplicata registrada na escrituradora"

      - status: "aceita"
        label: "Aceita"
        color: "green"
        description: "Sacado aceitou a duplicata"

      - status: "recusada"
        label: "Recusada"
        color: "red"
        description: "Sacado recusou a duplicata"

      - status: "liquidada"
        label: "Liquidada"
        color: "purple"
        description: "Duplicata paga integralmente"

  error_messages:
    - code: "CNPJ_INVALIDO"
      message: "O CNPJ informado é inválido. Verifique os dígitos."
      action: "Corrija o CNPJ e tente novamente."

    - code: "CERTIFICADO_EXPIRADO"
      message: "Seu certificado digital expirou."
      action: "Renove seu certificado ICP-Brasil para continuar."

    - code: "REGISTRO_FALHOU"
      message: "Não foi possível registrar a duplicata na escrituradora."
      action: "Tentaremos novamente automaticamente. Se persistir, contate o suporte."

    - code: "DUPLICATA_JA_REGISTRADA"
      message: "Esta duplicata já foi registrada anteriormente."
      action: "Consulte o número de registro na tela de detalhes."

  flows:
    - flow: "Emissão completa"
      steps:
        1: "Usuário acessa 'Nova Duplicata'"
        2: "Preenche dados do sacado e valores"
        3: "Clica em 'Emitir e Assinar'"
        4: "Sistema solicita certificado digital"
        5: "Usuário insere senha do certificado"
        6: "Sistema assina e envia para registro"
        7: "Exibe confirmação com número de registro"
```

---

### 🔴 INTERAÇÃO HUMANA #2: Validação de Requisitos

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  VALIDAÇÃO REQUERIDA: Requisitos do Produto                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  MVP definido com 5 features principais:                     ║
║                                                              ║
║  1. Emissão de duplicata mercantil (8 pts)                   ║
║  2. Assinatura digital ICP-Brasil (13 pts)                   ║
║  3. Registro na CERC (13 pts)                                ║
║  4. Consulta de duplicatas (5 pts)                           ║
║  5. Aceite eletrônico (8 pts)                                ║
║                                                              ║
║  Total: 47 story points                                      ║
║                                                              ║
║  NFRs definidos:                                             ║
║  • Performance: < 2s para 95% das requisições                ║
║  • Disponibilidade: 99.9% SLA                                ║
║  • Segurança: TLS 1.3 + AES-256                              ║
║                                                              ║
║  Perguntas:                                                  ║
║  1. O MVP está correto? Falta alguma feature crítica?        ║
║  2. Os NFRs estão adequados ao negócio?                      ║
║  3. Há algum fluxo de UX que precisa de ajuste?              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Aprovar] [Solicitar alterações]
```

**Resposta esperada do usuário:**
> "Aprovar. Mas adicione suporte a duplicata de serviço no MVP, não só mercantil."

**Ação do sistema:**
- requirements-analyst atualiza FR-001 para incluir duplicata de serviço
- Story points aumentam para 10
- Total MVP: 49 story points

---

### Gate 2 → 3: Produto → Arquitetura

**Artefatos verificados:**
- ✅ Requirements Document
- ✅ User Stories (5 stories com acceptance criteria)
- ✅ NFR Document
- ✅ UX Writing Spec
- ✅ Product Vision

**Aprovadores requeridos:**
- Product Owner: ✅ (automático, é o próprio PO que criou)
- Tech Lead: 🔴 Aguardando

---

### 🔴 INTERAÇÃO HUMANA #3: Aprovação de Tech Lead

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  APROVAÇÃO REQUERIDA: Gate 2 → 3 (Produto → Arquitetura)     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Aprovador: Tech Lead                                        ║
║                                                              ║
║  Artefatos para revisão:                                     ║
║  • docs/requirements.md                                      ║
║  • docs/stories/*.md                                         ║
║  • docs/nfr.md                                               ║
║  • docs/ux/spec.md                                           ║
║                                                              ║
║  Checklist:                                                  ║
║  [ ] Requisitos são tecnicamente viáveis?                    ║
║  [ ] NFRs são alcançáveis com a stack proposta?              ║
║  [ ] Integrações estão bem definidas?                        ║
║  [ ] Riscos técnicos foram identificados?                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Aprovar] [Rejeitar] [Solicitar alterações]
```

**Resposta esperada do usuário:**
> "Aprovar. Os requisitos estão claros e viáveis."

---

## Fase 3: Arquitetura

### Agente: system-architect

**Arquitetura do sistema:**

```yaml
architecture_overview:
  project: "duplicatas-eletronicas"
  version: "1.0"

  architecture_style: "Microservices"
  deployment: "Kubernetes (AKS)"

  components:
    - name: "api-gateway"
      type: "Gateway"
      technology: "Kong"
      responsibilities:
        - "Roteamento de requisições"
        - "Rate limiting"
        - "Autenticação JWT"
        - "Logging de acesso"

    - name: "duplicatas-service"
      type: "Microservice"
      technology: "Python/FastAPI"
      responsibilities:
        - "CRUD de duplicatas"
        - "Regras de negócio"
        - "Validações"
      database: "PostgreSQL"

    - name: "signature-service"
      type: "Microservice"
      technology: "Java/Spring Boot"
      responsibilities:
        - "Assinatura digital XMLDSig"
        - "Validação de certificados"
        - "Verificação CRL/OCSP"
      dependencies:
        - "HSM para chaves"

    - name: "registry-service"
      type: "Microservice"
      technology: "Python/FastAPI"
      responsibilities:
        - "Integração com CERC"
        - "Integração com TAG"
        - "Retry e circuit breaker"
      dependencies:
        - "mTLS certificates"

    - name: "notification-service"
      type: "Microservice"
      technology: "Node.js"
      responsibilities:
        - "Envio de emails"
        - "Webhooks"
        - "Push notifications"

    - name: "audit-service"
      type: "Microservice"
      technology: "Go"
      responsibilities:
        - "Log de auditoria"
        - "Imutabilidade"
        - "Compliance"
      database: "MongoDB (append-only)"

  infrastructure:
    cloud: "Azure"
    region: "Brazil South"
    components:
      - "AKS (Kubernetes)"
      - "Azure Database for PostgreSQL"
      - "Azure Cosmos DB (MongoDB API)"
      - "Azure Key Vault"
      - "Azure Service Bus"
      - "Azure CDN"
      - "Azure Front Door"

  integrations:
    - name: "CERC"
      protocol: "REST + mTLS"
      auth: "Certificate-based"
      endpoints:
        - "POST /duplicatas"
        - "GET /duplicatas/{id}"
        - "POST /duplicatas/{id}/endosso"

    - name: "TAG"
      protocol: "REST + OAuth2"
      auth: "Client credentials"
      endpoints:
        - "POST /registros"
        - "GET /consultas"

  nfr_approach:
    performance:
      strategy: "Caching + Async processing"
      tools: ["Redis", "Azure Service Bus"]

    availability:
      strategy: "Multi-AZ + Auto-scaling"
      tools: ["AKS", "Azure Load Balancer"]

    security:
      strategy: "Defense in depth"
      tools: ["WAF", "Key Vault", "mTLS"]
```

### Agente: adr-author

**ADR-001: Escolha de Arquitetura**

```markdown
# ADR-001: Arquitetura de Microservices

## Status
Accepted

## Context
O sistema de duplicatas eletrônicas precisa:
- Integrar com múltiplas registradoras (CERC, TAG)
- Escalar independentemente cada componente
- Isolar falhas de integração
- Permitir evolução independente

## Decision
Adotar arquitetura de microservices com:
- 6 serviços independentes
- Comunicação síncrona via REST
- Comunicação assíncrona via Service Bus
- Deploy em Kubernetes (AKS)

## Consequences
### Positivas
- Escalabilidade granular
- Isolamento de falhas
- Deploy independente
- Tecnologia adequada por serviço

### Negativas
- Complexidade operacional
- Latência de rede
- Consistência eventual
- Necessidade de observabilidade robusta
```

### Agente: data-architect

**Modelo de dados:**

```yaml
data_model:
  entities:
    - entity: "Duplicata"
      table: "duplicatas"
      fields:
        - name: "id"
          type: "UUID"
          primary_key: true
        - name: "numero"
          type: "VARCHAR(20)"
          unique: true
        - name: "tipo"
          type: "ENUM('mercantil', 'servico')"
        - name: "sacador_cnpj"
          type: "VARCHAR(14)"
          indexed: true
        - name: "sacado_cnpj"
          type: "VARCHAR(14)"
          indexed: true
        - name: "valor"
          type: "DECIMAL(15,2)"
        - name: "vencimento"
          type: "DATE"
          indexed: true
        - name: "status"
          type: "ENUM('rascunho','emitida','registrada','aceita','recusada','liquidada')"
        - name: "assinatura_xml"
          type: "TEXT"
        - name: "registro_cerc_id"
          type: "VARCHAR(50)"
        - name: "created_at"
          type: "TIMESTAMP"
        - name: "updated_at"
          type: "TIMESTAMP"

    - entity: "AuditLog"
      collection: "audit_logs"
      fields:
        - name: "_id"
          type: "ObjectId"
        - name: "entity_type"
          type: "String"
        - name: "entity_id"
          type: "String"
        - name: "action"
          type: "String"
        - name: "actor_id"
          type: "String"
        - name: "actor_ip"
          type: "String"
        - name: "timestamp"
          type: "DateTime"
        - name: "changes"
          type: "Object"
        - name: "metadata"
          type: "Object"

  api_contracts:
    - name: "Criar Duplicata"
      method: "POST"
      path: "/api/v1/duplicatas"
      request:
        content_type: "application/json"
        schema:
          type: "object"
          required: ["sacado_cnpj", "valor", "vencimento", "tipo"]
          properties:
            sacado_cnpj:
              type: "string"
              pattern: "^\\d{14}$"
            valor:
              type: "number"
              minimum: 0.01
            vencimento:
              type: "string"
              format: "date"
            tipo:
              type: "string"
              enum: ["mercantil", "servico"]
      response:
        status: 201
        schema:
          $ref: "#/definitions/Duplicata"

  events:
    - event: "DuplicataEmitida"
      topic: "duplicatas.emitida"
      payload:
        duplicata_id: "UUID"
        numero: "string"
        valor: "decimal"
        timestamp: "datetime"

    - event: "DuplicataRegistrada"
      topic: "duplicatas.registrada"
      payload:
        duplicata_id: "UUID"
        registro_id: "string"
        registradora: "string"
        timestamp: "datetime"
```

### Agente: threat-modeler

**Análise STRIDE:**

```yaml
threat_model:
  project: "duplicatas-eletronicas"
  methodology: "STRIDE"

  assets:
    critical:
      - "Duplicatas (títulos de crédito)"
      - "Certificados digitais"
      - "Dados de empresas (CNPJ)"
      - "Credenciais de integração"

    high:
      - "Logs de auditoria"
      - "Tokens de sessão"

  threats:
    - id: "T001"
      category: "Spoofing"
      threat: "Falsificação de identidade do emissor"
      asset: "Duplicatas"
      likelihood: "Medium"
      impact: "Critical"
      risk: "High"
      mitigations:
        - "Assinatura digital ICP-Brasil obrigatória"
        - "Validação de certificado em tempo real"
        - "Verificação de revogação (OCSP)"

    - id: "T002"
      category: "Tampering"
      threat: "Alteração de valor da duplicata"
      asset: "Duplicatas"
      likelihood: "Low"
      impact: "Critical"
      risk: "Medium"
      mitigations:
        - "Assinatura digital cobre todos os campos"
        - "Hash SHA-256 do documento"
        - "Log de auditoria imutável"

    - id: "T003"
      category: "Repudiation"
      threat: "Negação de emissão de duplicata"
      asset: "Duplicatas"
      likelihood: "Medium"
      impact: "High"
      risk: "High"
      mitigations:
        - "Assinatura digital com não-repúdio"
        - "Registro em escrituradora"
        - "Timestamp qualificado"

    - id: "T004"
      category: "Information Disclosure"
      threat: "Vazamento de dados financeiros"
      asset: "Dados de empresas"
      likelihood: "Medium"
      impact: "High"
      risk: "High"
      mitigations:
        - "Criptografia em trânsito (TLS 1.3)"
        - "Criptografia em repouso (AES-256)"
        - "RBAC granular"
        - "Mascaramento de dados sensíveis"

    - id: "T005"
      category: "Denial of Service"
      threat: "Indisponibilidade do serviço de registro"
      asset: "Integração CERC"
      likelihood: "Medium"
      impact: "High"
      risk: "High"
      mitigations:
        - "Circuit breaker"
        - "Retry com backoff"
        - "Queue de fallback"
        - "Múltiplas registradoras"

    - id: "T006"
      category: "Elevation of Privilege"
      threat: "Acesso não autorizado a duplicatas de terceiros"
      asset: "Duplicatas"
      likelihood: "Medium"
      impact: "Critical"
      risk: "High"
      mitigations:
        - "Multi-tenancy com isolamento"
        - "RBAC por empresa"
        - "Validação de ownership"

  risk_summary:
    high_risks: 4
    medium_risks: 2
    low_risks: 0
    accepted_risks: 0

  security_requirements:
    - "Implementar WAF com regras OWASP"
    - "Habilitar audit logging em todos os serviços"
    - "Realizar pentest antes do go-live"
    - "Implementar rotação de credenciais"
```

---

### 🔴 INTERAÇÃO HUMANA #4: Aprovação de Arquitetura

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  APROVAÇÃO REQUERIDA: Gate 3 → 4 (Arquitetura → Planejamento)║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Arquitetura proposta: Microservices (6 serviços)            ║
║                                                              ║
║  Stack:                                                      ║
║  • Gateway: Kong                                             ║
║  • Backend: Python/FastAPI, Java/Spring, Node.js, Go         ║
║  • Database: PostgreSQL + MongoDB                            ║
║  • Cloud: Azure (AKS, Service Bus, Key Vault)                ║
║                                                              ║
║  Threat Model:                                               ║
║  • 4 riscos HIGH identificados                               ║
║  • Mitigações definidas para todos                           ║
║                                                              ║
║  ADRs criados:                                               ║
║  • ADR-001: Arquitetura de Microservices                     ║
║  • ADR-002: Escolha de Cloud (Azure)                         ║
║  • ADR-003: Estratégia de Assinatura Digital                 ║
║                                                              ║
║  Aprovadores requeridos:                                     ║
║  • Tech Lead: [ ]                                            ║
║  • Security Lead: [ ] (devido a riscos HIGH)                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Aprovar como Tech Lead] [Aprovar como Security Lead] [Rejeitar]
```

**Resposta esperada do usuário:**
> "Aprovar como Tech Lead. Arquitetura está sólida."

**Sistema aguarda segunda aprovação:**

```
╔══════════════════════════════════════════════════════════════╗
║  APROVAÇÃO PENDENTE: Security Lead                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  O Threat Model identificou 4 riscos HIGH:                   ║
║  • T001: Falsificação de identidade (Spoofing)               ║
║  • T003: Negação de emissão (Repudiation)                    ║
║  • T004: Vazamento de dados (Information Disclosure)         ║
║  • T005: Indisponibilidade (DoS)                             ║
║                                                              ║
║  Mitigações propostas estão adequadas?                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Aprovar como Security Lead] [Rejeitar]
```

**Resposta esperada do usuário:**
> "Aprovar como Security Lead. Adicionar requisito de pentest trimestral."

---

## Fase 4: Planejamento

### Agente: delivery-planner

**Plano de entrega:**

```yaml
delivery_plan:
  project: "duplicatas-eletronicas"
  methodology: "Scrum"
  sprint_duration: "2 weeks"

  team_allocation:
    backend_developers: 3
    frontend_developer: 1
    devops_engineer: 1
    qa_engineer: 1
    tech_lead: 1 (parcial)

  sprints:
    - sprint: 1
      goal: "Infraestrutura e setup"
      stories:
        - "Setup AKS cluster"
        - "Setup PostgreSQL e MongoDB"
        - "Setup CI/CD pipelines"
        - "Configurar observabilidade básica"
      capacity: 40 pts
      committed: 38 pts

    - sprint: 2
      goal: "Duplicatas Service - CRUD básico"
      stories:
        - "FR-001: Emissão de duplicata (parte 1)"
        - "FR-004: Consulta de duplicatas"
        - "Modelo de dados inicial"
      capacity: 40 pts
      committed: 35 pts

    - sprint: 3
      goal: "Assinatura digital"
      stories:
        - "FR-002: Assinatura digital ICP-Brasil"
        - "Integração com HSM"
        - "Validação de certificados"
      capacity: 40 pts
      committed: 38 pts

    - sprint: 4
      goal: "Integração CERC"
      stories:
        - "FR-003: Registro em escrituradora"
        - "mTLS configuration"
        - "Circuit breaker e retry"
      capacity: 40 pts
      committed: 40 pts

    - sprint: 5
      goal: "Aceite eletrônico e notificações"
      stories:
        - "FR-005: Aceite eletrônico"
        - "Notification service"
        - "Email templates"
      capacity: 40 pts
      committed: 35 pts

    - sprint: 6
      goal: "QA, Security e Performance"
      stories:
        - "Testes E2E"
        - "Security scan e fixes"
        - "Load testing"
        - "Performance tuning"
      capacity: 40 pts
      committed: 40 pts

  milestones:
    - name: "Alpha Release"
      date: "Sprint 3"
      criteria:
        - "CRUD de duplicatas funcionando"
        - "Assinatura digital operacional"

    - name: "Beta Release"
      date: "Sprint 5"
      criteria:
        - "Integração CERC em sandbox"
        - "Fluxo completo funcional"

    - name: "Go-Live"
      date: "Sprint 6 + 1 semana"
      criteria:
        - "Todos os testes passando"
        - "Security scan sem criticals"
        - "Performance dentro do SLA"
        - "Aprovação de Release Manager"

  risks:
    - risk: "Atraso na homologação CERC"
      probability: "Medium"
      impact: "High"
      mitigation: "Iniciar processo de homologação na Sprint 2"

    - risk: "Problemas com HSM"
      probability: "Low"
      impact: "High"
      mitigation: "Ambiente de sandbox desde Sprint 1"

  dependencies:
    external:
      - "Contrato CERC assinado"
      - "Certificados mTLS emitidos"
      - "HSM provisionado"
    internal:
      - "Ambiente Azure provisionado"
      - "Equipe onboarded"
```

---

### 🔴 INTERAÇÃO HUMANA #5: Aprovação do Plano

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  APROVAÇÃO REQUERIDA: Gate 4 → 5 (Planejamento → Implementação)
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Plano de 6 sprints (12 semanas):                            ║
║                                                              ║
║  Sprint 1: Infraestrutura (38 pts)                           ║
║  Sprint 2: CRUD Duplicatas (35 pts)                          ║
║  Sprint 3: Assinatura Digital (38 pts) → Alpha               ║
║  Sprint 4: Integração CERC (40 pts)                          ║
║  Sprint 5: Aceite Eletrônico (35 pts) → Beta                 ║
║  Sprint 6: QA/Security/Perf (40 pts) → Go-Live               ║
║                                                              ║
║  Total: 226 story points                                     ║
║  Equipe: 3 backend + 1 frontend + 1 DevOps + 1 QA            ║
║                                                              ║
║  Dependências externas:                                      ║
║  • Contrato CERC                                             ║
║  • Certificados mTLS                                         ║
║  • HSM                                                       ║
║                                                              ║
║  Riscos identificados: 2                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Aprovar] [Solicitar alterações]
```

**Resposta esperada do usuário:**
> "Aprovar. Mas garantir que o contrato CERC seja assinado antes do Sprint 2."

---

## Fase 5: Implementação

### Agente: code-author

**Exemplo de código gerado (duplicatas-service):**

```python
# src/duplicatas/models.py
from enum import Enum
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
import re

class TipoDuplicata(str, Enum):
    MERCANTIL = "mercantil"
    SERVICO = "servico"

class StatusDuplicata(str, Enum):
    RASCUNHO = "rascunho"
    EMITIDA = "emitida"
    REGISTRADA = "registrada"
    ACEITA = "aceita"
    RECUSADA = "recusada"
    LIQUIDADA = "liquidada"

class DuplicataCreate(BaseModel):
    sacado_cnpj: str = Field(..., regex=r"^\d{14}$")
    valor: Decimal = Field(..., gt=0)
    vencimento: date
    tipo: TipoDuplicata
    descricao: str | None = None

    @validator("sacado_cnpj")
    def validate_cnpj(cls, v):
        if not _validar_cnpj(v):
            raise ValueError("CNPJ inválido")
        return v

    @validator("vencimento")
    def validate_vencimento(cls, v):
        if v <= date.today():
            raise ValueError("Vencimento deve ser futuro")
        return v

class Duplicata(BaseModel):
    id: UUID
    numero: str
    sacador_cnpj: str
    sacado_cnpj: str
    valor: Decimal
    vencimento: date
    tipo: TipoDuplicata
    status: StatusDuplicata
    assinatura_xml: str | None = None
    registro_cerc_id: str | None = None
    created_at: datetime
    updated_at: datetime

def _validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ usando algoritmo oficial."""
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calc_digito(cnpj: str, peso: list[int]) -> int:
        soma = sum(int(d) * p for d, p in zip(cnpj, peso))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    peso2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    d1 = calc_digito(cnpj[:12], peso1)
    d2 = calc_digito(cnpj[:12] + str(d1), peso2)

    return cnpj[-2:] == f"{d1}{d2}"
```

```python
# src/duplicatas/service.py
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import DuplicataCreate, Duplicata, StatusDuplicata
from .repository import DuplicataRepository
from ..signature.client import SignatureClient
from ..registry.client import RegistryClient
from ..events.publisher import EventPublisher

class DuplicataService:
    def __init__(
        self,
        repository: DuplicataRepository,
        signature_client: SignatureClient,
        registry_client: RegistryClient,
        event_publisher: EventPublisher,
    ):
        self._repository = repository
        self._signature = signature_client
        self._registry = registry_client
        self._events = event_publisher

    async def criar_duplicata(
        self,
        data: DuplicataCreate,
        sacador_cnpj: str,
        certificado: bytes,
        senha_certificado: str,
    ) -> Duplicata:
        """
        Cria uma nova duplicata, assina e registra na escrituradora.

        Fluxo:
        1. Gera número único
        2. Cria duplicata em rascunho
        3. Assina com certificado ICP-Brasil
        4. Registra na CERC
        5. Publica evento
        """
        # 1. Gerar número único
        numero = await self._gerar_numero_unico()

        # 2. Criar duplicata
        duplicata = await self._repository.create(
            id=uuid4(),
            numero=numero,
            sacador_cnpj=sacador_cnpj,
            sacado_cnpj=data.sacado_cnpj,
            valor=data.valor,
            vencimento=data.vencimento,
            tipo=data.tipo,
            status=StatusDuplicata.RASCUNHO,
        )

        # 3. Assinar
        xml_assinado = await self._signature.assinar(
            documento=self._gerar_xml(duplicata),
            certificado=certificado,
            senha=senha_certificado,
        )

        duplicata = await self._repository.update(
            duplicata.id,
            assinatura_xml=xml_assinado,
            status=StatusDuplicata.EMITIDA,
        )

        # 4. Registrar na CERC
        registro_id = await self._registry.registrar(duplicata)

        duplicata = await self._repository.update(
            duplicata.id,
            registro_cerc_id=registro_id,
            status=StatusDuplicata.REGISTRADA,
        )

        # 5. Publicar evento
        await self._events.publish(
            topic="duplicatas.registrada",
            payload={
                "duplicata_id": str(duplicata.id),
                "numero": duplicata.numero,
                "valor": str(duplicata.valor),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        return duplicata

    async def _gerar_numero_unico(self) -> str:
        """Gera número único no formato YYYYMMDD-NNNNNN."""
        hoje = datetime.now().strftime("%Y%m%d")
        sequencia = await self._repository.get_next_sequence(hoje)
        return f"{hoje}-{sequencia:06d}"

    def _gerar_xml(self, duplicata: Duplicata) -> str:
        """Gera XML da duplicata conforme Lei 13.775/2018."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<duplicata xmlns="http://www.bcb.gov.br/duplicata">
    <numero>{duplicata.numero}</numero>
    <tipo>{duplicata.tipo.value}</tipo>
    <sacador>
        <cnpj>{duplicata.sacador_cnpj}</cnpj>
    </sacador>
    <sacado>
        <cnpj>{duplicata.sacado_cnpj}</cnpj>
    </sacado>
    <valor>{duplicata.valor}</valor>
    <vencimento>{duplicata.vencimento.isoformat()}</vencimento>
</duplicata>"""
```

### Agente: code-reviewer

**Review do código:**

```yaml
code_review:
  file: "src/duplicatas/service.py"
  reviewer: "code-reviewer"
  status: "approved_with_comments"

  findings:
    - severity: "high"
      line: 45
      issue: "Senha do certificado em memória"
      suggestion: |
        Considerar limpar a senha da memória após uso:
        ```python
        finally:
            senha_certificado = None
        ```

    - severity: "medium"
      line: 62
      issue: "Sem timeout na chamada ao registry"
      suggestion: |
        Adicionar timeout para evitar bloqueio:
        ```python
        registro_id = await asyncio.wait_for(
            self._registry.registrar(duplicata),
            timeout=30.0
        )
        ```

    - severity: "low"
      line: 80
      issue: "XML inline no código"
      suggestion: "Extrair para template Jinja2"

    - severity: "info"
      issue: "Cobertura de testes"
      suggestion: "Garantir testes para cenários de falha da CERC"

  metrics:
    complexity: 12
    lines_of_code: 95
    test_coverage: 0  # Testes ainda não escritos

  approval: true
  conditions:
    - "Resolver finding de severity HIGH antes do merge"
    - "Adicionar testes unitários"
```

### Agente: test-author

**Testes gerados:**

```python
# tests/duplicatas/test_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import date, datetime
from decimal import Decimal

from src.duplicatas.service import DuplicataService
from src.duplicatas.models import (
    DuplicataCreate,
    Duplicata,
    TipoDuplicata,
    StatusDuplicata,
)

@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.create.return_value = Duplicata(
        id=uuid4(),
        numero="20260112-000001",
        sacador_cnpj="12345678000190",
        sacado_cnpj="98765432000121",
        valor=Decimal("1000.00"),
        vencimento=date(2026, 2, 12),
        tipo=TipoDuplicata.MERCANTIL,
        status=StatusDuplicata.RASCUNHO,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    repo.update.return_value = repo.create.return_value
    repo.get_next_sequence.return_value = 1
    return repo

@pytest.fixture
def mock_signature_client():
    client = AsyncMock()
    client.assinar.return_value = "<xml>assinado</xml>"
    return client

@pytest.fixture
def mock_registry_client():
    client = AsyncMock()
    client.registrar.return_value = "CERC-2026-00001"
    return client

@pytest.fixture
def mock_event_publisher():
    return AsyncMock()

@pytest.fixture
def service(
    mock_repository,
    mock_signature_client,
    mock_registry_client,
    mock_event_publisher,
):
    return DuplicataService(
        repository=mock_repository,
        signature_client=mock_signature_client,
        registry_client=mock_registry_client,
        event_publisher=mock_event_publisher,
    )

class TestCriarDuplicata:
    @pytest.mark.asyncio
    async def test_criar_duplicata_sucesso(self, service, mock_repository):
        # Given
        data = DuplicataCreate(
            sacado_cnpj="98765432000121",
            valor=Decimal("1000.00"),
            vencimento=date(2026, 2, 12),
            tipo=TipoDuplicata.MERCANTIL,
        )
        certificado = b"certificado_fake"
        senha = "senha123"

        # When
        resultado = await service.criar_duplicata(
            data=data,
            sacador_cnpj="12345678000190",
            certificado=certificado,
            senha_certificado=senha,
        )

        # Then
        assert resultado is not None
        mock_repository.create.assert_called_once()
        assert mock_repository.update.call_count == 2  # assinatura + registro

    @pytest.mark.asyncio
    async def test_criar_duplicata_falha_assinatura(
        self, service, mock_signature_client
    ):
        # Given
        mock_signature_client.assinar.side_effect = Exception("Certificado inválido")
        data = DuplicataCreate(
            sacado_cnpj="98765432000121",
            valor=Decimal("1000.00"),
            vencimento=date(2026, 2, 12),
            tipo=TipoDuplicata.MERCANTIL,
        )

        # When/Then
        with pytest.raises(Exception, match="Certificado inválido"):
            await service.criar_duplicata(
                data=data,
                sacador_cnpj="12345678000190",
                certificado=b"cert",
                senha_certificado="senha",
            )

    @pytest.mark.asyncio
    async def test_criar_duplicata_falha_registro_cerc(
        self, service, mock_registry_client
    ):
        # Given
        mock_registry_client.registrar.side_effect = Exception("CERC indisponível")
        data = DuplicataCreate(
            sacado_cnpj="98765432000121",
            valor=Decimal("1000.00"),
            vencimento=date(2026, 2, 12),
            tipo=TipoDuplicata.MERCANTIL,
        )

        # When/Then
        with pytest.raises(Exception, match="CERC indisponível"):
            await service.criar_duplicata(
                data=data,
                sacador_cnpj="12345678000190",
                certificado=b"cert",
                senha_certificado="senha",
            )

class TestValidarCNPJ:
    def test_cnpj_valido(self):
        from src.duplicatas.models import _validar_cnpj
        assert _validar_cnpj("11222333000181") == True

    def test_cnpj_invalido_digitos(self):
        from src.duplicatas.models import _validar_cnpj
        assert _validar_cnpj("11222333000182") == False

    def test_cnpj_invalido_tamanho(self):
        from src.duplicatas.models import _validar_cnpj
        assert _validar_cnpj("1122233300018") == False

    def test_cnpj_invalido_repetido(self):
        from src.duplicatas.models import _validar_cnpj
        assert _validar_cnpj("11111111111111") == False
```

---

### 🔴 INTERAÇÃO HUMANA #6: Code Review Crítico

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  REVIEW CRÍTICO: Senha de certificado em memória             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  O code-reviewer identificou um problema de ALTA severidade: ║
║                                                              ║
║  Arquivo: src/duplicatas/service.py                          ║
║  Linha: 45                                                   ║
║  Issue: A senha do certificado permanece em memória          ║
║                                                              ║
║  Sugestão do reviewer:                                       ║
║  ```python                                                   ║
║  finally:                                                    ║
║      senha_certificado = None                                ║
║  ```                                                         ║
║                                                              ║
║  Você deseja:                                                ║
║  1. Aplicar a correção sugerida                              ║
║  2. Usar abordagem mais segura (SecureString/memset)         ║
║  3. Aceitar o risco (não recomendado)                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Opção 1] [Opção 2] [Opção 3]
```

**Resposta esperada do usuário:**
> "Opção 2. Usar SecureString para garantir que a senha seja limpa da memória."

**Ação do sistema:**
- code-author implementa SecureString wrapper
- code-reviewer re-aprova o código
- Merge autorizado

---

### Gate 5 → 6: Implementação → Qualidade

**Artefatos verificados:**
- ✅ Código fonte (100% das features implementadas)
- ✅ Testes unitários (cobertura > 80%)
- ✅ Code reviews aprovados
- ✅ Nenhum finding HIGH pendente

**Status:** APROVADO

---

## Fase 6: Qualidade

### Agente: qa-analyst

**Relatório de QA:**

```yaml
qa_report:
  project: "duplicatas-eletronicas"
  version: "1.0.0-beta"
  date: "2026-01-12"

  test_execution:
    unit_tests:
      total: 156
      passed: 154
      failed: 2
      skipped: 0
      coverage: 87%

    integration_tests:
      total: 42
      passed: 40
      failed: 2
      skipped: 0

    e2e_tests:
      total: 18
      passed: 18
      failed: 0
      skipped: 0

  failed_tests:
    - test: "test_registro_cerc_timeout"
      reason: "Timeout de 30s muito curto para sandbox"
      action: "Aumentar para 60s em ambiente de teste"

    - test: "test_assinatura_certificado_a3"
      reason: "Token USB não disponível no CI"
      action: "Mockar para CI, testar manualmente"

  defects_found:
    critical: 0
    high: 1
    medium: 3
    low: 5

  high_defects:
    - id: "BUG-001"
      title: "Duplicata não exibe erro quando CERC retorna 500"
      severity: "high"
      status: "fixed"
      fixed_in: "commit abc123"

  test_environments:
    - env: "dev"
      status: "passed"
    - env: "staging"
      status: "passed"
    - env: "sandbox-cerc"
      status: "passed"

  recommendation: "APPROVED_FOR_RELEASE"
  conditions:
    - "Resolver 2 testes falhando"
    - "Executar teste manual com certificado A3"
```

### Agente: security-scanner

**Relatório de segurança:**

```yaml
security_scan:
  project: "duplicatas-eletronicas"
  date: "2026-01-12"
  tools:
    - "Trivy (container scanning)"
    - "Bandit (Python SAST)"
    - "Snyk (dependency scanning)"
    - "OWASP ZAP (DAST)"

  findings:
    critical: 0
    high: 0
    medium: 2
    low: 8
    informational: 15

  medium_findings:
    - id: "SEC-001"
      category: "Dependency"
      package: "cryptography==41.0.0"
      issue: "CVE-2024-XXXX - Memory corruption"
      recommendation: "Upgrade to cryptography>=42.0.0"
      status: "fixed"

    - id: "SEC-002"
      category: "Configuration"
      issue: "HTTP headers missing X-Content-Type-Options"
      recommendation: "Add 'nosniff' header"
      status: "fixed"

  compliance:
    owasp_top_10:
      - "A01:2021 Broken Access Control": "PASS"
      - "A02:2021 Cryptographic Failures": "PASS"
      - "A03:2021 Injection": "PASS"
      - "A04:2021 Insecure Design": "PASS"
      - "A05:2021 Security Misconfiguration": "PASS"
      - "A06:2021 Vulnerable Components": "PASS"
      - "A07:2021 Auth Failures": "PASS"
      - "A08:2021 Software Integrity": "PASS"
      - "A09:2021 Logging Failures": "PASS"
      - "A10:2021 SSRF": "PASS"

  penetration_test:
    status: "scheduled"
    date: "2026-01-20"
    vendor: "Security Vendor XYZ"

  recommendation: "APPROVED"
  notes: "Pentest agendado, sem bloqueadores para release"
```

### Agente: performance-analyst

**Relatório de performance:**

```yaml
performance_report:
  project: "duplicatas-eletronicas"
  date: "2026-01-12"

  load_test:
    tool: "k6"
    duration: "30 minutes"
    virtual_users: 1000
    ramp_up: "5 minutes"

    results:
      requests_total: 450000
      requests_per_second: 250

      latency:
        p50: 120ms
        p95: 350ms
        p99: 890ms
        max: 2100ms

      error_rate: 0.02%

      endpoints:
        - path: "POST /api/v1/duplicatas"
          p95: 450ms
          throughput: 50 req/s

        - path: "GET /api/v1/duplicatas"
          p95: 80ms
          throughput: 150 req/s

        - path: "GET /api/v1/duplicatas/{id}"
          p95: 45ms
          throughput: 200 req/s

  stress_test:
    tool: "k6"
    max_users: 5000

    results:
      breaking_point: 3500 users
      degradation_start: 2800 users
      error_rate_at_break: 5.2%

  benchmarks:
    - metric: "Latency P95"
      target: "< 500ms"
      actual: "350ms"
      status: "PASS"

    - metric: "Error Rate"
      target: "< 1%"
      actual: "0.02%"
      status: "PASS"

    - metric: "Throughput"
      target: "> 100 req/s"
      actual: "250 req/s"
      status: "PASS"

  slo_compliance:
    availability:
      target: 99.9%
      measured: 99.98%
      status: "PASS"

    latency:
      target: "p95 < 500ms"
      measured: "350ms"
      status: "PASS"

  resilience_tests:
    circuit_breaker:
      scenario: "CERC 100% failure"
      behavior: "Circuit opens after 5 failures"
      recovery: "30 seconds half-open"
      status: "PASS"

    retry_mechanism:
      scenario: "CERC 50% failure rate"
      behavior: "Exponential backoff 1s, 2s, 4s"
      success_after_retry: 98%
      status: "PASS"

  recommendations:
    - "Considerar cache para consultas frequentes"
    - "Monitorar latência do endpoint de criação"

  overall_status: "APPROVED"
```

---

### 🔴 INTERAÇÃO HUMANA #7: Aprovação de QA

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  APROVAÇÃO REQUERIDA: Gate 6 → 7 (Qualidade → Release)       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  QA Report:                                                  ║
║  • Unit tests: 154/156 passed (87% coverage)                 ║
║  • Integration: 40/42 passed                                 ║
║  • E2E: 18/18 passed                                         ║
║  • Defects: 0 critical, 0 high (1 high já corrigido)         ║
║                                                              ║
║  Security Scan:                                              ║
║  • 0 critical, 0 high vulnerabilities                        ║
║  • OWASP Top 10: 100% PASS                                   ║
║  • Pentest agendado para 2026-01-20                          ║
║                                                              ║
║  Performance:                                                ║
║  • P95 latency: 350ms (target < 500ms) ✓                     ║
║  • Error rate: 0.02% (target < 1%) ✓                         ║
║  • Throughput: 250 req/s (target > 100) ✓                    ║
║  • SLO compliance: 100%                                      ║
║                                                              ║
║  Pendências:                                                 ║
║  • 2 testes falhando (timeout e token USB)                   ║
║  • Teste manual com certificado A3                           ║
║                                                              ║
║  Aprovadores requeridos:                                     ║
║  • QA Lead: [ ]                                              ║
║  • Security Lead: [ ]                                        ║
║  • Tech Lead: [ ]                                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Aprovar] [Rejeitar] [Solicitar correções]
```

**Resposta esperada do usuário:**
> "Aprovar. Os 2 testes são de ambiente, não de código. Teste manual A3 será feito amanhã."

---

## Fase 7: Release

### Agente: release-manager

**Preparação do release:**

```yaml
release_preparation:
  version: "1.0.0"
  release_date: "2026-01-15"
  type: "major"

  release_notes:
    title: "Sistema de Duplicatas Eletrônicas v1.0.0"
    highlights:
      - "Emissão de duplicatas mercantis e de serviço"
      - "Assinatura digital ICP-Brasil (A1 e A3)"
      - "Integração com CERC para registro"
      - "Aceite eletrônico de duplicatas"
      - "Dashboard de consulta e gestão"

    breaking_changes: []

    new_features:
      - "FR-001: Emissão de duplicatas"
      - "FR-002: Assinatura digital"
      - "FR-003: Registro em escrituradora"
      - "FR-004: Consulta de duplicatas"
      - "FR-005: Aceite eletrônico"

    bug_fixes: []

    known_issues:
      - "Certificado A3 requer driver específico"
      - "Timeout de registro pode variar com CERC"

  artifacts:
    - name: "duplicatas-service"
      version: "1.0.0"
      image: "acr.azurecr.io/duplicatas-service:1.0.0"
      checksum: "sha256:abc123..."

    - name: "signature-service"
      version: "1.0.0"
      image: "acr.azurecr.io/signature-service:1.0.0"
      checksum: "sha256:def456..."

    - name: "registry-service"
      version: "1.0.0"
      image: "acr.azurecr.io/registry-service:1.0.0"
      checksum: "sha256:ghi789..."

  rollback_plan:
    trigger_conditions:
      - "Error rate > 5% por 5 minutos"
      - "Latency P95 > 2s por 5 minutos"
      - "Health check failing"

    steps:
      1: "Pausar deploy (kubectl rollout pause)"
      2: "Avaliar logs e métricas"
      3: "Se necessário: kubectl rollout undo"
      4: "Notificar stakeholders"
      5: "Criar incident report"

    rollback_time: "< 5 minutos"

  deployment_strategy:
    type: "blue-green"
    canary_percentage: 10
    canary_duration: "15 minutes"
    full_rollout_duration: "30 minutes"
```

### Agente: cicd-engineer

**Pipeline de deploy:**

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

env:
  REGISTRY: acr.azurecr.io
  AKS_CLUSTER: duplicatas-prod
  RESOURCE_GROUP: duplicatas-rg

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to ACR
        uses: azure/docker-login@v1
        with:
          login-server: ${{ env.REGISTRY }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and push images
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          docker build -t $REGISTRY/duplicatas-service:$VERSION ./services/duplicatas
          docker push $REGISTRY/duplicatas-service:$VERSION

  deploy-canary:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy canary (10%)
        run: |
          kubectl set image deployment/duplicatas-service \
            duplicatas-service=$REGISTRY/duplicatas-service:$VERSION
          kubectl rollout status deployment/duplicatas-service --timeout=5m

      - name: Wait for canary validation
        run: sleep 900  # 15 minutes

      - name: Check canary metrics
        run: |
          ERROR_RATE=$(curl -s prometheus/api/v1/query?query=error_rate | jq '.data.result[0].value[1]')
          if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
            echo "Canary failed: error rate $ERROR_RATE"
            exit 1
          fi

  deploy-full:
    needs: deploy-canary
    runs-on: ubuntu-latest
    steps:
      - name: Full rollout
        run: |
          kubectl scale deployment/duplicatas-service --replicas=6
          kubectl rollout status deployment/duplicatas-service --timeout=10m

      - name: Verify deployment
        run: |
          kubectl get pods -l app=duplicatas-service
          curl -f https://api.duplicatas.com.br/health
```

### Agente: change-manager

**Change request:**

```yaml
change_request:
  id: "CHG-2026-001"
  title: "Deploy Sistema de Duplicatas Eletrônicas v1.0.0"
  type: "normal"
  priority: "high"

  requestor: "Release Manager"
  approvers:
    - role: "Change Manager"
      status: "pending"
    - role: "Tech Lead"
      status: "approved"
    - role: "Security Lead"
      status: "approved"

  schedule:
    requested_date: "2026-01-15"
    requested_time: "06:00 BRT"
    maintenance_window: "06:00 - 08:00 BRT"
    estimated_duration: "90 minutes"

  impact_assessment:
    affected_services:
      - "API de Duplicatas"
      - "Portal Web"
      - "Integrações CERC"

    affected_users:
      - "Empresas emissoras (200+)"
      - "Equipe de suporte"

    risk_level: "medium"
    risk_mitigation:
      - "Deploy em horário de baixo uso"
      - "Blue-green deployment"
      - "Rollback automatizado"

  communication_plan:
    pre_change:
      - channel: "Email"
        audience: "Clientes"
        timing: "48h antes"
        message: "Manutenção programada para novo release"

      - channel: "Slack"
        audience: "Equipe interna"
        timing: "24h antes"
        message: "Deploy v1.0.0 agendado para amanhã 06:00"

    during_change:
      - channel: "Status Page"
        status: "Maintenance"

    post_change:
      - channel: "Email"
        audience: "Clientes"
        timing: "Imediato"
        message: "Sistema disponível com novas funcionalidades"

  checklist:
    pre_deployment:
      - "[ ] Backup de banco de dados"
      - "[ ] Certificados mTLS válidos"
      - "[ ] Feature flags configuradas"
      - "[ ] Runbook atualizado"
      - "[ ] On-call confirmado"

    post_deployment:
      - "[ ] Health checks passando"
      - "[ ] Métricas normais"
      - "[ ] Smoke tests executados"
      - "[ ] Clientes notificados"

  status: "pending_approval"
```

---

### 🔴 INTERAÇÃO HUMANA #8: Aprovação de Change Request

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  APROVAÇÃO REQUERIDA: Change Request CHG-2026-001            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Deploy: Sistema de Duplicatas Eletrônicas v1.0.0            ║
║                                                              ║
║  Janela de manutenção: 2026-01-15 06:00-08:00 BRT            ║
║  Duração estimada: 90 minutos                                ║
║  Estratégia: Blue-green com canary 10%                       ║
║                                                              ║
║  Impacto:                                                    ║
║  • 200+ empresas clientes                                    ║
║  • API de Duplicatas                                         ║
║  • Integrações CERC                                          ║
║                                                              ║
║  Risco: MEDIUM                                               ║
║  Mitigação: Deploy em horário baixo + rollback automático    ║
║                                                              ║
║  Aprovações obtidas:                                         ║
║  • Tech Lead: ✅                                              ║
║  • Security Lead: ✅                                          ║
║  • Change Manager: ⏳ Aguardando                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Aprovar como Change Manager] [Rejeitar] [Solicitar alterações]
```

**Resposta esperada do usuário:**
> "Aprovar como Change Manager. Garantir que on-call esteja de prontidão."

---

### 🔴 INTERAÇÃO HUMANA #9: Go-Live Confirmation

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  CONFIRMAÇÃO FINAL: Go-Live v1.0.0                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Checklist de pré-deploy:                                    ║
║  ✅ Backup de banco de dados completo                        ║
║  ✅ Certificados mTLS válidos (expira 2027-01-15)            ║
║  ✅ Feature flags configuradas                               ║
║  ✅ Runbook atualizado e revisado                            ║
║  ✅ On-call confirmado (João Silva)                          ║
║  ✅ Comunicação enviada aos clientes                         ║
║                                                              ║
║  Status Page: https://status.duplicatas.com.br               ║
║  Grafana: https://grafana.duplicatas.internal/dashboard      ║
║                                                              ║
║  Horário atual: 05:55 BRT                                    ║
║  Janela de manutenção inicia em 5 minutos                    ║
║                                                              ║
║  ⚠️  ATENÇÃO: Esta ação iniciará o deploy em produção        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[INICIAR DEPLOY] [Cancelar] [Adiar 1 hora]
```

**Resposta esperada do usuário:**
> "INICIAR DEPLOY"

---

### Gate 7 → 8: Release → Operação

**Artefatos verificados:**
- ✅ Release Notes publicadas
- ✅ Change Request aprovado
- ✅ Deploy executado com sucesso
- ✅ Health checks passando
- ✅ Métricas dentro do esperado
- ✅ Rollback plan testado

**Aprovadores:**
- Release Manager: ✅
- Change Manager: ✅
- On-Call Engineer: ✅

**Status:** APROVADO

---

## Fase 8: Operação

### Agente: observability-engineer

**Configuração de observabilidade:**

```yaml
observability_config:
  project: "duplicatas-eletronicas"
  version: "1.0.0"

  logging:
    provider: "Azure Log Analytics"
    retention: "90 days"
    log_levels:
      production: "INFO"
      staging: "DEBUG"

    structured_fields:
      - "trace_id"
      - "span_id"
      - "user_id"
      - "empresa_id"
      - "duplicata_id"

  tracing:
    provider: "Azure Application Insights"
    sampling_rate: 0.1  # 10% em produção
    propagation: "W3C Trace Context"

    instrumentation:
      - "FastAPI (auto)"
      - "SQLAlchemy (auto)"
      - "HTTP clients (auto)"
      - "Azure Service Bus (auto)"

  metrics:
    provider: "Prometheus + Grafana"
    scrape_interval: "15s"

    custom_metrics:
      - name: "duplicatas_emitidas_total"
        type: "counter"
        labels: ["tipo", "status"]

      - name: "duplicatas_valor_total"
        type: "counter"
        labels: ["tipo"]

      - name: "cerc_latency_seconds"
        type: "histogram"
        buckets: [0.1, 0.5, 1, 2, 5, 10]

      - name: "signature_latency_seconds"
        type: "histogram"
        buckets: [0.1, 0.5, 1, 2, 5]

  dashboards:
    - name: "Duplicatas Overview"
      panels:
        - "Duplicatas emitidas/hora"
        - "Valor total/dia"
        - "Taxa de erro"
        - "Latência P95"

    - name: "Integração CERC"
      panels:
        - "Registros/hora"
        - "Taxa de sucesso"
        - "Latência média"
        - "Circuit breaker status"

    - name: "Sistema de Assinatura"
      panels:
        - "Assinaturas/hora"
        - "Certificados por tipo (A1/A3)"
        - "Erros de validação"
        - "Latência de assinatura"

  slos:
    - name: "Disponibilidade"
      target: 99.9%
      measurement: "1 - (error_requests / total_requests)"
      window: "30 days"

    - name: "Latência"
      target: "95% das requisições < 500ms"
      measurement: "histogram_quantile(0.95, latency)"
      window: "7 days"

  alerts:
    critical:
      - name: "High Error Rate"
        condition: "error_rate > 5% for 5m"
        action: "PagerDuty critical"

      - name: "Service Down"
        condition: "up == 0 for 2m"
        action: "PagerDuty critical"

    warning:
      - name: "Elevated Latency"
        condition: "p95_latency > 1s for 10m"
        action: "Slack #alerts"

      - name: "CERC Integration Degraded"
        condition: "cerc_success_rate < 95% for 5m"
        action: "Slack #alerts + PagerDuty warning"
```

### Agente: metrics-analyst

**Métricas DORA (primeira semana):**

```yaml
dora_metrics:
  period: "2026-01-15 to 2026-01-22"
  project: "duplicatas-eletronicas"

  deployment_frequency:
    value: 1
    target: "> 1/week"
    status: "PASS"
    note: "Release inicial"

  lead_time_for_changes:
    value: "12 weeks"
    target: "< 1 month"
    status: "N/A"
    note: "Projeto greenfield, métrica não aplicável"

  mean_time_to_recovery:
    value: "N/A"
    target: "< 1 hour"
    status: "N/A"
    note: "Nenhum incidente ainda"

  change_failure_rate:
    value: "0%"
    target: "< 15%"
    status: "PASS"
    note: "Deploy bem sucedido"

  business_metrics:
    duplicatas_emitidas:
      first_day: 47
      first_week: 312
      trend: "growing"

    valor_total_registrado:
      first_week: "R$ 2.347.890,00"

    empresas_ativas:
      count: 23
      target: 50 (fim do mês)

    aceite_rate:
      value: 78%
      note: "22% pendentes de aceite"

  system_health:
    availability:
      measured: 99.98%
      target: 99.9%
      status: "PASS"

    error_rate:
      measured: 0.03%
      target: "< 1%"
      status: "PASS"

    latency_p95:
      measured: "320ms"
      target: "< 500ms"
      status: "PASS"
```

---

### 🔴 INTERAÇÃO HUMANA #10: Incidente em Produção

**Cenário simulado: CERC fora do ar**

```
╔══════════════════════════════════════════════════════════════╗
║  🚨 ALERTA: Degradação de Serviço Detectada                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Serviço: registry-service                                   ║
║  Severidade: SEV2                                            ║
║  Início: 2026-01-18 14:32 BRT                                ║
║                                                              ║
║  Sintomas:                                                   ║
║  • Taxa de erro CERC: 100%                                   ║
║  • Circuit breaker: OPEN                                     ║
║  • Duplicatas não sendo registradas                          ║
║                                                              ║
║  Impacto:                                                    ║
║  • 15 duplicatas pendentes de registro                       ║
║  • Funcionalidade de emissão degradada                       ║
║                                                              ║
║  Status CERC (externo): https://status.cerc.inf.br           ║
║  → "Manutenção não programada em andamento"                  ║
║                                                              ║
║  Ações automáticas executadas:                               ║
║  ✅ Circuit breaker aberto                                   ║
║  ✅ Duplicatas enfileiradas para retry                       ║
║  ✅ Alerta enviado para on-call                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Você deseja:
1. Escalar para SEV1
2. Aguardar recuperação da CERC
3. Ativar fallback (outra registradora)
4. Comunicar clientes

[1] [2] [3] [4]
```

**Resposta esperada do usuário:**
> "2 e 4. Aguardar CERC mas comunicar clientes sobre a degradação."

---

### Agente: incident-commander

**Gestão do incidente:**

```yaml
incident:
  id: "INC-2026-001"
  title: "CERC indisponível - Registro de duplicatas degradado"
  severity: "SEV2"
  status: "resolved"

  timeline:
    - time: "14:32"
      event: "Alerta disparado: CERC error rate 100%"
      actor: "system"

    - time: "14:33"
      event: "Circuit breaker aberto automaticamente"
      actor: "system"

    - time: "14:35"
      event: "On-call (João) acionado via PagerDuty"
      actor: "system"

    - time: "14:38"
      event: "Incident commander assume"
      actor: "João Silva"

    - time: "14:40"
      event: "Verificado status CERC: manutenção não programada"
      actor: "João Silva"

    - time: "14:42"
      event: "Comunicação enviada aos clientes via email"
      actor: "sistema"

    - time: "14:45"
      event: "Status page atualizado: degraded"
      actor: "João Silva"

    - time: "15:15"
      event: "CERC retorna online"
      actor: "externo"

    - time: "15:16"
      event: "Circuit breaker half-open"
      actor: "system"

    - time: "15:18"
      event: "Retry das 15 duplicatas pendentes iniciado"
      actor: "system"

    - time: "15:22"
      event: "Todas as duplicatas registradas com sucesso"
      actor: "system"

    - time: "15:25"
      event: "Incidente resolvido"
      actor: "João Silva"

  duration: "53 minutes"
  customer_impact: "Degraded for 53 minutes"
  data_loss: "None"

  communication:
    internal:
      - channel: "Slack #incidents"
        updates: 8

    external:
      - channel: "Email"
        message: "Degradação temporária no registro de duplicatas"
        sent_at: "14:42"

      - channel: "Email"
        message: "Serviço normalizado"
        sent_at: "15:26"
```

### Agente: rca-analyst

**Root Cause Analysis:**

```yaml
rca_report:
  incident_id: "INC-2026-001"
  date: "2026-01-19"
  author: "rca-analyst"

  executive_summary: |
    Incidente causado por manutenção não programada da CERC.
    Sistema se comportou conforme esperado (circuit breaker + retry).
    Nenhuma ação corretiva necessária no nosso lado.

  root_cause:
    primary: "Indisponibilidade externa da CERC"
    contributing:
      - "CERC não comunicou manutenção com antecedência"
      - "Não temos integração com status page da CERC"

  impact:
    duration: "53 minutes"
    affected_customers: 8
    affected_duplicatas: 15
    financial_impact: "R$ 0,00 (nenhuma perda)"

  what_went_well:
    - "Circuit breaker funcionou perfeitamente"
    - "Retry automático recuperou todas as duplicatas"
    - "Comunicação com clientes foi rápida"
    - "Time-to-detect: 1 minuto"

  what_went_wrong:
    - "Não temos monitoramento proativo do status da CERC"
    - "Clientes não tinham visibilidade do status"

  action_items:
    - id: "AI-001"
      action: "Integrar com status page da CERC via API"
      owner: "DevOps"
      due_date: "2026-01-31"
      priority: "medium"

    - id: "AI-002"
      action: "Adicionar widget de status da CERC no dashboard"
      owner: "Frontend"
      due_date: "2026-02-07"
      priority: "low"

    - id: "AI-003"
      action: "Documentar processo de comunicação com clientes"
      owner: "Suporte"
      due_date: "2026-01-25"
      priority: "high"

  lessons_learned:
    - "Circuit breaker é essencial para integrações externas"
    - "Comunicação proativa reduz tickets de suporte"
    - "Monitorar dependências externas é tão importante quanto internas"

  review_meeting:
    date: "2026-01-20"
    attendees:
      - "Tech Lead"
      - "DevOps"
      - "Suporte"
      - "Product Owner"
```

---

### 🔴 INTERAÇÃO HUMANA #11: Aprovação de Action Items

**Prompt para o usuário:**

```
╔══════════════════════════════════════════════════════════════╗
║  REVISÃO: RCA do Incidente INC-2026-001                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Root Cause: Indisponibilidade externa da CERC               ║
║  Duração: 53 minutos                                         ║
║  Impacto: 8 clientes, 15 duplicatas (todas recuperadas)      ║
║                                                              ║
║  O que funcionou bem:                                        ║
║  ✅ Circuit breaker                                          ║
║  ✅ Retry automático                                         ║
║  ✅ Comunicação rápida                                       ║
║                                                              ║
║  Action Items propostos:                                     ║
║                                                              ║
║  1. [MEDIUM] Integrar com status page CERC                   ║
║     Owner: DevOps | Due: 2026-01-31                          ║
║                                                              ║
║  2. [LOW] Widget de status no dashboard                      ║
║     Owner: Frontend | Due: 2026-02-07                        ║
║                                                              ║
║  3. [HIGH] Documentar processo de comunicação                ║
║     Owner: Suporte | Due: 2026-01-25                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

[Aprovar action items] [Adicionar mais items] [Escalar]
```

**Resposta esperada do usuário:**
> "Aprovar action items. Adicionar item para avaliar integração com TAG como fallback."

---

### Agente: memory-curator

**Persistência de conhecimento:**

```yaml
knowledge_persistence:
  project: "duplicatas-eletronicas"
  session_date: "2026-01-18"

  decisions_stored:
    - decision: "Usar circuit breaker para CERC"
      rationale: "Proteger sistema de falhas externas"
      outcome: "Validado em incidente real"
      reference: "ADR-005"

    - decision: "Comunicar clientes em degradações > 15min"
      rationale: "Transparência e redução de tickets"
      outcome: "Positivo - clientes apreciaram comunicação"
      reference: "INC-2026-001"

  learnings_indexed:
    - learning: "CERC pode ter manutenções não programadas"
      source: "INC-2026-001"
      tags: ["cerc", "integração", "disponibilidade"]

    - learning: "Retry com backoff funciona bem para falhas transientes"
      source: "INC-2026-001"
      tags: ["resiliência", "retry", "cerc"]

    - learning: "Circuit breaker deve abrir após 5 falhas consecutivas"
      source: "configuração validada"
      tags: ["circuit-breaker", "config"]

  patterns_detected:
    - pattern: "Integração externa crítica"
      instances: ["CERC", "TAG"]
      recommendation: "Sempre implementar circuit breaker + retry"

  rag_corpus_updated:
    documents_added: 3
    total_documents: 50
    last_update: "2026-01-18T16:00:00Z"
```

---

## Resumo de Interações

### Total de Interações Humanas: 11

| # | Fase | Tipo | Descrição |
|---|------|------|-----------|
| 1 | 0 | Gate Approval | Aprovação de compliance e regulamentações |
| 2 | 2 | Validation | Validação de requisitos do MVP |
| 3 | 2 | Gate Approval | Aprovação de Tech Lead para arquitetura |
| 4 | 3 | Gate Approval | Aprovação de arquitetura (Tech Lead + Security Lead) |
| 5 | 4 | Gate Approval | Aprovação do plano de sprints |
| 6 | 5 | Code Review | Decisão sobre tratamento de senha em memória |
| 7 | 6 | Gate Approval | Aprovação de QA (QA Lead + Security Lead + Tech Lead) |
| 8 | 7 | Change Approval | Aprovação de change request |
| 9 | 7 | Deploy Approval | Confirmação de go-live |
| 10 | 8 | Incident | Decisão durante incidente |
| 11 | 8 | RCA Approval | Aprovação de action items do RCA |

### Decisões por Tipo

```
Gate Approvals:     6 (55%)
Validations:        2 (18%)
Incident Response:  2 (18%)
Code Decisions:     1 (9%)
```

### Tempo Médio por Interação

- Gate Approvals: ~5 minutos
- Validations: ~10 minutos
- Incident Response: ~2 minutos
- Code Decisions: ~5 minutos

---

## Métricas Finais

### Métricas do Projeto

```yaml
project_metrics:
  duration:
    planned: "12 weeks"
    actual: "12 weeks"
    variance: "0%"

  effort:
    story_points_planned: 226
    story_points_delivered: 226
    velocity_average: 38 pts/sprint

  quality:
    defects_found: 9
    defects_critical: 0
    defects_escaped: 0
    test_coverage: 87%

  security:
    vulnerabilities_critical: 0
    vulnerabilities_high: 0
    owasp_compliance: 100%
    pentest_status: "passed"

  performance:
    latency_p95: 350ms (target < 500ms)
    error_rate: 0.02% (target < 1%)
    availability: 99.98% (target 99.9%)
```

### Métricas do SDLC Agêntico

```yaml
sdlc_metrics:
  agents_used: 28 (de 32 disponíveis)
  gates_passed: 8/8
  human_interactions: 11
  automated_decisions: 47

  time_saved_estimate:
    documentation: "40 hours"
    code_review: "20 hours"
    test_creation: "30 hours"
    deployment: "10 hours"
    total: "100 hours (~2.5 weeks)"

  quality_improvements:
    defects_caught_early: 9
    security_issues_prevented: 2
    performance_issues_identified: 3

  compliance:
    gates_with_approval: 8/8
    audit_trail_complete: true
    documentation_generated: 100%
```

### Resumo Visual

```
┌─────────────────────────────────────────────────────────────┐
│                    SDLC COMPLETO                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Fase 0 ──► Fase 1 ──► Fase 2 ──► Fase 3 ──► Fase 4        │
│  Intake    Descoberta  Produto   Arquitetura Planejamento   │
│    │          │          │          │          │            │
│    ▼          ▼          ▼          ▼          ▼            │
│  Gate 0    Gate 1     Gate 2     Gate 3     Gate 4         │
│  [✅]       [✅]        [✅]        [✅]        [✅]          │
│                                                             │
│  Fase 5 ──► Fase 6 ──► Fase 7 ──► Fase 8                   │
│  Implement  Qualidade   Release   Operação                  │
│    │          │          │          │                       │
│    ▼          ▼          ▼          ▼                       │
│  Gate 5    Gate 6     Gate 7     Gate 8                    │
│  [✅]       [✅]        [✅]        [✅]                      │
│                                                             │
│  Interações: 11 | Agentes: 28 | Duração: 12 semanas        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Conclusão

Esta simulação demonstrou o fluxo completo do SDLC Agêntico para o Sistema de Duplicatas Eletrônicas, incluindo:

1. **Todas as 8 fases** do ciclo de vida de desenvolvimento
2. **32 agentes** especializados trabalhando em conjunto
3. **11 pontos de interação humana** em momentos críticos
4. **Gates de qualidade** entre cada fase
5. **Gestão de incidentes** com RCA e aprendizado contínuo
6. **Persistência de conhecimento** para projetos futuros

O sistema garante:
- **Compliance** com regulamentações (Lei 13.775, LGPD, BACEN)
- **Segurança** em todos os níveis (OWASP, pentest, threat modeling)
- **Qualidade** com testes automatizados e revisões de código
- **Rastreabilidade** completa de decisões e aprovações
- **Resiliência** operacional com circuit breakers e retry

---

**Documento gerado pelo SDLC Agêntico**
**Versão**: 1.0
**Data**: 2026-01-12
