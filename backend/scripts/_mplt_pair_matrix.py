import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.content.algo_syntax_showcase_meta import transfer_meta_for_language_pair
from application.curriculum.display.transfer_pitfall_detector import detect_transfer_pitfalls
from application.curriculum.display.algorithm_debug_detector import detect_algorithm_debug

LANGS = ["pascal", "python", "cpp", "csharp", "java"]
PAIRS = [(s, t) for s in LANGS for t in LANGS if s != t]

FCC_SAMPLES = {
    "pascal": "var a,b:integer; begin readln(a,b); writeln(a / b); end.",
    "cpp": "#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a/b;}",
    "csharp": "using System; class P{ static void Main(){ int a=int.Parse(Console.ReadLine()); int b=int.Parse(Console.ReadLine()); Console.WriteLine(a/b);}}",
    "java": "import java.util.*; class M{ public static void main(String[]a){ Scanner s=new Scanner(System.in); int x=s.nextInt(),y=s.nextInt(); System.out.println(x/y);}}",
    "python": "a=int(input()); b=int(input()); print(a/b)",
}

AFCC_SAMPLES = {
    "pascal": "var a,b,c:integer; begin readln(a); readln(b); readln(c); writeln(a); end.",
    "java": "import java.util.*; class M{ public static void main(String[]a){ Scanner s=new Scanner(System.in); System.out.println(s.nextInt());}}",
    "cpp": "#include <iostream>\nint main(){int a,b,c; std::cin>>a>>b>>c; std::cout<<a;}",
    "csharp": "using System; class P{ static void Main(){ Console.WriteLine(int.Parse(Console.ReadLine()));}}",
    "python": "a=int(input()); print(a)",
}

DEBUG_SAMPLES = {
    "filter_positive": {
        "pascal": "if amount >= 0 then count := count + 1;",
        "python": "if amount >= 0: count += 1",
        "cpp": "if(amount>=0) count++;",
        "csharp": "if(amount>=0) count++;",
        "java": "if(amount>=0) count++;",
    },
    "threshold_count": {
        "pascal": "if x > 50 then count := count + 1;",
        "python": "if x > 50: count += 1",
        "cpp": "if(x>50) count++;",
        "csharp": "if(x>50) count++;",
        "java": "if(x>50) count++;",
    },
}


def matrix_task006():
    rows = []
    for s, t in PAIRS:
        tm = transfer_meta_for_language_pair("task_006", source_language=s, target_language=t)
        code = FCC_SAMPLES.get(t, "")
        hits = detect_transfer_pitfalls(
            pitfall_id="integer_division",
            transfer_type="FCC",
            source_language=s,
            target_language=t,
            code=code,
            test_results=[{"status": "FAILED"}],
        )
        proactive = (tm.get("proactive") or {}).get("text") or ""
        reactive = hits[0].get("text", "") if hits else ""
        rows.append(
            {
                "pair": f"{s}->{t}",
                "transfer_type": tm.get("transfer_type"),
                "proactive": bool(proactive),
                "proactive_has_code": bool("div" in proactive or "//" in proactive),
                "reactive": bool(reactive),
                "reactive_has_code": bool("div" in reactive or "total" in reactive or "/" in reactive),
            }
        )
    return rows


def matrix_task003():
    rows = []
    for s, t in PAIRS:
        tm = transfer_meta_for_language_pair("task_003", source_language=s, target_language=t)
        code = AFCC_SAMPLES.get(t, "")
        hits = detect_transfer_pitfalls(
            pitfall_id="input_line_model",
            transfer_type="AFCC",
            source_language=s,
            target_language=t,
            code=code,
            test_results=[{"status": "FAILED"}],
        )
        proactive = (tm.get("proactive") or {}).get("text") or ""
        reactive = hits[0].get("text", "") if hits else ""
        rows.append(
            {
                "pair": f"{s}->{t}",
                "transfer_type": tm.get("transfer_type"),
                "proactive": bool(proactive),
                "proactive_has_code": len(proactive) > 60,
                "reactive": bool(reactive),
                "reactive_has_code": bool("readln" in reactive or "cin" in reactive or "Scanner" in reactive),
            }
        )
    return rows


def matrix_debug(pattern, debug_id):
    rows = []
    for s, t in PAIRS:
        tm = transfer_meta_for_language_pair(pattern, source_language=s, target_language=t)
        code = DEBUG_SAMPLES[debug_id].get(t, "")
        hits = detect_algorithm_debug(
            debug_id=debug_id,
            target_language=t,
            code=code,
            test_results=[{"status": "FAILED"}],
            buggy_code=code,
        )
        proactive = (tm.get("proactive") or {}).get("text") or ""
        hint = tm.get("algorithm_hint_ru") or tm.get("reference_warning_ru") or ""
        reactive = hits[0].get("text", "") if hits else ""
        rows.append(
            {
                "pair": f"{s}->{t}",
                "transfer_type": tm.get("transfer_type"),
                "algorithm_hint": bool(hint),
                "reactive": bool(reactive),
                "reactive_has_code": bool(">" in reactive or ">=" in reactive or "50" in reactive or "0" in reactive),
            }
        )
    return rows


if __name__ == "__main__":
    out = {
        "task_006": matrix_task006(),
        "task_003": matrix_task003(),
        "task_004": matrix_debug("task_004", "filter_positive"),
        "task_007": matrix_debug("task_007", "threshold_count"),
        "task_053": [
            {
                "pair": f"{s}->{t}",
                "transfer_type": transfer_meta_for_language_pair(
                    "task_053", source_language=s, target_language=t
                ).get("transfer_type"),
                "proactive": False,
                "reactive": False,
            }
            for s, t in PAIRS
        ],
    }
    path = BACKEND.parent / "docs" / "_mplt_pair_matrix.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    for pid, rows in out.items():
        fail = [r for r in rows if pid in ("task_053",) and r.get("transfer_type") != "TCC"]
        if pid == "task_006":
            fail = [r for r in rows if not r.get("proactive") or not r.get("reactive_has_code")]
        elif pid == "task_003":
            fail = [r for r in rows if not r.get("proactive")]
        elif pid in ("task_004", "task_007"):
            fail = [r for r in rows if not r.get("reactive")]
        else:
            fail = []
        print(f"{pid}: {len(rows)} pairs, issues={len(fail)}")
    print(f"Wrote {path}")
