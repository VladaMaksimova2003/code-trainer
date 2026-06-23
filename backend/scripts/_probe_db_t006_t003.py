import json
import psycopg2

DB = dict(host="localhost", port=5433, dbname="code_trainer", user="code_trainer", password="change_me")
conn = psycopg2.connect(**DB)
cur = conn.cursor()
cur.execute("select id, title from task where id in (4,5,7,77) order by id")
print("tasks:", cur.fetchall())
for tid in (4, 7):
    cur.execute("select code_examples, test_cases from task where id=%s", (tid,))
    ce_raw, tc_raw = cur.fetchone()
    ce = json.loads(ce_raw) if isinstance(ce_raw, str) else ce_raw
    tc = json.loads(tc_raw) if isinstance(tc_raw, str) else tc_raw
    print(f"\n=== task id={tid} tests={len(tc)} ===")
    for lang in ["pascal", "python", "cpp", "csharp", "java"]:
        fixed = bool(ce.get(lang))
        buggy = bool(ce.get(f"buggy_{lang}"))
        hints = ce.get(f"hints_{lang}")
        if hints is None and isinstance(ce.get("hints"), dict):
            hints = ce["hints"].get(lang)
        ps = ce.get(f"post_solve_{lang}")
        if ps is None and isinstance(ce.get("post_solve_explanation"), dict):
            ps = ce["post_solve_explanation"].get(lang)
        ec = ce.get("expected_concepts", {})
        if isinstance(ec, dict):
            ec_lang = ec.get(lang, [])
        else:
            ec_lang = ec
        print(
            lang,
            "fixed", fixed,
            "buggy", buggy,
            "hints", len(hints or []),
            "post", bool(ps),
            "ec", len(ec_lang or []),
        )
    # show task_004 pattern for comparison
    if tid == 5:
        pass
cur.execute("select id, code_examples from task where id=5")
ce5 = json.loads(cur.fetchone()[1])
print("\n=== task_004 hints keys sample ===")
for k in sorted(ce5.keys()):
    if "hint" in k or "post" in k or "buggy" in k or k in LANGS if False else False:
        print(k)
for k in sorted(ce5.keys()):
    if "hint" in k or "post" in k or "buggy" in k or k in ("pascal","python"):
        v = ce5[k]
        if isinstance(v, str):
            print(k, "str", len(v))
        elif isinstance(v, list):
            print(k, "list", len(v))
        elif isinstance(v, dict):
            print(k, "dict", list(v.keys())[:5])
