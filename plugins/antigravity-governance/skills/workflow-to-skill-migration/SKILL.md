---
name: workflow-to-skill-migration
description: Guia e procedimentos automatizados para converter fluxos de trabalho legados (Workflows) em Agent Skills canônicas no Antigravity com Progressive Disclosure.
---

# Migração e Criação de Agent Skills

Este documento orienta a estruturação de procedimentos e automações repetíveis no ecossistema Antigravity, em conformidade com a depreciação de **Workflows** em favor de **Agent Skills**.

---

## Estrutura Canônica de uma Skill

Toda nova rotina automatizada deve seguir a seguinte topologia de diretório:

```text
skills/<nome-da-skill>/
├── SKILL.md                 # Arquivo principal de instruções com frontmatter YAML
├── scripts/                 # Scripts determinísticos de automação (opcional)
├── resources/               # Templates e dados estáticos (opcional)
└── references/              # Documentação detalhada e runbooks (opcional)
```

---

## Passos para Converter um Workflow em Skill

### 1. Criar o Diretório e o Frontmatter
Defina o identificador único em kebab-case (`name`) e uma descrição em terceira pessoa (`description`) que explique claramente **o que** a skill faz e **quando** deve ser ativada:

```yaml
---
name: minha-nova-skill
description: >-
  Executa a rotina de validação e release de serviços. Use quando o usuário 
  solicitar preparação de release ou deploy.
---
```

### 2. Decompor Passos Lineares em Fases Claras
Ao contrário dos workflows legados que eram sequências de prompts soltos, estruture as etapas com:
- **Objetivo da etapa**
- **Comandos exatos a executar**
- **Critério de sucesso / validação**

### 3. Extrair Scripts Complexos para `scripts/`
Evite comandos bash/powershell gigantescos inline no markdown. Encapsule-os em scripts dedicados na pasta `scripts/` e invoque-os com links relativos:
`python ./scripts/validate.py`

### 4. Isolar Documentação Volumosa em `references/`
Utilize o princípio de **Progressive Disclosure**: mantenha o `SKILL.md` enxuto e referencie arquivos adicionais na pasta `references/` para que o agente os leia apenas quando necessário.

---

## Checklist de Validação

- [ ] Nome do diretório idêntico ao `name` no frontmatter YAML.
- [ ] Descrição rica (> 20 caracteres) com gatilhos de contexto claros.
- [ ] Scripts auxiliares possuem permissão de execução e tratamento de erro.
- [ ] Validação realizada com a suíte de testes de integridade (`test_skills_healthcheck.py`).
