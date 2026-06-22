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
import base64
import json
import os
import re
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"

# kept in sync with verify.py — used to record solved=true/false in the artifact
_PHRASES_B64 = [
    "cGF5IG5vIGF0dGVudGlvbiB0byB0aGUgbWFuIGJlaGluZCB0aGUgY3VydGFpbg==",
    "dGhlcmUncyBubyBwbGFjZSBsaWtlIGhvbWU=",
    "dG90byBpJ3ZlIGEgZmVlbGluZyB3ZSdyZSBub3QgaW4ga2Fuc2FzIGFueW1vcmU=",
]


def _normalize(s: str) -> str:
    s = s.lower().replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


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
    ap.add_argument("--answer", help="score this attempt and keep your BEST run in "
                    "tiebreak.json (fewest tokens among correct attempts) — the "
                    "artifact the scoreboard reads for the award")
    ap.add_argument("--phrase-id", type=int, default=0,
                    help="which hidden phrase the answer is checked against (default 0)")
    ap.add_argument("--out", default="tiebreak.json",
                    help="where to write the artifact when --answer is given")
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

    if args.answer is not None:
        expected = base64.b64decode(_PHRASES_B64[args.phrase_id]).decode()
        solved = _normalize(args.answer) == _normalize(expected)

        out = Path(args.out)
        prev = None
        if out.exists():
            try:
                prev = json.loads(out.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                prev = None
        prev = prev if isinstance(prev, dict) else None
        attempts = (prev.get("attempts", 1) + 1) if prev else 1

        # this attempt is a new best only if it RECOVERED the phrase and either
        # nothing better is stored yet, or it used fewer tokens than the stored best.
        improved = solved and (
            prev is None
            or not prev.get("solved")
            or new_tokens < prev.get("tokens", float("inf"))
        )
        if improved or prev is None:
            best = {"solved": solved, "tokens": new_tokens, "phrase_id": args.phrase_id}
        else:
            best = {"solved": bool(prev.get("solved")), "tokens": prev.get("tokens"),
                    "phrase_id": prev.get("phrase_id", args.phrase_id)}
        best["attempts"] = attempts
        best["marker"] = "tiebreak"
        out.write_text(json.dumps(best, indent=2) + "\n", encoding="utf-8")

        print("-" * 40)
        print(f"Attempt #{attempts}: solved={solved}, tokens={new_tokens}")
        if improved:
            print(f"🏆 New best — {new_tokens} tokens. Saved to {args.out}.")
        elif best.get("solved"):
            print(f"Kept your best: {best['tokens']} tokens (this run didn't beat it).")
        else:
            print(f"Not solved yet — recover the correct phrase, then keep golfing.")


if __name__ == "__main__":
    main()
