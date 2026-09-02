# 0004. Governança Automatizada de Habilidades (SkillFactory & SkillHealthChecker)

Decidimos padronizar a criação e evolução de habilidades no catálogo através do motor de scaffolding `SkillFactory` e do validador estrito `SkillHealthChecker`, integrados diretamente às rotas do `AutoSkillRouter`.

## Contexto e Motivação

Conforme o Meta-Workspace passa a operar sobre diferentes stacks e projetos alvo, a quantidade de habilidades procedimentais (`SKILL.md`) cresce significativamente. Criar habilidades manualmente de forma não estruturada pode introduzir metadados inválidos, caminhos quebrados e falhas no roteamento cognitivo dos agentes.

## Decisão

1. **Scaffolding Padronizado via SkillFactory**: Toda nova habilidade deve ser instanciada através do `SkillFactory`, garantindo frontmatter YAML correto, especificação de dependências e documentação de disparo.
2. **Portão de Qualidade via SkillHealthChecker**: Nenhuma skill é adicionada ao catálogo ativo sem passar pela suíte de validação de integridade (links, schemas de ferramentas e sintaxe).
3. **Progressive Disclosure**: O `skill_parser.py` e o `AutoSkillRouter` utilizam carregamento sob demanda baseado nas descrições de alto nível, mantendo o consumo de tokens dos agentes estritamente enxuto e escalável.
