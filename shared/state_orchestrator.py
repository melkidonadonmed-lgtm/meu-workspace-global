"""Persistência Transacional e Checkpointing de Sessões via SQLite WAL."""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from shared.logger import get_logger

logger = get_logger("StateOrchestrator")


class StateOrchestrator:
    """Gerenciador de estado persistente com modo WAL para rastreabilidade de agentes."""

    def __init__(self, db_path: Path | str | None = None):
        configured_db_path = db_path or os.getenv("BRAIN_STATE_DB_PATH")
        if configured_db_path is None:
            state_dir = Path(__file__).resolve().parent / "state"
            state_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = state_dir / "sessions.db"
        else:
            self.db_path = Path(configured_db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_session_step ON session_checkpoints (session_id, step_index);
                """
            )

    def save_checkpoint(
        self,
        session_id: str,
        step_index: int,
        agent_name: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Salva um checkpoint incremental append-only na sessão. Retorna True se persistido com sucesso."""
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO session_checkpoints (session_id, step_index, agent_name, role, content, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (session_id, step_index, agent_name, role, content, meta_str),
                )
            return True
        except Exception as e:  # noqa: BLE001 - erro de persistência não deve travar o pipeline
            logger.warning(f"Falha ao persistir checkpoint SQLite para sessão {session_id}: {e}")
            return False

    def load_session_history(self, session_id: str) -> list[dict[str, Any]]:
        """Recupera todo o histórico ordenado de mensagens de uma sessão persistida."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT step_index, agent_name, role, content, metadata_json, created_at
                    FROM session_checkpoints
                    WHERE session_id = ?
                    ORDER BY step_index ASC, id ASC;
                    """,
                    (session_id,),
                )
                rows = cursor.fetchall()
                history: list[dict[str, Any]] = []
                for r in rows:
                    metadata_raw = r[4] or "{}"
                    try:
                        metadata = json.loads(metadata_raw)
                    except json.JSONDecodeError:
                        metadata = {}
                    if not isinstance(metadata, dict):
                        metadata = {}
                    history.append(
                        {
                            "step_index": r[0],
                            "agent_name": r[1],
                            "role": r[2],
                            "content": r[3],
                            "metadata": metadata,
                            "created_at": r[5],
                        }
                    )
                return history
        except Exception as e:  # noqa: BLE001 - fallback seguro
            logger.warning(f"Falha ao carregar checkpoints da sessão {session_id}: {e}")
            return []
