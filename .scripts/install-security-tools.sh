#!/bin/bash
#
# Script para instalar ferramentas de seguranca opcionais
# Estas ferramentas sao usadas pelo security-gate e security-scanner
#
# Uso:
#   ./.scripts/install-security-tools.sh [--all | --semgrep | --trivy | --gitleaks]
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
echo "   Security Tools - Instalador"
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

# Detectar se sistema tem PEP 668 (externally-managed-environment)
has_pep668() {
    # PEP 668: Distribuições Linux modernas marcam Python do sistema como externally-managed
    test -f /usr/lib/python3.*/EXTERNALLY-MANAGED 2>/dev/null
}

# Instalar pipx se não existir (necessário em sistemas PEP 668)
ensure_pipx() {
    if command -v pipx &> /dev/null; then
        return 0
    fi

    log_info "pipx não encontrado. Instalando pipx..."

    if [[ "$OS" == "linux" ]]; then
        # Tentar apt/dnf/pacman
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y pipx
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y pipx
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm python-pipx
        else
            # Fallback: pip install pipx para usuário
            python3 -m pip install --user pipx 2>/dev/null || {
                log_error "Falha ao instalar pipx"
                return 1
            }
        fi

        # Adicionar pipx ao PATH se necessário
        python3 -m pipx ensurepath 2>/dev/null || true

    elif [[ "$OS" == "macos" ]]; then
        brew install pipx
    else
        log_error "Instalação automática de pipx não suportada no Windows"
        log_info "Instale manualmente: python -m pip install --user pipx"
        return 1
    fi

    log_success "pipx instalado"
}

# Instalar Semgrep (SAST)
install_semgrep() {
    log_info "Verificando Semgrep..."

    if command -v semgrep &> /dev/null; then
        log_success "Semgrep ja instalado: $(semgrep --version 2>/dev/null | head -n1)"
        return 0
    fi

    log_info "Instalando Semgrep..."

    # Estratégia de instalação por prioridade:
    # 1. pipx (recomendado para ferramentas CLI, especialmente em sistemas PEP 668)
    # 2. brew (macOS)
    # 3. pip3 --user (fallback para sistemas sem PEP 668)

    if has_pep668 || [[ "$OS" == "linux" ]]; then
        # Sistema com PEP 668 ou Linux: usar pipx
        log_info "Sistema detectado com PEP 668 ou Linux - usando pipx (isolado)"
        ensure_pipx || {
            log_error "Falha ao configurar pipx"
            return 1
        }
        pipx install semgrep

    elif command -v brew &> /dev/null; then
        # macOS com brew
        brew install semgrep

    elif command -v pip3 &> /dev/null; then
        # Fallback: pip3 --user (evitar --break-system-packages)
        log_warn "Usando pip3 --user (instalação no diretório do usuário)"
        pip3 install --user semgrep

    else
        log_error "Nenhum gerenciador de pacotes encontrado"
        log_info "Instale manualmente: https://semgrep.dev/docs/getting-started/"
        log_info "Ou instale pipx: python3 -m pip install --user pipx"
        return 1
    fi

    log_success "Semgrep instalado"

    # Verificar se precisa adicionar ao PATH
    if ! command -v semgrep &> /dev/null; then
        log_warn "Semgrep instalado mas não está no PATH"
        log_info "Adicione ao PATH: export PATH=\"\$HOME/.local/bin:\$PATH\""
        log_info "Ou reinicie o terminal"
    fi
}

# Instalar Trivy (SCA - Container/Dependency Scanner)
install_trivy() {
    log_info "Verificando Trivy..."

    if command -v trivy &> /dev/null; then
        log_success "Trivy ja instalado: $(trivy --version 2>/dev/null | head -n1)"
        return 0
    fi

    log_info "Instalando Trivy..."

    if [[ "$OS" == "macos" ]]; then
        brew install trivy
    elif [[ "$OS" == "linux" ]]; then
        # Instalar via script oficial
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin
    else
        log_error "Instalacao automatica do Trivy nao suportada no Windows"
        log_info "Instale manualmente: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
        return 1
    fi

    log_success "Trivy instalado"
}

# Instalar Gitleaks (Secret Scanner)
install_gitleaks() {
    log_info "Verificando Gitleaks..."

    if command -v gitleaks &> /dev/null; then
        log_success "Gitleaks ja instalado: $(gitleaks version 2>/dev/null)"
        return 0
    fi

    log_info "Instalando Gitleaks..."

    if [[ "$OS" == "macos" ]]; then
        brew install gitleaks
    elif [[ "$OS" == "linux" ]]; then
        # Detectar arquitetura
        ARCH=$(uname -m)
        case $ARCH in
            x86_64) ARCH="x64" ;;
            aarch64) ARCH="arm64" ;;
            *) log_error "Arquitetura nao suportada: $ARCH"; return 1 ;;
        esac

        # Obter ultima versao
        GITLEAKS_VERSION=$(curl -s https://api.github.com/repos/gitleaks/gitleaks/releases/latest | grep tag_name | cut -d'"' -f4)

        # Download e instalacao
        curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION#v}_linux_${ARCH}.tar.gz" -o /tmp/gitleaks.tar.gz
        sudo tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin gitleaks
        rm /tmp/gitleaks.tar.gz
    else
        log_error "Instalacao automatica do Gitleaks nao suportada no Windows"
        log_info "Instale manualmente: https://github.com/gitleaks/gitleaks#installing"
        return 1
    fi

    log_success "Gitleaks instalado"
}

# Verificar todas as ferramentas
verify_tools() {
    echo ""
    log_info "Status das ferramentas de seguranca:"
    echo ""

    # Semgrep
    if command -v semgrep &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Semgrep (SAST)"
    else
        echo -e "  ${RED}✗${NC} Semgrep (SAST) - nao instalado"
    fi

    # Trivy
    if command -v trivy &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Trivy (SCA/Container)"
    else
        echo -e "  ${RED}✗${NC} Trivy (SCA/Container) - nao instalado"
    fi

    # Gitleaks
    if command -v gitleaks &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Gitleaks (Secrets)"
    else
        echo -e "  ${RED}✗${NC} Gitleaks (Secrets) - nao instalado"
    fi

    echo ""
}

# Mostrar uso
show_usage() {
    echo "Uso: $0 [opcao]"
    echo ""
    echo "Opcoes:"
    echo "  --all       Instala todas as ferramentas (padrao)"
    echo "  --semgrep   Instala apenas Semgrep (SAST)"
    echo "  --trivy     Instala apenas Trivy (SCA/Container Scanner)"
    echo "  --gitleaks  Instala apenas Gitleaks (Secret Scanner)"
    echo "  --verify    Apenas verifica o status das ferramentas"
    echo "  --help      Mostra esta mensagem"
    echo ""
    echo "Ferramentas:"
    echo "  Semgrep  - Static Application Security Testing (SAST)"
    echo "             Analisa codigo fonte em busca de vulnerabilidades"
    echo ""
    echo "  Trivy    - Software Composition Analysis (SCA)"
    echo "             Analisa dependencias e containers em busca de CVEs"
    echo ""
    echo "  Gitleaks - Secret Scanner"
    echo "             Detecta secrets e credenciais vazadas no codigo"
    echo ""
}

# Main
main() {
    detect_os

    OPTION="${1:---all}"

    case "$OPTION" in
        --all)
            echo ""
            log_info "Instalando todas as ferramentas de seguranca..."
            echo ""
            install_semgrep
            install_trivy
            install_gitleaks
            ;;
        --semgrep)
            install_semgrep
            ;;
        --trivy)
            install_trivy
            ;;
        --gitleaks)
            install_gitleaks
            ;;
        --verify)
            verify_tools
            exit 0
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            log_error "Opcao desconhecida: $OPTION"
            show_usage
            exit 1
            ;;
    esac

    verify_tools

    echo ""
    log_success "Instalacao concluida!"
    echo ""
    echo "Proximos passos:"
    echo "  - Execute '/security-scan' no Claude Code para analisar o projeto"
    echo "  - Configure .gitleaks.toml para regras customizadas"
    echo "  - Veja .claude/skills/gate-evaluator/gates/security-gate.yml"
    echo ""
}

# Executar
main "$@"
