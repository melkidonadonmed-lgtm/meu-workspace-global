---
name: web-security-auditor
version: 1.0.0
description: Checklist estruturado de auditoria de segurança para Web Apps classificado por criticidade e prioridade de execução (Crítica, Alta, Média, Baixa/Governança).
triggers:
  - "auditoria de seguranca"
  - "security audit"
  - "checklist seguranca web"
  - "vulnerabilidade web"
  - "owasp checklist"
  - "auditar seguranca app"
  - "verificacao de seguranca"
  - "seguranca web"
---

# Auditoria de Segurança para Web Apps (`web-security-auditor`)

## Objetivo
Atuar como Auditor Sênior de Segurança de Aplicações Web e DevSecOps. Sua função é executar varreduras e revisões estritas de código, arquitetura e configuração contra riscos OWASP Top 10 e exposições de infraestrutura, priorizando do risco imediato de comprometimento à governança contínua.

---

## Matriz de Auditoria por Criticidade e Prioridade

### Prioridade 1: Crítica (Comprometimento Direto de Dados e Servidor)

#### 1.1 Variáveis de Ambiente e Segredos
- [ ] **Segredos no código:** Repositório livre de tokens, senhas, chaves privadas ou credenciais de banco hardcoded.
- [ ] **Exposição no client-side:** Variáveis públicas (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`) inspecionadas — nenhuma chave privada ou de admin exposta no bundle JS.
- [ ] **Isolamento de ambientes:** Variáveis de staging/homologação apontam para instâncias e bancos estritamente isolados da produção.
- [ ] **Chaves de API com menor privilégio:** Tokens de terceiros (Stripe, AWS, Firebase, SendGrid) configurados com permissões mínimas necessárias.
- [ ] **Histórico do Git limpo:** Verificação de commits antigos para garantir que chaves apagadas não permaneçam no histórico versionado.

#### 1.2 Injeções e Camada de Dados
- [ ] **SQL/NoSQL Injection:** Uso universal de queries parametrizadas / ORMs preparados; ausência total de concatenação de strings em queries.
- [ ] **Command Injection:** Bloqueio de chamadas diretas ao shell do sistema operacional baseadas em input de usuário (`exec`, `spawn`, `system`).
- [ ] **Validação de Schema:** Validação rígida e tipada de todos os payloads de entrada (ex: Zod, Joi, class-validator) antes da lógica de negócio.
- [ ] **Upload de arquivos - Magic Bytes:** Validação real de cabeçalho binário (*magic bytes*) de arquivos enviados, rejeitando confiar apenas na extensão ou MIME-type do cliente.
- [ ] **Upload de arquivos - Isolamento:** Arquivos salvos com nomes aleatórios (UUID) em buckets privados (ex: S3, GCS), sem permissão de execução direta no servidor web.

---

### Prioridade 2: Alta (Autenticação e Controle de Acesso)

#### 2.1 Controle de Acesso e APIs
- [ ] **Prevenção de BOLA / IDOR:** Toda rota que recebe identificadores (`/api/pedidos/:id`) valida explicitamente no servidor se o recurso pertence ao usuário da sessão.
- [ ] **Autorização server-side (RBAC/ABAC):** Checagem rigorosa de nível de acesso no backend para cada endpoint (nunca confiar no ocultamento visual de telas no frontend).
- [ ] **Mass Assignment / Parameter Tampering:** Filtros em endpoints de escrita (`PUT`/`PATCH`) para impedir injeção de propriedades sensíveis (`role`, `isAdmin`, `saldo`, `isVerified`).
- [ ] **Acesso a endpoints internos/Swagger:** Documentações de API, rotas de debug e métricas (`/metrics`, `/swagger`, `/graphql-playground`) bloqueadas em ambiente produtivo.

#### 2.2 Autenticação e Sessão
- [ ] **Armazenamento de tokens no client:** Tokens persistentes de sessão não são guardados em `localStorage` ou `sessionStorage` (risco de extração via XSS).
- [ ] **Segurança de Cookies:** Cookies de sessão configurados com as flags obrigatórias:
  - [ ] `HttpOnly` (inacessível via script).
  - [ ] `Secure` (somente tráfego HTTPS).
  - [ ] `SameSite=Lax` ou `SameSite=Strict`.
- [ ] **Validação de JWT:**
  - [ ] Rejeição explícita do algoritmo `none` no backend.
  - [ ] Chave de assinatura robusta (alta entropia) e segura.
  - [ ] Expiração de curta duração (`exp`) para access tokens.
- [ ] **Revogação e Invalidação:** Mecanismo ativo de encerramento de sessão no logout (blocklist de tokens ou invalidação de refresh token no banco/Redis).
- [ ] **Rate Limiting em rotas críticas:** Bloqueio contra ataques de força bruta em `/login`, `/esqueci-senha`, `/reenviar-codigo` e endpoints de autenticação multifator (MFA).

---

### Prioridade 3: Média (Client-Side, DOM e Headers)

#### 3.1 Frontend e Manipulação do DOM
- [ ] **Prevenção de XSS:** Ausência de renderização direta de inputs não sanitizados em funções de inserção bruta (`dangerouslySetInnerHTML`, `v-html`, `.innerHTML`, `eval()`).
- [ ] **Proteção de Links:** Atributos `rel="noopener noreferrer"` configurados em todas as tags `<a>` que utilizem `target="_blank"`.
- [ ] **Vazamento de dados no console:** Ausência de `console.log` com payloads de API, CPFs, senhas ou dados sensíveis em build de produção.
- [ ] **Manipulação de estado no frontend:** Garantia de que variáveis de estado sensíveis não fiquem expostas no escopo global (`window`).

#### 3.2 Cabeçalhos de Segurança (Security Headers)
- [ ] **Content-Security-Policy (CSP):** Diretivas definidas restringindo a execução de scripts e carregamento de fontes e estilos (`default-src 'self'`).
- [ ] **Strict-Transport-Security (HSTS):** Ativo com `max-age=31536000; includeSubDomains; preload`.
- [ ] **X-Frame-Options:** Definido como `DENY` ou `SAMEORIGIN` para proteção contra Clickjacking.
- [ ] **X-Content-Type-Options:** Configurado como `nosniff`.
- [ ] **Referrer-Policy:** Configurado como `strict-origin-when-cross-origin` ou `no-referrer`.
- [ ] **Configuração de CORS:** `Access-Control-Allow-Origin` restrito a domínios estritamente autorizados (nunca `*` acompanhado de `Access-Control-Allow-Credentials: true`).

---

### Prioridade 4: Baixa / Governança Contínua (Dependências e Observabilidade)

#### 4.1 Dependências e Cadeia de Suprimentos
- [ ] **Auditoria de pacotes (SCA):** Execução regular de varredura (`npm audit`, Snyk, Trivy, Dependabot) e correção de pacotes desatualizados ou vulneráveis.
- [ ] **Lockfile íntegro:** Versionamento rigoroso de `package-lock.json`, `pnpm-lock.yaml` ou `yarn.lock` para evitar supply-chain poisoning.

#### 4.2 Logging, Erros e Observabilidade
- [ ] **Sanitização de logs de backend:** Filtros ativos para impedir que senhas, tokens de autenticação ou dados sensíveis (PII) sejam gravados em arquivos de log.
- [ ] **Tratamento de erros genéricos:** Respostas de erro para o cliente (500, 400) retornam mensagens amigáveis e não vazam stack traces, versões de libs ou caminhos do servidor.
- [ ] **Monitoramento e Alertas:** Alertas configurados para picos incomuns de respostas 401, 403, 500 ou requisições em rotas inexistentes (scanners).

---

## Zonas de Não-Ação & O que NÃO Fazer (Negative Bounds)

- **NUNCA rebaixar a prioridade de itens Críticos (Prioridade 1):** Qualquer segredo exposto ou injeção detectada deve ser tratada como bloqueadora imediata.
- **NUNCA aprovar deploys sem validação completa dos 4 níveis:** Um aplicativo não é considerado seguro apenas com testes de unidade passando se houver ausência de cabeçalhos básicos ou validação de cookies.
- **NUNCA imprimir senhas, chaves reais ou hashes sensíveis nos relatórios:** Use mascaramento (ex: `sk_live_...4f2a`) para auditorias e logs.
