#!/usr/bin/env python3
"""
Dependency Checker for Frontend Testing Skill
Verifica todas as dependencias necessarias.

Usage:
    python check_deps.py
    python check_deps.py --install
"""

import argparse
import json
import subprocess
import sys
import shutil


def check_python_packages() -> dict:
    """Verifica pacotes Python instalados."""
    packages = {
        "playwright": {"required": True, "purpose": "Browser automation"},
        "pytest": {"required": False, "purpose": "Test framework"},
        "pytest-playwright": {"required": False, "purpose": "Pytest integration"},
    }

    result = {}
    for pkg, info in packages.items():
        try:
            __import__(pkg.replace("-", "_"))
            result[pkg] = {
                "installed": True,
                "required": info["required"],
                "purpose": info["purpose"],
            }
        except ImportError:
            result[pkg] = {
                "installed": False,
                "required": info["required"],
                "purpose": info["purpose"],
            }

    return result


def check_browsers() -> dict:
    """Verifica browsers do Playwright instalados."""
    result = {
        "chromium": False,
        "firefox": False,
        "webkit": False,
    }

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Tentar cada browser
            for browser_name in result.keys():
                try:
                    browser_type = getattr(p, browser_name)
                    browser = browser_type.launch()
                    browser.close()
                    result[browser_name] = True
                except Exception:
                    pass
    except Exception:
        pass

    return result


def check_system_tools() -> dict:
    """Verifica ferramentas do sistema."""
    tools = {
        "node": {"required": False, "purpose": "Node.js runtime"},
        "npm": {"required": False, "purpose": "Node package manager"},
    }

    result = {}
    for tool, info in tools.items():
        path = shutil.which(tool)
        result[tool] = {
            "installed": path is not None,
            "path": path,
            "required": info["required"],
            "purpose": info["purpose"],
        }

        # Obter versao se instalado
        if path:
            try:
                proc = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=5)
                version = proc.stdout.strip().split("\n")[0]
                result[tool]["version"] = version
            except Exception:
                pass

    return result


def install_dependencies():
    """Instala dependencias faltantes."""
    print("Instalando dependencias...")

    # Instalar pacotes Python
    packages = ["playwright", "pytest", "pytest-playwright"]
    for pkg in packages:
        print(f"  Instalando {pkg}...")
        subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)

    # Instalar browser
    print("  Instalando Chromium...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

    print("Dependencias instaladas com sucesso!")


def main():
    parser = argparse.ArgumentParser(description="Verifica dependencias do frontend-testing")
    parser.add_argument("--install", action="store_true", help="Instalar dependencias faltantes")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")

    args = parser.parse_args()

    if args.install:
        install_dependencies()
        return

    result = {
        "python_packages": check_python_packages(),
        "browsers": check_browsers(),
        "system_tools": check_system_tools(),
        "overall_status": "ok",
        "missing": [],
    }

    # Verificar dependencias obrigatorias
    for pkg, info in result["python_packages"].items():
        if info["required"] and not info["installed"]:
            result["missing"].append(pkg)

    # Verificar se pelo menos um browser esta instalado
    if not any(result["browsers"].values()):
        result["missing"].append("browser (chromium/firefox/webkit)")

    if result["missing"]:
        result["overall_status"] = "missing_required"
        result["install_command"] = "python check_deps.py --install"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=== Frontend Testing Dependencies ===\n")

        print("Python Packages:")
        for pkg, info in result["python_packages"].items():
            status = "✓" if info["installed"] else "✗"
            req = "(required)" if info["required"] else "(optional)"
            print(f"  {status} {pkg} {req}")

        print("\nBrowsers:")
        for browser, installed in result["browsers"].items():
            status = "✓" if installed else "✗"
            print(f"  {status} {browser}")

        print("\nSystem Tools:")
        for tool, info in result["system_tools"].items():
            status = "✓" if info["installed"] else "✗"
            version = f" ({info.get('version', '')})" if info.get("version") else ""
            print(f"  {status} {tool}{version}")

        print(f"\nStatus: {result['overall_status']}")

        if result["missing"]:
            print(f"\nFaltando: {', '.join(result['missing'])}")
            print(f"Para instalar: python check_deps.py --install")

    sys.exit(0 if result["overall_status"] == "ok" else 1)


if __name__ == "__main__":
    main()
