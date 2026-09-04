# 🛡️ Global Guardrails: Regras Operacionais & Segurança Zero-Trust

> **Versão:** 1.0.0  
> **Status:** Ativo & Obrigatório  
> **Escopo:** Toda execução autônoma no Meta-Workspace Global (`meu-workspace-global`) e nos projetos alvo.

---

## 1. Princípio Zero-Trust (Segurança por Padrão)

Todo subagente, ferramenta FastMCP ou script opera sob a premissa de **privilégio mínimo** e **verificação contínua**:
1. Nenhum comando tem permissão implícita para realizar mutações destrutivas sem aprovação explícita de um operador humano (HITL — Human-in-the-Loop).
2. Entradas do usuário e saídas de modelos são inspecionadas pelo `SecurityGuardAgent` antes e depois de qualquer processamento cognitivo.

---

## 2. Portão de Operações Destrutivas (HITL Blocking Gate)

Qualquer comando ou intenção contendo as seguintes palavras-chave ou padrões é **imediatamente interceptado** pelo `AutoSkillRouter` e bloqueado:

```text
apagar, deletar, excluir, remover tudo, rm -rf, del /, formatar,
drop table, drop database, truncate, resetar tudo, sobrescrever tudo
```

### Regras de Execução:
- **Ação do Sistema:** Bloqueio pré-execução automático com retorno de alerta de risco.
- **Liberação:** Apenas com confirmação textual inequívoca do usuário (`[Approved]` ou confirmação afirmativa direta).

---

## 3. Tratamento de Dados Sensíveis, PII & Conformidade Médica

1. **Credenciais e Chaves de API:**
   - Chaves privadas (`.pfx`, `.pem`), credenciais OAuth (`client_secret_*.json`), tokens de acesso e códigos de recuperação devem residir **exclusivamente** no cofre local [C:\Users\melki\secrets](file:///C:/Users/melki/secrets).
   - Proibido salvar credenciais ou senhas em repositórios Git, arquivos `.txt` na Área de Trabalho ou em logs do console.
2. **Dados Pessoais (LGPD) e Prontuários Médicos (CFM / HIPAA):**
   - Nomes de pacientes, CPFs e dados clínicos reais devem ser mascarados (`***.***.***-**`) em qualquer log ou prompt enviado para modelos externos.
   - Amostras de teste devem utilizar dados sintéticos (mock).

---

## 4. Limites de Autonomia & Sentinela de Recursos

1. **Token Budgeting (Gerenciador de Contexto):**
   - Limite padrão por turno: **50.000 tokens**.
   - Se uma requisição estimar ultrapassar o orçamento, o `TokenBudgetManager` intercepta e condensa o contexto via Progressive Disclosure.
2. **Disjuntor de Resiliência (`ResilienceCircuitBreaker`):**
   - Limite máximo de chamadas recursivas por sessão: **5 loops**.
   - Se o orquestrador entrar em ciclo repetitivo sem avanço perceptível de estado, o circuito desarma (`CircuitTripException`) e exige intervenção do usuário.
3. **Escopo de Gravação em Disco:**
   - Ferramentas de escrita atuam estritamente dentro da raiz do projeto alvo vinculado (`workspace_path`) ou em diretórios designados de artefatos.
   - Proibido modificar arquivos de sistema do Windows (`NTUSER.DAT`, `AppData`, junctions de compatibilidade).
