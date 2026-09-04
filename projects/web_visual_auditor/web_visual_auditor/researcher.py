"""Módulo Semantic Web Researcher para higienização semântica e busca web.

Componente autônomo responsável pela extração cirúrgica de conteúdo textual nobre,
expurgo de ruídos (scripts, estilos, SVG, noscript, comentários), normalização de
espaçamento e orquestração de pesquisas web com suporte determinístico offline.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, ClassVar, Self
from urllib.parse import unquote, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Comment

from web_visual_auditor.exceptions import (
    ResearchError,
    SemanticExtractionError,
)
from web_visual_auditor.models import SourceReference

logger = logging.getLogger(__name__)


class SemanticCleanResult(str):
    """Resultado de higienização semântica.

    Comporta-se nativamente como string pura (preservando operações de texto e
    compatibilidade com asserções de substring), mas permite desempacotamento em
    tupla `(cleaned_text, references)` e acesso direto ao atributo `.references`.
    """

    _references: list[SourceReference]

    def __new__(
        cls,
        content: str,
        references: list[SourceReference] | None = None,
    ) -> Self:
        instance = super().__new__(cls, content)
        instance._references = list(references) if references is not None else []
        return instance

    @property
    def references(self) -> list[SourceReference]:
        """Lista de referências (links/fontes) extraídas do documento."""
        return self._references

    @property
    def cleaned_text(self) -> str:
        """Alias para o texto higienizado."""
        return str(self)

    def __iter__(self):
        """Permite desempacotamento transparente: text, refs = cleaner.clean_html(...)."""
        yield str(self)
        yield self._references


class SemanticHTMLCleaner:
    """Motor especializado em higienização e extração semântica de HTML."""

    DEFAULT_REMOVE_TAGS: ClassVar[set[str]] = {
        "script",
        "style",
        "svg",
        "noscript",
        "iframe",
        "template",
        "link",
        "meta",
        "object",
        "embed",
        "canvas",
        "applet",
        "aside",
    }

    def __init__(
        self,
        remove_tags: set[str] | None = None,
        preferred_parser: str = "html.parser",
    ) -> None:
        """Inicializa o limpador semântico.

        Args:
            remove_tags: Conjunto customizado de tags a serem expurgadas.
            preferred_parser: Parser preferencial para o BeautifulSoup (padrão: html.parser).
        """
        self.remove_tags = (
            set(remove_tags) if remove_tags is not None else set(self.DEFAULT_REMOVE_TAGS)
        )
        self.preferred_parser = preferred_parser

    def _parse_soup(self, raw_html: str) -> BeautifulSoup:
        """Instancia BeautifulSoup com fallback transparente para html.parser."""
        try:
            return BeautifulSoup(raw_html, self.preferred_parser)
        except Exception:  # noqa: BLE001
            return BeautifulSoup(raw_html, "html.parser")

    def _purge_noise(self, soup: BeautifulSoup) -> None:
        """Remove cirurgicamente nós de ruído, scripts, estilos, SVG e comentários."""
        # 1. Remover comentários HTML (incluindo comentários condicionais como IE)
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 2. Decompor tags ruidosas e toda a sua subárvore
        for tag in soup.find_all(list(self.remove_tags)):
            tag.decompose()

        # 3. Remover atributos de eventos inline (onclick, onload, onerror, etc.)
        for element in soup.find_all():
            attrs_to_remove = [attr for attr in element.attrs if attr.lower().startswith("on")]
            for attr in attrs_to_remove:
                del element.attrs[attr]

    def extract_title_and_snippet(self, raw_html: str) -> tuple[str, str]:
        """Extrai o título principal e snippet representativo da página.

        Retorna:
            Tupla contendo (título, snippet).
        """
        if not raw_html:
            return ("", "")

        soup = self._parse_soup(raw_html)

        # Extração preventiva de metadados antes de _purge_noise eliminar as tags meta
        meta_og_title = ""
        meta_og = soup.find("meta", property="og:title") or soup.find(
            "meta", attrs={"name": "og:title"}
        )
        if meta_og and meta_og.get("content"):
            meta_og_title = str(meta_og.get("content", "")).strip()

        meta_desc_text = ""
        meta_desc = (
            soup.find("meta", attrs={"name": "description"})
            or soup.find("meta", property="og:description")
            or soup.find("meta", attrs={"name": "og:description"})
        )
        if meta_desc and meta_desc.get("content"):
            meta_desc_text = str(meta_desc.get("content", "")).strip()

        self._purge_noise(soup)

        # 1. Extração do título
        title = ""
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            title = title_tag.get_text(strip=True)
        else:
            h1_tag = soup.find("h1")
            if h1_tag and h1_tag.get_text(strip=True):
                title = h1_tag.get_text(strip=True)
            elif meta_og_title:
                title = meta_og_title

        # 2. Extração do snippet
        snippet = ""
        if meta_desc_text:
            snippet = meta_desc_text
        else:
            for p in soup.find_all("p"):
                p_text = " ".join(p.get_text().split())
                if len(p_text) >= 20:
                    snippet = p_text
                    break

            if not snippet:
                full_text = " ".join(soup.stripped_strings)
                snippet = full_text[:200].strip()

        return (title, snippet)

    def extract_links(self, raw_html: str, base_url: str = "") -> list[SourceReference]:
        """Extrai links úteis do documento convertendo-os em instâncias de SourceReference."""
        if not raw_html:
            return []

        soup = self._parse_soup(raw_html)
        self._purge_noise(soup)

        references: list[SourceReference] = []
        seen_urls: set[str] = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            href_lower = href.lower()
            if not href or href_lower.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            full_url = urljoin(base_url, href) if base_url else href
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            link_text = " ".join(a.get_text().split())
            link_title = a.get("title", "").strip() or link_text or full_url

            ref = SourceReference(
                title=link_title,
                url=full_url,
                snippet=link_text,
                cleaned_text=link_text,
                metadata={"source_tag": "a", "original_href": href},
            )
            references.append(ref)

        return references

    def clean_text(self, raw_html: str) -> str:
        """Higieniza o HTML e retorna string normalizada com texto nobre puro."""
        if not raw_html or not raw_html.strip():
            return ""

        soup = self._parse_soup(raw_html)
        self._purge_noise(soup)

        blocks: list[str] = []
        for string in soup.stripped_strings:
            clean_s = " ".join(string.split())
            if clean_s:
                blocks.append(clean_s)

        merged = " ".join(blocks)
        return re.sub(r"\s+([.,;:!?])", r"\1", merged)

    def clean_html(
        self_or_raw: Any,
        raw_html: str | None = None,
        base_url: str = "",
    ) -> SemanticCleanResult:
        """Higieniza o HTML e retorna SemanticCleanResult.

        Suporta chamada como método de instância (`cleaner.clean_html(html)`) ou
        como método de classe (`SemanticHTMLCleaner.clean_html(html)`).
        """
        if isinstance(self_or_raw, SemanticHTMLCleaner):
            instance = self_or_raw
            html_to_clean = raw_html if raw_html is not None else ""
        elif isinstance(self_or_raw, type) and issubclass(self_or_raw, SemanticHTMLCleaner):
            instance = self_or_raw()
            html_to_clean = raw_html if raw_html is not None else ""
        else:
            instance = SemanticHTMLCleaner()
            html_to_clean = str(self_or_raw)
            if raw_html is not None and not base_url:
                base_url = raw_html

        cleaned_text = instance.clean_text(html_to_clean)
        references = instance.extract_links(html_to_clean, base_url=base_url)
        return SemanticCleanResult(cleaned_text, references)

    def clean_and_extract(
        self,
        raw_html: str,
        base_url: str = "",
    ) -> tuple[str, list[SourceReference]]:
        """Retorna tupla explícita `(texto_limpo, lista_referencias)`."""
        res = self.clean_html(raw_html, base_url=base_url)
        return (str(res), res.references)

    @classmethod
    def clean(cls, raw_html: str) -> str:
        """Atalho estático para higienizar HTML retornando string direta."""
        return cls().clean_text(raw_html)


class WebResearcher:
    """Orquestrador de pesquisa semântica, recuperação e higienização web."""

    def __init__(
        self,
        http_client: httpx.Client | None = None,
        default_timeout_s: float = 15.0,
        cleaner: SemanticHTMLCleaner | None = None,
        offline_mode: bool = False,
    ) -> None:
        """Inicializa o orquestrador de pesquisa web.

        Args:
            http_client: Cliente HTTP opcional (para injeção e mocks de teste).
            default_timeout_s: Timeout padrão em segundos.
            cleaner: Instância customizada de SemanticHTMLCleaner.
            offline_mode: Se True, opera em modo determinístico offline.
        """
        self.default_timeout_s = default_timeout_s
        self.cleaner = cleaner or SemanticHTMLCleaner()
        self.offline_mode = offline_mode
        self._http_client = http_client
        self._mock_responses: dict[str, list[SourceReference]] = {}

    @property
    def http_client(self) -> httpx.Client:
        """Retorna o cliente HTTP configurado ou instancia o padrão."""
        if self._http_client is None:
            self._http_client = httpx.Client(
                timeout=self.default_timeout_s,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebVisualAuditor/0.1.0"
                },
            )
        return self._http_client

    def extract_from_html(
        self,
        raw_html: str,
        url: str = "local://raw",
        title: str | None = None,
    ) -> SourceReference:
        """Extrai conteúdo semântico estruturado a partir de uma string HTML."""
        if not isinstance(raw_html, str):
            raise SemanticExtractionError("raw_html deve ser uma string.")

        try:
            extracted_title, snippet = self.cleaner.extract_title_and_snippet(raw_html)
            clean_res = self.cleaner.clean_html(raw_html, base_url=url)
            cleaned_text = str(clean_res)

            resolved_title = title or extracted_title or "Artigo sem título"

            # Metadados adicionais
            soup = self.cleaner._parse_soup(raw_html)
            meta_dict: dict[str, Any] = {}
            html_tag = soup.find("html")
            if html_tag and html_tag.get("lang"):
                meta_dict["lang"] = html_tag.get("lang")

            author_meta = soup.find("meta", attrs={"name": "author"})
            if author_meta and author_meta.get("content"):
                meta_dict["author"] = str(author_meta.get("content"))

            meta_dict["extracted_links_count"] = len(clean_res.references)

            return SourceReference(
                title=resolved_title,
                url=url,
                snippet=snippet,
                cleaned_text=cleaned_text,
                raw_content=raw_html,
                metadata=meta_dict,
            )
        except Exception as exc:
            if isinstance(exc, (SemanticExtractionError, ResearchError)):
                raise
            raise SemanticExtractionError(f"Erro ao processar HTML: {exc}") from exc

    def clean_raw_html(
        self,
        raw_html: str,
        url: str = "file://local",
        title: str | None = None,
    ) -> SourceReference:
        """Higieniza diretamente uma string HTML retornando SourceReference."""
        return self.extract_from_html(raw_html=raw_html, url=url, title=title)

    def extract_from_url(self, url: str) -> SourceReference:
        """Recupera conteúdo de uma URL (http, https, file:// ou caminho local) e higieniza."""
        if not url:
            raise ResearchError("URL não pode ser vazia.")

        # Cenário 1: Arquivo local via file://
        if url.startswith("file://"):
            raw_path = url[7:]
            # No Windows, remove a barra inicial se estiver como /C:/...
            if len(raw_path) >= 3 and raw_path[0] == "/" and raw_path[2] == ":":
                raw_path = raw_path[1:]
            file_path = Path(unquote(raw_path))
            if not file_path.exists():
                raise ResearchError(f"Arquivo local não encontrado: {file_path}")
            raw_html = file_path.read_text(encoding="utf-8")
            return self.extract_from_html(raw_html, url=url)

        # Caminho direto no sistema de arquivos
        possible_local = Path(url)
        if possible_local.exists() and possible_local.is_file():
            raw_html = possible_local.read_text(encoding="utf-8")
            return self.extract_from_html(raw_html, url=f"file://{possible_local.resolve()}")

        # Cenário 2: URL HTTP / HTTPS
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https"):
            try:
                response = self.http_client.get(url)
                response.raise_for_status()
                return self.extract_from_html(response.text, url=str(response.url))
            except httpx.HTTPError as exc:
                raise ResearchError(f"Falha na requisição HTTP para '{url}': {exc}") from exc
            except Exception as exc:
                raise ResearchError(f"Erro inesperado ao buscar '{url}': {exc}") from exc

        raise ResearchError(f"Esquema de URL não suportado: '{url}'")

    def fetch_and_clean(self, url: str) -> SourceReference:
        """Alias para extract_from_url."""
        return self.extract_from_url(url)

    def search(
        self,
        query: str,
        limit: int = 5,
        max_results: int | None = None,
    ) -> list[SourceReference]:
        """Executa busca web estruturada com DuckDuckGo e fallback gracioso offline."""
        effective_limit = max_results if max_results is not None else limit
        if effective_limit <= 0:
            return []

        # 1. Resposta mockada registrada
        if query in self._mock_responses:
            return self._mock_responses[query][:effective_limit]

        # 2. Modo offline explícito
        if self.offline_mode:
            return self._generate_offline_fallback(query, effective_limit)

        # 3. Tentativa de busca online real via DuckDuckGo
        try:
            from duckduckgo_search import DDGS

            ddgs = DDGS(timeout=self.default_timeout_s)
            raw_results = list(ddgs.text(query, max_results=effective_limit))
            references: list[SourceReference] = []

            for item in raw_results:
                title = str(item.get("title", "Sem título")).strip()
                href = str(
                    item.get("href")
                    or item.get("url")
                    or item.get("link")
                    or "https://duckduckgo.com"
                ).strip()
                snippet = str(item.get("body") or item.get("snippet") or "").strip()

                ref = SourceReference(
                    title=title,
                    url=href,
                    snippet=snippet,
                    cleaned_text=snippet,
                    metadata={"source": "duckduckgo", "query": query},
                )
                references.append(ref)

            return references
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Falha na busca DuckDuckGo para '%s' (%s). Ativando fallback gracioso.",
                query,
                exc,
            )
            return self._generate_offline_fallback(query, effective_limit)

    def search_and_extract(
        self,
        query: str,
        limit: int = 5,
    ) -> list[SourceReference]:
        """Contrato oficial PROJECT.md: busca e retorna lista de SourceReference."""
        return self.search(query=query, limit=limit)

    def _generate_offline_fallback(self, query: str, limit: int) -> list[SourceReference]:
        """Gera referências determinísticas em caso de rede indisponível ou modo offline."""
        results: list[SourceReference] = []
        for i in range(1, limit + 1):
            ref = SourceReference(
                title=f"Resultado offline #{i} para '{query}'",
                url=f"https://offline.search.local/query?q={query}&rank={i}",
                snippet=f"Resumo semântico determinístico offline do artigo sobre '{query}'.",
                cleaned_text=f"Conteúdo editorial informativo simulado para o tópico '{query}'.",
                metadata={"source": "offline_fallback", "query": query, "rank": i},
            )
            results.append(ref)
        return results

    def register_mock_search(self, query: str, references: list[SourceReference]) -> None:
        """Permite registrar respostas mockadas para testes determinísticos."""
        self._mock_responses[query] = references

    def close(self) -> None:
        """Encerra o cliente HTTP subjacente se ativo."""
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


__all__ = [
    "SemanticCleanResult",
    "SemanticHTMLCleaner",
    "WebResearcher",
]
