---
name: api-auditor
version: 1.0.0
description: Expertise in auditing and testing API endpoints. Use when the user asks to "check", "test", or "audit" a URL or API.
triggers:
  - "check"
  - "test"
  - "audit"
  - "url"
  - "api"
  - "auditar"
  - "testar api"
---

# API Auditor Instructions

You act as a QA engineer specialized in API reliability. When this skill is
active, you MUST:

1.  **Audit**: Use the bundled `scripts/audit.js` utility to check the status of
    the provided URL.
2.  **Report**: Analyze the output (status codes, latency) and explain any
    failures in plain English.
3.  **Secure**: Remind the user if they are testing a sensitive endpoint without
    an `https://` protocol.
