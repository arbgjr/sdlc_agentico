import json
import sys
from pathlib import Path

BASE = Path(".claude/skills/system-design-decision-engine")
CHUNKS_PATH = BASE / "rag_chunks.json"

def search(query: str, top_k: int = 5):
    q = query.lower().strip()
    items = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    scored = []
    for it in items:
        t = it["text"].lower()
        score = t.count(q)
        if score > 0:
            scored.append((score, it))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in scored[:top_k]]

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        print("Uso: rag_search.py <consulta>")
        raise SystemExit(2)

    if not CHUNKS_PATH.exists():
        print("Chunks nao encontrados. Rode: python .../scripts/rag_ingest.py")
        raise SystemExit(3)

    res = search(query, top_k=5)
    for it in res:
        print("-----")
        print(it["id"])
        print(it["text"][:900])
