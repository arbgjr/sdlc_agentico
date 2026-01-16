#!/usr/bin/env python3
"""
Operacoes de memoria para o SDLC.
v1.2.0 - Usa .agentic_sdlc como diretorio principal
"""
import yaml
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
import os

# Diretorio principal (v1.2.0+)
AGENTIC_SDLC_DIR = Path(".agentic_sdlc")
# Diretorio legado (para compatibilidade)
LEGACY_MEMORY_DIR = Path(".claude/memory")


def ensure_directories():
    """Garante que diretorios necessarios existem."""
    AGENTIC_SDLC_DIR.mkdir(exist_ok=True)
    (AGENTIC_SDLC_DIR / "projects").mkdir(exist_ok=True)
    (AGENTIC_SDLC_DIR / "corpus").mkdir(exist_ok=True)
    (AGENTIC_SDLC_DIR / "corpus" / "decisions").mkdir(exist_ok=True)
    (AGENTIC_SDLC_DIR / "corpus" / "learnings").mkdir(exist_ok=True)


def get_project_dir(project_id: str) -> Path:
    """Retorna diretorio do projeto."""
    project_dir = AGENTIC_SDLC_DIR / "projects" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def save_decision(
    project_id: str,
    decision_type: str,
    title: str,
    context: str,
    decision: str,
    consequences: List[str],
    phase: int,
    author: str = "system",
    status: str = "accepted"
) -> str:
    """
    Salva uma decisao (ADR).

    Returns:
        ID da decisao (ex: ADR-001)
    """
    ensure_directories()
    project_dir = get_project_dir(project_id)
    decisions_dir = project_dir / "decisions"
    decisions_dir.mkdir(exist_ok=True)

    # Gerar ID
    existing = list(decisions_dir.glob("adr-*.yml"))
    next_num = len(existing) + 1
    decision_id = f"ADR-{next_num:03d}"

    # Criar ADR
    adr = {
        "id": decision_id,
        "type": decision_type,
        "title": title,
        "status": status,
        "date": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "phase": phase,
        "author": author,
        "context": context,
        "decision": decision,
        "consequences": consequences
    }

    # Salvar
    adr_file = decisions_dir / f"{decision_id.lower()}.yml"
    with open(adr_file, "w") as f:
        yaml.dump(adr, f, default_flow_style=False, allow_unicode=True)

    return decision_id


def load_decision(project_id: str, decision_id: str) -> Optional[Dict]:
    """Carrega uma decisao por ID."""
    project_dir = get_project_dir(project_id)
    adr_file = project_dir / "decisions" / f"{decision_id.lower()}.yml"

    if not adr_file.exists():
        return None

    with open(adr_file) as f:
        return yaml.safe_load(f)


def search_decisions(
    project_id: str,
    phase: Optional[int] = None,
    decision_type: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict]:
    """Busca decisoes por filtros."""
    project_dir = get_project_dir(project_id)
    decisions_dir = project_dir / "decisions"

    if not decisions_dir.exists():
        return []

    results = []
    for adr_file in decisions_dir.glob("adr-*.yml"):
        with open(adr_file) as f:
            adr = yaml.safe_load(f)

        # Filtros
        if phase is not None and adr.get("phase") != phase:
            continue
        if decision_type and adr.get("type") != decision_type:
            continue
        if status and adr.get("status") != status:
            continue

        results.append(adr)

    return results


def save_learning(
    project_id: str,
    learning_type: str,
    title: str,
    insight: str,
    source: str,
    actions: List[str],
    tags: List[str]
) -> str:
    """
    Salva um learning (licao aprendida).

    Returns:
        ID do learning (ex: LEARNING-001)
    """
    ensure_directories()
    project_dir = get_project_dir(project_id)
    learnings_dir = project_dir / "learnings"
    learnings_dir.mkdir(exist_ok=True)

    # Gerar ID
    existing = list(learnings_dir.glob("learning-*.yml"))
    next_num = len(existing) + 1
    learning_id = f"LEARNING-{next_num:03d}"

    # Criar learning
    learning = {
        "id": learning_id,
        "type": learning_type,
        "title": title,
        "date": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": source,
        "insight": insight,
        "actions": actions,
        "tags": tags
    }

    # Salvar
    learning_file = learnings_dir / f"{learning_id.lower()}.yml"
    with open(learning_file, "w") as f:
        yaml.dump(learning, f, default_flow_style=False, allow_unicode=True)

    return learning_id


def search_learnings(
    project_id: str,
    learning_type: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Dict]:
    """Busca learnings por filtros."""
    project_dir = get_project_dir(project_id)
    learnings_dir = project_dir / "learnings"

    if not learnings_dir.exists():
        return []

    results = []
    for learning_file in learnings_dir.glob("learning-*.yml"):
        with open(learning_file) as f:
            learning = yaml.safe_load(f)

        # Filtros
        if learning_type and learning.get("type") != learning_type:
            continue
        if tags and not any(tag in learning.get("tags", []) for tag in tags):
            continue

        results.append(learning)

    return results


def get_project_manifest(project_id: str) -> Dict:
    """Retorna manifest do projeto."""
    project_dir = get_project_dir(project_id)
    manifest_file = project_dir / "manifest.yml"

    if not manifest_file.exists():
        # Criar manifest padrao
        manifest = {
            "project_id": project_id,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "current_phase": 0,
            "complexity": 2
        }
        with open(manifest_file, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True)
        return manifest

    with open(manifest_file) as f:
        return yaml.safe_load(f)


def update_project_manifest(project_id: str, updates: Dict):
    """Atualiza manifest do projeto."""
    manifest = get_project_manifest(project_id)
    manifest.update(updates)
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    project_dir = get_project_dir(project_id)
    manifest_file = project_dir / "manifest.yml"

    with open(manifest_file, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True)


if __name__ == "__main__":
    # Testes basicos
    ensure_directories()
    print("Diretorios criados com sucesso")

    # Teste de salvar decisao
    decision_id = save_decision(
        project_id="test",
        decision_type="architecture",
        title="Teste de decisao",
        context="Contexto de teste",
        decision="Decisao de teste",
        consequences=["Consequencia 1", "Consequencia 2"],
        phase=3
    )
    print(f"Decisao salva: {decision_id}")

    # Teste de carregar
    loaded = load_decision("test", decision_id)
    print(f"Decisao carregada: {loaded['title']}")
