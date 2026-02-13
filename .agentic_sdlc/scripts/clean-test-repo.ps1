<#
.SYNOPSIS
    Limpa um repositório de teste mantendo apenas LICENSE e README.md

.DESCRIPTION
    Remove todos os arquivos e diretórios de um repositório git de teste,
    preservando apenas .git, LICENSE e README.md original (se existir).
    Útil para resetar repositórios de teste rapidamente.

.PARAMETER RepoPath
    Caminho do repositório a limpar. Padrão: diretório atual

.EXAMPLE
    .\clean-test-repo.ps1

.EXAMPLE
    .\clean-test-repo.ps1 -RepoPath "C:\projetos\teste-repo"

.NOTES
    Author: SDLC Agentico Team
    Version: 3.0.4-pwsh7
    Requires: PowerShell Core 7+ (compatível com 5.1+), Git
    Last Updated: 2026-02-12

    ⚠️ ATENÇÃO: Este script REMOVE arquivos. Use com cuidado!
#>

[CmdletBinding()]
param(
    [string]$RepoPath = (Get-Location).Path
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
Write-Host "=== Limpando Repositório de Teste ===" -ForegroundColor Cyan
Write-Host "Path: $RepoPath"
Write-Host "Timestamp: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
Write-Host ""

# Validar que é um repositório git
$gitPath = Join-Path $RepoPath ".git"
if (-not (Test-Path $gitPath)) {
    Write-Error2 "$RepoPath não é um repositório git"
    exit 1
}

# Mudar para o diretório do repositório
Push-Location $RepoPath

try {
    # [1/5] Restaurar LICENSE do git se existir
    Write-Info "[1/5] Restaurando LICENSE..."
    try {
        git checkout LICENSE -ErrorAction Stop 2>$null
        Write-Success "LICENSE restaurado do git"
    }
    catch {
        Write-Warn "LICENSE não existe no git"
    }

    # [2/5] Salvar conteúdo original do README.md se existir
    Write-Info "[2/5] Verificando README.md..."
    $readmeContent = $null
    $readmePath = "README.md"

    if (Test-Path $readmePath) {
        $currentContent = Get-Content $readmePath -Raw -ErrorAction SilentlyContinue

        # Verificar se é o README original (não gerado pelo framework)
        if ($currentContent -match "SDLC Agêntico") {
            Write-Info "README.md contém conteúdo do framework, será recriado"
        }
        else {
            $readmeContent = $currentContent
            Write-Success "README.md original preservado"
        }
    }
    else {
        Write-Info "README.md não existe"
    }

    # [3/5] Remover todos os arquivos e diretórios exceto .git e LICENSE
    Write-Info "[3/5] Removendo arquivos..."

    Get-ChildItem -Path . -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -ne '.git' -and $_.Name -ne 'LICENSE'
        } |
        ForEach-Object {
            try {
                Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
                Write-Verbose "Removido: $($_.Name)"
            }
            catch {
                Write-Warn "Não foi possível remover: $($_.Name)"
            }
        }

    Write-Success "Arquivos removidos"

    # [4/5] Limpar arquivos não rastreados pelo git
    Write-Info "[4/5] Limpando arquivos não rastreados..."
    try {
        git clean -fd -ErrorAction SilentlyContinue 2>$null | Out-Null
        Write-Success "Arquivos não rastreados removidos"
    }
    catch {
        Write-Warn "git clean falhou (pode ser normal)"
    }

    # [5/5] Criar/restaurar README.md
    Write-Info "[5/5] Criando README.md..."

    if ($readmeContent) {
        # Restaurar README original
        Set-Content -Path $readmePath -Value $readmeContent -NoNewline
        Write-Success "README.md original restaurado"
    }
    else {
        # Criar README.md padrão baseado no nome do repositório
        $repoName = Split-Path -Leaf $RepoPath

        # Capitalizar primeira letra
        $repoNameCapitalized = $repoName.Substring(0, 1).ToUpper() + $repoName.Substring(1)

        $defaultReadme = @"
# $repoNameCapitalized

Projeto em desenvolvimento usando SDLC Agêntico.

## Status

Aguardando início do ciclo de desenvolvimento.

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.
"@

        Set-Content -Path $readmePath -Value $defaultReadme -NoNewline
        Write-Success "README.md padrão criado"
    }

    # Resultado final
    Write-Host ""
    Write-Host "=== Limpeza Concluída ===" -ForegroundColor Green
    Write-Host ""
    Write-Info "Estado atual do repositório:"
    Get-ChildItem -Force | Format-Table Name, Length, LastWriteTime -AutoSize

    # Mostrar status git
    Write-Host ""
    Write-Info "Git status:"
    git status --short
}
finally {
    # Voltar ao diretório original
    Pop-Location
}
