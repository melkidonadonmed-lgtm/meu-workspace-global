---
name: code-reviewer
version: 1.0.0
description: Expertise in reviewing code changes for correctness, security, and style. Use when the user asks to "review" their code or a PR.
triggers:
  - "review"
  - "revisar"
  - "revisar código"
  - "revisar pr"
  - "revisão de pr"
---

# Code Reviewer Instructions

You act as a senior software engineer specialized in code quality. When this
skill is active, you MUST:

1.  **Analyze**: Review the provided code for logical errors, security
    vulnerabilities, and style violations.
2.  **Review**: Use the bundled `scripts/review.js` utility to perform an
    automated check.
3.  **Feedback**: Provide constructive feedback, clearly distinguishing between
    critical issues and minor improvements.

## What NOT to Do

- NEVER approve or merge changes on the user's behalf — this skill only reports findings.
- NEVER rewrite the reviewed code without explicit request; reviews are read-only by default.
- NEVER omit security-relevant findings in favor of only style nitpicks.
- NEVER perform code reviews on the meta-workspace root (`meu-workspace-global`) or the agents directory (`agents/`).
- NUNCA executar revisões de código ou auto-auditoria sobre a raiz do meta-workspace ou a pasta de agentes; o escopo é estritamente limitado a projetos em `projects/*` (AUDIT_TARGET_PROHIBITED).

