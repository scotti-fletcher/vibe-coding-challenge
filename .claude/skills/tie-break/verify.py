#!/usr/bin/env python3
"""Verify a tie-break answer and, on success, reveal the reference golf solution.

Run this AFTER your one-shot attempt (it does not need to read the vault).

Usage:
    python verify.py "pay no attention to the man behind the curtain"
    echo "..." | python verify.py            # read answer from stdin
    python verify.py --phrase-id 1 "there's no place like home"
"""
from __future__ import annotations

import argparse
import base64
import re
import sys

_PHRASES_B64 = [
    "cGF5IG5vIGF0dGVudGlvbiB0byB0aGUgbWFuIGJlaGluZCB0aGUgY3VydGFpbg==",
    "dGhlcmUncyBubyBwbGFjZSBsaWtlIGhvbWU=",
    "dG90byBpJ3ZlIGEgZmVlbGluZyB3ZSdyZSBub3QgaW4ga2Fuc2FzIGFueW1vcmU=",
]


def normalize(s: str) -> str:
    s = s.lower().replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def reference_solution(use_rot13: bool) -> str:
    base = (r"grep -rhoE 'OZFLAG:[0-9]+:[^ ]+' tie-break-vault "
            r"| sort -t: -k2 -n | cut -d: -f3")
    if use_rot13:
        base += " | tr 'A-Za-z' 'N-ZA-Mn-za-m'"
    return base + " | paste -sd' ' -"


def main():
    ap = argparse.ArgumentParser(description="Check a tie-break answer.")
    ap.add_argument("answer", nargs="*", help="the recovered phrase")
    ap.add_argument("--phrase-id", type=int, default=0)
    ap.add_argument("--rot13", action="store_true",
                    help="show the rot13 reference solution on success")
    args = ap.parse_args()

    answer = " ".join(args.answer).strip() or sys.stdin.read().strip()
    if not answer:
        print("No answer provided.")
        sys.exit(2)

    expected = base64.b64decode(_PHRASES_B64[args.phrase_id]).decode()
    if normalize(answer) == normalize(expected):
        print("✅ PASS — correct phrase.")
        print(f"\nReference one-shot solution (what the golfers aimed for):\n  {reference_solution(args.rot13)}")
        print("\nNow score your attempt:  python score.py")
        sys.exit(0)
    print("❌ FAIL — that's not the phrase. Try a sharper search.")
    sys.exit(1)


if __name__ == "__main__":
    main()
