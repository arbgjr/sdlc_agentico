# Documentos de Referencia

Este diretorio contem documentos externos usados como referencia no desenvolvimento.

## Estrutura

```
references/
├── legal/          # Leis, regulamentos, normas
├── technical/      # RFCs, especificacoes tecnicas
├── business/       # Regras de negocio, manuais
└── internal/       # Documentos internos da organizacao
```

## Como Adicionar

1. Coloque o documento na pasta apropriada
2. Atualize o indice abaixo
3. Execute `/ref-add {caminho}` para indexar no corpus RAG
4. Se for PDF/Word, considere adicionar resumo em texto

## Indice

### Legal

| Documento | Descricao | Data |
|-----------|-----------|------|
| *vazio* | *adicione documentos aqui* | - |

### Technical

| Documento | Descricao | Versao |
|-----------|-----------|--------|
| *vazio* | *adicione documentos aqui* | - |

### Business

| Documento | Descricao | Atualizacao |
|-----------|-----------|-------------|
| *vazio* | *adicione documentos aqui* | - |

### Internal

| Documento | Descricao | Autor |
|-----------|-----------|-------|
| coding-standards.md | Manual de Desenvolvimento | Time |

## Formatos Suportados

- **PDF**: Extraido automaticamente com pdftotext
- **Markdown**: Indexado diretamente
- **Word (.docx)**: Extraido com python-docx
- **Texto**: Indexado diretamente

## Boas Praticas

1. **Nomeie arquivos de forma descritiva**: `lei-13775-2018-duplicatas.pdf` em vez de `documento.pdf`
2. **Mantenha versoes**: Se atualizar um documento, mantenha a versao anterior com sufixo `_old`
3. **Documente a fonte**: Adicione comentario no indice sobre de onde veio o documento
4. **Resuma documentos longos**: Para PDFs grandes, crie um resumo em `.txt` ou `.md`
