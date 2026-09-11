# Original User Request

## 2026-09-03T03:51:58Z

Construir o pacote Python autônomo `projects/web_visual_auditor`, composto por agentes modulares para pesquisa web com extração semântica de conteúdo, inspeção hierárquica e geométrica do DOM (bounding boxes) e auditoria visual de regressão pixel a pixel (tela inteira e micro-componentes isolados de design systems).

Working directory: c:\Users\melki\meu-workspace-global\projects\web_visual_auditor
Integrity mode: development

## Requirements

### R1. Pesquisa Web & Extração Semântica de Artigos
O módulo de pesquisa deve executar consultas web estruturadas (DuckDuckGo / APIs de busca), limpar o HTML com BeautifulSoup (eliminando scripts, styles, nós svg e metadados ruidosos) e retornar referências consolidadas com títulos, URLs e snippets normalizados.

### R2. Inspeção de Geometria Computada do DOM
O módulo de inspeção deve renderizar aplicações web via Playwright em modo headless, extraindo elementos-chave (`header`, `main`, `article`, `button`, `nav`, `h1`, etc.) com IDs, classes, visibilidade computada e coordenadas geométricas precisas (`x`, `y`, `width`, `height`) obtidas via `getBoundingClientRect`.

### R3. Auditoria Visual e Regressão Diferencial Pixel a Pixel
O módulo de regressão deve comparar duas capturas de tela (baseline vs current) via Pillow (PIL), calcular o percentual exato de divergência entre imagens com tolerância a variações de antialiasing (`channel > 15`), e gerar uma imagem de máscara destacando os pixels alterados em vermelho puro (`#FF0000`).

### R4. Auditoria Granular por Micro-Componentes de Design System
O sistema deve permitir isolar seletores CSS específicos (ex: botões, cards, modais), capturando exclusivamente a área delimitada de cada componente (`element.screenshot()`), calculando suas dimensões e executando a comparação visual diferencial de forma independente da página como um todo.

### R5. Interface CLI e Módulo Integrado
O projeto deve fornecer uma interface de linha de comando (`cli.py`) e uma classe principal orquestradora (`WebVisualAuditorSuite`) permitindo disparar fluxos individuais (`search`, `dom-inspect`, `visual-diff`, `component-diff`) ou o pipeline completo.

## Verification Resources & Test Strategy

- **Testes Locais Determinísticos:** A suíte de testes deve utilizar fixtures locais (páginas HTML estáticas servidas localmente ou carregadas via `file://` / data URLs e pares de imagens baseline/current sintéticas) para testar 100% da lógica sem depender de internet ativa.
- **Suíte Pytest Completa:** Cobertura de testes unitários para a limpeza semântica de HTML, extração de geometrias do DOM, cálculo de diff de imagens e captura de micro-componentes.

## Acceptance Criteria

### Arquitetura & Qualidade de Código
- [ ] Código modular em `projects/web_visual_auditor/` estruturado em módulos independentes (`researcher.py`, `dom_auditor.py`, `visual_regression.py`, `component_auditor.py`, `cli.py`).
- [ ] Modelos de dados com dataclasses ou Pydantic tipados estritamente (`SourceReference`, `DOMNodeSummary`, `ComputedElementGeometry`, `VisualDiffResult`, `ComponentSnapshot`, `ComponentDiffReport`).
- [ ] Tratamento robusto de exceções e timeouts (uso de `wait_until="domcontentloaded"` com fallback para carregamento lento).

### Testes & Verificação
- [ ] `pytest` executado com 100% de aprovação nas fixtures locais.
- [ ] Geração comprovada do mapa diferencial (`diff_result.png` / `diff_<selector>.png`) quando há divergência visual intencional nos testes.
- [ ] Nenhum erro de lint (`ruff check .` limpo).

## 2026-09-11T07:05:21Z

Construir um sistema autônomo de inteligência e engenharia de código (Code Intelligence & Tool Calling) para ambiente de produção, integrando o Google Agent Development Kit (ADK) e o Google Antigravity SDK, dotado de guardrails de segurança, ferramentas com validação robusta e uma suíte completa de avaliação automatizada baseada no Quality Flywheel (`agents-cli eval`).

Working directory: C:\Users\melki\meu-workspace-global\projects\code_intelligence_agent
Integrity mode: development

## Requirements

### R1. Sistema de Agente de Engenharia e Inteligência de Código
O agente deve ser capaz de inspecionar bases de código, identificar anomalias, propor modificações precisas e orquestrar ferramentas de navegação e análise estática via tool calling determinístico. Deve gerenciar estado conversacional e histórico de raciocínio de forma transparente.

### R2. Guardrails e Políticas de Segurança (HITL & Sanitização)
O sistema deve implementar interceptadores de ciclo de vida (hooks/callbacks) para impedir comandos destrutivos no sistema operacional, mascarar credenciais ou tokens sensíveis e assegurar integridade de fronteiras de diretório.

### R3. Suíte de Avaliação Automatizada (Quality Flywheel)
Implementação de dataset canônico em `tests/eval/datasets/` cobrindo cenários multi-turn de análise de código e arquivo `eval_config.yaml` parametrizando métricas de qualidade (`multi_turn_task_success`, `multi_turn_tool_use_quality`).

### R4. Interface de Execução e Gerenciamento de Ambiente
Configuração de ambiente isolado gerenciado por `uv`, compatibilidade com FastAPI / ADK API Server para invocação programática e entrada CLI padrão para interação em terminal.

## Acceptance Criteria

### Verificação Funcional e Qualidade de Código
- [ ] A suíte de testes automatizados (`uv run pytest`) executa e passa com 100% de sucesso no diretório do projeto.
- [ ] O código passa na checagem estática e linter (`uv run ruff check`) com zero erros.

### Verificação da Suíte de Avaliação (Eval Flywheel)
- [ ] Execução de `agents-cli eval run` atinge `multi_turn_task_success >= 0.85`.
- [ ] Métrica `multi_turn_tool_use_quality` atinge pontuação >= 0.80 sem chamadas errôneas ou redundantes de ferramentas.
- [ ] Relatórios de avaliação (`results_*.json` e `.html`) são gerados com sucesso na pasta de artefatos de teste.

### Guardrails de Segurança
- [ ] Comandos potencialmente destrutivos ou violações de fronteira de diretório são interceptados e bloqueados com feedback explicativo.
