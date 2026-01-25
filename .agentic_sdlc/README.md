# SDLC Agêntico - Framework Assets

Este diretório contém todos os assets do framework SDLC Agêntico, que são **reutilizáveis** entre múltiplos projetos.

## Estrutura

```
.agentic_sdlc/
├── templates/         # Templates reutilizáveis (ADR, spec, threat-model)
├── schemas/           # Schemas JSON para validação de dados
├── examples/          # Exemplos de artifacts
├── docs/              # Documentação do framework
│   ├── guides/        # Guias de uso (quickstart, troubleshooting)
│   ├── sdlc/          # Documentação SDLC (agents, commands)
│   └── engineering-playbook/  # Padrões e práticas
├── scripts/           # Scripts de setup e utilitários
└── logo.png           # Logo do framework
```

## Instalação

O framework é instalado via script de setup:

```bash
./.agentic_sdlc/scripts/setup-sdlc.sh
```

## Reutilização em Múltiplos Projetos

Para usar o mesmo framework em vários projetos, crie symlinks:

```bash
cd ~/projects/my-project
ln -s ~/sdlc-agentico/.claude .claude
ln -s ~/sdlc-agentico/.agentic_sdlc .agentic_sdlc
mkdir -p .project
```

## Separação Framework vs Projeto

- **Framework** (`.agentic_sdlc/`): Assets reutilizáveis, versionados neste repositório
- **Projeto** (`.project/`): Artifacts específicos do projeto (corpus, decisions, reports)

Esta separação permite:
- ✅ Reutilizar framework em N projetos
- ✅ Portabilidade (copiar 2 diretórios = framework pronto)
- ✅ Gitignore seletivo (versionar decisions, ignorar sessions)
- ✅ Clareza (desenvolvedor sabe o que é framework vs projeto)

## Versionamento

O framework segue [Semantic Versioning](https://semver.org/):
- **Major**: Breaking changes, mudanças arquiteturais
- **Minor**: Novas features, novos agentes
- **Patch**: Bug fixes, documentação

Veja `.claude/VERSION` para versão atual.
