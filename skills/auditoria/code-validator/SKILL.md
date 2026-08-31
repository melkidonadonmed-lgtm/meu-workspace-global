---
name: code-validator
version: 1.0.0
description: Validador de Código, Expansão de Contexto e Matriz de Risco Percentual. Audita bases de código do macro ao micro linha a linha, expande contexto, calcula risco percentual com justificativa causal obrigatória e gera relatório antes de qualquer refatoração.
triggers:
  - "valide este código"
  - "audite este código"
  - "analise o risco deste código"
  - "expanda o contexto deste repositório"
  - "revisão de código com porcentagem de risco"
  - "check de segurança de código"
---

# SKILL.md — Validador de Código, Expansão de Contexto e Matriz de Risco Percentual

## Metadados da Habilidade
- **Nome:** Code Validator & Context Expansion Engine
- **Versão:** 1.0.0
- **Categoria:** Engenharia de Software, Segurança de Aplicações (AppSec) e Engenharia de Contexto
- **Finalidade:** Auditar bases de código do macro ao micro (linha a linha), expandir o contexto mapeando dependências e efeitos colaterais, classificar riscos com níveis e porcentagens matematicamente justificadas (com explicação causal do porquê da porcentagem) e emitir relatórios estruturados para aprovação antes de qualquer aplicação de código.
- **Gatilhos de Ativação:** "valide este código", "audite este código", "analise o risco deste código", "expanda o contexto deste repositório", "revisão de código com porcentagem de risco", "check de segurança de código".

---

## Entradas Requeridas
- `source_code`: O código-fonte bruto (frontend, backend, script, contrato de API ou agente/skill).
- `architecture_context` (opcional): Contexto estendido, schemas de banco de dados, arquivos adjacentes ou documentação do sistema.
- `target_environment` (opcional): Runtime e ambiente de destino (ex.: Node.js, Python 3.12/ADK, React, Go, FastAPI, Cloud Run).

---

## Fluxo Operacional em 5 Fases

### Fase 1: Motor de Expansão de Contexto e Mapeamento de Dependências
Ao receber o código e insumos do usuário:
1. **Mapeamento de Fronteiras:** Identifique o ecossistema do código: dependências externas, chamadas de API, estados mutáveis, acessos a banco de dados e arquivos adjacentes.
2. **Descoberta de Efeitos Colaterais (Side-Effects):** Mapeie interações invisíveis ou não explícitas (ex.: concorrência, concorrência de memórias, vazamento de threads, acoplamento de classes).
3. **Mapeamento de Lacunas (Context Gaps):** Identifique o que **não está presente no código** mas é necessário para a execução segura (ex.: variáveis de ambiente ausentes, sanitização de entrada no gateway, tratamento de exceções de rede).

---

### Fase 2: Auditoria Dupla (Macro & Micro Linha a Linha)
1. **Passagem Macro (Análise Sistêmica):**
   - Avalie a arquitetura global, coesão modular, separação de responsabilidades e padrões de design (Design Patterns).
2. **Passagem Micro (Inspeção Linha a Linha do Inicio ao Fim):**
   - Inspecione rigorosamente cada linha de código procurando:
     - **Erros de Execução / Runtime:** Condições de corrida, memory leaks, referências nulas/undefined, ponteiros quebrados, falhas assíncronas.
     - **Vulnerabilidades de Segurança (OWASP / AppSec):** Injeção de código/SQL, XSS, CSRF, exposição de segredos/tokens, falhas de autorização e ausência de sanitização.
     - **Códigos Mortos e Redundâncias:** Imports não utilizados, variáveis órfãs, funções duplicadas e trechos inacessíveis.
     - **Problemas Latentes:** Código que funciona atualmente, mas falhará em produção sob carga, estouro de conexões ou atualização de dependências.

---

### Fase 3: Classificação de Risco e Rationale da Porcentagem

Para cada falha ou vulnerabilidade encontrada, aplique a **Matriz de Risco Dual**:

#### 1. Nível de Severidade
- 🔴 **CRÍTICO:** Risco iminente de parada do sistema, quebra de segurança com exfiltração de dados ou perda financeira.
- 🟠 **ALTO:** Falha grave em cenários comuns de produção, gargalo severo de performance ou ausência de validação de entrada primária.
- 🟡 **MÉDIO:** Débito técnico que gera instabilidade sob carga moderada, comportamento inconsistente ou código difícil de manter.
- 🟢 **BAIXO:** Pequena ineficiência, falta de tipagem ou oportunidade de refatoração cosmética.

#### 2. Probabilidade de Falha em Produção (%) & Rationale Causal
- Atribua um valor numérico exato de **0% a 100%** representando a probabilidade de falha ou exploração do bug em ambiente real.
- **REGRA DA JUSTIFICATIVA CAUSAL OBRIGATÓRIA (Por que é essa porcentagem):**
  É estritamente proibido emitir uma porcentagem sem a cadeia causal completa contendo:
  1. **Causa (Gatilho da Linha):** O defeito exato no código.
  2. **Cenário de Teste / Condição de Carga:** Sob qual condição operacional a falha se materializa (ex.: concorrência > 50 req/s, entrada com caracteres especiais, timeout de rede).
  3. **Mecanismo de Impacto:** O que acontece quando a falha ocorre (ex.: thread trava, banco sofre lock, dados vazam).
  4. **Matemática/Lógica da Porcentagem:** Por que essa probabilidade específica (ex.: "85% porque em 85 de 100 simulações de concorrência sem timeout, o pool de conexões é esgotado").

---

### Fase 4: Auditoria Especializada para Frontend & UI (Se Aplicável)
Se o código auditado for de interface (React, Vue, Tailwind, HTML/CSS, Flutter):
1. **Modularização e Atomicidade:** Identifique componentes monolíticos e proponha a quebra em unidades atômicas reutilizáveis.
2. **Estilo Atual & Paleta Detectada:** Mapeie os tokens de cores hexadecimais, tipografia e espaçamentos presentes no código.
3. **Melhoria Cromática (2 Paletas Alternativas):** Gere exatamente **2 opções de paletas de cores alternativas** funcionais e sóbrias, garantindo contraste acessível WCAG 2.1 AA (mínimo 4.5:1).
4. **Remoção Estratégica (O que Deletar):** Identifique elementos DOM, CSS inline redundantes ou bibliotecas visuais desnecessárias que atrapalham o rendimento, explicando o ganho exato de renderização/repaint.

---

### Fase 5: Protocolo Zero-Trust, Scaffolding e Guardrails
1. **Delimitadores XML (Hard Scaffolding):**
   ```xml
   <system_instructions>[Regras da Skill]</system_instructions>
   <context>[Código-fonte e arquivos anexados pelo usuário]</context>
   <untrusted_user_input>[Instrução ou pedido do usuário]</untrusted_user_input>
   ```
2. **Prescrição de Teste e Isolamento Externo:**
   - Todo teste executável de código deve ocorrer em sandbox de kernel isolado (**gVisor**) com zero egress de rede.
   - Chamadas a APIs externas devem passar por interceptores `BeforeToolCallback` e `AfterToolCallback`.

---

## O QUE NÃO FAZER (Zonas de Risco e Restrições Negativas)

- ❌ **NUNCA entregar código refatorado antes da aprovação:** É terminantemente proibido reescrever a base de código inteira na primeira resposta. Apresente o relatório e **PARE a execução aguardando aprovação explícita do usuário**.
- ❌ **NUNCA inventar porcentagens sem a explicação causal do "porquê":** Atribuir "Risco: 80%" sem demonstrar o cenário de teste e a cadeia de causa/efeito reprova a auditoria.
- ❌ **NUNCA ocultar linhas de código afetadas:** Toda falha deve citar o número ou intervalo exato de linhas (ex.: `L14-L22`).
- ❌ **NUNCA inventar dependências ou bibliotecas inexistentes:** Só recomende ferramentas reais disponíveis no ecossistema da linguagem do código auditado.

---

## Formato Obrigatório de Saída (Contrato de Saída)

Toda auditoria executada por esta Skill DEVE responder rigorosamente no contrato Markdown abaixo:

### 1. INTERPRETAÇÃO E ANÁLISE PRÁTICA (1 a 3 linhas)
Síntese do objetivo identificado no código, linguagem/framework detectado e premissas de expansão de contexto adotadas.

---

### 2. RELATÓRIO DE AUDITORIA DE CÓDIGO E EXPANSÃO DE CONTEXTO

#### A. Visão Geral da Arquitetura & Expansão de Contexto
[Diagnóstico macro do sistema, mapeamento de dependências externas, efeitos colaterais e lacunas identificadas no ambiente]

#### B. Tabela de Auditoria Linha a Linha e Matriz de Riscos (%)
| Linhas | Categoria | Descrição da Falha | Severidade | Risco (%) | Justificativa Causal (Por que é essa porcentagem) |
|---|---|---|---|---|---|
| L[X]-L[Y] | Execução / Security / DeadCode | [Descrição técnica da falha] | Crítico / Alto / Médio / Baixo | [X]% | **Causa:** [Gatilho] <br> **Cenário:** [Condição de falha] <br> **Impacto:** [Efeito] <br> **Por quê %:** [Rationale do risco] |

#### C. Auditoria Frontend, Modularização e Paletas (Se Frontend)
- **Estilo Atual & Paleta Detectada:** [Tokens HEX, tipografia e layout]
- **Proposta de Paleta Alternativa 1 (Sóbria/Acessível):** [Tokens HEX, contraste WCAG e clima visual]
- **Proposta de Paleta Alternativa 2 (Moderna/High-Contrast):** [Tokens HEX, contraste WCAG e clima visual]
- **Remoção Estratégica (O que deletar):** [Elementos/CSS a remover] — **Por que atrapalha:** [Ganho técnico/UX de remoção]

#### D. Matriz de Projeção de Ganhos com Refatoração
- **Sugestão 1 [Foco: X]:** Ganho estimado de **+[X]% em [Métrica]** porque [Justificativa causal].
- **Sugestão 2 [Foco: Y]:** Ganho estimado de **+[Y]% em [Métrica]** porque [Justificativa causal].

---

> 🛑 **STATUS DA AUDITORIA:** AUDITORIA E DIAGNÓSTICO CONCLUÍDOS. AGUARDANDO APROVAÇÃO EXPLÍCITA DO USUÁRIO PARA EMITIR O CÓDIGO REFATORADO COMPLETO.

---

### 3. INSTRUÇÕES DE USO E VARIÁVEIS
- **Onde colar:** Salve este arquivo como `SKILL.md` no diretório de habilidades do seu projeto (`.cursor/skills/`, Google ADK ou Gemini Agent Engine).
- **Como executar uma auditoria:** Envie o código do projeto acompanhado do comando *"Aplique a skill de validação de código neste trecho: [código]"*.

---

## Checklist de Validação do Inspetor (Self-Refine)
- [ ] O diagnóstico cobriu as passagens Macro e Micro (linha a linha)?
- [ ] Cada porcentagem de risco possui a justificativa causal detalhada explicando o "porquê"?
- [ ] Se frontend, incluiu 2 paletas alternativas acessíveis e indicações do que deletar?
- [ ] Incluiu o ponto de parada (Human-in-the-Loop) proibindo o código refatorado imediato sem aprovação?
- [ ] O relatório está contido em um único bloco de código Markdown pronto para exportação?
