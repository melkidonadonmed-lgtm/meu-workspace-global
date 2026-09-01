---
name: engenharia
version: 1.0.0
description: Hub de engenharia de software, diagnóstico de servidores FastMCP, resolução de bloqueios em subagentes e padrões de tool calling.
has-sub-skill: true
triggers:
  - "engenharia"
  - "diagnostico mcp"
  - "troubleshoot mcp"
  - "tool calling"
---

# Engenharia & Ferramentas — Hub de Soluções Técnicas

Bundle focado na infraestrutura de agentes, comunicação MCP e depuração de tool calls.

## Sub-skills

| Sub-skill | Quando usar |
|---|---|
| [`mcp-troubleshooter-design-advisor`](mcp-troubleshooter-design-advisor/SKILL.md) | Diagnóstico e resolução de bloqueios, timeouts e validação de schemas em servidores FastMCP. |

## Zonas de Não-Ação & O que NÃO Fazer
- NUNCA expor tokens de autenticação em logs de depuração.
- NUNCA desativar validações de tipo de dados em tools MCP.
