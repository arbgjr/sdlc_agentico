import json
import sys
from pathlib import Path

BASE = Path(".claude/skills/system-design-decision-engine")
PATTERNS_DIR = BASE / "data" / "patterns"

def load_patterns():
    patterns = []
    for p in PATTERNS_DIR.glob("*.json"):
        patterns.append(json.loads(p.read_text(encoding="utf-8")))
    return patterns

def detect(text: str, patterns):
    t = (text or "").lower()
    activated = []
    for pat in patterns:
        hits = []
        for sig in pat.get("signals", []):
            s = (sig or "").lower()
            if s and s in t:
                hits.append(sig)
        if hits:
            activated.append({
                "id": pat["id"],
                "hits": hits,
                "score": len(hits)
            })
    activated.sort(key=lambda x: x["score"], reverse=True)
    return activated

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]).strip()
    if not text:
        print(json.dumps({"error": "Uso: detect_patterns.py <texto do problema>"}, ensure_ascii=False))
        raise SystemExit(2)

    pats = load_patterns()
    res = detect(text, pats)
    print(json.dumps({"activated_patterns": res}, ensure_ascii=False, indent=2))
