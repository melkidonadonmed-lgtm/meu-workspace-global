---
name: frontend-auditor
description: Auditoria estruturada de interfaces frontend com nota comparativa, evidência automatizada e histórico. Use quando o usuário pedir para avaliar, revisar, auditar ou dar nota a uma página web, app, dashboard, landing page ou qualquer UI (a partir de URL, screenshot, arquivos HTML/CSS/JS ou projeto React/Vite). Também aciona em frases como "avalie meu frontend", "dê uma nota pro design", "review de UI/UX", "auditoria de frontend", "o que melhorar nessa tela", "QA visual", "compare antes e depois de um redesign", "regrediu alguma coisa no front?". Executa probes comportamentais (cliques, teclado, forms), scan axe-core de acessibilidade, compara com auditorias anteriores e produz relatório com nota 0–100 por dimensão, veredito e plano de melhorias priorizado.
triggers:
  - "frontend auditor"
  - "auditar frontend"
  - "revisar interface"
  - "qualidade de frontend"
  - "inspecionar frontend"
---

# Frontend Auditor

Auditar uma interface em 4 dimensões com **evidência automatizada**, nota 0–100 ancorada em referências fixas e histórico comparável. Mesma tela, mesmas regras, mesma nota.

## Workflow

1. **Escolher o perfil.** Perguntar ou inferir pelo contexto: `landing`, `dashboard`, `design-tool` (padrão: `generic`, sem ajustes). Ler `references/profiles/<perfil>.md` — ele redefine pesos e marca itens N/A.
2. **Coletar evidência mecânica** (rodar os três, em paralelo quando possível):
   - `scripts/mechanical_checks.py <alvo>` — HTML estático: meta, labels, landmarks, headings, alt, lorem ipsum.
   - `scripts/behavioral_probe.py <alvo> --out probe.json --screens screens/` — Playwright: cliques em controles, navegação por Tab, forms, tela branca, zoom 200%, offline. Requer Chromium (usa o do sistema).
   - `scripts/axe_scan.py <alvo> --out axe.json --screens screens/` — axe-core: violações de acessibilidade + screenshots dos temas claro/escuro e reduced-motion.
   - `<alvo>` aceita URL ou caminho de arquivo HTML. Se o usuário enviou só screenshot, pular os scripts e marcar os itens dependentes como `[N/A — sem evidência automatizada]`.
3. **Passagem cega (obrigatória).** Antes de ler código ou saída de script, pontuar D2 e D3 olhando apenas o screenshot, ancorando em `references/golden-set/README.md`. Anotar.
4. **Passagem técnica.** Com os JSONs dos scripts, pontuar D1 e D4 seguindo `references/rubric.md`. As regras D1.2, D1.4, D4.1, D4.2 têm fonte de dados definida — usar o número do script, não impressão.
5. **Revisão cruzada.** Só ajustar D2/D3 se a evidência técnica revelar algo invisível no screenshot. Nunca ajustar por simpatia/antipatia ao código.
6. **Persistir e comparar.**
   - `scripts/audit_store.py save <projeto> notas.json` — grava a auditoria.
   - Se já houver histórico: `scripts/audit_store.py diff <projeto>` e incluir a tabela Δ no relatório.
   - Se houver screenshot anterior: `scripts/visual_diff.py antes.png depois.png --out diff.png` e anexar o veredito visual.
7. **Gerar o relatório** no formato abaixo.

## Classificação de evidência (obrigatória em cada achado)

- `[VERIFICADO]` — confirmado por screenshot, DOM, console ou teste de interação.
- `[INFERIDO]` — provável pelo código/padrão, não testado diretamente.
- `[N/A]` — impossível avaliar; sai do denominador e o peso é redistribuído.

## Formato do relatório (obrigatório)

```
# Auditoria Frontend — <alvo> — <data> — perfil: <perfil>

## Nota geral: NN/100 — <veredito>
Vereditos: ≥90 Excelente · 75–89 Bom · 60–74 Aceitável · 40–59 Fraco · <40 Crítico

## Quadro de notas
| Dimensão | Nota | Peso | Contribuição |
|---|---|---|---|
| D1 Funcionalidade | NN | xx% | NN |
| D2 Design visual | NN | xx% | NN |
| D3 Tipografia & conteúdo | NN | xx% | NN |
| D4 Acessibilidade & técnica | NN | xx% | NN |

## Evidência automatizada
- behavioral_probe: X/Y cliques ok, N erros de console, M requests falhos
- axe-core: N violações (C críticas/sérias): <lista das 5 principais>
- mechanical_checks: <falhas>

## Achados
### Críticos (bloqueiam uso)  / ### Maiores  / ### Menores
- [VERIFICADO] descrição — onde — regra violada

## Plano de melhorias (impacto/esforço)
1. **Ação concreta** — +N pts em DN — esforço P/M/G

## Comparativo com auditoria anterior (se houver)
| Dimensão | Antes | Agora | Δ |
### Regressões por item / ### Melhorias por item
Diff visual: <veredito do visual_diff>
```

## Diretrizes

- **Nota sem evidência é proibida.** Cada ponto retirado cita o achado; cada achado cita a regra.
- **Melhorias acionáveis**: "aumentar contraste do texto secundário de #666 para #595959 (D4.1)" e não "melhorar contraste".
- **Não reescrever a UI** salvo pedido explícito — a saída padrão é o relatório.
- **Regressão tem prioridade**: se o diff mostrar queda em qualquer item, o relatório abre com isso.
- **Idioma**: seguir o do usuário.

## O que NÃO Fazer

- Não atribuir nota sem evidência rastreável nem omitir a classificação `[VERIFICADO]`, `[INFERIDO]` ou `[N/A]`.
- Não alterar ou reescrever a interface auditada sem pedido explícito do usuário.
- Não tratar itens sem evidência disponível como falhas; marcá-los como `[N/A]` e redistribuir o peso conforme a rubrica.
- Não expor segredos, credenciais ou dados pessoais encontrados no alvo ou nos artefatos de auditoria.
