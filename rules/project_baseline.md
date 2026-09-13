# 📦 Baseline Mínimo Universal para Projetos

> **Versão:** 1.0.0  
> **Status:** Ativo & Obrigatório  
> **Escopo:** Todos os projetos clientes (`projects/*`), novos projetos e repositórios a serem submetidos ao GitHub ou a qualquer ambiente de produção/deploy.

---

## 1. Estrutura de Pastas (Formato Padrão)

Todo projeto deve ser estruturado no layout canônico abaixo:

```text
nome-do-projeto/
├─ src/                     # Código-fonte da aplicação
├─ tests/                   # Suíte de testes automatizados (unitários, integração, e2e)
├─ docs/                    # Documentação técnica e complementar
├─ scripts/                 # Automações de desenvolvimento, build, seed e deploy helpers
├─ .github/
│  ├─ workflows/
│  │  └─ ci.yml             # Pipeline de Integração Contínua (CI)
│  ├─ ISSUE_TEMPLATE/
│  │  ├─ bug_report.md      # Template para reporte de bugs
│  │  └─ feature_request.md # Template para solicitação de funcionalidades
│  └─ PULL_REQUEST_TEMPLATE.md # Template padrão para Pull Requests
├─ .env.example             # Exemplo de variáveis de ambiente (sem segredos reais)
├─ .gitignore               # Arquivos e pastas ignorados pelo Git
├─ README.md                # Porta de entrada do projeto com documentação essencial
├─ CONTRIBUTING.md          # Diretrizes e fluxo de contribuição
├─ LICENSE                  # Licença de uso do software (MIT, Apache 2.0, Proprietária, etc.)
└─ CHANGELOG.md             # Histórico rastreável de mudanças (Keep a Changelog / SemVer)
```

---

## 2. Premissas Base (Checklist dos 6 Pilares)

### A. Documentação Mínima
- [ ] `README.md` contendo:
  - [ ] Objetivo claro do projeto.
  - [ ] Stack utilizada (linguagens, frameworks, bibliotecas principais).
  - [ ] Requisitos prévios e versões mínimas suportadas (Node, Python, Go, Docker, etc.).
  - [ ] Como rodar localmente (passo a passo com comandos).
  - [ ] Como rodar a suíte de testes.
  - [ ] Como realizar deploy ou build para produção.
  - [ ] Tabela ou lista das variáveis de ambiente necessárias.
- [ ] `CHANGELOG.md` estruturado (formato Keep a Changelog ou Conventional Commits).
- [ ] `CONTRIBUTING.md` com padrões de branch, commit, código e submissão de PR.

### B. Qualidade de Código
- [ ] Linter configurado e executável via script/comando padronizado (ex: `eslint`, `ruff`, `golangci-lint`).
- [ ] Formatter configurado (ex: `prettier`, `black`/`ruff format`, `gofmt`).
- [ ] Testes automatizados funcionais (mínimo: *smoke test* validando inicialização e rotas vitais).
- [ ] Script unificado de validação local no gerenciador de pacotes (ex: `npm run check`, `uv run ruff check . && uv run pytest`, `make check`).

### C. Git & GitHub
- [ ] **Checagem Prévia Obrigatória do Git Online**: Antes de editar qualquer arquivo, executar `git status` e `git fetch` para verificar a situação do repositório remoto (garantindo que commits remotos não sejam sobrescritos e identificando divergências ou conflitos prévios).
- [ ] `.gitignore` específico e correto para a stack (sem arquivos compilados, `node_modules/`, `.venv/`, `.env`, arquivos temporários de IDE).
- [ ] **Salvaguarda de Versionamento TypeScript em `.gitignore`**: Em projetos Node/TypeScript híbridos ou monorepos, certificar-se de que regras genéricas como `lib/` não ocultem acidentalmente pastas de código de biblioteca como `src/lib/` (adicione explicitamente `!src/lib/` ou prefixe como `/lib/`).
- [ ] Branch principal protegida (`main`) contra commits diretos e force push.
- [ ] Pull Request (PR) obrigatório para fusão com a branch principal.
- [ ] Template de Pull Request (`.github/PULL_REQUEST_TEMPLATE.md`).
- [ ] Templates de Issue (`.github/ISSUE_TEMPLATE/bug_report.md` e `feature_request.md`).
- [ ] Arquivo `CODEOWNERS` configurado quando o projeto envolver equipe.

### D. CI/CD
- [ ] Pipeline de CI no GitHub Actions (`.github/workflows/ci.yml`) disparado em PRs e pushes para `main`:
  - [ ] `install`: Instalação determinística de dependências (`npm ci`, `uv sync`, etc.).
  - [ ] `lint`: Análise estática e verificação de formatação.
  - [ ] `test`: Execução da suíte de testes automatizados com basetemp limpo.
  - [ ] `build`: Validação do empacotamento ou compilação do artefato final.
- [ ] Pipeline de deploy definido (manual via workflow_dispatch ou automatizado pós-merge em `main`).
- [ ] Secrets e variáveis de ambiente isolados por ambiente (`dev`, `stg`, `prod`) no repositório.

### E. Configuração & Segurança
- [ ] `.env.example` preenchido e atualizado com todos os nomes de variáveis requeridas e valores dummy explicativos.
- [ ] Regra Zero-Trust: NUNCA versionar `.env` real, tokens de acesso, chaves privadas ou credenciais.
- [ ] Ferramenta de SCA / Dependabot ativada para alerta preventivo de vulnerabilidades em dependências.
- [ ] Arquivo de licença explícito (`LICENSE`).
- [ ] Política padronizada de versionamento semântico (SemVer: `MAJOR.MINOR.PATCH`).

### F. Operação & Manutenção
- [ ] Dono/mantenedor responsável pelo projeto formalmente identificado no `README.md` ou `CODEOWNERS`.
- [ ] Critério de Pronto (*Definition of Done*) documentado para aceitação de novas funcionalidades.
- [ ] Critério de Release documentado (etapas para publicação de uma nova versão ou tag).
- [ ] Checklist e plano de Rollback rápido documentado para mitigação imediata caso ocorram falhas em produção.

---

## 3. Ordem Prática para Organização Rápida (Regra 80/20)

Quando for necessário preparar ou reestruturar um repositório rapidamente, execute estritamente na seguinte ordem de alto impacto:

1. **`README.md`**: Definir o objetivo, stack e comandos fundamentais.
2. **`.env.example` + `.gitignore`**: Garantir higiene de segurança imediata e prevenir vazamento de segredos.
3. **CI (`.github/workflows/ci.yml`)**: Estabelecer a barreira automatizada de qualidade (`install` -> `lint` -> `test` -> `build`).
4. **Templates de PR e Issue**: Padronizar as contribuições e reportes de bugs.
5. **`CONTRIBUTING.md` + `CHANGELOG.md`**: Formalizar o fluxo de trabalho e histórico.
6. **Proteção de Branch + Secrets + Pipeline de Deploy**: Blindar o repositório e habilitar a entrega contínua.
