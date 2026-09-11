"""
Servidor MCP (Model Context Protocol) do ecossistema Brain — brain-mcp-inspector.
Expõe .brain/state/sessions.db (checkpoints do brain-state-orchestrator e
auditoria do resilience-circuit-breaker) como recursos/ferramentas MCP
somente-leitura, e oferece uma ferramenta para pré-visualizar artefatos HTML
de .brain/artifacts/ via servidor web local efêmero.

Transportes:
  - stdio (padrão): processo filho local de um host MCP (Claude Desktop,
    Claude Code, Cursor). Não requer autenticação — stdio já é local/confiável.
  - sse: Streamable HTTP/SSE para agentes remotos. Autenticação Bearer/JWT é
    OBRIGATÓRIA sempre que o servidor faz bind fora de loopback (ver main()).

Executável em Python 3.10+ padrão, sem dependências externas.
"""

import argparse
import base64
from functools import partial
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os
from pathlib import Path
import queue
import sqlite3
import sys
import threading
import time
import urllib.parse
import uuid
import webbrowser
from typing import Any, Dict, List, Optional, Tuple

# Ajusta stderr para UTF-8 no Windows para evitar mojibake em logs.
# IMPORTANTE: em modo stdio, sys.stdout É o canal do protocolo JSON-RPC —
# logging vai para stderr (stream=sys.stderr abaixo) para nunca corrompê-lo.
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s", stream=sys.stderr)

DB_PATH = Path(".brain/state/sessions.db")
ARTIFACTS_DIR = Path(".brain/artifacts")
AUTH_SECRET_ENV = "BRAIN_AUTH_SECRET"


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cursor = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table_name,)
    )
    return cursor.fetchone() is not None


class LocalArtifactServer:
    """Gerenciador de servidor HTTP estático efêmero (thread desacoplada) para
    pré-visualização de artefatos HTML gerados em .brain/artifacts/."""

    _server_instance: Optional[HTTPServer] = None
    _server_thread: Optional[threading.Thread] = None
    _active_port: Optional[int] = None

    @classmethod
    def start(cls, port: int = 8765, open_browser: bool = True) -> Dict[str, Any]:
        if cls._server_instance is not None:
            return {
                "status": "ALREADY_RUNNING",
                "port": cls._active_port,
                "url": f"http://127.0.0.1:{cls._active_port}/workspace_explorer.html",
            }

        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        handler = partial(SimpleHTTPRequestHandler, directory=str(ARTIFACTS_DIR.resolve()))

        try:
            cls._server_instance = HTTPServer(("127.0.0.1", port), handler)
            cls._active_port = port
            cls._server_thread = threading.Thread(target=cls._server_instance.serve_forever, daemon=True)
            cls._server_thread.start()

            url = f"http://127.0.0.1:{port}/workspace_explorer.html"
            if open_browser:
                webbrowser.open(url)

            return {
                "status": "STARTED",
                "port": port,
                "url": url,
                "serving_directory": str(ARTIFACTS_DIR.resolve()),
            }
        except Exception as exc:
            cls._server_instance = None
            cls._active_port = None
            return {"status": "ERROR", "message": str(exc)}


class JWTManager:
    """Codificação e validação nativa de tokens JWT (HS256), via stdlib.

    Sem segredo padrão embutido: um HMAC assinado com uma chave fixa e visível
    no repositório seria trivialmente forjável por qualquer pessoa com acesso
    ao código-fonte. O chamador sempre fornece um segredo explícito (CLI
    --secret ou variável de ambiente BRAIN_AUTH_SECRET).
    """

    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    @staticmethod
    def _base64url_decode(data: str) -> bytes:
        padding = "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + padding)

    @classmethod
    def create_token(cls, payload: Dict[str, Any], secret: str, expires_in_sec: int = 3600) -> str:
        """Gera um JWT assinado com HMAC-SHA256."""
        header = {"alg": "HS256", "typ": "JWT"}
        payload_copy = dict(payload)
        payload_copy["exp"] = int(time.time()) + expires_in_sec
        payload_copy["iat"] = int(time.time())

        header_b64 = cls._base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_b64 = cls._base64url_encode(json.dumps(payload_copy, separators=(",", ":")).encode("utf-8"))

        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        signature_b64 = cls._base64url_encode(signature)

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    @classmethod
    def verify_token(cls, token: str, secret: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Valida assinatura, formato e expiração. Retorna (ok, payload, mensagem)."""
        parts = token.strip().split(".")
        if len(parts) != 3:
            return False, None, "Formato de token invalido. Esperado header.payload.signature"

        header_b64, payload_b64, signature_b64 = parts
        try:
            signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
            expected_signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
            provided_signature = cls._base64url_decode(signature_b64)

            if not hmac.compare_digest(expected_signature, provided_signature):
                return False, None, "Assinatura digital invalida"

            payload = json.loads(cls._base64url_decode(payload_b64).decode("utf-8"))

            exp = payload.get("exp")
            if exp and time.time() > exp:
                return False, None, f"Token expirado em {exp} (timestamp atual: {int(time.time())})"

            return True, payload, "Token valido"
        except Exception as exc:
            return False, None, f"Falha na decodificacao do token: {exc}"


class MCPCoreEngine:
    """Núcleo de processamento JSON-RPC 2.0 — puro, sem I/O de transporte.
    Compartilhado pelos transportes stdio e SSE para nunca haver dois
    dispatchers divergentes (ver SKILL.md, "O que NÃO Fazer")."""

    @staticmethod
    def _read_latest_state() -> str:
        if not DB_PATH.exists():
            return json.dumps({"status": "EMPTY", "message": "Banco de checkpoints ainda nao inicializado."})
        with sqlite3.connect(str(DB_PATH)) as conn:
            if not _table_exists(conn, "checkpoints"):
                return json.dumps({
                    "status": "EMPTY",
                    "message": "Tabela 'checkpoints' ainda nao existe (brain-state-orchestrator nunca gravou um snapshot).",
                })
            cursor = conn.execute("SELECT state_blob FROM checkpoints ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else "{}"

    @staticmethod
    def _list_checkpoints(limit: int) -> List[Dict[str, Any]]:
        if not DB_PATH.exists():
            return []
        with sqlite3.connect(str(DB_PATH)) as conn:
            if not _table_exists(conn, "checkpoints"):
                return []
            cursor = conn.execute(
                """
                SELECT id, session_id, step_index, current_node, created_at
                FROM checkpoints ORDER BY id DESC LIMIT ?
                """,
                (limit,)
            )
            return [
                {"id": r[0], "session_id": r[1], "step": r[2], "node": r[3], "timestamp": r[4]}
                for r in cursor.fetchall()
            ]

    @staticmethod
    def _session_details(session_id: Optional[str]) -> Dict[str, Any]:
        steps: List[Dict[str, Any]] = []
        if session_id and DB_PATH.exists():
            with sqlite3.connect(str(DB_PATH)) as conn:
                if _table_exists(conn, "checkpoints"):
                    cursor = conn.execute(
                        """
                        SELECT step_index, current_node, state_blob, created_at
                        FROM checkpoints WHERE session_id = ? ORDER BY step_index ASC
                        """,
                        (session_id,)
                    )
                    steps = [
                        {"step": r[0], "node": r[1], "state": json.loads(r[2]), "timestamp": r[3]}
                        for r in cursor.fetchall()
                    ]
        return {"session_id": session_id, "total_steps": len(steps), "steps": steps}

    @staticmethod
    def process_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processa uma mensagem JSON-RPC 2.0 e retorna a resposta (ou None
        para notificações, que não recebem resposta)."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params") or {}

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"resources": {}, "tools": {}},
                    "serverInfo": {"name": "brain-mcp-inspector", "version": "1.0.0"},
                },
            }

        if method == "resources/list":
            resources = [
                {
                    "uri": "brain://state/latest",
                    "name": "Ultimo Estado do Workspace Brain",
                    "description": "Snapshot JSON mais recente gravado no banco de checkpoints.",
                    "mimeType": "application/json",
                },
                {
                    "uri": "brain://artifacts/explorer",
                    "name": "Dashboard Web de Artefatos",
                    "description": "Conteudo do arquivo HTML do Workspace Explorer.",
                    "mimeType": "text/html",
                },
            ]
            return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": resources}}

        if method == "resources/read":
            uri = params.get("uri", "")
            if uri == "brain://state/latest":
                content = MCPCoreEngine._read_latest_state()
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {"contents": [{"uri": uri, "mimeType": "application/json", "text": content}]},
                }
            if uri == "brain://artifacts/explorer":
                html_file = ARTIFACTS_DIR / "workspace_explorer.html"
                content = html_file.read_text(encoding="utf-8") if html_file.exists() else "<!-- Artefato nao gerado -->"
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {"contents": [{"uri": uri, "mimeType": "text/html", "text": content}]},
                }
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": f"Recurso nao encontrado: {uri}"}}

        if method == "tools/list":
            tools = [
                {
                    "name": "list_checkpoints",
                    "description": "Lista os checkpoints mais recentes registrados em .brain/state/sessions.db.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Quantidade maxima de registros (padrao: 5)."},
                        },
                    },
                },
                {
                    "name": "get_session_details",
                    "description": "Recupera o historico completo de passos de uma sessao especifica.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"session_id": {"type": "string", "description": "ID da sessao a inspecionar."}},
                        "required": ["session_id"],
                    },
                },
                {
                    "name": "open_visual_artifact_server",
                    "description": "Inicia um servidor web local efemero (127.0.0.1) para visualizar o dashboard HTML de artefatos.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "port": {"type": "integer", "description": "Porta TCP local (padrao: 8765)."},
                            "open_browser": {"type": "boolean", "description": "Se verdadeiro, abre o navegador padrao automaticamente."},
                        },
                    },
                },
            ]
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}

        if method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments") or {}

            if tool_name == "list_checkpoints":
                rows = MCPCoreEngine._list_checkpoints(args.get("limit", 5))
                text = json.dumps({"checkpoints": rows}, indent=2, ensure_ascii=False)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": text}]}}

            if tool_name == "get_session_details":
                details = MCPCoreEngine._session_details(args.get("session_id"))
                text = json.dumps(details, indent=2, ensure_ascii=False)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": text}]}}

            if tool_name == "open_visual_artifact_server":
                status = LocalArtifactServer.start(
                    port=args.get("port", 8765), open_browser=args.get("open_browser", True)
                )
                text = json.dumps(status, indent=2, ensure_ascii=False)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": text}]}}

            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Ferramenta desconhecida: {tool_name}"}}

        if method == "notifications/initialized":
            return None

        if req_id is not None:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Metodo nao suportado: {method}"}}
        return None


class MCPHttpHandler(BaseHTTPRequestHandler):
    """Transporte SSE (Streamable HTTP): GET /sse abre um stream de eventos
    por sessão; POST /messages?session_id=... injeta uma mensagem JSON-RPC,
    cuja resposta é entregue de volta pelo stream SSE correspondente.

    Autenticação Bearer/JWT é aplicada a /sse e /messages SOMENTE quando
    `auth_secret` está configurado (ver main()). Sem segredo configurado, o
    servidor roda sem autenticação — por isso main() recusa bind fora de
    loopback nesse caso.

    Usa ThreadingHTTPServer (ver run_sse): HTTPServer puro processa uma
    requisição por vez, e o handler de /sse bloqueia indefinidamente em loop
    de heartbeat — sem threading, uma segunda conexão (inclusive o POST
    /messages do próprio fluxo documentado) nunca seria aceita.
    """

    active_clients: Dict[str, Dict[str, Any]] = {}
    auth_secret: Optional[str] = None

    def log_message(self, format: str, *args: Any) -> None:
        pass  # Silencia o log padrao do http.server (usamos `logging` explicitamente)

    def _extract_token(self) -> Optional[str]:
        auth_header = self.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:].strip()
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "token" in query_params:
            return query_params["token"][0]
        return None

    def _send_json(self, status: int, payload: Dict[str, Any], extra_headers: Optional[Dict[str, str]] = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _authorize(self) -> bool:
        """True se autorizado (ou se nenhum segredo estiver configurado). Em
        caso de rejeicao, ja envia a resposta 401 e retorna False."""
        if self.auth_secret is None:
            return True
        token = self._extract_token()
        if not token:
            self._send_json(
                401,
                {"jsonrpc": "2.0", "error": {"code": -32001, "message": "Nao autorizado: token Bearer ausente."}},
                extra_headers={"WWW-Authenticate": 'Bearer realm="Brain-MCP"'},
            )
            return False
        is_valid, _claims, err_msg = JWTManager.verify_token(token, secret=self.auth_secret)
        if not is_valid:
            self._send_json(
                401,
                {"jsonrpc": "2.0", "error": {"code": -32001, "message": f"Nao autorizado: {err_msg}"}},
                extra_headers={"WWW-Authenticate": 'Bearer realm="Brain-MCP"'},
            )
            return False
        return True

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)

        if parsed_url.path == "/sse":
            if not self._authorize():
                return

            session_id = str(uuid.uuid4())
            client_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()
            MCPHttpHandler.active_clients[session_id] = {"queue": client_queue, "created_at": time.time()}

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            post_endpoint = f"/messages?session_id={session_id}"
            self.wfile.write(f"event: endpoint\ndata: {post_endpoint}\n\n".encode("utf-8"))
            self.wfile.flush()
            logging.info("Cliente SSE conectado: %s", session_id)

            try:
                while True:
                    try:
                        msg = MCPHttpHandler.active_clients[session_id]["queue"].get(timeout=15.0)
                        event_payload = f"event: message\ndata: {json.dumps(msg, ensure_ascii=False)}\n\n"
                        self.wfile.write(event_payload.encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                logging.info("Cliente SSE desconectado: %s", session_id)
            finally:
                MCPHttpHandler.active_clients.pop(session_id, None)
            return

        if parsed_url.path == "/health":
            self._send_json(200, {"status": "UP", "auth": "ENABLED" if self.auth_secret else "DISABLED"})
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)

        if parsed_url.path == "/messages":
            if not self._authorize():
                return

            query_params = urllib.parse.parse_qs(parsed_url.query)
            session_id = query_params.get("session_id", [None])[0]
            client_entry = MCPHttpHandler.active_clients.get(session_id) if session_id else None
            if not client_entry:
                self._send_json(400, {"error": "session_id invalido, expirado ou sem conexao /sse ativa."})
                return

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                request_data = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                self._send_json(400, {"error": f"JSON invalido: {exc}"})
                return

            # Despacha pelo MESMO núcleo usado pelo stdio — nunca uma resposta
            # fabricada/desconectada do método realmente solicitado.
            response = MCPCoreEngine.process_request(request_data)

            self._send_json(202, {"status": "ACCEPTED"})
            if response is not None:
                client_entry["queue"].put(response)
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()


def run_stdio() -> None:
    """Loop do transporte stdio: lê uma mensagem JSON-RPC por linha de
    sys.stdin, despacha via MCPCoreEngine e escreve a resposta em sys.stdout.
    NUNCA use print()/logging para stdout aqui — corromperia o canal do
    protocolo (ver SKILL.md, "Erros Comuns")."""
    logging.info("Servidor MCP iniciado em modo STDIO.")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}}) + "\n")
            sys.stdout.flush()
            continue

        try:
            response = MCPCoreEngine.process_request(request)
        except Exception as exc:
            logging.exception("Erro nao tratado ao processar requisicao.")
            response = {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32603, "message": f"Erro interno: {exc}"}}

        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def run_sse(host: str, port: int, secret: Optional[str]) -> None:
    MCPHttpHandler.auth_secret = secret
    MCPHttpHandler.active_clients = {}
    server = ThreadingHTTPServer((host, port), MCPHttpHandler)
    logging.info("Servidor MCP (SSE) escutando em http://%s:%d/sse", host, port)
    logging.info("Autenticacao Bearer/JWT: %s", "ATIVADA" if secret else "DESATIVADA (somente loopback)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Servidor MCP (SSE) encerrado.")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Brain MCP Inspector")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transporte MCP (padrao: stdio)")
    parser.add_argument("--host", default="127.0.0.1", help="Host de binding para o transporte sse (padrao: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Porta TCP para o transporte sse (padrao: 8000)")
    parser.add_argument("--secret", default=None, help=f"Segredo HMAC para autenticacao Bearer/JWT no transporte sse (ou defina {AUTH_SECRET_ENV})")
    parser.add_argument("--generate-token", action="store_true", help=f"Gera um token JWT de teste (requer --secret ou {AUTH_SECRET_ENV}) e encerra")
    parser.add_argument("--token-subject", default="local_dev", help="Claim 'sub' do token gerado por --generate-token (padrao: local_dev)")
    args = parser.parse_args()

    secret = args.secret or os.getenv(AUTH_SECRET_ENV)

    if args.generate_token:
        if not secret:
            parser.error(f"--generate-token requer um segredo: use --secret ou defina {AUTH_SECRET_ENV}.")
        print(JWTManager.create_token({"sub": args.token_subject}, secret=secret))
        return

    if args.transport == "stdio":
        run_stdio()
        return

    is_loopback = args.host in ("127.0.0.1", "localhost", "::1")
    if not is_loopback and not secret:
        parser.error(
            f"--host {args.host} expoe o servidor alem de localhost sem nenhum segredo configurado "
            f"(--secret ou {AUTH_SECRET_ENV}). Use --host 127.0.0.1 ou configure um segredo."
        )
    run_sse(args.host, args.port, secret)


if __name__ == "__main__":
    main()
