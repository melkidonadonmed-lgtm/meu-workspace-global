# Perfil: Dashboard / SaaS de dados

Painéis com métricas, tabelas, gráficos, filtros. Usuário recorrente, sessões longas.

## Ajustes de peso
- D1: 40% (ferramenta de trabalho — quebrar custa caro)
- D2: 25%
- D3: 10%
- D4: 25%

## Regras específicas do perfil
- **Densidade é virtude**: inverter D2.5 — penalizar espaço desperdiçado e painéis que escondem dados atrás de cliques desnecessários; elogiar mais dados por tela com hierarquia clara
- Tabelas: cabeçalho fixo, ordenação, alinhamento numérico à direita — cada ausência é −2 em D1.4
- Gráficos: precisam de rótulos ou tooltip; gráfico sem eixo/legenda legível → D3.4 metade
- Estados (D1.6) valem dobro: dashboard sem skeleton/loading parece quebrado em rede lenta
- Filtros e busca precisam de estado visível (chip, badge) — sem isso, D2.6 metade
- Responsividade (D1.7): aceitar N/A se o produto for explicitamente desktop-only; senão manter
