"""Pacote canônico audit_agent para Google Agent Development Kit (ADK).

Fornece auditoria contínua de código, resolução determinística de projetos
e guardrails de segurança Zero-Trust integrados ao runtime do ADK.
"""

from .agent import root_agent

__all__ = ["root_agent"]
