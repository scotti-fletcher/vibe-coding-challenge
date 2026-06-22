# Wiz SE AI CLI Hackathon — Participant Skills

This repo carries the Claude Code skills for the Wiz SE AI CLI vibe-coding
hackathon. Clone it onto your workstation and the skills become available in
your AI CLI.

## Get started

In your AI CLI, just say **"get started"** (or run `/hackathon-start`). The
skill will:

1. Clone OWASP Juice Shop for the security-review challenge.
2. Run a quick pre-flight (CLI working + Wiz MCP responding).
3. Walk you through the six challenge cards with hints and "done looks like"
   criteria.

## Submit your work

When you're done, say **"submit my work"** (or run `/submit-to-scoreboard`). It
finds your artifacts (skill, insight, findings, website) and session logs and
uploads them to the scoreboard under your team name. If it can't find a file, it
asks you where it is.

## What's here

| Path | Purpose |
|------|---------|
| `.claude/skills/hackathon-start/` | Onboarding skill (active on clone) |
| `.claude/skills/submit-to-scoreboard/` | Submission skill + uploader |
| `skills/` | Source mirror of the same skills |

The `.claude/skills/` copies are what your CLI loads; `skills/` is the editable
source.
