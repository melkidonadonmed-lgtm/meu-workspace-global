"""Laboratório e Showcase de Recursos Avançados do Google ADK (adk_lab).

Demonstra na prática:
- Action Confirmations (HITL)
- Artifacts (Armazenamento de binários/arquivos versionados)
- State & Session Scopes (user:, temp:, app:)
- Skills dinâmicas (SkillToolset + SKILL.md)
- Callbacks de observabilidade
- Rewind de sessões
"""

from .agent import root_agent

__all__ = ["root_agent"]
