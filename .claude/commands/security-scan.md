---
name: security-scan
description: |
  Executa scan de seguranca no codigo e dependencias.
  Identifica vulnerabilidades antes do deploy.

  Examples:
  - <example>
    user: "/security-scan"
    assistant: "Vou executar scans de SAST, SCA e secrets"
    </example>
---

# Security Scan

## Instrucoes

Voce deve executar scans de seguranca e reportar vulnerabilidades.

## Tipos de Scan

### 1. SAST (Static Application Security Testing)
- Analise estatica do codigo
- Detecta vulnerabilidades no codigo fonte
- Ferramentas: bandit (Python), semgrep

### 2. SCA (Software Composition Analysis)
- Analise de dependencias
- Detecta CVEs em bibliotecas
- Ferramentas: pip-audit, npm audit, safety

### 3. Secret Detection
- Detecta secrets no codigo
- API keys, passwords, tokens
- Ferramentas: gitleaks, detect-secrets

## Processo

1. **Detectar Linguagem**: Identificar linguagens do projeto
2. **Selecionar Ferramentas**: Escolher ferramentas apropriadas
3. **Executar Scans**: Rodar cada tipo de scan
4. **Consolidar Resultados**: Agregar findings
5. **Classificar Severidade**: Categorizar por risco
6. **Gerar Report**: Produzir relatorio estruturado

## Comandos de Scan

```bash
# Python SAST
bandit -r src/ -f json -o reports/bandit.json

# Python SCA
pip-audit --format json > reports/pip-audit.json

# Secrets
gitleaks detect --source . --report-path reports/gitleaks.json

# JavaScript/Node
npm audit --json > reports/npm-audit.json

# Containers
trivy image myapp:latest --format json > reports/trivy.json
```

## Output Esperado

```yaml
security_report:
  scan_id: "SCAN-20260111-001"
  timestamp: "2026-01-11T..."
  scope: "src/"

  summary:
    critical: 0
    high: 2
    medium: 3
    low: 5
    total: 10

  findings:
    - id: "VULN-001"
      severity: "high"
      category: "SQL Injection"
      file: "src/orders/repository.py"
      line: 45
      remediation: "Use parameterized queries"

  verdict: "FAIL"
  blockers: ["VULN-001", "VULN-002"]
```

## Uso

```
/security-scan                 # Scan completo
/security-scan --type sast     # Apenas SAST
/security-scan --type sca      # Apenas dependencias
/security-scan --type secrets  # Apenas secrets
/security-scan --fix           # Tentar corrigir automaticamente
```
