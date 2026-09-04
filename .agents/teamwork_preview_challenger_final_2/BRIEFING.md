# BRIEFING — 2026-09-03T04:24:00Z

## Mission
Desafiar adversariamente a higienização semântica e a inspeção do DOM (researcher.py e dom_auditor.py) em web_visual_auditor.

## 🔒 My Identity
- Archetype: empirical_challenger
- Roles: critic, specialist
- Working directory: c:\Users\melki\meu-workspace-global\.agents\teamwork_preview_challenger_final_2
- Original parent: ccc2ab57-1e80-4064-8e39-4de9a6ee1c52
- Milestone: preview_challenge_dom_sanitization
- Instance: 2 of 2

## 🔒 Key Constraints
- Review-only — do NOT modify implementation code
- Run tests and verifications yourself, empirical evidence required
- .agents/ holds only metadata (no code/tests in .agents/)
- Idioma obrigatório: Português (BR)

## Current Parent
- Conversation ID: ccc2ab57-1e80-4064-8e39-4de9a6ee1c52
- Updated: 2026-09-03T04:24:00Z

## Review Scope
- **Files to review**:
  - `projects/web_visual_auditor/web_visual_auditor/researcher.py`
  - `projects/web_visual_auditor/web_visual_auditor/dom_auditor.py`
- **Interface contracts**: `PROJECT.md`, `ORIGINAL_REQUEST.md`
- **Review criteria**: sanitização semântica, resquícios de tags (scripts, styles, SVGs com texto, inline styles, nós invisíveis, etc.), e inspeção de nós-chave/bounding boxes.

## Attack Surface
- **Hypotheses tested**:
  1. Scripts disfarçados (CDATA, modules, on* handlers) são purgados do texto nobre. (CONFIRMADO: purgados de clean_text).
  2. SVGs com texto interno aninhado (<text>, <tspan>, <foreignObject>) são purgados do texto nobre. (CONFIRMADO: purgados de clean_text).
  3. Styles inline e blocos <style> não vazam para o texto. (CONFIRMADO: purgados de clean_text).
  4. Tags desconhecidas e web components customizados têm texto preservado. (CONFIRMADO).
  5. Links com protocolos pseudo-javascript em maiúsculas (ex: `JAVASCRIPT:alert(1)`) furam a checagem em `extract_links`. (CONFIRMADO: bypass ativo devido a `href.startswith(...)` sem `.lower()`).
  6. Em `extract_title_and_snippet`, `<meta>` tags são destruídas prematuramente por `_purge_noise(soup)` antes da extração de og:title e description. (CONFIRMADO: falha de lógica).
  7. Elementos com `opacity: 0` no Playwright são classificados erroneamente como visíveis. (CONFIRMADO: `isOpacityZero` calculado mas omitido em `isVisible`).
  8. Elementos com largura zero (`width: 0px`) no fallback estrutural permanecem visíveis devido à condição `width <= 0 and height <= 0`. (CONFIRMADO: deveria ser `or`).
  9. Elementos com atributo nativo HTML5 `hidden` são ignorados no fallback estrutural. (CONFIRMADO: não avalia `el.has_attr("hidden")`).

- **Vulnerabilities found**:
  1. `researcher.py:179`: `extract_links` tem bypass case-sensitive para links `JAVASCRIPT:` / `JavaScript:`.
  2. `researcher.py:130`: `extract_title_and_snippet` executa `_purge_noise(soup)` que deleta todas as tags `<meta>`, impedindo a extração de `og:title` e `description` via meta tags.
  3. `dom_auditor.py:438`: Script de injeção no Playwright calcula `const isOpacityZero = parseFloat(style.opacity || '1') === 0;` na linha 435 mas não inclui `!isOpacityZero` em `const isVisible = !isDisplayNone && !isVisibilityHidden && !hasZeroDimensions;` na linha 438.
  4. `dom_auditor.py:571`: Fallback estrutural usa `width <= 0 and height <= 0` em vez de `or`, fazendo nós com largura 0 (ex: colapsados) serem marcados como `is_visible=True`.
  5. `dom_auditor.py:557`: Fallback estrutural ignora o atributo HTML5 `<... hidden>`.

- **Untested angles**:
  - Testes reais de rendering com GPU em browsers com aceleração gráfica (fora do escopo headless).

## Loaded Skills
- None

## Key Decisions Made
- Implementada suíte de testes adversariais empíricos em `projects/web_visual_auditor/tests/test_adversarial_preview.py` com marcações `@pytest.mark.xfail` documentando formalmente as vulnerabilidades detectadas.
- Veredito emitido: REQUEST_CHANGES devido aos bugs de bypass de link malicioso em `researcher.py`, destruição prematura de meta tags em `extract_title_and_snippet`, e falhas de classificação de visibilidade em `dom_auditor.py`.

## Artifact Index
- DISPATCH.md — histórico de mensagens recebidas
- progress.md — liveness e status
- handoff.md — relatório final com veredito
- projects/web_visual_auditor/tests/test_adversarial_preview.py — suíte de testes adversariais
