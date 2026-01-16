#!/usr/bin/env python3
"""
GitHub Projects V2 Views Manager

Gerencia views (Kanban, Timeline, Table) do Project.

Uso:
    python project_views.py create-kanban --project-number 1
    python project_views.py create-timeline --project-number 1
    python project_views.py list --project-number 1
"""

import argparse
import json
import subprocess
import sys
from typing import Dict, Any, List


def gh_graphql(query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
    """Executa query GraphQL via gh CLI."""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    
    if variables:
        for key, value in variables.items():
            if isinstance(value, (dict, list)):
                cmd.extend(["-f", f"{key}={json.dumps(value)}"])
            else:
                cmd.extend(["-F", f"{key}={value}"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erro GraphQL: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_owner_info() -> Dict[str, str]:
    """Obtém informações do owner do repositório atual."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "owner,name"],
        capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def get_project_info(project_number: int) -> Dict[str, Any]:
    """Obtém informações do project."""
    owner_info = get_owner_info()
    owner = owner_info["owner"]["login"]
    
    query = """
    query($login: String!, $number: Int!) {
        user(login: $login) {
            projectV2(number: $number) {
                id
                title
                views(first: 20) {
                    nodes {
                        id
                        name
                        layout
                    }
                }
                fields(first: 20) {
                    nodes {
                        ... on ProjectV2SingleSelectField {
                            id
                            name
                            dataType
                        }
                        ... on ProjectV2Field {
                            id
                            name
                            dataType
                        }
                    }
                }
            }
        }
    }
    """
    
    result = gh_graphql(query, {"login": owner, "number": project_number})
    return result["data"]["user"]["projectV2"]


def list_views(project_number: int) -> List[Dict[str, Any]]:
    """Lista views do project."""
    project = get_project_info(project_number)
    views = project.get("views", {}).get("nodes", [])
    
    print(f"Views do project '{project['title']}':")
    print("-" * 40)
    
    for view in views:
        layout_emoji = {
            "BOARD_LAYOUT": "📋",
            "TABLE_LAYOUT": "📊",
            "ROADMAP_LAYOUT": "🗺️"
        }.get(view["layout"], "📄")
        
        print(f"  {layout_emoji} {view['name']} [{view['layout']}]")
        print(f"     ID: {view['id']}")
    
    return views


def create_view(project_number: int, name: str, layout: str) -> Dict[str, Any]:
    """Cria uma nova view no project."""
    project = get_project_info(project_number)
    project_id = project["id"]
    
    # Note: Creating views via GraphQL is limited
    # The mutation createProjectV2View may not be available in all cases
    
    query = """
    mutation($projectId: ID!, $name: String!, $layout: ProjectV2ViewLayout!) {
        createProjectV2View(input: {
            projectId: $projectId,
            name: $name,
            layout: $layout
        }) {
            projectV2View {
                id
                name
                layout
            }
        }
    }
    """
    
    try:
        result = gh_graphql(query, {
            "projectId": project_id,
            "name": name,
            "layout": layout
        })
        view = result["data"]["createProjectV2View"]["projectV2View"]
        print(f"View '{name}' criada com sucesso!")
        return view
    except Exception as e:
        print(f"Erro ao criar view: {e}", file=sys.stderr)
        print("Note: Criação de views via API pode ser limitada.", file=sys.stderr)
        print("Considere criar a view manualmente no GitHub.", file=sys.stderr)
        sys.exit(1)


def create_kanban_view(project_number: int) -> None:
    """Cria view Kanban agrupada por fase SDLC."""
    print(f"Criando view Kanban para project #{project_number}...")
    
    try:
        view = create_view(project_number, "SDLC Kanban", "BOARD_LAYOUT")
        print(f"View Kanban criada: {view['id']}")
        
        # Configure grouping by Phase field
        # Note: Configuring view settings requires additional mutations
        print("\n⚠️ Configure manualmente no GitHub:")
        print("  1. Abra o project no GitHub")
        print("  2. Vá para a view 'SDLC Kanban'")
        print("  3. Configure 'Group by' para o campo 'Phase'")
        
    except:
        print("\n📋 Para criar view Kanban manualmente:")
        print("  1. Acesse: https://github.com/users/{owner}/projects/{number}")
        print("  2. Clique em '+ New view'")
        print("  3. Selecione 'Board'")
        print("  4. Configure 'Group by: Phase'")


def create_timeline_view(project_number: int) -> None:
    """Cria view Timeline/Roadmap."""
    print(f"Criando view Timeline para project #{project_number}...")
    
    try:
        view = create_view(project_number, "SDLC Timeline", "ROADMAP_LAYOUT")
        print(f"View Timeline criada: {view['id']}")
        
    except:
        print("\n🗺️ Para criar view Timeline manualmente:")
        print("  1. Acesse: https://github.com/users/{owner}/projects/{number}")
        print("  2. Clique em '+ New view'")
        print("  3. Selecione 'Roadmap'")
        print("  4. Configure datas de início e fim")


def create_table_view(project_number: int) -> None:
    """Cria view Table."""
    print(f"Criando view Table para project #{project_number}...")
    
    try:
        view = create_view(project_number, "SDLC Table", "TABLE_LAYOUT")
        print(f"View Table criada: {view['id']}")
        
    except:
        print("\n📊 Para criar view Table manualmente:")
        print("  1. Acesse: https://github.com/users/{owner}/projects/{number}")
        print("  2. Clique em '+ New view'")
        print("  3. Selecione 'Table'")


def main():
    parser = argparse.ArgumentParser(description="GitHub Projects V2 Views Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # list
    list_parser = subparsers.add_parser("list", help="Listar views")
    list_parser.add_argument("--project-number", type=int, required=True)
    
    # create-kanban
    kanban_parser = subparsers.add_parser("create-kanban", help="Criar view Kanban")
    kanban_parser.add_argument("--project-number", type=int, required=True)
    
    # create-timeline
    timeline_parser = subparsers.add_parser("create-timeline", help="Criar view Timeline")
    timeline_parser.add_argument("--project-number", type=int, required=True)
    
    # create-table
    table_parser = subparsers.add_parser("create-table", help="Criar view Table")
    table_parser.add_argument("--project-number", type=int, required=True)
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_views(args.project_number)
    
    elif args.command == "create-kanban":
        create_kanban_view(args.project_number)
    
    elif args.command == "create-timeline":
        create_timeline_view(args.project_number)
    
    elif args.command == "create-table":
        create_table_view(args.project_number)


if __name__ == "__main__":
    main()
