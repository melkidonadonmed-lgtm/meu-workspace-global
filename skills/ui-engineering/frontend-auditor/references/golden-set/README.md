# Golden Set — Âncoras de calibração

Antes de pontuar D2/D3, ler a âncora mais próxima do tipo de tela avaliada. A nota do alvo deve se posicionar **em relação** a estas referências, não no absoluto. Isso é o que torna auditorias de telas diferentes comparáveis entre si.

## Âncoras (descritas, não pontuar sem reler)

### Âncora 95 — "Instrumento refinado"
Interface de ferramenta madura estilo Linear/Raycast: uma família tipográfica + mono, escala de cinzas com um acento, zero elementos decorativos sem função, estados visuais em todo interativo, densidade alta porém organizada por proximidade e divisores. Erros típicos: nenhum visível sem inspeção cuidadosa.
→ Uma tela tira 90+ em D2 quando: não sobra nada para remover sem perder função, e cada decisão (raio, espaçamento, cor) se repete com consistência.

### Âncora 80 — "Produto bom, polimento pendente"
Dashboard SaaS competente: hierarquia clara, paleta controlada, componentes consistentes; mas com 1–2 falhas por tela — texto secundário com contraste limítrofe, um ícone fora do estilo, espaçamento irregular entre seções.
→ 75–89 em D2 quando: a tela está claramente organizada, mas uma varredura encontra inconsistências de token em menos de 1 minuto.

### Âncora 65 — "Funciona, mas genérico"
App de template: visual "correto" sem identidade — gradiente padrão, cards aninhados 3 níveis, ícones em quadrados coloridos, 6+ cores de UI, hero centrado com dois CTAs. Nada quebrado, nada memorável.
→ 60–74 em D2 quando: a tela funciona e não ofende, mas qualquer item da rubrica de consistência (D2.2–D2.4) falha em múltiplos lugares.

### Âncora 50 — "Bagunça organizada"
Ferramenta interna que cresceu sem direção: tudo empilhado na primeira tela, modais sobre modais, cores semânticas usadas como decoração, tipografia sem escala (tudo 13–14px), densidade alta sem agrupamento.
→ 40–59 em D2 quando: o usuário precisa *procurar* a ação principal; a hierarquia depende de ler o texto, não de ver a tela.

### Âncora 25 — "Quebrado"
Tela branca parcial, overflow horizontal, fonte não carregada, controles sem resposta, placeholder visível.
→ <40 quando falhas impedem completar a tarefa principal.

## Regra de duas passagens (obrigatória)

1. **Passagem cega**: pontuar D2 e D3 olhando **somente o screenshot**, sem ter lido o código. Anotar as notas.
2. **Passagem técnica**: rodar scripts, ler o código, pontuar D1 e D4.
3. **Revisão cruzada**: reler as notas de D2/D3 da passagem 1. Só ajustar se a evidência técnica revelar algo **invisível no screenshot** (ex.: hover inexistente). Nunca ajustar porque "o código é bonito/feio" — implementação não muda aparência.
