#!/usr/bin/env python3
"""Checagens mecânicas de frontend para o Frontend Auditor.

Uso:
    python3 mechanical_checks.py <arquivo.html | URL>

Saída: relatório textual com itens PASS / FAIL / WARN por regra da rubrica.
Cobre D1.2 (parcial), D1.8, D3.3, D4.3–D4.6. Itens visuais ficam para
análise de screenshot pelo agente.
"""
import re
import sys
import urllib.request
from html.parser import HTMLParser


class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.lang = None
        self.viewport = False
        self.favicon = False
        self.fonts = []
        self.images = []          # (src, alt ou None)
        self.buttons = 0
        self.fake_buttons = 0     # div/span com onclick
        self.inputs_unlabeled = 0
        self.labels_for = set()
        self.input_ids = []
        self.landmarks = set()
        self.headings = []
        self._in_title = False
        self.resources = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "meta" and a.get("name") == "viewport":
            self.viewport = True
        if tag == "link":
            rel = a.get("rel", "")
            if "icon" in rel:
                self.favicon = True
            href = a.get("href", "")
            if "font" in href or "fonts.g" in href:
                self.fonts.append(href)
        if tag == "img":
            self.images.append((a.get("src", "?"), a.get("alt")))
        if tag == "button":
            self.buttons += 1
        if tag in ("div", "span") and "onclick" in a:
            self.fake_buttons += 1
        if tag in ("input", "textarea", "select"):
            if a.get("type") not in ("hidden", "submit", "button"):
                self.input_ids.append(a.get("id"))
        if tag == "label" and a.get("for"):
            self.labels_for.add(a["for"])
        if tag in ("header", "main", "nav", "footer", "aside"):
            self.landmarks.add(tag)
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        for attr in ("src", "href"):
            if attr in a and a[attr] and not a[attr].startswith(("#", "data:", "mailto:")):
                self.resources.append(a[attr])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def report(name, ok, detail="", warn=False):
    mark = "PASS" if ok else ("WARN" if warn else "FAIL")
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))


def main(path):
    if path.startswith(("http://", "https://")):
        html = urllib.request.urlopen(path, timeout=20).read().decode("utf-8", "replace")
    else:
        html = open(path, encoding="utf-8", errors="replace").read()

    p = AuditParser()
    p.feed(html)

    print("== D4.6 Meta e documento ==")
    report("title descritivo", bool(p.title.strip()) and len(p.title.strip()) > 3, p.title.strip()[:60])
    report("lang no <html>", bool(p.lang), p.lang or "ausente")
    report("meta viewport", p.viewport)
    report("favicon", p.favicon)

    print("\n== D4.3 Semântica ==")
    report("landmarks (header/main/nav)", bool(p.landmarks), ", ".join(sorted(p.landmarks)) or "nenhuma")
    report("sem div/span com onclick", p.fake_buttons == 0, f"{p.fake_buttons} encontrados")
    seq_ok = all(b - a <= 1 for a, b in zip(p.headings, p.headings[1:]))
    report("hierarquia de headings sem saltos", seq_ok, str(p.headings[:12]), warn=not seq_ok)

    print("\n== D4.4 Imagens ==")
    if not p.images:
        print("[N/A] sem imagens")
    for src, alt in p.images:
        report(f"alt em {src[:40]}", alt is not None, repr(alt))

    print("\n== D4.5 Formulários ==")
    if not p.input_ids:
        print("[N/A] sem campos de formulário")
    else:
        sem_label = [i for i in p.input_ids if i and i not in p.labels_for]
        report("inputs com <label for>", not sem_label, f"{len(sem_label)} sem label")

    print("\n== D1.8 / D3.3 Recursos ==")
    report("webfonts declaradas", bool(p.fonts), f"{len(p.fonts)} link(s) de fonte", warn=not p.fonts)
    mixed = [r for r in p.resources if r.startswith("http://")]
    report("sem conteúdo misto http", not mixed, f"{len(mixed)} recurso(s) http")

    print("\n== Checagens textuais ==")
    lorem = len(re.findall(r"lorem ipsum", html, re.I))
    report("sem lorem ipsum", lorem == 0, f"{lorem} ocorrência(s)")
    todos = len(re.findall(r"\bTODO\b|\bFIXME\b|placeholder text", html))
    report("sem TODO/placeholder visível", todos == 0, f"{todos} ocorrência(s)", warn=todos > 0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("uso: mechanical_checks.py <arquivo.html | URL>")
    main(sys.argv[1])
