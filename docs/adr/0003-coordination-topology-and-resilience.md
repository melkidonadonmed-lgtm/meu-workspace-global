# 0003. Topologia de Coordenação Hub-and-Spoke e Resiliência com Checkpoints Git

> **Status: Superseded (2026-09-05).** A camada de interface deste ADR (API Gateway FastAPI na porta 8000, `run.ps1`, servidor FastMCP na porta 8080) foi removida — era um teste de deploy remoto que não compensava manter. `MasterOrchestrator` ficou sem ponto de entrada ativo; a topologia Hub-and-Spoke em si não foi invalidada, mas seu meio de consumo precisa de uma nova decisão (provável migração para subagentes nativos do Claude Code).

Decidimos adotar a topologia de orquestração centralizada em estrela (*Hub-and-Spoke*), disjuntor de resiliência com rollback baseado em checkpoints Git e interface híbrida de consumo via API Gateway SSE (porta 8000) e FastMCP (porta 8080).

## Contexto e Motivação

Execuções autônomas multi-agente em projetos alvo podem gerar loops de chamadas infinitas, corrupção acidental de arquivos ou estados inconsistentes quando subagentes comunicam-se de forma descentralizada. Para garantir segurança, determinismo e alta observabilidade durante o desenvolvimento, precisamos de uma hierarquia clara de controle e uma rede de segurança atômica para reversão.

## Decisão

1. **Topologia Hub-and-Spoke**: O `MasterOrchestrator` é o único coordenador do ciclo de vida das tarefas. Ele planeja, divide e delega trabalho para subagentes especializados stateless (`security_guard`, `workspace_specialist`, etc.). Subagentes não invocam outros subagentes diretamente.
2. **Resiliência e Checkpoints Git**: Antes de aplicar mutações críticas de código no projeto alvo, o sistema registra um checkpoint atômico no Git. Caso o `ResilienceCircuitBreaker` detecte falhas consecutivas, erros de sintaxe irrecuperáveis ou loops, o projeto é restaurado ao estado limpo original e uma notificação estruturada é enviada.
3. **Interface e Barramento Unificados**: O consumo do motor ocorre de forma híbrida:
   - Integração nativa no Antigravity IDE via `antigravity_bridge.py`.
   - Streaming de eventos em tempo real via SSE no FastAPI Gateway (porta 8000).
   - Servidor unificado FastMCP (porta 8080) expondo as ferramentas do workspace para clientes MCP.
