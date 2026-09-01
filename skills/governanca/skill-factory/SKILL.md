---
name: skill-factory
version: 1.0.0
description: Criação e padronização de novas habilidades no formato canônico SKILL.md com validação estrutural obrigatória antes da gravação no catálogo.
triggers:
  - "criar skill"
  - "nova skill"
  - "padronizar skill"
  - "fabricar skill"
  - "skill.md"
---

# Fábrica de Habilidades (`skill-factory`)

Módulo responsável pela fabricação, padronização e validação de novas habilidades modulares consumidas pelos agentes do ecossistema.

## 1. Diretrizes e Princípios
- Cada skill deve resolver um problema específico de ponta a ponta sem instruções vagas.
- O nome deve ser estritamente em **kebab-case** e corresponder ao diretório pai.
- O frontmatter YAML deve conter `name`, `version`, `description` (mínimo 20 caracteres) e `triggers`.

## 2. Fluxo Operacional
1. Coletar parâmetros da skill (nome, categoria, princípios, fluxo operacional, zonas de não-ação).
2. Gerar Markdown a partir do template oficial.
3. Validar sintaxe YAML e seções obrigatórias via `SkillHealthChecker`.
4. Persistir o arquivo `SKILL.md` no subdiretório apropriado em `skills/`.

## 3. Formato de Saída Obrigatório
```json
{
  "status": "success",
  "name": "nova-skill",
  "path": "skills/categoria/nova-skill/SKILL.md",
  "message": "Skill registrada com sucesso."
}
```

## 4. Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)
- NUNCA salvar skills com placeholders como `// código aqui` ou `/* TODO */`.
- NUNCA finalizar criação de skills sem validar se o nome no YAML coincide com o diretório.
- NUNCA criar personas puramente descritivas; foque em procedimentos operacionais e verificáveis.
