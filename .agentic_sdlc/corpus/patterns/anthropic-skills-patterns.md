# Padroes Extraidos dos Skills Oficiais da Anthropic

**Fonte**: github.com/anthropics/skills
**Data de Extracao**: 2026-01-14
**Proposito**: Padroes de design production-grade para automacao de documentos e testes

---

## 1. Validation-First Pattern

### Descricao

Separar a criacao de documentos/codigo da validacao, usando ferramentas especializadas para cada etapa. Coletar TODOS os erros antes de reportar.

### Implementacao

```yaml
workflow:
  1_create:
    action: Gerar documento/codigo
    tool: openpyxl, python-docx, etc.

  2_validate:
    action: Executar validacao especializada
    tool: LibreOffice headless, linters, etc.

  3_report:
    action: Agregar erros em formato estruturado
    format: JSON com localizacao e sugestoes

  4_fix:
    action: Corrigir todos os problemas de uma vez
    benefit: Evita multiplas iteracoes
```

### Exemplo (xlsx skill)

```python
# 1. Criar planilha
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet['A1'] = '=SUM(B1:B10)'
workbook.save('report.xlsx')

# 2. Validar com LibreOffice
# recalc.py forca recalculo e detecta erros

# 3. Reportar
{
  "status": "errors_found",
  "total_errors": 3,
  "errors": [
    {"cell": "B5", "type": "#REF!", "formula": "=A1+Sheet2!Z99"},
    {"cell": "C10", "type": "#DIV/0!", "formula": "=A10/B10"}
  ],
  "suggestions": [
    "B5: Verifique se Sheet2!Z99 existe",
    "C10: B10 esta vazio ou zero"
  ]
}

# 4. Corrigir todos de uma vez
```

### Quando Usar

- Processamento de documentos (XLSX, DOCX, PDF)
- Geracao de codigo
- Builds de CI/CD
- Qualquer operacao que pode ter multiplos erros

### Beneficios

- Usuario ve todos os problemas de uma vez
- Reduz ciclos de correcao
- Melhora UX significativamente
- Permite priorizacao de correcoes

---

## 2. Multi-Tool Strategy Pattern

### Descricao

Usar a ferramenta mais adequada para cada tarefa, combinando diferentes linguagens e ferramentas CLI.

### Implementacao

```yaml
tools_by_task:
  extraction:
    language: Python
    libraries: [pdfplumber, openpyxl, python-docx]
    rationale: APIs pythonnicas, facil manipulacao de dados

  creation:
    language: JavaScript
    libraries: [docx, pptxgenjs]
    rationale: Melhor suporte a formatacao rica

  validation:
    tools: [LibreOffice, pandoc, tesseract]
    rationale: Ferramentas maduras, precisas, battle-tested

  conversion:
    tools: [pandoc, ImageMagick, poppler-utils]
    rationale: Padrao da industria
```

### Exemplo (docx skill)

```python
# Python para ler e processar
from docx import Document
doc = Document('input.docx')
text = '\n'.join([p.text for p in doc.paragraphs])

# JavaScript para criar com formatacao rica
// docx-js
const doc = new Document({
  sections: [{
    properties: {},
    children: [
      new Paragraph({
        children: [new TextRun("Hello World")],
      }),
    ],
  }],
});

# CLI para validacao
pandoc input.docx -t markdown -o output.md
```

### Quando Usar

- Tarefas que envolvem multiplas etapas
- Quando uma linguagem/ferramenta nao faz tudo bem
- Integracao de sistemas legados

### Beneficios

- Usa o melhor de cada ferramenta
- Permite fallbacks
- Mais resiliente a falhas

---

## 3. Confidence Scoring Pattern

### Descricao

Atribuir scores de confianca a findings/sugestoes e filtrar por threshold para reduzir ruido.

### Implementacao

```yaml
scoring:
  threshold: 80  # Minimo para reportar

  levels:
    high: 90-100     # Certeza alta, sempre reportar
    medium: 70-89    # Provavelmente correto
    low: 50-69       # Possivel falso positivo
    noise: 0-49      # Ignorar

  output:
    - Reportar apenas >= threshold
    - Low-confidence como warnings opcionais
```

### Exemplo (code-review plugin)

```python
findings = [
    {"issue": "SQL injection", "confidence": 95, "line": 42},
    {"issue": "Possible null", "confidence": 65, "line": 78},
    {"issue": "Style violation", "confidence": 55, "line": 100},
]

# Filtrar por threshold
threshold = 80
high_confidence = [f for f in findings if f["confidence"] >= threshold]

# Output
{
  "findings": high_confidence,  # Apenas SQL injection
  "filtered_count": 2,          # 2 foram filtrados
  "low_confidence_available": True
}
```

### Quando Usar

- Code review automatizado
- Analise de seguranca
- Deteccao de anomalias
- Qualquer sistema que gera muitos alertas

### Beneficios

- Reduz fadiga de alertas
- Foco nos problemas reais
- Menos falsos positivos
- Melhor signal-to-noise ratio

---

## 4. Parallel Agent Execution Pattern

### Descricao

Executar agentes/tarefas independentes em paralelo e consolidar resultados.

### Implementacao

```yaml
execution:
  parallel:
    agents:
      - security_agent     # Verifica vulnerabilidades
      - performance_agent  # Verifica performance
      - style_agent        # Verifica estilo
      - complexity_agent   # Verifica complexidade

  sequential:
    steps:
      - consolidate_findings
      - filter_by_confidence
      - deduplicate
      - generate_report
```

### Exemplo (pr-review-toolkit)

```python
import asyncio

async def run_parallel_review(pr_data):
    # Executar agentes em paralelo
    tasks = [
        asyncio.create_task(security_review(pr_data)),
        asyncio.create_task(performance_review(pr_data)),
        asyncio.create_task(style_review(pr_data)),
        asyncio.create_task(test_coverage_review(pr_data)),
    ]

    results = await asyncio.gather(*tasks)

    # Consolidar
    all_findings = []
    for result in results:
        all_findings.extend(result["findings"])

    # Deduplicate
    unique_findings = deduplicate(all_findings)

    return {
        "total_findings": len(unique_findings),
        "by_category": group_by_category(unique_findings),
        "high_priority": [f for f in unique_findings if f["severity"] == "high"],
    }
```

### Quando Usar

- Code review com multiplos aspectos
- Validacao de multiplas dimensoes
- Tarefas independentes que podem rodar simultaneamente

### Beneficios

- Reducao significativa de tempo
- Analise mais abrangente
- Escalabilidade

---

## 5. Reconnaissance-Then-Action Pattern

### Descricao

Sempre explorar/descobrir antes de agir. Nunca assumir estado ou seletores.

### Implementacao

```yaml
workflow:
  1_navigate:
    action: Ir para a pagina
    wait: networkidle

  2_capture:
    action: Screenshot ou inspecao DOM
    purpose: Descobrir estado atual

  3_discover:
    action: Identificar seletores reais
    method: Do DOM renderizado, nao hardcoded

  4_interact:
    action: Executar acoes
    using: Seletores descobertos
```

### Exemplo (webapp-testing)

```python
from playwright.sync_api import sync_playwright

def test_login(page):
    # 1. Navigate
    page.goto("http://localhost:3000/login")

    # 2. Wait for network idle
    page.wait_for_load_state("networkidle")

    # 3. Capture current state
    page.screenshot(path="before_login.png")

    # 4. Discover selectors from DOM
    # NAO usar seletores hardcoded
    email_input = page.locator('[data-testid="email"], input[type="email"]').first
    password_input = page.locator('[data-testid="password"], input[type="password"]').first

    # 5. Interact with discovered selectors
    if email_input.count() > 0:
        email_input.fill("test@example.com")
```

### Quando Usar

- Testes E2E
- Automacao de UI
- Web scraping
- Qualquer interacao com sistemas externos

### Beneficios

- Testes mais robustos
- Adapta a mudancas de UI
- Menos flaky tests
- Debugging mais facil

---

## 6. Zero-Error Policy Pattern

### Descricao

Documentos/artefatos criados devem ter ZERO erros. Validacao obrigatoria antes de entregar.

### Implementacao

```yaml
policy:
  scope: Documentos gerados pelo sistema
  errors_allowed: 0
  validation: Obrigatoria antes de entrega

  enforcement:
    - Pre-commit hook verifica erros
    - CI/CD falha se erros detectados
    - Review humano so apos zero-error
```

### Exemplo (xlsx skill)

```python
def create_report(data):
    # Criar planilha
    wb = create_workbook(data)

    # OBRIGATORIO: Validar antes de entregar
    validation = validate_workbook(wb)

    if validation["status"] == "errors_found":
        # NAO entregar com erros
        raise ValidationError(
            f"Planilha tem {validation['total_errors']} erros",
            errors=validation["errors"]
        )

    # Só entregar se zero-error
    return wb
```

### Quando Usar

- Geracao de documentos profissionais
- Relatorios financeiros
- Contratos e documentos legais
- Qualquer artefato que sera usado por terceiros

### Beneficios

- Qualidade garantida
- Confianca do usuario
- Menos retrabalho
- Profissionalismo

---

## Aplicacao no SDLC Agentico

### Mapeamento para Fases

| Padrao | Fases Aplicaveis | Agentes |
|--------|------------------|---------|
| Validation-First | 2, 5, 6, 7 | requirements-analyst, code-author, qa-analyst |
| Multi-Tool | 1, 3, 5 | domain-researcher, system-architect, code-author |
| Confidence Scoring | 6 | qa-analyst, code-reviewer, security-scanner |
| Parallel Execution | 1, 6 | domain-researcher, qa-analyst |
| Recon-Then-Action | 6 | qa-analyst (frontend-testing) |
| Zero-Error | 7 | release-manager, doc-generator |

### Integracao com Gate Evaluator

```yaml
# .claude/skills/gate-evaluator/gates/phase-6-to-7.yml
quality_criteria:
  - name: validation_first
    check: "Todos artefatos foram validados antes de entrega"

  - name: zero_errors
    check: "Zero erros em documentos gerados"

  - name: confidence_threshold
    check: "Findings com confidence >= 80"
```

---

## Referencias

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [xlsx skill](https://github.com/anthropics/skills/tree/main/skills/xlsx)
- [docx skill](https://github.com/anthropics/skills/tree/main/skills/docx)
- [webapp-testing skill](https://github.com/anthropics/skills/tree/main/skills/webapp-testing)
- [code-review plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review)
