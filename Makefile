.PHONY: setup agent-go test test-workspace sync-skills lint clean help

PYTHONPATH := .

help:
	@echo "Comandos Disponíveis:"
	@echo "  make setup          - Instala dependências Python, Node.js e Go"
	@echo "  make agent-go       - Executa o agente de chamados em Go (ADK v2)"
	@echo "  make test-workspace - Executa os testes internos do workspace"
	@echo "  make sync-skills    - Sincroniza o catálogo plano de skills (published_skills)"
	@echo "  make test           - Executa a suíte de testes (pytest + go test)"
	@echo "  make lint           - Executa verificações com Ruff"
	@echo "  make clean          - Remove caches e temporários"

setup:
	@test -f .env || cp configs/.env.example .env
	pip install -e ".[dev]"
	@if [ -d "agents/specialized/customer_issue_reviewer_go" ]; then cd agents/specialized/customer_issue_reviewer_go && go mod tidy; fi
	@if [ -d "projects/canvas_ide" ]; then cd projects/canvas_ide && npm install; fi

agent-go:
	cd agents/specialized/customer_issue_reviewer_go && go run main.go

sync-skills:
	uv run python scripts/sync_flat_catalog.py

test-workspace:
	uv run pytest tests/unit -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"

test:
	uv run pytest tests/unit -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
	@if [ -d "agents/specialized/customer_issue_reviewer_go" ]; then cd agents/specialized/customer_issue_reviewer_go && go test ./... -v; fi

lint:
	ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
