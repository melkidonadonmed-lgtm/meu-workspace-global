#!/usr/bin/env bash
# ==============================================================================
# Inicializacao rapida do brain-mcp-inspector.
# Uso: launch_ecosystem.sh [stdio|sse] [porta]
#   stdio (padrao): processo filho local (Claude Desktop/Code/Cursor).
#   sse: Streamable HTTP em 127.0.0.1:<porta> (sem autenticacao). Para expor
#        alem de localhost ou exigir Bearer/JWT, invoque mcp_server.py
#        diretamente com --host/--secret (ver SKILL.md).
# ==============================================================================
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

mkdir -p .brain/state .brain/artifacts

MODE="${1:-stdio}"
PORT="${2:-8000}"

case "$MODE" in
  stdio)
    echo "Iniciando brain-mcp-inspector em modo STDIO..." >&2
    exec python .agents/skills/brain-mcp-inspector/scripts/mcp_server.py --transport stdio
    ;;
  sse)
    echo "Iniciando brain-mcp-inspector em modo SSE na porta $PORT (127.0.0.1, sem autenticacao)..." >&2
    exec python .agents/skills/brain-mcp-inspector/scripts/mcp_server.py --transport sse --port "$PORT"
    ;;
  *)
    echo "Modo desconhecido: $MODE. Use 'stdio' ou 'sse'." >&2
    exit 1
    ;;
esac
