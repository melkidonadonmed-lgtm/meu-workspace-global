"""Módulo do agente multi-ferramentas (multi_tool_agent) para Google ADK.

Expõe root_agent para descoberta dinâmica pelo Google ADK e agents-cli.
"""

from .agent import root_agent

__all__ = ["root_agent"]
