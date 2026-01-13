# Copilot Coding Agent Instructions for SDLC Agêntico

## Visão Geral
Este repositório implementa o **SDLC Agêntico**: um framework de orquestração de desenvolvimento orientado por agentes de IA, cobrindo todas as fases do ciclo de vida de software. O projeto é altamente configurável, dirigido por arquivos em `.claude/` e `.docs/`.

## Como ser produtivo aqui
- **Nunca escreva código "solto"**: toda implementação deve ser guiada por specs, user stories ou decisões documentadas (ADRs).
- **Siga o fluxo SDLC**: use comandos como `/sdlc-start`, `/sdlc-create-issues`, `/gate-check` para navegar entre fases e garantir qualidade.
- **Respeite os quality gates**: cada transição de fase exige validação automática (ver `.claude/skills/gate-evaluator/gates/`).
- **Implemente por agente**: cada agente tem responsabilidades e outputs YAML claros (veja `.docs/AGENTS.md`).
- **Documente decisões**: toda mudança relevante de arquitetura deve gerar um ADR.

## Estrutura e Arquitetura
- `.claude/settings.json`: configura agentes, fases, hooks e gates.
- `.claude/agents/`, `.docs/AGENTS.md`: catálogo e responsabilidades dos agentes.
- `.claude/skills/`: skills reutilizáveis (ex: `rag-query`, `memory-manager`).
- `.docs/`: documentação, playbook, comandos e infraestrutura.
- `.scripts/setup-sdlc.sh`: instalação automatizada de dependências.

## Workflows e Comandos Essenciais
- `./.scripts/setup-sdlc.sh`: instala tudo (Python, Node, CLI, etc).
- `claude`: CLI principal para orquestração e comandos SDLC.
- `/sdlc-start "Nova feature"`: inicia workflow.
- `/sdlc-create-issues --assign-copilot`: cria issues e atribui ao Copilot.
- `/gate-check`: valida transição de fase.
- `/adr-create`: registra decisão arquitetural.

## Convenções e Padrões
- **Commits e PRs**: devem referenciar fases, agentes e outputs YAML.
- **Testes**: obrigatórios para toda feature (veja outputs de `test-author`).
- **Observabilidade**: sempre inclua métricas e logs conforme outputs de `observability-engineer`.
- **Pequenas mudanças**: prefira PRs pequenos e incrementais.
- **Integração Copilot**: issues podem ser atribuídas ao Copilot para implementação automática.

## Exemplos de Outputs YAML
- User Story:
  ```yaml
  user_story:
    id: "US-001"
    story: "Como usuário, quero..."
    acceptance_criteria:
      - given: "..."
        when: "..."
        then: "..."
  ```
- Quality Report:
  ```yaml
  quality_report:
    summary:
      status: approved
    test_execution:
      passed: 10
      failed: 0
  ```

## Integrações
- **GitHub Copilot Coding Agent**: issues podem ser atribuídas para implementação automática.
- **Spec Kit**: especificação e validação de requisitos.
- **Claude Code CLI**: orquestração de agentes e comandos SDLC.

## Referências
- `.docs/AGENTS.md`: catálogo de agentes e outputs esperados
- `.claude/settings.json`: configuração central
- `.docs/playbook.md`: princípios e padrões de desenvolvimento
- `.docs/COMMANDS.md`: referência de comandos

> Siga sempre o fluxo SDLC, documente decisões e utilize os agentes conforme suas responsabilidades.
