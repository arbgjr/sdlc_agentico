<#
.SYNOPSIS
    Valida se uma fase do SDLC foi completada corretamente

.DESCRIPTION
    Verifica a estrutura e artefatos obrigatórios de cada fase do SDLC Agêntico.
    Valida arquivos YAML e reporta erros encontrados.

.PARAMETER ProjectPath
    Caminho do projeto a validar. Padrão: diretório atual

.PARAMETER Phase
    Número da fase a validar (0-3). Padrão: 0

.EXAMPLE
    .\validate-sdlc-phase.ps1 -ProjectPath "C:\projetos\meu-app" -Phase 0

.EXAMPLE
    .\validate-sdlc-phase.ps1 -Phase 2

.NOTES
    Author: SDLC Agentico Team
    Version: 3.0.4-pwsh7
    Requires: PowerShell Core 7+ (compatível com 5.1+), Python 3 (para validação YAML)
    Last Updated: 2026-02-12
#>

[CmdletBinding()]
param(
    [string]$ProjectPath = (Get-Location).Path,
    [ValidateRange(0, 3)]
    [int]$Phase = 0
)

$ErrorActionPreference = "Continue"

# Header
Write-Host ""
Write-Host "=== Validação de Fase SDLC ===" -ForegroundColor Cyan
Write-Host "Projeto: $ProjectPath"
Write-Host "Fase: $Phase"
Write-Host "Timestamp: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
Write-Host ""

# Variável de erro global
$script:ErrorCount = 0

# Função para verificar arquivo
function Test-RequiredFile {
    param(
        [string]$FilePath,
        [bool]$Required = $true
    )

    $fileName = Split-Path -Leaf $FilePath

    if (Test-Path $FilePath) {
        $size = (Get-Item $FilePath).Length
        Write-Host "  ✅ $fileName ($size bytes)" -ForegroundColor Green
        return $true
    }
    else {
        if ($Required) {
            Write-Host "  ❌ $fileName - MISSING (REQUIRED)" -ForegroundColor Red
            $script:ErrorCount++
            return $false
        }
        else {
            Write-Host "  ⚠️  $fileName - missing (optional)" -ForegroundColor Yellow
            return $false
        }
    }
}

# Função para validar YAML
function Test-YamlFile {
    param([string]$FilePath)

    $fileName = Split-Path -Leaf $FilePath

    if (-not (Test-Path $FilePath)) {
        return $false
    }

    # Verificar se Python está disponível
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }

    if ($python) {
        try {
            $validateScript = "import yaml; yaml.safe_load(open('$($FilePath.Replace('\', '/'))'))"
            & $python.Source -c $validateScript -ErrorAction Stop 2>$null

            Write-Host "  ✅ YAML válido: $fileName" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "  ❌ YAML inválido: $fileName" -ForegroundColor Red
            $script:ErrorCount++
            return $false
        }
    }
    else {
        Write-Host "  ⚠️  Python não encontrado, pulando validação YAML" -ForegroundColor Yellow
        return $false
    }
}

# [1/4] Verificar estrutura base
Write-Host "[1/4] Verificando estrutura SDLC..."

$sdlcPath = Join-Path $ProjectPath ".agentic_sdlc"
if (-not (Test-Path $sdlcPath)) {
    Write-Host "  ❌ Diretório .agentic_sdlc não encontrado" -ForegroundColor Red
    $script:ErrorCount++
}
else {
    Write-Host "  ✅ Diretório .agentic_sdlc existe" -ForegroundColor Green
}

# [2/4] Verificar projeto
Write-Host ""
Write-Host "[2/4] Verificando projeto..."

$projectsPath = Join-Path $sdlcPath "projects"
$projectDir = $null

if (Test-Path $projectsPath) {
    $projectDirs = Get-ChildItem -Path $projectsPath -Directory -ErrorAction SilentlyContinue |
                   Where-Object { $_.Name -ne "projects" } |
                   Select-Object -First 1

    if ($projectDirs) {
        $projectDir = $projectDirs.FullName
        Write-Host "  ✅ Projeto encontrado: $($projectDirs.Name)" -ForegroundColor Green

        # Verificar manifest
        $manifestPath = Join-Path $projectDir "manifest.yml"
        if (Test-RequiredFile -FilePath $manifestPath -Required $true) {
            Test-YamlFile -FilePath $manifestPath | Out-Null
        }
    }
    else {
        Write-Host "  ❌ Nenhum projeto encontrado em $projectsPath" -ForegroundColor Red
        $script:ErrorCount++
    }
}
else {
    Write-Host "  ❌ Diretório projects/ não encontrado" -ForegroundColor Red
    $script:ErrorCount++
}

# [3/4] Verificar artefatos da fase
Write-Host ""
Write-Host "[3/4] Verificando artefatos da Phase $Phase..."

if ($projectDir) {
    $phaseDir = Join-Path $projectDir "phase-$Phase"

    switch ($Phase) {
        0 {
            Write-Host "Phase 0 - Preparation:"

            $intakeAnalysis = Join-Path $phaseDir "intake-analysis.yml"
            $complianceAssessment = Join-Path $phaseDir "compliance-assessment.yml"
            $complianceSummary = Join-Path $phaseDir "compliance-summary.md"
            $complianceChecklist = Join-Path $phaseDir "compliance-checklist.md"

            Test-RequiredFile -FilePath $intakeAnalysis -Required $true | Out-Null
            Test-RequiredFile -FilePath $complianceAssessment -Required $true | Out-Null
            Test-RequiredFile -FilePath $complianceSummary -Required $false | Out-Null
            Test-RequiredFile -FilePath $complianceChecklist -Required $false | Out-Null

            # Validar YAMLs
            if (Test-Path $intakeAnalysis) {
                Test-YamlFile -FilePath $intakeAnalysis | Out-Null
            }
            if (Test-Path $complianceAssessment) {
                Test-YamlFile -FilePath $complianceAssessment | Out-Null
            }
        }
        1 {
            Write-Host "Phase 1 - Discovery:"

            $researchBrief = Join-Path $phaseDir "research-brief.yml"
            $techRecommendations = Join-Path $phaseDir "technology-recommendations.md"

            Test-RequiredFile -FilePath $researchBrief -Required $true | Out-Null
            Test-RequiredFile -FilePath $techRecommendations -Required $false | Out-Null

            # Validar YAML
            if (Test-Path $researchBrief) {
                Test-YamlFile -FilePath $researchBrief | Out-Null
            }
        }
        2 {
            Write-Host "Phase 2 - Requirements:"

            $spec = Join-Path $phaseDir "spec.yml"
            $userStories = Join-Path $phaseDir "user-stories.yml"
            $nfr = Join-Path $phaseDir "nfr.yml"

            Test-RequiredFile -FilePath $spec -Required $true | Out-Null
            Test-RequiredFile -FilePath $userStories -Required $true | Out-Null
            Test-RequiredFile -FilePath $nfr -Required $false | Out-Null

            # Validar YAMLs
            if (Test-Path $spec) {
                Test-YamlFile -FilePath $spec | Out-Null
            }
            if (Test-Path $userStories) {
                Test-YamlFile -FilePath $userStories | Out-Null
            }
            if (Test-Path $nfr) {
                Test-YamlFile -FilePath $nfr | Out-Null
            }
        }
        3 {
            Write-Host "Phase 3 - Architecture:"

            $architecture = Join-Path $phaseDir "architecture.yml"
            $threatModel = Join-Path $phaseDir "threat-model.yml"

            Test-RequiredFile -FilePath $architecture -Required $true | Out-Null
            Test-RequiredFile -FilePath $threatModel -Required $true | Out-Null

            # ADRs podem estar em subdiretório
            if (Test-Path $phaseDir) {
                $adrCount = (Get-ChildItem -Path $phaseDir -Filter "adr-*.yml" -Recurse -ErrorAction SilentlyContinue).Count
                if ($adrCount -gt 0) {
                    Write-Host "  ✅ $adrCount ADR(s) encontrado(s)" -ForegroundColor Green
                }
                else {
                    Write-Host "  ⚠️  Nenhum ADR encontrado (recomendado ter pelo menos 1)" -ForegroundColor Yellow
                }
            }

            # Validar YAMLs
            if (Test-Path $architecture) {
                Test-YamlFile -FilePath $architecture | Out-Null
            }
            if (Test-Path $threatModel) {
                Test-YamlFile -FilePath $threatModel | Out-Null
            }
        }
        default {
            Write-Host "Validação para Phase $Phase não implementada ainda" -ForegroundColor Yellow
        }
    }
}

# [4/4] Resultado final
Write-Host ""
Write-Host "[4/4] Resultado..."
Write-Host "========================================"

if ($script:ErrorCount -eq 0) {
    Write-Host "✅ Phase $Phase VALIDADA com sucesso!" -ForegroundColor Green
    Write-Host "   Pode avançar para Phase $($Phase + 1)"
    exit 0
}
else {
    Write-Host "❌ Phase $Phase com $($script:ErrorCount) erro(s)" -ForegroundColor Red
    Write-Host "   Corrija os erros antes de avançar"
    exit 1
}
