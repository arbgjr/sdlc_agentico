# Output Styles: Guia Completo

**Versão**: 2.0
**Última Atualização**: 2026-01-11
**Referência oficial**: https://code.claude.com/docs/en/output-styles

---

## 📋 Índice

1. [O Que São?](#o-que-são)
2. [Como Funcionam](#como-funcionam)
3. [Built-in Styles](#built-in-styles)
4. [Usando Output Styles](#usando-output-styles)
5. [Custom Output Styles](#custom-output-styles)
6. [Frontmatter](#frontmatter)
7. [Comparações](#comparações)
8. [Casos de Uso](#casos-de-uso)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## O Que São?

Output Styles permitem modificar o **system prompt** do Claude Code para adaptar comportamento em diferentes contextos.

**Características:**

- ✅ Modificam system prompt do Claude Code
- ✅ Permitem adaptar Claude para diferentes domínios
- ✅ Built-in styles + custom styles
- ✅ Ativação manual pelo usuário

**Quando usar:**

- Claude Code precisa funcionar em domínios além de engenharia de software
- Quer modo educacional com "Insights"
- Precisa de learn-by-doing (Learning mode)
- Customizar comportamento padrão do Claude

---

## Como Funcionam

Output styles modificam diretamente o **system prompt** do Claude Code:

1. **Excluem instruções de eficiência**: Todos os styles removem requisitos de concisão
2. **Custom styles excluem instruções de coding por padrão**: A menos que `keep-coding-instructions: true`
3. **Adicionam instruções customizadas**: Anexadas ao final do system prompt
4. **Disparam lembretes de aderência**: Lembram Claude durante a conversa para seguir regras do style

### Fluxo de Aplicação

```
System Prompt Original
        │
        ▼
┌───────────────────────┐
│ Output Style Ativo    │
├───────────────────────┤
│ - Remove eficiência   │
│ - Remove/mantém coding│
│ - Adiciona instruções │
└───────────────────────┘
        │
        ▼
System Prompt Modificado
```

### Persistência

Mudanças são salvas em `.claude/settings.local.json` no nível do projeto e podem ser editadas diretamente em arquivos de configuração em qualquer nível.

---

## Built-in Styles

### Default

**Descrição**: "The existing system prompt, designed to help you complete software engineering tasks efficiently"

**Comportamento**:

- Foco em engenharia de software
- Respostas diretas e eficientes
- Sem conteúdo educacional extra

**Quando usar**:

- Desenvolvimento de software padrão
- Máxima eficiência
- Comportamento original do Claude Code

---

### Explanatory

**Descrição**: "Educational 'Insights' in between helping you complete software engineering tasks"

**Comportamento**:

- Mantém foco em engenharia de software
- Adiciona seções "Insights" educacionais
- Explica decisões e conceitos

**Quando usar**:

- Aprendendo novos conceitos
- Quer entender o "porquê" por trás das decisões
- Onboarding de novos desenvolvedores

**Exemplo de output**:

```
Let me implement the user authentication API.

[Implementa código]

💡 **Insight**: I used bcrypt for password hashing instead of plain text storage.
This provides:
- Protection against rainbow table attacks
- Adaptive hashing (can increase rounds as hardware improves)
- Industry-standard security (OWASP recommended)

Consider using JWT tokens for session management, which are stateless and
scale better than server-side sessions.
```

---

### Learning

**Descrição**: "Learn-by-doing mode where Claude will not only share 'Insights' while coding, but also ask you to contribute small, strategic pieces of code"

**Comportamento**:

- Modo educacional interativo
- Claude implementa estrutura principal
- Pede contribuições de código do usuário
- Fornece Insights + exercícios práticos

**Quando usar**:

- Aprendendo ativamente uma tecnologia
- Quer praticar escrevendo código
- Precisa reforçar conceitos com prática

**Exemplo de output**:

```
I'll set up the Express API structure for you.

[Implementa boilerplate]

💡 **Insight**: Express uses middleware for request processing. Each middleware
function has access to req, res, and next(). They execute in order.

📝 **Your turn**: Implement the authentication middleware.

Create a function that:
1. Extracts JWT token from Authorization header
2. Verifies the token
3. Attaches user data to req.user
4. Calls next() if valid, or returns 401 if invalid

Try writing this yourself, and I'll review your implementation!
```

---

## Usando Output Styles

### Comandos

**Menu de seleção**:

```
/output-style
```

Abre menu interativo para escolher style.

**Mudar diretamente**:

```
/output-style explanatory
/output-style learning
/output-style default
```

**Acessar configurações**:

```
/config
```

Abre configurações gerais, incluindo output styles.

### Verificar Style Atual

```
/output-style
```

Mostra style ativo atual.

---

## Custom Output Styles

### Estrutura

**Localização**:

- **Projeto**: `.claude/output-styles/my-style.md`
- **Pessoal**: `~/.claude/output-styles/my-style.md`

### Exemplo Básico

```markdown
---
name: security-focused
description: "Focus on security-first approach in all implementations"
keep-coding-instructions: true
---

# Security-First Development

You are an expert developer with deep knowledge of security best practices.

## Core Principles
- Security is NEVER an afterthought
- Follow OWASP Top 10 guidelines
- Implement defense in depth
- Validate all inputs, sanitize all outputs
- Use parameterized queries (never string concatenation)
- Apply least privilege principle

## Before Implementing Any Feature
1. Identify security implications
2. List potential vulnerabilities
3. Propose mitigations
4. Implement with security controls

## Security Checklist
For every feature, verify:
- [ ] Input validation implemented
- [ ] Output encoding/escaping applied
- [ ] Authentication required (if applicable)
- [ ] Authorization checks in place
- [ ] Sensitive data encrypted
- [ ] Error messages don't leak information
- [ ] Rate limiting considered
- [ ] CSRF protection (for state-changing ops)

Always explain security decisions and trade-offs.
```

**Salvar em**: `.claude/output-styles/security-focused.md`

**Usar**: `/output-style security-focused`

### Exemplo Avançado

```markdown
---
name: architecture-review
description: "Focus on architecture, design patterns, and scalability"
keep-coding-instructions: false
---

# Architecture & Design Expert

You are a principal architect specializing in system design, patterns, and scalability.

## Core Focus Areas
- System architecture and design patterns
- Scalability and performance
- Maintainability and extensibility
- Technology stack decisions
- Trade-off analysis

## Response Structure

For every feature request:

### 1. Architecture Analysis
- Current system architecture
- Proposed changes impact
- Scalability considerations
- Performance implications

### 2. Design Patterns
- Applicable patterns (Factory, Strategy, Observer, etc.)
- Why each pattern fits (or doesn't)
- Implementation approach

### 3. Technology Choices
- Recommended technologies/libraries
- Justification for each choice
- Alternatives considered
- Trade-offs

### 4. Scalability Plan
- Horizontal vs vertical scaling
- Caching strategy
- Database considerations
- CDN usage (if applicable)

### 5. Implementation Roadmap
- Phase 1: Core functionality
- Phase 2: Optimization
- Phase 3: Scale-out

## Decision Framework

For every technical decision, provide:
- ✅ **Pros**: Benefits and advantages
- ❌ **Cons**: Drawbacks and limitations
- ⚖️ **Trade-offs**: What we're optimizing for
- 🎯 **Recommendation**: Final choice with reasoning

Always consider: maintainability, performance, cost, and team expertise.
```

---

## Frontmatter

```yaml
---
name: style-name                        # Obrigatório: identificador único
description: "Brief description"        # Obrigatório: mostrado na UI
keep-coding-instructions: true          # Opcional: mantém instruções de coding
---
```

### Campos Detalhados

**`name`** (obrigatório):

- Identificador único do style
- Lowercase com hífens recomendado
- Usado para invocar: `/output-style name`

**`description`** (obrigatório):

- Breve descrição exibida na UI
- Explica o propósito do style
- Ajuda usuário a escolher style apropriado

**`keep-coding-instructions`** (opcional):

- `true` (padrão): Mantém instruções de coding do system prompt
- `false`: Remove instruções de coding (apenas suas instruções)

**Quando usar `keep-coding-instructions: false`**:

- Style completamente substitui comportamento padrão
- Não é para coding (ex: data analysis, document review)
- Quer controle total sobre system prompt

**Quando usar `keep-coding-instructions: true`**:

- Style **complementa** comportamento padrão de coding
- Adiciona foco adicional (ex: security, performance)
- Mantém capacidades de coding do Claude Code

---

## Comparações

### Output Styles vs CLAUDE.md

| Aspecto | Output Styles | CLAUDE.md |
|---------|---------------|-----------|
| **Efeito** | Substitui seções do system prompt | Adiciona como user message após system prompt |
| **Escopo** | Modificação profunda | Adição de contexto |
| **Uso** | Mudança de comportamento | Instruções de projeto |

### Output Styles vs `--append-system-prompt`

| Aspecto | Output Styles | `--append-system-prompt` |
|---------|---------------|--------------------------|
| **Efeito** | Substitui seções | Anexa ao final |
| **Flexibilidade** | Arquivos .md persistentes | Flag de linha de comando |
| **Uso** | Modos alternativos | Contexto temporário |

### Output Styles vs Agents

| Aspecto | Output Styles | Agents |
|---------|---------------|--------|
| **Escopo** | Afeta loop principal | Invocados para tarefas específicas |
| **Modificação** | Apenas system prompt | Model, tools, contexto |
| **Ativação** | Manual (`/output-style`) | Automática ou manual (`@agent`) |

### Output Styles vs Slash Commands

| Aspecto | Output Styles | Slash Commands |
|---------|---------------|----------------|
| **Natureza** | "Stored system prompts" | "Stored prompts" (user messages) |
| **Efeito** | Modifica comportamento | Executa ação específica |
| **Persistência** | Dura toda sessão | Única execução |

---

## Casos de Uso

### 1. Security Auditor

```markdown
---
name: security-auditor
description: "Comprehensive security review and vulnerability detection"
keep-coding-instructions: true
---

# Security Auditor Mode

You are a security expert conducting code security audits.

## Audit Checklist

For every code review:

### OWASP Top 10
- [ ] A01: Broken Access Control
- [ ] A02: Cryptographic Failures
- [ ] A03: Injection
- [ ] A04: Insecure Design
- [ ] A05: Security Misconfiguration
- [ ] A06: Vulnerable Components
- [ ] A07: Identification and Authentication Failures
- [ ] A08: Software and Data Integrity Failures
- [ ] A09: Security Logging and Monitoring Failures
- [ ] A10: Server-Side Request Forgery

### Code Security
- Input validation and sanitization
- Output encoding
- Parameterized queries
- Secure authentication
- Proper authorization
- Sensitive data handling
- Error handling (no information leakage)

## Output Format

```markdown
## Security Audit: [Component Name]

### Critical Issues
- [Issue with code reference and fix]

### Warnings
- [Potential issue with recommendation]

### Best Practices
- [Security best practice applied]

### Recommendations
1. [Improvement with priority]
```

```

### 2. Performance Optimizer

```markdown
---
name: performance-optimizer
description: "Focus on performance optimization and efficiency"
keep-coding-instructions: true
---

# Performance Optimization Mode

You are a performance expert focused on speed and efficiency.

## Analysis Framework

For every implementation:

### 1. Complexity Analysis
- Time complexity: O(?)
- Space complexity: O(?)
- Bottlenecks identified

### 2. Optimization Opportunities
- Algorithm improvements
- Data structure choices
- Caching strategies
- Database query optimization
- Network calls reduction

### 3. Benchmarking
- Expected performance metrics
- Comparison with alternatives
- Break-even points

## Performance Checklist
- [ ] O(n²) or worse algorithms reviewed
- [ ] Database N+1 queries prevented
- [ ] Caching implemented where beneficial
- [ ] Lazy loading applied
- [ ] Resource pooling considered
- [ ] Parallel processing opportunities identified

Always provide before/after performance comparisons.
```

### 3. Documentation Generator

```markdown
---
name: documentation-generator
description: "Generate comprehensive technical documentation"
keep-coding-instructions: true
---

# Documentation Expert Mode

You are a technical writer specializing in developer documentation.

## Documentation Standards

For every feature:

### 1. Overview
- What it does (one sentence)
- Why it exists (business value)
- When to use it

### 2. API Reference
- Function signatures
- Parameters (types, defaults, validation)
- Return values
- Exceptions/errors

### 3. Usage Examples
- Basic usage (hello world)
- Common scenarios (80% use cases)
- Advanced usage (20% edge cases)
- Anti-patterns (what NOT to do)

### 4. Implementation Details
- Architecture decisions
- Design patterns used
- Dependencies
- Performance characteristics

### 5. Testing
- Unit test examples
- Integration test scenarios
- Edge cases to consider

## Style Guide
- Use present tense
- Active voice
- Code examples for every concept
- Explain "why" not just "what"
```

---

## Best Practices

### ✅ DO

- **Be specific**: Clear instructions sobre comportamento esperado
- **Provide structure**: Templates e checklists ajudam consistência
- **Explain purpose**: Description clara para usuário escolher
- **Test thoroughly**: Testar output style antes de compartilhar
- **Keep focused**: Um propósito por style
- **Use markdown**: Formatting melhora legibilidade

### ❌ DON'T

- **Make it too broad**: Style focado é melhor que genérico
- **Duplicate default**: Se é igual ao default, não precisa de style
- **Forget description**: Usuário precisa saber o que o style faz
- **Mix concerns**: Um style = um foco (não misturar security + performance)
- **Overcomplicate**: Simplicidade é melhor

---

## Troubleshooting

### Style não aparece

**Problema**: Custom style não lista em `/output-style`

**Soluções**:

- ✅ Verificar localização: `.claude/output-styles/` ou `~/.claude/output-styles/`
- ✅ Verificar frontmatter YAML válido
- ✅ Verificar campos obrigatórios: `name` e `description`
- ✅ Reiniciar Claude Code

### Style não muda comportamento

**Problema**: Output style ativo mas comportamento não mudou

**Soluções**:

- ✅ Verificar `keep-coding-instructions: true` (mantém instruções padrão)
- ✅ Instruções devem ser claras e específicas
- ✅ Testar com request específico do domínio do style
- ✅ Usar comandos imperativos no style (ex: "Always...", "Never...")

### Conflito com instruções padrão

**Problema**: Style conflita com instruções de coding padrão

**Soluções**:

- ✅ Usar `keep-coding-instructions: false` para controle total
- ✅ Instruções mais específicas têm prioridade
- ✅ Revisar se style está bem focado

### Style muito genérico

**Problema**: Style não produz diferença perceptível

**Soluções**:

- ✅ Adicionar checklists concretos
- ✅ Fornecer templates de output
- ✅ Usar comandos imperativos específicos
- ✅ Incluir exemplos de comportamento esperado

---

## Recursos

**Documentação Oficial**:

- [Claude Code: Output Styles](https://code.claude.com/docs/en/output-styles)

**Guides**:

- [Quick Reference](../quick-reference.md) - Visão geral
- [Best Practices](../best-practices.md) - Práticas gerais

**Configuração**:

- `.claude/output-styles/` - Styles do projeto
- `~/.claude/output-styles/` - Styles pessoais

---

**Última Revisão**: 2026-01-11 por Claude Code
