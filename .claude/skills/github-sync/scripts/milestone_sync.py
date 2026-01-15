#!/usr/bin/env python3
"""
Milestone Sync - Gerencia milestones (sprints) no repositorio GitHub.

Usage:
    python milestone_sync.py create --title "Sprint 1" --description "Goal" --due-date "2026-01-28"
    python milestone_sync.py close --title "Sprint 1"
    python milestone_sync.py list
    python milestone_sync.py get --title "Sprint 1"
    python milestone_sync.py update --title "Sprint 1" --description "New goal"
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Milestone:
    """Representa um milestone do GitHub."""
    number: int
    title: str
    description: str
    state: str
    due_on: Optional[str]
    open_issues: int
    closed_issues: int
    html_url: str


def run_gh_command(args: list[str]) -> subprocess.CompletedProcess:
    """Executa comando gh e retorna resultado."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return result
    except FileNotFoundError:
        print("Erro: GitHub CLI (gh) nao encontrado.", file=sys.stderr)
        sys.exit(1)


def get_repo_info() -> tuple[str, str]:
    """Retorna owner e repo do repositorio atual."""
    result = run_gh_command(["repo", "view", "--json", "owner,name"])
    if result.returncode != 0:
        print("Erro: Nao foi possivel detectar repositorio.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    return data["owner"]["login"], data["name"]


def list_milestones(state: str = "all") -> list[Milestone]:
    """Lista milestones do repositorio."""
    owner, repo = get_repo_info()

    result = run_gh_command([
        "api", f"repos/{owner}/{repo}/milestones",
        "-X", "GET",
        "-f", f"state={state}",
        "-f", "per_page=100"
    ])

    if result.returncode != 0:
        print(f"Erro ao listar milestones: {result.stderr}", file=sys.stderr)
        return []

    try:
        data = json.loads(result.stdout)
        return [
            Milestone(
                number=m["number"],
                title=m["title"],
                description=m.get("description", ""),
                state=m["state"],
                due_on=m.get("due_on"),
                open_issues=m["open_issues"],
                closed_issues=m["closed_issues"],
                html_url=m["html_url"]
            )
            for m in data
        ]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Erro ao processar resposta: {e}", file=sys.stderr)
        return []


def get_milestone_by_title(title: str) -> Optional[Milestone]:
    """Busca milestone por titulo."""
    milestones = list_milestones("all")
    for m in milestones:
        if m.title.lower() == title.lower():
            return m
    return None


def create_milestone(title: str, description: str = "", due_date: Optional[str] = None) -> Optional[Milestone]:
    """Cria um novo milestone."""
    owner, repo = get_repo_info()

    # Verificar se ja existe
    existing = get_milestone_by_title(title)
    if existing:
        print(f"Milestone '{title}' ja existe (#{existing.number})")
        return existing

    # Preparar payload
    payload = {
        "title": title,
        "description": description,
        "state": "open"
    }

    if due_date:
        # Converter para formato ISO
        try:
            dt = datetime.strptime(due_date, "%Y-%m-%d")
            payload["due_on"] = dt.strftime("%Y-%m-%dT23:59:59Z")
        except ValueError:
            print(f"Aviso: Data invalida '{due_date}', ignorando.", file=sys.stderr)

    # Criar milestone via API
    args = ["api", f"repos/{owner}/{repo}/milestones", "-X", "POST"]
    for key, value in payload.items():
        args.extend(["-f", f"{key}={value}"])

    result = run_gh_command(args)

    if result.returncode != 0:
        print(f"Erro ao criar milestone: {result.stderr}", file=sys.stderr)
        return None

    try:
        data = json.loads(result.stdout)
        milestone = Milestone(
            number=data["number"],
            title=data["title"],
            description=data.get("description", ""),
            state=data["state"],
            due_on=data.get("due_on"),
            open_issues=data["open_issues"],
            closed_issues=data["closed_issues"],
            html_url=data["html_url"]
        )
        print(f"Milestone criado: #{milestone.number} - {milestone.title}")
        print(f"URL: {milestone.html_url}")
        return milestone
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Erro ao processar resposta: {e}", file=sys.stderr)
        return None


def update_milestone(
    title: str,
    new_title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    state: Optional[str] = None
) -> bool:
    """Atualiza um milestone existente."""
    milestone = get_milestone_by_title(title)
    if not milestone:
        print(f"Milestone '{title}' nao encontrado.", file=sys.stderr)
        return False

    owner, repo = get_repo_info()

    # Preparar payload apenas com campos alterados
    args = ["api", f"repos/{owner}/{repo}/milestones/{milestone.number}", "-X", "PATCH"]

    if new_title:
        args.extend(["-f", f"title={new_title}"])
    if description is not None:
        args.extend(["-f", f"description={description}"])
    if state:
        args.extend(["-f", f"state={state}"])
    if due_date:
        try:
            dt = datetime.strptime(due_date, "%Y-%m-%d")
            args.extend(["-f", f"due_on={dt.strftime('%Y-%m-%dT23:59:59Z')}"])
        except ValueError:
            print(f"Aviso: Data invalida '{due_date}', ignorando.", file=sys.stderr)

    result = run_gh_command(args)

    if result.returncode != 0:
        print(f"Erro ao atualizar milestone: {result.stderr}", file=sys.stderr)
        return False

    print(f"Milestone #{milestone.number} atualizado com sucesso.")
    return True


def close_milestone(title: str) -> bool:
    """Fecha um milestone."""
    return update_milestone(title, state="closed")


def reopen_milestone(title: str) -> bool:
    """Reabre um milestone."""
    return update_milestone(title, state="open")


def print_milestones(milestones: list[Milestone]):
    """Imprime lista de milestones formatada."""
    if not milestones:
        print("Nenhum milestone encontrado.")
        return

    print(f"{'#':<4} {'Titulo':<25} {'Estado':<10} {'Progresso':<15} {'Due Date':<12}")
    print("-" * 70)

    for m in milestones:
        total = m.open_issues + m.closed_issues
        progress = f"{m.closed_issues}/{total}" if total > 0 else "0/0"
        due = m.due_on[:10] if m.due_on else "N/A"
        print(f"{m.number:<4} {m.title[:25]:<25} {m.state:<10} {progress:<15} {due:<12}")


def print_milestone_detail(milestone: Milestone):
    """Imprime detalhes de um milestone."""
    print(f"Milestone #{milestone.number}: {milestone.title}")
    print(f"  Estado: {milestone.state}")
    print(f"  Descricao: {milestone.description or 'N/A'}")
    print(f"  Due Date: {milestone.due_on[:10] if milestone.due_on else 'N/A'}")
    print(f"  Issues: {milestone.closed_issues} fechadas, {milestone.open_issues} abertas")
    print(f"  URL: {milestone.html_url}")


def main():
    parser = argparse.ArgumentParser(
        description="Gerencia milestones (sprints) no GitHub"
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Cria milestone")
    create_parser.add_argument("--title", "-t", required=True, help="Titulo do milestone")
    create_parser.add_argument("--description", "-d", default="", help="Descricao/goal")
    create_parser.add_argument("--due-date", help="Data limite (YYYY-MM-DD)")

    # close
    close_parser = subparsers.add_parser("close", help="Fecha milestone")
    close_parser.add_argument("--title", "-t", required=True, help="Titulo do milestone")

    # reopen
    reopen_parser = subparsers.add_parser("reopen", help="Reabre milestone")
    reopen_parser.add_argument("--title", "-t", required=True, help="Titulo do milestone")

    # list
    list_parser = subparsers.add_parser("list", help="Lista milestones")
    list_parser.add_argument("--state", "-s", default="all", choices=["open", "closed", "all"])

    # get
    get_parser = subparsers.add_parser("get", help="Obtem milestone por titulo")
    get_parser.add_argument("--title", "-t", required=True, help="Titulo do milestone")

    # update
    update_parser = subparsers.add_parser("update", help="Atualiza milestone")
    update_parser.add_argument("--title", "-t", required=True, help="Titulo atual")
    update_parser.add_argument("--new-title", help="Novo titulo")
    update_parser.add_argument("--description", "-d", help="Nova descricao")
    update_parser.add_argument("--due-date", help="Nova data limite")

    args = parser.parse_args()

    if args.action == "create":
        result = create_milestone(args.title, args.description, args.due_date)
        return 0 if result else 1

    elif args.action == "close":
        return 0 if close_milestone(args.title) else 1

    elif args.action == "reopen":
        return 0 if reopen_milestone(args.title) else 1

    elif args.action == "list":
        milestones = list_milestones(args.state)
        print_milestones(milestones)
        return 0

    elif args.action == "get":
        milestone = get_milestone_by_title(args.title)
        if milestone:
            print_milestone_detail(milestone)
            return 0
        else:
            print(f"Milestone '{args.title}' nao encontrado.")
            return 1

    elif args.action == "update":
        return 0 if update_milestone(
            args.title,
            new_title=args.new_title,
            description=args.description,
            due_date=args.due_date
        ) else 1


if __name__ == "__main__":
    sys.exit(main())
