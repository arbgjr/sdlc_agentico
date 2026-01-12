#!/bin/bash
#
# Git Repository Initialization Script
# Inicializa ou clona repositórios Git com configuração automática
#
# Uso:
#   ./git_init.sh
#

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para ler input com opção de cancelar e valor default
read_with_cancel() {
    local prompt="$1"
    local default_value="$2"
    local input=""
    
    while [[ -z "$input" ]]; do
        if [[ -n "$default_value" ]]; then
            read -rp "$prompt (ou 'cancelar' para sair) [default: $default_value]: " input
        else
            read -rp "$prompt (ou 'cancelar' para sair): " input
        fi
        
        if [[ "$input" == "cancelar" ]]; then
            echo -e "${RED}Operação cancelada pelo usuário.${NC}"
            exit 1
        fi
        
        if [[ -z "$input" && -n "$default_value" ]]; then
            input="$default_value"
        fi
    done
    
    echo "$input"
}

# Configuração do usuário Git
set_git_configuration() {
    local configured_gitname
    local configured_gitemail
    
    configured_gitname=$(git config user.name 2>/dev/null || echo "")
    local user_name
    user_name=$(read_with_cancel "Insira o seu nome" "$configured_gitname")
    git config --global user.name "$user_name"
    
    configured_gitemail=$(git config user.email 2>/dev/null || echo "")
    local user_email
    user_email=$(read_with_cancel "Insira o seu email" "$configured_gitemail")
    git config --global user.email "$user_email"
}

# Inicializar repositório local
initialize_local_git_repository() {
    local repo_path="$1"
    local branch_name="${2:-main}"
    
    cd "$repo_path"
    git init
    git symbolic-ref HEAD "refs/heads/$branch_name"
    git add .
    git commit -m "Initial commit"
    echo -e "${GREEN}Repositório local inicializado com sucesso em '$repo_path'.${NC}"
}

# Clonar repositório
clone_git_repository() {
    local repo_url="$1"
    local clone_path="$2"
    
    git clone "$repo_url" "$clone_path"
    echo -e "${GREEN}Repositório '$repo_url' clonado com sucesso em '$clone_path'.${NC}"
}

# Criar branch de feature e push
create_feature_branch_and_push() {
    local feature_branch_name="$1"
    local repo_url="$2"
    
    # Verifica se a branch existe
    if ! git branch --list "$feature_branch_name" | grep -q "$feature_branch_name"; then
        git checkout -b "$feature_branch_name"
    else
        git checkout "$feature_branch_name"
    fi
    
    # Adiciona remote se não existir
    if [[ -z "$(git remote)" ]]; then
        git remote add origin "$repo_url"
    fi
    
    # Push com upstream
    git push --set-upstream origin "$feature_branch_name"
    echo -e "${GREEN}Branch de feature '$feature_branch_name' criada e enviada para o repositório remoto '$repo_url'.${NC}"
}

# Verificar se token GitHub é válido
validate_github_token() {
    local token="$1"
    
    if [[ -z "$token" ]]; then
        return 1
    fi
    
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $token" "https://api.github.com/user")
    
    [[ "$response" == "200" ]]
}

# Verificar se repositório existe no GitHub
check_repo_exists() {
    local org_name="$1"
    local repo_name="$2"
    local token="$3"
    
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $token" "https://api.github.com/repos/$org_name/$repo_name")
    
    [[ "$response" == "200" ]]
}

# Criar repositório no GitHub via API
create_github_repo_api() {
    local org_name="$1"
    local repo_name="$2"
    local token="$3"
    
    local response
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: token $token" \
        -H "User-Agent: Bash-Script" \
        -H "Content-Type: application/json" \
        -X POST \
        -d "{\"name\": \"$repo_name\", \"private\": true}" \
        "https://api.github.com/orgs/$org_name/repos")
    
    local http_code
    http_code=$(echo "$response" | tail -n1)
    local body
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "201" ]]; then
        local html_url
        html_url=$(echo "$body" | grep -o '"html_url": *"[^"]*"' | head -1 | cut -d'"' -f4)
        echo -e "${GREEN}Repositório criado com sucesso: $html_url${NC}"
        return 0
    else
        # Tenta criar em user repos se falhar em org
        response=$(curl -s -w "\n%{http_code}" \
            -H "Authorization: token $token" \
            -H "User-Agent: Bash-Script" \
            -H "Content-Type: application/json" \
            -X POST \
            -d "{\"name\": \"$repo_name\", \"private\": true}" \
            "https://api.github.com/user/repos")
        
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')
        
        if [[ "$http_code" == "201" ]]; then
            local html_url
            html_url=$(echo "$body" | grep -o '"html_url": *"[^"]*"' | head -1 | cut -d'"' -f4)
            echo -e "${GREEN}Repositório criado com sucesso: $html_url${NC}"
            return 0
        else
            echo -e "${RED}Falha ao criar repositório remoto: $body${NC}"
            return 1
        fi
    fi
}

# Criar repositório usando gh CLI
create_github_repo_cli() {
    local org_name="$1"
    local repo_name="$2"
    
    if command -v gh &> /dev/null; then
        if gh repo create "$org_name/$repo_name" --private --confirm 2>/dev/null || \
           gh repo create "$org_name/$repo_name" --private -y 2>/dev/null; then
            echo -e "${GREEN}Repositório criado com sucesso via gh CLI: https://github.com/$org_name/$repo_name${NC}"
            return 0
        else
            echo -e "${RED}Falha ao criar repositório via gh CLI.${NC}"
            return 1
        fi
    else
        echo -e "${RED}GitHub CLI (gh) não encontrado. O repositório deve ser criado manualmente ou via site.${NC}"
        return 1
    fi
}

# Main
main() {
    clear
    
    # Configuração do usuário Git
    set_git_configuration
    
    local operation
    operation=$(read_with_cancel "Você deseja 'inicializar' um novo repositório local ou 'clonar' um repositório remoto? (inicializar/clonar)" "")
    
    case "$operation" in
        inicializar)
            local current_dir
            current_dir=$(pwd)
            
            local repo_path
            repo_path=$(read_with_cancel "Insira o caminho para inicializar o repositório" "$current_dir")
            
            local branch_name
            branch_name=$(read_with_cancel "Insira o nome da branch principal" "main")
            
            initialize_local_git_repository "$repo_path" "$branch_name"
            
            # Sugerir nome do repo pelo nome da pasta
            local repo_folder
            repo_folder=$(basename "$repo_path")
            
            local org_default=""
            if [[ -n "$GITHUB_ORG" ]]; then
                org_default="$GITHUB_ORG"
            elif [[ -n "$GITHUB_USER" ]]; then
                org_default="$GITHUB_USER"
            fi
            
            local org_name
            org_name=$(read_with_cancel "Insira o nome da organização do repositório remoto (GitHub)" "$org_default")
            
            local default_repo_name="$repo_folder"
            if [[ "$org_name" == "$default_repo_name" ]]; then
                default_repo_name="${repo_folder}-repo"
            fi
            
            local repo_name
            repo_name=$(read_with_cancel "Insira o nome do repositório remoto (GitHub)" "$default_repo_name")
            
            # Token GitHub
            local github_token="${TOKEN_GITHUB:-}"
            local token_valid=false
            
            if [[ -n "$github_token" ]]; then
                if validate_github_token "$github_token"; then
                    token_valid=true
                    echo -e "${GREEN}TOKEN_GITHUB encontrado e válido. Usando token do ambiente.${NC}"
                else
                    github_token=$(read_with_cancel "Insira seu GitHub Personal Access Token (com permissão para criar repositórios, ou deixe em branco para usar o CLI gh/git)" "")
                fi
            fi
            
            local repo_url="https://github.com/$org_name/$repo_name.git"
            local repo_exists=false
            
            if [[ -n "$github_token" ]]; then
                # Verifica se repo existe via API
                if check_repo_exists "$org_name" "$repo_name" "$github_token"; then
                    repo_exists=true
                    echo -e "${GREEN}Repositório remoto já existe: https://github.com/$org_name/$repo_name${NC}"
                else
                    echo -e "${YELLOW}Repositório remoto não existe. Criando no GitHub via API...${NC}"
                    if ! create_github_repo_api "$org_name" "$repo_name" "$github_token"; then
                        exit 1
                    fi
                fi
            else
                # Sem token: tenta com gh CLI
                echo -e "${YELLOW}Tentando criar repositório remoto usando o GitHub CLI (gh)...${NC}"
                create_github_repo_cli "$org_name" "$repo_name" || true
            fi
            
            local feature_branch_name
            feature_branch_name=$(read_with_cancel "Insira o nome da branch de feature para suas alterações" "$repo_name")
            
            create_feature_branch_and_push "$feature_branch_name" "$repo_url"
            ;;
            
        clonar)
            local repo_url
            repo_url=$(read_with_cancel "Insira a URL do repositório remoto" "")
            
            local clone_path
            clone_path=$(read_with_cancel "Insira o caminho onde o repositório deve ser clonado" "")
            
            clone_git_repository "$repo_url" "$clone_path"
            ;;
            
        *)
            echo -e "${RED}Operação desconhecida. Cancelando...${NC}"
            exit 1
            ;;
    esac
}

# Executar
main "$@"
