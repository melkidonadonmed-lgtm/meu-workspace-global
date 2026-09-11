# Code Intelligence & Tool Calling Agent

Sistema autônomo de inteligência e engenharia de código para ambiente de produção, integrando o **Google Agent Development Kit (ADK 2.9.0)** e o **Google Antigravity SDK**, dotado de guardrails de segurança Zero-Trust (prevenção de path traversal, bloqueio de comandos destrutivos e mascaramento de PII/credenciais), ferramentas determinísticas de análise estática AST e uma suíte completa de avaliação automatizada baseada no Quality Flywheel (`agents-cli eval`).

---

## 🏛️ Arquitetura do Sistema

```
projects/code_intelligence_agent/
├── pyproject.toml                     # Configuração hatchling e dependências uv
├── README.md                          # Documentação arquitetural e de uso (PT-BR)
├── .env.example                       # Modelo de variáveis de ambiente
├── app/                               # Pacote canônico do agente ADK (App name="app")
│   ├── __init__.py                    # Inicializador do pacote e exportações
│   ├── agent.py                       # Configuração do root_agent e ADK App
│   ├── tools.py                       # Ferramentas determinísticas de código e AST
│   ├── guardrails.py                  # Guardrails e interceptadores de ciclo de vida
│   ├── fast_api_app.py                # Wrapper FastAPI e endpoints HTTP
│   └── cli.py                         # Interface de linha de comando CLI (code-intel)
├── artifacts/
│   └── grade_results/                 # Relatórios de avaliação (results_*.json e .html)
└── tests/
    ├── conftest.py                    # Fixtures e isolamento de testes
    ├── unit/                          # Testes unitários (ferramentas e guardrails)
    ├── integration/                   # Testes de integração (CLI e API)
    └── eval/                          # Suíte Quality Flywheel (R3)
        ├── datasets/
        │   └── code_intelligence_multi_turn.json
        ├── eval_config.yaml
        └── eval_runner.py
```

---

## 🔧 Ferramentas Determinísticas de Código

1. **`inspect_directory(directory_path: str, max_depth: int) -> dict[str, Any]`**
   - Varre a estrutura de arquivos e diretórios respeitando limites de profundidade.
   - Poda automática de pastas irrelevantes (`.git`, `__pycache__`, `.venv`, `node_modules`).
   - Retorno estruturado com metadados de cada nó e contadores totais.

2. **`read_code_file(file_path: str, start_line: int, end_line: int) -> dict[str, Any]`**
   - Leitura de arquivos de código com paginação segura e numeração 1-indexed.
   - Validação de arquivos inexistentes ou fora de limites.

3. **`analyze_ast_anomalies(file_path: str) -> dict[str, Any]`**
   - Análise estática avançada via árvore sintática abstrata (`ast` do Python 3.12).
   - Detecção de erros sintáticos (`SyntaxError`).
   - Identificação de `except:` genérico ou desprotegido (BLE001).
   - Cálculo da complexidade ciclomática de McCabe (alerta para complexidade > 10).
   - Identificação de funções monolíticas (> 60 linhas físicas).
   - Detecção de chamadas perigosas (`eval()`, `exec()`, `__import__()`, `os.system()`).

4. **`generate_unified_patch(file_path: str, original_snippet: str, replacement_snippet: str) -> dict[str, Any]`**
   - Substituição precisa e geração de diff unificado (`difflib.unified_diff`).
   - **Validação AST Pré-Gravação (Dry-Run)**: rejeita sumariamente alterações que introduzam erros sintáticos antes de gravar no disco.

---

## 🛡️ Guardrails e Segurança (Zero-Trust)

- **Boundary Guard**: confinamento estrito de caminhos ao escopo permitido do projeto (bloqueio de path traversal).
- **Bloqueio de Comandos Destrutivos**: interceptação de comandos de alto risco (`rm -rf`, `git reset --hard`, `del /s /q`, etc.).
- **Sanitização de Dados**: mascaramento automático de CPF, e-mails, tokens Bearer e chaves de API (`AIza...`).
- **Human-in-the-Loop (HITL)**: autorização explícita para ações de mutação de alta criticidade.

---

## 🚀 Como Executar e Testar

### Pré-requisitos
- Python 3.11+ (recomendado Python 3.12+)
- Gerenciador `uv`

### Instalação de Dependências
```powershell
uv sync
```

### Verificação de Qualidade & Linter (Ruff)
```powershell
uv run ruff check projects/code_intelligence_agent
```

### Execução de Testes Unitários (Pytest)
```powershell
uv run pytest projects/code_intelligence_agent/tests/unit/test_tools.py -v --tb=short --basetemp="C:\Users\melki\AppData\Local\Temp\opencode\pytest_tmp"
```

---

## 📄 Licença
Desenvolvido como componente autônomo do ecossistema Global de Agentes.
