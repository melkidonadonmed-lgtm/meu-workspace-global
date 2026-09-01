"""Suíte de Testes Unitários para Validação de Saída HTML Modular, Semântica e WCAG 2.1 AA.

Módulo: test_html_output.py
Descrição: Valida se as estruturas HTML geradas atendem aos critérios de qualidade,
           semântica HTML5, regras de acessibilidade, classes responsivas e segurança.
"""

import re
import unittest
from html.parser import HTMLParser

VALID_FULL_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaaS Analytics - Solução de IA</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 antialiased font-sans">
    <header class="w-full bg-slate-900 text-white shadow-md">
        <nav class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center" aria-label="Navegação Principal">
            <a href="/" class="text-xl font-bold text-blue-400" aria-label="Página Inicial da SaaS Analytics">SaaS AI</a>
            <ul class="hidden md:flex space-x-6">
                <li><a href="#recursos" class="hover:text-blue-400 transition-colors">Recursos</a></li>
                <li><a href="#precos" class="hover:text-blue-400 transition-colors">Preços</a></li>
                <li><a href="#contato" class="hover:text-blue-400 transition-colors">Contato</a></li>
            </ul>
            <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors" aria-label="Acessar conta da plataforma">Entrar</button>
        </nav>
    </header>
    <main id="conteudo-principal">
        <section class="py-20 px-6 max-w-7xl mx-auto flex flex-col md:flex-row items-center">
            <div class="md:w-1/2 space-y-6">
                <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight text-slate-900">
                    Transforme seus dados em <span class="text-blue-600">decisões inteligentes</span>
                </h1>
                <p class="text-lg text-slate-600">
                    Nossa plataforma de IA orquestra fluxos analíticos em tempo real com segurança empresarial.
                </p>
                <div class="flex space-x-4">
                    <a href="#comecar" class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 shadow-lg shadow-blue-500/30">Começar Grátis</a>
                </div>
            </div>
            <div class="md:w-1/2 mt-10 md:mt-0">
                <img src="https://via.placeholder.com/600x400" alt="Painel analítico com gráficos de desempenho em tempo real" class="rounded-2xl shadow-2xl w-full h-auto" />
            </div>
        </section>
        <section id="recursos" class="py-16 bg-white border-t border-slate-200">
            <div class="max-w-7xl mx-auto px-6">
                <h2 class="text-3xl font-bold text-center mb-12">Recursos Principais</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <article class="p-6 bg-slate-50 rounded-xl border border-slate-200">
                        <h3 class="text-xl font-semibold mb-2">Processamento Real-Time</h3>
                        <p class="text-slate-600">Análise contínua com latência reduzida e alta disponibilidade.</p>
                    </article>
                </div>
            </div>
        </section>
    </main>
    <footer class="bg-slate-900 text-slate-400 py-8 border-t border-slate-800">
        <div class="max-w-7xl mx-auto px-6 text-center">
            <p>&copy; 2026 SaaS Analytics. Todos os direitos reservados.</p>
        </div>
    </footer>
</body>
</html>"""

INVALID_DIVSOUP_HTML = """<div>
    <div class="header">
        <div class="logo"><img src="logo.png"></div>
        <div class="menu">
            <div><a href="#">Link 1</a></div>
        </div>
    </div>
    <div class="content">
        <div class="title">Título sem H1</div>
        <button></button>
    </div>
</div>"""


class HTMLNode:
    """Nó representativo de tag HTML extraído pelo parser."""

    def __init__(self, tag: str, attrs: dict[str, str]):
        self.tag = tag
        self.attrs = attrs
        self.text_chunks: list[str] = []

    def get_text(self) -> str:
        return " ".join(self.text_chunks).strip()


class FastHTMLInspector(HTMLParser):
    """Parser leve nativo de HTML5 para inspeção semântica e de acessibilidade."""

    def __init__(self, html_content: str):
        super().__init__()
        self.nodes: list[HTMLNode] = []
        self._current_node: HTMLNode | None = None
        self.feed(html_content)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        node = HTMLNode(tag.lower(), attr_dict)
        self.nodes.append(node)
        self._current_node = node

    def handle_data(self, data: str):
        if self._current_node and data.strip():
            self._current_node.text_chunks.append(data.strip())

    def find_all(self, tag_names: str | list[str]) -> list[HTMLNode]:
        if isinstance(tag_names, str):
            tag_names = [tag_names.lower()]
        else:
            tag_names = [t.lower() for t in tag_names]
        return [n for n in self.nodes if n.tag in tag_names]

    def find(self, tag_name: str) -> HTMLNode | None:
        matches = self.find_all(tag_name)
        return matches[0] if matches else None


class TestHTML5Semantics(unittest.TestCase):
    """Testa a conformidade da estrutura com o padrão HTML5 semântico."""

    def test_doctype_declaration(self):
        cleaned_html = VALID_FULL_HTML.strip()
        self.assertTrue(
            cleaned_html.lower().startswith("<!doctype html>"),
            "O documento deve iniciar com <!DOCTYPE html>",
        )

    def test_html_lang_attribute(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        html_node = inspector.find("html")
        self.assertIsNotNone(html_node, "A tag <html> deve estar presente.")
        self.assertIn("lang", html_node.attrs, "A tag <html> deve conter o atributo 'lang'.")
        self.assertGreater(len(html_node.attrs["lang"].strip()), 0)

    def test_essential_meta_tags(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        meta_nodes = inspector.find_all("meta")

        has_charset = any("charset" in m.attrs for m in meta_nodes)
        self.assertTrue(has_charset, "Deve existir uma tag <meta charset='UTF-8'>")

        has_viewport = any(
            m.attrs.get("name") == "viewport" and len(m.attrs.get("content", "")) > 0
            for m in meta_nodes
        )
        self.assertTrue(has_viewport, "Deve existir uma tag <meta name='viewport'>")

    def test_semantic_structural_tags(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        self.assertIsNotNone(inspector.find("header"), "Falta a tag semântica <header>")
        self.assertIsNotNone(inspector.find("nav"), "Falta a tag semântica <nav>")
        self.assertIsNotNone(inspector.find("main"), "Falta a tag semântica <main>")
        self.assertIsNotNone(inspector.find("footer"), "Falta a tag semântica <footer>")

    def test_avoid_div_soup_ratio(self):
        inspector_valid = FastHTMLInspector(VALID_FULL_HTML)
        semantic_tags = ["header", "nav", "main", "section", "article", "aside", "footer"]
        valid_count = len(inspector_valid.find_all(semantic_tags))
        self.assertGreaterEqual(valid_count, 4)

        inspector_invalid = FastHTMLInspector(INVALID_DIVSOUP_HTML)
        invalid_count = len(inspector_invalid.find_all(semantic_tags))
        self.assertEqual(invalid_count, 0)


class TestAccessibilityWCAG(unittest.TestCase):
    """Valida requisitos fundamentais de acessibilidade digital (WCAG 2.1 AA)."""

    def test_images_have_alt_attributes(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        images = inspector.find_all("img")
        self.assertGreater(len(images), 0)
        for img in images:
            self.assertIn("alt", img.attrs, f"Imagem {img.attrs} não possui atributo 'alt'.")
            self.assertGreater(len(img.attrs["alt"].strip()), 0)

    def test_heading_hierarchy_has_h1(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        h1_tags = inspector.find_all("h1")
        self.assertEqual(len(h1_tags), 1, "A página deve ter exatamente 1 tag <h1>.")
        self.assertGreater(len(h1_tags[0].get_text()), 0)

    def test_interactive_elements_have_labels(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        buttons = inspector.find_all("button")
        for btn in buttons:
            text = btn.get_text()
            has_aria_label = "aria-label" in btn.attrs and len(btn.attrs["aria-label"].strip()) > 0
            self.assertTrue(bool(text or has_aria_label))

    def test_navigation_has_aria_label(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        nav_tags = inspector.find_all("nav")
        for nav in nav_tags:
            self.assertIn("aria-label", nav.attrs, "A tag <nav> deve possuir 'aria-label'.")


class TestTailwindResponsiveness(unittest.TestCase):
    """Verifica o emprego de classes utilitárias para layouts responsivos (Mobile-First)."""

    def test_presence_of_responsive_breakpoints(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        has_responsive = False
        for node in inspector.nodes:
            classes = node.attrs.get("class", "").split()
            if any(re.match(r"^(sm|md|lg|xl|2xl):", cls) for cls in classes):
                has_responsive = True
                break
        self.assertTrue(has_responsive, "O documento HTML deve conter classes com breakpoints.")

    def test_flex_or_grid_layout_usage(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        has_layout = False
        for node in inspector.nodes:
            classes = node.attrs.get("class", "").split()
            if any(cls in ["flex", "grid", "inline-flex", "inline-grid"] for cls in classes):
                has_layout = True
                break
        self.assertTrue(has_layout, "O layout deve utilizar classes de Flexbox ou Grid.")


class TestSecurityAndCleanliness(unittest.TestCase):
    """Verifica a ausência de más práticas de código ou código inseguro."""

    def test_no_inline_styles(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        nodes_with_style = [n for n in inspector.nodes if "style" in n.attrs]
        self.assertEqual(len(nodes_with_style), 0, "Evite atributos 'style' inline.")

    def test_no_unsafe_javascript_links(self):
        inspector = FastHTMLInspector(VALID_FULL_HTML)
        links = inspector.find_all("a")
        for a in links:
            href = a.attrs.get("href", "").strip().lower()
            self.assertFalse(href.startswith("javascript:"), f"Link inseguro detectado: {href}")


if __name__ == "__main__":
    unittest.main()
