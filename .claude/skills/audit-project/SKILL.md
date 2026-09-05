---
name: audit-project
description: Audits a real target project living under projects/* (pcm, remix-prescmed-new, canvas_ide, keepdocs-workspace, WAOE) or any other codebase path the user points at — checks it for security issues, broken lint/typecheck/build, dependency vulnerabilities, and accessibility gaps, then reports findings ranked by severity. Use this whenever the user asks to audit, review, check, or validate a project before shipping or handing it off, even if they just name the project casually ("dá uma olhada no pcm", "audita o canvas_ide", "revisa isso antes de eu mandar pro cliente") — don't wait for the word "audit" specifically. Do not use this on meu-workspace-global itself (the tooling repo) — it targets projects, not the workspace.
---

# Audit a project

You are auditing someone else's real, shipping application — not this tooling workspace. The point of this skill is to do the actual checking yourself, directly, rather than routing the request through another layer. If a step below doesn't apply to the project's stack, say so and move to the next one; don't skip a step silently.

## 1. Resolve the target

Match what the user said against the known projects (see `AGENTS.md` at the repo root for the current list and their GitHub repos). If they named a project casually ("o pcm", "aquele canvas"), resolve it to its `projects/<name>` symlink. If they gave a path instead, use that directly. If nothing matches and nothing was given, ask which project before doing anything else — don't guess between two similarly-named projects.

## 2. Read the project before running anything

Read `package.json` (or `pyproject.toml`, `go.mod` — whatever fits the stack) to see what scripts actually exist. Projects in this workspace are inconsistent: some have `lint`, some only have `tsc --noEmit` under that name, some have neither. Only run what's declared — inventing a `npm test` call on a project with no test script just produces a misleading failure.

## 3. Run what exists

For each of these, run it if the project defines it, and capture the real output:
- Typecheck / lint (`npm run lint`, `tsc --noEmit`, `ruff check`, etc.)
- Build (`npm run build`) — a broken build is always worth flagging even if nothing else is
- Tests, if any are defined

## 4. Spot-check for security issues

Read through the source for patterns that matter more in a shipping app than a prototype:
- Hardcoded API keys, tokens, or credentials (grep for `sk-`, `AIza`, `api_key`, `.env` values committed into source). Require a long alphanumeric run after the prefix, not just the prefix itself — `sk-[A-Za-z0-9]` alone matches CSS words like `mask-image` too.
- `dangerouslySetInnerHTML`, `eval(`, or unsanitized user input reaching the DOM or a query
- Sensitive data (PII, medical data for apps like PCM) persisted to `localStorage`/`IndexedDB` without a reason documented nearby
- Secrets or credentials files accidentally tracked in git (`.env` committed, not gitignored)

## 5. Spot-check accessibility, only for UI projects

For React/HTML frontends: missing `alt` on images, missing labels on form inputs and icon-only buttons, heading hierarchy skipping levels, obvious color-contrast issues in the design tokens. Skip this step entirely for non-UI projects (Go services, data pipelines) — don't force it.

## 6. Report

Use the `ReportFindings` tool if it's available in this session; otherwise write the findings out in the same shape: most severe first, each with the file, a one-sentence summary of the defect, and the concrete scenario where it bites (bad input, real usage) rather than a vague "could be an issue." An empty findings list is a valid, good outcome — say so plainly rather than padding the report to look thorough.

Before reporting, confirm each of steps 3–5 was actually attempted (run, skipped-with-reason, or not-applicable-to-stack) — a step silently skipped is worse than a step that found nothing.
