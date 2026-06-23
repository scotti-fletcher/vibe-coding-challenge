#!/usr/bin/env python3
"""Create empty-ish artifact templates in the locations the scoreboard expects,
so a participant's work lands where the submit skill will auto-collect it.

Idempotent: never overwrites an existing file (use --force to replace). Templates
are deliberately light — section headers and prompts, no answers.

Also persists SCOREBOARD_URL into your shell profile so submit-to-scoreboard can
reach the live scoreboard server (re-running updates the value; --no-env skips it).

Usage:
    python scaffold.py                 # scaffold in the current directory
    python scaffold.py --dir <path>    # scaffold elsewhere
    python scaffold.py --force         # overwrite existing templates
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# The live scoreboard server. submit-to-scoreboard reads this from SCOREBOARD_URL;
# a facilitator updates it here (and re-runs scaffold) if the host changes.
SCOREBOARD_URL = "https://scoreboard-service-971046046859.australia-southeast1.run.app/"

# relative path -> template body. Paths match submit-to-scoreboard discovery.
TEMPLATES = {
    ".claude/skills/customer-summary/SKILL.md": """\
---
name: customer-summary
description: Summarize a code file for a customer, explaining what it does and why.
---

# Customer Summary (Card 3)

This skill provides a basic summary of a code file.

To use it:
- Read the file at the path provided by the user.
- Explain in simple terms what the file does.
- Explain why this file is important for the application.

---
### 🛠️ IMPROVE THIS SKILL!
This is a naive starter prompt. To complete Card 3 and get full points, you should edit this file (`.claude/skills/customer-summary/SKILL.md`) and improve the prompt to:
1. Identify and explain any **security implications** or risks in the code.
2. Support an optional **audience** parameter (e.g., `/customer-summary <file> executive` vs `/customer-summary <file> technical`) and tailor the tone and detail level accordingly.
3. Make it robust so it works on any file path.
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


def _shell_profile() -> Path:
    """Best-guess shell rc for the current user (the file the login shell sources)."""
    home = Path.home()
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return home / ".zshrc"
    if "bash" in shell:
        return home / ".bashrc"
    return home / ".profile"


def ensure_env_vars(team_name: str | None = None) -> list[str]:
    """Persist `export SCOREBOARD_URL=...` and optionally `export TEAM_NAME=...`
    in the user's shell profile so the values are present in new terminals.

    Idempotent: updates the lines in place if they already exist, appends if absent.
    Returns a list of status strings for the run summary.
    """
    profile = _shell_profile()
    existing = profile.read_text(encoding="utf-8") if profile.exists() else ""
    statuses = []

    # 1. Handle SCOREBOARD_URL
    os.environ["SCOREBOARD_URL"] = SCOREBOARD_URL
    url_line = f"export SCOREBOARD_URL={SCOREBOARD_URL}"
    url_pattern = re.compile(r"^export SCOREBOARD_URL=.*$", re.M)

    if url_pattern.search(existing):
        updated = url_pattern.sub(url_line, existing)
        if updated != existing:
            existing = updated
            profile.write_text(existing, encoding="utf-8")
            statuses.append(f"updated  SCOREBOARD_URL in {profile}")
        else:
            statuses.append(f"kept     SCOREBOARD_URL in {profile} (already current)")
    else:
        sep = "" if existing == "" or existing.endswith("\n") else "\n"
        block = f"{sep}\n# Wiz hackathon scoreboard\n{url_line}\n"
        existing += block
        profile.write_text(existing, encoding="utf-8")
        statuses.append(f"added    SCOREBOARD_URL to {profile}")

    # 2. Handle TEAM_NAME
    if team_name:
        os.environ["TEAM_NAME"] = team_name
        team_line = f"export TEAM_NAME=\"{team_name}\""
        team_pattern = re.compile(r"^export TEAM_NAME=.*$", re.M)

        if team_pattern.search(existing):
            updated = team_pattern.sub(team_line, existing)
            if updated != existing:
                existing = updated
                profile.write_text(existing, encoding="utf-8")
                statuses.append(f"updated  TEAM_NAME in {profile}")
            else:
                statuses.append(f"kept     TEAM_NAME in {profile} (already current)")
        else:
            sep = "" if existing == "" or existing.endswith("\n") else "\n"
            block = f"{sep}export TEAM_NAME=\"{team_name}\"\n"
            existing += block
            profile.write_text(existing, encoding="utf-8")
            statuses.append(f"added    TEAM_NAME (\"{team_name}\") to {profile}")

    return statuses


def main():
    ap = argparse.ArgumentParser(description="Scaffold hackathon artifact templates.")
    ap.add_argument("--dir", default=".", help="project root (default: cwd)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--no-env", action="store_true",
                    help="skip persisting env vars to your shell profile")
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

    team_name = os.environ.get("TEAM_NAME", "")
    if not team_name and sys.stdin.isatty() and not args.no_env:
        try:
            print("\n🏆 Scoreboard Setup")
            team_name = input("Enter your Team Name (to auto-submit later): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSkipping team name setup.")

    if not args.no_env:
        statuses = ensure_env_vars(team_name if team_name else None)
        for status in statuses:
            print(f"  {status}")
        print("  (open a new terminal — or just submit via Claude — to pick it up)")

    if skipped and not args.force:
        print("\nExisting files were left untouched. Re-run with --force to reset them.")


if __name__ == "__main__":
    main()
