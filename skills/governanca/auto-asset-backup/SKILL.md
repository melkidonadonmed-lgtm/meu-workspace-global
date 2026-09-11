---
name: auto-asset-backup
description: Governança e backup automático de ativos reutilizáveis (Prompts, Skills e Agentes), sanitizando informações e mantendo a integridade do repositório Brain.
triggers:
  - "backup de ativos"
  - "backup de skills"
  - "backup drive"
  - "fazer backup"
  - "auto asset backup"
---

# SKILL: Governança e Backup Automático de Ativos (`auto-asset-backup`)

## Gatilho de Ativação
- Ativado automaticamente sempre que a IA finalizar a geração de uma nova Skill (`SKILL.md`), Arquitetura de Agente ou Prompt Otimizado, ou mediante a solicitação de salvamento de ativos reutilizáveis.

---

## Entradas Obrigatórias
1. `asset_payload`: O conteúdo completo do prompt, agente ou skill gerado.
2. `asset_type`: Declaração ou inferência do tipo (`SKILL`, `AGENT`, `PROMPT`).
3. `target_repository_path`: O diretório base de destino no repositório.

---

## Fluxo Passo a Passo com Decisões Condicionais

### Passo 1: Intercepção e Análise de Reutilização
- Avalie se o conteúdo gerado é um ativo reutilizável ou apenas uma resposta pontual ao usuário.
- *Condição:* Se for uma resposta contextual única, encerre o fluxo sem gravar. Se for uma instrução reutilizável, avance para o Passo 2.

### Passo 2: Sanitização e Padronização
- Remova dados sensíveis ou informações voláteis da conversa.
- Certifique-se de que a estrutura esteja padronizada:
  - **Skills:** Formato `SKILL.md` com YAML, entradas, fluxo e seções de restrições.
  - **Agentes:** Formato de especificação de papel, ferramentas e critérios de parada.

### Passo 3: Roteamento de Pastas
Determine o caminho de gravação final com base no tipo:

```text
[Ativo Identificado]
│
├─► Tipo: SKILL ────────────► Gravar em: .agents/skills/[nome_skill]/SKILL.md
├─► Tipo: AGENTE ───────────► Gravar em: .brain/state/agents/[nome_agente].md
└─► Tipo: MODELO_PROMPT ────► Gravar em: .brain/state/prompts/[nome_prompt].md
```

---

## Modelo de Saída (Log de Confirmação de Backup)

```json
{
  "backup_execution": {
    "status": "SUCCESS | SKIPPED",
    "asset_name": "Discussao_Clinica_Estruturada",
    "file_path": ".agents/skills/med_clinical_discussion/SKILL.md",
    "timestamp": "2026-08-16T00:00:00Z"
  }
}
```

---

## O que NÃO Fazer

- **NÃO sobrescreva arquivos existentes com o mesmo nome sem pedir autorização prévia** ou utilizar versionamento (`_v2`, `_v3`).
- **NÃO salve credenciais, senhas ou dados pessoais de usuários nos arquivos de backup**.
- **NÃO crie nomes de arquivos com espaços ou caracteres especiais** (use formato `kebab-case` ou `snake_case`).
