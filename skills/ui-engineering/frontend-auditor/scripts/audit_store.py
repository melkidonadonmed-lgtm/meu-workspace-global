#!/usr/bin/env python3
"""audit_store.py — Histórico persistente de auditorias + diff comparativo.

Cada auditoria é gravada como audits/<slug>/<timestamp>.json com notas por item
(não só por dimensão), permitindo diff exato entre execuções.

Uso:
    python3 audit_store.py save <projeto> <notas.json> [--dir audits]
    python3 audit_store.py diff <projeto> [--dir audits]
    python3 audit_store.py list <projeto> [--dir audits]

Formato de <notas.json>:
{
  "target": "Tela X",
  "profile": "dashboard",
  "items": {"D1.1": 20, "D1.2": 10, ...},          // pontos obtidos por regra
  "penalties": [{"rule": "blank_screen", "value": -20, "reason": "..."}],
  "findings": [{"severity": "critical|major|minor", "evidence": "VERIFICADO|INFERIDO",
                "text": "...", "rule": "D4.1"}]
}
O script calcula dimensões e nota geral a partir dos itens, usando os pesos do perfil.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime

WEIGHTS = {"D1": 0.35, "D2": 0.30, "D3": 0.15, "D4": 0.20}
MAX_POINTS = {  # espelha references/rubric.md
    "D1": {"D1.1": 20, "D1.2": 10, "D1.3": 12, "D1.4": 15, "D1.5": 12, "D1.6": 12, "D1.7": 12, "D1.8": 7},
    "D2": {"D2.1": 18, "D2.2": 16, "D2.3": 16, "D2.4": 14, "D2.5": 12, "D2.6": 10, "D2.7": 8, "D2.8": 6},
    "D3": {"D3.1": 20, "D3.2": 22, "D3.3": 12, "D3.4": 16, "D3.5": 14, "D3.6": 16},
    "D4": {"D4.1": 24, "D4.2": 18, "D4.3": 16, "D4.4": 10, "D4.5": 12, "D4.6": 8, "D4.7": 12, "D4.8": 8, "D4.9": 4, "D4.10": 6},
}
VERDICTS = [(90, "Excelente"), (75, "Bom"), (60, "Aceitável"), (40, "Fraco"), (0, "Crítico")]


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def compute(notes):
    dims = {}
    for dim, items in MAX_POINTS.items():
        got = sum(min(notes["items"].get(k, 0), v) for k, v in items.items() if k in notes["items"])
        avail = sum(v for k, v in items.items() if k in notes["items"])
        dims[dim] = round(got / avail * 100) if avail else None
    applicable = {d: v for d, v in dims.items() if v is not None}
    wsum = sum(WEIGHTS[d] for d in applicable)
    overall = sum(applicable[d] * WEIGHTS[d] for d in applicable) / wsum if wsum else 0
    for p in notes.get("penalties", []):
        if p.get("rule") == "blank_screen":
            overall = min(overall, 20)
        else:
            overall += p.get("value", 0)
    overall = max(0, round(overall))
    verdict = next(v for lim, v in VERDICTS if overall >= lim)
    return {"dimensions": dims, "overall": overall, "verdict": verdict}


def cmd_save(project, notes_path, base):
    notes = json.load(open(notes_path, encoding="utf-8"))
    scores = compute(notes)
    entry = {"ts": datetime.now().isoformat(timespec="seconds"),
             "target": notes.get("target", project),
             "profile": notes.get("profile", "generic"),
             **scores, "items": notes["items"],
             "penalties": notes.get("penalties", []),
             "findings": notes.get("findings", [])}
    d = os.path.join(base, slugify(project))
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, entry["ts"].replace(":", "-") + ".json")
    json.dump(entry, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"salvo: {path}")
    print(f"nota geral: {scores['overall']}/100 — {scores['verdict']}")
    print(json.dumps(scores["dimensions"], ensure_ascii=False))


def load_history(project, base):
    d = os.path.join(base, slugify(project))
    if not os.path.isdir(d):
        return []
    return [json.load(open(os.path.join(d, f), encoding="utf-8"))
            for f in sorted(os.listdir(d)) if f.endswith(".json")]


def cmd_list(project, base):
    for e in load_history(project, base):
        print(f"{e['ts']}  {e['overall']:>3}/100  {e['verdict']:<10}  {e['target']}")


def cmd_diff(project, base):
    hist = load_history(project, base)
    if len(hist) < 2:
        sys.exit("histórico insuficiente — precisa de 2+ auditorias salvas")
    old, new = hist[-2], hist[-1]
    print(f"# Comparativo: {old['ts']} → {new['ts']}")
    print(f"nota geral: {old['overall']} → {new['overall']} ({new['overall']-old['overall']:+d})\n")
    print("| Dimensão | Antes | Agora | Δ |")
    print("|---|---|---|---|")
    for dim in MAX_POINTS:
        a, b = old["dimensions"].get(dim), new["dimensions"].get(dim)
        if a is not None and b is not None:
            print(f"| {dim} | {a} | {b} | {b-a:+d} |")
    print("\n## Itens que mudaram")
    keys = sorted(set(old["items"]) | set(new["items"]))
    regressions, improvements = [], []
    for k in keys:
        a, b = old["items"].get(k), new["items"].get(k)
        if a != b:
            line = f"- {k}: {a if a is not None else 'N/A'} → {b if b is not None else 'N/A'}"
            (improvements if (b or 0) > (a or 0) else regressions).append(line)
    if regressions:
        print("### Regressões\n" + "\n".join(regressions))
    if improvements:
        print("### Melhorias\n" + "\n".join(improvements))
    if not regressions and not improvements:
        print("(nenhuma mudança por item)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["save", "diff", "list"])
    ap.add_argument("project")
    ap.add_argument("notes", nargs="?")
    ap.add_argument("--dir", default="audits")
    a = ap.parse_args()
    if a.cmd == "save":
        if not a.notes:
            sys.exit("save requer <notas.json>")
        cmd_save(a.project, a.notes, a.dir)
    elif a.cmd == "diff":
        cmd_diff(a.project, a.dir)
    else:
        cmd_list(a.project, a.dir)
