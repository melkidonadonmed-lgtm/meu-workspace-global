.PHONY: setup agent-go test test-workspace ci-test-workspace sync-skills lint ci-lint clean help

PYTHONPATH := .
CI_PYTEST_BASETEMP := /tmp/pytest_tmp
CI_TEST_FILES := \
	tests/unit/test_code_consistency_specialist.py \
	tests/unit/test_custom_agents_healthcheck.py \
	tests/unit/test_ecosystem_healthcheck.py \
	tests/unit/test_headless_runner.py \
	tests/unit/test_html_output.py \
	tests/unit/test_plugins_and_skills_spec.py \
	tests/unit/test_repository_git_hygiene.py \
	tests/unit/test_skills_healthcheck.py
CI_RUFF_TARGETS := agents ecosystem_healthcheck.py $(CI_TEST_FILES)

help:
	@echo "Comandos Disponíveis:"
	@echo "  make setup          - Instala dependências Python, Node.js e Go"
	@echo "  make agent-go       - Executa o agente de chamados em Go (ADK v2)"
	@echo "  make test-workspace - Executa os testes internos do workspace"
	@echo "  make ci-test-workspace - Executa a suíte autocontida usada no CI Linux"
	@echo "  make sync-skills    - Sincroniza o catálogo plano de skills (published_skills)"
	@echo "  make test           - Executa a suíte de testes (pytest + go test)"
	@echo "  make lint           - Executa verificações com Ruff"
	@echo "  make ci-lint        - Executa o escopo de lint usado no CI Linux"
	@echo "  make clean          - Remove caches e temporários"

setup:
	uv sync --extra dev

agent-go:
	cd agents/specialized/customer_issue_reviewer_go && go run main.go

sync-skills:
	uv run python scripts/sync_flat_catalog.py

test-workspace:
	uv run pytest tests/unit -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"

ci-test-workspace:
	uv run pytest $(CI_TEST_FILES) -v --tb=short --basetemp="$(CI_PYTEST_BASETEMP)"

test:
	uv run pytest tests/unit -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
	@if [ -d "agents/specialized/customer_issue_reviewer_go" ]; then cd agents/specialized/customer_issue_reviewer_go && go test ./... -v; fi

lint:
	uv run ruff check agents scripts tests ecosystem_healthcheck.py

ci-lint:
	uv run ruff check $(CI_RUFF_TARGETS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
