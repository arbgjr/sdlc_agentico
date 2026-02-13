<#
.SYNOPSIS
    Setup Script para SDLC Agentico (Windows PowerShell)

.DESCRIPTION
    Instala todas as dependencias necessarias para o workflow SDLC Agentico no Windows.

    ⚠️  REQUISITOS:
    - Windows 10+ (para tar e curl nativos)
    - PowerShell 5.1+ (PowerShell Core 7+ RECOMENDADO)
    - Privilégios de Administrador para instalação de ferramentas globais

    ✨ OTIMIZADO PARA POWERSHELL CORE 7+:
    - Compatibilidade multiplataforma com Join-Path
    - ErrorAction consistente em vez de redirecionamento 2>$null
    - Instalação segura de ferramentas sem Invoke-Expression direto
    - Suporte para verificação de privilégios em Windows/Linux/macOS
    - Melhor tratamento de erros e logging

    O script tentará instalar ferramentas usando winget (Windows Package Manager).
    Se winget não estiver disponível, fornecerá instruções manuais.

.PARAMETER FromRelease
    Instala a partir de uma release do GitHub (baixa e extrai)

.PARAMETER Version
    Especifica a versão a instalar (ex: "v3.0.3"). Padrão: "latest"

.PARAMETER SkipDeps
    Pula a instalação de dependências (Python, Node, etc)

.PARAMETER Force
    Força atualização sem perguntar

.PARAMETER InstallOptional
    Instala dependências opcionais (document-processor, frontend-testing)

.EXAMPLE
    # Instalação local (após baixar release)
    .\setup-sdlc.ps1

.EXAMPLE
    # Instalação com download da última release
    .\setup-sdlc.ps1 -FromRelease

.EXAMPLE
    # Instalação de versão específica
    .\setup-sdlc.ps1 -FromRelease -Version "v3.0.3"

.EXAMPLE
    # Instalação sem dependências (apenas configuração)
    .\setup-sdlc.ps1 -SkipDeps

.NOTES
    Author: SDLC Agentico Team
    Version: 3.0.4-pwsh7
    Requires: PowerShell 5.1+ (PowerShell Core 7+ recommended)
    Last Updated: 2026-02-12
    Changelog: Otimizado para PowerShell Core 7+ com melhor compatibilidade multiplataforma
#>

[CmdletBinding()]
param(
    [switch]$FromRelease,
    [string]$Version = "latest",
    [switch]$SkipDeps,
    [switch]$Force,
    [switch]$InstallOptional
)

# Configurações
$ErrorActionPreference = "Stop"
$RepoOwner = "arbgjr"
$RepoName = "sdlc_agentico"
$RepoUrl = "https://github.com/$RepoOwner/$RepoName"

# Funções de log com cores
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO]" -ForegroundColor Blue -NoNewline
    Write-Host " $Message"
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK]" -ForegroundColor Green -NoNewline
    Write-Host " $Message"
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN]" -ForegroundColor Yellow -NoNewline
    Write-Host " $Message"
}

function Write-Error2 {
    param([string]$Message)
    Write-Host "[ERROR]" -ForegroundColor Red -NoNewline
    Write-Host " $Message"
}

function Write-Question {
    param([string]$Message)
    Write-Host "[?]" -ForegroundColor Cyan -NoNewline
    Write-Host " $Message"
}

# Show splash screen
function Show-Splash {
    $ScriptDir = Split-Path -Parent $MyInvocation.PSCommandPath
    $FrameworkRoot = (Get-Item $ScriptDir).Parent.Parent.FullName

    $SplashPath = $null

    # Priority 1: Relative to framework root (using Join-Path for cross-platform compatibility)
    $candidatePath = Join-Path $FrameworkRoot ".agentic_sdlc" | Join-Path -ChildPath "splash.py"
    if (Test-Path $candidatePath) {
        $SplashPath = $candidatePath
    }
    # Priority 2: Current directory
    else {
        $candidatePath = Join-Path ".agentic_sdlc" "splash.py"
        if (Test-Path $candidatePath) {
            $SplashPath = $candidatePath
        }
    }

    if ($SplashPath -and (Test-Path $SplashPath)) {
        try {
            & python $SplashPath --no-animate -ErrorAction SilentlyContinue
        }
        catch {
            Write-Host ""
            Write-Host "========================================"
            Write-Host "   SDLC Agentico - Setup Script"
            Write-Host "========================================"
            Write-Host ""
        }
    }
    else {
        Write-Host ""
        Write-Host "========================================"
        Write-Host "   SDLC Agentico - Setup Script"
        Write-Host "========================================"
        Write-Host ""
    }
}

# Check if running as Administrator (Windows only)
function Test-Administrator {
    # Only check on Windows
    if ($IsWindows -or ($PSVersionTable.PSVersion.Major -lt 6)) {
        try {
            $user = [Security.Principal.WindowsIdentity]::GetCurrent()
            $principal = New-Object Security.Principal.WindowsPrincipal $user
            return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        }
        catch {
            Write-Warn "Não foi possível verificar privilégios de administrador"
            return $false
        }
    }
    # On non-Windows, check if running as root
    elseif ($IsLinux -or $IsMacOS) {
        return (id -u) -eq 0
    }
    return $false
}

# Detect installed version
function Get-InstalledVersion {
    $installedVersion = ""

    # Method 1: Read .claude/VERSION
    if (Test-Path ".claude\VERSION") {
        $versionContent = Get-Content ".claude\VERSION" -ErrorAction SilentlyContinue
        $versionLine = $versionContent | Where-Object { $_ -match "^version:" }
        if ($versionLine) {
            $installedVersion = ($versionLine -split ":")[1].Trim().Trim('"')
        }
    }

    # Method 2: Git tag (if git repo)
    if (-not $installedVersion -and (Test-Path ".git")) {
        try {
            $installedVersion = git describe --tags --abbrev=0 -ErrorAction SilentlyContinue
        }
        catch {
            # Ignore
        }
    }

    # Method 3: Check if .agentic_sdlc exists
    if (-not $installedVersion -and (Test-Path ".agentic_sdlc")) {
        $installedVersion = "unknown"
    }

    return $installedVersion
}

# Check project artifacts in .agentic_sdlc
function Test-ProjectArtifactsInAgentic {
    $agenticPath = ".agentic_sdlc"
    if (-not (Test-Path $agenticPath)) {
        return $false
    }

    $projectDirs = @(
        (Join-Path $agenticPath "corpus" | Join-Path -ChildPath "nodes" | Join-Path -ChildPath "decisions"),
        (Join-Path $agenticPath "architecture"),
        (Join-Path $agenticPath "security"),
        (Join-Path $agenticPath "reports")
    )

    foreach ($dir in $projectDirs) {
        if (Test-Path $dir) {
            $fileCount = (Get-ChildItem -Path $dir -Recurse -File -ErrorAction SilentlyContinue |
                         Where-Object { $_.Name -ne ".gitkeep" }).Count
            if ($fileCount -gt 0) {
                return $true
            }
        }
    }

    return $false
}

# Migrate project artifacts from .agentic_sdlc to .project
function Move-ProjectArtifacts {
    Write-Info "Iniciando migração de artefatos..."
    Write-Host ""

    $projectPath = ".project"
    # Create .project if not exists
    if (-not (Test-Path $projectPath)) {
        New-Item -ItemType Directory -Path $projectPath -Force | Out-Null
    }

    $migratedCount = 0

    $dirsToMigrate = @{
        "corpus" = "corpus"
        "architecture" = "architecture"
        "security" = "security"
        "reports" = "reports"
        "references" = "references"
        "sessions" = "sessions"
    }

    foreach ($dirName in $dirsToMigrate.Keys) {
        $sourceDir = Join-Path ".agentic_sdlc" $dirName
        $destName = $dirsToMigrate[$dirName]
        $destDir = Join-Path $projectPath $destName

        if (Test-Path $sourceDir) {
            $fileCount = (Get-ChildItem -Path $sourceDir -Recurse -File -ErrorAction SilentlyContinue |
                         Where-Object { $_.Name -ne ".gitkeep" }).Count

            if ($fileCount -gt 0) {
                Write-Info "Migrando $sourceDir → $destDir"

                # Create destination directory
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }

                # Copy content (preserving structure)
                $sourcePath = Join-Path $sourceDir "*"
                Copy-Item -Path $sourcePath -Destination $destDir -Recurse -Force -ErrorAction SilentlyContinue

                # Remove .gitkeep if exists in destination
                $gitkeepPath = Join-Path $destDir ".gitkeep"
                if (Test-Path $gitkeepPath) {
                    Remove-Item $gitkeepPath -Force -ErrorAction SilentlyContinue
                }

                $migratedCount++
                Write-Success "  ✓ Migrado: $fileCount arquivos"
            }
        }
    }

    if ($migratedCount -gt 0) {
        Write-Success "Migração completa: $migratedCount diretórios migrados"
        return $true
    }
    else {
        Write-Info "Nenhum artefato encontrado para migrar"
        return $false
    }
}

# Clean .agentic_sdlc (remove migrated artifacts, keep framework)
function Clear-AgenticArtifacts {
    if (-not (Test-Path ".agentic_sdlc")) {
        return
    }

    Write-Info "Limpando artefatos de .agentic_sdlc/..."

    # Create backup
    $backupDir = ".agentic_sdlc.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item -Path ".agentic_sdlc" -Destination $backupDir -Recurse -Force -ErrorAction SilentlyContinue

    if (Test-Path $backupDir) {
        Write-Info "Backup criado em: $backupDir"
    }

    # Remove ONLY artifacts, keep framework (scripts, templates, schemas, docs, logo.png, splash.py)
    $artifactDirs = @(
        "corpus",
        "architecture",
        "security",
        "reports",
        "references",
        "sessions"
    )

    foreach ($dir in $artifactDirs) {
        $fullPath = ".agentic_sdlc\$dir"
        if (Test-Path $fullPath) {
            Write-Info "  Removendo $fullPath\"
            Remove-Item -Path $fullPath -Recurse -Force
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            New-Item -ItemType File -Path "$fullPath\.gitkeep" -Force | Out-Null
        }
    }

    Write-Success "Artefatos removidos (framework mantido)"
    Write-Info "Framework preservado: scripts/, templates/, schemas/, docs/, logo.png, splash.py"
}

# Confirm update
function Confirm-Update {
    param(
        [string]$CurrentVersion,
        [string]$NewVersion
    )

    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║           ATUALIZAÇÃO DO SDLC AGÊNTICO                     ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Versão instalada:" -ForegroundColor Yellow -NoNewline
    Write-Host " $CurrentVersion"
    Write-Host "Nova versão:" -ForegroundColor Green -NoNewline
    Write-Host "      $NewVersion"
    Write-Host ""

    # Check if there are project artifacts in wrong location
    if (Test-ProjectArtifactsInAgentic) {
        Write-Host "⚠️  ATENÇÃO: Artefatos de projeto detectados em .agentic_sdlc/" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Foi detectado que este projeto possui artefatos em .agentic_sdlc/"
        Write-Host "que deveriam estar em .project/ (REGRA DE OURO v2.1.7+)."
        Write-Host ""
        Write-Host "Artefatos encontrados:"

        # List artifacts
        $dirs = @("corpus", "architecture", "security", "reports", "references")
        foreach ($dir in $dirs) {
            if (Test-Path ".agentic_sdlc\$dir") {
                $count = (Get-ChildItem -Path ".agentic_sdlc\$dir" -Recurse -File | Where-Object { $_.Name -ne ".gitkeep" }).Count
                if ($count -gt 0) {
                    Write-Host "  • $dir/ ($count arquivos)"
                }
            }
        }

        Write-Host ""
        Write-Host "O que deseja fazer?" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  [1] Migrar artefatos para .project/ e atualizar (RECOMENDADO)"
        Write-Host "  [2] Continuar SEM migrar (PERDERÁ todos os artefatos!)"
        Write-Host "  [3] Cancelar atualização"
        Write-Host ""

        $choice = Read-Host "Escolha [1-3]"

        switch ($choice) {
            "1" {
                Write-Info "Opção selecionada: Migrar e atualizar"
                Write-Host ""

                if (Move-ProjectArtifacts) {
                    Write-Host ""
                    Write-Success "Artefatos migrados com sucesso para .project/"

                    Write-Host ""
                    Write-Question "Deseja remover .agentic_sdlc/ agora?"
                    Write-Host "  (Um backup será criado antes da remoção)"
                    Write-Host ""

                    $removeOld = Read-Host "Remover .agentic_sdlc/? [y/N]"

                    if ($removeOld -match "^[Yy]$") {
                        Clear-AgenticArtifacts
                    }
                    else {
                        Write-Warn ".agentic_sdlc/ mantido. Remova manualmente após validar migração."
                    }

                    return $true
                }
                else {
                    Write-Error2 "Falha na migração de artefatos"
                    return $false
                }
            }
            "2" {
                Write-Host ""
                Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Red
                Write-Host "║                    ⚠️  AVISO CRÍTICO ⚠️                     ║" -ForegroundColor Red
                Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Red
                Write-Host ""
                Write-Host "Você escolheu NÃO migrar os artefatos do projeto." -ForegroundColor Yellow
                Write-Host ""
                Write-Host "Isso significa que você PERDERÁ:"
                Write-Host "  • Todos os ADRs inferidos/convertidos"
                Write-Host "  • Diagramas de arquitetura"
                Write-Host "  • Threat models"
                Write-Host "  • Reports de tech debt"
                Write-Host "  • Referências e sessões"
                Write-Host ""
                Write-Host "Esta ação é IRREVERSÍVEL!" -ForegroundColor Red
                Write-Host ""

                $confirmLoss = Read-Host "Tem CERTEZA que deseja continuar SEM migrar? [y/N]"

                if ($confirmLoss -match "^[Yy]$") {
                    Write-Warn "Continuando SEM migração. Artefatos serão perdidos."
                    Clear-AgenticArtifacts
                    return $true
                }
                else {
                    Write-Info "Atualização cancelada. Execute novamente e escolha opção 1 para migrar."
                    exit 0
                }
            }
            "3" {
                Write-Info "Atualização cancelada pelo usuário."
                exit 0
            }
            default {
                Write-Error2 "Opção inválida. Atualização cancelada."
                exit 1
            }
        }
    }
    else {
        # No project artifacts, just confirm update
        Write-Host "A atualização irá:"
        Write-Host "  • Atualizar framework de $CurrentVersion → $NewVersion"
        Write-Host "  • Limpar .agentic_sdlc/ (se existir)"
        Write-Host "  • Manter .project/ intacto"
        Write-Host ""

        $confirm = Read-Host "Deseja continuar com a atualização? [y/N]"

        if ($confirm -match "^[Yy]$") {
            # Clean .agentic_sdlc if exists
            if (Test-Path ".agentic_sdlc") {
                Clear-AgenticArtifacts
            }
            return $true
        }
        else {
            Write-Info "Atualização cancelada pelo usuário."
            exit 0
        }
    }
}

# Check if .claude already exists
function Test-ExistingClaude {
    if (Test-Path ".claude") {
        $currentVersion = Get-InstalledVersion

        if ($currentVersion) {
            if ($Force) {
                Write-Info "Modo --force: atualizando sem perguntar"
                return (Confirm-Update $currentVersion $Version)
            }
            else {
                return (Confirm-Update $currentVersion $Version)
            }
        }
        else {
            Write-Host ""
            Write-Warn "O diretório .claude/ já existe!"
            Write-Host ""
            Write-Host "O que deseja fazer?"
            Write-Host "  [1] Fazer backup e substituir (recomendado)"
            Write-Host "  [2] Substituir sem backup"
            Write-Host "  [3] Cancelar instalação"
            Write-Host ""

            $choice = Read-Host "Escolha [1-3]"

            switch ($choice) {
                "1" {
                    $backupDir = ".claude.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                    Write-Info "Criando backup em $backupDir..."
                    Move-Item -Path ".claude" -Destination $backupDir -Force
                    Write-Success "Backup criado em $backupDir"
                    return $true
                }
                "2" {
                    Write-Warn "Substituindo sem backup..."
                    Remove-Item -Path ".claude" -Recurse -Force
                    return $true
                }
                "3" {
                    Write-Info "Instalação cancelada pelo usuário."
                    exit 0
                }
                default {
                    Write-Error2 "Opção inválida. Cancelando."
                    exit 1
                }
            }
        }
    }

    return $true
}

# Get release URL
function Get-ReleaseUrl {
    if ($Version -eq "latest") {
        Write-Info "Obtendo última release..."

        $apiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/releases/latest"
        $release = Invoke-RestMethod -Uri $apiUrl -ErrorAction Stop
        $asset = $release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1

        if (-not $asset) {
            Write-Error2 "Nenhuma release encontrada."
            Write-Info "Verifique se existem releases em: $RepoUrl/releases"
            exit 1
        }

        $script:Version = $release.tag_name
        Write-Success "Versão mais recente: $Version"

        return $asset.browser_download_url
    }
    else {
        Write-Info "Obtendo release $Version..."
        $releaseUrl = "$RepoUrl/releases/download/$Version/sdlc-agentico-$Version.zip"

        # Check if exists
        try {
            $response = Invoke-WebRequest -Uri $releaseUrl -Method Head -ErrorAction Stop
            return $releaseUrl
        }
        catch {
            Write-Error2 "Release $Version não encontrada."
            Write-Info "Verifique releases disponíveis em: $RepoUrl/releases"
            exit 1
        }
    }
}

# Install from release
function Install-FromRelease {
    Write-Info "Instalando a partir de release..."

    # Check if .claude already exists
    Test-ExistingClaude | Out-Null

    # Get URL
    $releaseUrl = Get-ReleaseUrl
    Write-Info "Baixando: $releaseUrl"

    # Create temp directory
    $tempDir = New-Item -ItemType Directory -Path "$env:TEMP\sdlc-setup-$(Get-Random)" -Force

    try {
        # Download
        $zipPath = "$tempDir\sdlc.zip"
        Invoke-WebRequest -Uri $releaseUrl -OutFile $zipPath -ErrorAction Stop

        # Extract
        Write-Info "Extraindo arquivos..."
        Expand-Archive -Path $zipPath -DestinationPath "." -Force

        Write-Success "Arquivos extraídos com sucesso"
    }
    finally {
        # Cleanup
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Check Python
function Test-Python {
    Write-Info "Verificando Python..."

    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }

    if ($python) {
        $version = & $python.Source --version 2>&1
        if ($version -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]

            if ($major -ge 3 -and $minor -ge 11) {
                Write-Success "Python $version instalado"
                return $true
            }
            else {
                Write-Warn "Python $version encontrado, mas 3.11+ é necessário"
            }
        }
    }

    Write-Info "Python 3.11+ não encontrado. Instalando..."

    # Try winget first
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Info "Instalando Python via winget..."
        winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
        Write-Success "Python instalado"
        return $true
    }
    else {
        Write-Warn "winget não disponível. Instalação manual necessária:"
        Write-Host ""
        Write-Host "  1. Baixe Python 3.11+ de: https://www.python.org/downloads/"
        Write-Host "  2. Execute o instalador"
        Write-Host "  3. Marque 'Add Python to PATH' durante instalação"
        Write-Host "  4. Execute este script novamente"
        Write-Host ""
        return $false
    }
}

# Install uv
function Install-Uv {
    Write-Info "Verificando uv..."

    if (Get-Command uv -ErrorAction SilentlyContinue) {
        $version = uv --version
        Write-Success "uv já instalado: $version"
        return $true
    }

    Write-Info "Instalando uv..."

    try {
        # Download installer script
        $tempFile = Join-Path $env:TEMP "install-uv.ps1"
        Write-Info "Baixando instalador do uv..."
        Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile $tempFile -UseBasicParsing

        # Execute the installer script
        Write-Info "Executando instalador..."
        & $tempFile

        # Clean up
        Remove-Item $tempFile -ErrorAction SilentlyContinue

        Write-Success "uv instalado"

        # Refresh PATH for current session
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        return $true
    }
    catch {
        Write-Warn "Falha ao instalar uv automaticamente: $_"
        Write-Host ""
        Write-Host "Instale manualmente:"
        Write-Host "  irm https://astral.sh/uv/install.ps1 | iex"
        Write-Host ""
        return $false
    }
}

# Check Git
function Test-Git {
    Write-Info "Verificando Git..."

    if (Get-Command git -ErrorAction SilentlyContinue) {
        $version = git --version
        Write-Success "Git instalado: $version"
        return $true
    }

    Write-Info "Git não encontrado. Instalando..."

    # Try winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Info "Instalando Git via winget..."
        winget install Git.Git --silent --accept-package-agreements --accept-source-agreements
        Write-Success "Git instalado"
        return $true
    }
    else {
        Write-Warn "winget não disponível. Instalação manual necessária:"
        Write-Host ""
        Write-Host "  Baixe Git de: https://git-scm.com/download/win"
        Write-Host ""
        return $false
    }
}

# Check GitHub CLI
function Test-GH {
    Write-Info "Verificando GitHub CLI..."

    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $version = gh --version | Select-Object -First 1
        Write-Success "GitHub CLI instalado: $version"

        # Check authentication
        try {
            gh auth status -ErrorAction SilentlyContinue | Out-Null
            Write-Success "GitHub CLI autenticado"
            Test-GHProjectScope
        }
        catch {
            Write-Warn "GitHub CLI não autenticado. Execute: gh auth login"
        }

        return $true
    }

    Write-Info "GitHub CLI não encontrado. Instalando..."

    # Try winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Info "Instalando GitHub CLI via winget..."
        winget install GitHub.cli --silent --accept-package-agreements --accept-source-agreements
        Write-Success "GitHub CLI instalado"
        Write-Warn "Execute 'gh auth login' para autenticar"
        return $true
    }
    else {
        Write-Warn "winget não disponível. Instalação manual necessária:"
        Write-Host ""
        Write-Host "  Baixe GitHub CLI de: https://cli.github.com/"
        Write-Host ""
        return $false
    }
}

# Check gh project scope
function Test-GHProjectScope {
    Write-Info "Verificando scope 'project' para GitHub Projects V2..."

    try {
        gh auth status 2>&1 | Out-Null
    }
    catch {
        Write-Warn "GitHub CLI não autenticado. Execute 'gh auth login' primeiro."
        return $false
    }

    # Check via API
    try {
        $scopes = gh api user -H "X-OAuth-Scopes: true" -ErrorAction Stop | Select-Object -First 1
        if ($scopes -match "project") {
            Write-Success "Scope 'project' disponível"
            return $true
        }
    }
    catch {
        # Ignore errors - scope check failed
        Write-Verbose "Não foi possível verificar scopes via API"
    }

    Write-Warn "Scope 'project' não encontrado"
    Write-Info "Este scope é necessário para gerenciar GitHub Projects V2"
    Write-Host ""
    Write-Host "Para adicionar o scope, execute:"
    Write-Host "  gh auth refresh -s project"
    Write-Host ""

    $addScope = Read-Host "Deseja adicionar o scope agora? [y/N]"
    if ($addScope -match "^[Yy]$") {
        Write-Info "Executando 'gh auth refresh -s project'..."
        try {
            gh auth refresh -s project
            Write-Success "Scope 'project' adicionado com sucesso"
            return $true
        }
        catch {
            Write-Error2 "Falha ao adicionar scope."
            Write-Info "Execute manualmente: gh auth refresh -s project"
            return $false
        }
    }
    else {
        Write-Warn "Scope 'project' não adicionado. GitHub Projects V2 pode não funcionar."
        return $false
    }
}

# Check Node.js
function Test-Node {
    Write-Info "Verificando Node.js..."

    if (Get-Command node -ErrorAction SilentlyContinue) {
        $version = node --version
        Write-Success "Node.js instalado: $version"
        return $true
    }

    Write-Info "Node.js não encontrado. Instalando..."

    # Try winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Info "Instalando Node.js via winget..."
        winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
        Write-Success "Node.js instalado"
        return $true
    }
    else {
        Write-Warn "winget não disponível. Instalação manual necessária:"
        Write-Host ""
        Write-Host "  Baixe Node.js de: https://nodejs.org/"
        Write-Host ""
        return $false
    }
}

# Install Claude Code
function Install-ClaudeCode {
    Write-Info "Verificando Claude Code..."

    if (Get-Command claude -ErrorAction SilentlyContinue) {
        Write-Success "Claude Code já instalado"
        return $true
    }

    Write-Info "Instalando Claude Code..."

    try {
        npm install -g @anthropic-ai/claude-code
        Write-Success "Claude Code instalado"
        return $true
    }
    catch {
        Write-Error2 "Falha ao instalar Claude Code"
        Write-Info "Execute manualmente: npm install -g @anthropic-ai/claude-code"
        return $false
    }
}

# Install Spec Kit
function Install-SpecKit {
    Write-Info "Verificando Spec Kit..."

    if (Get-Command specify -ErrorAction SilentlyContinue) {
        Write-Success "Spec Kit já instalado"
        return $true
    }

    Write-Info "Instalando Spec Kit do GitHub..."

    try {
        uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
        Write-Success "Spec Kit instalado"
        return $true
    }
    catch {
        Write-Warn "Falha ao instalar Spec Kit"
        Write-Info "Execute manualmente: uv tool install specify-cli --from git+https://github.com/github/spec-kit.git"
        return $false
    }
}

# Setup Python virtual environment
function Initialize-PythonVenv {
    Write-Info "Configurando ambiente virtual Python..."
    Write-Host ""

    # Create .venv if not exists
    if (-not (Test-Path ".venv")) {
        Write-Info "Criando virtualenv em .venv..."
        python -m venv .venv
        Write-Success "Virtualenv criado"
    }
    else {
        Write-Success "Virtualenv já existe"
    }

    # Activate virtualenv
    Write-Info "Ativando virtualenv..."
    & ".venv\Scripts\Activate.ps1"
    Write-Success "Virtualenv ativado"

    # Upgrade pip
    Write-Info "Atualizando pip..."
    python -m pip install --upgrade pip setuptools wheel --quiet

    Write-Host ""
}

# Install Python dependencies
function Install-PythonDeps {
    Write-Info "Instalando dependências Python..."
    Write-Host ""

    if (-not (Test-Path "requirements.txt")) {
        Write-Error2 "requirements.txt não encontrado!"
        Write-Info "Certifique-se de estar no diretório raiz do projeto"
        exit 1
    }

    Write-Info "Instalando pacotes de requirements.txt..."
    pip install -r requirements.txt
    Write-Success "Dependências Python instaladas"

    # Install Playwright browser
    Write-Info "Instalando browser Chromium para Playwright..."
    try {
        python -m playwright install chromium -ErrorAction SilentlyContinue
    }
    catch {
        Write-Warn "Playwright browser não foi instalado"
    }

    Write-Host ""
}

# Make scripts executable
function Set-ScriptsExecutable {
    Write-Info "Configurando permissões de scripts..."

    # Note: PowerShell doesn't need chmod, but we set execution policy
    if (Test-Path ".agentic_sdlc\scripts") {
        Write-Success "Scripts em .agentic_sdlc\scripts\ configurados"
    }

    if (Test-Path ".claude\hooks") {
        Write-Success "Hooks em .claude\hooks\ configurados"
    }

    if (Test-Path ".claude\skills") {
        Write-Success "Scripts das skills configurados"
    }
}

# Initialize Spec Kit
function Initialize-SpecKit {
    Write-Info "Inicializando Spec Kit no projeto..."

    if (Test-Path ".specify") {
        Write-Success "Projeto já inicializado com Spec Kit"
        return
    }

    Write-Info "Executando specify init..."
    try {
        specify init . --ai claude --force -ErrorAction SilentlyContinue
    }
    catch {
        Write-Warn "Spec Kit init falhou (pode ser normal se diretório não estiver vazio)"
    }
}

# Check Claude structure
function Test-ClaudeStructure {
    Write-Info "Verificando estrutura .claude/..."

    if (Test-Path ".claude") {
        $agentsCount = (Get-ChildItem -Path ".claude\agents" -Filter "*.md" -Recurse -ErrorAction SilentlyContinue).Count
        $skillsCount = (Get-ChildItem -Path ".claude\skills" -Filter "SKILL.md" -Recurse -ErrorAction SilentlyContinue).Count
        $commandsCount = (Get-ChildItem -Path ".claude\commands" -Filter "*.md" -ErrorAction SilentlyContinue).Count

        Write-Success "Estrutura .claude/ encontrada:"
        Write-Info "  - Agentes: $agentsCount"
        Write-Info "  - Skills: $skillsCount"
        Write-Info "  - Comandos: $commandsCount"
    }
    else {
        Write-Warn "Diretório .claude/ não encontrado"
    }
}

# Print summary
function Write-Summary {
    Write-Host ""
    Write-Host "========================================"
    Write-Host "   Setup Completo!"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Próximos passos:"
    Write-Host ""
    Write-Host "  1. Autenticar GitHub (se ainda não fez):"
    Write-Host "     gh auth login"
    Write-Host ""
    Write-Host "  2. Configurar Claude Code:"
    Write-Host "     claude"
    Write-Host "     (siga as instruções de autenticação)"
    Write-Host ""
    Write-Host "  3. Ativar virtualenv Python:"
    Write-Host "     .\.venv\Scripts\Activate.ps1"
    Write-Host ""
    Write-Host "  4. Iniciar workflow SDLC:"
    Write-Host "     claude ""/sdlc-start Minha nova feature"""
    Write-Host ""
    Write-Host "Documentação:"
    Write-Host "  - .agentic_sdlc\docs\guides\quickstart.md"
    Write-Host "  - .agentic_sdlc\docs\guides\infrastructure.md"
    Write-Host ""
}

# Check and migrate artifacts (ALWAYS, independent of origin)
function Assert-ArtifactsMigration {
    if ($Force) {
        return
    }

    if (Test-ProjectArtifactsInAgentic) {
        Write-Host ""
        Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "║          ⚠️  ARTEFATOS EM LOCAL INCORRETO ⚠️                ║" -ForegroundColor Yellow
        Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
        Write-Host ""
        Write-Warn "Artefatos de projeto detectados em .agentic_sdlc/"
        Write-Host ""
        Write-Host "REGRA DE OURO (v2.1.7+): Artefatos de PROJETO devem estar em .project/"
        Write-Host ""

        $choice = Read-Host "Deseja migrar estes artefatos para .project/ AGORA? [1] Sim / [2] Não / [3] Cancelar [1-3]"

        switch ($choice) {
            "1" {
                Write-Info "Executando migração automática..."
                if (Move-ProjectArtifacts) {
                    Write-Success "Migração concluída!"

                    $cleanChoice = Read-Host "Deseja limpar .agentic_sdlc/ agora? (backup será criado) [y/N]"
                    if ($cleanChoice -match "^[Yy]$") {
                        Clear-AgenticArtifacts
                    }
                    else {
                        Write-Info "Artefatos mantidos em .agentic_sdlc/ (duplicados)"
                    }
                }
                else {
                    Write-Error2 "Falha na migração. Tente manualmente: .\setup-sdlc.sh"
                    exit 1
                }
            }
            "2" {
                Write-Info "Instalação continuará. Migre manualmente depois:"
                Write-Host ""
                Write-Host "  .\.agentic_sdlc\scripts\migrate-artifacts.sh"
                Write-Host ""
            }
            "3" {
                Write-Info "Instalação cancelada."
                exit 0
            }
            default {
                Write-Error2 "Opção inválida."
                exit 1
            }
        }
    }
}

# Main execution
function Main {
    # Show splash
    Show-Splash

    # Give time to see splash
    Start-Sleep -Seconds 2

    # Check if running as Administrator (warn only, don't block)
    if (-not (Test-Administrator)) {
        Write-Warn "Este script não está sendo executado como Administrador."
        Write-Host ""
        Write-Host "Algumas instalações podem falhar ou requerer privilégios elevados."
        Write-Host "Recomendamos executar PowerShell como Administrador."
        Write-Host ""

        $continue = Read-Host "Deseja continuar mesmo assim? [y/N]"
        if ($continue -notmatch "^[Yy]$") {
            Write-Info "Instalação cancelada."
            Write-Host ""
            Write-Host "Para executar como Administrador:"
            Write-Host "  1. Abra PowerShell como Administrador (botão direito > Executar como Administrador)"
            Write-Host "  2. Navegue até o diretório do projeto"
            Write-Host "  3. Execute: .\setup-sdlc.ps1"
            Write-Host ""
            exit 0
        }
    }

    # ALWAYS check artifacts before continuing
    Assert-ArtifactsMigration

    # If installing from release
    if ($FromRelease) {
        Install-FromRelease
    }

    # Install dependencies (if not skipped)
    if (-not $SkipDeps) {
        Write-Host ""
        Write-Info "Instalando dependências..."
        Write-Host ""

        Test-Python | Out-Null
        Install-Uv | Out-Null
        Test-Git | Out-Null
        Test-GH | Out-Null
        Test-Node | Out-Null
        Install-ClaudeCode | Out-Null
        Install-SpecKit | Out-Null
        Initialize-PythonVenv
        Install-PythonDeps
    }

    Write-Host ""
    Write-Info "Configurando projeto..."
    Write-Host ""

    Set-ScriptsExecutable
    Initialize-SpecKit
    Test-ClaudeStructure

    Write-Summary
}

# Run main
Main
