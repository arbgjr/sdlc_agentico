#!/bin/bash
#
# clean-test-repo.sh
# Limpa um repositório de teste, mantendo apenas LICENSE e README.md
#
# Uso:
#   ./.scripts/clean-test-repo.sh [REPO_PATH]
#
# Se REPO_PATH não for fornecido, usa o diretório atual.
#

set -e

# Determinar caminho do repositório
REPO_PATH="${1:-$(pwd)}"

# Validar que é um repositório git
if [[ ! -d "$REPO_PATH/.git" ]]; then
    echo "Erro: $REPO_PATH não é um repositório git"
    exit 1
fi

cd "$REPO_PATH" || exit 1

echo "=== Limpando Repositório de Teste ==="
echo "Path: $REPO_PATH"
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# 1. Fazer checkout do LICENSE se existir no git
echo "[1/5] Restaurando LICENSE..."
git checkout LICENSE 2>/dev/null || echo "LICENSE não existe no git"

# 2. Salvar conteúdo original do README.md se existir
README_CONTENT=""
if [[ -f "README.md" ]]; then
    # Verificar se é o README original (não o do mice_dolphins)
    if grep -q "SDLC Agêntico" README.md 2>/dev/null; then
        echo "[2/5] README.md contém conteúdo do mice_dolphins, será recriado"
    else
        README_CONTENT=$(cat README.md)
        echo "[2/5] README.md original preservado"
    fi
else
    echo "[2/5] README.md não existe"
fi

# 3. Remover todos os arquivos e diretórios exceto .git, LICENSE
echo "[3/5] Removendo arquivos..."
find . -mindepth 1 -maxdepth 1 \
    ! -name '.git' \
    ! -name 'LICENSE' \
    -exec rm -rf {} \; 2>/dev/null || true

# 4. Limpar arquivos não rastreados pelo git
echo "[4/5] Limpando arquivos não rastreados..."
git clean -fd 2>/dev/null || true

# 5. Criar/restaurar README.md
echo "[5/5] Criando README.md..."
if [[ -n "$README_CONTENT" ]]; then
    echo "$README_CONTENT" > README.md
else
    # Criar README.md padrão baseado no nome do repositório
    REPO_NAME=$(basename "$REPO_PATH")
    cat > README.md << EOF
# ${REPO_NAME^}

Projeto em desenvolvimento usando SDLC Agêntico.

## Status

Aguardando início do ciclo de desenvolvimento.

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.
EOF
fi

echo ""
echo "=== Limpeza Concluída ==="
echo "Estado atual do repositório:"
ls -la

# Mostrar status git
echo ""
echo "Git status:"
git status --short
