import json
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "resources/curriculum/tc_display_registry.json"
data = json.loads(p.read_text(encoding="utf-8"))
langs = list(data.get("languages") or [])
missing = []
thin = []
for tc_id, card in sorted((data.get("tc_cards") or {}).items()):
    hints = card.get("hints_by_language") or {}
    for lang in langs:
        rows = hints.get(lang) or []
        if not rows:
            missing.append(f"{tc_id}/{lang}")
        elif len(rows) < 2:
            thin.append(f"{tc_id}/{lang}:{len(rows)}")
print("MISSING", len(missing))
for line in missing:
    print(line)
print("THIN", len(thin))
for line in thin:
    print(line)
