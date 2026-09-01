---
name: resilience-circuit-breaker
version: 1.0.0
description: Disjuntor de execução e guardião de orçamento para o fluxo de agentes e tools. Detecta loops e deadlocks por hash de payload, aplica teto de passos e tokens, e desarma com causa raiz estruturada.
triggers:
  - "disjuntor"
  - "circuit breaker"
  - "loop infinito"
  - "deadlock"
  - "estouro de orcamento"
  - "resetar disjuntor"
---

# Sentinela de Resiliência e Disjuntor de Execução (`resilience-circuit-breaker`)

Guardião determinístico de execução e orçamento para o ecossistema multiagente. Monitora em tempo real a profundidade das chamadas, a repetição de estados (detecção de loops/deadlocks), erros consecutivos e o teto de tokens/tempo por sessão. Quando uma anomalia ultrapassa os limiares de segurança, o circuito desarma (`OPEN`), registra a causa raiz e interrompe a cascata antes de desperdiçar recursos.

## 1. Princípios e Diretrizes Técnicas
- **Camada não funcional:** O disjuntor nunca altera o conteúdo das decisões de negócio; atua estritamente em infraestrutura, custo e fluxo.
- **Detecção determinística de loop:** Nós que produzem payloads com hash SHA-256 idêntico por 3 ciclos consecutivos são desarmados com `DEADLOCK_LOOP_DETECTED`.
- **Falha seca e transparente:** Ao desarmar, levanta `CircuitTripException` com causa raiz explícita em JSON estruturado.

## 2. Fluxo Operacional
1. `before_node_execution`: Verifica se o circuito está `CLOSED`. Valida tetos de passos e tokens, calculando hash SHA-256 da entrada.
2. `after_node_execution`: Incrementa ou reseta contadores de erro consecutivo.
3. `reset_circuit`: Transição supervisionada (HITL) para `HALF_OPEN` zerando contadores operacionais.

## 3. Formato de Saída Obrigatório
```json
{
  "circuit_status": "OPEN",
  "can_proceed": false,
  "trip_reason": "[DEADLOCK_LOOP_DETECTED] Payload idêntico detectado em ciclos consecutivos.",
  "action_required": "HUMAN_IN_THE_LOOP_APPROVAL"
}
```

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA permitir que subagentes alterem limiares de política do circuito em tempo de execução.
- NUNCA ocultar a causa técnica ao desarmar o disjuntor.
- NUNCA retomar execução em estado `OPEN` sem autorização humana explícita.
