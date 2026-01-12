import json
import re
from pathlib import Path

BASE = Path(".claude/skills/system-design-decision-engine")
CORPUS_DIR = BASE / "rag_corpus"
CHUNKS_PATH = BASE / "rag_chunks.json"

MAX_CHARS = 1600
OVERLAP = 200

def normalize_md(text: str) -> str:
    t = text.replace("\r\n", "\n")
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t

def chunk_text(text: str):
    chunks = []
    i = 0
    while i < len(text):
        j = min(i + MAX_CHARS, len(text))
        chunks.append(text[i:j])
        if j == len(text):
            break
        i = max(0, j - OVERLAP)
    return chunks

def main():
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    all_chunks = []

    for md in CORPUS_DIR.rglob("*.md"):
        raw = md.read_text(encoding="utf-8")
        norm = normalize_md(raw)
        parts = chunk_text(norm)
        for idx, part in enumerate(parts):
            all_chunks.append({
                "id": f"{md.as_posix()}::{idx}",
                "source_path": md.as_posix(),
                "text": part
            })

    CHUNKS_PATH.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Ingested {len(all_chunks)} chunks into {CHUNKS_PATH.as_posix()}")

if __name__ == "__main__":
    main()
