#!/usr/bin/env python3
"""
Screenshot Capture Script
Captura screenshots de paginas web usando Playwright.

Usage:
    python capture_screenshot.py https://example.com --output screenshot.png
    python capture_screenshot.py http://localhost:3000 --full-page --output home.png
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def check_dependencies() -> dict:
    """Verifica dependencias."""
    deps = {
        "playwright": False,
    }

    try:
        from playwright.sync_api import sync_playwright
        deps["playwright"] = True
    except ImportError:
        pass

    return deps


def capture_screenshot(
    url: str,
    output_path: str,
    full_page: bool = False,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    timeout: int = 30000,
    wait_for_selector: str = None,
) -> dict:
    """Captura screenshot de uma URL."""
    from playwright.sync_api import sync_playwright

    result = {
        "url": url,
        "output": output_path,
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "errors": [],
        "console_messages": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height}
        )
        page = context.new_page()

        # Capturar mensagens de console
        def handle_console(msg):
            result["console_messages"].append({
                "type": msg.type,
                "text": msg.text,
            })

        def handle_error(error):
            result["errors"].append(str(error))

        page.on("console", handle_console)
        page.on("pageerror", handle_error)

        try:
            # Navegar
            response = page.goto(url, timeout=timeout)

            if response:
                result["status_code"] = response.status

            # Aguardar network idle
            page.wait_for_load_state("networkidle", timeout=timeout)

            # Aguardar seletor especifico se fornecido
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=timeout)

            # Capturar screenshot
            page.screenshot(path=output_path, full_page=full_page)

            # Coletar informacoes da pagina
            result["title"] = page.title()
            result["viewport"] = {
                "width": viewport_width,
                "height": viewport_height,
            }

            # Contar erros de console
            error_count = sum(1 for msg in result["console_messages"] if msg["type"] == "error")
            warning_count = sum(1 for msg in result["console_messages"] if msg["type"] == "warning")

            result["console_summary"] = {
                "errors": error_count,
                "warnings": warning_count,
                "total": len(result["console_messages"]),
            }

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))

        finally:
            browser.close()

    return result


def main():
    parser = argparse.ArgumentParser(description="Captura screenshots de paginas web")
    parser.add_argument("url", help="URL para capturar")
    parser.add_argument("--output", "-o", required=True, help="Caminho do arquivo de saida")
    parser.add_argument("--full-page", action="store_true", help="Capturar pagina inteira")
    parser.add_argument("--width", type=int, default=1280, help="Largura do viewport")
    parser.add_argument("--height", type=int, default=720, help="Altura do viewport")
    parser.add_argument("--timeout", type=int, default=30000, help="Timeout em ms")
    parser.add_argument("--wait-for", help="Seletor para aguardar antes de capturar")
    parser.add_argument("--check-deps", action="store_true", help="Verificar dependencias")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")

    args = parser.parse_args()

    if args.check_deps:
        deps = check_dependencies()
        print(json.dumps(deps, indent=2))
        sys.exit(0 if deps["playwright"] else 1)

    deps = check_dependencies()
    if not deps["playwright"]:
        print(json.dumps({
            "error": "playwright nao instalado",
            "install": "pip install playwright && playwright install chromium",
        }))
        sys.exit(1)

    # Criar diretorio de saida se necessario
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = capture_screenshot(
        url=args.url,
        output_path=str(output_path),
        full_page=args.full_page,
        viewport_width=args.width,
        viewport_height=args.height,
        timeout=args.timeout,
        wait_for_selector=args.wait_for,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["status"] == "success":
            print(f"Screenshot salvo: {result['output']}")
            print(f"Titulo: {result.get('title', 'N/A')}")
            summary = result.get("console_summary", {})
            if summary.get("errors", 0) > 0:
                print(f"Avisos: {summary.get('errors', 0)} erros no console")
        else:
            print(f"Erro: {result.get('errors', ['Desconhecido'])}")
            sys.exit(1)


if __name__ == "__main__":
    main()
