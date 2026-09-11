# Diretrizes do Plugin de Governança Antigravity

1. **Idioma Oficial**: Sempre responder em Português BR.
2. **Zero-Trust & HITL**: Comandos potencialmente destrutivos (deleção recursiva, git force, drop tables) exigem validação prévia.
3. **Padrão Skill-First**: Novos procedimentos e automações devem ser empacotados como Agent Skills (`SKILL.md`), respeitando a depreciação de workflows legados.
4. **Isolamento de Domínio**: Alterações devem respeitar as fronteiras do projeto e convenções de código estabelecidas.
