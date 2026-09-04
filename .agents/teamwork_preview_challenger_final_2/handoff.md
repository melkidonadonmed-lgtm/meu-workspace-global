# Relatório de Handoff — Desafio Adversarial de Preview (DOM & Sanitização)

**Identidade:** `teamwork_preview_challenger_final_2`  
**Papel:** Empirical Challenger (critic / specialist)  
**Veredito:** **REQUEST_CHANGES**  
**Data:** 2026-09-03T04:25:00Z  

---

## 1. Observation

Durante a auditoria adversarial aprofundada dos módulos `projects/web_visual_auditor/web_visual_auditor/researcher.py` e `projects/web_visual_auditor/web_visual_auditor/dom_auditor.py`, foram observadas as seguintes evidências de código e comportamentos empíricos:

### 1.1. Higienização Semântica Robusta (Pontos Fortes Observados)
- Em `researcher.py` (`SemanticHTMLCleaner._purge_noise`, linhas 104-118), nós das tags contidas em `DEFAULT_REMOVE_TAGS` (`script`, `style`, `svg`, `noscript`, `iframe`, etc.) são decompostos via `tag.decompose()`, eliminando a tag e toda a sua subárvore.
- Tags `<svg>` com textos internos aninhados (`<text>`, `<tspan>`, `<foreignObject>`) são purgadas em 100%, sem nenhum vazamento para o texto nobre (`clean_text`).
- Blocos `<style>`, CSS inline e atributos de manipuladores de eventos `on*` (`onclick`, `onmouseover`, etc.) são eliminados.

### 1.2. Falha de Segurança: Bypass de Links Maliciosos em `extract_links`
- No arquivo `projects/web_visual_auditor/web_visual_auditor/researcher.py`, linhas 177-182:
```python
177:         for a in soup.find_all("a", href=True):
178:             href = a["href"].strip()
179:             if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
180:                 continue
181: 
182:             full_url = urljoin(base_url, href) if base_url else href
```
- **Fato observado:** O método `href.startswith(...)` na linha 179 é sensível a maiúsculas e minúsculas (case-sensitive). Links como `<a href="JAVASCRIPT:alert(1)">` ou `<a href="JavaScript:steal()">` retornam `False` para `href.startswith(("javascript:", ...))` e são indevidamente extraídos como referências de fonte legítimas (`SourceReference`).

### 1.3. Defeito Lógico: Destruição Prematura de Meta Tags em `extract_title_and_snippet`
- No arquivo `projects/web_visual_auditor/web_visual_auditor/researcher.py`, linhas 65-73 e 129-152:
```python
65:     DEFAULT_REMOVE_TAGS: set[str] = {
...
73:         "meta",
...
79:     }
```
```python
129:         soup = self._parse_soup(raw_html)
130:         self._purge_noise(soup)
...
142:                 meta_og = soup.find("meta", property="og:title")
143:                 if meta_og and meta_og.get("content"):
144:                     title = str(meta_og.get("content", "")).strip()
...
148:         meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
149:             "meta", property="og:description"
150:         )
```
- **Fato observado:** A linha 130 executa `self._purge_noise(soup)`, que chama `tag.decompose()` para todas as tags em `self.remove_tags`. Como `"meta"` está em `DEFAULT_REMOVE_TAGS` (linha 73), todas as tags `<meta>` são destruídas na linha 130. Subsequentemente, as linhas 142 e 148 buscam `soup.find("meta", ...)` em uma árvore onde todas as meta tags já deixaram de existir, tornando impossível o fallback de título via `og:title` ou snippet via `meta description`.

### 1.4. Defeito de Visibilidade no Playwright: `isOpacityZero` Ignorado
- No arquivo `projects/web_visual_auditor/web_visual_auditor/dom_auditor.py`, linhas 431-438:
```javascript
431:                     const rect = el.getBoundingClientRect();
432:                     const style = window.getComputedStyle(el);
433: 
434:                     const isDisplayNone = style.display === 'none';
435:                     const isVisibilityHidden = (style.visibility === 'hidden' || style.visibility === 'collapse');
436:                     const isOpacityZero = parseFloat(style.opacity || '1') === 0;
437:                     const hasZeroDimensions = (rect.width <= 0 || rect.height <= 0);
438: 
439:                     const isVisible = !isDisplayNone && !isVisibilityHidden && !hasZeroDimensions;
```
- **Fato observado:** Na linha 436, a variável `isOpacityZero` é calculada. Contudo, na linha 438, a expressão que define `isVisible` é `!isDisplayNone && !isVisibilityHidden && !hasZeroDimensions`, omitindo `!isOpacityZero`. Elementos 100% transparentes (`opacity: 0`) são reportados como `is_visible=True` no runtime Playwright.

### 1.5. Divergência e Defeito de Dimensão Zero no Fallback Estrutural
- No arquivo `projects/web_visual_auditor/web_visual_auditor/dom_auditor.py`, linhas 571-575:
```python
571:                 # Coordenadas X e Y
572:                 if not is_visible or (width <= 0 and height <= 0):
573:                     x_coord = 0.0
574:                     y_coord = y_cursor
575:                     is_visible = False
```
- **Fato observado:** A condição na linha 572 utiliza o operador lógico `and`: `(width <= 0 and height <= 0)`. Se um elemento colapsado possuir largura zero (`width: 0px`) mas altura positiva (`height: 50px`), a condição avalia como `False`, e `is_visible` permanece `True`. Isso diverge diretamente da verificação do Playwright (`rect.width <= 0 || rect.height <= 0`), onde qualquer dimensão nula desqualifica a visibilidade.

### 1.6. Ausência de Suporte ao Atributo Nativo HTML5 `hidden` no Fallback
- No arquivo `projects/web_visual_auditor/web_visual_auditor/dom_auditor.py`, linhas 547-560:
```python
547:                 # Avaliação de visibilidade
548:                 is_display_none = computed_styles.get("display") == "none"
549:                 is_visibility_hidden = computed_styles.get("visibility") in ("hidden", "collapse")
550:                 has_hidden_class = any(
551:                     cls in ("hidden-box", "zero-dim-box", "hidden", "invisible") for cls in classes
552:                 )
...
557:                 is_visible = not (
558:                     is_display_none or is_visibility_hidden or has_hidden_class or is_aria_hidden
559:                 )
```
- **Fato observado:** O fallback não verifica `el.has_attr("hidden")`. Elementos com `<button hidden>Texto</button>` são marcados como `is_visible=True` no modo fallback.

---

## 2. Logic Chain

1. **Premissa 1 (Segurança de Links):** O requisito R1 de `ORIGINAL_REQUEST.md` exige que a extração semântica retorne referências normalizadas e purificadas de ruído. URLs contendo `javascript:` não devem ser propagadas. Como demonstrado na Observação 1.2, a checagem `href.startswith` não normaliza `href.lower()`, permitindo que links com esquemas em maiúsculas (`JAVASCRIPT:alert(1)`) passem incólumes para a lista de `references`.
2. **Premissa 2 (Integridade de Metadados):** O método `extract_title_and_snippet` tem a finalidade de extrair título e snippet, utilizando metadados OpenGraph (`og:title`) e `meta description` como fallback prioritário antes do corpo do texto. Como demonstrado na Observação 1.3, ao invocar `_purge_noise(soup)` antes de inspecionar as tags `<meta>`, o método elimina as tags de onde pretendia ler os dados, tornando os blocos de fallback em linhas 142-152 inoperantes.
3. **Premissa 3 (Inspeção Precisa do DOM):** O requisito R2 exige a extração de visibilidade computada fidedigna. Como demonstrado na Observação 1.4, o script injetado no Playwright calcula explicitamente `isOpacityZero`, mas o desenvolvedor esqueceu de incluí-lo na conjunção lógica de `isVisible`. Além disso, na Observação 1.5, a discrepância entre a condição `rect.width <= 0 || rect.height <= 0` (Playwright) e `width <= 0 and height <= 0` (Fallback) faz com que elementos com uma das dimensões zerada sejam considerados visíveis no fallback. Por fim, a ausência de checagem do atributo HTML5 `hidden` (Observação 1.6) viola o princípio de conformidade semântica.
4. **Conclusão Lógica:** O sistema apresenta vulnerabilidade de sanitização de links e regressões de cálculo de visibilidade/extração de metadados que comprometem a fidelidade das auditorias visual e semântica.

---

## 3. Caveats

- A suíte de testes `projects/web_visual_auditor/tests/test_adversarial_preview.py` foi criada com os testes das falhas identificadas marcados com `@pytest.mark.xfail` explicativos, permitindo que a suíte execute sem interrupções até que os ajustes sejam aplicados pelos especialistas de implementação.
- Não foram auditadas acelerações de GPU nativa do WebGL dentro do contexto headless do Chromium, por estar fora do escopo de inspeção geométrica básica do DOM especificado em R2.

---

## 4. Conclusion

O veredito é **REQUEST_CHANGES**.

A implementação de base é robusta na eliminação de scripts, styles e SVGs vetoriais no texto nobre (`clean_text`), mas requer correções cirúrgicas antes da aprovação final:

1. **Em `researcher.py`:**
   - Na linha 179 de `extract_links`: alterar para `href_lower = href.lower()` e verificar `href_lower.startswith(("#", "javascript:", "mailto:", "tel:"))`.
   - Em `extract_title_and_snippet`: extrair os metadados de `<meta>` do `soup` **antes** de chamar `self._purge_noise(soup)` (ou remover provisoriamente `"meta"` de `remove_tags` dentro desse fluxo específico).
2. **Em `dom_auditor.py`:**
   - Na linha 438 de `_evaluate_and_extract_nodes`: incluir `&& !isOpacityZero` na expressão de `isVisible`.
   - Na linha 572 de `_inspect_html_structural_fallback`: alterar a condição para `(width <= 0 or height <= 0)`.
   - Na linha 548 de `_inspect_html_structural_fallback`: incluir `is_html_hidden = el.has_attr("hidden")` na composição de `is_visible`.

---

## 5. Verification Method

Para verificar independentemente todas as observações e falhas reportadas:

1. **Inspecionar a suíte adversarial criada:**
   - Arquivo: `projects/web_visual_auditor/tests/test_adversarial_preview.py`
2. **Comando de Teste Pytest:**
   ```powershell
   uv run pytest projects/web_visual_auditor/tests/test_adversarial_preview.py -v
   ```
3. **Condições de Invalidação:**
   - Se `test_adversarial_link_case_sensitive_javascript_bypass` falhar sem `@pytest.mark.xfail`, comprova o vazamento de links `JAVASCRIPT:`.
   - Se `test_extract_title_and_snippet_preserves_meta_information` falhar sem `@pytest.mark.xfail`, comprova a destruição de meta tags por `_purge_noise`.
   - Se `test_dom_auditor_zero_width_or_height_visibility_discrepancy` falhar sem `@pytest.mark.xfail`, comprova a falha da condição `and` para elementos com dimensão zero.
