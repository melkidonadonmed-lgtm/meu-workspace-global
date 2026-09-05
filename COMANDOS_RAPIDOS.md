# 🚀 Guia Rápido — Meus Projetos & Claude Code

> Atualizado em 2026-09-05. Cópia irmã de `C:\Users\melki\OneDrive\Área de Trabalho\COMANDOS_PROJETOS.txt` — mantenha os dois em sincronia.

---

### 🔹 0. Pedir pro Claude Code fazer (sem comando, só fale)

Não existe mais `.\run.ps1` nem `ativa brain`. Pra auditar/revisar um projeto, é só pedir em português normal dentro do Claude Code:

- "audita o pcm"
- "dá uma olhada no canvas_ide antes de eu mandar pro cliente"
- "revisa a segurança do keepdocs"

Isso aciona a skill `audit-project`: acha o projeto certo, roda lint/build/teste que existirem, checa segurança e acessibilidade, e devolve os achados. Não funciona sobre o próprio `meu-workspace-global`.

---

### 🔹 1. Auditoria de qualidade do workspace

```powershell
make setup   # instala dependências
make test    # ou: uv run pytest -v
make lint    # ou: uv run ruff check .
uv run python skills/skill_healthcheck.py
```

---

### 🔹 2. PCM (PresCMed — Prescrição & Doses Pediátricas)

📁 `C:\Users\melki\Projetos\pcm` · 🔗 GitHub `melkidonadonmed-lgtm/PCM`

```powershell
cd "C:\Users\melki\Projetos\pcm" ; npm run dev
```
- 🌐 **Navegador:** [http://localhost:3000](http://localhost:3000)

---

### 🔹 3. Canvas IDE (Editor & Canvas Visual)

📁 `C:\Users\melki\Projetos\canvas_ide` · 🔗 GitHub `melkidonadonmed-lgtm/canvas_ide`

```powershell
cd "C:\Users\melki\Projetos\canvas_ide" ; npm run dev
```
- 🌐 **Navegador:** [http://localhost:5173](http://localhost:5173)
- 💡 **Modo Direto (Sem Terminal):** Basta dar duplo clique no arquivo `C:\Users\melki\Projetos\canvas_ide\canvas_preview.html`.

---

### 🔹 4. KeepDocs Workspace (Documentação)

📁 `C:\Users\melki\Projetos\keepdocs-workspace` · 🔗 GitHub `melkidonadonmed-lgtm/keepdocs-v2`

```powershell
cd "C:\Users\melki\Projetos\keepdocs-workspace" ; npm run dev
```
- 🌐 **Navegador:** [http://localhost:5173](http://localhost:5173)

---

### 🔹 5. WAOE

📁 `C:\Users\melki\Projetos\WAOE` · 🔗 GitHub `melkidonadonmed-lgtm/agents-md-95`

```powershell
cd "C:\Users\melki\Projetos\WAOE" ; npm run dev
```

---

### 🔹 6. PresCMed Remix (variante separada do PCM)

📁 `C:\Users\melki\Projetos\remix-prescmed-new` · 🔗 GitHub `melkidonadonmed-lgtm/remix-prescmed-new`

⚠️ App diferente do PCM acima, com histórico próprio — nome parecido, projeto separado.

```powershell
cd "C:\Users\melki\Projetos\remix-prescmed-new" ; npm run dev
```

---

### 🔹 7. Customer Issue Reviewer (Go ADK v2)

📁 `C:\Users\melki\meu-workspace-global\agents\specialized\customer_issue_reviewer_go`

```powershell
cd "C:\Users\melki\meu-workspace-global\agents\specialized\customer_issue_reviewer_go" ; go run main.go
```

---

### 🛑 Comandos Úteis do Dia a Dia

- **Parar um servidor rodando:** Ctrl + C
- **Erro de dependência Node:** `npm install` (dentro da pasta do projeto)
- **Erro de dependência Python:** `make setup` (dentro de `meu-workspace-global`)
- **Projetos ficam em** `C:\Users\melki\Projetos\` **— não mais em** `Brain\projetos\`
