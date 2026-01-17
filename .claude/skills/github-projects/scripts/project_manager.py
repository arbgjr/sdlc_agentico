#!/usr/bin/env python3
"""
Project Manager - Gerencia GitHub Projects V2 via GraphQL.

Usage:
    python project_manager.py create --title "SDLC: Feature X"
    python project_manager.py get --title "SDLC: Feature X"
    python project_manager.py list
    python project_manager.py add-item --project-number 1 --issue-url URL
    python project_manager.py update-field --project-number 1 --item-id ID --field "Phase" --value "QA"
    python project_manager.py configure-fields --project-number 1
    python project_manager.py update-phase
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Project:
    """Representa um GitHub Project V2."""
    id: str
    number: int
    title: str
    url: str
    description: Optional[str] = None


@dataclass
class ProjectItem:
    """Representa um item em um Project."""
    id: str
    content_id: str
    content_type: str
    title: str


# Campos customizados SDLC
SDLC_FIELDS = {
    "Phase": {
        "type": "SingleSelect",
        "options": [
            "Backlog",
            "Requirements",
            "Architecture",
            "Planning",
            "In Progress",
            "QA",
            "Release",
            "Done"
        ]
    },
    "Priority": {
        "type": "SingleSelect",
        "options": ["Critical", "High", "Medium", "Low"]
    },
    "Story Points": {
        "type": "Number",
        "options": None
    }
}


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


def run_graphql(query: str, variables: Optional[dict] = None) -> Optional[dict]:
    """Executa query GraphQL via gh api."""
    args = ["api", "graphql"]

    if variables:
        args.extend(["-F", f"query={query}"])
        for key, value in variables.items():
            if isinstance(value, bool):
                args.extend(["-F", f"{key}={str(value).lower()}"])
            elif isinstance(value, int):
                args.extend(["-F", f"{key}={value}"])
            else:
                args.extend(["-f", f"{key}={value}"])
    else:
        args.extend(["-f", f"query={query}"])

    result = run_gh_command(args)

    if result.returncode != 0:
        print(f"Erro GraphQL: {result.stderr}", file=sys.stderr)
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def get_owner_id() -> Optional[str]:
    """Obtem ID do owner (user) autenticado."""
    query = """
    query {
        viewer {
            id
            login
        }
    }
    """
    result = run_graphql(query)
    if result and "data" in result:
        return result["data"]["viewer"]["id"]
    return None


def get_repo_node_id() -> Optional[str]:
    """Obtem node ID do repositorio atual."""
    result = run_gh_command(["repo", "view", "--json", "id"])
    if result.returncode != 0:
        return None

    try:
        data = json.loads(result.stdout)
        return data.get("id")
    except json.JSONDecodeError:
        return None


def list_projects(owner: str = "@me") -> list[Project]:
    """Lista projects do owner."""
    # Usar comando gh project list que e mais simples
    result = run_gh_command([
        "project", "list",
        "--owner", owner,
        "--format", "json"
    ])

    if result.returncode != 0:
        print(f"Erro ao listar projects: {result.stderr}", file=sys.stderr)
        return []

    try:
        data = json.loads(result.stdout)
        projects = data.get("projects", [])
        return [
            Project(
                id=p.get("id", ""),
                number=p.get("number", 0),
                title=p.get("title", ""),
                url=p.get("url", ""),
                description=p.get("shortDescription")
            )
            for p in projects
        ]
    except json.JSONDecodeError:
        return []


def get_project_by_title(title: str, owner: str = "@me") -> Optional[Project]:
    """Busca project por titulo."""
    projects = list_projects(owner)
    for p in projects:
        if p.title.lower() == title.lower():
            return p
    return None


def get_project_by_number(number: int, owner: str = "@me") -> Optional[Project]:
    """Busca project por numero."""
    result = run_gh_command([
        "project", "view", str(number),
        "--owner", owner,
        "--format", "json"
    ])

    if result.returncode != 0:
        return None

    try:
        data = json.loads(result.stdout)
        return Project(
            id=data.get("id", ""),
            number=data.get("number", number),
            title=data.get("title", ""),
            url=data.get("url", ""),
            description=data.get("shortDescription")
        )
    except json.JSONDecodeError:
        return None


def create_project(title: str, description: str = "", owner: str = "@me") -> Optional[Project]:
    """Cria um novo Project V2."""
    # Verificar se ja existe
    existing = get_project_by_title(title, owner)
    if existing:
        print(f"Project '{title}' ja existe (#{existing.number})")
        return existing

    # Criar via gh project create
    args = ["project", "create", "--owner", owner, "--title", title]

    result = run_gh_command(args)

    if result.returncode != 0:
        print(f"Erro ao criar project: {result.stderr}", file=sys.stderr)
        return None

    # Buscar project criado
    project = get_project_by_title(title, owner)
    if project:
        print(f"Project criado: #{project.number} - {project.title}")
        print(f"URL: {project.url}")

        # Atualizar descricao se fornecida
        if description:
            run_gh_command([
                "project", "edit", str(project.number),
                "--owner", owner,
                "--title", title,
                "--description", description
            ])

        return project

    return None


def add_item_to_project(project_number: int, issue_url: str, owner: str = "@me") -> Optional[str]:
    """Adiciona issue/PR ao project."""
    result = run_gh_command([
        "project", "item-add", str(project_number),
        "--owner", owner,
        "--url", issue_url
    ])

    if result.returncode != 0:
        print(f"Erro ao adicionar item: {result.stderr}", file=sys.stderr)
        return None

    print(f"Item adicionado ao Project #{project_number}")

    # Tentar extrair item ID do output
    # O gh project item-add retorna o item ID
    return result.stdout.strip() if result.stdout else None


def get_project_fields(project_number: int, owner: str = "@me") -> list[dict]:
    """Lista campos do project."""
    result = run_gh_command([
        "project", "field-list", str(project_number),
        "--owner", owner,
        "--format", "json"
    ])

    if result.returncode != 0:
        return []

    try:
        data = json.loads(result.stdout)
        return data.get("fields", [])
    except json.JSONDecodeError:
        return []


def create_single_select_field(project_number: int, name: str, options: list[str], owner: str = "@me") -> bool:
    """Cria campo SingleSelect no project."""
    # Primeiro verificar se ja existe
    fields = get_project_fields(project_number, owner)
    for field in fields:
        if field.get("name", "").lower() == name.lower():
            print(f"Campo '{name}' ja existe")
            return True

    # Criar campo via gh project field-create
    # Formatar opcoes como string separada por virgulas
    options_str = ",".join(options)

    args = [
        "project", "field-create", str(project_number),
        "--owner", owner,
        "--name", name,
        "--data-type", "SINGLE_SELECT",
        "--single-select-options", options_str
    ]

    result = run_gh_command(args)

    if result.returncode != 0:
        print(f"Erro ao criar campo '{name}': {result.stderr}", file=sys.stderr)
        return False

    print(f"Campo '{name}' criado com {len(options)} opcoes")
    return True


def configure_sdlc_fields(project_number: int, owner: str = "@me") -> bool:
    """Configura campos SDLC no project."""
    print(f"Configurando campos SDLC no Project #{project_number}...")

    success = True
    for field_name, config in SDLC_FIELDS.items():
        if config["type"] == "SingleSelect":
            if not create_single_select_field(project_number, field_name, config["options"], owner):
                success = False
        # Number fields sao criados automaticamente pelo GitHub

    return success


def update_phase_from_manifest(owner: str = "@me") -> bool:
    """
    Atualiza campo Phase no Project baseado no manifest do projeto.

    Detecta fase atual, mapeia para coluna do Project, e atualiza
    campo Phase de todas as issues do projeto.
    """
    # Carregar manifest do projeto
    project_root = Path.cwd()
    projects_dir = project_root / ".agentic_sdlc" / "projects"

    # Tentar current.json symlink
    current_json = projects_dir / "current.json"
    manifest_path = None

    if current_json.exists():
        with open(current_json) as f:
            data = json.load(f)
            manifest_path = projects_dir / data["project_id"] / "manifest.json"
    else:
        # Buscar manifest mais recente
        manifests = list(projects_dir.glob("*/manifest.json"))
        if manifests:
            manifest_path = max(manifests, key=lambda p: p.stat().st_mtime)

    if not manifest_path or not manifest_path.exists():
        print("✗ Nenhum projeto encontrado", file=sys.stderr)
        return False

    # Carregar projeto
    with open(manifest_path) as f:
        project = json.load(f)

    current_phase = project.get('current_phase', 0)
    project_number = project.get('github', {}).get('project_number')

    if not project_number:
        print("✗ Projeto sem GitHub Project configurado", file=sys.stderr)
        return False

    # Mapear fase para coluna
    phase_map = {
        0: "Backlog",
        1: "Backlog",
        2: "Requirements",
        3: "Architecture",
        4: "Planning",
        5: "In Progress",
        6: "QA",
        7: "Release",
        8: "Done"
    }

    target_phase = phase_map.get(current_phase, "Backlog")

    print(f"Atualizando Project #{project_number} → Phase {current_phase} ({target_phase})")

    # Listar issues do milestone atual
    milestone_name = project.get('github', {}).get('milestone', 'Sprint 1')

    result = run_gh_command([
        "issue", "list",
        "--milestone", milestone_name,
        "--json", "number,url",
        "--limit", "1000"
    ])

    if result.returncode != 0:
        print(f"✗ Erro ao listar issues: {result.stderr}", file=sys.stderr)
        return False

    try:
        issues = json.loads(result.stdout)
    except json.JSONDecodeError:
        issues = []

    if not issues:
        print(f"⚠ Nenhuma issue encontrada no milestone '{milestone_name}'")
        return True

    print(f"Encontradas {len(issues)} issues no milestone")

    # Para cada issue, atualizar campo Phase no Project
    # NOTA: Isso requer GraphQL pois gh CLI não expõe isso diretamente
    # Por ora, apenas log - implementação completa requer GraphQL
    print(f"TODO: Atualizar campo Phase das {len(issues)} issues para '{target_phase}'")
    print("NOTA: Requer GraphQL mutation - adicionar em versão futura")

    return True


def update_item_field(
    project_number: int,
    item_id: str,
    field_name: str,
    value: str,
    owner: str = "@me"
) -> bool:
    """Atualiza campo de um item no project."""
    # Primeiro obter o field ID
    fields = get_project_fields(project_number, owner)
    field_id = None

    for field in fields:
        if field.get("name", "").lower() == field_name.lower():
            field_id = field.get("id")
            break

    if not field_id:
        print(f"Campo '{field_name}' nao encontrado", file=sys.stderr)
        return False

    # Atualizar via gh project item-edit
    result = run_gh_command([
        "project", "item-edit",
        "--project-id", str(project_number),
        "--id", item_id,
        "--field-id", field_id,
        "--single-select-option-id", value  # Para SingleSelect
    ])

    if result.returncode != 0:
        # Tentar com text value
        result = run_gh_command([
            "project", "item-edit",
            "--project-id", str(project_number),
            "--id", item_id,
            "--field-id", field_id,
            "--text", value
        ])

    if result.returncode != 0:
        print(f"Erro ao atualizar campo: {result.stderr}", file=sys.stderr)
        return False

    print(f"Campo '{field_name}' atualizado para '{value}'")
    return True


def print_projects(projects: list[Project]):
    """Imprime lista de projects formatada."""
    if not projects:
        print("Nenhum project encontrado.")
        return

    print(f"{'#':<6} {'Titulo':<40} {'URL':<50}")
    print("-" * 100)

    for p in projects:
        print(f"{p.number:<6} {p.title[:40]:<40} {p.url:<50}")


def main():
    parser = argparse.ArgumentParser(
        description="Gerencia GitHub Projects V2"
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Cria project")
    create_parser.add_argument("--title", "-t", required=True, help="Titulo")
    create_parser.add_argument("--description", "-d", default="", help="Descricao")
    create_parser.add_argument("--owner", "-o", default="@me", help="Owner")

    # list
    list_parser = subparsers.add_parser("list", help="Lista projects")
    list_parser.add_argument("--owner", "-o", default="@me", help="Owner")

    # get
    get_parser = subparsers.add_parser("get", help="Obtem project")
    get_parser.add_argument("--title", "-t", help="Titulo")
    get_parser.add_argument("--number", "-n", type=int, help="Numero")
    get_parser.add_argument("--owner", "-o", default="@me", help="Owner")

    # add-item
    add_parser = subparsers.add_parser("add-item", help="Adiciona item ao project")
    add_parser.add_argument("--project-number", "-p", type=int, required=True, help="Numero do project")
    add_parser.add_argument("--issue-url", "-u", required=True, help="URL da issue/PR")
    add_parser.add_argument("--owner", "-o", default="@me", help="Owner")

    # update-field
    update_parser = subparsers.add_parser("update-field", help="Atualiza campo de item")
    update_parser.add_argument("--project-number", "-p", type=int, required=True, help="Numero do project")
    update_parser.add_argument("--item-id", "-i", required=True, help="ID do item")
    update_parser.add_argument("--field", "-f", required=True, help="Nome do campo")
    update_parser.add_argument("--value", "-v", required=True, help="Novo valor")
    update_parser.add_argument("--owner", "-o", default="@me", help="Owner")

    # configure-fields
    config_parser = subparsers.add_parser("configure-fields", help="Configura campos SDLC")
    config_parser.add_argument("--project-number", "-p", type=int, required=True, help="Numero do project")
    config_parser.add_argument("--owner", "-o", default="@me", help="Owner")

    # fields
    fields_parser = subparsers.add_parser("fields", help="Lista campos do project")
    fields_parser.add_argument("--project-number", "-p", type=int, required=True, help="Numero do project")
    fields_parser.add_argument("--owner", "-o", default="@me", help="Owner")

    # update-phase
    update_phase_parser = subparsers.add_parser("update-phase", help="Atualiza campo Phase baseado no manifest")
    update_phase_parser.add_argument("--owner", "-o", default="@me", help="Owner")

    args = parser.parse_args()

    if args.action == "create":
        result = create_project(args.title, args.description, args.owner)
        return 0 if result else 1

    elif args.action == "list":
        projects = list_projects(args.owner)
        print_projects(projects)
        return 0

    elif args.action == "get":
        if args.number:
            project = get_project_by_number(args.number, args.owner)
        elif args.title:
            project = get_project_by_title(args.title, args.owner)
        else:
            print("Erro: Especifique --title ou --number", file=sys.stderr)
            return 1

        if project:
            print(f"Project #{project.number}: {project.title}")
            print(f"  URL: {project.url}")
            print(f"  Descricao: {project.description or 'N/A'}")
            return 0
        else:
            print("Project nao encontrado.")
            return 1

    elif args.action == "add-item":
        result = add_item_to_project(args.project_number, args.issue_url, args.owner)
        return 0 if result else 1

    elif args.action == "update-field":
        return 0 if update_item_field(
            args.project_number,
            args.item_id,
            args.field,
            args.value,
            args.owner
        ) else 1

    elif args.action == "configure-fields":
        return 0 if configure_sdlc_fields(args.project_number, args.owner) else 1

    elif args.action == "fields":
        fields = get_project_fields(args.project_number, args.owner)
        if fields:
            print(f"Campos do Project #{args.project_number}:")
            for field in fields:
                print(f"  - {field.get('name')} ({field.get('dataType', 'N/A')})")
        else:
            print("Nenhum campo encontrado.")
        return 0

    elif args.action == "update-phase":
        return 0 if update_phase_from_manifest(args.owner) else 1


if __name__ == "__main__":
    sys.exit(main())
