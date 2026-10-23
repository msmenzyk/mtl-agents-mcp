# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | Yes       |

## Reporting a Vulnerability

**Please do not open a public issue for security vulnerabilities.**

Instead, report vulnerabilities by emailing **opensource@musictechlab.io**
with the following information:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within **48 hours** and aim to provide
a fix or mitigation within **7 days** for critical issues.

## Disclosure Policy

- We follow **coordinated disclosure**: we ask reporters to give us
  reasonable time to fix issues before public disclosure
- We credit reporters in the release notes (unless they prefer anonymity)
- We do not pursue legal action against good-faith security researchers

## Threat model

This server reads every Claude Code and Codex transcript of the user it runs as,
and `ask_session` can start a headless agent run in another project. Messages
between sessions are marked as coming from another agent, but a model can still
be talked into things, so keep `ask_session` behind your client's permission
prompt. Transcripts are not scrubbed for secrets.
