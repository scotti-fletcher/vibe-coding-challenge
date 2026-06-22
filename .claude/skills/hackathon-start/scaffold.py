#!/usr/bin/env python3
"""Create empty-ish artifact templates in the locations the scoreboard expects,
so a participant's work lands where the submit skill will auto-collect it.

Idempotent: never overwrites an existing file (use --force to replace). Templates
are deliberately light — section headers and prompts, no answers.

Usage:
    python scaffold.py                 # scaffold in the current directory
    python scaffold.py --dir <path>    # scaffold elsewhere
    python scaffold.py --force         # overwrite existing templates
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

# relative path -> template body. Paths match submit-to-scoreboard discovery.
TEMPLATES = {
    ".claude/skills/customer-summary/SKILL.md": """\
---
name: customer-summary
description: <one line — when should the AI reach for this skill?>
---

# Customer Summary  (Card 3)

<!--
Write your best reusable prompt here. The goal: a customer-ready summary of ANY
code file. Things worth covering — what it does, why it matters, security
implications. Bonus: take an audience argument (technical vs executive).
Delete these comments as you go.
-->
""",
    "insight.md": """\
# Customer Insight  (Card 4)

<!-- Pull live data with the Wiz MCP first, then write what a customer would
     actually read. Keep it grounded in the data you pulled. -->

## Headline
_The one-line takeaway._

## What the data shows
-

## Why it matters / recommended next step
-
""",
    "findings.md": """\
# Security Review — OWASP Juice Shop  (Card 5)

<!-- Run a quick baseline review, then a sharper second pass (better prompts,
     tighter context, subagents per area). The interesting part is the diff. -->

## Baseline run
-

## Improved run
-

## What changed, and why
_Why did one run find more than the other?_
""",
    "site/index.html": """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Security Posture</title>
</head>
<body>
  <h1>Security Posture</h1>
  <!-- Card 6: build this out by conversation. Describe the vibe, iterate on it,
       and feed it real Wiz MCP data for bonus realism. -->
</body>
</html>
""",
}


def main():
    ap = argparse.ArgumentParser(description="Scaffold hackathon artifact templates.")
    ap.add_argument("--dir", default=".", help="project root (default: cwd)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    root = Path(args.dir).expanduser().resolve()
    created, skipped = [], []
    for rel, body in TEMPLATES.items():
        target = root / rel
        if target.exists() and not args.force:
            skipped.append(rel)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        created.append(rel)

    print(f"Scaffolded in {root}")
    for rel in created:
        print(f"  created  {rel}")
    for rel in skipped:
        print(f"  kept     {rel}  (already exists — left your work alone)")
    if skipped and not args.force:
        print("\nExisting files were left untouched. Re-run with --force to reset them.")


if __name__ == "__main__":
    main()
