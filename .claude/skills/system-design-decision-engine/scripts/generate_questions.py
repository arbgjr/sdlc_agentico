import json
import sys
from pathlib import Path

BASE = Path(".claude/skills/system-design-decision-engine")
PATTERNS_DIR = BASE / "data" / "patterns"

def load_pattern(pid: str):
    for p in PATTERNS_DIR.glob("*.json"):
        obj = json.loads(p.read_text(encoding="utf-8"))
        if obj.get("id") == pid:
            return obj
    return None

if __name__ == "__main__":
    ids = [a.strip() for a in " ".join(sys.argv[1:]).split(",") if a.strip()]
    if not ids:
        print(json.dumps({"error": "Uso: generate_questions.py <id1,id2,id3>"}, ensure_ascii=False))
        raise SystemExit(2)

    questions = []
    missing = []
    for pid in ids:
        pat = load_pattern(pid)
        if not pat:
            missing.append(pid)
            continue
        for q in pat.get("mandatory_questions", []):
            questions.append({"pattern": pid, "question": q})

    out = {"missing_patterns": missing, "mandatory_questions": questions}
    print(json.dumps(out, ensure_ascii=False, indent=2))
