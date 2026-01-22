# GitHub Actions - Tests v2.0

## Configuração da Badge Dinâmica

### 1. Criar GitHub Personal Access Token

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token" (classic)
3. Dê permissão de **gist** (create/update gists)
4. Copie o token gerado

### 2. Criar um Gist para armazenar a badge

1. Acesse: https://gist.github.com/
2. Crie um novo gist (pode ser público ou secreto)
3. Nome do arquivo: `sdlc-agentico-tests.json`
4. Conteúdo inicial:
   ```json
   {
     "schemaVersion": 1,
     "label": "tests",
     "message": "0/0 passing",
     "color": "lightgrey"
   }
   ```
5. Copie o **Gist ID** da URL (ex: `abc123def456`)

### 3. Adicionar secrets ao repositório

1. Vá em: Settings → Secrets and variables → Actions
2. Adicione o secret:
   - **Name:** `GIST_SECRET`
   - **Value:** [seu token do passo 1]

### 4. Atualizar workflow com o Gist ID

Edite `.github/workflows/test-v2.yml`:

```yaml
gistID: YOUR_GIST_ID_HERE  # Substitua pelo ID do passo 2
```

### 5. Usar a badge no README

Após o primeiro run da Action:

```markdown
[![Tests](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/YOUR_USERNAME/YOUR_GIST_ID/raw/sdlc-agentico-tests.json)](https://github.com/arbgjr/sdlc_agentico/actions/workflows/test-v2.yml)
```

## Como funciona

1. **Trigger:** Push em main ou PRs, ou manual via `workflow_dispatch`
2. **Testes executados:**
   - Integration tests (9 tests)
   - Simple memory tests (4 tests)
   - Session handoff tests (1 test)
   - **Total:** 14 testes automatizados

3. **Badge atualizada automaticamente:**
   - Verde: 100% passing
   - Amarelo: 60-99% passing
   - Vermelho: <60% passing

4. **Artefatos:**
   - `test-summary.md` - Resumo dos testes
   - `test-output.txt` - Output completo

## Executar manualmente

Vá em: Actions → Tests v2.0 → Run workflow

## Alternativa sem Gist (shields.io estático)

Se não quiser configurar Gist, pode usar badge estática:

```markdown
[![Tests](https://github.com/arbgjr/sdlc_agentico/actions/workflows/test-v2.yml/badge.svg)](https://github.com/arbgjr/sdlc_agentico/actions/workflows/test-v2.yml)
```

Essa badge mostrará apenas "passing" ou "failing" do último run.
