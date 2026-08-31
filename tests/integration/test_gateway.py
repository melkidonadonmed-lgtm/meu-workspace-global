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
