"""Testes de integridade e validação de schema para agentes customizados (.agents/agents/*.md)."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = REPO_ROOT / ".agents" / "agents"

# Ferramentas canônicas válidas conhecidas da plataforma Antigravity
CANONICAL_TOOLS = {
    "view_file",
    "replace_file_content",
    "write_to_file",
    "grep_search",
    "find_by_name",
    "list_dir",
    "run_command",
    "manage_task",
    "schedule",
    "send_message",
    "ask_question",
    "invoke_subagent",
    "define_subagent",
    "manage_subagents",
    "read_url_content",
    "search_web",
}


def parse_agent_markdown(content: str) -> tuple[dict[str, any] | None, str | None]:
    """Extrai o frontmatter YAML e o corpo do prompt de um arquivo de agente."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return None, "Frontmatter YAML ausente ou mal delimitado por '---'."

    yaml_text = match.group(1)
    body = match.group(2).strip()

    data: dict[str, any] = {}
    current_key = None
    list_items = []

    for line in yaml_text.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue

        if trimmed.startswith("- ") and current_key:
            list_items.append(trimmed[2:].strip().strip('"').strip("'"))
            continue

        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            if current_key and list_items:
                data[current_key] = list_items
                list_items = []

            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.lower() == "true":
                data[key] = True
                current_key = None
            elif val.lower() == "false":
                data[key] = False
                current_key = None
            elif not val:
                current_key = key
                list_items = []
            else:
                data[key] = val
                current_key = None

    if current_key and list_items:
        data[current_key] = list_items

    data["__body__"] = body
    return data, None


def test_custom_agents_directory_and_files_exist():
    """Valida a presença do diretório de agentes e ao menos um agente configurado."""
    assert AGENTS_DIR.exists(), f"Diretório de agentes não encontrado: {AGENTS_DIR}"
    agent_files = list(AGENTS_DIR.glob("*.md"))
    assert len(agent_files) >= 2, f"Esperado ao menos 2 agentes, encontrados {len(agent_files)}."


def test_custom_agents_schema_and_tools():
    """Garante que todos os agentes tenham metadados válidos e ferramentas canônicas."""
    agent_files = list(AGENTS_DIR.glob("*.md"))
    errors = []

    for agent_file in agent_files:
        rel_path = agent_file.relative_to(REPO_ROOT).as_posix()
        content = agent_file.read_text(encoding="utf-8")
        data, err = parse_agent_markdown(content)

        if err or not data:
            errors.append(f"[{rel_path}] {err}")
            continue

        # 1. Validação de Name
        name = data.get("name")
        if not name:
            errors.append(f"[{rel_path}] Campo obrigatório 'name' ausente.")
        elif not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            errors.append(f"[{rel_path}] 'name' ('{name}') deve estar em kebab-case.")
        elif name != agent_file.stem:
            errors.append(f"[{rel_path}] 'name' ('{name}') difere do nome do arquivo ('{agent_file.stem}').")

        # 2. Validação de Description
        desc = data.get("description", "")
        if not desc or len(desc) < 20:
            errors.append(f"[{rel_path}] 'description' ausente ou muito curta (< 20 caracteres).")

        # 3. Validação de flags de ativação
        subagent = data.get("subagent", False)
        main_agent = data.get("mainAgent", False)
        if not subagent and not main_agent:
            errors.append(f"[{rel_path}] Ao menos uma das flags 'subagent' ou 'mainAgent' deve ser true.")

        # 4. Validação de Ferramentas (Tools)
        tools = data.get("tools", [])
        if not isinstance(tools, list) or len(tools) == 0:
            errors.append(f"[{rel_path}] Campo 'tools' deve ser uma lista não-vazia.")
        else:
            for tool in tools:
                if tool not in CANONICAL_TOOLS:
                    errors.append(
                        f"[{rel_path}] Ferramenta inválida '{tool}'. Assegure nome canônico para evitar hang no processo."
                    )

        # 5. Validação de System Prompt
        body = data.get("__body__", "")
        if not body or len(body) < 30:
            errors.append(f"[{rel_path}] Corpo do prompt de sistema ausente ou muito curto.")

    assert not errors, "Falhas de validação nos agentes customizados:\n" + "\n".join(errors)
