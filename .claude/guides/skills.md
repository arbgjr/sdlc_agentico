# Skills: Guia Completo

**Versão**: 2.0
**Última Atualização**: 2026-01-11
**Referência oficial**: https://code.claude.com/docs/en/skills

---

## 📋 Índice

1. [O Que São?](#o-que-são)
2. [Progressive Disclosure](#progressive-disclosure)
3. [Estrutura de Skills](#estrutura-de-skills)
4. [Criando Skills](#criando-skills)
5. [Frontmatter (Metadados)](#frontmatter-metadados)
6. [Context Fork](#context-fork)
7. [Hooks em Skills](#hooks-em-skills)
8. [Integração com Subagents](#integração-com-subagents)
9. [Padrões de Organização](#padrões-de-organização)
10. [Workflows e Validação](#workflows-e-validação)
11. [Allowed Tools](#allowed-tools)
12. [Built-in Skills (API)](#built-in-skills-api)
13. [Custom Skills (Upload)](#custom-skills-upload)
14. [Exemplos Práticos](#exemplos-práticos)
15. [Troubleshooting](#troubleshooting)

---

## O Que São?

Skills são **capacidades modulares** que Claude invoca automaticamente quando relevante. Diferente de slash commands, Claude **decide sozinho** quando usar uma skill.

**Características:**

- ✅ Ativação **automática** (Claude decide)
- ✅ Estrutura de diretório (múltiplos arquivos)
- ✅ Progressive disclosure (carrega apenas o necessário)
- ✅ Suporta scripts, templates, recursos
- ✅ Reutilizável entre projetos

**Quando usar:**

- Capacidades modulares que Claude deve ativar automaticamente
- Processos que precisam de múltiplos arquivos (scripts, templates)
- Workflows complexos com progressive disclosure

---

## Progressive Disclosure

Skills usam **progressive disclosure** - carregam informações em **3 níveis**:

### Nível 1 - Metadados (sempre carregado)

**~100 tokens por skill**

```yaml
name: pdf-processing
description: "Extracts text and tables from PDFs, fills forms, merges documents. Use when working with PDF files."
```

Claude vê **todos** os metadados de todas as skills disponíveis.

### Nível 2 - Instruções (carregado quando ativado)

**~5k tokens**

```markdown
# SKILL.md body

## Mission
Extract and manipulate PDF content.

## Workflow
1. Validate PDF file
2. Extract content
3. Process data
4. Generate output
```

Claude carrega o corpo do `SKILL.md` **apenas** quando decide usar a skill.

### Nível 3 - Recursos (carregado sob demanda)

**Via bash, sem carregar no contexto**

```bash
python scripts/extract.py
cat templates/form.pdf
cat docs/reference.md
```

Claude executa comandos para acessar recursos **sem** consumir contexto.

**Benefício**: Minimize uso de contexto - carregue apenas o necessário.

---

## Estrutura de Skills

### Armazenamento

```bash
# Skills de projeto (compartilhadas via Git)
.claude/skills/
├── pdf-processing/
│   ├── SKILL.md             # Obrigatório
│   ├── scripts/
│   │   ├── extract.py       # Scripts auxiliares
│   │   └── fill_form.py
│   ├── templates/
│   │   └── form.pdf         # Templates
│   └── docs/
│       ├── reference.md     # Docs estendidas
│       └── examples.md
└── api-testing/
    └── SKILL.md

# Skills pessoais (apenas você)
~/.claude/skills/
├── my-workflow/
│   └── SKILL.md
└── personal-tools/
    └── SKILL.md

# Skills de plugins (instalados)
~/.claude/plugins/my-plugin/skills/
└── plugin-skill/
    └── SKILL.md
```

**Precedência**: Projeto > Pessoal > Plugin

### Estrutura Recomendada

```
my-skill/
├── SKILL.md                 # Instruções principais (<500 linhas)
├── README.md                # Documentação externa (opcional)
├── scripts/                 # Scripts executáveis
│   ├── process.py
│   ├── validate.sh
│   └── utils.py
├── templates/               # Templates
│   ├── output.xlsx
│   └── report.md
└── docs/                    # Documentação estendida
    ├── reference.md         # Carregado sob demanda
    ├── examples.md
    └── advanced.md
```

---

## Criando Skills

### Skill Básica

**Arquivo obrigatório**: `SKILL.md`

```markdown
---
name: pdf-form-filling
description: "Fills PDF forms with provided data. Use when user needs to populate PDF forms or extract/modify PDF form fields."
---

# PDF Form Filling Skill

## Mission
Fill PDF forms programmatically using provided data.

## Workflow
1. Validate PDF file exists
2. Extract form field names
3. Map data to fields
4. Generate filled PDF
5. Verify output

## Usage

To fill a PDF form:
1. Provide PDF path
2. Provide data as JSON or key-value pairs
3. Skill will generate filled PDF

## Output Format
```json
{
  "status": "success",
  "output_file": "/path/to/filled.pdf",
  "fields_filled": 15
}
```

```

**Salvar em**: `.claude/skills/pdf-form-filling/SKILL.md`

### Skill com Scripts

```markdown
---
name: pdf-processing
description: "Extract text, tables, and metadata from PDF files. Use when user needs to analyze or process PDF documents."
allowed-tools: Bash(python:*)
---

# PDF Processing Skill

## Mission
Extract and analyze PDF content.

## Workflow
1. Validate PDF exists
2. Extract content using script
3. Process extracted data
4. Return structured output

## Scripts Available

**List form fields**:
```bash
python scripts/extract_fields.py <pdf-path>
```

**Fill form**:

```bash
python scripts/fill_form.py <pdf-path> <data.json>
```

**Extract text**:

```bash
python scripts/extract_text.py <pdf-path>
```

## Edge Cases

- Handle password-protected PDFs
- Validate data types before filling
- Check for missing form fields

```

**Estrutura**:
```

.claude/skills/pdf-processing/
├── SKILL.md
└── scripts/
    ├── extract_fields.py
    ├── fill_form.py
    └── extract_text.py

```

---

## Frontmatter (Metadados)

```yaml
---
name: skill-name-lowercase                     # Obrigatório
description: "What it does + when to use"     # Obrigatório (max 1024 chars)
allowed-tools:                                 # Opcional (herda tudo se omitido)
  - Bash
  - Read
  - Write
model: sonnet                                  # Opcional: haiku, sonnet, opus
context: fork                                  # Opcional: execução isolada
agent: true                                    # Opcional: executar como agente
user-invocable: true                           # Opcional: mostrar em /skill
disable-model-invocation: false                # Opcional: desativar auto-invocação
skills:                                        # Opcional: skills a incluir
  - other-skill-name
hooks:                                         # Opcional: hooks para eventos
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "echo 'Editing...'"
---
```

### Tabela de Campos

| Campo | Obrigatório | Padrão | Descrição |
|-------|-------------|--------|-----------|
| `name` | ✅ | - | Identificador único (lowercase, hífens) |
| `description` | ✅ | - | O que faz + quando usar (max 1024 chars) |
| `allowed-tools` | ❌ | Herda tudo | Lista de ferramentas permitidas |
| `model` | ❌ | Herda | Modelo preferido: `haiku`, `sonnet`, `opus` |
| `context` | ❌ | Compartilhado | `fork` para contexto isolado |
| `agent` | ❌ | `false` | Se executa como agente autônomo |
| `user-invocable` | ❌ | `false` | Se aparece no menu `/skill` |
| `disable-model-invocation` | ❌ | `false` | Impede invocação automática |
| `skills` | ❌ | Nenhum | Lista de skills a incluir |
| `hooks` | ❌ | Nenhum | Hooks para eventos da skill |

### name

**Regras**:

- ✅ Apenas lowercase, números, hífens
- ❌ Sem espaços, underscores, maiúsculas

**Exemplos**:

```yaml
name: pdf-processing        # ✅ Correto
name: api-testing           # ✅ Correto
name: PDF-Processing        # ❌ Maiúsculas
name: pdf_processing        # ❌ Underscore
```

### description

**Crítico para descoberta**: Deve conter:

1. **O que faz** (funcionalidade)
2. **Quando usar** (gatilhos/triggers)

**Exemplo ruim**:

```yaml
description: "Helps with documents"
```

**Exemplo bom**:

```yaml
description: "Extracts text and tables from PDFs, fills forms, merges documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction."
```

**Dicas**:

- Inclua termos-chave que usuários mencionariam
- Seja específico sobre capacidades
- Liste casos de uso comuns
- Use terceira pessoa: "Extracts..." não "Extract..."

### allowed-tools

Restringe ferramentas disponíveis. Pode ser lista ou string separada por vírgulas:

```yaml
# Formato lista (recomendado)
allowed-tools:
  - Read
  - Grep
  - Bash

# Formato string
allowed-tools: Read, Grep, Bash(python:*, node:*)
```

**Quando omitir** (herda todas):

- Skills exploratórias
- Protótipos
- Máxima flexibilidade

**Quando especificar** (restringir):

- Skills de revisão (apenas Read, Grep)
- Skills sensíveis (sem Write, sem Bash)
- Controle fino de operações

### model

Define modelo preferido para execução:

```yaml
model: haiku   # Rápido, econômico
model: sonnet  # Equilibrado (padrão)
model: opus    # Mais capaz
```

**Quando usar**:

- `haiku`: Tasks simples, validação, parsing
- `sonnet`: Maioria das tarefas
- `opus`: Raciocínio complexo, coding avançado

### user-invocable

Controla se a skill aparece no menu `/skill`:

```yaml
user-invocable: true   # Aparece em /skill menu
user-invocable: false  # Apenas invocação automática (padrão)
```

**Use `true` quando**:

- Usuário deve poder invocar manualmente
- Skill é um workflow autônomo
- Quer exposição no menu

### disable-model-invocation

Impede que Claude invoque a skill automaticamente:

```yaml
disable-model-invocation: true  # Só manual
disable-model-invocation: false # Auto + manual (padrão)
```

**Use `true` quando**:

- Skill só deve ser invocada explicitamente
- Evitar falsos positivos na detecção
- Controle total do usuário

---

## Context Fork

O campo `context: fork` permite executar a skill em um **contexto isolado**, sem acesso ao histórico da conversa atual.

### Comportamento Normal (sem fork)

```yaml
---
name: my-skill
description: "..."
# context não especificado = compartilha contexto
---
```

- Skill tem acesso ao histórico da conversa
- Pode referenciar mensagens anteriores
- Resultado é integrado ao contexto principal

### Com Context Fork

```yaml
---
name: isolated-analyzer
description: "Analyzes code independently"
context: fork
---
```

- Skill inicia com contexto limpo
- Não vê mensagens anteriores da conversa
- Execução completamente isolada
- Resultado retorna ao contexto principal

### Quando Usar Fork

**Use `context: fork` quando**:

- Análise não deve ser influenciada por contexto anterior
- Execução deve ser determinística
- Skill é auto-contida (não precisa de histórico)
- Quer evitar poluição de contexto

**Não use fork quando**:

- Skill precisa referenciar discussões anteriores
- Resultado depende de decisões prévias
- Workflow é iterativo com múltiplas invocações

### Exemplo Prático

```yaml
---
name: code-security-scanner
description: "Scans code for security vulnerabilities independently"
context: fork
allowed-tools:
  - Read
  - Grep
  - Glob
model: sonnet
---

# Security Scanner

Este scanner analisa código de forma independente, sem viés de
discussões anteriores sobre o código.

## Workflow
1. Receber caminho do arquivo/diretório
2. Escanear por vulnerabilidades conhecidas
3. Retornar relatório objetivo
```

---

## Hooks em Skills

Skills podem definir hooks que executam em resposta a eventos durante sua execução.

### Estrutura de Hooks

```yaml
---
name: skill-with-hooks
description: "..."
hooks:
  PreToolUse:
    - matcher: "Edit(*.py)"
      hooks:
        - type: command
          command: "python -m py_compile \"$TOOL_INPUT_FILE_PATH\""
  PostToolUse:
    - matcher: "Write(*.ts)"
      hooks:
        - type: command
          command: "npx prettier --write \"$TOOL_INPUT_FILE_PATH\""
---
```

### Eventos Disponíveis

| Evento | Quando Dispara | Variáveis |
|--------|----------------|-----------|
| `PreToolUse` | Antes de usar ferramenta | `$TOOL_NAME`, `$TOOL_INPUT_*` |
| `PostToolUse` | Após usar ferramenta | `$TOOL_NAME`, `$TOOL_INPUT_*`, `$TOOL_OUTPUT` |
| `Stop` | Quando skill termina | `$STOP_REASON` |

### Matchers

Matchers filtram quando hooks executam:

```yaml
# Qualquer Edit
matcher: "Edit"

# Edit em arquivos Python
matcher: "Edit(*.py)"

# Edit em diretório específico
matcher: "Edit(src/**/*.ts)"

# Múltiplas ferramentas
matcher: "Edit,Write"
```

### Exemplo: Auto-Format

```yaml
---
name: python-developer
description: "Develops Python code with auto-formatting"
hooks:
  PostToolUse:
    - matcher: "Edit(*.py),Write(*.py)"
      hooks:
        - type: command
          command: "black \"$TOOL_INPUT_FILE_PATH\" && isort \"$TOOL_INPUT_FILE_PATH\""
---
```

### Exemplo: Validação

```yaml
---
name: terraform-manager
description: "Manages Terraform configurations with validation"
hooks:
  PostToolUse:
    - matcher: "Edit(*.tf),Write(*.tf)"
      hooks:
        - type: command
          command: "terraform fmt -check \"$TOOL_INPUT_FILE_PATH\""
---
```

---

## Integração com Subagents

Skills podem incluir outras skills e integrar com subagents definidos em `.claude/agents/`.

### Campo skills

```yaml
---
name: full-stack-developer
description: "Full-stack development with frontend and backend skills"
skills:
  - frontend-developer
  - backend-developer
  - database-manager
---
```

Quando esta skill é ativada, as skills listadas também ficam disponíveis.

### Usando Agents com Skills

Agents em `.claude/agents/` podem referenciar skills:

```yaml
# .claude/agents/tech-lead.md
---
name: tech-lead
description: "Technical lead for architecture decisions"
skills:
  - system-design-decision-engine
  - code-reviewer
model: opus
---

Você é um tech lead experiente...
```

### Padrão: Skill Orquestradora

```yaml
---
name: project-setup
description: "Sets up new projects with all configurations"
skills:
  - git-initializer
  - docker-setup
  - ci-cd-config
  - documentation-generator
user-invocable: true
---

# Project Setup

Orquestra configuração completa de novos projetos.

## Workflow
1. Inicializar Git com `.gitignore` apropriado
2. Configurar Docker e docker-compose
3. Setup CI/CD (GitHub Actions)
4. Gerar documentação inicial
```

### Padrão: Skill com Agent Especializado

```markdown
---
name: api-development
description: "Develops REST APIs with best practices"
skills:
  - openapi-generator
  - api-testing
---

# API Development

## Quando usar agents especializados

Para revisão de segurança, use: `@security-reviewer`
Para otimização de performance, use: `@performance-optimizer`
```

---

## Padrões de Organização

### Padrão 1: Guia com Referências

**Use quando**: Instruções básicas inline, detalhes em arquivos separados

```markdown
---
name: word-processing
description: "Create and edit Word documents with formatting, tables, and charts."
---

# Word Processing Skill

## Quick Start
1. Specify document type (report, letter, memo)
2. Provide content and formatting requirements
3. Skill generates .docx file

## Basic Features
- Text formatting (bold, italic, fonts)
- Tables and lists
- Headers and footers
- Page numbering

## Advanced Features

For form creation, see `docs/FORMS.md`
For redlining and track changes, see `docs/REDLINING.md`
For OOXML manipulation, see `docs/OOXML.md`
```

**Benefício**: SKILL.md permanece < 500 linhas, detalhes sob demanda.

### Padrão 2: Organização por Domínio

**Use quando**: Skill cobre múltiplos domínios

```markdown
---
name: sales-reporting
description: "Generate sales reports with charts, KPIs, and analysis."
---

# Sales Reporting

## Workflow
1. Analyze data source type
2. Load domain-specific instructions:
   - **Financial reports**: see `docs/finance.md`
   - **Product analysis**: see `docs/product.md`
   - **Customer analytics**: see `docs/customer.md`
3. Generate report with appropriate metrics

## Standard Metrics
[lista de métricas comuns]

## Custom Analysis
For advanced analysis patterns, see `docs/advanced-analytics.md`
```

**Benefício**: Claude carrega apenas domínio relevante.

### Padrão 3: Detalhes Condicionais

**Use quando**: Recursos avançados são opcionais

```markdown
---
name: api-testing
description: "Test REST APIs with various authentication and validation methods."
---

# API Testing

## Basic Testing
1. Define endpoint URL
2. Specify HTTP method (GET, POST, PUT, DELETE)
3. Provide request body (if applicable)
4. Execute request
5. Validate response

## Advanced Scenarios

**Authentication**:
If user needs OAuth, JWT, or API key auth, see `docs/auth.md`

**Performance Testing**:
For load testing and benchmarking, see `docs/performance.md`

**Contract Testing**:
For API contract validation, see `docs/contracts.md`
```

**Benefício**: Funcionalidade básica acessível, avançado sob demanda.

### ⚠️ EVITE

**Referências profundamente aninhadas**:

```markdown
# ❌ NÃO FAÇA ISSO
See docs/main.md
  └── References docs/advanced.md
      └── References docs/deep-dive.md
```

**Limite**: 1 nível de profundidade de `SKILL.md`

---

## Workflows e Validação

### Checklists para Tarefas Complexas

```markdown
## API Integration Workflow

Copy this checklist and mark items as complete:

- [ ] 1. Review API documentation
- [ ] 2. Set up authentication
- [ ] 3. Test connectivity
- [ ] 4. Map endpoints to functions
- [ ] 5. Implement error handling
- [ ] 6. Write integration tests
- [ ] 7. Document usage
```

**Benefício**: Rastreamento de progresso visível.

### Loops de Validação

```markdown
## Validation Loop

1. Generate output file
2. Run validator:
   ```bash
   python scripts/validate.py output.json
   ```

3. If errors found:
   - Review error messages
   - Fix issues in output
   - Re-run validator
   - Repeat until validation passes
4. Proceed to next step

```

**Benefício**: Catch problemas antes de prosseguir.

### Plan → Validate → Execute

```markdown
## Execution Pattern

### Phase 1: Plan
Create structured plan file:
```json
{
  "steps": [
    {"action": "fetch_data", "params": {...}},
    {"action": "transform", "params": {...}},
    {"action": "output", "params": {...}}
  ]
}
```

### Phase 2: Validate

Run plan validator:

```bash
python scripts/validate_plan.py plan.json
```

### Phase 3: Execute

Only after validation passes:

```bash
python scripts/execute_plan.py plan.json
```

```

**Benefício**: Verificação antes de ações irreversíveis.

---

## Allowed Tools

### Omitir Tools (Recomendado)

```yaml
---
name: my-skill
description: "My skill description"
# Sem allowed-tools = herda TUDO
---
```

**Herda**:

- Todos os built-in tools (Read, Write, Edit, Bash, etc.)
- MCP tools de servers conectados
- Ferramentas futuras automaticamente

**Use quando**:

- Skill precisa de máxima flexibilidade
- Protótipos e exploração
- Não há restrições de segurança

### Especificar Tools (Restringir)

```yaml
---
name: code-reviewer
description: "Reviews code for quality and best practices"
allowed-tools: Read, Grep, Glob
---
```

**Apenas** leitura - sem Write, sem Bash.

**Use quando**:

- Skills de revisão (apenas leitura)
- Skills sensíveis à segurança
- Operações com escopo limitado

### Padrões Comuns

**Apenas leitura**:

```yaml
allowed-tools: Read, Grep, Glob
```

**Leitura + Bash limitado**:

```yaml
allowed-tools: Read, Grep, Bash(python:*, node:*)
```

**Full access**:

```yaml
# Omitir allowed-tools
```

---

## Built-in Skills (API)

**Skills pré-construídas** disponíveis via Anthropic API:

| Skill | ID | Descrição |
|-------|----|----|
| **PowerPoint** | `pptx` | Criar apresentações com slides, gráficos, transições |
| **Excel** | `xlsx` | Criar workbooks com fórmulas, gráficos, formatação |
| **Word** | `docx` | Gerar documentos Word com formatação rica |
| **PDF** | `pdf` | Criar PDFs formatados com texto, tabelas, imagens |

### Usando Built-in Skills

**Nota**: Built-in skills **NÃO** funcionam no Claude Code - apenas via API.

```python
import anthropic

client = anthropic.Anthropic()

# Listar skills disponíveis
skills = client.beta.skills.list(
    source="anthropic",
    betas=["skills-2025-10-02"]
)

# Usar skill
response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=[
        "code-execution-2025-08-25",
        "skills-2025-10-02",
        "files-api-2025-04-14"
    ],
    container={
        "skills": [
            {"type": "anthropic", "skill_id": "pptx", "version": "latest"}
        ]
    },
    messages=[
        {
            "role": "user",
            "content": "Create a 5-slide presentation about renewable energy"
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
)

# Extrair file_id
file_id = None
for block in response.content:
    if block.type == 'tool_use' and block.name == 'code_execution':
        for result_block in block.content:
            if hasattr(result_block, 'file_id'):
                file_id = result_block.file_id

# Download via Files API
if file_id:
    file_content = client.beta.files.download(file_id=file_id)
    with open("output.pptx", "wb") as f:
        f.write(file_content)
```

### Limitações

- ✅ Máximo **8 skills** por request
- ✅ Requires beta headers
- ✅ Apenas via API (não Claude Code)

---

## Custom Skills (Upload)

### Upload via API

```python
import anthropic

client = anthropic.Anthropic()

# Upload custom skill
skill = client.beta.skills.create(
    directory="/path/to/my-skill/",  # Diretório contendo SKILL.md
    betas=["skills-2025-10-02"]
)

print(f"Skill ID: {skill.id}")
print(f"Version: {skill.version}")

# Usar skill customizada
response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=[
        "code-execution-2025-08-25",
        "skills-2025-10-02"
    ],
    container={
        "skills": [
            {"type": "custom", "skill_id": skill.id, "version": "latest"}
        ]
    },
    messages=[
        {"role": "user", "content": "Process this data..."}
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
)
```

### Limitações

- ✅ Máximo **8MB** total (diretório comprimido)
- ✅ Requer `SKILL.md` com frontmatter válido
- ✅ Versioning automático (epoch timestamps)

### Versioning

**Custom skills**: Auto-generated timestamps

- Use `"latest"` durante desenvolvimento
- Pin versão específica para produção

**Anthropic skills**: Date-based (ex: `20251013`)

- Use `"latest"` para sempre usar mais recente

---

## Exemplos Práticos

### 1. PDF Form Filler

```markdown
---
name: pdf-form-filler
description: "Fill PDF forms with structured data. Use when user provides PDF form and data to populate."
allowed-tools: Bash(python:*)
---

# PDF Form Filler

## Mission
Automate PDF form filling with provided data.

## Workflow
1. Validate PDF file exists
2. Extract form field names: `python scripts/list_fields.py <pdf>`
3. Map user data to fields
4. Fill form: `python scripts/fill_form.py <pdf> <data.json>`
5. Output filled PDF

## Data Format
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

## Edge Cases

- Password-protected PDFs → request password
- Missing required fields → warn user
- Invalid data types → validate before filling

```

**Estrutura**:
```

.claude/skills/pdf-form-filler/
├── SKILL.md
└── scripts/
    ├── list_fields.py
    └── fill_form.py

```

### 2. API Contract Tester

```markdown
---
name: api-contract-tester
description: "Validate API responses against OpenAPI/Swagger contracts. Use when testing API compliance or validating endpoints."
allowed-tools: Bash(python:*, curl:*)
---

# API Contract Tester

## Mission
Validate API responses match defined contracts.

## Workflow
1. Load OpenAPI spec
2. Extract endpoint definitions
3. Execute API calls
4. Compare responses with schema
5. Report violations

## Usage

Test single endpoint:
```bash
python scripts/test_endpoint.py --spec openapi.yaml --endpoint /api/users
```

Test all endpoints:

```bash
python scripts/test_all.py --spec openapi.yaml
```

## Output

```json
{
  "endpoint": "/api/users",
  "method": "GET",
  "status": "PASS",
  "violations": []
}
```

## Advanced

For authentication setup, see `docs/auth.md`
For performance benchmarking, see `docs/performance.md`

```

### 3. Code Documentation Generator

```markdown
---
name: code-documenter
description: "Generate comprehensive code documentation from source files. Use when user needs API docs, function references, or code explanations."
allowed-tools: Read, Bash(python:*, node:*)
---

# Code Documentation Generator

## Mission
Extract and document code structure and APIs.

## Workflow
1. Analyze source code language
2. Extract:
   - Functions/methods
   - Classes/interfaces
   - Parameters and return types
   - Dependencies
3. Generate formatted documentation
4. Output as Markdown or HTML

## Supported Languages
- Python (docstrings)
- JavaScript/TypeScript (JSDoc)
- C# (XML comments)
- Java (Javadoc)

## Templates

For API reference format, see `templates/api-reference.md`
For usage guide format, see `templates/usage-guide.md`
```

---

## Troubleshooting

### Skill não ativa

**Problema**: Claude não usa a skill quando esperado

**Soluções**:

- ✅ Verificar `description` contém triggers claros
  - Incluir termos que usuários mencionariam
  - Especificar "Use when..."
- ✅ Verificar sintaxe YAML (sem tabs)
- ✅ Verificar caminho: `.claude/skills/skill-name/SKILL.md`
- ✅ Testar com `claude --debug`

**Exemplo de description ruim**:

```yaml
description: "Helps with documents"  # ❌ Vago
```

**Exemplo de description boa**:

```yaml
description: "Extracts text and tables from PDFs, fills forms, merges documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction."  # ✅ Específico
```

### Skill ativa quando não deveria

**Problema**: Skill ativa em contextos incorretos

**Soluções**:

- ✅ Refinar `description` com termos mais específicos
- ✅ Adicionar "Use when..." condicional
- ✅ Verificar conflitos com outras skills
- ✅ Usar nomes únicos e descritivos

### Scripts não executam

**Problema**: Scripts em `scripts/` não rodam

**Soluções**:

- ✅ Verificar `allowed-tools: Bash(...)`
- ✅ Verificar permissões: `chmod +x scripts/*.py`
- ✅ Caminhos relativos a `SKILL.md`:

  ```bash
  python scripts/process.py  # ✅ Correto
  python ./scripts/process.py  # ✅ Também ok
  python /absolute/path/process.py  # ⚠️ Evitar
  ```

- ✅ Verificar dependências Python instaladas

### Progressive disclosure não funciona

**Problema**: Arquivos de docs não carregam

**Soluções**:

- ✅ Verificar caminhos relativos ao `SKILL.md`
- ✅ Evitar referências aninhadas (> 1 nível)
- ✅ Usar `cat docs/file.md` explicitamente
- ✅ Mencionar arquivo em SKILL.md: "For details, see `docs/reference.md`"

**Exemplo correto**:

```markdown
For advanced usage, see `docs/advanced.md`

To view: `cat docs/advanced.md`
```

### SKILL.md muito longo

**Problema**: SKILL.md > 500 linhas

**Soluções**:

- ✅ Mover detalhes para `docs/`
- ✅ Usar progressive disclosure patterns
- ✅ Extrair exemplos para `docs/examples.md`
- ✅ Mover referências para `docs/reference.md`

---

## Best Practices

### ✅ DO

- **Keep SKILL.md < 500 lines**: Use progressive disclosure
- **Specific descriptions**: Include functionality + triggers
- **Handle errors in scripts**: Don't punt to Claude
- **Provide utility scripts**: More reliable than generated code
- **Use checklists**: Track complex workflows
- **Validation loops**: Catch errors early
- **Consistent terminology**: One term throughout
- **Test with multiple models**: Haiku, Sonnet, Opus

### ❌ DON'T

- **Offer excessive options**: Provide defaults with escape hatches
- **Use "voodoo constants"**: Justify all configuration values
- **Assume tools installed**: Show explicit installation
- **Deep nesting**: Keep references 1 level from SKILL.md
- **Time-sensitive info**: Use "Old Patterns" for deprecations
- **Windows paths**: Use forward slashes `/` not `\`
- **Vague descriptions**: Be specific about capabilities

---

## Content Guidelines

### Avoid Time-Sensitive Information

```markdown
# ❌ DON'T
As of 2024, the recommended approach is...

# ✅ DO
## Current Approach
[describe approach]

## Old Patterns (Deprecated)
[legacy approaches for reference]
```

### Maintain Consistent Terminology

```markdown
# ❌ DON'T (mixing terms)
Use the API endpoint...
Call the URL...
Hit the path...

# ✅ DO (consistent)
Use the API endpoint...
Call the endpoint...
Query the endpoint...
```

### Justify Configuration Values

```markdown
# ❌ DON'T (magic number)
Set timeout to 30

# ✅ DO (justified)
Set timeout to 30 seconds
- Network latency: ~5s
- Processing time: ~20s
- Buffer: ~5s
```

---

## Recursos

**Documentação Oficial**:

- [Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Agent Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Skills API Guide](https://docs.claude.com/en/api/skills-guide)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)

**Guides**:

- [Quick Reference](../quick-reference.md) - Comparação com Commands e Agents
- [Best Practices](../best-practices.md) - Práticas gerais

**Exemplos no Repositório**:

- `.claude/skills/` - Skills do projeto

---

**Última Revisão**: 2026-01-11 por Claude Code
