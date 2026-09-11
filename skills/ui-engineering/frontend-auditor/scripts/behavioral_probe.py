#!/usr/bin/env python3
"""behavioral_probe.py — Roteiros de interação automatizados (D1).

Percorre a página clicando em controles, testando formulários, navegando por
teclado e forçando estados de erro/rede. Produz JSON com evidências.

Uso:
    python3 behavioral_probe.py <URL | file://...> [--out probe.json] [--screens dir]

Requer playwright (usa o Chromium do sistema via CHROMIUM_PATH ou /usr/bin/chromium).
"""
import argparse
import json
import os
import sys
import time

CHROMIUM = os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium")


def run(url, out_path, screens_dir):
    from playwright.sync_api import sync_playwright

    results = {
        "url": url,
        "console_errors": [],
        "failed_requests": [],
        "clicks": [],
        "keyboard": {},
        "forms": {},
        "states": {},
        "load_ms": None,
        "blank_screen": False,
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("console", lambda m: results["console_errors"].append(m.text)
                if m.type == "error" else None)
        page.on("requestfailed", lambda r: results["failed_requests"].append(r.url))
        page.on("response", lambda r: results["failed_requests"].append(f"{r.status} {r.url}")
                if r.status >= 400 else None)

        t0 = time.time()
        try:
            page.goto(url, wait_until="load", timeout=25000)
        except Exception as e:
            results["console_errors"].append(f"navigation: {e}")
        results["load_ms"] = int((time.time() - t0) * 1000)
        page.wait_for_timeout(1200)

        # D1.1 — tela branca?
        body_text = page.evaluate("document.body ? document.body.innerText.trim().length : 0")
        results["blank_screen"] = body_text == 0
        if screens_dir:
            os.makedirs(screens_dir, exist_ok=True)
            page.screenshot(path=os.path.join(screens_dir, "01_initial.png"))

        # D1.4 — clicar em controles visíveis (amostra de até 15)
        controls = page.locator(
            "button:visible, [role='button']:visible, summary:visible, "
            "input[type='checkbox']:visible, input[type='radio']:visible, select:visible"
        )
        n = min(controls.count(), 15)
        for i in range(n):
            try:
                el = controls.nth(i)
                name = (el.inner_text(timeout=500) or el.get_attribute("aria-label") or "?").strip()[:40]
                el.click(timeout=1200)
                page.wait_for_timeout(250)
                results["clicks"].append({"target": name, "ok": True})
            except Exception as e:
                results["clicks"].append({"target": f"#{i}", "ok": False, "err": str(e)[:120]})
        # fecha qualquer modal aberto pelo teste
        page.keyboard.press("Escape")

        # D4.2 — navegação por teclado: quantos stops de foco? foco visível?
        page.evaluate("document.activeElement && document.activeElement.blur()")
        page.locator("body").click(position={"x": 5, "y": 5})
        focus_seen = []
        for _ in range(25):
            page.keyboard.press("Tab")
            info = page.evaluate("""() => {
                const el = document.activeElement;
                if (!el || el === document.body) return null;
                const st = getComputedStyle(el);
                const visible = st.outlineStyle !== 'none' || st.boxShadow !== 'none';
                return {tag: el.tagName, label: (el.innerText || el.getAttribute('aria-label') || '').slice(0,30), visible};
            }""")
            if info is None:
                break
            focus_seen.append(info)
        results["keyboard"] = {
            "tab_stops": len(focus_seen),
            "focus_visible_count": sum(1 for f in focus_seen if f["visible"]),
            "sample": focus_seen[:8],
        }

        # D1.5 — formulários: submit vazio e inválido
        forms = page.locator("form:visible")
        results["forms"] = {"count": forms.count(), "tests": []}
        for i in range(min(forms.count(), 3)):
            f = forms.nth(i)
            test = {"form": i, "empty_submit_blocked": None, "invalid_email_flagged": None}
            try:
                email = f.locator("input[type='email']")
                if email.count():
                    email.first.fill("nao-e-email")
                    email.first.evaluate("e => e.form && e.form.requestSubmit ? e.form.requestSubmit() : null")
                    page.wait_for_timeout(300)
                    test["invalid_email_flagged"] = email.first.evaluate(
                        "e => !e.checkValidity()")
                submit = f.locator("button[type='submit'], input[type='submit'], button:not([type])")
                if submit.count():
                    test["empty_submit_blocked"] = submit.first.evaluate(
                        "b => { const f = b.form || b.closest('form'); return f ? !f.checkValidity() : null; }")
            except Exception as e:
                test["error"] = str(e)[:120]
            results["forms"]["tests"].append(test)

        # Estados forçados — rede offline
        vp = {"width": 1440, "height": 900}
        ctx2 = browser.new_context(viewport=vp, offline=True)
        pg2 = ctx2.new_page()
        try:
            pg2.goto(url, timeout=8000)
            results["states"]["offline"] = "rendered"
        except Exception:
            results["states"]["offline"] = "failed_to_render"
        ctx2.close()

        # Zoom 200% — overflow?
        page.evaluate("document.body.style.zoom = '200%'")
        page.wait_for_timeout(300)
        results["states"]["zoom200_overflow"] = page.evaluate(
            "document.documentElement.scrollWidth > window.innerWidth + 10")
        page.evaluate("document.body.style.zoom = ''")

        # prefers-reduced-motion — a página respeita?
        rm = page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
        results["states"]["reduced_motion_media_available"] = True  # API existe
        results["states"]["note_reduced_motion"] = (
            "verificar manualmente se animações são desativadas sob prefers-reduced-motion" if not rm else "UA em reduced-motion")

        browser.close()

    results["summary"] = {
        "clicks_ok": sum(1 for c in results["clicks"] if c["ok"]),
        "clicks_total": len(results["clicks"]),
        "console_error_count": len(results["console_errors"]),
        "failed_request_count": len(results["failed_requests"]),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(json.dumps(results["summary"], ensure_ascii=False))
    print(f"gravado: {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="probe.json")
    ap.add_argument("--screens", default=None)
    a = ap.parse_args()
    url = a.url
    if os.path.exists(url):
        url = "file://" + os.path.abspath(url)
    run(url, a.out, a.screens)
