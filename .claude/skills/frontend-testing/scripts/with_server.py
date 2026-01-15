#!/usr/bin/env python3
"""
Server Lifecycle Manager
Gerencia servidores locais durante testes.
Baseado no padrao with_server.py do webapp-testing da Anthropic.

Usage:
    python with_server.py --server "npm run dev" --port 3000 -- pytest tests/
    python with_server.py --server "cd backend && python server.py" --port 3000 \
                          --server "cd frontend && npm run dev" --port 5173 \
                          -- python run_tests.py
"""

import argparse
import subprocess
import sys
import time
import socket
import signal
import os
from typing import List, Tuple, Optional


def parse_args():
    parser = argparse.ArgumentParser(
        description="Gerencia servidores durante execucao de comandos"
    )
    parser.add_argument(
        "--server", "-s",
        action="append",
        required=True,
        help="Comando do servidor (pode repetir para multiplos servidores)"
    )
    parser.add_argument(
        "--port", "-p",
        action="append",
        type=int,
        required=True,
        help="Porta do servidor (deve corresponder a cada --server)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=30,
        help="Timeout em segundos para aguardar servidor (default: 30)"
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Fazer health check HTTP alem de verificar porta"
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Comando a executar apos servidores iniciarem"
    )

    args = parser.parse_args()

    # Validar que temos mesmo numero de servers e ports
    if len(args.server) != len(args.port):
        parser.error("Numero de --server deve igual a numero de --port")

    # Remover '--' do inicio do comando se presente
    if args.command and args.command[0] == '--':
        args.command = args.command[1:]

    return args


def is_port_open(host: str, port: int) -> bool:
    """Verifica se uma porta esta aberta."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.error:
        return False


def wait_for_port(port: int, timeout: int = 30, interval: float = 0.5) -> bool:
    """Aguarda ate que uma porta esteja disponivel."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_open("127.0.0.1", port):
            return True
        time.sleep(interval)
    return False


def health_check_http(port: int) -> bool:
    """Faz um health check HTTP basico."""
    try:
        import urllib.request
        url = f"http://127.0.0.1:{port}/"
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status < 500
    except Exception:
        return False


def start_server(command: str, port: int) -> subprocess.Popen:
    """Inicia um servidor em background."""
    # Usar shell=True para suportar comandos como "cd x && y"
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,  # Criar novo grupo de processos
    )
    return proc


def stop_server(proc: subprocess.Popen):
    """Para um servidor e todos seus processos filhos."""
    if proc.poll() is None:  # Ainda rodando
        try:
            # Enviar SIGTERM para o grupo de processos
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                # Forcar com SIGKILL
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass


def main():
    args = parse_args()

    if not args.command:
        print("Erro: Nenhum comando especificado para executar", file=sys.stderr)
        sys.exit(1)

    servers: List[Tuple[subprocess.Popen, int, str]] = []
    exit_code = 1

    try:
        # Iniciar todos os servidores
        print(f"Iniciando {len(args.server)} servidor(es)...")

        for cmd, port in zip(args.server, args.port):
            # Verificar se porta ja esta em uso
            if is_port_open("127.0.0.1", port):
                print(f"Aviso: Porta {port} ja esta em uso", file=sys.stderr)

            print(f"  Iniciando: {cmd} (porta {port})")
            proc = start_server(cmd, port)
            servers.append((proc, port, cmd))

        # Aguardar todos os servidores
        print(f"Aguardando servidores (timeout: {args.timeout}s)...")

        for proc, port, cmd in servers:
            if not wait_for_port(port, timeout=args.timeout):
                print(f"Erro: Servidor na porta {port} nao iniciou", file=sys.stderr)
                print(f"  Comando: {cmd}", file=sys.stderr)

                # Mostrar stderr do servidor
                if proc.stderr:
                    stderr = proc.stderr.read().decode('utf-8', errors='replace')
                    if stderr:
                        print(f"  Stderr: {stderr[:500]}", file=sys.stderr)

                raise RuntimeError(f"Servidor na porta {port} falhou ao iniciar")

            print(f"  Porta {port}: OK")

            # Health check opcional
            if args.health_check:
                if health_check_http(port):
                    print(f"  Health check {port}: OK")
                else:
                    print(f"  Aviso: Health check {port} falhou (servidor pode estar OK)")

        # Executar comando principal
        print(f"\nExecutando: {' '.join(args.command)}\n")
        print("-" * 50)

        result = subprocess.run(args.command)
        exit_code = result.returncode

        print("-" * 50)
        print(f"\nComando finalizado com codigo: {exit_code}")

    except KeyboardInterrupt:
        print("\nInterrompido pelo usuario")
        exit_code = 130

    except Exception as e:
        print(f"\nErro: {e}", file=sys.stderr)
        exit_code = 1

    finally:
        # Parar todos os servidores
        print("\nEncerrando servidores...")
        for proc, port, cmd in servers:
            print(f"  Parando servidor na porta {port}...")
            stop_server(proc)
        print("Servidores encerrados")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
