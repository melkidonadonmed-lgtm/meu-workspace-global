"""Suíte de Testes Adversariais e Empíricos de Preview (Challenger).

Executa desafios adversariais rigorosos contra:
1. SemanticHTMLCleaner / WebResearcher (researcher.py):
   - Injeção de scripts disfarçados, CDATA, módulos, telemetria inline e manipuladores de eventos on*
   - Injeção de SVGs aninhados com <text>, <tspan>, <foreignObject> e nós gráficos
   - Injeção de tags <style> e inline styles com payloads
   - Injeção de blocos <noscript> e comentários condicionais
   - Injeção de tags desconhecidas e web components customizados
   - Sanitização de links maliciosos com protocolos pseudo-javascript (maiúsculas/minúsculas)
   - Extração de metadados em extract_title_and_snippet

2. DOMAuditor (dom_auditor.py):
   - Inspeção de elementos com display: none, visibility: hidden, visibility: collapse
   - Inspeção de nós com dimensão zero (width=0 ou height=0) e discrepâncias headless vs fallback
   - Inspeção de nós com opacity: 0 (Playwright vs Fallback)
   - Inspeção de atributo nativo HTML5 'hidden'
   - Extração e cálculo correto de getBoundingClientRect e ComputedElementGeometry
   - Tratamento de nós obrigatórios e seletores CSS complexos
"""

from __future__ import annotations

from web_visual_auditor.dom_auditor import DOMAuditor
from web_visual_auditor.models import (
    ComputedElementGeometry,
)
from web_visual_auditor.researcher import (
    SemanticHTMLCleaner,
)

# ==============================================================================
# 1. DESAFIOS ADVERSARIAIS: SANITIZAÇÃO SEMÂNTICA (researcher.py)
# ==============================================================================


class TestAdversarialSemanticSanitization:
    """Bateria de testes adversariais para a higienização semântica."""

    def test_purge_complex_disguised_scripts(self) -> None:
        """Injeta múltiplos formatos de script disfarçados e garante expurgo total."""
        malicious_html = (
            "<div>"
            "<h1>Título Nobre</h1>"
            "<script type='text/javascript'>alert('xss1');</script>"
            "<SCRIPT type='module'>import { evil } from 'evil.js'; evil();</SCRIPT>"
            "<script src='https://tracker.local/beacon.js' async defer>tracker payload</script>"
            "<script>/*<![CDATA[*/var secret = 'leaked';/*]]>*/</script>"
            "<script>//<!--\nvar x = 1;\n//--></script>"
            "<button onclick=\"evil()\" ONMOUSEOVER=\"steal()\" OnFocus=\"bad()\">Ação</button>"
            "<p>Texto legítimo preservado.</p>"
            "</div>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned = cleaner.clean_text(malicious_html)

        # Validações de ausência absoluta de resquícios de scripts
        assert "alert" not in cleaned
        assert "xss1" not in cleaned
        assert "evil" not in cleaned
        assert "tracker payload" not in cleaned
        assert "beacon.js" not in cleaned
        assert "secret" not in cleaned
        assert "leaked" not in cleaned
        assert "onclick" not in cleaned
        assert "steal" not in cleaned

        # Validação de preservação de texto nobre
        assert "Título Nobre" in cleaned
        assert "Ação" in cleaned
        assert "Texto legítimo preservado." in cleaned

    def test_purge_nested_svg_with_internal_text_and_foreign_objects(self) -> None:
        """Injeta SVGs complexos com nós <text>, <tspan> e <foreignObject> e valida expurgo."""
        svg_html = (
            "<article>"
            "<h2>Título do Artigo</h2>"
            "<svg width='400' height='300' viewBox='0 0 400 300'>"
            "  <text x='20' y='50'>Texto Interno em SVG Não Deve Vazar</text>"
            "  <g id='camada-1'>"
            "    <text x='20' y='80'><tspan>Subtexto tspan aninhado</tspan></text>"
            "    <foreignObject width='100' height='50'>"
            "      <p>Texto dentro de foreignObject embutido no SVG</p>"
            "    </foreignObject>"
            "  </g>"
            "</svg>"
            "<p>Conteúdo textual fora do SVG deve permanecer intacto.</p>"
            "</article>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned = cleaner.clean_text(svg_html)

        # Todo o conteúdo dentro da árvore SVG deve ser purgado
        assert "Texto Interno em SVG Não Deve Vazar" not in cleaned
        assert "Subtexto tspan aninhado" not in cleaned
        assert "Texto dentro de foreignObject embutido no SVG" not in cleaned
        assert "foreignObject" not in cleaned
        assert "viewBox" not in cleaned

        # Conteúdo nobre externo preservado
        assert "Título do Artigo" in cleaned
        assert "Conteúdo textual fora do SVG deve permanecer intacto." in cleaned

    def test_purge_inline_styles_css_blocks_and_style_attributes(self) -> None:
        """Injeta tags style inline, media queries e styles inline com CSS expressions."""
        styled_html = (
            "<head>"
            "<style>"
            "  @media screen { body { background: red; } }"
            "  .injected-class { display: block; content: 'css-leak'; }"
            "</style>"
            "</head>"
            "<body>"
            "<STYLE type='text/css'>p { color: blue; }</STYLE>"
            "<div style=\"background-image: url('javascript:alert(1)'); color: green;\">"
            "  <p style=\"font-size: 16px; margin: 0;\">Parágrafo com estilo inline.</p>"
            "</div>"
            "</body>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned = cleaner.clean_text(styled_html)

        assert "background: red" not in cleaned
        assert "css-leak" not in cleaned
        assert "color: blue" not in cleaned
        assert "color: green" not in cleaned
        assert "background-image" not in cleaned
        assert "javascript:alert" not in cleaned
        assert "Parágrafo com estilo inline." in cleaned

    def test_purge_noscript_and_conditional_comments(self) -> None:
        """Injeta nós noscript e comentários condicionais legados."""
        html = (
            "<div>"
            "<!--[if IE]><p>Aviso IE legado</p><![endif]-->"
            "<!-- Comentário normal com <script>fake()</script> -->"
            "<noscript>"
            "  <p>Ative o JavaScript para a melhor experiência.</p>"
            "  <a href='https://evil.local/nojs'>Clique aqui</a>"
            "</noscript>"
            "<p>Texto principal limpo.</p>"
            "</div>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned = cleaner.clean_text(html)

        assert "Aviso IE legado" not in cleaned
        assert "fake()" not in cleaned
        assert "Ative o JavaScript" not in cleaned
        assert "evil.local" not in cleaned
        assert "Texto principal limpo." in cleaned

    def test_unknown_and_custom_web_component_tags(self) -> None:
        """Injeta web components customizados e tags desconhecidas."""
        custom_html = (
            "<custom-dashboard id='dash-1'>"
            "  <user-avatar user-id='42'>Avatar</user-avatar>"
            "  <metric-card data-value='99.9'>"
            "    <h3>Disponibilidade do Sistema</h3>"
            "    <span class='percentage'>99.9%</span>"
            "  </metric-card>"
            "</custom-dashboard>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned = cleaner.clean_text(custom_html)

        assert "Avatar" in cleaned
        assert "Disponibilidade do Sistema" in cleaned
        assert "99.9%" in cleaned
        # Não deve haver resíduos literais das tags
        assert "<custom-dashboard" not in cleaned
        assert "<metric-card" not in cleaned

    def test_adversarial_link_case_sensitive_javascript_bypass(self) -> None:
        """Demonstra a vulnerabilidade de bypass de protocolo pseudo-javascript via maiúsculas."""
        html = (
            "<nav>"
            "  <a href='javascript:alert(1)'>Link JS Minúsculo (bloqueado)</a>"
            "  <a href='JAVASCRIPT:alert(2)'>Link JS Maiúsculo (bypass)</a>"
            "  <a href='JavaScript:alert(3)'>Link JS Misto (bypass)</a>"
            "  <a href='https://legitimo.local'>Link Legítimo</a>"
            "</nav>"
        )
        cleaner = SemanticHTMLCleaner()
        refs = cleaner.extract_links(html)

        # O esperado de uma sanitização segura é que NENHUM link javascript passe
        urls = [r.url for r in refs]
        assert "https://legitimo.local" in urls
        assert "javascript:alert(1)" not in urls
        # Estas asserções expõem o bug caso href.startswith não seja case-insensitive:
        assert not any("javascript:" in u.lower() for u in urls), (
            f"Links maliciosos com bypass de case vazaram: {urls}"
        )

    def test_extract_title_and_snippet_preserves_meta_information(self) -> None:
        """Valida que extract_title_and_snippet consegue extrair meta tags mesmo com _purge_noise."""
        html = (
            "<html>"
            "<head>"
            "  <meta property='og:title' content='Título Extraído via OpenGraph'>"
            "  <meta name='description' content='Descrição semântica extraída de meta tag.'>"
            "</head>"
            "<body>"
            "  <!-- Sem h1 e sem title -->"
            "  <div>Conteúdo curto</div>"
            "</body>"
            "</html>"
        )
        cleaner = SemanticHTMLCleaner()
        title, snippet = cleaner.extract_title_and_snippet(html)

        assert title == "Título Extraído via OpenGraph"
        assert snippet == "Descrição semântica extraída de meta tag."


# ==============================================================================
# 2. DESAFIOS ADVERSARIAIS: INSPEÇÃO DO DOM E GEOMETRIA (dom_auditor.py)
# ==============================================================================


class TestAdversarialDOMInspection:
    """Bateria de testes adversariais para inspeção geométrica e nós do DOM."""

    def test_dom_inspection_with_complex_hidden_mechanisms(self) -> None:
        """Valida a identificação de nós ocultos por múltiplos mecanismos de CSS."""
        html = (
            "<style>"
            "  .collapse-box { visibility: collapse; }"
            "  .invisible-box { visibility: hidden; }"
            "  .none-box { display: none; }"
            "  .zero-box { width: 0px; height: 0px; }"
            "</style>"
            "<div>"
            "  <header id='hdr-vis' style='width: 1280px; height: 80px;'>Topo Visível</header>"
            "  <nav id='nav-disp-none' class='none-box'>Nav Display None</nav>"
            "  <article id='art-vis-hidden' class='invisible-box'>Article Hidden</article>"
            "  <main id='main-collapse' class='collapse-box'>Main Collapse</main>"
            "  <button id='btn-zero' class='zero-box'>Botão Zero</button>"
            "  <button id='btn-ok' style='width: 100px; height: 40px;'>Botão Visível</button>"
            "</div>"
        )
        auditor = DOMAuditor(force_fallback=True)
        nodes = auditor.inspect_html(html)

        hdr = auditor.find_required_node(nodes, "#hdr-vis")
        assert hdr.is_visible is True

        btn_ok = auditor.find_required_node(nodes, "#btn-ok")
        assert btn_ok.is_visible is True

        nav = auditor.find_required_node(nodes, "#nav-disp-none")
        assert nav.is_visible is False

        art = auditor.find_required_node(nodes, "#art-vis-hidden")
        assert art.is_visible is False

        main = auditor.find_required_node(nodes, "#main-collapse")
        assert main.is_visible is False

        btn_zero = auditor.find_required_node(nodes, "#btn-zero")
        assert btn_zero.is_visible is False

    def test_dom_auditor_zero_width_or_height_visibility_discrepancy(self) -> None:
        """Verifica se elementos com largura 0 (ex: colapsados) são marcados como invisíveis."""
        html = (
            "<div>"
            "  <button id='btn-thin' style='width: 0px; height: 50px;'>Botão Linha Fina</button>"
            "  <button id='btn-flat' style='width: 100px; height: 0px;'>Botão Achatado</button>"
            "</div>"
        )
        auditor = DOMAuditor(force_fallback=True)
        nodes = auditor.inspect_html(html)

        # Em browsers reais e no Playwright (rect.width <= 0 || rect.height <= 0), ambos são invisíveis
        btn_thin = auditor.find_required_node(nodes, "#btn-thin")
        btn_flat = auditor.find_required_node(nodes, "#btn-flat")

        assert btn_thin.is_visible is False, (
            f"Botão com width 0 deve ser invisível, mas obteve is_visible={btn_thin.is_visible}"
        )
        assert btn_flat.is_visible is False, (
            f"Botão com height 0 deve ser invisível, mas obteve is_visible={btn_flat.is_visible}"
        )

    def test_dom_auditor_html5_hidden_attribute(self) -> None:
        """Verifica se elementos com atributo nativo 'hidden' são reconhecidos como invisíveis."""
        html = (
            "<div>"
            "  <button id='btn-native-hidden' hidden>Botão Oculto Nativo</button>"
            "</div>"
        )
        auditor = DOMAuditor(force_fallback=True)
        nodes = auditor.inspect_html(html)

        btn = auditor.find_required_node(nodes, "#btn-native-hidden")
        assert btn.is_visible is False, (
            f"Elemento com atributo 'hidden' deve ser is_visible=False, mas obteve {btn.is_visible}"
        )

    def test_bounding_box_and_geometry_spatial_calculations(self) -> None:
        """Valida propriedades de ComputedElementGeometry: x, y, width, height, area, as_tuple."""
        geo1 = ComputedElementGeometry(x=10.0, y=20.0, width=150.0, height=40.0)
        assert geo1.x == 10.0
        assert geo1.y == 20.0
        assert geo1.width == 150.0
        assert geo1.height == 40.0
        assert geo1.area == 6000.0
        assert geo1.as_tuple == (10.0, 20.0, 150.0, 40.0)

        # Sobreposição espacial (intersects)
        geo_overlapping = ComputedElementGeometry(x=50.0, y=30.0, width=100.0, height=50.0)
        geo_disjoint = ComputedElementGeometry(x=300.0, y=300.0, width=50.0, height=50.0)

        assert geo1.intersects(geo_overlapping) is True
        assert geo1.intersects(geo_disjoint) is False

    def test_dom_auditor_handles_severely_malformed_html(self) -> None:
        """Valida que HTML quebrado/truncado não causa quebra catastrófica no DOMAuditor."""
        broken_html = (
            "<html><head><title>Unclosed"
            "<header id='h1'><h1>Header sem fechar"
            "<article class='card'>Texto truncado..."
            "<button id='b1' onclick='broken'>Botão sem fechar"
            "<div><span><nav><ul><li>item"
        )
        auditor = DOMAuditor(force_fallback=True)
        nodes = auditor.inspect_html(broken_html)

        assert len(nodes) >= 3
        tags_found = {n.tag_name for n in nodes}
        assert "header" in tags_found
        assert "h1" in tags_found
        assert "button" in tags_found
