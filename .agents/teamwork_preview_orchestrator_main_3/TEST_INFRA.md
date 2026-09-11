# E2E Test Infra: Code Intelligence Agent

## Test Philosophy
- Opaque-box, requirement-driven e determinístico.
- Cobertura em 4 Tiers:
  - Tier 1: Feature Coverage (Ferramentas de inspeção, leitura, AST e patch)
  - Tier 2: Boundary & Corner Cases (Tentativas de path traversal, caracteres especiais, erros sintáticos em dry-run, arquivos vazios ou gigantes)
  - Tier 3: Cross-Feature Combinations (Fluxos encadeados: inspeção -> leitura -> detecção de anomalia -> patch -> guardrail)
  - Tier 4: Real-World Scenarios (Quality Flywheel multi-turn com 5 cenários completos em `tests/eval/datasets/`)

## Test Architecture
- Test runner: `uv run pytest tests -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"`
- Eval runner: `uv run python -m tests.eval.eval_runner`
- Pass/Fail Semantics:
  - 100% de aprovação no pytest (0 falhas, 0 erros).
  - Linter Ruff com 0 violações (`uv run ruff check .`).
  - Quality Flywheel: `multi_turn_task_success >= 0.85` e `multi_turn_tool_use_quality >= 0.80`.
  - Relatórios `results_*.json` e `results_*.html` gerados com sucesso em `artifacts/grade_results/`.
