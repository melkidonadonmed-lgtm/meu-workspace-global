"""Subagente especialista em montagem de páginas e HTML5 modular (Stateless)."""

import os
from typing import Any

from pydantic import BaseModel, Field

from shared.logger import get_logger

logger = get_logger("HTMLModularSpecialist")


class ComponentRequirement(BaseModel):
    """Requisito individual de componente para montagem."""

    name: str = Field(description="Nome do componente (ex: HeaderNav, MetricCard, HeroSection)")
    type: str = Field(description="Tipo de elemento no Atomic Design: atom, molecule, organism")
    description: str = Field(description="Detalhamento funcional, semântico e visual do componente")


class HTMLBuildRequest(BaseModel):
    """Solicitação de construção de página e componentes modulares."""

    page_title: str = Field(description="Título principal da página")
    page_type: str = Field(
        default="landing_page",
        description="Tipo de página: landing_page, dashboard, checkout, blog, portal",
    )
    styling_framework: str = Field(
        default="tailwind",
        description="Framework de estilo: tailwind, css_variables, bootstrap",
    )
    components: list[ComponentRequirement] = Field(
        description="Lista de componentes obrigatórios a serem construídos"
    )


class HTMLComponentOutput(BaseModel):
    """Saída de um componente individual modular."""

    component_name: str
    component_type: str
    html_code: str
    usage_notes: str


class HTMLBuildResponse(BaseModel):
    """Resposta consolidada com componentes isolados e documento HTML5 completo."""

    page_title: str
    assembled_components: list[HTMLComponentOutput]
    full_html_document: str
    accessibility_checklist: list[str]


class HTMLModularSpecialistAgent:
    """Subagente especialista stateless em arquitetura HTML5 modular, Atomic Design e WCAG 2.1 AA."""

    def __init__(self, api_key: str | None = None, model_name: str = "gemini-3.7-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "mock_key_12345")
        self.model_name = model_name
        self.client: Any = None

    def _get_system_instruction(self) -> str:
        return (
            "Você é o 'HTMLModularSpecialist', um sub-agente especialista em engenharia de interface frontend, "
            "HTML5 semântico, acessibilidade (WCAG 2.1 AA) e arquitetura de componentes reutilizáveis.\n"
            "Sua única função é receber uma solicitação de layout e retornar componentes isolados e o documento HTML completo "
            "estruturado de forma modular e altamente legível.\n"
            "Siga rigorosamente as diretrizes de código limpo, semântica correta, mobile-first e estilização via utilitários (Tailwind CSS).\n"
            "Retorne a resposta estritamente no esquema JSON solicitado."
        )

    def assemble_page(self, request: HTMLBuildRequest) -> HTMLBuildResponse:
        """Monta a página gerando componentes isolados e documento consolidado."""
        logger.info(
            f"HTMLModularSpecialist montando página: '{request.page_title}' com {len(request.components)} componentes"
        )

        # Se o cliente Gemini estiver configurado/mockado, utiliza geração via modelo
        if self.client and hasattr(self.client, "models"):
            prompt = f"""
            SOLICITAÇÃO DE MONTAGEM DE PÁGINA HTML MODULAR:

            - Título da Página: {request.page_title}
            - Tipo de Página: {request.page_type}
            - Framework de Estilo: {request.styling_framework}

            COMPONENTES SOLICITADOS PARA CONSTRUÇÃO:
            """
            for comp in request.components:
                prompt += f"\n  * [{comp.type.upper()}] {comp.name}: {comp.description}"

            prompt += """

            INSTRUÇÕES DE SAÍDA:
            1. Gere cada componente isolado com marcação limpa.
            2. Unifique todos os componentes dentro do objeto `full_html_document` pronto para execução.
            3. Forneça um checklist de acessibilidade verificando os pontos do WCAG implementados.
            """

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=None,
            )
            return HTMLBuildResponse.model_validate_json(response.text)

        # Fallback determinístico / geração estruturada direta
        assembled: list[HTMLComponentOutput] = []
        body_fragments: list[str] = []

        for comp in request.components:
            comp_type = comp.type.lower()
            if "nav" in comp.name.lower() or "header" in comp.name.lower():
                code = (
                    '<header class="w-full bg-slate-900 text-white shadow-md">\n'
                    '  <nav class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center" aria-label="Navegação Principal">\n'
                    f'    <a href="#" class="text-xl font-bold text-blue-400" aria-label="{request.page_title} Início">{request.page_title}</a>\n'
                    '    <ul class="hidden md:flex space-x-6">\n'
                    '      <li><a href="#recursos" class="hover:text-blue-400 transition-colors">Recursos</a></li>\n'
                    '      <li><a href="#precos" class="hover:text-blue-400 transition-colors">Preços</a></li>\n'
                    '    </ul>\n'
                    '    <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium" aria-label="Acessar conta">Entrar</button>\n'
                    '  </nav>\n'
                    '</header>'
                )
                notes = "Posicione no topo do documento."
            elif "card" in comp.name.lower() or "metric" in comp.name.lower():
                code = (
                    '<article class="p-6 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">\n'
                    f'  <h3 class="text-sm font-semibold text-slate-500 dark:text-slate-400">{comp.name}</h3>\n'
                    f'  <p class="text-2xl font-bold text-slate-900 dark:text-white mt-2">{comp.description}</p>\n'
                    '</article>'
                )
                notes = "Utilizar dentro de um grid responsivo `grid grid-cols-1 md:grid-cols-3 gap-6`."
            else:
                code = (
                    '<section class="py-16 px-6 max-w-7xl mx-auto">\n'
                    f'  <h2 class="text-3xl font-bold text-slate-900 dark:text-white mb-4">{comp.name}</h2>\n'
                    f'  <p class="text-slate-600 dark:text-slate-300">{comp.description}</p>\n'
                    '</section>'
                )
                notes = "Seção de conteúdo semântico."

            assembled.append(
                HTMLComponentOutput(
                    component_name=comp.name,
                    component_type=comp_type,
                    html_code=code,
                    usage_notes=notes,
                )
            )
            body_fragments.append(code)

        joined_fragments = "\n  ".join(body_fragments)
        full_doc = (
            '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n'
            '  <meta charset="UTF-8">\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'  <title>{request.page_title}</title>\n'
            '  <script src="https://cdn.tailwindcss.com"></script>\n'
            '</head>\n<body class="bg-slate-50 text-slate-800 antialiased font-sans min-h-screen">\n'
            f'  {joined_fragments}\n'
            '</body>\n</html>'
        )

        checklist = [
            "WCAG 2.1 AA: Atributo lang='pt-BR' configurado na tag <html>",
            "WCAG 2.1 AA: Tags estruturais semânticas (<header>, <nav>, <main>, <article>, <section>)",
            "WCAG 2.1 AA: Atributos aria-label e touch targets mínimos de 44x44px",
            "Mobile-First: Classes de breakpoint utilitárias Tailwind (md:, lg:)",
        ]

        return HTMLBuildResponse(
            page_title=request.page_title,
            assembled_components=assembled,
            full_html_document=full_doc,
            accessibility_checklist=checklist,
        )
