# Documentacao do SDLC Agentico

Este diretorio contem toda a documentacao do framework SDLC Agentico.

## Estrutura

### engineering-playbook/

Padroes de engenharia e desenvolvimento de software.

- **manual-desenvolvimento/** - Regras e praticas operacionais
  - principios.md - Guias de decisao estaveis
  - qualidade.md - Criterios minimos e gates
  - testes.md - Estrategia pragmatica de testes

- **stacks/** - Catalogo de referencias tecnicas
  - software/ - Linguagens e runtimes (.NET, Python, Rust)
  - dados/ - Data platform e analytics
  - devops/ - CI/CD, observabilidade, seguranca

### sdlc/

Documentacao especifica do SDLC Agentico.

- overview.md - Visao geral e diagrama de fases
- agents.md - Catalogo dos 34 agentes especializados
- commands.md - Comandos disponiveis (/sdlc-start, /gate-check, etc.)

### guides/

Guias praticos para usuarios.

- quickstart.md - Como comecar
- troubleshooting.md - Resolucao de problemas
- infrastructure.md - Configuracao de infraestrutura

### examples/

Exemplos e simulacoes.

- simulation-duplicatas.md - Exemplo completo de uso do SDLC

## Como navegar

1. **Novo no framework?** Comece pelo [quickstart](guides/quickstart.md)
2. **Precisa de padroes de codigo?** Veja [engineering-playbook](engineering-playbook/README.md)
3. **Quer entender as fases?** Veja [sdlc/overview](sdlc/overview.md)
4. **Problema ou erro?** Veja [troubleshooting](guides/troubleshooting.md)

## Relacao com agentes e skills

Os agentes do SDLC Agentico consultam esta documentacao como fonte de verdade:

- Agentes de implementacao consultam `engineering-playbook/` para padroes
- Agentes de arquitetura consultam `stacks/` para decisoes de tecnologia
- Agentes de qualidade consultam `manual-desenvolvimento/qualidade.md` para criterios
