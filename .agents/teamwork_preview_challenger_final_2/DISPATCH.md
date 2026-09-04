## 2026-09-03T04:20:25Z
Sua identidade: teamwork_preview_challenger_final_2
Seu diretório de trabalho: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_challenger_final_2
Você DEVE ler o arquivo de requisitos originais em: c:\Users\melki\meu-workspace-global\.agents\ORIGINAL_REQUEST.md
Leia também:
- c:\Users\melki\meu-workspace-global\PROJECT.md
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\researcher.py
- c:\Users\melki\meu-workspace-global\projects\web_visual_auditor\web_visual_auditor\dom_auditor.py
Sua missão:
Desafiar adversariamente a higienização semântica e a inspeção do DOM:
- Injetar HTMLs com tags maliciosas/complexas (scripts disfarçados, SVGs aninhados com texto interno, nós invisíveis via CSS, inline styles, noscript, tags desconhecidas).
- Validar que o texto purificado não contém qualquer resquício de scripts, styles ou tags svg.
- Validar a correta identificação dos nós-chave e das caixas delimitadoras (getBoundingClientRect).
- Emitir seu relatório com veredito (APPROVE ou REQUEST_CHANGES) em seu handoff.md e enviar mensagem ao orquestrador.
Idioma obrigatório: Português (BR).
