# Domain Documentation

## Layout

This repository uses a single-context layout.

- Context document: `CONTEXT.md`
- Architecture decisions: `docs/adr/`

There is no `CONTEXT-MAP.md` because this repository is not organized as a monorepo.

## Consumer rules

- Read `CONTEXT.md` before making architecture or domain-model decisions.
- Read relevant ADRs from `docs/adr/` when changing an established architectural decision.
- Prefer the repository's existing terminology and constraints.
- Update the relevant ADR or context documentation when a structural decision changes.
- Do not invent per-package context files unless the repository becomes a genuine multi-context monorepo.