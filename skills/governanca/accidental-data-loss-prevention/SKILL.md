---
name: accidental-data-loss-prevention
description: Protocolo de segurança do ecossistema Brain para prevenção contra perda acidental de dados, exigindo validação e confirmação explícita antes de ações destrutivas.
triggers:
  - "apagar"
  - "deletar"
  - "excluir"
  - "rm -rf"
  - "drop table"
  - "perda de dados"
  - "operacao destrutiva"
---

# Prevenção contra Perda Acidental de Dados

> [!CAUTION]
> **PARE E VERIFIQUE**: Antes de executar qualquer comando ou ferramenta que resulte na exclusão irreversível de dados, arquivos críticos ou infraestrutura, você DEVE obter consentimento explícito do usuário.

---

## Operações Críticas que Exigem Confirmação

1. **Operações em Banco de Dados (SQL)**:
   - `DROP TABLE`, `DROP VIEW`, `DROP SCHEMA`, `DROP DATABASE`.
   - `TRUNCATE TABLE`.
   - `DELETE` em massa (sem cláusula `WHERE` ou com `WHERE 1=1`).

2. **Gerenciamento de Arquivos e Repositórios**:
   - Remoção recursiva de diretórios com código-fonte (`rmdir /s /q`, `rm -rf`).
   - Comandos Git destrutivos (`git reset --hard`, `git clean -fd`, `git push --force`).

3. **Recursos de Nuvem e Infraestrutura**:
   - Deleção de buckets, tabelas Spanner/BigQuery ou projetos na nuvem (`gcloud storage rm`, `bq rm`).

---

## Procedimento Obrigatório

1. **Pausar Execução**: Não execute o comando destrutivo diretamente.
2. **Explicar o Impacto**: Apresente claramente ao usuário o que será deletado e o motivo da necessidade.
3. **Aguardar Confirmação**: Somente prossiga após receber resposta afirmativa do usuário.

---

## O que NÃO Fazer

- **NÃO execute comandos destrutivos sem a confirmação explícita prévia do usuário**.
- **NÃO tente burlar confirmações de segurança usando flags como `--force` ou `-y`** em operações de deleção crítica sem autorização.
- **NÃO assuma que arquivos ou tabelas não possuem valor sem antes inspecionar seu conteúdo**.
