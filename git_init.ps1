function Read-HostWithCancel {
	param (
		[string]$Prompt,
		[string]$DefaultValue = ""
	)

	$input = ""
	do {
		$showDefault = ($null -ne $DefaultValue -and $DefaultValue -ne "")
		if ($showDefault) {
			$msg = "$Prompt (ou 'cancelar' para sair) [default: $DefaultValue]"
		}
		else {
			$msg = "$Prompt (ou 'cancelar' para sair)"
		}
		$input = Read-Host $msg
		if ($input -eq 'cancelar') {
			Write-Host "Operação cancelada pelo usuário." -ForegroundColor Red
			exit
		}
		if ($showDefault -and [string]::IsNullOrWhiteSpace($input)) {
			$input = $DefaultValue
		}
	} while ([string]::IsNullOrWhiteSpace($input))
	return $input
}

function Set-GitConfiguration {
	$configured_gitname = git config user.name
	$userName = Read-HostWithCancel "Insira o seu nome" $configured_gitname
	git config --global user.name $userName

	$configured_gitemail = git config user.email
	$userEmail = Read-HostWithCancel "Insira o seu email" $configured_gitemail
	git config --global user.email $userEmail
}

function Initialize-LocalGitRepository {
	param (
		[string]$RepoPath,
		[string]$BranchName = "main"
	)

	Set-Location -Path $RepoPath
	git init
	git symbolic-ref HEAD refs/heads/$BranchName
	git add .
	git commit -m "Initial commit"
	Write-Host "Repositório local inicializado com sucesso em '$RepoPath'." -ForegroundColor Green
}

function Clone-GitRepository {
	param (
		[string]$RepoUrl,
		[string]$ClonePath
	)

	git clone $RepoUrl $ClonePath
	Write-Host "Repositório '$RepoUrl' clonado com sucesso em '$ClonePath'." -ForegroundColor Green
}

function Create-FeatureBranchAndPush {
	param (
		[string]$FeatureBranchName,
		[string]$RepoUrl
	)

	# Checando se a branch de feature já existe e criando-a se necessário
	if (-not (git branch --list $FeatureBranchName)) {
		git checkout -b $FeatureBranchName
	}
 else {
		git checkout $FeatureBranchName
	}
	
	# Adiciona a configuração do repositório remoto apenas se ainda não estiver configurado
	$remoteName = git remote
	if (-not $remoteName) {
		git remote add origin $RepoUrl
	}
	
	# O primeiro push da branch de feature pode precisar definir upstream
	git push --set-upstream origin $FeatureBranchName
	Write-Host "Branch de feature '$FeatureBranchName' criada e enviada para o repositório remoto '$RepoUrl'." -ForegroundColor Green
}

clear-host

# Configuração do usuário Git
Set-GitConfiguration

$operation = Read-HostWithCancel "Você deseja 'inicializar' um novo repositório local ou 'clonar' um repositório remoto? (inicializar/clonar)"
switch ($operation) {
	'inicializar' {
		$currentDir = (Get-Location).Path
		$repoPath = Read-HostWithCancel "Insira o caminho para inicializar o repositório" $currentDir
		if ([string]::IsNullOrWhiteSpace($repoPath)) {
			$repoPath = $currentDir
		}
		$branchName = Read-HostWithCancel "Insira o nome da branch principal" "main"
		Initialize-LocalGitRepository -RepoPath $repoPath -BranchName $branchName

		# Sugerir nome do repo pelo nome da pasta

		$repoFolder = Split-Path $repoPath -Leaf
		$githubOrg = $env:GITHUB_ORG
		$githubLogin = $env:GITHUB_USER
		$orgDefault = if (![string]::IsNullOrWhiteSpace($githubOrg)) { $githubOrg } elseif (![string]::IsNullOrWhiteSpace($githubLogin)) { $githubLogin } else { "" }
		$orgName = Read-HostWithCancel "Insira o nome da organização do repositório remoto (GitHub)" $orgDefault
		$defaultRepoName = $repoFolder
		if ($orgName -eq $defaultRepoName) {
			$defaultRepoName = "$repoFolder-repo"
		}
		$repoName = Read-HostWithCancel "Insira o nome do repositório remoto (GitHub)" $defaultRepoName


		# Token GitHub (opcional, pode vir do ambiente)
		$githubToken = $env:TOKEN_GITHUB
		$tokenValid = $false
		if (![string]::IsNullOrWhiteSpace($githubToken)) {
			# Testa se o token é válido tentando acessar o endpoint do usuário
			try {
				$me = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers @{Authorization = "token $githubToken" } -Method Get -ErrorAction Stop
				$tokenValid = $true
			}
			catch {
				$tokenValid = $false
			}
			if (-not $tokenValid) {
				$githubToken = Read-HostWithCancel "Insira seu GitHub Personal Access Token (com permissão para criar repositórios, ou deixe em branco para usar o CLI gh/git)" ""
			}
			else {
				Write-Host "TOKEN_GITHUB encontrado e válido. Usando token do ambiente." -ForegroundColor Green
			}
		}
		else {
			# Token vazio: não tenta autenticar, segue para gh CLI/manual
			$githubToken = ""
		}

		$repoUrl = "https://github.com/$orgName/$repoName.git"
		$repoExists = $false

		if ($githubToken) {
			# Verifica se repo existe via API
			$repoApiUrl = "https://api.github.com/repos/$orgName/$repoName"
			try {
				$resp = Invoke-RestMethod -Uri $repoApiUrl -Headers @{Authorization = "token $githubToken" } -Method Get -ErrorAction Stop
				$repoExists = $true
			}
			catch {
				$repoExists = $false
			}
			if (-not $repoExists) {
				Write-Host "Repositório remoto não existe. Criando no GitHub via API..." -ForegroundColor Yellow
				$createRepoUrl = "https://api.github.com/orgs/$orgName/repos"
				$body = @{ name = $repoName; private = $true } | ConvertTo-Json
				try {
					$resp = Invoke-RestMethod -Uri $createRepoUrl -Headers @{Authorization = "token $githubToken"; 'User-Agent' = 'PowerShell' } -Method Post -Body $body -ContentType 'application/json'
					Write-Host "Repositório criado com sucesso: $($resp.html_url)" -ForegroundColor Green
				}
				catch {
					Write-Host "Falha ao criar repositório remoto: $_" -ForegroundColor Red
					exit 1
				}
			}
			else {
				Write-Host "Repositório remoto já existe: https://github.com/$orgName/$repoName" -ForegroundColor Green
			}
		}
		else {
			# Sem token: tenta com gh CLI
			Write-Host "Tentando criar repositório remoto usando o GitHub CLI (gh)..." -ForegroundColor Yellow
			$ghExists = (Get-Command gh -ErrorAction SilentlyContinue) -ne $null
			if ($ghExists) {
				$ghCreateCmd = "gh repo create $orgName/$repoName --private --confirm"
				try {
					iex $ghCreateCmd
					Write-Host "Repositório criado com sucesso via gh CLI: https://github.com/$orgName/$repoName" -ForegroundColor Green
				}
				catch {
					Write-Host "Falha ao criar repositório via gh CLI: $_" -ForegroundColor Red
					exit 1
				}
			}
			else {
				Write-Host "GitHub CLI (gh) não encontrado. O repositório deve ser criado manualmente ou via site. Prosseguindo apenas com git remote add origin..." -ForegroundColor Red
			}
		}

		$featureBranchName = Read-HostWithCancel "Insira o nome da branch de feature para suas alterações" $repoName
		Create-FeatureBranchAndPush -FeatureBranchName $featureBranchName -RepoUrl $repoUrl
	}
	'clonar' {
		$repoUrl = Read-HostWithCancel "Insira a URL do repositório remoto"
		$clonePath = Read-HostWithCancel "Insira o caminho onde o repositório deve ser clonado"
		Clone-GitRepository -RepoUrl $repoUrl -ClonePath $clonePath
	}
	default {
		Write-Host "Operação desconhecida. Cancelando..." -ForegroundColor Red
		exit
	}
}
