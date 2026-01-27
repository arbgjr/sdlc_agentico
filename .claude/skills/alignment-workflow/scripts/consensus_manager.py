#!/usr/bin/env python3
"""
Gerenciador de consenso para ODRs.
Implementa o workflow de coleta de inputs e aprovações.
"""
import yaml
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any


def get_project_id() -> str:
    """Obtém ID do projeto atual."""
    current_file = Path(".agentic_sdlc/.current-project")
    if current_file.exists():
        return current_file.read_text().strip()
    return "default"


def get_odr_path(odr_id: str, project_id: str = None) -> Path:
    """Retorna caminho do arquivo ODR."""
    if project_id is None:
        project_id = get_project_id()
    
    # Normalizar ID
    odr_num = odr_id.replace("ODR-", "").replace("odr-", "")
    return Path(f".agentic_sdlc/projects/{project_id}/decisions/odr-{odr_num}.yml")


def load_odr(odr_id: str, project_id: str = None) -> Optional[Dict]:
    """Carrega um ODR por ID."""
    odr_path = get_odr_path(odr_id, project_id)
    
    if not odr_path.exists():
        print(f"ODR não encontrado: {odr_id}")
        return None
    
    with open(odr_path) as f:
        data = yaml.safe_load(f)
    
    return data.get("odr", data)


def save_odr(odr: Dict, project_id: str = None):
    """Salva um ODR."""
    odr_path = get_odr_path(odr["id"], project_id)
    odr_path.parent.mkdir(parents=True, exist_ok=True)
    
    odr["updated_at"] = datetime.now().isoformat()
    
    with open(odr_path, "w") as f:
        yaml.dump({"odr": odr}, f, default_flow_style=False, allow_unicode=True, default_style="'")


def transition_odr(odr_id: str, new_status: str, project_id: str = None) -> bool:
    """
    Transiciona ODR para novo status.
    
    Transições válidas:
    - draft -> pending_input
    - pending_input -> pending_approval
    - pending_approval -> approved | rejected
    - any -> superseded
    """
    valid_transitions = {
        "draft": ["pending_input", "superseded"],
        "pending_input": ["pending_approval", "draft", "superseded"],
        "pending_approval": ["approved", "rejected", "pending_input", "superseded"],
        "approved": ["superseded"],
        "rejected": ["draft", "superseded"],
        "superseded": []
    }
    
    odr = load_odr(odr_id, project_id)
    if not odr:
        return False
    
    current = odr.get("status", "draft")
    
    if new_status not in valid_transitions.get(current, []):
        print(f"Transição inválida: {current} -> {new_status}")
        print(f"Transições válidas: {valid_transitions.get(current, [])}")
        return False
    
    odr["status"] = new_status
    
    # Adicionar ao histórico
    if "history" not in odr:
        odr["history"] = []
    
    odr["history"].append({
        "timestamp": datetime.now().isoformat(),
        "action": f"status_changed_to_{new_status}",
        "details": f"Transição de {current} para {new_status}"
    })
    
    save_odr(odr, project_id)
    print(f"✓ ODR {odr_id}: {current} -> {new_status}")
    return True


def add_input(odr_id: str, stakeholder: str, input_text: str, project_id: str = None) -> bool:
    """Registra input de um stakeholder."""
    odr = load_odr(odr_id, project_id)
    if not odr:
        return False
    
    # Encontrar stakeholder na lista de consultados
    consulted = odr.get("stakeholders", {}).get("consulted", [])
    found = False
    
    for c in consulted:
        if c.get("name", "").lower() == stakeholder.lower():
            c["input_status"] = "received"
            c["input"] = input_text
            c["received_at"] = datetime.now().isoformat()
            found = True
            break
    
    if not found:
        # Adicionar novo stakeholder
        consulted.append({
            "name": stakeholder,
            "role": "Contributor",
            "input_status": "received",
            "input": input_text,
            "received_at": datetime.now().isoformat()
        })
    
    odr["stakeholders"]["consulted"] = consulted
    
    # Adicionar ao histórico
    if "history" not in odr:
        odr["history"] = []
    
    odr["history"].append({
        "timestamp": datetime.now().isoformat(),
        "action": "input_received",
        "by": stakeholder,
        "details": input_text[:100] + "..." if len(input_text) > 100 else input_text
    })
    
    save_odr(odr, project_id)
    print(f"✓ Input de {stakeholder} registrado em {odr_id}")
    
    # Verificar se todos inputs foram coletados
    pending = [c for c in consulted if c.get("input_status") == "pending"]
    if not pending and odr.get("status") == "pending_input":
        print(f"ℹ Todos inputs coletados. Use 'transition --to pending_approval' para prosseguir.")
    
    return True


def approve_odr(odr_id: str, approver: str, approved: bool, comment: str = "", project_id: str = None) -> bool:
    """Registra aprovação/rejeição de ODR."""
    odr = load_odr(odr_id, project_id)
    if not odr:
        return False
    
    if odr.get("status") != "pending_approval":
        print(f"ODR não está aguardando aprovação. Status atual: {odr.get('status')}")
        return False
    
    # Registrar aprovação
    if "approvals" not in odr:
        odr["approvals"] = []
    
    odr["approvals"].append({
        "stakeholder": approver,
        "approved": approved,
        "approved_at": datetime.now().isoformat(),
        "comments": comment
    })
    
    # Atualizar status
    new_status = "approved" if approved else "rejected"
    odr["status"] = new_status
    
    # Adicionar ao histórico
    if "history" not in odr:
        odr["history"] = []
    
    odr["history"].append({
        "timestamp": datetime.now().isoformat(),
        "action": new_status,
        "by": approver,
        "details": comment
    })
    
    # Preencher decisão se aprovado
    if approved and not odr.get("decision", {}).get("description"):
        print("ℹ ODR aprovado. Considere atualizar o campo 'decision' com detalhes.")
    
    save_odr(odr, project_id)
    print(f"✓ ODR {odr_id} {new_status} por {approver}")
    return True


def check_timeouts(project_id: str = None, timeout_hours: int = 48) -> List[Dict]:
    """Verifica ODRs com inputs pendentes em timeout."""
    if project_id is None:
        project_id = get_project_id()
    
    decisions_dir = Path(f".agentic_sdlc/projects/{project_id}/decisions")
    timeouts = []
    
    for odr_file in decisions_dir.glob("odr-*.yml"):
        with open(odr_file) as f:
            data = yaml.safe_load(f)
        
        odr = data.get("odr", data)
        
        if odr.get("status") != "pending_input":
            continue
        
        consulted = odr.get("stakeholders", {}).get("consulted", [])
        
        for c in consulted:
            if c.get("input_status") != "pending":
                continue
            
            requested_at = c.get("requested_at")
            if not requested_at:
                continue
            
            req_dt = datetime.fromisoformat(requested_at.replace("Z", "+00:00"))
            if datetime.now().astimezone() - req_dt > timedelta(hours=timeout_hours):
                timeouts.append({
                    "odr_id": odr["id"],
                    "odr_title": odr["title"],
                    "stakeholder": c["name"],
                    "requested_at": requested_at,
                    "hours_overdue": int((datetime.now().astimezone() - req_dt).total_seconds() / 3600)
                })
    
    return timeouts


def status_odr(odr_id: str, project_id: str = None):
    """Exibe status detalhado de um ODR."""
    odr = load_odr(odr_id, project_id)
    if not odr:
        return
    
    print(f"\n{'='*60}")
    print(f"ODR: {odr['id']} - {odr['title']}")
    print(f"{'='*60}")
    print(f"Status: {odr.get('status', 'unknown')}")
    print(f"Categoria: {odr.get('metadata', {}).get('category', 'N/A')}")
    print(f"Impacto: {odr.get('metadata', {}).get('impact_level', 'N/A')}")
    print(f"Criado: {odr.get('created_at', 'N/A')[:10]}")
    
    if odr.get("deadline"):
        print(f"Deadline: {odr['deadline'][:10]}")
    
    print(f"\n--- Stakeholders ---")
    dm = odr.get("stakeholders", {}).get("decision_maker", {})
    print(f"Decision Maker: {dm.get('name', 'N/A')} ({dm.get('role', '')})")
    
    consulted = odr.get("stakeholders", {}).get("consulted", [])
    if consulted:
        print(f"\nConsultados ({len(consulted)}):")
        for c in consulted:
            status_icon = "✓" if c.get("input_status") == "received" else "⏳"
            print(f"  {status_icon} {c.get('name')} ({c.get('input_status', 'pending')})")
    
    if odr.get("approvals"):
        print(f"\n--- Aprovações ---")
        for a in odr["approvals"]:
            icon = "✓" if a.get("approved") else "✗"
            print(f"  {icon} {a.get('stakeholder')}: {a.get('approved_at', '')[:10]}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="Gerenciador de consenso para ODRs")
    subparsers = parser.add_subparsers(dest="command", help="Comandos")
    
    # transition
    trans = subparsers.add_parser("transition", help="Transicionar ODR")
    trans.add_argument("--odr", required=True, help="ID do ODR")
    trans.add_argument("--to", required=True, help="Novo status")
    trans.add_argument("--project", help="ID do projeto")
    
    # add-input
    inp = subparsers.add_parser("add-input", help="Adicionar input")
    inp.add_argument("--odr", required=True, help="ID do ODR")
    inp.add_argument("--stakeholder", required=True, help="Nome do stakeholder")
    inp.add_argument("--input", required=True, help="Texto do input")
    inp.add_argument("--project", help="ID do projeto")
    
    # approve
    appr = subparsers.add_parser("approve", help="Aprovar ODR")
    appr.add_argument("--odr", required=True, help="ID do ODR")
    appr.add_argument("--approver", required=True, help="Nome do aprovador")
    appr.add_argument("--comment", default="", help="Comentário")
    appr.add_argument("--project", help="ID do projeto")
    
    # reject
    rej = subparsers.add_parser("reject", help="Rejeitar ODR")
    rej.add_argument("--odr", required=True, help="ID do ODR")
    rej.add_argument("--approver", required=True, help="Nome do rejeitador")
    rej.add_argument("--comment", default="", help="Motivo")
    rej.add_argument("--project", help="ID do projeto")
    
    # check-timeouts
    timeout = subparsers.add_parser("check-timeouts", help="Verificar timeouts")
    timeout.add_argument("--project", help="ID do projeto")
    timeout.add_argument("--hours", type=int, default=48, help="Horas para timeout")
    
    # status
    stat = subparsers.add_parser("status", help="Ver status do ODR")
    stat.add_argument("--odr", required=True, help="ID do ODR")
    stat.add_argument("--project", help="ID do projeto")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "transition":
        transition_odr(args.odr, args.to, args.project)
    
    elif args.command == "add-input":
        add_input(args.odr, args.stakeholder, args.input, args.project)
    
    elif args.command == "approve":
        approve_odr(args.odr, args.approver, True, args.comment, args.project)
    
    elif args.command == "reject":
        approve_odr(args.odr, args.approver, False, args.comment, args.project)
    
    elif args.command == "check-timeouts":
        timeouts = check_timeouts(args.project, args.hours)
        if timeouts:
            print(f"\n⚠️ {len(timeouts)} inputs em timeout:\n")
            for t in timeouts:
                print(f"  - {t['odr_id']}: {t['stakeholder']} ({t['hours_overdue']}h overdue)")
        else:
            print("✓ Nenhum input em timeout")
    
    elif args.command == "status":
        status_odr(args.odr, args.project)


if __name__ == "__main__":
    main()
