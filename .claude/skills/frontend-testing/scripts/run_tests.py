#!/usr/bin/env python3
"""
E2E Test Runner Script
Executa testes E2E usando Playwright.

Usage:
    python run_tests.py --url http://localhost:3000
    python run_tests.py --url http://localhost:3000 --test-dir tests/e2e
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime


def check_dependencies() -> dict:
    """Verifica dependencias."""
    deps = {
        "playwright": False,
        "pytest": False,
    }

    try:
        from playwright.sync_api import sync_playwright
        deps["playwright"] = True
    except ImportError:
        pass

    try:
        import pytest
        deps["pytest"] = True
    except ImportError:
        pass

    return deps


def run_health_check(url: str, timeout: int = 30000) -> dict:
    """Executa verificacao de saude basica."""
    from playwright.sync_api import sync_playwright

    result = {
        "url": url,
        "status": "healthy",
        "checks": [],
        "timestamp": datetime.now().isoformat(),
    }

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        console_errors = []
        page_errors = []

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        try:
            # Teste 1: Pagina carrega
            response = page.goto(url, timeout=timeout)
            page.wait_for_load_state("networkidle", timeout=timeout)

            check_load = {
                "name": "page_load",
                "status": "pass" if response and response.status < 400 else "fail",
                "details": {
                    "status_code": response.status if response else None,
                    "title": page.title(),
                },
            }
            result["checks"].append(check_load)

            # Teste 2: Sem erros criticos no console
            page.wait_for_timeout(2000)  # Aguardar erros assincronos

            check_console = {
                "name": "console_errors",
                "status": "pass" if len(console_errors) == 0 else "warn",
                "details": {
                    "error_count": len(console_errors),
                    "errors": console_errors[:5],  # Primeiros 5
                },
            }
            result["checks"].append(check_console)

            # Teste 3: Sem erros de pagina
            check_page_errors = {
                "name": "page_errors",
                "status": "pass" if len(page_errors) == 0 else "fail",
                "details": {
                    "error_count": len(page_errors),
                    "errors": page_errors[:5],
                },
            }
            result["checks"].append(check_page_errors)

            # Teste 4: Conteudo basico existe
            body_text = page.inner_text("body")
            check_content = {
                "name": "has_content",
                "status": "pass" if len(body_text.strip()) > 10 else "warn",
                "details": {
                    "body_length": len(body_text),
                },
            }
            result["checks"].append(check_content)

            # Teste 5: Links basicos (nao quebrados)
            links = page.locator("a[href]").all()
            broken_links = []

            for link in links[:10]:  # Verificar apenas primeiros 10
                href = link.get_attribute("href")
                if href and href.startswith(("http://", "https://")):
                    try:
                        # Verificacao rapida
                        import urllib.request
                        req = urllib.request.Request(href, method='HEAD')
                        req.add_header('User-Agent', 'Mozilla/5.0')
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            if resp.status >= 400:
                                broken_links.append({"href": href, "status": resp.status})
                    except Exception as e:
                        broken_links.append({"href": href, "error": str(e)[:50]})

            check_links = {
                "name": "links",
                "status": "pass" if len(broken_links) == 0 else "warn",
                "details": {
                    "total_links": len(links),
                    "checked": min(10, len(links)),
                    "broken": broken_links,
                },
            }
            result["checks"].append(check_links)

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        finally:
            browser.close()

    # Determinar status geral
    failed = any(c["status"] == "fail" for c in result["checks"])
    warned = any(c["status"] == "warn" for c in result["checks"])

    if failed:
        result["status"] = "unhealthy"
    elif warned:
        result["status"] = "degraded"

    return result


def run_e2e_tests(url: str, test_dir: str = None) -> dict:
    """Executa testes E2E com pytest."""
    import subprocess

    result = {
        "url": url,
        "test_dir": test_dir,
        "status": "unknown",
        "timestamp": datetime.now().isoformat(),
    }

    # Configurar URL como variavel de ambiente
    env = os.environ.copy()
    env["TEST_BASE_URL"] = url

    # Comando pytest
    cmd = ["pytest", "-v", "--tb=short"]

    if test_dir:
        cmd.append(test_dir)

    # Adicionar report JSON
    cmd.extend(["--json-report", "--json-report-file=test_report.json"])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,  # 5 minutos
        )

        result["exit_code"] = proc.returncode
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
        result["status"] = "pass" if proc.returncode == 0 else "fail"

        # Tentar ler report JSON
        report_path = Path("test_report.json")
        if report_path.exists():
            with open(report_path) as f:
                report = json.load(f)
                result["summary"] = report.get("summary", {})

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Testes excederam timeout de 5 minutos"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(description="Executa testes E2E")
    parser.add_argument("--url", required=True, help="URL base para testes")
    parser.add_argument("--test-dir", help="Diretorio de testes")
    parser.add_argument("--health-only", action="store_true",
                        help="Apenas verificacao de saude (sem pytest)")
    parser.add_argument("--check-deps", action="store_true")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")

    args = parser.parse_args()

    if args.check_deps:
        deps = check_dependencies()
        print(json.dumps(deps, indent=2))
        sys.exit(0 if all(deps.values()) else 1)

    deps = check_dependencies()
    if not deps["playwright"]:
        print(json.dumps({
            "error": "playwright nao instalado",
            "install": "pip install playwright && playwright install chromium",
        }))
        sys.exit(1)

    if args.health_only:
        result = run_health_check(args.url)
    else:
        if not deps["pytest"]:
            print("pytest nao instalado, executando apenas health check")
            result = run_health_check(args.url)
        else:
            # Health check primeiro
            health = run_health_check(args.url)
            if health["status"] == "unhealthy":
                result = {
                    "status": "skipped",
                    "reason": "Health check failed",
                    "health_check": health,
                }
            else:
                # Executar testes
                test_result = run_e2e_tests(args.url, args.test_dir)
                result = {
                    "health_check": health,
                    "tests": test_result,
                    "status": test_result["status"],
                }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Status: {result['status']}")
        if "checks" in result:
            for check in result["checks"]:
                status_icon = "✓" if check["status"] == "pass" else "✗" if check["status"] == "fail" else "⚠"
                print(f"  {status_icon} {check['name']}: {check['status']}")

    # Exit code baseado no status
    if result["status"] in ["unhealthy", "fail", "error"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
