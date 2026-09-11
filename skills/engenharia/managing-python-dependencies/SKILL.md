---
name: managing-python-dependencies
description: Gerencia ambientes virtuais e dependências Python no ecossistema Brain, detectando uv, poetry, pipenv, conda ou venv de forma segura e multiplataforma (Windows/POSIX).
triggers:
  - "uv"
  - "poetry"
  - "pip"
  - "venv"
  - "dependencias python"
  - "gerenciar dependencias"
  - "pyproject.toml"
---

# Regras de Gerenciamento de Dependências Python

> [!CAUTION]
> **ANTES de qualquer instalação `pip`**: Você DEVE primeiro detectar o gerenciador de dependências existente no projeto e utilizá-lo corretamente. NUNCA execute `pip install` globalmente.

---

## 1. Detecção do Gerenciador de Dependências

Antes de instalar QUALQUER pacote Python, verifique o diretório do projeto na seguinte ordem de prioridade:

1. **Sinal:** `uv.lock` ou `pyproject.toml` contendo `[tool.uv]`
   - **Ferramenta:** **uv**
   - **Comandos:** `uv add <pacote>` | `uv sync`
2. **Sinal:** `pyproject.toml` contendo `[tool.poetry]`
   - **Ferramenta:** **Poetry**
   - **Comandos:** `poetry add <pacote>` | `poetry install`
3. **Sinal:** `Pipfile`
   - **Ferramenta:** **Pipenv**
   - **Comandos:** `pipenv install <pacote>` | `pipenv install`
4. **Sinal:** `environment.yml`
   - **Ferramenta:** **Conda**
   - **Comandos:** `conda install <pacote>` | `conda env create -f environment.yml`
5. **Sinal:** `requirements.txt` ou nenhum arquivo acima
   - **Ferramenta:** **venv + pip** (Padrão)

---

## 2. Fluxo Padrão Multiplataforma (venv + pip)

Quando nenhum gerenciador específico for detectado, utilize o fluxo **venv + pip + requirements.txt**:

### No Windows (PowerShell / CMD):
```powershell
# Criar ambiente virtual
python -m venv .venv

# Instalar pacotes via venv local
.\.venv\Scripts\pip.exe install <pacote>

# Congelar dependências
.\.venv\Scripts\pip.exe freeze > requirements.txt
```

### No Linux / macOS (POSIX):
```bash
# Criar ambiente virtual
python3 -m venv .venv

# Instalar pacotes via venv local
./.venv/bin/pip install <pacote>

# Congelar dependências
./.venv/bin/pip freeze > requirements.txt
```

---

## O que NÃO Fazer

- **NÃO execute `pip install` no ambiente Python global do sistema**.
- **NÃO misture gerenciadores de dependências** (ex: rodar `pip install` direto em projetos gerenciados por `poetry` ou `uv`).
- **NÃO utilize caminhos de binares rígidos ou exclusivos de um único SO** sem considerar a compatibilidade entre Windows (`.venv\Scripts\python`) e Linux/macOS (`.venv/bin/python`).
- **NÃO esqueça de congelar/atualizar o arquivo `requirements.txt` ou o lockfile** após alterar dependências.
