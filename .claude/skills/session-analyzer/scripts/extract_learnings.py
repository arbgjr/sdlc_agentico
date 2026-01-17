#!/usr/bin/env python3
"""
Session Analyzer - Extrai learnings de sessoes do Claude Code

Este script analisa arquivos de sessao JSONL do Claude Code e extrai:
- Decisoes tomadas
- Bloqueios encontrados e resolucoes
- Learnings e padroes identificados

Uso:
    python extract_learnings.py [--session-id UUID] [--persist] [--project PATH]
"""

import json
import os
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import yaml


# Palavras-chave para deteccao
DECISION_KEYWORDS = [
    "decidi", "escolhi", "vou usar", "optei por",
    "a melhor opcao", "faz mais sentido", "vamos com",
    "prefiro", "recomendo", "sugiro", "decided", "chose",
    "will use", "going with", "best option"
]

BLOCKER_KEYWORDS = [
    "erro", "falhou", "problema", "nao funcionou",
    "bug", "issue", "bloqueado", "travado",
    "nao consegui", "impossivel", "error", "failed",
    "problem", "blocked", "stuck"
]

RESOLUTION_KEYWORDS = [
    "resolvido", "funcionou", "corrigido", "sucesso",
    "consegui", "pronto", "finalizado", "ok",
    "resolved", "fixed", "success", "working"
]

LEARNING_KEYWORDS = [
    "aprendi", "descobri", "percebi", "entendi",
    "importante notar", "lembre-se", "dica",
    "evite", "sempre", "nunca", "learned",
    "discovered", "realized", "note that", "remember"
]


def encode_project_path(path: str) -> str:
    """Converte path do projeto para formato encoded do Claude Code.

    Claude Code encodes paths by replacing both '/' and '_' with '-'.
    """
    return path.replace("/", "-").replace("_", "-")


def find_claude_sessions_dir() -> Path:
    """Encontra o diretorio de sessoes do Claude Code."""
    home = Path.home()
    claude_dir = home / ".claude" / "projects"
    return claude_dir


def find_project_sessions(project_path: str) -> Path:
    """Encontra o diretorio de sessoes para um projeto especifico."""
    sessions_dir = find_claude_sessions_dir()
    encoded = encode_project_path(project_path)
    return sessions_dir / encoded


def get_latest_session(sessions_path: Path) -> Optional[Path]:
    """Retorna o arquivo de sessao mais recente."""
    if not sessions_path.exists():
        return None

    session_files = list(sessions_path.glob("*.jsonl"))
    if not session_files:
        return None

    # Ordenar por data de modificacao (mais recente primeiro)
    session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return session_files[0]


def parse_session_file(session_path: Path) -> list[dict]:
    """Le e parseia um arquivo de sessao JSONL."""
    events = []
    with open(session_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def extract_text_content(event: dict) -> str:
    """Extrai conteudo textual de um evento."""
    content = ""

    if "content" in event:
        if isinstance(event["content"], str):
            content = event["content"]
        elif isinstance(event["content"], list):
            for item in event["content"]:
                if isinstance(item, dict) and "text" in item:
                    content += item["text"] + "\n"
                elif isinstance(item, str):
                    content += item + "\n"

    if "message" in event and isinstance(event["message"], dict):
        if "content" in event["message"]:
            msg_content = event["message"]["content"]
            if isinstance(msg_content, str):
                content += msg_content
            elif isinstance(msg_content, list):
                for item in msg_content:
                    if isinstance(item, dict) and "text" in item:
                        content += item["text"] + "\n"

    return content


def contains_keywords(text: str, keywords: list[str]) -> bool:
    """Verifica se o texto contem alguma das palavras-chave."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def extract_sentence_with_keyword(text: str, keywords: list[str]) -> Optional[str]:
    """Extrai a sentenca que contem a palavra-chave."""
    sentences = re.split(r'[.!?\n]', text)
    for sentence in sentences:
        if contains_keywords(sentence, keywords):
            return sentence.strip()
    return None


def analyze_session(events: list[dict]) -> dict:
    """Analisa eventos da sessao e extrai informacoes."""
    analysis = {
        "decisions": [],
        "blockers": [],
        "learnings": [],
        "tools_used": set(),
        "message_count": 0,
        "assistant_responses": 0
    }

    for event in events:
        event_type = event.get("type", "")

        # Contar mensagens
        if event_type in ["user", "assistant", "message"]:
            analysis["message_count"] += 1

        if event_type == "assistant":
            analysis["assistant_responses"] += 1

        # Registrar tools usadas
        if event_type == "tool_use":
            tool_name = event.get("name", "")
            if tool_name:
                analysis["tools_used"].add(tool_name)

        # Extrair conteudo textual
        text = extract_text_content(event)
        if not text:
            continue

        # Buscar decisoes
        if contains_keywords(text, DECISION_KEYWORDS):
            sentence = extract_sentence_with_keyword(text, DECISION_KEYWORDS)
            if sentence and len(sentence) > 20:
                analysis["decisions"].append({
                    "type": "technical",
                    "description": sentence[:500],
                    "source": event_type,
                    "confidence": "medium"
                })

        # Buscar bloqueios
        if contains_keywords(text, BLOCKER_KEYWORDS):
            sentence = extract_sentence_with_keyword(text, BLOCKER_KEYWORDS)
            if sentence and len(sentence) > 15:
                # Verificar se ha resolucao proxima
                resolution = None
                if contains_keywords(text, RESOLUTION_KEYWORDS):
                    resolution = extract_sentence_with_keyword(text, RESOLUTION_KEYWORDS)

                analysis["blockers"].append({
                    "description": sentence[:500],
                    "resolution": resolution[:500] if resolution else None,
                    "source": event_type
                })

        # Buscar learnings
        if contains_keywords(text, LEARNING_KEYWORDS):
            sentence = extract_sentence_with_keyword(text, LEARNING_KEYWORDS)
            if sentence and len(sentence) > 20:
                analysis["learnings"].append({
                    "type": "pattern",
                    "description": sentence[:500],
                    "source": event_type
                })

    # Converter set para list para serialização
    analysis["tools_used"] = list(analysis["tools_used"])

    return analysis


def generate_summary(session_path: Path, analysis: dict, project_path: str) -> dict:
    """Gera um resumo estruturado da analise."""
    session_id = session_path.stem
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return {
        "session_analysis": {
            "id": f"session-{datetime.now().strftime('%Y%m%d')}-{session_id[:8]}",
            "analyzed_at": now,
            "source_file": str(session_path),
            "project_path": project_path,
            "summary": {
                "messages_count": analysis["message_count"],
                "assistant_responses": analysis["assistant_responses"],
                "tools_used": analysis["tools_used"]
            },
            "decisions": analysis["decisions"][:10],  # Limitar a 10
            "blockers": analysis["blockers"][:5],    # Limitar a 5
            "learnings": analysis["learnings"][:10]  # Limitar a 10
        }
    }


def save_analysis(summary: dict, output_dir: Path):
    """Salva a analise em arquivo YAML."""
    output_dir.mkdir(parents=True, exist_ok=True)

    session_id = summary["session_analysis"]["id"]
    output_path = output_dir / f"{session_id}.yml"

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(summary, f, default_flow_style=False, allow_unicode=True, default_style="'")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Analisa sessoes do Claude Code")
    parser.add_argument("--session-id", help="UUID da sessao especifica")
    parser.add_argument("--persist", action="store_true", help="Salvar analise em disco")
    parser.add_argument("--project", help="Path do projeto", default=os.getcwd())
    parser.add_argument("--output-dir", help="Diretorio de output",
                        default=".agentic_sdlc/sessions")
    args = parser.parse_args()

    project_path = os.path.abspath(args.project)
    sessions_path = find_project_sessions(project_path)

    print(f"Projeto: {project_path}")
    print(f"Sessoes em: {sessions_path}")

    if args.session_id:
        session_file = sessions_path / f"{args.session_id}.jsonl"
        if not session_file.exists():
            print(f"Erro: Sessao {args.session_id} nao encontrada")
            return 1
    else:
        session_file = get_latest_session(sessions_path)
        if not session_file:
            print("Erro: Nenhuma sessao encontrada para este projeto")
            return 1

    print(f"Analisando: {session_file.name}")

    # Parsear e analisar
    events = parse_session_file(session_file)
    print(f"Eventos carregados: {len(events)}")

    analysis = analyze_session(events)
    summary = generate_summary(session_file, analysis, project_path)

    # Exibir resultados
    print("\n" + "=" * 50)
    print("RESUMO DA SESSAO")
    print("=" * 50)
    print(f"Mensagens: {analysis['message_count']}")
    print(f"Respostas do assistente: {analysis['assistant_responses']}")
    print(f"Tools usadas: {', '.join(analysis['tools_used']) or 'Nenhuma'}")

    if analysis["decisions"]:
        print(f"\nDecisoes encontradas: {len(analysis['decisions'])}")
        for i, dec in enumerate(analysis["decisions"][:3], 1):
            print(f"  {i}. {dec['description'][:100]}...")

    if analysis["blockers"]:
        print(f"\nBloqueios encontrados: {len(analysis['blockers'])}")
        for i, blk in enumerate(analysis["blockers"][:3], 1):
            print(f"  {i}. {blk['description'][:100]}...")

    if analysis["learnings"]:
        print(f"\nLearnings encontrados: {len(analysis['learnings'])}")
        for i, lrn in enumerate(analysis["learnings"][:3], 1):
            print(f"  {i}. {lrn['description'][:100]}...")

    # Persistir se solicitado
    if args.persist:
        output_dir = Path(args.output_dir)
        output_path = save_analysis(summary, output_dir)
        print(f"\nAnalise salva em: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
