import json
from pathlib import Path
d=json.loads(Path("_model_stress_out.json").read_text(encoding="utf-8"))
mp=d["multi_pitfall_patterns"]
lines = [f"multi count {len(mp)}"]
for row in mp:
    ex=row.get("explicit_pitfall")
    m=row["matching_pitfalls"]
    types=sorted({x["transfer_type"] for x in m})
    pids=[x["pitfall_id"] for x in m]
    if len(set(pids))>=2:
        lines.append(f"{row['pattern']} explicit={ex} pitfalls={pids} types={types}")
lines.append("--- ATCC no pitfall ---")
for row in d["no_pitfall_non_tcc_signals"]:
    if row.get("action_default_tt")=="ATCC":
        lines.append(f"{row['pattern']} {row['title']}")
lines.append(f"ATCC no pitfall count: {sum(1 for r in d['no_pitfall_non_tcc_signals'] if r.get('action_default_tt')=='ATCC')}")
lines.append(f"FCC no pitfall count: {sum(1 for r in d['no_pitfall_non_tcc_signals'] if r.get('action_default_tt')=='FCC')}")
Path("_model_stress_summary.txt").write_text("\n".join(lines), encoding="utf-8")
