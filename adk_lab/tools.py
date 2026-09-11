"""Ferramentas avançadas de demonstração e teste do Google ADK (adk_lab).

Demonstra na prática:
1. Artifacts: Criação e leitura de arquivos/relatórios binários e markdown (save_artifact, load_artifact).
2. State Scopes: Estado de sessão, temporário ('temp:') e persistente do usuário ('user:').
3. Action Confirmations: Ações críticas que exigem aprovação humana (require_confirmation=True).
4. Skills Dinâmicas: Carregamento do catálogo governado via SkillToolset.
"""

from pathlib import Path
from typing import Any, Dict
from google.adk.tools import ToolContext, FunctionTool
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types


async def generate_and_save_report(
    report_title: str, summary: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Gera um relatório estruturado em Markdown e o salva como um Artefato versionado do ADK.

    Args:
        report_title: Título principal do relatório técnico.
        summary: Resumo executivo dos pontos avaliados.

    Returns:
        Dicionário com o nome do artefato, versão gerada e status da operação.
    """
    filename = "relatorio_tecnico.md"
    markdown_content = f"""# {report_title}
**Data de Geração**: Relatório emitido pelo Google ADK Lab
**Resumo Executivo**:
{summary}

---
*Gerado via Google ADK Artifact Service (versionado e persistente).*
"""
    # Criação do Part de bytes (padrão oficial de Artifacts no ADK)
    artifact_part = types.Part.from_bytes(
        data=markdown_content.encode("utf-8"),
        mime_type="text/markdown",
    )

    # 1. Salva como Artifact no ToolContext
    version = await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
        custom_metadata={"title": report_title, "author": "adk_lab"},
    )

    # 2. Registra o ponteiro temporário no State (prefixo temp:)
    tool_context.state["temp:last_artifact_filename"] = filename
    tool_context.state["temp:last_artifact_version"] = version

    return {
        "status": "success",
        "filename": filename,
        "version": version,
        "size_bytes": len(markdown_content.encode("utf-8")),
        "message": f"Artefato '{filename}' (v{version}) salvo com sucesso no ArtifactService.",
    }


async def get_stored_report(
    filename: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Recupera o conteúdo de um artefato previamente salvo na sessão do ADK.

    Args:
        filename: Nome do arquivo a ser recuperado (ex: 'relatorio_tecnico.md').

    Returns:
        Dicionário com o conteúdo em texto do artefato e metadados.
    """
    part = await tool_context.load_artifact(filename=filename)
    if not part or not part.inline_data:
        return {
            "status": "error",
            "message": f"Artefato '{filename}' não encontrado nesta sessão.",
        }

    decoded_text = part.inline_data.data.decode("utf-8")
    return {
        "status": "success",
        "filename": filename,
        "mime_type": part.inline_data.mime_type,
        "content_preview": decoded_text[:300],
    }


def set_user_preference(
    preference_key: str, preference_value: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Armazena preferências persistentes de longo prazo associadas ao usuário (State prefix 'user:').

    Args:
        preference_key: Nome da preferência (ex: 'theme', 'language', 'output_format').
        preference_value: Valor a ser configurado (ex: 'dark', 'pt-BR', 'markdown').

    Returns:
        Dicionário com a confirmação da preferência gravada no State.
    """
    # Prefixo oficial user: persiste além da sessão corrente
    scoped_key = f"user:{preference_key.strip().lower()}"
    tool_context.state[scoped_key] = preference_value

    return {
        "status": "success",
        "scoped_key": scoped_key,
        "saved_value": preference_value,
        "message": f"Preferência '{scoped_key}' persistida com sucesso.",
    }


def get_user_preferences(tool_context: ToolContext) -> Dict[str, Any]:
    """Lê todas as preferências persistentes do usuário atualmente armazenadas no State.

    Returns:
        Dicionário contendo todas as chaves de usuário (user:*).
    """
    user_prefs = {
        k.replace("user:", ""): v
        for k, v in tool_context.state.items()
        if k.startswith("user:")
    }
    return {
        "status": "success",
        "total_preferences": len(user_prefs),
        "preferences": user_prefs,
    }


def apply_critical_system_patch(
    component_name: str, patch_version: str
) -> Dict[str, Any]:
    """Aplica uma atualização crítica no sistema. Requer confirmação humana prévia (HITL).

    Args:
        component_name: Nome do microsserviço ou componente (ex: 'api_gateway', 'auth_server').
        patch_version: Versão do patch a ser aplicado (ex: 'v2.4.1-security').

    Returns:
        Dicionário com o status da aplicação do patch.
    """
    return {
        "status": "applied",
        "component": component_name,
        "patch_version": patch_version,
        "message": f"Patch {patch_version} aplicado com sucesso no componente {component_name} após confirmação!",
    }


def build_skill_toolset_for_analytics() -> SkillToolset:
    """Carrega dinamicamente a skill local 'analytics' (SKILL.md) e a expõe como SkillToolset."""
    skill_path = Path(__file__).resolve().parent.parent / "skills" / "analytics"
    skill_def = load_skill_from_dir(skill_path)
    return SkillToolset(skills=[skill_def])


# Ferramenta com confirmação humana obrigatória (Action Confirmation)
critical_patch_tool = FunctionTool(
    apply_critical_system_patch,
    require_confirmation=True,
)
