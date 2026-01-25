# Badges do Projeto - SDLC Agêntico

Este documento explica todos os badges exibidos no README.md do projeto.

## 📊 Visão Geral

O projeto exibe **17 badges** organizados em 4 categorias:
- **Core Badges** (3) - Informações essenciais
- **AI Compatibility** (2) - Compatibilidade com ferramentas IA
- **CI/CD & Quality** (3) - Status de pipelines e qualidade
- **Community & Stats** (4) - Estatísticas da comunidade
- **Maintenance & Activity** (3) - Atividade e manutenção

---

## 🎯 Core Badges

### License: MIT
```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```
- **O que mostra**: Licença do projeto (MIT)
- **Por que importante**: Indica que o projeto é open source e pode ser usado livremente
- **Cor**: Amarelo
- **Status**: Estático (não muda)

### Version
```markdown
[![Version](https://img.shields.io/badge/version-1.7.16-red.svg)](https://github.com/arbgjr/sdlc_agentico/releases/tag/v1.7.16)
```
- **O que mostra**: Versão atual do framework
- **Por que importante**: Usuários sabem qual versão estão usando/baixando
- **Cor**: Vermelho
- **Status**: Atualizado manualmente a cada release
- **Link**: Vai para a página de release no GitHub

### Python
```markdown
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
```
- **O que mostra**: Versão mínima do Python requerida
- **Por que importante**: Requisito técnico claro para instalação
- **Cor**: Azul
- **Status**: Estático (atualizado apenas quando mudamos requisito)

---

## 🤖 AI Compatibility Badges

### Claude Code
```markdown
[![Claude Code](https://img.shields.io/badge/Compatible%20with%20Claude%20Code-white?logo=claude)](https://code.claude.com/docs/en/sub-agents)
```
- **O que mostra**: Compatibilidade com Claude Code CLI
- **Por que importante**: Principal ferramenta para usar o framework
- **Cor**: Branco com logo Claude
- **Link**: Documentação oficial do Claude Code

### GitHub Copilot
```markdown
[![Github Copilot](https://img.shields.io/badge/Compatible%20with%20Github%20Copilot-black?logo=githubcopilot)](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
```
- **O que mostra**: Compatibilidade com GitHub Copilot Coding Agent
- **Por que importante**: Integração automática para implementação via Copilot
- **Cor**: Preto com logo GitHub Copilot
- **Link**: Documentação sobre Agent Skills

---

## ✅ CI/CD & Quality Badges

### Doc Validation
```markdown
[![Doc Validation](https://github.com/arbgjr/sdlc_agentico/actions/workflows/validate-docs.yml/badge.svg)](https://github.com/arbgjr/sdlc_agentico/actions/workflows/validate-docs.yml)
```
- **O que mostra**: Status do workflow de validação de documentação
- **Estados possíveis**:
  - ✅ **Passing** (verde) - Todas as validações passaram
  - ❌ **Failing** (vermelho) - Uma ou mais validações falharam
  - 🟡 **Running** (amarelo) - Workflow em execução
- **O que valida**:
  - Contagens de agentes, skills, hooks, comandos
  - Referências ao nome antigo do repositório
  - Links quebrados
  - Consistência de versão Python
- **Atualização**: Automática a cada push/PR
- **Link**: Vai para a página do workflow

### CI
```markdown
[![CI](https://github.com/arbgjr/sdlc_agentico/actions/workflows/ci.yml/badge.svg)](https://github.com/arbgjr/sdlc_agentico/actions/workflows/ci.yml)
```
- **O que mostra**: Status do workflow principal de CI
- **O que executa**:
  - Linting de código
  - Testes unitários
  - Verificação de segurança
  - Build do projeto
- **Atualização**: Automática a cada push/PR
- **Link**: Vai para a página do workflow

### Release
```markdown
[![Release](https://github.com/arbgjr/sdlc_agentico/actions/workflows/release.yml/badge.svg)](https://github.com/arbgjr/sdlc_agentico/actions/workflows/release.yml)
```
- **O que mostra**: Status do workflow de release
- **O que executa**:
  - Criação de releases automatizadas
  - Publicação de assets
  - Atualização de CHANGELOG
- **Atualização**: Automática quando uma tag é criada
- **Link**: Vai para a página do workflow

---

## 👥 Community & Stats Badges

### GitHub Stars
```markdown
[![GitHub Stars](https://img.shields.io/github/stars/arbgjr/sdlc_agentico?style=social)](https://github.com/arbgjr/sdlc_agentico/stargazers)
```
- **O que mostra**: Número de stars do repositório
- **Por que importante**: Indica popularidade e engajamento da comunidade
- **Estilo**: Social (estilo GitHub)
- **Atualização**: Automática (shields.io puxa do GitHub)
- **Link**: Lista de stargazers

### GitHub Forks
```markdown
[![GitHub Forks](https://img.shields.io/github/forks/arbgjr/sdlc_agentico?style=social)](https://github.com/arbgjr/sdlc_agentico/network/members)
```
- **O que mostra**: Número de forks do repositório
- **Por que importante**: Indica quantas pessoas estão usando/modificando o projeto
- **Estilo**: Social
- **Atualização**: Automática
- **Link**: Network graph

### GitHub Issues
```markdown
[![GitHub Issues](https://img.shields.io/github/issues/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/issues)
```
- **O que mostra**: Número de issues abertas
- **Por que importante**:
  - Transparência sobre bugs/features pendentes
  - Indicador de atividade do projeto
- **Cor**: Dinâmica (verde/amarelo/vermelho baseado em quantidade)
- **Atualização**: Automática
- **Link**: Lista de issues

### GitHub Pull Requests
```markdown
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/pulls)
```
- **O que mostra**: Número de PRs abertos
- **Por que importante**: Indicador de contribuições ativas
- **Cor**: Dinâmica
- **Atualização**: Automática
- **Link**: Lista de PRs

---

## 🔧 Maintenance & Activity Badges

### Last Commit
```markdown
[![Last Commit](https://img.shields.io/github/last-commit/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/commits/main)
```
- **O que mostra**: Data do último commit no branch main
- **Por que importante**: Indica se o projeto está ativo
- **Formato**: Tempo relativo (e.g., "2 days ago")
- **Atualização**: Automática
- **Link**: Histórico de commits

### Maintenance
```markdown
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/arbgjr/sdlc_agentico/graphs/commit-activity)
```
- **O que mostra**: Status de manutenção do projeto
- **Estados possíveis**:
  - ✅ **Yes** (verde) - Projeto mantido ativamente
  - ⚠️ **Deprecated** (amarelo) - Projeto deprecado mas funcional
  - ❌ **No** (vermelho) - Projeto não mantido
- **Status atual**: Yes (verde)
- **Atualização**: Manual (quando status de manutenção mudar)
- **Link**: Gráfico de atividade de commits

### Contributors
```markdown
[![Contributors](https://img.shields.io/github/contributors/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/graphs/contributors)
```
- **O que mostra**: Número de contribuidores do projeto
- **Por que importante**: Indica colaboração e diversidade de contribuições
- **Atualização**: Automática
- **Link**: Gráfico de contribuidores

---

## 🎨 Customização de Badges

### Usando Shields.io

Todos os badges (exceto GitHub Actions) usam [shields.io](https://shields.io). Para customizar:

```markdown
![Nome](https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>.svg)
```

**Parâmetros**:
- `LABEL`: Texto à esquerda (ex: "version")
- `MESSAGE`: Texto à direita (ex: "1.7.16")
- `COLOR`: Cor do badge (ex: "red", "green", "#ff0000")

**Estilos disponíveis**:
- `?style=flat` (padrão)
- `?style=flat-square`
- `?style=plastic`
- `?style=for-the-badge`
- `?style=social`

### Badges Dinâmicos do GitHub

Para informações do GitHub:
```markdown
https://img.shields.io/github/<METRIC>/<USER>/<REPO>
```

**Métricas disponíveis**:
- `stars` - Número de stars
- `forks` - Número de forks
- `issues` - Issues abertas
- `issues-pr` - PRs abertos
- `last-commit` - Último commit
- `contributors` - Número de contribuidores
- `commit-activity/<PERIOD>` - Atividade (period: y, m, w)
- `license` - Licença do projeto
- `languages/top` - Linguagem principal
- `repo-size` - Tamanho do repositório
- `code-size` - Tamanho do código

---

## 📝 Badges Adicionais (Opcionais)

### Code Size
```markdown
[![Code Size](https://img.shields.io/github/languages/code-size/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico)
```
Mostra o tamanho total do código no repositório.

### Top Language
```markdown
[![Top Language](https://img.shields.io/github/languages/top/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico)
```
Mostra a linguagem de programação dominante no projeto.

### Commit Activity
```markdown
[![Commit Activity](https://img.shields.io/github/commit-activity/m/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/graphs/commit-activity)
```
Mostra média de commits por mês.

### Downloads (Releases)
```markdown
[![Downloads](https://img.shields.io/github/downloads/arbgjr/sdlc_agentico/total)](https://github.com/arbgjr/sdlc_agentico/releases)
```
Mostra total de downloads de releases.

### Release Date
```markdown
[![Release Date](https://img.shields.io/github/release-date/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/releases)
```
Mostra data do último release.

---

## 🔍 Monitoramento de Badges

### Como verificar se badges estão funcionando

1. **Visualmente**: Abra o README.md no GitHub e veja se todos os badges aparecem
2. **Links**: Clique em cada badge para verificar se o link está correto
3. **Status**: Badges dinâmicos (CI, Issues, Stars) atualizam automaticamente

### Troubleshooting

**Badge mostra "unknown" ou "invalid":**
- Verifique se o nome do repositório está correto
- Verifique se o workflow existe no caminho especificado
- Para GitHub Actions, o workflow precisa ter rodado pelo menos uma vez

**Badge não atualiza:**
- Shields.io tem cache de ~5 minutos
- Adicione `?cache=300` à URL para forçar atualização
- Exemplo: `?cache=300&style=flat`

**Badge mostra erro 404:**
- Verifique se o repositório é público
- Verifique se o workflow/arquivo existe
- Para repositórios privados, alguns badges não funcionam

---

## 📚 Referências

- [Shields.io Documentation](https://shields.io/)
- [GitHub Badges Guide](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge)
- [Simple Icons (logos)](https://simpleicons.org/)
- [Markdown Badges Guide](https://github.com/Ileriayo/markdown-badges)

---

**Mantido por**: Equipe SDLC Agêntico
**Última atualização**: 2026-01-21
