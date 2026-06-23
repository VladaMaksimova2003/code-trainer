#!/usr/bin/env python3
import json
import urllib.request

API = "http://127.0.0.1:9000/tasks/4"
for qs in [
    "?learning_language=python&source_language=cpp",
    "?learning_language=python&source_language=python",
    "?learning_language=python",
    "?learning_language=pascal&source_language=python",
]:
    url = API + qs
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            d = json.load(r)
    except Exception as exc:
        print(url, "ERR", exc)
        continue
    t = d.get("transfer") or (d.get("curriculum") or {}).get("transfer") or {}
    p = (t.get("proactive") or {}).get("text") or t.get("reference_warning_ru") or ""
    hints = d.get("hints") or (d.get("curriculum") or {}).get("hints") or []
    print("===", qs)
    print("proactive:", p[:160].replace("\n", " | "))
    if len(hints) > 2:
        print("hint[2]:", hints[2])
    print()
