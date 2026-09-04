"""Suíte de testes unitários para o módulo Semantic Web Researcher.

Valida detalhadamente:
1. Remoção completa de scripts inline, scripts externos e telemetria.
2. Remoção de CSS inline e tags style.
3. Remoção de tags SVG e nós vetoriais.
4. Remoção de tags noscript e nós de comentários HTML.
5. Preservação integral do texto editorial nobre, títulos e links.
6. Validação estrita da criação e imutabilidade de instâncias de SourceReference.
7. Limpeza determinística com a fixture sample_noisy_article.html.
8. Operação offline graciosa e resiliência de rede do WebResearcher.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from web_visual_auditor.exceptions import (
    ResearchError,
    SemanticExtractionError,
)
from web_visual_auditor.models import SourceReference
from web_visual_auditor.researcher import (
    SemanticCleanResult,
    SemanticHTMLCleaner,
    WebResearcher,
)

try:
    from .fixtures import SAMPLE_NOISY_ARTICLE_HTML
except (ImportError, ValueError):
    from fixtures import SAMPLE_NOISY_ARTICLE_HTML  # type: ignore[no-redef]


# ==============================================================================
# 1. Testes do SemanticHTMLCleaner
# ==============================================================================


class TestSemanticHTMLCleaner:
    """Testes de unidade e regressão para o SemanticHTMLCleaner."""

    def test_remove_inline_and_external_scripts_and_telemetry(self) -> None:
        """Valida que scripts inline, externos e códigos de telemetria são expurgados."""
        html = (
            "<div>"
            "<script type='text/javascript'>"
            "window.dataLayer = ['event']; alert('telemetry');"
            "</script>"
            "<script src='https://cdn.example.com/tracker.js' async></script>"
            "<p>Conteúdo editorial legítimo e limpo.</p>"
            "<button onclick=\"sendBeacon('bad')\">Clique aqui</button>"
            "</div>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned_text = cleaner.clean_text(html)

        assert "dataLayer" not in cleaned_text
        assert "alert" not in cleaned_text
        assert "telemetry" not in cleaned_text
        assert "tracker.js" not in cleaned_text
        assert "sendBeacon" not in cleaned_text
        assert "Conteúdo editorial legítimo e limpo." in cleaned_text
        assert "Clique aqui" in cleaned_text

    def test_remove_css_inline_and_style_tags(self) -> None:
        """Valida que tags <style> e declarações CSS são completamente eliminadas."""
        html = (
            "<head>"
            "<style type='text/css'>"
            "body { margin: 0; background-color: #f0f0f0; }"
            ".ad-banner { display: none; }"
            "</style>"
            "</head>"
            "<body>"
            "<style>.inline-style { color: red; }</style>"
            "<h1>Título Editorial</h1>"
            "<p>Texto sob formatação visual.</p>"
            "</body>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned_text = cleaner.clean_text(html)

        assert "margin: 0" not in cleaned_text
        assert "background-color" not in cleaned_text
        assert "ad-banner" not in cleaned_text
        assert "inline-style" not in cleaned_text
        assert "color: red" not in cleaned_text
        assert "Título Editorial" in cleaned_text
        assert "Texto sob formatação visual." in cleaned_text

    def test_remove_svg_and_vector_graphics(self) -> None:
        """Valida que tags SVG e todo o seu conteúdo vetorial são descartados."""
        html = (
            "<div>"
            "<svg width='100' height='100' viewBox='0 0 100 100'>"
            "<circle cx='50' cy='50' r='40' stroke='green' />"
            "<path d='M 10 80 Q 52.5 10, 95 80' />"
            "<text x='10' y='20'>SVG TEXT MUST BE PURGED</text>"
            "</svg>"
            "<p>Parágrafo pós-vetor preservado com sucesso.</p>"
            "</div>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned_text = cleaner.clean_text(html)

        assert "SVG TEXT MUST BE PURGED" not in cleaned_text
        assert "<circle" not in cleaned_text
        assert "viewBox" not in cleaned_text
        assert "Parágrafo pós-vetor preservado com sucesso." in cleaned_text

    def test_remove_noscript_and_comments(self) -> None:
        """Valida que blocos noscript e comentários normais ou condicionais são removidos."""
        html = (
            "<div>"
            "<!-- Comentário inicial do template -->"
            "<noscript>Ative o JavaScript para visualizar este anúncio.</noscript>"
            "<!--[if IE]><div>Aviso legado para Internet Explorer</div><![endif]-->"
            "<article><p>Artigo relevante sobre arquitetura.</p></article>"
            "<!-- Comentário final -->"
            "</div>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned_text = cleaner.clean_text(html)

        assert "Comentário inicial" not in cleaned_text
        assert "Ative o JavaScript" not in cleaned_text
        assert "Internet Explorer" not in cleaned_text
        assert "Comentário final" not in cleaned_text
        assert "Artigo relevante sobre arquitetura." in cleaned_text

    def test_preservation_of_noble_editorial_content(self) -> None:
        """Valida a preservação integral da estrutura editorial nobre."""
        html = (
            "<article>"
            "<h1>Título Principal do Estudo</h1>"
            "<h2>Seção Secundária</h2>"
            "<p>Primeiro parágrafo informativo de introdução ao problema.</p>"
            "<blockquote>Citação importante de um pesquisador renomado.</blockquote>"
            "<ul>"
            "<li>Item 1: Primeira evidência empírica;</li>"
            "<li>Item 2: Segunda evidência corroborada.</li>"
            "</ul>"
            "<p>Conclusão da análise com "
            "<a href='https://example.com/artigo'>link de referência</a>.</p>"
            "</article>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned_text = cleaner.clean_text(html)

        assert "Título Principal do Estudo" in cleaned_text
        assert "Seção Secundária" in cleaned_text
        assert "Primeiro parágrafo informativo de introdução ao problema." in cleaned_text
        assert "Citação importante de um pesquisador renomado." in cleaned_text
        assert "Item 1: Primeira evidência empírica;" in cleaned_text
        assert "Item 2: Segunda evidência corroborada." in cleaned_text
        assert "Conclusão da análise com link de referência." in cleaned_text

    def test_clean_text_normalizes_whitespace(self) -> None:
        """Garante a normalização de quebras de linha múltiplas e espaços redundantes."""
        html = (
            "<p>  Espaçamento   irregular    com \t múltiplos \n\n tabs   e quebras.  </p>"
            "<p>   Segundo   parágrafo  normalizado.  </p>"
        )
        cleaner = SemanticHTMLCleaner()
        cleaned_text = cleaner.clean_text(html)

        assert "   " not in cleaned_text
        assert "\t" not in cleaned_text
        assert "Espaçamento irregular com múltiplos tabs e quebras." in cleaned_text
        assert "Segundo parágrafo normalizado." in cleaned_text

    def test_extract_title_and_snippet(self) -> None:
        """Valida extração precisa de título e snippet representativo."""
        html = (
            "<html><head>"
            "<title>Título na Tag Title</title>"
            "<meta name='description' content='Resumo extraído da meta tag.'>"
            "</head><body>"
            "<h1>Título Alternativo no H1</h1>"
            "<p>Texto completo da página.</p>"
            "</body></html>"
        )
        cleaner = SemanticHTMLCleaner()
        title, snippet = cleaner.extract_title_and_snippet(html)

        assert title == "Título na Tag Title"
        assert snippet == "Resumo extraído da meta tag."

    def test_extract_title_fallback_to_h1(self) -> None:
        """Garante fallback para <h1> quando a tag <title> estiver ausente."""
        html = "<html><body><h1>Título Somente no H1</h1><p>Conteúdo de teste.</p></body></html>"
        cleaner = SemanticHTMLCleaner()
        title, _ = cleaner.extract_title_and_snippet(html)

        assert title == "Título Somente no H1"

    def test_extract_links_as_source_references(self) -> None:
        """Valida a conversão de tags âncora <a> em instâncias de SourceReference."""
        html = (
            "<nav>"
            "<a href='https://example.com/guia' title='Guia Completo'>Clique no Guia</a>"
            "<a href='/artigos/visual-diff'>Diferença Visual</a>"
            "<a href='#ancora-interna'>Ignorar Âncora</a>"
            "<a href='javascript:void(0)'>Ignorar JS</a>"
            "</nav>"
        )
        cleaner = SemanticHTMLCleaner()
        refs = cleaner.extract_links(html, base_url="https://site.local")

        assert len(refs) == 2
        assert refs[0].url == "https://example.com/guia"
        assert refs[0].title == "Guia Completo"
        assert refs[1].url == "https://site.local/artigos/visual-diff"
        assert refs[1].title == "Diferença Visual"

    def test_clean_html_returns_semantic_clean_result(self) -> None:
        """Garante que clean_html suporta uso como string e desempacotamento de tupla."""
        html = (
            "<div>"
            "<script>bad();</script>"
            "<h1>Título</h1>"
            "<p>Texto limpo com <a href='https://example.com'>link</a>.</p>"
            "</div>"
        )
        cleaner = SemanticHTMLCleaner()
        result = cleaner.clean_html(html)

        # 1. Comportamento como String
        assert isinstance(result, SemanticCleanResult)
        assert isinstance(result, str)
        assert "Título" in result
        assert "Texto limpo" in result
        assert "bad();" not in result

        # 2. Atributo .references
        assert len(result.references) == 1
        assert result.references[0].url == "https://example.com"

        # 3. Desempacotamento transparente como tupla (text, refs)
        text, refs = cleaner.clean_html(html)
        assert isinstance(text, str)
        assert "Título" in text
        assert isinstance(refs, list)
        assert len(refs) == 1

    def test_clean_and_extract_explicit_tuple(self) -> None:
        """Valida o método clean_and_extract retornando explicitamente tupla."""
        html = "<h1>Header</h1><a href='https://example.com'>Link</a>"
        cleaner = SemanticHTMLCleaner()
        text, refs = cleaner.clean_and_extract(html)

        assert isinstance(text, str)
        assert "Header" in text
        assert len(refs) == 1
        assert isinstance(refs[0], SourceReference)

    def test_classmethod_clean_shortcut(self) -> None:
        """Garante que o método estático SemanticHTMLCleaner.clean() opera diretamente."""
        html = "<p>Parágrafo simples com <script>console.log(1);</script> script.</p>"
        result = SemanticHTMLCleaner.clean(html)

        assert "Parágrafo simples com script." == result

    def test_clean_html_as_class_method(self) -> None:
        """Garante que SemanticHTMLCleaner.clean_html pode ser chamado sem instanciar."""
        html = "<h1>Título Direto</h1>"
        result = SemanticHTMLCleaner.clean_html(html)

        assert "Título Direto" in result

    def test_parser_fallback_mechanism(self) -> None:
        """Valida que parser inexistente realiza fallback transparente para html.parser."""
        cleaner = SemanticHTMLCleaner(preferred_parser="parser_inexistente_com_certeza")
        soup = cleaner._parse_soup("<p>Fallback funcional</p>")

        assert soup.find("p") is not None
        assert soup.find("p").get_text() == "Fallback funcional"

    def test_deterministic_cleaning_sample_noisy_article(self) -> None:
        """Valida a limpeza determinística completa da fixture sample_noisy_article.html."""
        assert SAMPLE_NOISY_ARTICLE_HTML.exists(), "A fixture deve existir no disco."
        raw_html = SAMPLE_NOISY_ARTICLE_HTML.read_text(encoding="utf-8")

        cleaner = SemanticHTMLCleaner()
        cleaned_text = cleaner.clean_text(raw_html)

        # Asserts de Ausência de Ruído (Zero Contaminação)
        assert "dataLayer" not in cleaned_text
        assert "gtag" not in cleaned_text
        assert "UA-99999999-1" not in cleaned_text
        assert "telemetry beacon" not in cleaned_text.lower()
        assert "ad-banner" not in cleaned_text
        assert "SVG TEXT MUST BE PURGED" not in cleaned_text
        assert "Atenção: Este site requer JavaScript" not in cleaned_text
        assert "Analytics tracking snippet" not in cleaned_text
        assert "Alerta exclusivo para navegadores legados" not in cleaned_text
        assert "adSlots" not in cleaned_text

        # Asserts de Preservação Editorial Nobre
        assert "Revolução na Auditoria Visual de Interfaces Web" in cleaned_text
        assert "Fundamentos da Auditoria Diferencial" in cleaned_text
        assert "automação de inspeção de regressão visual" in cleaned_text
        assert "A verdadeira robustez de um sistema de design" in cleaned_text
        assert "Isolamento Semântico e Remoção de Ruído" in cleaned_text
        assert "Eliminação completa de nós de scripts executáveis" in cleaned_text
        assert "Exclusão de coordenadas vetoriais em elementos SVG embutidos;" in cleaned_text


# ==============================================================================
# 2. Testes do WebResearcher
# ==============================================================================


class TestWebResearcher:
    """Testes de unidade e integração para o WebResearcher."""

    def test_extract_from_html_instantiates_source_reference(self) -> None:
        """Valida extração a partir de string HTML retornando SourceReference rigoroso."""
        raw_html = (
            "<html lang='pt-BR'>"
            "<head>"
            "<title>Auditoria Visual Contínua</title>"
            "<meta name='description' content='Artigo focado em regressão visual.'>"
            "<meta name='author' content='Equipe QA'>"
            "</head>"
            "<body>"
            "<script>telemetry();</script>"
            "<main><p>Conteúdo editorial completo sobre o pipeline.</p></main>"
            "</body>"
            "</html>"
        )
        researcher = WebResearcher()
        ref = researcher.extract_from_html(raw_html, url="https://auditor.local/artigo")

        assert isinstance(ref, SourceReference)
        assert ref.title == "Auditoria Visual Contínua"
        assert ref.url == "https://auditor.local/artigo"
        assert ref.snippet == "Artigo focado em regressão visual."
        assert "Conteúdo editorial completo sobre o pipeline." in ref.cleaned_text
        assert "telemetry" not in ref.cleaned_text
        assert ref.raw_content == raw_html
        assert ref.metadata.get("lang") == "pt-BR"
        assert ref.metadata.get("author") == "Equipe QA"

    def test_clean_raw_html_alias(self) -> None:
        """Garante que o alias clean_raw_html se comporta identicamente a extract_from_html."""
        raw_html = "<h1>Título de Teste</h1><p>Parágrafo de teste.</p>"
        researcher = WebResearcher()
        ref = researcher.clean_raw_html(raw_html, url="file://teste.html", title="Custom Title")

        assert isinstance(ref, SourceReference)
        assert ref.title == "Custom Title"
        assert ref.url == "file://teste.html"
        assert "Parágrafo de teste." in ref.cleaned_text

    def test_extract_from_html_invalid_type_raises_semantic_error(self) -> None:
        """Valida que passar objeto que não seja string levanta SemanticExtractionError."""
        researcher = WebResearcher()
        with pytest.raises(SemanticExtractionError, match="deve ser uma string"):
            researcher.extract_from_html(12345)  # type: ignore[arg-type]

    def test_extract_from_url_file_scheme(self) -> None:
        """Valida extração direta de arquivo local através do esquema file://."""
        researcher = WebResearcher()
        file_url = SAMPLE_NOISY_ARTICLE_HTML.as_uri()
        ref = researcher.extract_from_url(file_url)

        assert isinstance(ref, SourceReference)
        assert ref.url == file_url
        assert "Revolução na Auditoria Visual" in ref.title
        assert "automação de inspeção de regressão visual" in ref.cleaned_text
        assert "dataLayer" not in ref.cleaned_text

    def test_extract_from_url_direct_filesystem_path(self) -> None:
        """Valida extração quando o caminho de um arquivo local é passado diretamente."""
        researcher = WebResearcher()
        ref = researcher.extract_from_url(str(SAMPLE_NOISY_ARTICLE_HTML))

        assert isinstance(ref, SourceReference)
        assert "Revolução na Auditoria Visual" in ref.title
        assert ref.url.startswith("file://")

    def test_extract_from_url_empty_raises_research_error(self) -> None:
        """Valida que URL vazia levanta ResearchError."""
        researcher = WebResearcher()
        with pytest.raises(ResearchError, match="não pode ser vazia"):
            researcher.extract_from_url("")

    def test_extract_from_url_nonexistent_file_raises_research_error(self) -> None:
        """Valida que arquivo inexistente levanta ResearchError."""
        researcher = WebResearcher()
        with pytest.raises(ResearchError, match="não encontrado"):
            researcher.extract_from_url("file:///c:/caminho/com_certeza_inexistente.html")

    def test_extract_from_url_unsupported_scheme_raises_research_error(self) -> None:
        """Valida que esquema de URL não suportado levanta ResearchError."""
        researcher = WebResearcher()
        with pytest.raises(ResearchError, match="não suportado"):
            researcher.extract_from_url("ftp://example.com/archive.zip")

    def test_extract_from_url_http_with_mock_client(self) -> None:
        """Valida recuperação HTTP via cliente mockado com resposta 200 OK."""
        mock_html = (
            "<html><head><title>Mocked Page</title></head>"
            "<body><p>Conteúdo retornado pelo mock.</p></body></html>"
        )

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=mock_html, request=request)

        mock_transport = httpx.MockTransport(mock_handler)
        mock_client = httpx.Client(transport=mock_transport)

        with WebResearcher(http_client=mock_client) as researcher:
            ref = researcher.extract_from_url("https://api.test.local/pagina")

            assert isinstance(ref, SourceReference)
            assert ref.title == "Mocked Page"
            assert "Conteúdo retornado pelo mock." in ref.cleaned_text
            assert ref.url == "https://api.test.local/pagina"

    def test_extract_from_url_http_error_raises_research_error(self) -> None:
        """Valida que erro HTTP (ex: 404) levanta ResearchError adequadamente."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, text="Not Found", request=request)

        mock_transport = httpx.MockTransport(mock_handler)
        mock_client = httpx.Client(transport=mock_transport)

        with (
            WebResearcher(http_client=mock_client) as researcher,
            pytest.raises(ResearchError, match="Falha na requisição HTTP"),
        ):
            researcher.extract_from_url("https://api.test.local/not-found")

    def test_search_offline_mode_deterministic(self) -> None:
        """Valida que a busca em modo offline opera de forma 100% determinística."""
        researcher = WebResearcher(offline_mode=True)
        results = researcher.search("regressão visual", limit=3)

        assert len(results) == 3
        for i, ref in enumerate(results, start=1):
            assert isinstance(ref, SourceReference)
            assert f"#{i}" in ref.title
            assert "regressão visual" in ref.title
            assert ref.metadata.get("source") == "offline_fallback"
            assert ref.metadata.get("rank") == i

    def test_search_and_extract_contract(self) -> None:
        """Valida conformidade com o contrato de interface de PROJECT.md."""
        researcher = WebResearcher(offline_mode=True)
        results = researcher.search_and_extract("pixel a pixel", limit=2)

        assert len(results) == 2
        assert all(isinstance(r, SourceReference) for r in results)

    def test_search_with_registered_mock(self) -> None:
        """Valida que queries com mocks registrados retornam os dados pré-definidos."""
        researcher = WebResearcher()
        mock_ref = SourceReference(
            title="Referência Mockada",
            url="https://mock.test/doc",
            snippet="Snippet customizado de teste",
            cleaned_text="Texto customizado",
        )
        researcher.register_mock_search("query customizada", [mock_ref])

        results = researcher.search("query customizada", limit=5)
        assert len(results) == 1
        assert results[0].title == "Referência Mockada"
        assert results[0].url == "https://mock.test/doc"

    def test_search_graceful_fallback_when_duckduckgo_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Valida que falhas inesperadas na busca DuckDuckGo ativam o fallback gracioso."""
        researcher = WebResearcher(offline_mode=False)

        def mock_text_failing(*args: Any, **kwargs: Any) -> Any:
            raise ConnectionResetError("Conexão interrompida com o servidor")

        try:
            import duckduckgo_search
            monkeypatch.setattr(duckduckgo_search.DDGS, "text", mock_text_failing)
        except ImportError:
            pass

        results = researcher.search("pesquisa com falha de rede", limit=2)
        assert len(results) == 2
        assert results[0].metadata.get("source") == "offline_fallback"

    def test_search_limit_zero_returns_empty_list(self) -> None:
        """Garante que busca com limit <= 0 retorne lista vazia imediatamente."""
        researcher = WebResearcher(offline_mode=True)
        assert researcher.search("teste", limit=0) == []
        assert researcher.search("teste", limit=-1) == []

    def test_context_manager_closes_http_client(self) -> None:
        """Valida o fechamento correto de recursos ao utilizar context manager."""
        with WebResearcher() as researcher:
            client = researcher.http_client
            assert not client.is_closed

        assert client.is_closed
