#!/usr/bin/env python3
"""
PDF Extraction Script
Extrai texto, tabelas e metadados de arquivos PDF.
Suporta OCR para documentos escaneados.

Usage:
    python extract_pdf.py input.pdf [--output json|text|markdown] [--ocr] [--pages 1-5]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


def check_dependencies() -> dict:
    """Verifica dependencias instaladas."""
    deps = {
        "pdfplumber": False,
        "PyPDF2": False,
        "pytesseract": False,
        "pdf2image": False,
    }

    try:
        import pdfplumber
        deps["pdfplumber"] = True
    except ImportError:
        pass

    try:
        import PyPDF2
        deps["PyPDF2"] = True
    except ImportError:
        pass

    try:
        import pytesseract
        deps["pytesseract"] = True
    except ImportError:
        pass

    try:
        from pdf2image import convert_from_path
        deps["pdf2image"] = True
    except ImportError:
        pass

    return deps


def extract_with_pdfplumber(pdf_path: str, pages: Optional[list] = None) -> dict:
    """Extrai texto e tabelas usando pdfplumber."""
    import pdfplumber

    result = {
        "source": pdf_path,
        "pages": [],
        "tables": [],
        "metadata": {},
    }

    with pdfplumber.open(pdf_path) as pdf:
        result["metadata"] = {
            "total_pages": len(pdf.pages),
            "info": pdf.metadata or {},
        }

        pages_to_process = pages or range(len(pdf.pages))

        for i in pages_to_process:
            if i >= len(pdf.pages):
                continue

            page = pdf.pages[i]
            page_data = {
                "number": i + 1,
                "text": page.extract_text() or "",
                "tables": [],
            }

            # Extrair tabelas
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                if table:
                    page_data["tables"].append({
                        "index": table_idx,
                        "rows": len(table),
                        "data": table,
                    })
                    result["tables"].append({
                        "page": i + 1,
                        "index": table_idx,
                        "data": table,
                    })

            result["pages"].append(page_data)

    return result


def extract_with_ocr(pdf_path: str, pages: Optional[list] = None) -> dict:
    """Extrai texto usando OCR (para PDFs escaneados)."""
    import pytesseract
    from pdf2image import convert_from_path

    result = {
        "source": pdf_path,
        "pages": [],
        "ocr_used": True,
        "metadata": {},
    }

    # Converter PDF para imagens
    images = convert_from_path(pdf_path)
    result["metadata"]["total_pages"] = len(images)

    pages_to_process = pages or range(len(images))

    for i in pages_to_process:
        if i >= len(images):
            continue

        image = images[i]
        text = pytesseract.image_to_string(image, lang='por+eng')

        result["pages"].append({
            "number": i + 1,
            "text": text,
            "ocr_confidence": "estimated",  # pytesseract nao retorna confidence por padrao
        })

    return result


def is_scanned_pdf(pdf_path: str) -> bool:
    """Detecta se PDF e escaneado (sem texto extraivel)."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # Verificar primeiras 3 paginas
            for i, page in enumerate(pdf.pages[:3]):
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    return False
        return True
    except Exception:
        return True


def format_as_markdown(data: dict) -> str:
    """Formata resultado como markdown."""
    lines = []
    lines.append(f"# Extracao de: {data.get('source', 'unknown')}")
    lines.append("")

    metadata = data.get("metadata", {})
    lines.append(f"**Paginas**: {metadata.get('total_pages', 'N/A')}")
    if data.get("ocr_used"):
        lines.append("**Metodo**: OCR (documento escaneado)")
    lines.append("")

    for page in data.get("pages", []):
        lines.append(f"## Pagina {page.get('number', '?')}")
        lines.append("")
        lines.append(page.get("text", ""))
        lines.append("")

        for table in page.get("tables", []):
            lines.append(f"### Tabela {table.get('index', 0) + 1}")
            table_data = table.get("data", [])
            if table_data:
                # Header
                header = table_data[0]
                lines.append("| " + " | ".join(str(c or "") for c in header) + " |")
                lines.append("| " + " | ".join("---" for _ in header) + " |")
                # Rows
                for row in table_data[1:]:
                    lines.append("| " + " | ".join(str(c or "") for c in row) + " |")
            lines.append("")

    return "\n".join(lines)


def format_as_text(data: dict) -> str:
    """Formata resultado como texto simples."""
    lines = []
    for page in data.get("pages", []):
        lines.append(f"=== Pagina {page.get('number', '?')} ===")
        lines.append(page.get("text", ""))
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Extrai texto de PDFs")
    parser.add_argument("input", help="Arquivo PDF de entrada")
    parser.add_argument("--output", choices=["json", "text", "markdown"], default="json",
                        help="Formato de saida")
    parser.add_argument("--ocr", action="store_true",
                        help="Forcar uso de OCR")
    parser.add_argument("--pages", type=str,
                        help="Paginas a processar (ex: 1-5 ou 1,3,5)")
    parser.add_argument("--check-deps", action="store_true",
                        help="Verificar dependencias instaladas")

    args = parser.parse_args()

    if args.check_deps:
        deps = check_dependencies()
        print(json.dumps(deps, indent=2))
        sys.exit(0 if all(deps.values()) else 1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(json.dumps({"error": f"Arquivo nao encontrado: {args.input}"}))
        sys.exit(1)

    # Parse pages argument
    pages = None
    if args.pages:
        pages = []
        for part in args.pages.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                pages.extend(range(start - 1, end))  # 0-indexed
            else:
                pages.append(int(part) - 1)

    # Decidir metodo de extracao
    use_ocr = args.ocr or is_scanned_pdf(str(input_path))

    deps = check_dependencies()

    if use_ocr:
        if not deps["pytesseract"] or not deps["pdf2image"]:
            print(json.dumps({
                "error": "OCR requerido mas dependencias nao instaladas",
                "missing": ["pytesseract", "pdf2image"],
                "install": "pip install pytesseract pdf2image && apt install tesseract-ocr",
            }))
            sys.exit(1)
        result = extract_with_ocr(str(input_path), pages)
    else:
        if not deps["pdfplumber"]:
            print(json.dumps({
                "error": "pdfplumber nao instalado",
                "install": "pip install pdfplumber",
            }))
            sys.exit(1)
        result = extract_with_pdfplumber(str(input_path), pages)

    # Formatar saida
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.output == "markdown":
        print(format_as_markdown(result))
    else:
        print(format_as_text(result))


if __name__ == "__main__":
    main()
