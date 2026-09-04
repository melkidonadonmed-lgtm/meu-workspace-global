## 2026-09-03T03:54:28Z

Sua identidade: teamwork_preview_spec_miner_survey_3
Seu diretório de trabalho: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_spec_miner_survey_3
Você DEVE ler o arquivo de requisitos originais em: c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md

Sua missão:
1. Extrair minuciosamente todas as especificações e critérios de aceitação de ORIGINAL_REQUEST.md.
2. Detalhar cada requisito (R1 a R5), limites numéricos (ex: channel > 15, vermelho puro #FF0000, tolerâncias, percentual exato, timeout com fallback), elementos DOM obrigatórios (header, main, article, button, nav, h1), atributos obrigatórios (x, y, width, height, id, classes, visibilidade).
3. Mapear a estratégia rigorosa de Testes Locais Determinísticos (sem internet ativa):
   - Fixtures locais estáticas em HTML servidas via file:// ou data URLs.
   - Imagens sintéticas baseline e current geradas deterministicamente com PIL para testar diff de 0% (idênticas), diff parcial (com alteração controlada acima e abaixo da tolerância 15) gerando diff_result.png com máscara vermelha #FF0000, e seletores de micro-componentes gerando diff_<selector>.png.
   - Mapear a matriz de testes necessária para 100% de aprovação no pytest.
   - Especificar a checagem de linter ruff check . limpo.
4. Gerar um inventário detalhado de requisitos e especificações de teste em c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_spec_miner_survey_3\survey_spec_report.md e entregar seu handoff.md.
5. Manter seu progress.md atualizado com 'Last visited' e enviar mensagem ao orquestrador ao concluir.
Idioma obrigatório: Português (BR).
