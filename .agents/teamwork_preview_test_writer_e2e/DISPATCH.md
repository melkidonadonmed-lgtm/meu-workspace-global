## 2026-09-02T23:59:39Z

Sua identidade: teamwork_preview_test_writer_e2e
Seu diretório de trabalho: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_test_writer_e2e
Você DEVE ler o arquivo de requisitos originais em: c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md
Leia também:
- c:\Users\melki\meu-workspace-global\PROJECT.md
- c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_spec_miner_survey_3\survey_spec_report.md

Sua missão para a Trilha E2E Testing (Dual Track):
1. Criar o documento `c:\Users\melki\meu-workspace-global\TEST_INFRA.md` definindo metodologia (Category-Partition, BVA, Pairwise, Workload), inventário de testes e semântica de execução.
2. Criar o diretório de fixtures `projects/web_visual_auditor/tests/fixtures/`.
3. Criar fixtures HTML estáticas ricas e determinísticas:
   - `sample_page.html`: página com header, nav, main, article, button, h1, IDs, classes e geometrias previsíveis.
   - `sample_noisy_article.html`: página contendo scripts, tags style, SVG inline, nós noscript, comentários e conteúdo editorial útil para validação da limpeza semântica.
4. Criar módulo utilitário de geração de fixtures de imagens sintéticas em `projects/web_visual_auditor/tests/fixtures/image_fixtures.py`:
   - Gerar baseline e current idênticos (100x100, branco puro)
   - Gerar par com ruído leve canal <= 15 (ex: cinza 245 vs branco 255)
   - Gerar par com quadrado 20x20 divergente em canal > 15 (ex: vermelho puro ou preto) sobre base 100x100, comprovando matematicamente 400 pixels divergentes / 10000 = 4.0% exato
5. Criar a estrutura inicial da suíte E2E em `projects/web_visual_auditor/tests/test_e2e.py` estruturada pelos 4 Tiers (Tier 1: Feature Coverage, Tier 2: Boundary/Corner, Tier 3: Cross-Feature, Tier 4: Real-World Scenarios).
6. Ao concluir a criação dos arquivos de infraestrutura e fixtures, publicar `c:\Users\melki\meu-workspace-global\TEST_READY.md` conforme o template oficial do Project Pattern.
7. Gerar relatório de handoff formal em `c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_test_writer_e2e\handoff.md` e enviar mensagem ao orquestrador ao concluir.
Idioma obrigatório: Português (BR).
