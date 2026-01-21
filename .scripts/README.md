# Scripts de Automação - SDLC Agêntico

Este diretório contém scripts de automação para manutenção e validação do projeto.

## 📋 Índice

- [Validação de Documentação](#validação-de-documentação)
- [Atualização Automática](#atualização-automática)
- [CI/CD](#cicd)
- [Outros Scripts](#outros-scripts)

---

## 🔍 Validação de Documentação

### `validate-doc-counts.sh`

Valida que as contagens de componentes na documentação estão corretas e consistentes.

**Uso:**
```bash
./.scripts/validate-doc-counts.sh [--verbose]
```

**O que valida:**
- ✅ Contagens de agentes, skills, hooks e comandos no README.md e CLAUDE.md
- ✅ Referências ao nome antigo do repositório (`mice_dolphins`)
- ✅ Links e arquivos documentados
- ✅ Consistência de versão Python (3.11+)

**Exit codes:**
- `0` - Todas as validações passaram
- `1` - Uma ou mais validações falharam

**Exemplo de saída:**
```
[INFO] Counting framework components...
[✓] README.md counts are correct
[✓] CLAUDE.md counts are correct
[✓] No old repository name references found
[✓] All documentation links are valid
[✓] Python version is consistent (3.11+)

✓ All validations passed!

Component counts:
  - Agents: 36
  - Skills: 23
  - Hooks: 18
  - Commands: 20
```

---

## 🔄 Atualização Automática

### `update-doc-counts.sh`

Atualiza automaticamente as contagens de componentes na documentação.

**Uso:**
```bash
./.scripts/update-doc-counts.sh [--dry-run] [--verbose]
```

**Opções:**
- `--dry-run` - Mostra as mudanças sem aplicá-las
- `--verbose` - Mostra saída detalhada

**O que atualiza:**
- README.md:
  - Linha ~17: Descrição principal com contagem de agentes
  - Linha ~28: Diagrama ASCII com contagem de agentes
  - Linhas ~308-311: Estrutura do projeto (agentes, skills, hooks, comandos)
- CLAUDE.md:
  - Linha ~7: Descrição principal com contagem de agentes
  - Linha ~93: Seção de configuração
  - Linha ~102: Estrutura do projeto
  - Linha ~185: Tabela de tipos de agentes

**Workflow recomendado:**
```bash
# 1. Ver o que seria mudado
./.scripts/update-doc-counts.sh --dry-run

# 2. Aplicar as mudanças
./.scripts/update-doc-counts.sh

# 3. Revisar as mudanças
git diff README.md CLAUDE.md

# 4. Commitar se satisfeito
git add README.md CLAUDE.md
git commit -m "docs: update component counts"
```

**Saída de exemplo (dry-run):**
```
[INFO] Counting framework components...
[✓] Component counts:
   - Agents: 36
   - Skills: 23
   - Hooks: 18
   - Commands: 20

[DRY-RUN] Would update README.md:
   Pattern: \*\*[0-9]\+ agentes especializados\*\*
   Replace: **36 agentes especializados** (32 orquestrados + 4 consultivos)
...
```

---

## 🤖 CI/CD

### GitHub Actions Workflow: `validate-docs.yml`

Workflow automático que roda a cada push ou pull request validando a documentação.

**Localização:** `.github/workflows/validate-docs.yml`

**Triggers:**
- Push para branches: `main`, `develop`, `feature/**`
- Pull requests para: `main`, `develop`
- Mudanças em: documentação (README.md, CLAUDE.md), agentes, skills, comandos, hooks

**Jobs executados:**
1. **Count components** - Conta todos os componentes automaticamente
2. **Validate README.md** - Verifica contagens em múltiplos locais
3. **Validate CLAUDE.md** - Verifica contagens e referências
4. **Check for old repository name** - Detecta `mice_dolphins`
5. **Validate links** - Verifica se arquivos documentados existem
6. **Check Python version** - Valida consistência de versão Python
7. **Validate version references** - Detecta referências desatualizadas

**Saída no GitHub:**
O workflow cria um resumo no GitHub Actions com:
- ✅ Status de cada validação
- 📊 Contagens atuais de componentes
- ❌ Erros encontrados (se houver)

**Exemplo de erro:**
```
::error file=README.md,line=17::Agent count mismatch. Found 36 agents but README declares 34
```

---

## 📝 Outros Scripts

### `setup-sdlc.sh`

Script de instalação principal do SDLC Agêntico.

**Uso:**
```bash
./.scripts/setup-sdlc.sh [--from-release] [--version VERSION]
```

### `install-security-tools.sh`

Instala ferramentas de segurança opcionais (Semgrep, Trivy, Gitleaks).

**Uso:**
```bash
./.scripts/install-security-tools.sh [--all|--semgrep|--trivy|--gitleaks]
```

---

## 🔧 Manutenção

### Quando adicionar novo componente

Sempre que você adicionar:
- Um novo agente (`.claude/agents/*.md`)
- Uma nova skill (`.claude/skills/*/`)
- Um novo hook (`.claude/hooks/*.sh`)
- Um novo comando (`.claude/commands/*.md`)

**Siga este processo:**

```bash
# 1. Adicionar o componente
# ... crie o arquivo ...

# 2. Atualizar contagens automaticamente
./.scripts/update-doc-counts.sh

# 3. Validar que está correto
./.scripts/validate-doc-counts.sh

# 4. Commitar tudo junto
git add .
git commit -m "feat(agents): add new xyz-agent

- Implement xyz-agent for phase N
- Update documentation counts automatically
"
```

### Integração com Pre-Commit Hook

Para executar validação automaticamente antes de cada commit:

```bash
# .git/hooks/pre-commit
#!/bin/bash
./.scripts/validate-doc-counts.sh
exit $?
```

---

## 🐛 Troubleshooting

### Validação falha após adicionar componente

```bash
# Execute o script de atualização
./.scripts/update-doc-counts.sh

# Depois valide novamente
./.scripts/validate-doc-counts.sh
```

### Script diz "Permission denied"

```bash
# Tornar scripts executáveis
chmod +x .scripts/*.sh
```

### Referências ao nome antigo do repositório

```bash
# Encontrar todas as referências
grep -r "mice_dolphins" --exclude-dir=.git --exclude-dir=.venv .

# Substituir globalmente (use com cuidado)
find . -type f \( -name "*.md" -o -name "*.json" -o -name "*.sh" \) \
  -exec sed -i 's|mice_dolphins|sdlc_agentico|g' {} +
```

### CI falha mas validação local passa

Verifique:
1. Todos os arquivos foram commitados
2. Não há diferenças entre local e remoto
3. O workflow está usando a versão correta dos scripts

```bash
# Comparar arquivos
git diff origin/main -- README.md CLAUDE.md

# Forçar push se necessário (com cuidado)
git push --force-with-lease
```

---

## 📚 Referências

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Shell Script Best Practices](https://google.github.io/styleguide/shellguide.html)

---

**Mantido por:** Equipe SDLC Agêntico
**Última atualização:** 2026-01-21
