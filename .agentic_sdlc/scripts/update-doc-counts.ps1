<#
.SYNOPSIS
    Atualiza automaticamente as contagens de componentes na documentação

.DESCRIPTION
    Este script:
    1. Conta agentes, skills, hooks e comandos automaticamente
    2. Atualiza README.md e CLAUDE.md com as contagens corretas
    3. Valida que as atualizações foram aplicadas corretamente

.PARAMETER DryRun
    Mostra as mudanças sem aplicá-las

.PARAMETER Verbose
    Mostra saída detalhada

.EXAMPLE
    # Ver o que seria mudado
    .\update-doc-counts.ps1 -DryRun

.EXAMPLE
    # Aplicar as mudanças
    .\update-doc-counts.ps1

.EXAMPLE
    # Com saída detalhada
    .\update-doc-counts.ps1 -Verbose

.NOTES
    Author: SDLC Agentico Team
    Version: 3.0.4-pwsh7
    Requires: PowerShell Core 7+ (compatível com 5.1+)
    Last Updated: 2026-02-12
#>

[CmdletBinding()]
param(
    [switch]$DryRun
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
    Write-Host "[✓]" -ForegroundColor Green -NoNewline
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

# Determinar diretório raiz do projeto
$scriptDir = Split-Path -Parent $PSCommandPath
$projectRoot = (Get-Item $scriptDir).Parent.Parent.FullName
Set-Location $projectRoot

# Contar componentes
Write-Info "Counting framework components..."

$agents = (Get-ChildItem -Path (Join-Path ".claude" "agents") -Filter "*.md" -Recurse -ErrorAction SilentlyContinue).Count
$skills = (Get-ChildItem -Path (Join-Path ".claude" "skills") -Directory -ErrorAction SilentlyContinue).Count
$hooks = (Get-ChildItem -Path (Join-Path ".claude" "hooks") -Filter "*.sh" -Recurse -ErrorAction SilentlyContinue).Count
$commands = (Get-ChildItem -Path (Join-Path ".claude" "commands") -Filter "*.md" -ErrorAction SilentlyContinue).Count

Write-Success "Component counts:"
Write-Host "   - Agents: $agents"
Write-Host "   - Skills: $skills"
Write-Host "   - Hooks: $hooks"
Write-Host "   - Commands: $commands"
Write-Host ""

# Determinar breakdown de agentes (orchestrated vs consultive)
# Lightweight agents: failure-analyst, interview-simulator, requirements-interrogator, tradeoff-challenger
$consultive = 4
$orchestrated = $agents - $consultive

Write-Verbose "Agent breakdown: $orchestrated orchestrated + $consultive consultive = $agents total"

# Função para atualizar arquivo com regex
function Update-FileContent {
    param(
        [string]$FilePath,
        [string]$Pattern,
        [string]$Replacement,
        [string]$Description
    )

    Write-Verbose "Updating $FilePath`: $Description"

    if ($DryRun) {
        Write-Host "[DRY-RUN]" -ForegroundColor Yellow -NoNewline
        Write-Host " Would update $FilePath`:"
        Write-Host "   Pattern: $Pattern"
        Write-Host "   Replace: $Replacement"
        return
    }

    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw

        if ($content -match $Pattern) {
            $content = $content -replace $Pattern, $Replacement
            Set-Content -Path $FilePath -Value $content -NoNewline
            Write-Success "Updated $FilePath`: $Description"
        }
        else {
            Write-Warn "Pattern not found in $FilePath`: $Pattern"
        }
    }
    else {
        Write-Error2 "File not found: $FilePath"
    }
}

# Criar backups se não for dry-run
if (-not $DryRun) {
    Write-Info "Creating backups..."
    Copy-Item "README.md" "README.md.bak" -Force
    Copy-Item "CLAUDE.md" "CLAUDE.md.bak" -Force
    Write-Verbose "Backups created: README.md.bak, CLAUDE.md.bak"
}

Write-Host ""
Write-Info "Updating README.md..."

# Update README.md - Main description
Update-FileContent -FilePath "README.md" `
    -Pattern "\*\*\d+ agentes especializados\*\* \(\d+ orquestrados \+ \d+ consultivos\)" `
    -Replacement "**$agents agentes especializados** ($orchestrated orquestrados + $consultive consultivos)" `
    -Description "Main description agent count"

# Update README.md - ASCII diagram
Update-FileContent -FilePath "README.md" `
    -Pattern "│  \d+ Agentes" `
    -Replacement "│  $agents Agentes" `
    -Description "ASCII diagram agent count"

# Update README.md - Structure section - Agents
Update-FileContent -FilePath "README.md" `
    -Pattern "├── agents/\s+# \d+ agentes especializados.*" `
    -Replacement "├── agents/           # $agents agentes especializados ($orchestrated + $consultive consultivos)" `
    -Description "Structure section agent count"

# Update README.md - Structure section - Skills
Update-FileContent -FilePath "README.md" `
    -Pattern "├── skills/\s+# \d+ skills reutilizáveis" `
    -Replacement "├── skills/           # $skills skills reutilizáveis" `
    -Description "Structure section skill count"

# Update README.md - Structure section - Commands
Update-FileContent -FilePath "README.md" `
    -Pattern "├── commands/\s+# \d+ comandos do usuário" `
    -Replacement "├── commands/         # $commands comandos do usuário" `
    -Description "Structure section command count"

# Update README.md - Structure section - Hooks
Update-FileContent -FilePath "README.md" `
    -Pattern "├── hooks/\s+# \d+ hooks de automação" `
    -Replacement "├── hooks/            # $hooks hooks de automação" `
    -Description "Structure section hook count"

Write-Host ""
Write-Info "Updating CLAUDE.md..."

# Update CLAUDE.md - Main description
Update-FileContent -FilePath "CLAUDE.md" `
    -Pattern "\*\*\d+ specialized agents \(\d+ orchestrated \+ \d+ consultive\)\*\*" `
    -Replacement "**$agents specialized agents ($orchestrated orchestrated + $consultive consultive)**" `
    -Description "Main description agent count"

# Update CLAUDE.md - Configuration section
Update-FileContent -FilePath "CLAUDE.md" `
    -Pattern "- \d+ agents organized by SDLC phase \(\d+ orchestrated \+ \d+ consultive\)" `
    -Replacement "- $agents agents organized by SDLC phase ($orchestrated orchestrated + $consultive consultive)" `
    -Description "Configuration section agent count"

# Update CLAUDE.md - Structure section
Update-FileContent -FilePath "CLAUDE.md" `
    -Pattern "├── agents/\s+# Agent specs \(markdown\) - \d+ specialized roles" `
    -Replacement "├── agents/           # Agent specs (markdown) - $agents specialized roles" `
    -Description "Structure section agent count"

# Update CLAUDE.md - Agent Types table
Update-FileContent -FilePath "CLAUDE.md" `
    -Pattern "\| \*\*Orchestrated\*\* \| \d+ \|" `
    -Replacement "| **Orchestrated** | $orchestrated |" `
    -Description "Agent types table orchestrated count"

Write-Host ""

# Validar atualizações
if (-not $DryRun) {
    Write-Info "Validating updates..."
    $validationErrors = 0

    # Check README.md
    $readmeContent = Get-Content "README.md" -Raw

    if ($readmeContent -notmatch "$agents agentes especializados") {
        Write-Error2 "Validation failed: Agent count not updated in README.md main description"
        $validationErrors++
    }

    if ($readmeContent -notmatch "$agents Agentes") {
        Write-Error2 "Validation failed: Agent count not updated in README.md ASCII diagram"
        $validationErrors++
    }

    if ($readmeContent -notmatch "# $agents agentes especializados") {
        Write-Error2 "Validation failed: Agent count not updated in README.md structure"
        $validationErrors++
    }

    if ($readmeContent -notmatch "# $skills skills reutilizáveis") {
        Write-Error2 "Validation failed: Skill count not updated in README.md"
        $validationErrors++
    }

    if ($readmeContent -notmatch "# $commands comandos do usuário") {
        Write-Error2 "Validation failed: Command count not updated in README.md"
        $validationErrors++
    }

    if ($readmeContent -notmatch "# $hooks hooks de automação") {
        Write-Error2 "Validation failed: Hook count not updated in README.md"
        $validationErrors++
    }

    # Check CLAUDE.md
    $claudeContent = Get-Content "CLAUDE.md" -Raw

    if ($claudeContent -notmatch "$agents specialized agents") {
        Write-Error2 "Validation failed: Agent count not updated in CLAUDE.md main description"
        $validationErrors++
    }

    if ($validationErrors -eq 0) {
        Write-Success "All validations passed!"
    }
    else {
        Write-Error2 "$validationErrors validation(s) failed"
        Write-Host ""
        Write-Info "Restoring backups..."
        Copy-Item "README.md.bak" "README.md" -Force
        Copy-Item "CLAUDE.md.bak" "CLAUDE.md" -Force
        Remove-Item "README.md.bak" -Force
        Remove-Item "CLAUDE.md.bak" -Force
        exit 1
    }

    # Remove backups if successful
    Remove-Item "README.md.bak" -Force -ErrorAction SilentlyContinue
    Remove-Item "CLAUDE.md.bak" -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Success "Documentation counts updated successfully!"
