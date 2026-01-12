#!/bin/bash
#
# Setup Script para SDLC Agentico
# Instala todas as dependencias necessarias para o workflow
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/arbgjr/mice_dolphins/main/.scripts/setup-sdlc.sh | bash
#   ou
#   ./.scripts/setup-sdlc.sh
#

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funcoes de log
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Header
echo ""
echo "========================================"
echo "   SDLC Agentico - Setup Script"
echo "========================================"
echo ""

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
    echo "Documentacao:"
    echo "  - INFRASTRUCTURE.md"
    echo "  - .claude/guides/"
    echo ""
}

# Main
main() {
    detect_os

    echo ""
    log_info "Instalando dependencias..."
    echo ""

    check_python
    install_uv
    check_git
    check_gh
    check_node
    install_claude_code
    install_speckit

    echo ""
    log_info "Configurando projeto..."
    echo ""

    init_speckit
    check_claude_structure
    enable_copilot_agent
    run_checks

    print_summary
}

# Executar
main "$@"
