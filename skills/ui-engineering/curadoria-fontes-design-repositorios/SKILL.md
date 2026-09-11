---
name: curadoria-fontes-design-repositorios
description: Busca, audita e valida referências de Design Systems, repositórios de código de agentes (Google ADK, MCP) e normas oficiais médicas/legais.
triggers:
  - "curadoria fontes"
  - "design repositorios"
  - "fontes design"
  - "repositorios ui"
  - "design system referencias"
---

# Skill: Curadoria de Referências, Repositórios e Fontes Oficiais

## Gatilhos de Ativação
- Consulta de sintaxe e padrões oficiais do Google ADK, Protocolo A2A ou servidores MCP.
- Busca por referências de Design System elegante, minimalista e acessível (Tailwind CSS, Material 3, Lucide).
- Verificação de normas regulatórias médicas (CFM, ANVISA, OMS) ou diretrizes de IA generativa.

---

## Fluxo Passo a Passo com Decisões Condicionais

### Passo 1: Seleção da Matriz de Fontes
- **DESIGN E INTERFACE:** `W3C/WCAG`, `Tailwind CSS Docs`, `Material.io`, `Lucide.dev`.
- **REPOSITÓRIOS E SDKs DE AGENTES:** `docs.cloud.google.com`, `ai.google.dev`, `github.com/google/adk-python`, `a2a-protocol.org`.
- **FONTES OFICIAIS E NORMAS:** CFM, ANVISA, OMS/WHO, Google Cloud Architecture Center.

### Passo 2: Execução do Grafo de Validação
1. Realizar busca direcionada utilizando operadores de domínio (`site:domain.com`).
2. Filtrar resultados desatualizados ou descontinuados (*deprecated*).
3. Confirmar licença open-source permissiva (MIT, Apache 2.0) para repositórios.

---

## O que NÃO Fazer

- **NÃO utilize fóruns informais, posts de blogs não verificados ou repositórios abandonados** como fontes primárias de arquitetura.
- **NÃO sugira bibliotecas descontinuadas (*deprecated*) ou sem suporte ativo**.
- **NÃO reproduza números de normas, leis ou regulamentações médicas sem conferir a fonte oficial atualizada**.
