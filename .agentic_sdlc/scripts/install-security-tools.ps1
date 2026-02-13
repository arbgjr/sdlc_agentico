<#
.SYNOPSIS
    Instala ferramentas de segurança opcionais para SDLC Agêntico

.DESCRIPTION
    Este script instala ferramentas de análise de segurança usadas pelo
    security-gate e security-scanner:
    - Semgrep (SAST - Static Application Security Testing)
    - Trivy (SCA - Dependency/Container Scanner)
    - Gitleaks (Secret Detection)

.PARAMETER All
    Instala todas as ferramentas de segurança

.PARAMETER Semgrep
    Instala apenas o Semgrep

.PARAMETER Trivy
    Instala apenas o Trivy

.PARAMETER Gitleaks
    Instala apenas o Gitleaks

.EXAMPLE
    .\install-security-tools.ps1 -All

.EXAMPLE
    .\install-security-tools.ps1 -Semgrep -Trivy

.NOTES
    Author: SDLC Agentico Team
    Version: 3.0.4-pwsh7
    Requires: PowerShell Core 7+ (compatível com 5.1+), winget ou chocolatey
    Last Updated: 2026-02-12
#>

[CmdletBinding()]
param(
    [switch]$All,
    [switch]$Semgrep,
    [switch]$Trivy,
    [switch]$Gitleaks
)

$ErrorActionPreference = "Stop"

# Funções de log
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

# Header
Write-Host ""
Write-Host "========================================"
Write-Host "   Security Tools - Instalador"
Write-Host "========================================"
Write-Host ""

# Se nenhuma flag específica, ativar All
if (-not $Semgrep -and -not $Trivy -and -not $Gitleaks) {
    $All = $true
}

# Verificar gerenciador de pacotes
function Test-PackageManager {
    $hasWinget = Get-Command winget -ErrorAction SilentlyContinue
    $hasChoco = Get-Command choco -ErrorAction SilentlyContinue

    if ($hasWinget) {
        Write-Info "Gerenciador de pacotes detectado: winget"
        return "winget"
    }
    elseif ($hasChoco) {
        Write-Info "Gerenciador de pacotes detectado: chocolatey"
        return "choco"
    }
    else {
        Write-Warn "Nenhum gerenciador de pacotes encontrado (winget/chocolatey)"
        Write-Host ""
        Write-Host "Recomendações:"
        Write-Host "  - winget: Já incluído no Windows 11 / Windows 10 22H2+"
        Write-Host "  - chocolatey: https://chocolatey.org/install"
        Write-Host ""
        return $null
    }
}

$packageManager = Test-PackageManager

# Instalar Semgrep
function Install-Semgrep {
    Write-Info "Verificando Semgrep..."

    if (Get-Command semgrep -ErrorAction SilentlyContinue) {
        $version = semgrep --version
        Write-Success "Semgrep já instalado: $version"
        return $true
    }

    Write-Info "Instalando Semgrep..."

    try {
        # Semgrep no Windows é melhor instalado via pip
        if (Get-Command pip -ErrorAction SilentlyContinue) {
            Write-Info "Instalando Semgrep via pip..."
            pip install semgrep
            Write-Success "Semgrep instalado"

            # Verificar se está no PATH
            if (-not (Get-Command semgrep -ErrorAction SilentlyContinue)) {
                Write-Warn "Semgrep instalado mas não está no PATH"
                Write-Info "Adicione ao PATH ou reinicie o terminal"
            }
            return $true
        }
        else {
            Write-Error2 "pip não encontrado. Instale Python 3.11+ primeiro."
            Write-Info "Ou instale manualmente: pip install semgrep"
            return $false
        }
    }
    catch {
        Write-Error2 "Falha ao instalar Semgrep: $_"
        Write-Info "Instale manualmente: pip install semgrep"
        Write-Info "Documentação: https://semgrep.dev/docs/getting-started/"
        return $false
    }
}

# Instalar Trivy
function Install-Trivy {
    Write-Info "Verificando Trivy..."

    if (Get-Command trivy -ErrorAction SilentlyContinue) {
        $version = trivy --version
        Write-Success "Trivy já instalado: $version"
        return $true
    }

    Write-Info "Instalando Trivy..."

    try {
        if ($packageManager -eq "winget") {
            Write-Info "Instalando Trivy via winget..."
            winget install Aquasecurity.Trivy --silent --accept-package-agreements --accept-source-agreements
            Write-Success "Trivy instalado"
            return $true
        }
        elseif ($packageManager -eq "choco") {
            Write-Info "Instalando Trivy via chocolatey..."
            choco install trivy -y
            Write-Success "Trivy instalado"
            return $true
        }
        else {
            Write-Warn "Instalação manual necessária para Trivy"
            Write-Host ""
            Write-Host "Baixe o binário de: https://github.com/aquasecurity/trivy/releases"
            Write-Host "E adicione ao PATH"
            Write-Host ""
            return $false
        }
    }
    catch {
        Write-Error2 "Falha ao instalar Trivy: $_"
        Write-Info "Baixe manualmente: https://github.com/aquasecurity/trivy/releases"
        return $false
    }
}

# Instalar Gitleaks
function Install-Gitleaks {
    Write-Info "Verificando Gitleaks..."

    if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
        $version = gitleaks version
        Write-Success "Gitleaks já instalado: $version"
        return $true
    }

    Write-Info "Instalando Gitleaks..."

    try {
        if ($packageManager -eq "winget") {
            Write-Info "Instalando Gitleaks via winget..."
            winget install Gitleaks.Gitleaks --silent --accept-package-agreements --accept-source-agreements
            Write-Success "Gitleaks instalado"
            return $true
        }
        elseif ($packageManager -eq "choco") {
            Write-Info "Instalando Gitleaks via chocolatey..."
            choco install gitleaks -y
            Write-Success "Gitleaks instalado"
            return $true
        }
        else {
            Write-Warn "Instalação manual necessária para Gitleaks"
            Write-Host ""
            Write-Host "Baixe o binário de: https://github.com/gitleaks/gitleaks/releases"
            Write-Host "E adicione ao PATH"
            Write-Host ""
            return $false
        }
    }
    catch {
        Write-Error2 "Falha ao instalar Gitleaks: $_"
        Write-Info "Baixe manualmente: https://github.com/gitleaks/gitleaks/releases"
        return $false
    }
}

# Main
function Main {
    Write-Host "Ferramentas a serem instaladas:"

    if ($All -or $Semgrep) {
        Write-Host "  ✓ Semgrep (SAST)"
    }
    if ($All -or $Trivy) {
        Write-Host "  ✓ Trivy (SCA/Container Scanner)"
    }
    if ($All -or $Gitleaks) {
        Write-Host "  ✓ Gitleaks (Secret Detection)"
    }

    Write-Host ""

    $results = @{
        "Semgrep" = $null
        "Trivy" = $null
        "Gitleaks" = $null
    }

    # Instalar ferramentas
    if ($All -or $Semgrep) {
        $results["Semgrep"] = Install-Semgrep
        Write-Host ""
    }

    if ($All -or $Trivy) {
        $results["Trivy"] = Install-Trivy
        Write-Host ""
    }

    if ($All -or $Gitleaks) {
        $results["Gitleaks"] = Install-Gitleaks
        Write-Host ""
    }

    # Resumo
    Write-Host "========================================"
    Write-Host "   Resumo da Instalação"
    Write-Host "========================================"
    Write-Host ""

    foreach ($tool in $results.Keys) {
        if ($null -ne $results[$tool]) {
            if ($results[$tool]) {
                Write-Host "  ✓ $tool" -ForegroundColor Green -NoNewline
                Write-Host " - OK"
            }
            else {
                Write-Host "  ✗ $tool" -ForegroundColor Red -NoNewline
                Write-Host " - FALHOU"
            }
        }
    }

    Write-Host ""
    Write-Info "Instalação concluída!"
    Write-Host ""
    Write-Info "Para usar estas ferramentas:"
    Write-Host "  - Semgrep: semgrep scan --config auto ."
    Write-Host "  - Trivy: trivy fs ."
    Write-Host "  - Gitleaks: gitleaks detect"
    Write-Host ""
}

# Executar
Main
