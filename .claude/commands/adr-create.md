---
name: adr-create
description: |
  Cria um novo Architecture Decision Record (ADR).
  Documenta decisoes arquiteturais significativas.

  Examples:
  - <example>
    user: "/adr-create Escolha de banco de dados"
    assistant: "Vou criar um ADR para documentar essa decisao"
    </example>
---

# Criar Architecture Decision Record

## Instrucoes

Voce deve criar um novo ADR seguindo o formato padrao do projeto.

## Processo

1. **Coletar Contexto**: Entender qual decisao precisa ser documentada
2. **Proximo Numero**: Identificar o proximo numero de ADR disponivel
3. **Gerar Slug**: Criar slug a partir do titulo
4. **Criar Arquivo**: Usar template padrao
5. **Preencher Conteudo**: Documentar decisao com alternativas
6. **Registrar no RAG**: Adicionar ao corpus de conhecimento

## Template ADR

```markdown
# ADR-{numero}: {Titulo}

## Status

Proposed

## Contexto

{Descreva a situacao que levou a essa decisao.
Inclua restricoes, requisitos e forcas em jogo.}

## Decisao

Vamos {decisao tomada}.

## Alternativas Consideradas

### Opcao 1: {Nome}
- **Pros:** ...
- **Cons:** ...

### Opcao 2: {Nome}
- **Pros:** ...
- **Cons:** ...

## Consequencias

### Positivas
- ...

### Negativas
- ...

### Neutras
- ...

## Referencias

- [Link]
```

## Estrutura de Arquivos

```
docs/
└── adr/
    ├── 0000-template.md
    ├── 0001-{slug}.md
    ├── 0002-{slug}.md
    └── index.md
```

## Output Esperado

Apos criar o ADR:

```yaml
adr_created:
  number: "0005"
  title: "Usar PostgreSQL como Banco Principal"
  slug: "use-postgresql-for-main-db"
  file: "docs/adr/0005-use-postgresql-for-main-db.md"
  status: "proposed"
  indexed: true

next_steps:
  - "Revisar com Tech Lead"
  - "Atualizar status para 'Accepted' apos aprovacao"
```

## Uso

```
/adr-create "Titulo da Decisao"
/adr-create --list                    # Listar ADRs existentes
/adr-create --status 0005 accepted    # Atualizar status
```
