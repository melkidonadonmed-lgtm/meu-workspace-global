# Como Contribuir

Agradecemos o interesse em contribuir com este projeto! Para manter a qualidade, estabilidade e segurança do código, siga as diretrizes abaixo.

---

## 1. Fluxo de Trabalho Git (Branch & PR)

1. Faça um Fork ou clone o repositório principal.
2. Crie uma branch nomeada semanticamente a partir de `main`:
   - `feature/nome-da-funcionalidade`
   - `fix/descricao-do-bug`
   - `refactor/modulo-alvo`
   - `docs/atualizacao-readme`
3. Mantenha os commits claros seguindo o padrão de **Conventional Commits** (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
4. Abra um Pull Request contra a branch `main`, preenchendo detalhadamente o template de PR.

---

## 2. Qualidade e Validação Local

Antes de abrir o Pull Request, execute a validação local completa:

```bash
# 1. Executar linter e formatter
npm run lint

# 2. Executar suíte de testes automatizados
npm test

# 3. Validar build / empacotamento
npm run build
```

Nenhum PR será aprovado com falhas no pipeline de CI.

---

## 3. Segurança e Zero-Trust

- **NUNCA** commite arquivos `.env`, tokens de acesso, chaves privadas ou dados sensíveis/PII.
- Certifique-se de que qualquer nova variável de ambiente necessária seja adicionada com valor ilustrativo no `.env.example`.
