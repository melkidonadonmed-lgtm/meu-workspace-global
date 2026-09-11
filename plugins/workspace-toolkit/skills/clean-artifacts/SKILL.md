---
name: clean-artifacts
description: Higieniza arquivos temporários, logs expirados e snapshots de rascunho do workspace com segurança Zero-Trust.
---

# Skill: Clean Artifacts (`/clean-artifacts`)

Esta habilidade orienta o agente a auditar e remover arquivos temporários expirados ou gerados durante sessões de desenvolvimento, garantindo conformidade com a política Zero-Trust.

## Procedimento de Execução

1. **Auditoria Prévia**:
   - Inspecione pastas temporárias como `scratch/`, `.pytest_cache/` e logs de depuração.
   - Liste os arquivos candidatos antes de qualquer remoção.

2. **Validação HITL (Human-in-the-Loop)**:
   - Nunca execute exclusões sem antes apresentar o resumo das alterações e solicitar a confirmação do usuário.

3. **Limpeza Segura**:
   - Execute a remoção apenas dos arquivos confirmados, preservando os artefatos históricos e arquivos protegidos por `.gitignore`.
