# 📐 Formatting Standards: Padrões de Saída, Esquemas & Engenharia de Código

> **Versão:** 1.0.0  
> **Status:** Ativo & Obrigatório  
> **Escopo:** Todas as respostas geradas por agentes e artefatos de código no workspace.

---

## 1. Padrões de Comunicação com o Usuário

1. **Idioma Estrito:** Todo texto, relatório, comentário de código e documentação deve ser redigido em **Português do Brasil (pt-BR)**.
2. **Painel de Despacho Executivo:** Toda resposta orquestrada de alta complexidade deve abrir com o painel resumindo a rota de decisão tomada:
   ```text
   🎯 Rota: [Nome da Skill / Subagente] | Modo: [SINGLE_SKILL / MULTI_AGENT] | Capacidade: [Existente / Nova]
   ```
3. **Links de Arquivo Clicáveis (Obrigatório):**
   - Sempre formatar caminhos de arquivo como links Markdown utilizando o esquema `file:///` com barras inclinadas para a direita (`/`), mesmo no Windows:
   - Exemplo: `[orchestrator.py](file:///C:/Users/melki/meu-workspace-global/agents/orchestrator.py)`

---

## 2. Padrões de Qualidade de Código (Python & Go)

1. **Código Limpo e Sem Poluição:**
   - Proibido deixar blocos de código comentado "morto" em arquivos definitivos.
   - Proibido remover docstrings ou comentários explicativos pré-existentes sem justificativa técnica.
   - Todo tratamento de exceção genérico (`except Exception:`) deve incluir justificativa explícita e comentário `# noqa: BLE001`.
2. **Linter & Tipagem:**
   - Código Python deve passar 100% limpo no `ruff check .` (PEP 8, ordenação de imports `I001`, remoção de imports não utilizados `F401`).
   - Uso de tipagem estrita moderna do Python 3.11+: `dict[str, Any]`, `list[str]`, `str | None`.
3. **Módulos em Go:**
   - Manter `go.mod` e `go.sum` sempre limpos via `go mod tidy`.
   - Código Go deve compilar sem warnings e seguir a convenção de pacotes idiomática em `pkg/`.

---

## 3. Esquemas de Saída Estruturados (JSON & YAML)

1. **Respostas Estruturadas via API / FastMCP:**
   - Respostas de ferramentas FastMCP e endpoints do Gateway devem retornar esquemas JSON válidos e serializáveis (conforme `Pydantic`).
   - Campos mínimos para relatórios analíticos:
     ```json
     {
       "agent": "NomeDoAgente",
       "status": "completed | error | blocked",
       "summary": "Resumo executivo em 1-2 linhas",
       "data": {},
       "timestamp": "2026-09-02T12:00:00Z"
     }
     ```
2. **Manifestos e Configurações (YAML):**
   - Indentação estrita de 2 espaços.
   - Proibido uso de tabs (`\t`).
   - Todos os caminhos de arquivos relativos devem usar barras normais (`/`).
