#!/bin/bash
#
# Setup Script para SDLC Agentico
# Instala todas as dependencias necessarias para o workflow
#
# Uso:
#   # Instalacao completa do zero (requer repositorio clonado)
#   ./\.agentic_sdlc/scripts/setup-sdlc.sh
#
#   # Instalacao a partir de uma release
#   curl -fsSL https://raw.githubusercontent.com/arbgjr/sdlc_agentico/main/\.agentic_sdlc/scripts/setup-sdlc.sh | bash -s -- --from-release
#
#   # Instalacao de versao especifica
#   curl -fsSL https://raw.githubusercontent.com/arbgjr/sdlc_agentico/main/\.agentic_sdlc/scripts/setup-sdlc.sh | bash -s -- --from-release --version v1.0.0
#

set -e

# Configuracoes
REPO_OWNER="arbgjr"
REPO_NAME="sdlc_agentico"
REPO_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Funcoes de log
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_question() { echo -e "${CYAN}[?]${NC} $1"; }

# Show splash screen
show_splash() {
    # Get script directory (where setup-sdlc.sh is located)
    local SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local FRAMEWORK_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

    # Try to find splash.py
    local SPLASH_PATH=""

    # Priority 1: Relative to framework root (most reliable)
    if [[ -f "$FRAMEWORK_ROOT/.agentic_sdlc/splash.py" ]]; then
        SPLASH_PATH="$FRAMEWORK_ROOT/.agentic_sdlc/splash.py"
    # Priority 2: Relative to current directory (if running from project root)
    elif [[ -f ".agentic_sdlc/splash.py" ]]; then
        SPLASH_PATH=".agentic_sdlc/splash.py"
    fi

    if [[ -n "$SPLASH_PATH" && -f "$SPLASH_PATH" ]]; then
        python3 "$SPLASH_PATH" --no-animate || {
            # Fallback to simple banner if splash.py fails
            echo ""
            echo "========================================"
            echo "   SDLC Agentico - Setup Script"
            echo "========================================"
            echo ""
        }
    else
        # Simple banner if splash.py not found
        echo ""
        echo "========================================"
        echo "   SDLC Agentico - Setup Script"
        echo "========================================"
        echo ""
    fi
}

# Header
show_splash

# Give user time to see splash before scrolling with logs
sleep 2

# Variaveis de opcoes
FROM_RELEASE=false
VERSION="latest"
SKIP_DEPS=false
FORCE_UPDATE=false

# Parse de argumentos
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --from-release)
                FROM_RELEASE=true
                shift
                ;;
            --version)
                VERSION="$2"
                shift 2
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --force)
                FORCE_UPDATE=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                log_error "Opcao desconhecida: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Mostrar uso
show_usage() {
    echo "Uso: $0 [opcoes]"
    echo ""
    echo "Opcoes:"
    echo "  --from-release      Instala a partir de uma release do GitHub"
    echo "  --version <tag>     Especifica versao (ex: v1.0.0). Padrao: latest"
    echo "  --skip-deps         Pula instalacao de dependencias (Python, Node, etc)"
    echo "  --force             Força atualização sem perguntar"
    echo "  --help              Mostra esta mensagem"
    echo ""
    echo "Exemplos:"
    echo "  # Instalacao local (apos clonar repo ou baixar release)"
    echo "  ./.agentic_sdlc/scripts/setup-sdlc.sh"
    echo ""
    echo "  # Instalacao remota (ultima release)"
    echo "  curl -fsSL ${REPO_URL}/raw/main/.agentic_sdlc/scripts/setup-sdlc.sh | bash -s -- --from-release"
    echo ""
    echo "  # Instalacao de versao especifica"
    echo "  curl -fsSL ${REPO_URL}/raw/main/.agentic_sdlc/scripts/setup-sdlc.sh | bash -s -- --from-release --version v1.0.0"
    echo ""
}

# Detectar OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        log_error "Sistema operacional nao suportado: $OSTYPE"
        exit 1
    fi
    log_info "Sistema detectado: $OS"
}

# Detectar versão instalada
detect_installed_version() {
    local INSTALLED_VERSION=""

    # Método 1: Ler .claude/VERSION
    if [[ -f ".claude/VERSION" ]]; then
        INSTALLED_VERSION=$(grep "^version:" .claude/VERSION 2>/dev/null | awk '{print $2}' | tr -d '"')
    fi

    # Método 2: Git tag (se for repo git)
    if [[ -z "$INSTALLED_VERSION" && -d ".git" ]]; then
        INSTALLED_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    fi

    # Método 3: Verificar diretório .agentic_sdlc
    if [[ -z "$INSTALLED_VERSION" && -d ".agentic_sdlc" ]]; then
        INSTALLED_VERSION="unknown"
    fi

    echo "$INSTALLED_VERSION"
}

# Verificar se há artefatos de projeto em .agentic_sdlc
check_project_artifacts_in_agentic_sdlc() {
    if [[ ! -d ".agentic_sdlc" ]]; then
        return 1
    fi

    # Verificar se há artefatos que parecem ser do projeto (não do framework)
    local HAS_ARTIFACTS=false

    # Diretórios que indicam artefatos de projeto
    local PROJECT_DIRS=(
        ".agentic_sdlc/corpus/nodes/decisions"
        ".agentic_sdlc/architecture"
        ".agentic_sdlc/security"
        ".agentic_sdlc/reports"
    )

    for dir in "${PROJECT_DIRS[@]}"; do
        if [[ -d "$dir" ]]; then
            # Verificar se tem arquivos (não apenas .gitkeep)
            local FILE_COUNT=$(find "$dir" -type f ! -name ".gitkeep" 2>/dev/null | wc -l)
            if [[ $FILE_COUNT -gt 0 ]]; then
                HAS_ARTIFACTS=true
                break
            fi
        fi
    done

    if $HAS_ARTIFACTS; then
        return 0
    else
        return 1
    fi
}

# Migrar artefatos de projeto de .agentic_sdlc para .project
migrate_project_artifacts() {
    log_info "Iniciando migração de artefatos..."
    echo ""

    # Criar .project se não existir
    mkdir -p .project

    local MIGRATED_COUNT=0

    # Diretórios a migrar
    declare -A DIRS_TO_MIGRATE=(
        [".agentic_sdlc/corpus"]="corpus"
        [".agentic_sdlc/architecture"]="architecture"
        [".agentic_sdlc/security"]="security"
        [".agentic_sdlc/reports"]="reports"
        [".agentic_sdlc/references"]="references"
        [".agentic_sdlc/sessions"]="sessions"
    )

    for source_dir in "${!DIRS_TO_MIGRATE[@]}"; do
        local dest_name="${DIRS_TO_MIGRATE[$source_dir]}"
        local dest_dir=".project/$dest_name"

        if [[ -d "$source_dir" ]]; then
            # Verificar se tem conteúdo (além de .gitkeep)
            local FILE_COUNT=$(find "$source_dir" -type f ! -name ".gitkeep" 2>/dev/null | wc -l)

            if [[ $FILE_COUNT -gt 0 ]]; then
                log_info "Migrando $source_dir → $dest_dir"

                # Criar diretório destino
                mkdir -p "$dest_dir"

                # Copiar conteúdo (preservando estrutura)
                cp -r "$source_dir"/* "$dest_dir/" 2>/dev/null || true

                # Remover .gitkeep se existir no destino
                rm -f "$dest_dir/.gitkeep"

                MIGRATED_COUNT=$((MIGRATED_COUNT + 1))
                log_success "  ✓ Migrado: $(find "$source_dir" -type f | wc -l) arquivos"
            fi
        fi
    done

    if [[ $MIGRATED_COUNT -gt 0 ]]; then
        log_success "Migração completa: $MIGRATED_COUNT diretórios migrados"
        return 0
    else
        log_info "Nenhum artefato encontrado para migrar"
        return 1
    fi
}

# Limpar .agentic_sdlc (remover arquivos do framework e artefatos migrados)
clean_agentic_sdlc() {
    if [[ ! -d ".agentic_sdlc" ]]; then
        return 0
    fi

    log_info "Limpando artefatos de .agentic_sdlc/..."

    # Criar backup antes de limpar
    local BACKUP_DIR=".agentic_sdlc.backup-$(date +%Y%m%d-%H%M%S)"
    cp -r ".agentic_sdlc" "$BACKUP_DIR" 2>/dev/null || true

    if [[ -d "$BACKUP_DIR" ]]; then
        log_info "Backup criado em: $BACKUP_DIR"
    fi

    # CORRIGIDO: Remover APENAS artefatos, manter framework (scripts, templates, schemas, docs, logo.png, splash.py)
    local ARTIFACT_DIRS=(
        "corpus"
        "architecture"
        "security"
        "reports"
        "references"
        "sessions"
    )

    for dir in "${ARTIFACT_DIRS[@]}"; do
        if [[ -d ".agentic_sdlc/$dir" ]]; then
            log_info "  Removendo .agentic_sdlc/$dir/"
            rm -rf ".agentic_sdlc/$dir"
            mkdir -p ".agentic_sdlc/$dir"
            touch ".agentic_sdlc/$dir/.gitkeep"
        fi
    done

    log_success "Artefatos removidos (framework mantido)"
    log_info "Framework preservado: scripts/, templates/, schemas/, docs/, logo.png, splash.py"
}

# Confirmar atualização
confirm_update() {
    local CURRENT_VERSION="$1"
    local NEW_VERSION="$2"

    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           ATUALIZAÇÃO DO SDLC AGÊNTICO                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${YELLOW}Versão instalada:${NC} $CURRENT_VERSION"
    echo -e "${GREEN}Nova versão:${NC}      $NEW_VERSION"
    echo ""

    # Verificar se há artefatos de projeto em local errado
    if check_project_artifacts_in_agentic_sdlc; then
        echo -e "${YELLOW}⚠️  ATENÇÃO: Artefatos de projeto detectados em .agentic_sdlc/${NC}"
        echo ""
        echo "Foi detectado que este projeto possui artefatos em .agentic_sdlc/"
        echo "que deveriam estar em .project/ (REGRA DE OURO v2.1.7+)."
        echo ""
        echo "Artefatos encontrados:"

        # Listar artefatos
        for dir in corpus architecture security reports references; do
            if [[ -d ".agentic_sdlc/$dir" ]]; then
                local COUNT=$(find ".agentic_sdlc/$dir" -type f ! -name ".gitkeep" 2>/dev/null | wc -l)
                if [[ $COUNT -gt 0 ]]; then
                    echo "  • $dir/ ($COUNT arquivos)"
                fi
            fi
        done

        echo ""
        echo -e "${CYAN}O que deseja fazer?${NC}"
        echo ""
        echo "  [1] Migrar artefatos para .project/ e atualizar (RECOMENDADO)"
        echo "  [2] Continuar SEM migrar (PERDERÁ todos os artefatos!)"
        echo "  [3] Cancelar atualização"
        echo ""
        read -p "Escolha [1-3]: " migration_choice

        case $migration_choice in
            1)
                log_info "Opção selecionada: Migrar e atualizar"
                echo ""

                # Executar migração
                if migrate_project_artifacts; then
                    echo ""
                    log_success "Artefatos migrados com sucesso para .project/"

                    # Perguntar se pode limpar .agentic_sdlc
                    echo ""
                    log_question "Deseja remover .agentic_sdlc/ agora?"
                    echo "  (Um backup será criado antes da remoção)"
                    echo ""
                    read -p "Remover .agentic_sdlc/? [y/N]: " remove_old

                    if [[ "$remove_old" =~ ^[Yy]$ ]]; then
                        clean_agentic_sdlc
                    else
                        log_warn ".agentic_sdlc/ mantido. Remova manualmente após validar migração."
                    fi

                    return 0
                else
                    log_error "Falha na migração de artefatos"
                    return 1
                fi
                ;;
            2)
                echo ""
                echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
                echo -e "${RED}║                    ⚠️  AVISO CRÍTICO ⚠️                     ║${NC}"
                echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
                echo ""
                echo -e "${YELLOW}Você escolheu NÃO migrar os artefatos do projeto.${NC}"
                echo ""
                echo "Isso significa que você PERDERÁ:"
                echo "  • Todos os ADRs inferidos/convertidos"
                echo "  • Diagramas de arquitetura"
                echo "  • Threat models"
                echo "  • Reports de tech debt"
                echo "  • Referências e sessões"
                echo ""
                echo "TOTAL DE DADOS QUE SERÃO PERDIDOS:"
                local TOTAL_FILES=$(find .agentic_sdlc/{corpus,architecture,security,reports,references,sessions} -type f ! -name ".gitkeep" 2>/dev/null | wc -l)
                local TOTAL_SIZE=$(du -sh .agentic_sdlc 2>/dev/null | cut -f1)
                echo "  • Arquivos: $TOTAL_FILES"
                echo "  • Tamanho: $TOTAL_SIZE"
                echo ""
                echo -e "${RED}Esta ação é IRREVERSÍVEL!${NC}"
                echo ""
                read -p "Tem CERTEZA que deseja continuar SEM migrar? [y/N]: " confirm_loss

                if [[ "$confirm_loss" =~ ^[Yy]$ ]]; then
                    log_warn "Continuando SEM migração. Artefatos serão perdidos."

                    # Criar backup antes de deletar
                    clean_agentic_sdlc

                    return 0
                else
                    log_info "Atualização cancelada. Execute novamente e escolha opção 1 para migrar."
                    exit 0
                fi
                ;;
            3)
                log_info "Atualização cancelada pelo usuário."
                exit 0
                ;;
            *)
                log_error "Opção inválida. Atualização cancelada."
                exit 1
                ;;
        esac
    else
        # Sem artefatos de projeto, apenas confirmar atualização
        echo "A atualização irá:"
        echo "  • Atualizar framework de $CURRENT_VERSION → $NEW_VERSION"
        echo "  • Limpar .agentic_sdlc/ (se existir)"
        echo "  • Manter .project/ intacto"
        echo ""
        read -p "Deseja continuar com a atualização? [y/N]: " confirm

        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            # Limpar .agentic_sdlc se existir
            if [[ -d ".agentic_sdlc" ]]; then
                clean_agentic_sdlc
            fi
            return 0
        else
            log_info "Atualização cancelada pelo usuário."
            exit 0
        fi
    fi
}

# Verificar se .claude ja existe e perguntar ao usuario
check_existing_claude() {
    if [[ -d ".claude" ]]; then
        # Detectar versão instalada
        CURRENT_VERSION=$(detect_installed_version)

        if [[ -n "$CURRENT_VERSION" ]]; then
            # Versão detectada, perguntar sobre atualização
            if [[ "$FORCE_UPDATE" == "true" ]]; then
                log_info "Modo --force: atualizando sem perguntar"
                confirm_update "$CURRENT_VERSION" "$VERSION"
                return 0
            else
                # Perguntar se quer atualizar
                confirm_update "$CURRENT_VERSION" "$VERSION"
                return 0
            fi
        else
            # .claude existe mas versão não detectada
            echo ""
            log_warn "O diretorio .claude/ ja existe!"
            echo ""
            echo "O que deseja fazer?"
            echo "  [1] Fazer backup e substituir (recomendado)"
            echo "  [2] Mesclar (manter arquivos existentes, adicionar novos)"
            echo "  [3] Substituir sem backup"
            echo "  [4] Cancelar instalacao"
            echo ""
            read -p "Escolha [1-4]: " choice

            case $choice in
                1)
                    BACKUP_DIR=".claude.backup.$(date +%Y%m%d_%H%M%S)"
                    log_info "Criando backup em $BACKUP_DIR..."
                    mv .claude "$BACKUP_DIR"
                    log_success "Backup criado em $BACKUP_DIR"
                    return 0
                    ;;
                2)
                    log_info "Modo mescla selecionado. Arquivos existentes serao preservados."
                    MERGE_MODE=true
                    return 0
                    ;;
                3)
                    log_warn "Substituindo sem backup..."
                    rm -rf .claude
                    return 0
                    ;;
                4)
                    log_info "Instalacao cancelada pelo usuario."
                    exit 0
                    ;;
                *)
                    log_error "Opcao invalida. Cancelando."
                    exit 1
                    ;;
            esac
        fi
    fi
}

# Obter URL da release
get_release_url() {
    if [[ "$VERSION" == "latest" ]]; then
        log_info "Obtendo ultima release..."
        RELEASE_URL=$(curl -s "https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest" | grep "browser_download_url.*\.zip" | cut -d'"' -f4)

        if [[ -z "$RELEASE_URL" ]]; then
            log_error "Nenhuma release encontrada."
            log_info "Verifique se existem releases em: ${REPO_URL}/releases"
            exit 1
        fi

        VERSION=$(echo "$RELEASE_URL" | grep -oP 'v[\d.]+')
        log_success "Versao mais recente: $VERSION"
    else
        log_info "Obtendo release $VERSION..."
        RELEASE_URL="${REPO_URL}/releases/download/${VERSION}/sdlc-agentico-${VERSION}.zip"

        # Verificar se existe
        if ! curl --output /dev/null --silent --head --fail "$RELEASE_URL"; then
            log_error "Release $VERSION nao encontrada."
            log_info "Verifique releases disponiveis em: ${REPO_URL}/releases"
            exit 1
        fi
    fi

    echo "$RELEASE_URL"
}

# Baixar e extrair release
install_from_release() {
    log_info "Instalando a partir de release..."

    # Verificar se .claude ja existe
    check_existing_claude

    # Obter URL
    RELEASE_URL=$(get_release_url)
    log_info "Baixando: $RELEASE_URL"

    # Criar diretorio temporario
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    # Download
    curl -sSL "$RELEASE_URL" -o "$TEMP_DIR/sdlc.zip"

    # Extrair
    log_info "Extraindo arquivos..."

    if [[ "$MERGE_MODE" == "true" ]]; then
        # Modo mescla: extrair para temp e copiar apenas arquivos que nao existem
        unzip -q "$TEMP_DIR/sdlc.zip" -d "$TEMP_DIR/extracted"

        # Copiar com merge
        for item in "$TEMP_DIR/extracted/"*; do
            BASE_NAME=$(basename "$item")
            if [[ -e "$BASE_NAME" ]]; then
                if [[ -d "$item" ]]; then
                    # Mesclar diretorios
                    cp -rn "$item"/* "$BASE_NAME/" 2>/dev/null || true
                else
                    log_warn "Pulando $BASE_NAME (ja existe)"
                fi
            else
                cp -r "$item" .
            fi
        done
    else
        # Modo normal: extrair diretamente
        unzip -q "$TEMP_DIR/sdlc.zip" -d .
    fi

    log_success "Arquivos extraidos com sucesso"
}

# Verificar Python
check_python() {
    log_info "Verificando Python..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
        MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)

        if [[ "$MAJOR" -ge 3 && "$MINOR" -ge 11 ]]; then
            log_success "Python $PYTHON_VERSION instalado"
            return 0
        else
            log_warn "Python $PYTHON_VERSION encontrado, mas 3.11+ e necessario"
        fi
    fi

    log_info "Instalando Python 3.11+..."
    if [[ "$OS" == "macos" ]]; then
        brew install python@3.11
    elif [[ "$OS" == "linux" ]]; then
        sudo apt-get update && sudo apt-get install -y python3.11 python3.11-venv
    fi
    log_success "Python instalado"
}

# Instalar uv
install_uv() {
    log_info "Verificando uv..."

    if command -v uv &> /dev/null; then
        log_success "uv ja instalado: $(uv --version)"
        return 0
    fi

    log_info "Instalando uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Adicionar ao PATH
    if [[ -f "$HOME/.local/bin/uv" ]]; then
        export PATH="$HOME/.local/bin:$PATH"
    fi

    log_success "uv instalado"
}

# Instalar Spec Kit
install_speckit() {
    log_info "Verificando Spec Kit..."

    if command -v specify &> /dev/null; then
        log_success "Spec Kit ja instalado"
        return 0
    fi

    log_info "Instalando Spec Kit do GitHub..."
    uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

    log_success "Spec Kit instalado"
}

# Verificar Git
check_git() {
    log_info "Verificando Git..."

    if command -v git &> /dev/null; then
        log_success "Git instalado: $(git --version)"
        return 0
    fi

    log_info "Instalando Git..."
    if [[ "$OS" == "macos" ]]; then
        brew install git
    elif [[ "$OS" == "linux" ]]; then
        sudo apt-get install -y git
    fi
    log_success "Git instalado"
}

# Verificar GitHub CLI
check_gh() {
    log_info "Verificando GitHub CLI..."

    if command -v gh &> /dev/null; then
        log_success "GitHub CLI instalado: $(gh --version | head -n1)"

        # Verificar autenticacao
        if gh auth status &> /dev/null; then
            log_success "GitHub CLI autenticado"
            # Verificar scope project para GitHub Projects V2
            check_gh_project_scope
        else
            log_warn "GitHub CLI nao autenticado. Execute: gh auth login"
        fi
        return 0
    fi

    log_info "Instalando GitHub CLI..."
    if [[ "$OS" == "macos" ]]; then
        brew install gh
    elif [[ "$OS" == "linux" ]]; then
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt update && sudo apt install gh -y
    fi
    log_success "GitHub CLI instalado"
    log_warn "Execute 'gh auth login' para autenticar"
}

# Verificar scope project para GitHub Projects V2
check_gh_project_scope() {
    log_info "Verificando scope 'project' para GitHub Projects V2..."

    # Verificar se está autenticado
    if ! gh auth status &> /dev/null; then
        log_warn "GitHub CLI não autenticado. Execute 'gh auth login' primeiro."
        return 1
    fi

    # Verificar scopes atuais usando gh auth status
    local AUTH_OUTPUT=$(gh auth status 2>&1)

    # Procurar por "Token scopes" na saída
    if echo "$AUTH_OUTPUT" | grep -qi "project"; then
        log_success "Scope 'project' disponível"
        return 0
    fi

    # Verificar via API diretamente (método mais confiável)
    local SCOPES=$(gh api user -H "X-OAuth-Scopes: true" 2>&1 | head -1 || echo "")
    if echo "$SCOPES" | grep -qi "project"; then
        log_success "Scope 'project' disponível (via API)"
        return 0
    fi

    # Scope project não encontrado
    log_warn "Scope 'project' não encontrado"
    log_info "Este scope é necessário para gerenciar GitHub Projects V2"
    echo ""
    echo "O scope 'project' permite:"
    echo "  - Criar e gerenciar Projects V2"
    echo "  - Adicionar issues a Projects"
    echo "  - Atualizar campos customizados"
    echo "  - Mover items entre colunas"
    echo ""
    echo "Para adicionar o scope, execute:"
    echo "  gh auth refresh -s project"
    echo ""

    # Perguntar se quer adicionar agora
    read -p "Deseja adicionar o scope agora? [y/N]: " ADD_SCOPE
    if [[ "$ADD_SCOPE" =~ ^[Yy]$ ]]; then
        log_info "Executando 'gh auth refresh -s project'..."
        if gh auth refresh -s project; then
            log_success "Scope 'project' adicionado com sucesso"

            # Verificar novamente
            if gh api user -H "X-OAuth-Scopes: true" 2>&1 | grep -qi "project"; then
                log_success "Verificação: scope 'project' confirmado"
            fi
            return 0
        else
            log_error "Falha ao adicionar scope."
            log_info "Execute manualmente: gh auth refresh -s project"
            return 1
        fi
    else
        log_warn "Scope 'project' não adicionado. GitHub Projects V2 pode não funcionar."
        return 1
    fi
}

# Verificar Node.js (para Claude Code)
check_node() {
    log_info "Verificando Node.js..."

    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js instalado: $NODE_VERSION"
        return 0
    fi

    log_info "Instalando Node.js..."
    if [[ "$OS" == "macos" ]]; then
        brew install node
    elif [[ "$OS" == "linux" ]]; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    log_success "Node.js instalado"
}

# Instalar Claude Code
install_claude_code() {
    log_info "Verificando Claude Code..."

    if command -v claude &> /dev/null; then
        log_success "Claude Code ja instalado"
        return 0
    fi

    log_info "Instalando Claude Code..."
    npm install -g @anthropic-ai/claude-code
    log_success "Claude Code instalado"
}

# Inicializar projeto com Spec Kit
init_speckit() {
    log_info "Inicializando Spec Kit no projeto..."

    if [[ -d ".specify" ]]; then
        log_success "Projeto ja inicializado com Spec Kit"
        return 0
    fi

    log_info "Executando specify init..."
    specify init . --ai claude --force 2>/dev/null || {
        log_warn "Spec Kit init falhou (pode ser normal se diretorio nao estiver vazio)"
    }
}

# Verificar estrutura Claude Code
check_claude_structure() {
    log_info "Verificando estrutura .claude/..."

    if [[ -d ".claude" ]]; then
        AGENTS_COUNT=$(find .claude/agents -name "*.md" 2>/dev/null | wc -l)
        SKILLS_COUNT=$(find .claude/skills -name "SKILL.md" 2>/dev/null | wc -l)
        COMMANDS_COUNT=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l)

        log_success "Estrutura .claude/ encontrada:"
        log_info "  - Agentes: $AGENTS_COUNT"
        log_info "  - Skills: $SKILLS_COUNT"
        log_info "  - Comandos: $COMMANDS_COUNT"
    else
        log_warn "Diretorio .claude/ nao encontrado"
    fi
}

# Habilitar Copilot Coding Agent
enable_copilot_agent() {
    log_info "Configurando Copilot Coding Agent..."

    if ! gh auth status &> /dev/null; then
        log_warn "GitHub CLI nao autenticado. Pulando configuracao do Copilot Agent."
        return 0
    fi

    # Detectar repositorio
    REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null || echo "")

    if [[ -z "$REPO" ]]; then
        log_warn "Nao foi possivel detectar repositorio. Execute dentro de um repo Git."
        return 0
    fi

    log_info "Repositorio detectado: $REPO"

    # Tentar habilitar (pode falhar se nao tiver permissao)
    gh api "repos/$REPO" --method PATCH -f allow_copilot_coding_agent=true 2>/dev/null && {
        log_success "Copilot Coding Agent habilitado para $REPO"
    } || {
        log_warn "Nao foi possivel habilitar Copilot Agent. Verifique permissoes."
    }
}

# Verificar dependencias
run_checks() {
    log_info "Executando verificacao de dependencias..."

    echo ""
    if command -v specify &> /dev/null; then
        specify check 2>/dev/null || log_warn "Algumas dependencias podem estar faltando"
    fi
    echo ""
}

# Tornar scripts executaveis
make_scripts_executable() {
    log_info "Configurando permissoes de scripts..."

    if [[ -d "\.agentic_sdlc/scripts" ]]; then
        chmod +x \.agentic_sdlc/scripts/*.sh 2>/dev/null || true
        log_success "Scripts em \.agentic_sdlc/scripts/ configurados"
    fi

    if [[ -d ".claude/hooks" ]]; then
        chmod +x .claude/hooks/*.sh 2>/dev/null || true
        log_success "Hooks em .claude/hooks/ configurados"
    fi

    # Configurar scripts das skills
    if [[ -d ".claude/skills" ]]; then
        find .claude/skills -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || true
        find .claude/skills -name "*.py" -type f -exec chmod +x {} \; 2>/dev/null || true
        log_success "Scripts das skills configurados"
    fi
}

# Verificar dependencias opcionais (document-processor e frontend-testing skills)
check_optional_deps() {
    log_info "Verificando dependencias opcionais dos skills..."
    echo ""

    # Verificar dependencias Python para document-processor
    local PYTHON_DEPS_MISSING=""

    for pkg in pdfplumber openpyxl python-docx pandas; do
        if python3 -c "import ${pkg//-/_}" 2>/dev/null; then
            log_success "Python: $pkg"
        else
            PYTHON_DEPS_MISSING="$PYTHON_DEPS_MISSING $pkg"
        fi
    done

    # Verificar Playwright
    if python3 -c "import playwright" 2>/dev/null; then
        log_success "Python: playwright"
    else
        PYTHON_DEPS_MISSING="$PYTHON_DEPS_MISSING playwright"
    fi

    # Verificar ferramentas de sistema
    echo ""
    log_info "Ferramentas de sistema (opcionais):"

    if command -v pdftotext &> /dev/null; then
        log_success "pdftotext (poppler-utils)"
    else
        log_warn "pdftotext nao instalado (apt install poppler-utils)"
    fi

    if command -v tesseract &> /dev/null; then
        log_success "tesseract (OCR)"
    else
        log_warn "tesseract nao instalado (apt install tesseract-ocr)"
    fi

    if command -v libreoffice &> /dev/null; then
        log_success "libreoffice (validacao XLSX)"
    else
        log_warn "libreoffice nao instalado (apt install libreoffice)"
    fi

    # Sugerir instalacao
    if [[ -n "$PYTHON_DEPS_MISSING" ]]; then
        echo ""
        log_info "Para instalar dependencias Python faltantes:"
        echo "  pip install$PYTHON_DEPS_MISSING"
    fi

    echo ""
}

# Setup Python virtualenv
setup_python_venv() {
    log_info "Configurando ambiente virtual Python..."
    echo ""

    # Criar .venv se não existir
    if [[ ! -d ".venv" ]]; then
        log_info "Criando virtualenv em .venv..."
        python3 -m venv .venv || {
            log_error "Falha ao criar virtualenv"
            exit 1
        }
        log_success "Virtualenv criado"
    else
        log_success "Virtualenv já existe"
    fi

    # Ativar virtualenv
    log_info "Ativando virtualenv..."
    source .venv/bin/activate || {
        log_error "Falha ao ativar virtualenv"
        exit 1
    }
    log_success "Virtualenv ativado"

    # Atualizar pip
    log_info "Atualizando pip..."
    python -m pip install --upgrade pip setuptools wheel --quiet || {
        log_warn "Falha ao atualizar pip"
    }

    echo ""
}

# Instalar dependencias Python
install_python_deps() {
    log_info "Instalando dependencias Python..."
    echo ""

    # Verificar se requirements.txt existe
    if [[ ! -f "requirements.txt" ]]; then
        log_error "requirements.txt nao encontrado!"
        log_info "Certifique-se de estar no diretorio raiz do projeto"
        exit 1
    fi

    # Instalar via requirements.txt (dentro do venv)
    log_info "Instalando pacotes de requirements.txt..."
    pip install -r requirements.txt || {
        log_error "Falha ao instalar dependencias Python"
        exit 1
    }
    log_success "Dependencias Python instaladas"

    # Instalar browser do Playwright
    log_info "Instalando browser Chromium para Playwright..."
    python -m playwright install chromium 2>/dev/null || {
        log_warn "Playwright browser nao foi instalado"
    }

    echo ""
}

# Instalar ferramentas de sistema
install_system_tools() {
    log_info "Instalando ferramentas de sistema..."
    echo ""

    # Dependencias de sistema
    if [[ "$OS" == "linux" ]]; then
        log_info "Instalando poppler-utils e tesseract-ocr (Linux)..."
        sudo apt-get install -y poppler-utils tesseract-ocr 2>/dev/null || {
            log_warn "Algumas ferramentas de sistema nao foram instaladas"
        }
    elif [[ "$OS" == "macos" ]]; then
        log_info "Instalando poppler e tesseract (macOS)..."
        brew install poppler tesseract 2>/dev/null || {
            log_warn "Algumas ferramentas de sistema nao foram instaladas"
        }
    fi

    log_success "Ferramentas de sistema instaladas"
    echo ""
}

# Resumo final
print_summary() {
    echo ""
    echo "========================================"
    echo "   Setup Completo!"
    echo "========================================"
    echo ""
    echo "Proximos passos:"
    echo ""
    echo "  1. Autenticar GitHub (se ainda nao fez):"
    echo "     gh auth login"
    echo ""
    echo "  2. Configurar Claude Code:"
    echo "     claude"
    echo "     (siga as instrucoes de autenticacao)"
    echo ""
    echo "  3. Iniciar workflow SDLC:"
    echo "     claude \"/sdlc-start Minha nova feature\""
    echo ""
    echo "  4. Ou criar spec diretamente:"
    echo "     claude \"/speckit.specify Descricao da feature\""
    echo ""
    echo "  5. Criar issues para Copilot:"
    echo "     gh issue create --assignee \"@copilot\" --title \"...\""
    echo ""
    echo "Ferramentas opcionais:"
    echo "  # Seguranca:"
    echo "  ./.agentic_sdlc/scripts/install-security-tools.sh --all"
    echo ""
    echo "Virtualenv Python:"
    echo "  source .venv/bin/activate    # Ativar venv antes de usar Claude Code"
    echo ""
    echo "  (Todas as dependências Python já foram instaladas no venv)"
    echo ""
    echo "Documentacao:"
    echo "  - .agentic_sdlc/docs/QUICKSTART.md"
    echo "  - .agentic_sdlc/docs/INFRASTRUCTURE.md"
    echo "  - .agentic_sdlc/docs/playbook.md"
    echo ""
}

# Verificar e oferecer migração de artefatos (SEMPRE, independente de origem)
check_and_migrate_artifacts() {
    # Se --force, pular verificação
    if [[ "$FORCE_UPDATE" == "true" ]]; then
        return 0
    fi

    # Verificar se há artefatos em .agentic_sdlc/ que deveriam estar em .project/
    if check_project_artifacts_in_agentic_sdlc; then
        echo ""
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║          ⚠️  ARTEFATOS EM LOCAL INCORRETO ⚠️                ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        echo ""
        log_warn "Artefatos de projeto detectados em .agentic_sdlc/"
        echo ""
        echo "REGRA DE OURO (v2.1.7+): Artefatos de PROJETO devem estar em .project/"
        echo ""
        echo "Artefatos encontrados:"
        for dir in corpus architecture security reports references sessions; do
            if [[ -d ".agentic_sdlc/$dir" ]]; then
                local COUNT=$(find ".agentic_sdlc/$dir" -type f ! -name ".gitkeep" 2>/dev/null | wc -l)
                if [[ $COUNT -gt 0 ]]; then
                    echo "  • $dir/ ($COUNT arquivos)"
                fi
            fi
        done

        echo ""
        echo -e "${CYAN}Deseja migrar estes artefatos para .project/ AGORA?${NC}"
        echo ""
        echo "  [1] Sim, migrar agora (RECOMENDADO)"
        echo "  [2] Não, vou migrar depois manualmente"
        echo "  [3] Cancelar instalação"
        echo ""
        read -p "Escolha [1-3]: " choice

        case $choice in
            1)
                log_info "Executando migração automática..."
                if migrate_project_artifacts; then
                    log_success "Migração concluída!"

                    # Perguntar sobre limpeza
                    echo ""
                    log_question "Deseja limpar .agentic_sdlc/ agora? (backup será criado)"
                    read -p "Limpar? [y/N]: " clean_choice

                    if [[ "$clean_choice" =~ ^[Yy]$ ]]; then
                        clean_agentic_sdlc
                    else
                        log_info "Artefatos mantidos em .agentic_sdlc/ (duplicados)"
                    fi
                else
                    log_error "Falha na migração. Tente manualmente: ./.agentic_sdlc/scripts/migrate-artifacts.sh"
                    exit 1
                fi
                ;;
            2)
                log_info "Instalação continuará. Migre manualmente depois:"
                echo ""
                echo "  ./.agentic_sdlc/scripts/migrate-artifacts.sh"
                echo ""
                ;;
            3)
                log_info "Instalação cancelada."
                exit 0
                ;;
            *)
                log_error "Opção inválida."
                exit 1
                ;;
        esac
    fi
}

# Main
main() {
    parse_args "$@"
    detect_os

    # SEMPRE verificar artefatos antes de continuar (independente de origem)
    check_and_migrate_artifacts

    # Se instalando de release
    if [[ "$FROM_RELEASE" == "true" ]]; then
        install_from_release
    fi

    # Instalar dependencias (se nao puladas)
    if [[ "$SKIP_DEPS" != "true" ]]; then
        echo ""
        log_info "Instalando dependencias..."
        echo ""

        check_python
        setup_python_venv
        install_python_deps
        install_system_tools
        install_uv
        check_git
        check_gh
        check_node
        install_claude_code
        install_speckit
    fi

    echo ""
    log_info "Configurando projeto..."
    echo ""

    make_scripts_executable
    init_speckit
    check_claude_structure
    enable_copilot_agent
    run_checks

    print_summary
}

# Executar
main "$@"
