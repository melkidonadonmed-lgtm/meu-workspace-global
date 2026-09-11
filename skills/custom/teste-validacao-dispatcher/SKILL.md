---
name: teste-validacao-dispatcher
description: Habilidade de teste e simulação de baixo impacto para verificar a integridade estrutural, a latência de ativação semântica e a robustez do despacho hierárquico sob a SkillFactory e o orquestrador global.
triggers:
  - "teste validacao dispatcher"
---

# Teste Validação Dispatcher (`teste-validacao-dispatcher`)

Esta habilidade serve como uma sonda de teste (mock/sonda) para garantir a integridade de rotas funcionais, prevenção de regressões de dispatch e calibração de tempo de execução (lifecycle loops) sem realizar alterações reais no sistema.

## 1. Diretrizes e Princípios
- Operar estritamente em modo de simulação passiva (dry-run).
- Validar se o motor do orquestrador global consegue extrair e despachar intenções sob demanda.
- Servir como baseline de comparação de latência e consumo de tokens contra skills de produção mais pesadas.

## 2. Fluxo Operacional
1. Disparar evento simulado no barramento de comunicação do dispatcher.
2. Monitorar e registrar os metadados de tráfego, garantindo que o transporte de dados (STDIN/STDOUT ou JSON-RPC) ocorra de forma fluida.
3. Emitir payload de sucesso sinalizando integridade do despacho de skills da SkillFactory.

## 3. Formato de Saída Obrigatório
A resposta de status de integridade deve seguir o formato estruturado abaixo:
```json
{
  "status": "success",
  "test_module": "hierarchical_dispatcher",
  "is_valid": true,
  "metrics": {
    "latency_ms": 12,
    "payload_bytes": 140
  }
}
```

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA executar ações reais ou modificações físicas de arquivos de código fora do escopo de teste.
- NUNCA pular etapas de validação estrutural do catálogo durante a calibração de rotas.
- NUNCA gerar triggers com palavras-chave genéricas como "teste" sem isolar devidamente a skill de testes.

