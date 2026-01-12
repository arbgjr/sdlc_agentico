# Agents (Sub-Agents): Guia Completo

**Versão**: 2.0
**Última Atualização**: 2026-01-11
**Referência oficial**: https://code.claude.com/docs/en/sub-agents

---

## 📋 Índice

1. [O Que São?](#o-que-são)
2. [Criando Agents](#criando-agents)
3. [Frontmatter Completo](#frontmatter-completo)
4. [XML-Style Examples](#xml-style-examples)
5. [Tool Configuration](#tool-configuration)
6. [Model Selection](#model-selection)
7. [Skills Integration](#skills-integration)
8. [Integration Patterns](#integration-patterns)
9. [Output Format](#output-format)
10. [Testing Agents](#testing-agents)
11. [Best Practices](#best-practices)
12. [Exemplos Práticos](#exemplos-práticos)
13. [Troubleshooting](#troubleshooting)

---

## O Que São?

Agents (ou sub-agents) são **especialistas focados** que Claude invoca para tarefas específicas. São mais sofisticados que skills, com capacidade de delegar para outros agents.

**Características:**

- ✅ Ativação automática (via description patterns) ou manual (`@agent-name`)
- ✅ Um arquivo `.md` = um agent
- ✅ XML-style examples para treinar invocação
- ✅ Podem delegar para outros agents
- ✅ Output estruturado para coordenação

**Quando usar:**

- Precisa de especialista focado em domínio
- Agent deve delegar para outros especialistas
- Workflow complexo com múltiplas etapas
- Output estruturado para outros agents

---

## Criando Agents

### Estrutura de Armazenamento

```bash
# Agents de projeto (compartilhados via Git)
.claude/agents/
├── backend-developer.md
├── frontend-developer.md
├── code-reviewer.md
└── performance-optimizer.md

# Agents pessoais (apenas você)
~/.claude/agents/
├── my-reviewer.md
└── personal-helper.md
```

**Precedência**: Projeto > Pessoal

### Template Básico

```yaml
---
name: your-agent-name
description: |
  Expert in [domain]. Use when [conditions].

  Examples:
  - <example>
    Context: When this agent should be used
    user: "Example user request"
    assistant: "I'll use @your-agent-name to..."
    <commentary>
    Why this agent was selected
    </commentary>
  </example>
allowed-tools:                    # Opcional - herda todos se omitido
  - Read
  - Write
  - Edit
  - Bash
model: sonnet                     # Opcional: haiku, sonnet, opus
skills:                           # Opcional: skills a incluir
  - skill-name
---

You are an expert [role] specializing in [domain].

## Core Expertise
- [Specific skill 1]
- [Specific skill 2]
- [Specific skill 3]

## Task Approach
1. [How you analyze the problem]
2. [Your methodology]
3. [How you validate solutions]

## Return Format

Provide clear, structured output that other agents can understand:

```markdown
## Task: [Description]

### Completed Actions
- [Action 1]
- [Action 2]

### Results
[Structured results]

### Next Steps
1. [Suggested next action]
2. [Follow-up task]
```

```

---

## XML-Style Examples

Claude aprende **quando invocar** agents através de exemplos XML na `description`.

### Por Que Funciona

1. **Pattern Learning**: Claude aprende padrões de invocação
2. **Context Awareness**: Entende estágio do projeto e intenção
3. **Smart Delegation**: Sabe quando delegar para outros
4. **Self-Documenting**: Exemplos servem como documentação viva

### Estrutura de Example

```yaml
description: |
  Brief description of expertise.

  Examples:
  - <example>
    Context: Describe when this applies
    user: "User request example"
    assistant: "How Claude should respond and invoke agent"
    <commentary>
    Explain WHY this agent was selected
    </commentary>
  </example>
```

### Exemplo Completo

```yaml
---
name: backend-developer
description: |
  Expert backend developer specializing in APIs, databases, and security.

  Examples:
  - <example>
    Context: User needs to build an API
    user: "Create a REST API for products with CRUD operations"
    assistant: "I'll use @backend-developer to build a comprehensive products API with proper validation and error handling"
    <commentary>
    API development is a core backend task requiring database design, business logic, and security considerations
    </commentary>
  </example>
  - <example>
    Context: User has completed backend and needs frontend
    user: "Now I need a UI for this API"
    assistant: "The backend is complete. Let me hand this off to @frontend-developer to build the user interface"
    <commentary>
    Recognizing when to delegate to frontend specialist rather than attempting UI work
    </commentary>
  </example>
  - <example>
    Context: User reports API performance issues
    user: "The /users endpoint is slow with large datasets"
    assistant: "I'll use @backend-developer to analyze and optimize the endpoint's database queries and implement pagination"
    <commentary>
    Performance optimization of backend endpoints requires database expertise
    </commentary>
  </example>
---

You are an expert backend developer specializing in building robust, scalable APIs.

## Core Expertise
- RESTful API design and implementation
- Database schema design and optimization
- Authentication and authorization (JWT, OAuth)
- Error handling and validation
- API documentation (OpenAPI/Swagger)
- Performance optimization

## Task Approach
1. **Understand requirements**: Clarify business logic and constraints
2. **Design first**: Plan schema, endpoints, and data flow
3. **Implement incrementally**: Build with tests
4. **Document thoroughly**: Code comments and API docs
5. **Optimize**: Profile and improve performance

## Return Format

```markdown
## API Implementation: [Feature Name]

### Endpoints Created
- `POST /api/products` - Create product
- `GET /api/products` - List products
- `GET /api/products/:id` - Get product details
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product

### Database Schema
```sql
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Tests Written

- Unit tests for business logic
- Integration tests for endpoints
- Validation tests for input

### Next Steps

1. Frontend team can start UI development
2. Consider adding search/filtering endpoints
3. Document in OpenAPI spec

```
```

### Multiple Examples Pattern

Inclua 2-3 exemplos cobrindo:

1. **Happy path**: Caso de uso primário
2. **Delegation**: Quando passar para outro agent
3. **Edge case**: Cenário menos comum mas importante

**Exemplo**:

```yaml
Examples:
- <example>
  Context: Primary use case
  user: "Build feature X"
  assistant: "I'll use @agent-name..."
  </example>
- <example>
  Context: When to delegate
  user: "Now add UI for feature X"
  assistant: "Feature X complete. Delegating to @frontend-agent..."
  </example>
- <example>
  Context: Edge case
  user: "Optimize feature X"
  assistant: "I'll use @agent-name to refactor and optimize..."
  </example>
```

---

## Tool Configuration

### Omitir allowed-tools (Recomendado)

```yaml
---
name: my-agent
description: "My agent description..."
# Sem allowed-tools = herda TUDO
---
```

**Herda**:

- Todos os built-in tools (Read, Write, Edit, Bash, Grep, Glob, etc.)
- MCP tools de servers conectados
- Ferramentas futuras automaticamente

**Benefícios**:

- ✅ Máxima flexibilidade
- ✅ Novos tools automaticamente disponíveis
- ✅ Acesso a MCP servers

**Use quando**:

- Agent precisa de capacidades completas
- Protótipos e exploração
- Não há restrições de segurança

### Especificar allowed-tools (Restringir)

```yaml
---
name: code-reviewer
description: "Reviews code without making changes..."
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---
```

**Apenas** ferramentas de leitura - sem Write, sem Edit.

**Use quando**:

- Agents de revisão (apenas leitura)
- Agents sensíveis à segurança
- Agents com escopo limitado

### Best Practices

1. **Most agents should omit allowed-tools** - Máxima flexibilidade
2. **Security-sensitive agents** - Lista explícita (ex: reviewers = read-only)
3. **Future-proof** - Omitir allowed-tools = novos tools automaticamente disponíveis

---

## Model Selection

O campo `model` define qual modelo Claude executa o agent.

### Opções Disponíveis

```yaml
model: haiku   # Rápido, econômico
model: sonnet  # Equilibrado (padrão)
model: opus    # Mais capaz
```

### Quando Usar Cada Modelo

| Modelo | Quando Usar | Exemplos |
|--------|-------------|----------|
| `haiku` | Tasks simples, validação, parsing | Linter, formatter, validator |
| `sonnet` | Maioria das tarefas (padrão) | Developer, reviewer, tester |
| `opus` | Raciocínio complexo, arquitetura | Architect, tech lead, security expert |

### Exemplo

```yaml
---
name: requirements-interrogator
description: "Elimina ambiguidade de requisitos..."
allowed-tools:
  - Read
  - Grep
model: haiku   # Task simples, não precisa de modelo pesado
---
```

```yaml
---
name: system-architect
description: "Designs complex system architectures..."
allowed-tools:
  - Read
  - Grep
  - Glob
model: opus    # Requer raciocínio complexo
---
```

---

## Skills Integration

Agents podem referenciar skills através do campo `skills`.

### Sintaxe

```yaml
---
name: my-agent
description: "..."
skills:
  - skill-name-1
  - skill-name-2
---
```

### Comportamento

Quando um agent é invocado:
1. Skills listadas são carregadas automaticamente
2. Agent tem acesso às instruções e recursos das skills
3. Scripts e templates das skills ficam disponíveis

### Exemplo Prático

```yaml
---
name: tech-lead
description: |
  Technical lead for architecture decisions and code quality.

  Examples:
  - <example>
    Context: Architecture decision needed
    user: "How should we handle high concurrency?"
    assistant: "I'll use @tech-lead to analyze patterns and make a decision"
  </example>
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
model: opus
skills:
  - system-design-decision-engine
  - code-reviewer
---

Você é um tech lead experiente...
```

### Padrões de Uso

**Agent especialista com skills de suporte**:

```yaml
skills:
  - api-testing        # Para validar endpoints
  - documentation      # Para gerar docs
```

**Agent orquestrador com múltiplas skills**:

```yaml
skills:
  - frontend-patterns
  - backend-patterns
  - database-patterns
  - deployment-patterns
```

---

## Integration Patterns

Agents trabalham juntos via coordenação do main Claude agent.

### Backend → Frontend Flow

```
@backend-developer → API Complete →
@frontend-developer → UI Built →
@code-reviewer → Approved →
Deploy
```

**Coordenação**:

1. Backend agent cria API e retorna endpoints
2. Frontend agent recebe endpoints e cria UI
3. Code reviewer valida ambos
4. Deploy se aprovado

### Full Stack Development

```
@tech-lead-orchestrator →
  @backend-developer (parallel) + @frontend-developer (parallel) →
  Integration Testing →
  @performance-optimizer →
  Deploy
```

**Coordenação**:

1. Tech lead planeja arquitetura
2. Backend e frontend trabalham em paralelo
3. Integration após conclusão
4. Performance optimization
5. Deploy

### Review Pipeline

```
@backend-developer → Code Complete →
@code-reviewer → Issues Found →
@backend-developer → Fixes Applied →
@code-reviewer → Approved →
@performance-optimizer → Optimized →
Deploy
```

**Coordenação**:

1. Developer implementa feature
2. Reviewer encontra issues
3. Developer corrige
4. Reviewer aprova
5. Optimizer melhora performance
6. Deploy

### Delegation Example

**Frontend agent delegando**:

```markdown
## UI Implementation Complete

### Components Created
- ProductList.tsx
- ProductDetail.tsx
- ProductForm.tsx

### API Integration
Using endpoints from @backend-developer:
- GET /api/products → ProductList
- POST /api/products → ProductForm

### Issues Found
API doesn't support pagination for large product lists.

### Next Steps
**Delegating to @backend-developer**:
- Add pagination to GET /api/products endpoint
- Support `?page=1&limit=20` query params
- Return total count in response

After pagination is added, I'll update ProductList to support it.
```

---

## Output Format

Agents devem retornar **resultados estruturados** para outros agents.

### Standard Output Template

```markdown
## Task: [Description]

### Completed Actions
- [Action 1 with details]
- [Action 2 with details]
- [Action 3 with details]

### Results

[Structured results - code, JSON, lists, etc.]

### Files Modified
- `src/api/products.py` - Added CRUD endpoints
- `tests/test_products.py` - Added integration tests
- `docs/api.md` - Documented new endpoints

### Tests Status
- ✅ Unit tests: 15/15 passed
- ✅ Integration tests: 8/8 passed
- ✅ Coverage: 94%

### Next Steps
1. [Immediate follow-up action]
2. [Suggested improvement]
3. [Potential delegation]

### Context for Next Agent
- [Key information for next agent]
- [Dependencies to be aware of]
- [Decisions made and rationale]
```

### JSON Output (When Appropriate)

```markdown
### Results

```json
{
  "feature": "Product API",
  "endpoints": [
    {"method": "POST", "path": "/api/products", "status": "implemented"},
    {"method": "GET", "path": "/api/products", "status": "implemented"},
    {"method": "GET", "path": "/api/products/:id", "status": "implemented"}
  ],
  "files_modified": ["src/api/products.py", "tests/test_products.py"],
  "tests_passed": true,
  "coverage": 94,
  "ready_for_review": true
}
```

```

### Code Output

```markdown
### Implementation

**File**: `src/api/products.py`

```python
from fastapi import APIRouter, HTTPException
from models import Product
from database import get_db

router = APIRouter()

@router.get("/api/products")
async def list_products(limit: int = 20, offset: int = 0):
    """List products with pagination"""
    db = get_db()
    products = db.query(Product).limit(limit).offset(offset).all()
    total = db.query(Product).count()
    return {"products": products, "total": total}
```

```

---

## Testing Agents

### 1. Invocation Test

**Objetivo**: Agent é invocado corretamente?

```

user: "Build a REST API for users"

```

**Verificar**:
- ✅ @backend-developer foi invocado
- ✅ Não invocou agent incorreto
- ✅ Reconheceu contexto corretamente

### 2. Output Test

**Objetivo**: Saída é estruturada e útil?

```markdown
Verificar output contém:
- ✅ Seção "Completed Actions"
- ✅ Seção "Results" com detalhes
- ✅ Seção "Next Steps"
- ✅ Informação suficiente para próximo agent
```

### 3. Quality Test

**Objetivo**: Solução é de nível expert?

```markdown
Verificar:
- ✅ Segue melhores práticas
- ✅ Código limpo e bem estruturado
- ✅ Testes incluídos
- ✅ Documentação adequada
- ✅ Considera edge cases
```

### 4. Delegation Test

**Objetivo**: Agent delega corretamente?

```
user: "API is built, now create UI"
```

**Verificar**:

- ✅ Backend agent reconhece fim do seu escopo
- ✅ Delega para @frontend-developer
- ✅ Passa contexto necessário (endpoints, schemas)

### Test Checklist

```markdown
- [ ] Agent invocado no contexto correto
- [ ] Agent NÃO invocado em contexto incorreto
- [ ] Output estruturado e completo
- [ ] Solução segue melhores práticas
- [ ] Testes incluídos quando aplicável
- [ ] Documentação clara
- [ ] Delega apropriadamente
- [ ] Passa contexto para próximo agent
```

---

## Frontmatter Completo

```yaml
---
name: unique-agent-name                # Obrigatório: lowercase & hyphens
description: |                         # Obrigatório: descrição + exemplos XML
  Expert in X. Use when Y.

  Examples:
  - <example>
    Context: When to use
    user: "User request"
    assistant: "How to invoke"
    <commentary>
    Why this agent
    </commentary>
  </example>
allowed-tools:                         # Opcional: omitir = herda todos
  - Read
  - Grep
  - Glob
model: sonnet                          # Opcional: haiku, sonnet, opus
skills:                                # Opcional: skills a incluir
  - skill-name-1
  - skill-name-2
---
```

### Tabela de Campos

| Campo | Obrigatório | Padrão | Descrição |
|-------|-------------|--------|-----------|
| `name` | ✅ | - | Identificador único (lowercase, hífens) |
| `description` | ✅ | - | Descrição + XML examples |
| `allowed-tools` | ❌ | Herda tudo | Lista de ferramentas permitidas |
| `model` | ❌ | Herda | Modelo preferido: `haiku`, `sonnet`, `opus` |
| `skills` | ❌ | Nenhum | Lista de skills a incluir |

### Campos Detalhados

**`name`** (obrigatório):

- Lowercase com hífens
- Descritivo e único
- Sem espaços ou underscores

**`description`** (obrigatório):

- Primeira linha: breve descrição da expertise
- Linhas seguintes: XML examples
- Incluir 2-3 exemplos cobrindo cenários diferentes

**`allowed-tools`** (opcional):

- Omitir para máxima flexibilidade
- Especificar para restringir acesso
- Ver [Tool Configuration](#tool-configuration)

**`model`** (opcional):

- `haiku`: Rápido, econômico - para tasks simples
- `sonnet`: Equilibrado (padrão) - maioria das tasks
- `opus`: Mais capaz - raciocínio complexo

**`skills`** (opcional):

- Lista de skills disponíveis para o agent
- Skills são carregadas quando agent é invocado
- Ver [Skills Integration](#skills-integration)

---

## Best Practices

### ✅ DO

**1. Focused Expertise**

- ✅ Um domínio de maestria por agent
- ✅ Limites claros de responsabilidade
- ✅ Casos de uso específicos e bem definidos

**2. Smart Examples**

- ✅ 2-3 exemplos cobrindo cenários diferentes
- ✅ Incluir edge cases e delegation
- ✅ Mostrar quando **NÃO** usar o agent
- ✅ Commentary explica raciocínio

**3. Clear Output**

- ✅ Resultados estruturados (template padrão)
- ✅ Identificar próximos passos claramente
- ✅ Incluir contexto relevante para próximo agent
- ✅ Listar files modificados

**4. Professional Quality**

- ✅ Seguir melhores práticas do domínio
- ✅ Incluir testes quando aplicável
- ✅ Documentar decisões e trade-offs
- ✅ Considerar edge cases e erros

**5. Iteration Workflow**

```bash
/agents              # Editor interativo
e                    # Abrir no editor externo
git add .claude/agents/*
git commit -m "feat(agents): add backend-developer agent"
```

### ❌ DON'T

**1. Avoid Scope Creep**

- ❌ Agent tentando fazer tudo
- ❌ Responsabilidades mal definidas
- ❌ Overlapping com outros agents

**2. Poor Communication**

- ❌ Output não estruturado
- ❌ Sem next steps
- ❌ Não passa contexto para próximo agent

**3. Low Quality**

- ❌ Código sem testes
- ❌ Ignora melhores práticas
- ❌ Não considera edge cases
- ❌ Documentação inadequada

**4. Wrong Tool Choice**

- ❌ Restringir tools desnecessariamente
- ❌ Dar acesso demais a agents de revisão
- ❌ Não aproveitar MCP tools

---

## Exemplos Práticos

### 1. Backend Developer

```yaml
---
name: backend-developer
description: |
  Expert backend developer specializing in APIs, databases, and server-side logic.

  Examples:
  - <example>
    Context: Building new API endpoint
    user: "Create API for user authentication"
    assistant: "I'll use @backend-developer to implement secure authentication with JWT tokens and password hashing"
    <commentary>
    Authentication requires backend expertise in security, database design, and API implementation
    </commentary>
  </example>
  - <example>
    Context: Completed backend, needs frontend
    user: "Add a login form UI"
    assistant: "Authentication API is ready. Delegating to @frontend-developer for the login form"
    <commentary>
    Backend complete, frontend specialist should handle UI
    </commentary>
  </example>
---

You are an expert backend developer specializing in building robust, scalable server-side applications.

## Core Expertise
- RESTful API design and implementation
- Database schema design and optimization (SQL and NoSQL)
- Authentication and authorization (JWT, OAuth2, API keys)
- Business logic and data validation
- Error handling and logging
- API documentation (OpenAPI/Swagger)
- Performance optimization and caching
- Security best practices (OWASP Top 10)

## Task Approach
1. **Understand requirements**: Clarify business logic, constraints, and scale requirements
2. **Design first**: Plan database schema, API endpoints, and data flow
3. **Implement incrementally**: Build with tests, one feature at a time
4. **Security always**: Validate inputs, sanitize outputs, use parameterized queries
5. **Document thoroughly**: Code comments, API docs, and usage examples
6. **Optimize**: Profile performance and optimize bottlenecks

## Return Format

```markdown
## API Implementation: [Feature Name]

### Endpoints Created
- `POST /api/resource` - Create resource
- `GET /api/resource` - List resources
- `GET /api/resource/:id` - Get resource details

### Database Schema
[SQL or schema definition]

### Files Modified
- `src/api/resource.py`
- `tests/test_resource.py`
- `docs/api.md`

### Security Considerations
- Input validation implemented
- SQL injection prevention via parameterized queries
- Authentication required for all endpoints

### Tests Status
- ✅ Unit tests: X/X passed
- ✅ Integration tests: X/X passed
- ✅ Coverage: X%

### Next Steps
1. [Immediate action]
2. [Suggested improvement]
```

```

### 2. Frontend Developer

```yaml
---
name: frontend-developer
description: |
  Expert frontend developer specializing in React, UI/UX, and client-side applications.

  Examples:
  - <example>
    Context: Building UI for existing API
    user: "Create a product listing page"
    assistant: "I'll use @frontend-developer to build a responsive product listing with filtering and pagination"
    <commentary>
    UI development requires frontend expertise in React, state management, and responsive design
    </commentary>
  </example>
  - <example>
    Context: API doesn't exist yet
    user: "Build a dashboard for analytics"
    assistant: "First, I'll use @backend-developer to create analytics API endpoints, then @frontend-developer will build the dashboard UI"
    <commentary>
    Need backend API first before building frontend
    </commentary>
  </example>
---

You are an expert frontend developer specializing in building modern, responsive user interfaces.

## Core Expertise
- React and TypeScript
- State management (Redux, Zustand, Context)
- Component architecture and design patterns
- Responsive design and CSS (Tailwind, CSS Modules)
- API integration and data fetching
- Form validation and error handling
- Accessibility (WCAG compliance)
- Performance optimization (lazy loading, code splitting)

## Task Approach
1. **Understand requirements**: Clarify user flows, design requirements, and API contracts
2. **Component design**: Plan component hierarchy and state management
3. **Implement incrementally**: Build components with tests
4. **Accessibility first**: Semantic HTML, ARIA labels, keyboard navigation
5. **Responsive always**: Mobile-first approach, test on multiple devices
6. **Optimize performance**: Code splitting, lazy loading, memoization

## Return Format

```markdown
## UI Implementation: [Feature Name]

### Components Created
- `ComponentName.tsx` - Description
- `ComponentName.test.tsx` - Tests

### API Integration
Using endpoints:
- `GET /api/resource` → ComponentName

### State Management
[Describe state approach]

### Accessibility
- ✅ Semantic HTML
- ✅ ARIA labels
- ✅ Keyboard navigation

### Tests Status
- ✅ Component tests: X/X passed
- ✅ Integration tests: X/X passed

### Next Steps
1. [Immediate action]
2. [Suggested improvement]
```

```

### 3. Code Reviewer

```yaml
---
name: code-reviewer
description: |
  Expert code reviewer specializing in quality, security, and best practices.

  Examples:
  - <example>
    Context: Code implementation complete
    user: "Review the authentication implementation"
    assistant: "I'll use @code-reviewer to analyze security, code quality, and best practices compliance"
    <commentary>
    Code review requires expertise in security, testing, and code quality standards
    </commentary>
  </example>
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

You are an expert code reviewer focusing on quality, security, and maintainability.

## Core Expertise
- Code quality and best practices
- Security vulnerabilities (OWASP Top 10)
- Test coverage and quality
- Performance issues
- Maintainability and readability
- Documentation completeness

## Review Checklist
- [ ] Security vulnerabilities (SQL injection, XSS, etc.)
- [ ] Input validation and error handling
- [ ] Code quality and readability
- [ ] Test coverage (minimum 80%)
- [ ] Documentation (code comments, API docs)
- [ ] Performance considerations
- [ ] Best practices compliance

## Return Format

```markdown
## Code Review: [Feature Name]

### Security Issues
- ❌ [Critical issue with details]
- ⚠️ [Warning with recommendation]
- ✅ [Approved aspect]

### Code Quality
- [Issue or approval with details]

### Tests
- Coverage: X%
- [Test quality assessment]

### Recommendations
1. [Priority 1 fix]
2. [Priority 2 improvement]

### Overall Assessment
[APPROVED / NEEDS CHANGES / BLOCKED]

### Next Steps
If NEEDS CHANGES: Delegate back to @[original-agent] with fixes
If APPROVED: Ready for deployment
```

```

---

## Troubleshooting

### Agent não é invocado

**Problema**: Claude não usa o agent quando esperado

**Soluções**:
- ✅ Verificar XML examples na `description`
- ✅ Examples devem cobrir o caso de uso
- ✅ Testar invocação manual: `@agent-name`
- ✅ Verificar nome (lowercase, hífens)
- ✅ Usar `claude --debug` para ver decisões

**Exemplo de description ruim**:
```yaml
description: "Backend developer"  # ❌ Sem examples
```

**Exemplo de description boa**:

```yaml
description: |
  Expert backend developer...

  Examples:
  - <example>...  # ✅ Com examples
```

### Agent invoca mas output ruim

**Problema**: Agent funciona mas resultados são pobres

**Soluções**:

- ✅ Revisar system prompt (corpo do arquivo)
- ✅ Adicionar exemplos de output esperado
- ✅ Refinar "Core Expertise" section
- ✅ Melhorar "Task Approach" workflow
- ✅ Fornecer template de output mais específico

### Tools não disponíveis

**Problema**: Agent não consegue usar ferramentas

**Soluções**:

- ✅ Verificar `allowed-tools` field (omitir para herdar todos)
- ✅ Verificar MCP servers conectados
- ✅ Testar com `claude --debug`
- ✅ Verificar se tool está disponível no contexto

### Delegation não funciona

**Problema**: Agent não delega para outros

**Soluções**:

- ✅ Adicionar example de delegation na description
- ✅ Mencionar outros agents no system prompt
- ✅ Treinar com scenarios de delegation
- ✅ Return format deve sugerir next agent

**Exemplo**:

```markdown
### Next Steps
Delegating to @frontend-developer:
- Build UI for these endpoints
- Use authentication flow implemented here
```

---

## Recursos

**Documentação Oficial**:

- [Claude Code Docs](https://code.claude.com/docs)

**Exemplos no Repositório**:

- `.claude/agents/` - Agents do projeto (se existir)

---

**Última Revisão**: 2026-01-11 por Claude Code
