#!/usr/bin/env python3
"""
Query Phase Errors - Consulta logs Loki por erros da fase atual.

Usage:
    python query_phase_errors.py [--phase N] [--severity LEVEL]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional


LOKI_URL = os.environ.get("SDLC_LOKI_URL", "http://localhost:3100")


def check_loki_available() -> bool:
    """Verifica se Loki está disponível."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "2", f"{LOKI_URL}/ready"],
            capture_output=True,
            timeout=3
        )
        return result.returncode == 0
    except Exception:
        return False


def query_loki_errors(phase: int, hours: int = 24, severity: str = "ERROR") -> List[Dict]:
    """
    Consulta Loki por erros da fase.

    Args:
        phase: Número da fase (0-8)
        hours: Janela de tempo em horas
        severity: Nível mínimo (ERROR, WARN, INFO)

    Returns:
        Lista de erros encontrados
    """
    # Calcular range de tempo
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    # Construir query LogQL
    # {app="sdlc-agentico",phase="N",level=~"ERROR|CRITICAL"}
    logql_query = f'{{app="sdlc-agentico",phase="{phase}",level=~"{severity}|CRITICAL"}}'

    # Fazer requisição ao Loki
    params = {
        "query": logql_query,
        "start": int(start_time.timestamp() * 1e9),  # nanoseconds
        "end": int(end_time.timestamp() * 1e9),
        "limit": 1000
    }

    try:
        result = subprocess.run(
            [
                "curl", "-s", "-G",
                f"{LOKI_URL}/loki/api/v1/query_range",
                "--data-urlencode", f"query={params['query']}",
                "--data-urlencode", f"start={params['start']}",
                "--data-urlencode", f"end={params['end']}",
                "--data-urlencode", f"limit={params['limit']}"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"✗ Erro ao consultar Loki: {result.stderr}", file=sys.stderr)
            return []

        # Parse JSON response
        response = json.loads(result.stdout)

        if response.get("status") != "success":
            print(f"✗ Loki retornou erro: {response.get('error', 'unknown')}", file=sys.stderr)
            return []

        # Extrair logs
        errors = []
        for stream in response.get("data", {}).get("result", []):
            labels = stream.get("stream", {})
            for value in stream.get("values", []):
                timestamp_ns, log_line = value

                # Tentar parsear JSON
                try:
                    log_data = json.loads(log_line)
                except json.JSONDecodeError:
                    log_data = {"message": log_line}

                errors.append({
                    "timestamp": int(timestamp_ns) // 1e9,  # Convert to seconds
                    "level": labels.get("level", "ERROR"),
                    "skill": labels.get("skill", "unknown"),
                    "message": log_data.get("message", log_line),
                    "script": labels.get("script", ""),
                    "data": log_data
                })

        return errors

    except subprocess.TimeoutExpired:
        print("✗ Timeout ao consultar Loki", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"✗ Erro ao parsear resposta do Loki: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"✗ Erro inesperado: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Consulta erros da fase no Loki")
    parser.add_argument("--phase", type=int, help="Número da fase (0-8)")
    parser.add_argument("--hours", type=int, default=24, help="Janela de tempo em horas")
    parser.add_argument("--severity", default="ERROR", help="Nível mínimo (ERROR, WARN, INFO)")
    parser.add_argument("--json", action="store_true", help="Output em JSON")
    args = parser.parse_args()

    # Detectar fase se não fornecida
    phase = args.phase
    if phase is None:
        # Tentar do manifest
        try:
            with open(".agentic_sdlc/projects/current.json") as f:
                data = json.load(f)
                phase = data.get("current_phase", 0)
        except Exception:
            phase = 0

    # Verificar Loki
    if not check_loki_available():
        print("⚠ Loki não está disponível", file=sys.stderr)
        print("   Pulando análise de erros do Loki", file=sys.stderr)
        return 0

    # Consultar erros
    errors = query_loki_errors(phase, args.hours, args.severity)

    if not errors:
        print(f"✓ Nenhum erro encontrado na Phase {phase} (últimas {args.hours}h)")
        return 0

    # Output
    if args.json:
        print(json.dumps(errors, indent=2))
    else:
        print(f"\n⚠ Encontrados {len(errors)} erros na Phase {phase}:")
        print("━" * 60)

        for i, error in enumerate(errors[:10], 1):  # Mostrar só 10 mais recentes
            timestamp = datetime.fromtimestamp(error["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{i}] {timestamp} - {error['level']}")
            print(f"    Skill: {error['skill']}")
            print(f"    Message: {error['message'][:100]}")
            if error['script']:
                print(f"    Script: {error['script']}")

        if len(errors) > 10:
            print(f"\n... e mais {len(errors) - 10} erros")

        print("\n━" * 60)
        print(f"Total: {len(errors)} erros encontrados")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
