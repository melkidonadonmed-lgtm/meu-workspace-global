#!/usr/bin/env python3
"""axe_scan.py — Auditoria de acessibilidade com axe-core (D4) + variantes de tema.

Baixa axe-core do CDN (ou usa cópia local em assets/axe.min.js), injeta na página
e retorna violações agrupadas por regra. Também captura screenshots do tema claro,
escuro e prefers-reduced-motion quando a página declara suporte.

Uso:
    python3 axe_scan.py <URL | arquivo.html> [--out axe.json] [--screens dir]
"""
import argparse
import json
import os
import urllib.request

CHROMIUM = os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium")
AXE_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"
AXE_LOCAL = os.path.join(os.path.dirname(__file__), "..", "assets", "axe.min.js")


def get_axe_source():
    if os.path.exists(AXE_LOCAL):
        return open(AXE_LOCAL, encoding="utf-8").read()
    try:
        src = urllib.request.urlopen(AXE_URL, timeout=20).read().decode("utf-8")
        os.makedirs(os.path.dirname(AXE_LOCAL), exist_ok=True)
        with open(AXE_LOCAL, "w", encoding="utf-8") as f:
            f.write(src)
        return src
    except Exception as e:
        raise SystemExit(f"não foi possível obter axe-core ({e}); coloque axe.min.js em assets/")


def run(url, out_path, screens_dir):
    from playwright.sync_api import sync_playwright

    axe_src = get_axe_source()
    report = {"url": url, "violations": [], "passes_count": 0, "themes": {}, "error": None}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])

        def scan(ctx_kwargs, label):
            vp = dict(width=1440, height=900)
            ctx = browser.new_context(viewport=vp, **ctx_kwargs)
            pg = ctx.new_page()
            pg.goto(url, wait_until="load", timeout=25000)
            pg.wait_for_timeout(800)
            data = pg.evaluate(
                "src => new Promise(res => {"
                " const s = document.createElement('script'); s.textContent = src;"
                " document.head.appendChild(s);"
                " axe.run(document, {resultTypes:['violations']}).then(r => res({"
                "   violations: r.violations.map(v => ({id: v.id, impact: v.impact,"
                "     help: v.help, nodes: v.nodes.length,"
                "     targets: v.nodes.slice(0,5).map(n => n.target.join(' '))})),"
                "   passes: r.passes.length })); })", axe_src)
            if screens_dir:
                os.makedirs(screens_dir, exist_ok=True)
                pg.screenshot(path=os.path.join(screens_dir, f"axe_{label}.png"))
            ctx.close()
            return data

        try:
            base = scan({}, "default")
            report["violations"] = base["violations"]
            report["passes_count"] = base["passes"]

            # tema claro/escuro: só vale a pena se a página reage a color-scheme
            for scheme, label in [("light", "light"), ("dark", "dark")]:
                try:
                    r = scan({"color_scheme": scheme}, label)
                    report["themes"][label] = {
                        "violations": len(r["violations"]),
                        "contrast_issues": [v for v in r["violations"] if v["id"] == "color-contrast"],
                    }
                except Exception as e:
                    report["themes"][label] = {"error": str(e)[:120]}

            # reduced motion
            try:
                scan({"reduced_motion": "reduce"}, "reduced-motion")
                report["themes"]["reduced_motion"] = "screenshot capturado — comparar animações"
            except Exception:
                pass
        except Exception as e:
            report["error"] = str(e)[:200]
        browser.close()

    impact_order = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
    report["violations"].sort(key=lambda v: impact_order.get(v["impact"], 4))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    crit = [v for v in report["violations"] if v["impact"] in ("critical", "serious")]
    print(f"violações: {len(report['violations'])} ({len(crit)} críticas/sérias) · passes: {report['passes_count']}")
    for v in report["violations"][:10]:
        print(f"  [{v['impact']}] {v['id']} — {v['nodes']} ocorrência(s)")
    print(f"gravado: {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="axe.json")
    ap.add_argument("--screens", default=None)
    a = ap.parse_args()
    url = a.url
    if os.path.exists(url):
        url = "file://" + os.path.abspath(url)
    run(url, a.out, a.screens)
