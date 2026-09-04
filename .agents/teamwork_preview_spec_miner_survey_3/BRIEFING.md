# BRIEFING — 2026-09-03T03:56:00Z

## Mission
Mineração aprofundada de requisitos, critérios de aceitação, limites numéricos e arquitetura de testes determinísticos para o pacote projects/web_visual_auditor com base em ORIGINAL_REQUEST.md.

## 🔒 My Identity
- Archetype: specification-miner
- Roles: specification-miner, teamwork-specialist
- Working directory: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_spec_miner_survey_3
- Original parent: ccc2ab57-1e80-4064-8e39-4de9a6ee1c52
- Milestone: survey_spec_mining

## 🔒 Key Constraints
- Requisitos extraídos estritamente de ORIGINAL_REQUEST.md
- Limites numéricos estritos: divergência de canal > 15, máscara vermelho puro #FF0000, 0.0% diff baseline idêntico, fallback de domcontentloaded
- Elementos obrigatórios: header, main, article, button, nav, h1
- Atributos obrigatórios: x, y, width, height, id, classes, visibilidade computada
- Testes 100% determinísticos e locais sem internet (file://, data URLs, imagens sintéticas PIL)
- Matriz de testes para 100% aprovação no pytest e conformidade total ruff check
- Idioma obrigatório: Português (BR)
- Não implementar código de produção nesta etapa (somente mineração e especificação)

## Current Parent
- Conversation ID: ccc2ab57-1e80-4064-8e39-4de9a6ee1c52
- Updated: 2026-09-03T03:56:00Z

## Task Summary
- **What to build**: Inventário completo de requisitos e matriz de testes determinísticos para `projects/web_visual_auditor`.
- **Success criteria**: `survey_spec_report.md` gerado com especificações detalhadas, `progress.md` com liveness heartbeat, `handoff.md` com 5 seções e mensagem enviada ao parent.
- **Interface contracts**: `ORIGINAL_REQUEST.md`
- **Code layout**: `projects/web_visual_auditor/` (researcher.py, dom_auditor.py, visual_regression.py, component_auditor.py, cli.py)

## Key Decisions Made
- Estruturação do relatório com tabela oficial de Features Discovered e Edge Cases, além do detalhamento de cada requisito R1-R5, modelos de dados e matriz de testes offline.

## Artifact Index
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_spec_miner_survey_3\survey_spec_report.md — Especificação técnica exaustiva e matriz de testes determinísticos
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_spec_miner_survey_3\handoff.md — Relatório de handoff formal de 5 seções
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_spec_miner_survey_3\progress.md — Registro de liveness e progresso
