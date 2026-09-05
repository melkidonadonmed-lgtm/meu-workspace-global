"""Utilitários reais de auditoria e resolução de projetos (sem orquestração/roteamento simulados)."""

from agents.project_resolver import ProjectTargetResolver
from agents.specialized.code_consistency_specialist import CodeConsistencySpecialistAgent
from agents.specialized.security_guard import SecurityGuardAgent
from agents.specialized.workspace_specialist import WorkspaceSpecialistAgent

__all__ = [
    "CodeConsistencySpecialistAgent",
    "ProjectTargetResolver",
    "SecurityGuardAgent",
    "WorkspaceSpecialistAgent",
]
