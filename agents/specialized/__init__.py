"""Subagentes especialistas com lógica real, deterministica, sem dependência de LLM."""

from agents.specialized.code_consistency_specialist import CodeConsistencySpecialistAgent
from agents.specialized.security_guard import SecurityGuardAgent
from agents.specialized.workspace_specialist import WorkspaceSpecialistAgent

__all__ = [
    "CodeConsistencySpecialistAgent",
    "SecurityGuardAgent",
    "WorkspaceSpecialistAgent",
]
