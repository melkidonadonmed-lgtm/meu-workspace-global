"""Testes de integração para os endpoints do API Gateway FastAPI."""

from fastapi.testclient import TestClient

from agents.api_gateway import app

client = TestClient(app)


def test_gateway_health_endpoint():
    """Valida o endpoint /health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-gateway"


def test_gateway_skills_endpoint():
    """Valida o endpoint /skills."""
    response = client.get("/skills")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert len(data["skills"]) >= 2


def test_gateway_chat_endpoint():
    """Valida o endpoint /chat com mensagem válida."""
    payload = {
        "session_id": "test_integration_session",
        "message": "Preciso de uma query SQL para o BigQuery"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["session_id"] == "test_integration_session"


def test_gateway_antigravity_chat_endpoint():
    """Valida o endpoint /antigravity/chat com mensagem válida."""
    payload = {
        "message": "Quais arquivos existem no diretório?"
    }
    response = client.post("/antigravity/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data
    assert "workspace_root" in data


def test_gateway_html_build_endpoint():
    """Valida o endpoint /agents/html/build com uma requisição estruturada mínima."""
    payload = {
        "page_title": "Página de Teste",
        "page_type": "landing_page",
        "styling_framework": "tailwind",
        "components": [
            {"name": "HeaderNav", "type": "organism", "description": "Cabeçalho de navegação principal"}
        ],
    }
    response = client.post("/agents/html/build", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["page_title"] == "Página de Teste"
    assert len(data["assembled_components"]) == 1
    assert "full_html_document" in data
