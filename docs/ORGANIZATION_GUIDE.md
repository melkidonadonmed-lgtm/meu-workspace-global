# 🏛️ Guia Definitivo de Organização, Governança e Manutenção do Workspace

> **Ambiente:** `C:\Users\melki\meu-workspace-global`  
> **Papel:** Manual de Referência e Boas Práticas Operacionais para Engenharia de Agentes, Skills e Projetos.

---

## 1. Topologia de Diretórios do Ecossistema

O repositório foi reorganizado sob o princípio estrito de **Separação de Conceitos (Separation of Concerns)**, onde o Meta-Workspace funciona como motor de inteligência e orquestração, e as aplicações de usuário residem no hub de projetos:

```
C:\Users\melki\
│
├── 🧠 meu-workspace-global/                  [O MOTOR COGNITIVO - ENGINE]
│   ├── agents/                               (Hub central do MasterOrchestrator e router)
│   │   ├── orchestrator.py                   (Orquestrador central stateful)
│   │   ├── router.py                         (AutoSkillRouter determinístico)
│   │   ├── api_gateway.py                    (Gateway FastAPI com endpoints REST e SSE)
│   │   ├── antigravity_bridge.py             (Ponte de integração Google Antigravity SDK)
│   │   └── specialized/                      (Subagentes especialistas nativos)
│   │       ├── sql_specialist.py             (Especialista BigQuery e SQL)
│   │       ├── html_modular_specialist.py    (Especialista em UI modular e HTML5)
│   │       ├── customer_issue_reviewer.py    (Wrapper Python do especialista em chamados)
│   │       ├── customer_issue_reviewer_go/   (Módulo nativo Go com Google ADK v2)
│   │       ├── workspace_specialist.py       (Especialista em scan local e Drive)
│   │       ├── security_guard.py             (Sentinela Zero-Trust de prompts e PII)
│   │       └── research_evolution_specialist.py (Especialista em deep research e SkillFactory)
│   ├── skills/                               (Catálogo de 69 skills governadas)
│   │   ├── governanca/, auditoria/, ui-engineering/, analytics/, arquitetura/, engenharia/
│   │   ├── skill_parser.py, skill_factory.py, skill_healthcheck.py
│   │   └── [links declarativos para .agents/skills/]
│   ├── rules/                                [DIRETÓRIO DE GOVERNANÇA E REGRAS]
│   │   ├── global_guardrails.md              (Restrições de segurança e Zero-Trust)
│   │   ├── routing_rules.md                  (Critérios determinísticos de despacho cognitivo)
│   │   └── formatting_standards.md           (Padrões de código, JSON e formatação pt-BR)
│   ├── configs/                              (Manifestos e definições declarativas)
│   │   ├── skills_manifest.yaml              (Índice central de todas as skills e destinos)
│   │   ├── agents_manifest.yaml              (Manifesto oficial de subagentes)
│   │   ├── guardrails.yaml                   (Padrões regex de segurança)
│   │   └── .env.example                      (Exemplo de variáveis de ambiente)
│   ├── mcp_servers/                          (Barramento FastMCP para BigQuery e Workspace)
│   ├── shared/                               (Circuit breaker, logger, state e auth)
│   ├── inbox/                                (Área de quarentena e pacotes de skills avulsas)
│   └── tests/                                (Suíte de 61 testes automatizados - 100% pass)
│
├── 📁 Brain\projetos\                        [O HUB DE CÓDIGO - APLICAÇÕES ALVO]
│   ├── pcm/                                  (PrescMed v2.0.0 - React 19 + Tailwind v4 + Vite)
│   ├── canvas_ide/                           (Canvas IDE visual interativo)
│   ├── keepdocs-workspace/                   (Plataforma KeepDocs de notas e documentação)
│   ├── prototype-orchestrator-bigquery/      (Protótipo de orquestração de dados)
│   └── WAOE/, agent-md-cloudrun/, etc.
│
└── 🔒 secrets/                              [COFRE LOCAL PROTEGIDO]
    ├── certificados/                         (Certificado PFX, CNH-e)
    └── oauth_e_keys/                         (Chaves OAuth Google Cloud, recovery codes)
```

---

## 2. Como Registrar uma Nova Skill Sem Quebrar o Roteador

Para adicionar uma nova habilidade ao catálogo de forma 100% estável:

### Passo 1: Criar a pasta e o `SKILL.md`
Crie o diretório da skill dentro da categoria temática adequada em `skills/<bundle>/<nome-da-skill>/SKILL.md`.
O arquivo **deve** conter o cabeçalho YAML obrigatório:

```markdown
---
name: minha-nova-skill
version: 1.0.0
description: Descrição clara do que a skill faz.
triggers:
  - palavra chave 1
  - frase de ativacao
---

# Instruções da Skill
...
```

### Passo 2: Adicionar a Skill na Matriz do Roteador (`agents/router.py`)
No arquivo [agents/router.py](file:///C:/Users/melki/meu-workspace-global/agents/router.py), adicione a tupla correspondente na `ROUTING_MATRIX`:

```python
ROUTING_MATRIX: list[tuple[str, str, tuple[str, ...]]] = [
    ...
    ("minha-nova-skill", "categoria", ("palavra chave 1", "frase de ativacao")),
]
```

### Passo 3: Atualizar o Manifesto de Skills
Execute a sincronização automática do manifesto para remapear caminhos e verificar se não há rotas quebradas:

```powershell
python -c "from skills.skill_parser import SkillParser; p = SkillParser(); print('Skills:', len(p.list_available_skills()))"
```

---

## 3. Como Atualizar Regras Globais

O diretório [rules/](file:///C:/Users/melki/meu-workspace-global/rules) é a **fonte única da verdade** de comportamento do sistema:

1. **Novas Restrições de Segurança:** Atualize [rules/global_guardrails.md](file:///C:/Users/melki/meu-workspace-global/rules/global_guardrails.md). Caso a regra exija bloqueio via regex pré-execução, replique o padrão em [configs/guardrails.yaml](file:///C:/Users/melki/meu-workspace-global/configs/guardrails.yaml).
2. **Novas Regras de Despacho:** Documente em [rules/routing_rules.md](file:///C:/Users/melki/meu-workspace-global/rules/routing_rules.md) e configure a lógica correspondente em [agents/router.py](file:///C:/Users/melki/meu-workspace-global/agents/router.py).
3. **Novos Padrões de Saída / Código:** Registre em [rules/formatting_standards.md](file:///C:/Users/melki/meu-workspace-global/rules/formatting_standards.md).

---

## 4. Procedimento de Validação de Integridade e Testes

Sempre que realizar modificações no ecossistema, execute o ciclo de validação tríplice:

```powershell
# 1. Validação de Linter e Estilo (Ruff)
uv run ruff check .

# 2. Suíte Completa de Testes Automatizados (61 testes)
uv run pytest

# 3. Healthcheck Específico do Catálogo de Skills
uv run python -m skills.skill_healthcheck
```

Se todos os passos retornarem sucesso (código 0), o ambiente está íntegro e pronto para commit ou execução em produção.
