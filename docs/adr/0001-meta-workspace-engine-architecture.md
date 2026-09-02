# 0001. Arquitetura de Meta-Workspace Universal para Orquestração de Agentes

Decidimos estruturar o repositório como um Meta-Workspace universal (motor de orquestração de agentes, catálogo de skills governadas e barramento FastMCP) projetado para operar sobre qualquer projeto de software alvo, desacoplando o núcleo de ferramentas das aplicações locais em desenvolvimento.

## Contexto e Motivação

O repositório contém diretórios de projetos (`projects/`), mas estes são apenas ambientes satélites de experimentação e incubação. O propósito real do sistema é fornecer uma infraestrutura reutilizável, modular e resiliente de agentes autônomos (`MasterOrchestrator`, `AutoSkillRouter`, `ResilienceCircuitBreaker`) e ferramentas FastMCP capazes de inspecionar, refatorar e construir qualquer código externo.

## Decisão

1. **Núcleo do Domínio**: O domínio do sistema é a orquestração cognitiva, governança de habilidades e execução de ferramentas seguras (Zero-Trust).
2. **Desacoplamento de Projetos Alvo**: O motor deve receber caminhos de projetos alvo dinamicamente ou operar sobre contextos externos sem acoplamento estático com os projetos satélites locais.
3. **Padrão de Ferramentas**: Toda integração com o ecossistema externo (GCP, Workspace, APIs, File System) deve passar pelo Barramento FastMCP e respeitar os guardrails de segurança.
