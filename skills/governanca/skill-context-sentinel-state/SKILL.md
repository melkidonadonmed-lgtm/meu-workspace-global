---
name: skill-context-sentinel-state
version: 1.0.0
description: Audita a integridade da janela de contexto, avalia saturação de tokens, isolamento semântico de dados e gera snapshots determinísticos de estado a cada 5 turnos com validação Pydantic/JSON.
triggers:
  - "context sentinel"
  - "auditar contexto"
  - "salvar estado"
  - "checkpoint de sessao"
  - "snapshot operacional"
  - "context rot"
---

# Context Sentinel & State Checkpoint Engine (`skill-context-sentinel-state`)

Audita a integridade da janela de contexto em conversas multi-turn e pipelines multiagente, avaliando saturação de tokens, isolamento semântico de dados e perda de contexto (*context rot* / *lost in the middle*). A cada ciclo de 5 turnos, extrai e compila o estado operacional da sessão em um snapshot estruturado e serializável, validado por um schema Pydantic/JSON para persistência determinística em SQLite local ou bancos vetoriais.

## 1. Princípios e Diretrizes Técnicas
- **Classificação Tripartite de Fatos:** Classificar todas as entradas em `[FATO]` (confirmado), `[PENDENCIA]` (em aberto) ou `[LACUNA]` (indispensável ausente).
- **Gatilho Determinístico:** Execução periódica a cada 5 turnos (`turn_counter % 5 == 0`) ou quando o consumo estimado ultrapassar 60% da cota.
- **Validação Estruturada:** Todo snapshot deve ser serializável em JSON estrito compatível com `StateCheckpointSchema`.

## 2. Fluxo Operacional Passo a Passo
1. **Auditoria de Contexto:** Calcular densidade de informação, identificar repetições de schemas ou dados estáticos e avaliar necessidade de poda (*context pruning*).
2. **Extração de Fatos e Variáveis:** Varrer mensagens recentes extraindo decisões irreversíveis, variáveis ativas e tarefas pendentes.
3. **Serialização e Validação:** Mapear os dados no schema JSON estruturado com validação de enums e campos obrigatórios.
4. **Persistência e Diretriz:** Enviar snapshot para persistência em SQLite (`shared/state/sessions.db`) e definir a próxima ação imediata.

## 3. Formato de Saída Obrigatório (JSON Schema)
```json
{
  "session_id": "sess_id_exemplo",
  "turn_number": 5,
  "context_health": "healthy",
  "noise_detected": [],
  "pruning_recommended": false,
  "objective": "Declaração clara do objetivo ativo.",
  "facts": [
    {"tag": "FATO", "content": "Decisão confirmada."},
    {"tag": "PENDENCIA", "content": "Ação em andamento."},
    {"tag": "LACUNA", "content": "Dado indispensável ausente."}
  ],
  "variables": {
    "target_database": "sqlite_wal"
  },
  "next_action": "Próximo passo acionável.",
  "requires_context_flush": false
}
```

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA inferir variáveis ou decisões que não foram explicitamente confirmadas no histórico.
- NUNCA omitir lacunas essenciais — classifique-as explicitamente como `[LACUNA]`.
- NUNCA executar mutações destrutivas na janela de contexto sem sinalização prévia (`pruning_recommended = true`).
