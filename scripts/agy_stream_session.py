"""Cliente Python de Streaming Contínuo (Multi-Turn) para o Google Antigravity CLI (agy).

Utiliza o modo `--input-format stream-json --output-format stream-json` para manter
um processo único aberto, reutilizando conexões e contexto sem sobrecarga de inicialização.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any, Generator


class AntigravitySession:
    """Gerencia uma sessão contínua de diálogo com o agy via NDJSON em stdin/stdout."""

    def __init__(
        self,
        model: str | None = None,
        effort: str | None = None,
        timeout_seconds: float = 300.0,
        extra_args: list[str] | None = None,
    ) -> None:
        self.model = model
        self.effort = effort
        self.timeout_seconds = timeout_seconds
        self.extra_args = extra_args or []
        self._proc: subprocess.Popen[str] | None = None
        self._conversation_id: str | None = None

    def start(self) -> None:
        """Inicia o processo persistente do agy."""
        agy_bin = shutil.which("agy") or shutil.which("agy.exe")
        if not agy_bin:
            raise FileNotFoundError("O executável 'agy' não foi encontrado no PATH.")

        cmd = [
            agy_bin,
            "--input-format",
            "stream-json",
            "--output-format",
            "stream-json",
        ]
        if self.model:
            cmd.extend(["--model", self.model])
        if self.effort:
            cmd.extend(["--effort", self.effort])
        cmd.extend(self.extra_args)

        self._proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered
        )

        # Lê o evento inicial 'init'
        if self._proc.stdout is not None:
            init_line = self._proc.stdout.readline()
            if init_line:
                try:
                    init_data = json.loads(init_line.strip())
                    if init_data.get("event") == "init":
                        self._conversation_id = init_data.get("conversation_id")
                except json.JSONDecodeError:
                    pass

    @property
    def conversation_id(self) -> str | None:
        """Retorna o ID da conversa ativa."""
        return self._conversation_id

    def stream_turn(self, prompt: str) -> Generator[dict[str, Any], None, dict[str, Any]]:
        """Envia um prompt e gera os eventos parciais (step_update) até emitir o evento final (result)."""
        if self._proc is None or self._proc.stdin is None or self._proc.stdout is None:
            raise RuntimeError("A sessão do agy não foi iniciada. Chame start() primeiro.")

        message = {"event": "user", "message": {"content": prompt}}
        payload = json.dumps(message) + "\n"
        self._proc.stdin.write(payload)
        self._proc.stdin.flush()

        result_payload: dict[str, Any] = {}

        for raw_line in self._proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = event.get("event")
            if event_type == "step_update":
                yield event
            elif event_type == "result":
                result_payload = event.get("result", {})
                break

        return result_payload

    def ask(self, prompt: str) -> dict[str, Any]:
        """Envia um prompt e aguarda a conclusão do turno, retornando o payload final de result."""
        final_result: dict[str, Any] = {}
        for _ in self.stream_turn(prompt):
            pass
        # Recupera o payload consumido
        # Em Python generators, o valor de return de um generator é obtido na exceção StopIteration,
        # mas para facilitar o uso síncrono simples, implementamos ask() chamando o pipeline:
        return final_result or self._ask_direct(prompt)

    def _ask_direct(self, prompt: str) -> dict[str, Any]:
        """Método síncrono direto para envio e coleta do evento result."""
        if self._proc is None or self._proc.stdin is None or self._proc.stdout is None:
            raise RuntimeError("A sessão do agy não foi iniciada. Chame start() primeiro.")

        message = {"event": "user", "message": {"content": prompt}}
        self._proc.stdin.write(json.dumps(message) + "\n")
        self._proc.stdin.flush()

        for raw_line in self._proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("event") == "result":
                return event.get("result", {})

        return {"status": "ERROR", "error": "Processo encerrou antes de emitir resultado."}

    def close(self) -> int:
        """Encerra graciosamente a sessão fechando o stdin."""
        if self._proc is not None:
            if self._proc.stdin is not None and not self._proc.stdin.closed:
                self._proc.stdin.close()
            return self._proc.wait(timeout=self.timeout_seconds)
        return 0

    def __enter__(self) -> AntigravitySession:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


if __name__ == "__main__":
    print("Iniciando sessão contínua multi-turn com agy...")
    with AntigravitySession() as session:
        print(f"Sessão ID: {session.conversation_id}")
        
        # Turno 1
        q1 = "Diga apenas o nome de um planeta do sistema solar."
        print(f"\n[Usuário]: {q1}")
        res1 = session._ask_direct(q1)
        r1_text = res1.get("response", "").strip()
        print(f"[Agente (Turno {res1.get('num_turns', 1)})]: {r1_text}")

        # Turno 2 (mantendo o contexto do processo aberto)
        q2 = f"Quantas luas aproximadamente possui o planeta {r1_text}? Responda em uma frase curta."
        print(f"\n[Usuário]: {q2}")
        res2 = session._ask_direct(q2)
        print(f"[Agente (Turno {res2.get('num_turns', 2)})]: {res2.get('response', '').strip()}")
        print(f"\nMétricas totais de uso: {res2.get('usage', {})}")
