# Ativação das skills do repositório

Este workspace Arrowgram descreve o comportamento efetivo do runtime atual. O ponto central é:

> Uma skill do catálogo é ativada quando o conteúdo integral do seu SKILL.md é carregado pelo
> SkillParser e inserido em system_instruction. Não existe um executor execute_skill separado.

## Como ler o diagrama

- Verde representa descoberta, cache e evolução do catálogo.
- Azul representa o fluxo de uma requisição.
- Roxo representa seleção e injeção efetiva de uma skill.
- Laranja representa subagentes Python executados por outro mecanismo.
- Vermelho representa bloqueios de segurança e confirmação humana.
- Setas tracejadas representam observação, enriquecimento de contexto ou efeito em turno futuro.

## Fluxo principal

1. Na inicialização, SkillParser varre skills/**/SKILL.md, separa frontmatter e corpo e mantém
   metadata, body e full_content em cache.
2. SkillHealthChecker audita o catálogo ao final da recarga, mas seu relatório apenas gera logs:
   no runtime atual ele não impede que uma skill já carregada permaneça no cache.
3. Cada mensagem passa primeiro pelo Circuit Breaker e pelo SecurityGuard Zero-Trust.
4. A entrada sanitizada alimenta dois mecanismos:
   - AutoSkillRouter decide alvo, complexidade e modo de roteamento.
   - match_skills_by_query procura ID/nome, triggers inteiros ou pelo menos duas palavras
     relevantes dos triggers. Hubs de bundle não são injetáveis.
5. Quando o alvo do Router é do tipo skill, ele também é acrescentado a matched_skills.
6. Para cada ID final, get_skill_full_content recupera o SKILL.md integral.
7. build_system_prompt combina:
   - nível 1: índice leve de name + description de todo o catálogo;
   - nível 2: conteúdo integral apenas das skills selecionadas.
8. Esse system_instruction enriquecido segue para Gemini Interactions API. Sem cliente ou em caso
   de erro, o orquestrador usa o fallback local.
9. A saída é auditada, recebe o painel de despacho, é persistida e retorna com metadados.

## Ressalvas importantes

- DIRECT_RESPONSE, SINGLE_SKILL e MULTI_AGENT_CASCADE são decisões de roteamento; não executam uma
  skill por si mesmas.
- SINGLE_SKILL não limita matched_skills a um item: o matcher pode selecionar várias skills.
- MULTI_AGENT_CASCADE não dispara automaticamente todos os candidatos.
- Subagentes SQL, Workspace e Research são classes Python acionadas por verificações próprias de
  palavras-chave; não são SKILL.md.
- Uma skill criada para preencher um gap complexo é recarregada depois que o prompt do turno atual
  já foi montado. Ela passa a influenciar plenamente a próxima requisição.
- No caminho Antigravity online, a ativação é delegada ao SDK por skills_paths. No fallback local,
  os matches são apenas relatados; o conteúdo integral não é injetado pelo bridge.
- configs/agents_manifest.yaml declara skill_injection, mas não funciona como gate de runtime no
  código atual.

## Fontes no código

- [AutoSkillRouter](../../../agents/router.py): matriz, portão destrutivo, pontuação e modos.
- [MasterOrchestrator](../../../agents/orchestrator.py): segurança, matching, injeção, execução e
  resposta.
- [SkillParser](../../../skills/skill_parser.py): descoberta, cache, matching e full_content.
- [SkillHealthChecker](../../../skills/skill_healthcheck.py): auditoria do catálogo.
- [API Gateway](../../../agents/api_gateway.py): pontos de entrada HTTP e SSE.
- [Antigravity bridge](../../../agents/antigravity_bridge.py): caminho paralelo do SDK.

## Validar e gerar

Execute a partir da raiz do repositório:

    npx -y @hotdocx/arrowgram-agent@0.1.6 validate --root docs/diagrams/ativacao-skills
    npx -y @hotdocx/arrowgram-agent@0.1.6 build --root docs/diagrams/ativacao-skills --out dist

O diretório dist é saída gerada e descartável; as fontes editáveis são
arrowgram.workspace.json e diagram.json.
