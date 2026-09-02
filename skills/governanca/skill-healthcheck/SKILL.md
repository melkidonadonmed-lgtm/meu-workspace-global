---
name: skill-healthcheck
version: 1.0.0
description: Auditoria contínua de integridade do catálogo de skills. Mapeia falhas de frontmatter, nomes divergentes, ausência de seções de restrição e redundâncias semânticas.
triggers:
  - "healthcheck"
  - "saude do catalogo"
  - "auditar skills"
  - "verificar skills"
  - "redundancia de skills"
---

# Auditoria e Saúde do Catálogo (`skill-healthcheck`)

Auditor de conformidade para prevenir degradação, links quebrados e redundâncias no ecossistema de habilidades.

## 1. Diretrizes e Princípios
- Validação automática de 100% dos arquivos `SKILL.md` sob o diretório `skills/`.
- Verificação de consistência entre o nome da pasta e o atributo `name` do frontmatter YAML.
- Cálculo de similaridade semântica Jaccard para alertar sobre sobreposição indevida de escopo.
- Hubs (`has-sub-skill: true`) e skills vendorizadas de terceiros (rastreadas em `skills-lock.json`) são isentas da cobrança da seção de restrições ("O que NÃO Fazer" / "Negative Bounds" / "What NOT to Do"), pois seguem convenções de origem próprias.

## 2. Fluxo Operacional
1. Varrer recursivamente todos os arquivos `SKILL.md`.
2. Analisar frontmatter YAML, kebab-case, comprimento da descrição e presença de seções de restrição.
3. Tokenizar descrições e calcular índice Jaccard entre pares de skills.
4. Emitir relatório detalhado com status de conformidade.

## 3. Formato de Saída Obrigatório
```json
{
  "status": "healthy",
  "total_skills": 18,
  "is_healthy": true,
  "total_issues": 0,
  "semantic_redundancies": []
}
```

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA ignorar falhas de sintaxe YAML ou nomes inconsistentes.
- NUNCA assumir conformidade sem inspecionar todos os subdiretórios de skills.
