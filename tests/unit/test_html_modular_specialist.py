"""Suíte de Testes Unitários em Pytest para o Sub-Agente HTMLModularSpecialist.

Módulos testados:
- Schemas Pydantic (ComponentRequirement, HTMLBuildRequest, HTMLBuildResponse, HTMLComponentOutput)
- Inicialização e Instruções de Sistema do Agente
- Método assemble_page() com Mocks e Fallbacks
- Validação de contratos de entrada/saída, manipulação de JSON e edge cases
"""

import json
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from agents.specialized.html_modular_specialist import (
    ComponentRequirement,
    HTMLBuildRequest,
    HTMLBuildResponse,
    HTMLModularSpecialistAgent,
)


@pytest.fixture
def sample_component_requirement() -> ComponentRequirement:
    """Fixture Pytest que fornece um componente individual válido."""
    return ComponentRequirement(
        name="HeaderNav",
        type="organism",
        description="Barra de navegação escura com logo, 4 links e botão CTA de login",
    )


@pytest.fixture
def sample_build_request(sample_component_requirement) -> HTMLBuildRequest:
    """Fixture Pytest que fornece uma solicitação de montagem completa."""
    return HTMLBuildRequest(
        page_title="Dashboard Analytics",
        page_type="dashboard",
        styling_framework="tailwind",
        components=[
            sample_component_requirement,
            ComponentRequirement(
                name="MetricCard",
                type="molecule",
                description="Card estatístico com indicador de alta/baixa",
            ),
        ],
    )


@pytest.fixture
def mock_html_response_json() -> str:
    """Fixture Pytest que retorna a resposta simulada do LLM em formato JSON."""
    payload = {
        "page_title": "Dashboard Analytics",
        "assembled_components": [
            {
                "component_name": "HeaderNav",
                "component_type": "organism",
                "html_code": "<header class='bg-slate-900 text-white p-4'><nav aria-label='Navegação Principal'><a href='#'>Logo</a></nav></header>",
                "usage_notes": "Posicione no topo da página principal.",
            },
            {
                "component_name": "MetricCard",
                "component_type": "molecule",
                "html_code": "<div class='p-6 bg-white shadow rounded-lg'><h3 class='text-sm text-gray-500'>Vendas</h3><p class='text-2xl font-bold'>R$ 45.000</p></div>",
                "usage_notes": "Utilizar dentro de um container CSS Grid.",
            },
        ],
        "full_html_document": "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'><title>Dashboard Analytics</title></head><body></body></html>",
        "accessibility_checklist": [
            "WCAG 2.1 AA: Atributo aria-label presente na tag nav",
            "WCAG 2.1 AA: Contraste mínimo de cor 4.5:1 verificado",
        ],
    }
    return json.dumps(payload)


@pytest.fixture
def agent(mock_html_response_json) -> HTMLModularSpecialistAgent:
    """Fixture Pytest que instancia o sub-agente com o SDK do Gemini mockado."""
    agent_instance = HTMLModularSpecialistAgent(api_key="test_api_key_gemini")
    mock_client = MagicMock()
    mock_generate = MagicMock()
    mock_generate.text = mock_html_response_json
    mock_client.models.generate_content.return_value = mock_generate
    agent_instance.client = mock_client
    return agent_instance


class TestPydanticSchemas:
    """Testes de validação dos contratos Pydantic de entrada e saída."""

    def test_component_requirement_valid(self):
        comp = ComponentRequirement(name="ButtonCTA", type="atom", description="Botão principal")
        assert comp.name == "ButtonCTA"
        assert comp.type == "atom"
        assert comp.description == "Botão principal"

    def test_component_requirement_missing_fields(self):
        with pytest.raises(ValidationError):
            ComponentRequirement(name="IncompleteComponent")  # type: ignore

    def test_html_build_request_defaults(self):
        comp = ComponentRequirement(name="Sidebar", type="organism", description="Menu lateral")
        request = HTMLBuildRequest(
            page_title="Portal Interno",
            page_type="dashboard",
            components=[comp],
        )
        assert request.styling_framework == "tailwind"
        assert len(request.components) == 1

    def test_html_build_response_deserialization(self, mock_html_response_json):
        response = HTMLBuildResponse.model_validate_json(mock_html_response_json)
        assert response.page_title == "Dashboard Analytics"
        assert len(response.assembled_components) == 2
        assert response.assembled_components[0].component_name == "HeaderNav"
        assert len(response.accessibility_checklist) == 2


class TestAgentInitialization:
    """Testes do construtor e diretrizes do sistema do sub-agente."""

    def test_init_with_explicit_api_key(self):
        agent_obj = HTMLModularSpecialistAgent(api_key="custom_key_abc123")
        assert agent_obj.api_key == "custom_key_abc123"

    def test_init_with_env_variable(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "env_key_xyz987")
        agent_obj = HTMLModularSpecialistAgent()
        assert agent_obj.api_key == "env_key_xyz987"

    def test_system_instruction_content(self, agent):
        instruction = agent._get_system_instruction()
        assert "HTMLModularSpecialist" in instruction
        assert "WCAG 2.1 AA" in instruction
        assert "Tailwind CSS" in instruction
        assert "JSON" in instruction


class TestAgentExecutionAndMocking:
    """Testes de execução do método assemble_page utilizando Mocks e Fallback."""

    def test_assemble_page_successful_call(self, agent, sample_build_request):
        result = agent.assemble_page(sample_build_request)

        assert agent.client.models.generate_content.call_count == 1
        assert isinstance(result, HTMLBuildResponse)
        assert result.page_title == "Dashboard Analytics"
        assert len(result.assembled_components) == 2

    def test_assemble_page_prompt_formatting(self, agent, sample_build_request):
        agent.assemble_page(sample_build_request)

        call_kwargs = agent.client.models.generate_content.call_args.kwargs
        prompt_sent = call_kwargs["contents"]

        assert "Dashboard Analytics" in prompt_sent
        assert "dashboard" in prompt_sent
        assert "tailwind" in prompt_sent
        assert "[ORGANISM] HeaderNav" in prompt_sent
        assert "[MOLECULE] MetricCard" in prompt_sent

    def test_assemble_page_fallback_deterministic(self, sample_build_request):
        agent_offline = HTMLModularSpecialistAgent(api_key="mock")
        result = agent_offline.assemble_page(sample_build_request)

        assert isinstance(result, HTMLBuildResponse)
        assert result.page_title == "Dashboard Analytics"
        assert len(result.assembled_components) == 2
        assert "<!DOCTYPE html>" in result.full_html_document
        assert "lang=\"pt-BR\"" in result.full_html_document

    def test_assemble_page_handles_invalid_json(self, agent, sample_build_request):
        mock_bad_response = MagicMock()
        mock_bad_response.text = "SAIDA_INVALIDA_NAO_JSON"
        agent.client.models.generate_content.return_value = mock_bad_response

        with pytest.raises(ValidationError):
            agent.assemble_page(sample_build_request)
