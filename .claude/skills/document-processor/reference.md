# Document Processor - Reference Guide

## Padroes de Design

### Validation-First Pattern

Baseado no padrao extraido do xlsx skill da Anthropic:

```
1. CREATE  → Gerar/processar documento
2. VALIDATE → Executar validacao especializada
3. REPORT  → Agregar TODOS os erros em formato estruturado
4. FIX     → Corrigir todos de uma vez
```

**Por que isso importa:**
- Evita falhas parciais
- Permite correcao em lote
- Melhora UX (usuario ve todos problemas de uma vez)

### Multi-Tool Strategy

| Tarefa | Ferramenta | Justificativa |
|--------|------------|---------------|
| Extracao PDF | pdfplumber | Melhor para texto estruturado e tabelas |
| OCR | tesseract | Padrao da industria para OCR |
| XLSX processing | openpyxl | Preserva formulas, suporta xlsx moderno |
| XLSX validation | LibreOffice | Recalcula formulas de verdade |
| DOCX extraction | python-docx | API pythonica limpa |
| DOCX tracked changes | OOXML direto | python-docx nao expoe tracked changes |

### Zero-Error Policy

Para documentos criados pelo skill:
- ZERO erros de formula em planilhas
- ZERO problemas de formatacao
- Validacao OBRIGATORIA antes de entregar

## Detalhes de Implementacao

### PDF - Deteccao de Escaneado

```python
def is_scanned_pdf(path):
    """PDF e escaneado se primeiras paginas nao tem texto."""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages[:3]:
            text = page.extract_text()
            if text and len(text.strip()) > 50:
                return False
    return True
```

### XLSX - Tipos de Erro

| Codigo | Causa | Resolucao |
|--------|-------|-----------|
| `#VALUE!` | Tipo incompativel | Verificar tipos de dados |
| `#REF!` | Referencia invalida | Celula/range deletado |
| `#DIV/0!` | Divisao por zero | Adicionar IF(B1=0,...) |
| `#NAME?` | Nome desconhecido | Funcao ou range inexistente |
| `#N/A` | VLOOKUP falhou | Valor nao encontrado |
| `#NUM!` | Numero invalido | Ex: SQRT(-1) |
| `#NULL!` | Intersecao nula | Range mal formatado |

### DOCX - Tracked Changes OOXML

Estrutura XML:

```xml
<!-- Insercao -->
<w:ins w:author="John Doe" w:date="2026-01-14T10:30:00Z">
  <w:r>
    <w:t>texto inserido</w:t>
  </w:r>
</w:ins>

<!-- Delecao -->
<w:del w:author="Jane Smith" w:date="2026-01-14T11:00:00Z">
  <w:r>
    <w:delText>texto deletado</w:delText>
  </w:r>
</w:del>

<!-- Mudanca de formatacao -->
<w:rPrChange w:author="Bob">
  <w:rPr><w:b/></w:rPr>
</w:rPrChange>
```

## Exemplos de Uso

### Extrair requisitos de PDF

```bash
# Extrair texto estruturado
python scripts/extract_pdf.py requirements.pdf --output markdown

# Se escaneado, usar OCR
python scripts/extract_pdf.py scanned.pdf --ocr --output json
```

### Validar planilha financeira

```bash
# Validacao rapida (openpyxl)
python scripts/process_xlsx.py budget.xlsx --mode validate

# Validacao profunda (LibreOffice - recalcula tudo)
python scripts/process_xlsx.py budget.xlsx --mode validate --use-libreoffice
```

### Detectar alteracoes em contrato

```bash
# Listar tracked changes
python scripts/process_docx.py contract.docx --mode changes

# Output esperado:
# {
#   "has_tracked_changes": true,
#   "changes": [
#     {"type": "insertion", "author": "Legal Team", "text": "nova clausula..."},
#     {"type": "deletion", "author": "Legal Team", "text": "clausula removida..."}
#   ]
# }
```

## Integracao com Agentes SDLC

### intake-analyst (Phase 0)

```yaml
workflow:
  - Receber documento de stakeholder
  - /doc-validate {documento}
  - Se valido: /doc-extract {documento}
  - Indexar no corpus RAG
```

### requirements-analyst (Phase 2)

```yaml
workflow:
  - Receber matriz de requisitos (XLSX)
  - /doc-extract requisitos.xlsx --output markdown
  - Validar completude
  - Gerar user stories
```

### qa-analyst (Phase 6)

```yaml
workflow:
  - Receber test report (XLSX)
  - /doc-validate report.xlsx
  - Se erros: reportar
  - Se valido: processar metricas
```

## Troubleshooting

### Erro: "pdfplumber nao instalado"

```bash
pip install pdfplumber
```

### Erro: "LibreOffice timeout"

LibreOffice pode ser lento na primeira execucao. Aumentar timeout ou pre-aquecer:

```bash
libreoffice --headless --version  # Pre-aquece JVM
```

### Erro: "OCR retorna texto ilegivel"

Verificar idioma:

```bash
tesseract --list-langs
# Instalar portugues se necessario
apt install tesseract-ocr-por
```

### Erro: "DOCX corrompido"

Tentar reparar via LibreOffice:

```bash
libreoffice --headless --convert-to docx --outdir /tmp corrupted.docx
```

## Performance

| Operacao | Tamanho | Tempo Esperado |
|----------|---------|----------------|
| PDF extract (texto) | 100 paginas | ~5s |
| PDF extract (OCR) | 10 paginas | ~30s |
| XLSX validate (openpyxl) | 10k linhas | ~2s |
| XLSX validate (LibreOffice) | 10k linhas | ~15s |
| DOCX extract | 50 paginas | ~1s |

## Limitacoes Conhecidas

1. **PDF com layout complexo**: Tabelas com celulas mescladas podem nao extrair corretamente
2. **XLSX com macros**: VBA nao e executado na validacao
3. **DOCX com OLE objects**: Objetos embedados (Excel, PPT) nao sao extraidos
4. **Arquivos protegidos**: Documentos com senha nao sao suportados

## Referencias

- [pdfplumber docs](https://github.com/jsvine/pdfplumber)
- [openpyxl docs](https://openpyxl.readthedocs.io/)
- [python-docx docs](https://python-docx.readthedocs.io/)
- [OOXML specification](https://docs.microsoft.com/en-us/openspecs/office_standards/ms-docx/)
- [Anthropic xlsx skill](https://github.com/anthropics/skills/tree/main/skills/xlsx) - Padroes de referencia
