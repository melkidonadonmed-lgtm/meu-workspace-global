"""
Módulo de Orquestração, Seleção de Rotas e Integração com skill-factory.

Implementa a persistência em batch da memória de rotas para evitar overhead de I/O em tempo real.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("TaskOrganizer")


@dataclass
class TaskProposal:
    task_id: str
    description: str
    assigned_agent: str
    required_skills: list[str] = field(default_factory=list)
    route_id: str | None = None
    missing_skill_needed: bool = False
    new_skill_proposal: dict[str, Any] | None = None


class TaskOrganizer:
    """Organizador de tarefas conectado à memória operacional de rotas e ao skill-factory."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.routes_memory_file = workspace_root / "configs" / "orchestration_routes_memory.json"
        self.routes_data = self._load_routes_memory()
        self._pending_updates: list[str] = []

    def _load_routes_memory(self) -> dict[str, Any]:
        """Carrega a base de memória em JSON."""
        if not self.routes_memory_file.exists():
            return {"routes": []}
        try:
            return json.loads(self.routes_memory_file.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Erro ao ler memória de rotas: {e}")
            return {"routes": []}

    def resolve_best_route(self, task_intent: str) -> dict[str, Any] | None:
        """Seleciona a melhor rota com base na intenção da tarefa."""
        intent_lower = task_intent.lower()
        
        # Mapeamento para rotas consagradas
        if any(w in intent_lower for w in ["auditar", "validar", "revisar", "analisar risco"]):
            return self._find_route_by_id("ROUTE-GOLD-ARCH-AUDIT")
        elif any(w in intent_lower for w in ["ui", "layout", "design", "css", "tela"]):
            return self._find_route_by_id("ROUTE-GOLD-UI-TACTILE")
        elif any(w in intent_lower for w in ["bug", "quebrou", "falha", "erro", "consertar"]):
            return self._find_route_by_id("ROUTE-MERGE-BUG-FIX")
        elif any(w in intent_lower for w in ["adk", "inovações", "novidades agentes", "skills"]):
            return self._find_route_by_id("ROUTE-SUGG-ADK-EVOLUTION")
        
        return None

    def _find_route_by_id(self, route_id: str) -> dict[str, Any] | None:
        for r in self.routes_data.get("routes", []):
            if r.get("route_id") == route_id:
                return r
        return None

    def record_route_execution(self, route_id: str) -> None:
        """Registra a execução em buffer de memória sem gravar em disco imediatamente."""
        self._pending_updates.append(route_id)

    def flush_memory_updates(self) -> None:
        """Persiste em batch todas as execuções acumuladas, minimizando I/O."""
        if not self._pending_updates:
            return

        counts: dict[str, int] = {}
        for rid in self._pending_updates:
            counts[rid] = counts.get(rid, 0) + 1

        for r in self.routes_data.get("routes", []):
            rid = r.get("route_id")
            if rid in counts:
                r["execution_count"] = r.get("execution_count", 0) + counts[rid]

        try:
            self.routes_memory_file.write_text(
                json.dumps(self.routes_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            self._pending_updates.clear()
        except Exception as e:  # noqa: BLE001
            logger.error(f"Falha ao persistir batch de rotas: {e}")
