#!/usr/bin/env python3
"""Plant the tie-break prompt-golf flag.

Scatters the words of a hidden phrase across a fake mini-codebase, each as a
single marker line (``OZFLAG:<index>:<word>``) buried in an otherwise-plausible
file. A precise search (one ``grep | sort | join`` pipeline) reassembles the
phrase cheaply; reading every file into the model's context does not.

The phrase is stored base64-encoded so a casual glance at this file does not
reveal the answer, and the planter NEVER prints the phrase. A few decoy files
carry a different marker (``DECOY``) to punish loose patterns.

Usage:
    python planter.py --dir <project>        # plant (default phrase id 0)
    python planter.py --dir <project> --rot13   # harder: rot13 the words
    python planter.py --dir <project> --clean   # remove the vault
"""
from __future__ import annotations

import argparse
import base64
import codecs
import shutil
from pathlib import Path

VAULT = "tie-break-vault"

# base64 so the answer is not plaintext in this file. A facilitator can pick one
# with --phrase-id; default 0. (All are Wizard of Oz lines.)
_PHRASES_B64 = [
    "cGF5IG5vIGF0dGVudGlvbiB0byB0aGUgbWFuIGJlaGluZCB0aGUgY3VydGFpbg==",
    "dGhlcmUncyBubyBwbGFjZSBsaWtlIGhvbWU=",
    "dG90byBpJ3ZlIGEgZmVlbGluZyB3ZSdyZSBub3QgaW4ga2Fuc2FzIGFueW1vcmU=",
]
# decoy fragments (never the real answer) — different marker, ignored by a good grep
_DECOY_WORDS = ["lions", "tigers", "bears", "ruby", "slippers", "emerald", "city"]

# (relative path, comment style) — varied languages/locations; all comment-safe
SLOTS = [
    ("src/auth/session.py",        "# {}"),
    ("src/utils/strings.go",       "// {}"),
    ("config/app.yaml",            "# {}"),
    ("internal/cache/store.rb",    "# {}"),
    ("web/handlers/router.js",     "// {}"),
    ("scripts/deploy.sh",          "# {}"),
    ("db/migrations/001_init.sql", "-- {}"),
    ("docs/NOTES.md",              "<!-- {} -->"),
    ("lib/parser/lexer.c",         "// {}"),
    ("pkg/api/client.ts",          "// {}"),
    ("ops/terraform/main.tf",      "# {}"),
    ("tests/test_smoke.py",        "# {}"),
]

FILLER = {
    "py":  ["def _noop():", "    return None", "", "VERSION = '1.0'", ""],
    "go":  ["package main", "", "func helper() bool { return true }", ""],
    "js":  ["export const ready = true;", "function ping() { return 200; }", ""],
    "ts":  ["export type Id = string;", "export const ok = (): boolean => true;", ""],
    "rb":  ["module Store", "  def self.warm?; true; end", "end", ""],
    "sh":  ["set -euo pipefail", 'echo "deploying..."', ""],
    "sql": ["CREATE TABLE widgets (id INT PRIMARY KEY);", ""],
    "md":  ["# Notes", "", "Internal scratch pad.", ""],
    "c":   ["#include <stdio.h>", "int lex(void) { return 0; }", ""],
    "yaml":["service: api", "replicas: 3", "env: prod", ""],
    "tf":  ['resource "null_resource" "x" {}', ""],
}


def rot13(s: str) -> str:
    return codecs.encode(s, "rot_13")


def decode_phrase(phrase_id: int) -> str:
    return base64.b64decode(_PHRASES_B64[phrase_id]).decode()


def _filler_for(path: Path) -> list[str]:
    return FILLER.get(path.suffix.lstrip("."), ["// placeholder", ""])


def plant(root: Path, phrase_id: int, use_rot13: bool) -> int:
    words = decode_phrase(phrase_id).split()
    vault = root / VAULT
    if vault.exists():
        shutil.rmtree(vault)

    # write one fragment per slot, scattered, indexed from 1
    for i, word in enumerate(words, start=1):
        rel, comment = SLOTS[(i - 1) % len(SLOTS)]
        target = vault / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = rot13(word) if use_rot13 else word
        marker = comment.format(f"OZFLAG:{i}:{payload}")
        lines = _filler_for(target)
        # tuck the marker partway down so it is not the first line
        mid = max(1, len(lines) // 2)
        body = lines[:mid] + [marker] + lines[mid:]
        target.write_text("\n".join(body) + "\n", encoding="utf-8")

    # decoys: different marker, plausible-but-wrong words
    for j, dw in enumerate(_DECOY_WORDS, start=1):
        rel, comment = SLOTS[(j + len(words)) % len(SLOTS)]
        target = vault / "vendor" / Path(rel).name
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = rot13(dw) if use_rot13 else dw
        marker = comment.format(f"DECOY:{j}:{payload}")
        target.write_text(marker + "\n" + "\n".join(_filler_for(target)) + "\n",
                          encoding="utf-8")

    return len(words)


def main():
    ap = argparse.ArgumentParser(description="Plant the tie-break prompt-golf flag.")
    ap.add_argument("--dir", default=".", help="project root (default: cwd)")
    ap.add_argument("--phrase-id", type=int, default=0,
                    help="which hidden phrase (0-2, default 0)")
    ap.add_argument("--rot13", action="store_true",
                    help="rot13-encode each word (harder variant)")
    ap.add_argument("--clean", action="store_true", help="remove the vault and exit")
    ap.add_argument("--quiet", action="store_true", help="minimal output")
    args = ap.parse_args()

    root = Path(args.dir).expanduser().resolve()
    vault = root / VAULT

    if args.clean:
        if vault.exists():
            shutil.rmtree(vault)
            print(f"removed {vault}")
        else:
            print("nothing to clean")
        return

    n = plant(root, args.phrase_id, args.rot13)
    mode = "rot13" if args.rot13 else "plain"
    if args.quiet:
        print(f"planted {n} fragments ({mode}) under {vault}")
    else:
        print(f"Planted {n} fragments + {len(_DECOY_WORDS)} decoys under {vault} ({mode}).")
        print("The phrase is NOT printed here — that's the challenge.")
        print("Now /clear your context and make your one-shot attempt.")


if __name__ == "__main__":
    main()
