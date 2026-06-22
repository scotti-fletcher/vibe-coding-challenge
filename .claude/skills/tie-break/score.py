#!/usr/bin/env python3
"""Score a tie-break attempt: the token cost of your single one-shot turn.

Reads the Claude Code session log and sums the model's token usage for the last
exchange (your one human prompt + everything the model did to answer it). The
headline number is "new" tokens — prompt input + tool-result/context growth +
output — which excludes the fixed cached baseline so it actually discriminates.

Lower is better. Run it right after your attempt.

Usage:
    python score.py                      # newest session for this project
    python score.py --session <file.jsonl>
    python score.py --all-tokens         # also include cached-read baseline
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"


def project_dir_for_cwd() -> Path:
    # Claude Code mangles the cwd path into the project folder name (/ -> -).
    mangled = str(Path.cwd().resolve()).replace("/", "-")
    return PROJECTS / mangled


def newest_jsonl(explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.exists() else None
    candidates: list[Path] = []
    pdir = project_dir_for_cwd()
    if pdir.exists():
        candidates = list(pdir.glob("*.jsonl"))
    if not candidates and PROJECTS.exists():
        candidates = list(PROJECTS.glob("*/*.jsonl"))
    return max(candidates, key=lambda f: f.stat().st_mtime) if candidates else None


def is_human_turn(obj: dict) -> bool:
    if obj.get("type") != "user" or obj.get("isSidechain"):
        return False
    content = obj.get("message", {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        # tool results come back as 'user' messages — skip those
        return not any(isinstance(it, dict) and it.get("type") == "tool_result"
                       for it in content)
    return False


def main():
    ap = argparse.ArgumentParser(description="Score a tie-break attempt's token cost.")
    ap.add_argument("--session", help="explicit path to a session .jsonl")
    ap.add_argument("--all-tokens", action="store_true",
                    help="include cached-read baseline in the total")
    args = ap.parse_args()

    path = newest_jsonl(args.session)
    if not path:
        print("Could not find a session log. Pass --session <file.jsonl>, or just "
              "run /context in Claude Code and read the token count there.")
        return

    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    objs = []
    for l in lines:
        try:
            objs.append(json.loads(l))
        except json.JSONDecodeError:
            continue

    last_human = max((i for i, o in enumerate(objs) if is_human_turn(o)), default=None)
    if last_human is None:
        print("No human turn found in the log; nothing to score.")
        return

    inp = cache_create = cache_read = out = 0
    turns = 0
    for o in objs[last_human + 1:]:
        if o.get("type") != "assistant":
            continue
        u = o.get("message", {}).get("usage") or {}
        inp += u.get("input_tokens", 0)
        cache_create += u.get("cache_creation_input_tokens", 0)
        cache_read += u.get("cache_read_input_tokens", 0)
        out += u.get("output_tokens", 0)
        turns += 1

    new_tokens = inp + cache_create + out
    total = new_tokens + (cache_read if args.all_tokens else 0)

    print(f"Session: {path.name}")
    print(f"Model turns in this attempt: {turns}")
    print("  prompt + context (input):", inp + cache_create)
    print("  output:                  ", out)
    print("  cached baseline (read):  ", cache_read, "(excluded from score)")
    print("-" * 40)
    label = "ATTEMPT COST (incl. cache)" if args.all_tokens else "ATTEMPT COST (new tokens)"
    print(f"{label}: {total}")
    print("Lower is better. Tie-break ranks on this number.")


if __name__ == "__main__":
    main()
