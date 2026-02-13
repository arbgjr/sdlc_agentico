<#
.SYNOPSIS
    Valida que as contagens na documentação estão corretas

.DESCRIPTION
    Este script:
    1. Conta agentes, skills, hooks e comandos automaticamente
    2. Valida que README.md e CLAUDE.md têm as contagens corretas
    3. Verifica referências ao nome antigo do repositório
    4. Valida links e arquivos documentados
    5. Verifica consistência de versão Python

.PARAMETER Verbose
    Mostra saída detalhada

.EXAMPLE
    .\validate-doc-counts.ps1

.EXAMPLE
    .\validate-doc-counts.ps1 -Verbose

.NOTES
    Author: SDLC Agentico Team
    Version: 3.0.4-pwsh7
    Requires: PowerShell Core 7+ (compatível com 5.1+)
    Last Updated: 2026-02-12

    Exit codes:
      0 - Todas as validações passaram
      1 - Uma ou mais validações falharam
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"

# Funções de log
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO]" -ForegroundColor Blue -NoNewline
    Write-Host " $Message"
}

function Write-Success {
    param([string]$Message)
    Write-Host "[✓]" -ForegroundColor Green -NoNewline
    Write-Host " $Message"
}

function Write-ValidationError {
    param([string]$Message)
    Write-Host "[✗]" -ForegroundColor Red -NoNewline
    Write-Host " $Message"
    $script:ValidationErrors++
}

# Determinar diretório raiz do projeto
$scriptDir = Split-Path -Parent $PSCommandPath
$projectRoot = (Get-Item $scriptDir).Parent.Parent.FullName
Set-Location $projectRoot

# Contador de erros de validação
$script:ValidationErrors = 0

# Contar componentes
Write-Info "Counting framework components..."

$agents = (Get-ChildItem -Path (Join-Path ".claude" "agents") -Filter "*.md" -Recurse -ErrorAction SilentlyContinue).Count
$skills = (Get-ChildItem -Path (Join-Path ".claude" "skills") -Directory -ErrorAction SilentlyContinue).Count
$hooks = (Get-ChildItem -Path (Join-Path ".claude" "hooks") -Filter "*.sh" -Recurse -ErrorAction SilentlyContinue).Count
$commands = (Get-ChildItem -Path (Join-Path ".claude" "commands") -Filter "*.md" -ErrorAction SilentlyContinue).Count

Write-Verbose "Found: $agents agents, $skills skills, $hooks hooks, $commands commands"
Write-Host ""

# Validar README.md
Write-Info "Validating README.md..."

$readmeContent = Get-Content "README.md" -Raw -ErrorAction SilentlyContinue

if ($readmeContent) {
    if ($readmeContent -notmatch "$agents agentes especializados") {
        Write-ValidationError "Agent count mismatch in README.md main description (expected: $agents)"
    }

    if ($readmeContent -notmatch "$agents Agentes") {
        Write-ValidationError "Agent count mismatch in README.md ASCII diagram (expected: $agents)"
    }

    if ($readmeContent -notmatch "# $agents agentes especializados") {
        Write-ValidationError "Agent count mismatch in README.md structure section (expected: $agents)"
    }

    if ($readmeContent -notmatch "# $skills skills reutilizáveis") {
        Write-ValidationError "Skill count mismatch in README.md (expected: $skills)"
    }

    if ($readmeContent -notmatch "# $commands comandos do usuário") {
        Write-ValidationError "Command count mismatch in README.md (expected: $commands)"
    }

    if ($readmeContent -notmatch "# $hooks hooks de automação") {
        Write-ValidationError "Hook count mismatch in README.md (expected: $hooks)"
    }

    $errorsBeforeReadme = $script:ValidationErrors
    if ($errorsBeforeReadme -eq 0 -or $script:ValidationErrors -eq 0) {
        Write-Success "README.md counts are correct"
    }
}
else {
    Write-ValidationError "README.md not found"
}

Write-Host ""

# Validar CLAUDE.md
Write-Info "Validating CLAUDE.md..."

$claudeContent = Get-Content "CLAUDE.md" -Raw -ErrorAction SilentlyContinue

if ($claudeContent) {
    if ($claudeContent -notmatch "$agents specialized agents") {
        Write-ValidationError "Agent count mismatch in CLAUDE.md main description (expected: $agents)"
    }

    if ($claudeContent -notmatch "$agents agents organized by SDLC phase") {
        Write-ValidationError "Agent count mismatch in CLAUDE.md configuration section (expected: $agents)"
    }

    if ($claudeContent -notmatch "Agent specs \(markdown\) - $agents specialized roles") {
        Write-ValidationError "Agent count mismatch in CLAUDE.md structure section (expected: $agents)"
    }

    $errorsBeforeClaude = $script:ValidationErrors
    if ($claudeContent -match "$agents specialized agents" -and
        $claudeContent -match "$agents agents organized by SDLC phase" -and
        $claudeContent -match "Agent specs \(markdown\) - $agents specialized roles") {
        Write-Success "CLAUDE.md counts are correct"
    }
}
else {
    Write-ValidationError "CLAUDE.md not found"
}

Write-Host ""

# Verificar nome antigo do repositório
Write-Info "Checking for old repository name..."

$excludePaths = @(
    ".git",
    ".venv",
    "clean-test-repo.sh",
    "clean-test-repo.ps1",
    "validate-doc-counts.sh",
    "validate-doc-counts.ps1",
    "validate-docs.yml",
    "settings.local.json"
)

$searchPaths = @(
    ".agentic_sdlc\scripts",
    ".claude",
    ".agentic_sdlc\docs"
)

$foundOldName = $false
foreach ($searchPath in $searchPaths) {
    if (Test-Path $searchPath) {
        $files = Get-ChildItem -Path $searchPath -Recurse -File -ErrorAction SilentlyContinue |
                 Where-Object { $excludePaths -notcontains $_.Name }

        foreach ($file in $files) {
            $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
            if ($content -match "mice_dolphins") {
                Write-ValidationError "Found old repository name 'mice_dolphins' in $($file.FullName)"
                $foundOldName = $true
            }
        }
    }
}

if (-not $foundOldName) {
    Write-Success "No old repository name references found"
}

Write-Host ""

# Validar links
Write-Info "Validating documentation links..."

$troubleshootingPath = Join-Path ".agentic_sdlc" "docs" | Join-Path -ChildPath "guides" | Join-Path -ChildPath "troubleshooting.md"
if (-not (Test-Path $troubleshootingPath)) {
    Write-ValidationError "Referenced file .agentic_sdlc/docs/guides/troubleshooting.md does not exist"
}

$manualDevPath = Join-Path ".agentic_sdlc" "docs" | Join-Path -ChildPath "engineering-playbook" | Join-Path -ChildPath "manual-desenvolvimento"
if (-not (Test-Path $manualDevPath)) {
    Write-ValidationError "Referenced directory .agentic_sdlc/docs/engineering-playbook/manual-desenvolvimento does not exist"
}

$examplesPath = Join-Path ".agentic_sdlc" "docs" | Join-Path -ChildPath "examples"
if (Test-Path $examplesPath) {
    Write-ValidationError "Directory .agentic_sdlc/docs/examples exists but should not be in repository"
}

if ($script:ValidationErrors -eq 0 -or
    (Test-Path $troubleshootingPath) -and (Test-Path $manualDevPath) -and (-not (Test-Path $examplesPath))) {
    Write-Success "All documentation links are valid"
}

Write-Host ""

# Verificar consistência de versão Python
Write-Info "Checking Python version consistency..."

if ($readmeContent) {
    if ($readmeContent -notmatch "python-3\.11") {
        Write-ValidationError "Python badge should declare 3.11+ (found different version)"
    }

    if ($readmeContent -notmatch "Python.*3\.11\+") {
        Write-ValidationError "Python requirement should be 3.11+"
    }

    if ($readmeContent -match "python-3\.11" -and $readmeContent -match "Python.*3\.11\+") {
        Write-Success "Python version is consistent (3.11+)"
    }
}

Write-Host ""

# Resumo
Write-Host "═══════════════════════════════════════════════════════════════════"

if ($script:ValidationErrors -eq 0) {
    Write-Host "✓ All validations passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Component counts:"
    Write-Host "  - Agents: $agents"
    Write-Host "  - Skills: $skills"
    Write-Host "  - Hooks: $hooks"
    Write-Host "  - Commands: $commands"
    Write-Host ""
    exit 0
}
else {
    Write-Host "✗ Found $($script:ValidationErrors) validation error(s)" -ForegroundColor Red
    Write-Host ""
    Write-Host "To fix automatically, run:"
    Write-Host "  .\.agentic_sdlc\scripts\update-doc-counts.ps1"
    Write-Host ""
    exit 1
}
