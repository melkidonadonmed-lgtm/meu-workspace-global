.PHONY: setup dev gateway mcp test lint clean help

PYTHONPATH := .

help:
	@echo "Comandos Disponíveis:"
	@echo "  make setup       - Instala dependências Python e Node.js em modo editável"
	@echo "  make dev         - Inicia API Gateway e Servidor FastMCP em paralelo"
	@echo "  make gateway     - Inicia apenas o API Gateway FastAPI (porta 8000)"
	@echo "  make mcp         - Inicia o Servidor FastMCP via stdio"
	@echo "  make mcp-sse     - Inicia o Servidor FastMCP via SSE (porta 8080)"
	@echo "  make test        - Executa a suíte de testes com pytest"
	@echo "  make lint        - Executa verificações com Ruff"
	@echo "  make clean       - Remove caches e temporários"

setup:
	@test -f .env || cp configs/.env.example .env
	pip install -e ".[dev]"
	@if [ -d "projects/canvas_ide" ]; then cd projects/canvas_ide && npm install; fi

dev:
	PYTHONPATH=$(PYTHONPATH) python -m mcp_servers.server --transport sse --port 8080 &
	PYTHONPATH=$(PYTHONPATH) python -m uvicorn agents.api_gateway:app --host 0.0.0.0 --port 8000 --reload

gateway:
	PYTHONPATH=$(PYTHONPATH) python -m uvicorn agents.api_gateway:app --host 0.0.0.0 --port 8000 --reload

mcp:
	PYTHONPATH=$(PYTHONPATH) python -m mcp_servers.server --transport stdio

mcp-sse:
	PYTHONPATH=$(PYTHONPATH) python -m mcp_servers.server --transport sse --port 8080

test:
	PYTHONPATH=$(PYTHONPATH) pytest tests -v --tb=short

lint:
	ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
