<#
.SYNOPSIS
    Migra artefatos de .agentic_sdlc/ para .project/

.DESCRIPTION
    Este script migra artefatos de projeto do diretório .agentic_sdlc/ para .project/
    conforme a Regra de Ouro v2.1.7+.

    Pode ser executado a qualquer momento, mesmo após instalação.
    Detecta automaticamente se há artefatos para migrar.

.NOTES
    Author: SDLC Agentico Team
    Version: 3.0.4-pwsh7
    Requires: PowerShell Core 7+ (compatível com 5.1+)
    Last Updated: 2026-02-12
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# Funções de log com cores
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO]" -ForegroundColor Cyan -NoNewline
    Write-Host " $Message"
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS]" -ForegroundColor Green -NoNewline
    Write-Host " $Message"
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARNING]" -ForegroundColor Yellow -NoNewline
    Write-Host " $Message"
}

function Write-Error2 {
    param([string]$Message)
    Write-Host "[ERROR]" -ForegroundColor Red -NoNewline
    Write-Host " $Message"
}

# Variável global para contagem de artefatos
$script:ArtifactsCount = @{}

# Verifica se há artefatos para migrar
function Test-ArtifactsToMigrate {
    if (-not (Test-Path ".agentic_sdlc")) {
        Write-Error2 ".agentic_sdlc/ não encontrado!"
        exit 1
    }

    $hasArtifacts = $false
    $projectDirs = @("corpus", "architecture", "security", "reports", "references", "sessions")

    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗"
    Write-Host "║          MIGRAÇÃO DE ARTEFATOS - SDLC AGÊNTICO            ║"
    Write-Host "╚════════════════════════════════════════════════════════════╝"
    Write-Host ""
    Write-Info "Verificando artefatos em .agentic_sdlc/..."
    Write-Host ""

    foreach ($dir in $projectDirs) {
        $sourceDir = Join-Path ".agentic_sdlc" $dir
        if (Test-Path $sourceDir) {
            $count = (Get-ChildItem -Path $sourceDir -Recurse -File -ErrorAction SilentlyContinue |
                     Where-Object { $_.Name -ne ".gitkeep" }).Count
            if ($count -gt 0) {
                $script:ArtifactsCount[$dir] = $count
                $hasArtifacts = $true
                Write-Host "  • $dir/ ($count arquivos)"
            }
        }
    }

    if (-not $hasArtifacts) {
        Write-Host ""
        Write-Success "Nenhum artefato encontrado em .agentic_sdlc/"
        Write-Info "Seus artefatos já estão em .project/ ou não há artefatos para migrar."
        exit 0
    }

    Write-Host ""
    $totalFiles = ($script:ArtifactsCount.Values | Measure-Object -Sum).Sum
    Write-Host "Total de arquivos para migrar: $totalFiles"
    Write-Host ""
}

# Migra artefatos para .project/
function Move-Artifacts {
    Write-Info "Iniciando migração de artefatos..."
    Write-Host ""

    # Criar .project/ se não existir
    $projectPath = ".project"
    if (-not (Test-Path $projectPath)) {
        New-Item -ItemType Directory -Path $projectPath -Force | Out-Null
    }

    $migratedCount = 0
    $migratedFiles = 0

    foreach ($dir in $script:ArtifactsCount.Keys) {
        $sourceDir = Join-Path ".agentic_sdlc" $dir
        $destDir = Join-Path $projectPath $dir
        $count = $script:ArtifactsCount[$dir]

        if ($count -gt 0) {
            Write-Info "Migrando $sourceDir → $destDir ($count arquivos)"

            # Criar destino
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }

            # Copiar arquivos (preservando estrutura)
            try {
                $sourcePath = Join-Path $sourceDir "*"
                Copy-Item -Path $sourcePath -Destination $destDir -Recurse -Force -ErrorAction Stop

                # Remover .gitkeep do destino se existir
                $gitkeepPath = Join-Path $destDir ".gitkeep"
                if (Test-Path $gitkeepPath) {
                    Remove-Item $gitkeepPath -Force -ErrorAction SilentlyContinue
                }

                $migratedCount++
                $migratedFiles += $count
                Write-Success "  ✓ Migrado: $count arquivos"
            }
            catch {
                Write-Warn "  ⚠ Falha ao migrar $dir : $_"
            }
        }
    }

    Write-Host ""
    Write-Success "Migração completa!"
    Write-Host ""
    Write-Host "  Diretórios migrados: $migratedCount"
    Write-Host "  Arquivos migrados:   $migratedFiles"
    Write-Host ""
}

# Limpa .agentic_sdlc/ após migração
function Clear-AgenticArtifacts {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║          LIMPEZA DE .agentic_sdlc/                         ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""

    Write-Warn "Deseja remover os artefatos de .agentic_sdlc/ agora?"
    Write-Host ""
    Write-Host "Os arquivos já foram copiados para .project/"
    Write-Host "Um backup será criado antes da remoção."
    Write-Host ""

    $removeChoice = Read-Host "Remover artefatos de .agentic_sdlc/? [y/N]"

    if ($removeChoice -match "^[Yy]$") {
        # Criar backup
        $backupDir = ".agentic_sdlc.artifacts-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Write-Info "Criando backup em $backupDir..."

        # Copiar apenas artefatos
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        foreach ($dir in $script:ArtifactsCount.Keys) {
            $sourceDir = Join-Path ".agentic_sdlc" $dir
            if (Test-Path $sourceDir) {
                $destBackup = Join-Path $backupDir $dir
                Copy-Item -Path $sourceDir -Destination $destBackup -Recurse -Force -ErrorAction SilentlyContinue
            }
        }

        Write-Success "Backup criado: $backupDir"

        # Remover artefatos de .agentic_sdlc/ (manter framework)
        Write-Host ""
        Write-Info "Removendo artefatos de .agentic_sdlc/..."
        foreach ($dir in $script:ArtifactsCount.Keys) {
            $dirPath = Join-Path ".agentic_sdlc" $dir
            if (Test-Path $dirPath) {
                Remove-Item -Path $dirPath -Recurse -Force -ErrorAction SilentlyContinue
                New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
                $gitkeepPath = Join-Path $dirPath ".gitkeep"
                New-Item -ItemType File -Path $gitkeepPath -Force | Out-Null
            }
        }

        Write-Success "Artefatos removidos de .agentic_sdlc/"
        Write-Info "Framework mantido em .agentic_sdlc/ (scripts/, templates/, etc.)"
    }
    else {
        Write-Info "Artefatos mantidos em .agentic_sdlc/"
        Write-Warn "ATENÇÃO: Você tem duplicação agora (.agentic_sdlc/ E .project/)"
        Write-Warn "Recomendamos remover os artefatos de .agentic_sdlc/ após validar a migração."
    }
}

# Verificar estrutura de .project/
function Test-Migration {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗"
    Write-Host "║          VERIFICAÇÃO PÓS-MIGRAÇÃO                          ║"
    Write-Host "╚════════════════════════════════════════════════════════════╝"
    Write-Host ""

    Write-Info "Verificando .project/..."
    Write-Host ""

    foreach ($dir in $script:ArtifactsCount.Keys) {
        $destDir = Join-Path ".project" $dir
        if (Test-Path $destDir) {
            $count = (Get-ChildItem -Path $destDir -Recurse -File -ErrorAction SilentlyContinue |
                     Where-Object { $_.Name -ne ".gitkeep" }).Count
            $expected = $script:ArtifactsCount[$dir]

            if ($count -eq $expected) {
                Write-Host "  ✓ $dir/ - $count arquivos (OK)"
            }
            else {
                Write-Host "  ⚠ $dir/ - $count arquivos (esperado: $expected)"
            }
        }
    }

    Write-Host ""
    Write-Success "Verificação completa!"
    Write-Host ""
    Write-Info "Próximos passos:"
    Write-Host "  1. Verifique manualmente os arquivos em .project/"
    Write-Host "  2. Se tudo estiver OK, remova artefatos de .agentic_sdlc/ (se ainda não removeu)"
    Write-Host "  3. Commit as alterações: git add .project/ && git commit -m 'chore: migrate artifacts to .project/'"
    Write-Host ""
}

# Main
function Main {
    # Verificar se está no root do projeto
    if (-not (Test-Path ".claude")) {
        Write-Error2 "Execute este script no diretório raiz do projeto (onde está .claude/)"
        exit 1
    }

    # Verificar artefatos
    Test-ArtifactsToMigrate

    # Confirmar migração
    Write-Host "Deseja migrar estes artefatos para .project/?" -ForegroundColor Cyan
    Write-Host ""
    $confirm = Read-Host "Migrar agora? [Y/n]"

    if ($confirm -notmatch "^[Nn]$") {
        # Migrar
        Move-Artifacts

        # Verificar
        Test-Migration

        # Perguntar sobre limpeza
        Clear-AgenticArtifacts
    }
    else {
        Write-Info "Migração cancelada."
        exit 0
    }
}

# Executar
Main
