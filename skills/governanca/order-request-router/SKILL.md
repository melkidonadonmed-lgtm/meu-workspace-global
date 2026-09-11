---
name: order-request-router
version: 1.0.0
description: Triagem semântica, classificação de intenções e roteador hierárquico de pedidos para agentes especialistas e subcatálogos.
triggers:
  - "roteamento de pedido"
  - "triagem de pedido"
  - "classificar intencao"
  - "despachar pedido"
  - "order router"
  - "request router"
---

# Roteador de Pedidos & Triagem Hierárquica (`order-request-router`)

Habilidade canônica de governança responsável pela recepção, desconstrução semântica e despacho de intenções do usuário para o agente especialista correto, garantindo o isolamento de subcatálogos e eliminando a ativação desordenada de skills em bloco (*bulk loading*).

## 1. Princípios Operacionais

1. **Separação Estrita de Domínios**:
   - Cada pedido deve ser mapeado para exatamente um agente primário ou projeto alvo.
   - O Orquestrador Global nunca deve carregar as instruções internas de skills especializadas em seu System Prompt. Ele delega para o subagente e o subagente ativa seu próprio subcatálogo.
2. **Classificação em 2 Etapas**:
   - **Etapa 1 (Portão de Segurança / Trivial)**: Detecta operações destrutivas (`accidental-data-loss-prevention` com bloqueio HITL) ou conversação trivial (resposta direta sem injeção de skills).
   - **Etapa 2 (Triagem Semântica & Decomposição)**: Extrai o domínio funcional (`dados`, `workspace`, `ui`, `auditoria`, `governanca`, `pesquisa`, `suporte`, `medico/pcm`, `projetos_externos`), identifica o agente responsável e as sub-skills necessárias.
3. **Prevenção Ativa de Context Bloat**:
   - O roteador restringe a injeção a no máximo 1–2 skills específicas por turno (Top-K) quando o orquestrador assume a resposta, ou transfere o controle para o agente especialista com seu subcatálogo isolado.

## 2. Taxonomia de Roteamento de Agentes e Projetos

| Domínio Funcional | Agente / Destino Alvo | Escopo de Subcatálogo / Skills |
|---|---|---|
| Consultas SQL, BigQuery, Schemas | `sql_specialist` (`SqlSpecialistAgent`) | `bigquery-sql`, `dataform-bigquery`, `mcp:bigquery_*` |
| Arquivos locais, Storage, Drive, Calendar | `workspace_specialist` (`WorkspaceSpecialistAgent`) | `workspace-data-analytics-architect`, `mcp:workspace_*` |
| Prescrição médica, CFM, CID-10, Atestados | `pcm` (`Brain/projetos/pcm`) | `design-interface-medica-minimalista`, `cidCatalog`, `pediatricMeds` |
| Montagem HTML5, Atomic Design, Responsivo | `html_modular_specialist` (`HTMLModularSpecialistAgent`) | `skill-html-modular-builder`, `responsive-html-ui-master`, `frontend-design` |
| Chamados, tickets, incidentes de clientes | `customer_issue_reviewer` (`CustomerIssueReviewerAgent`) | `customer_issue_reviewer_go`, `suporte` |
| Análise de código, anti-drift, consistência | `code_consistency_specialist` (`CodeConsistencySpecialistAgent`) | `code-validator`, `code-reviewer`, `api-auditor` |
| Pesquisa aprofundada, síntese web | `research_evolution_specialist` (`ResearchEvolutionSpecialistAgent`) | `deep-research`, `skill-factory` |
| Governança, resiliência, integridade | `governanca` (`MasterOrchestrator`) | `resilience-circuit-breaker`, `skill-healthcheck`, `order-request-router` |

## 3. Formato Estruturado de Despacho (Payload de Decisão)

O roteador emite uma estrutura canônica consumida pelo Orquestrador e pelos Gateways:

```json
{
  "order_id": "req-20260905-001",
  "intent": "CONSULTA_ANALITICA",
  "domain": "dados",
  "target_agent": "sql_specialist",
  "target_type": "agent",
  "target_subcatalog": ["bigquery-sql"],
  "complexity": "INTERMEDIARIO",
  "is_destructive": false,
  "execution_mode": "DELEGATE_TO_AGENT",
  "rationale": "Usuário solicitou análise de faturamento em tabela do BigQuery."
}
```

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)

- NUNCA carregar o texto completo (`SKILL.md`) de múltiplas habilidades simultaneamente no System Prompt do Orquestrador Global.
- NUNCA repassar comandos destrutivos sem a sinalização obrigatória de `is_destructive: true` e portão de confirmação humana (HITL).
- NUNCA rotear pedidos específicos de projetos clientes (ex: regras médicas do `pcm`) para agentes genéricos de código sem carregar o contexto de domínio local (`AGENTS.md` do projeto alvo).
- NUNCA utilizar correspondência exclusiva de palavras-chave cegas para decisões complexas que envolvam múltiplos domínios.
