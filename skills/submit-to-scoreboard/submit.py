#!/usr/bin/env python3
"""Locate a team's hackathon artifacts + Claude Code session logs and upload
them to the scoreboard server. Standard-library only (no pip installs).

Usage:
    python submit.py --check                      # discover only, print JSON
    python submit.py --team "Team Bravo"          # discover + upload
    python submit.py --team "Team Bravo" \
        --skill path/to/skill.md --website path/to/index.html   # overrides

Config via env (handy when baked into a workstation image):
    TEAM_NAME        default team name
    SCOREBOARD_URL   default server, e.g. https://scoreboard.internal  (default https://scoreboard-service-971046046859.australia-southeast1.run.app/)
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path

DEFAULT_SERVER = os.environ.get("SCOREBOARD_URL", "https://scoreboard-service-971046046859.australia-southeast1.run.app/")
PRUNE_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build",
              "__pycache__", ".next", ".cache", "site-packages"}
MAX_LOGS = 5  # most-recent session logs to send

# the scaffolding skills shipped with the hackathon repo — never submit these
# as a team's Card 3 Skill.
SKILL_EXCLUDE = ("/hackathon-start/", "/submit-to-scoreboard/", "/tie-break/")

# label -> (glob patterns, substrings that make a match preferred)
# Card 3 is now a Skill at .claude/skills/<name>/SKILL.md (the current standard);
# legacy .claude/commands/*.md still works and is kept as a fallback.
ARTIFACTS = {
    "skill":    ([".claude/skills/*/SKILL.md", ".claude/commands/*.md",
                  ".claude/commands/**/*.md", "**/*summary*.md"],
                 ["customer", "summary"]),
    "findings": (["**/*finding*.md", "**/*juice*.md", "**/security*review*.md",
                  "**/*vuln*.md"], ["juice", "finding"]),
    "insight":  (["**/*insight*.md", "**/*customer-insight*.md",
                  "**/*briefing*.md"], ["insight"]),
    "website":  (["index.html", "site/index.html", "**/site/index.html",
                  "**/index.html"], ["site", "posture", "dashboard"]),
    "tiebreak": (["tiebreak.json", "**/tiebreak.json"], ["tiebreak"]),
}


def _iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        for fn in filenames:
            yield Path(dirpath) / fn


def find_artifact(root: Path, patterns, prefer, exclude=()) -> Path | None:
    matches: list[Path] = []
    for pat in patterns:
        matches.extend(p for p in root.glob(pat) if p.is_file())
    if exclude:
        matches = [p for p in matches
                   if not any(x in (str(p) + "/") for x in exclude)]
    if not matches:
        return None
    # dedupe, prefer files whose path hints at the right thing, then shallowest
    seen, uniq = set(), []
    for m in matches:
        rp = m.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(m)

    def score(p: Path):
        s = str(p).lower()
        pref = 0 if any(sub in s for sub in prefer) else 1
        return (pref, len(p.parts))

    uniq.sort(key=score)
    return uniq[0]


def encode_project_dir(cwd: Path) -> str:
    """Claude Code stores logs under ~/.claude/projects/<abs-path with / -> ->."""
    return str(cwd.resolve()).replace("/", "-")


def find_session_logs(cwd: Path) -> list[Path]:
    base = Path.home() / ".claude" / "projects"
    if not base.is_dir():
        return []
    enc = encode_project_dir(cwd)
    candidates = [base / enc]
    if not candidates[0].is_dir():
        # fallback: a project dir ending with this folder's name, else newest
        leaf = cwd.resolve().name
        ending = [d for d in base.iterdir() if d.is_dir() and d.name.endswith(leaf)]
        if ending:
            candidates = ending
        else:
            dirs = [d for d in base.iterdir() if d.is_dir()]
            candidates = sorted(dirs, key=lambda d: d.stat().st_mtime, reverse=True)[:1]
    logs: list[Path] = []
    for d in candidates:
        if d.is_dir():
            logs.extend(p for p in d.glob("*.jsonl") if p.is_file())
    logs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return logs[:MAX_LOGS]


def discover(cwd: Path, overrides: dict) -> dict:
    found, missing = {}, []
    for label, (patterns, prefer) in ARTIFACTS.items():
        if overrides.get(label):
            p = Path(overrides[label]).expanduser()
            if p.is_file():
                found[label] = str(p)
            else:
                missing.append(label)
            continue
        hit = find_artifact(cwd, patterns, prefer,
                            exclude=SKILL_EXCLUDE if label == "skill" else ())
        if hit:
            found[label] = str(hit)
        else:
            missing.append(label)

    if overrides.get("logs"):
        lp = Path(overrides["logs"]).expanduser()
        found["logs"] = [str(lp)] if lp.is_file() else []
        if not found["logs"]:
            missing.append("logs")
    else:
        logs = find_session_logs(cwd)
        found["logs"] = [str(p) for p in logs]
        if not logs:
            missing.append("logs")
    return {"found": found, "missing": missing}


# ---- multipart upload (stdlib) -------------------------------------------
def _part(boundary, name, filename, content, ctype):
    return (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode() + content + b"\r\n"


def build_multipart(team: str, found: dict):
    boundary = uuid.uuid4().hex
    body = bytearray()
    body += (f"--{boundary}\r\n"
             f'Content-Disposition: form-data; name="team"\r\n\r\n{team}\r\n').encode()
    for field in ("skill", "findings", "insight", "website", "tiebreak"):
        path = found.get(field)
        if path:
            p = Path(path)
            ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            body += _part(boundary, field, p.name, p.read_bytes(), ctype)
    for path in found.get("logs", []):
        p = Path(path)
        body += _part(boundary, "logs", p.name, p.read_bytes(), "application/jsonl")
    body += f"--{boundary}--\r\n".encode()
    return bytes(body), boundary


def upload(server: str, team: str, found: dict) -> tuple[int, str]:
    import urllib.request
    import urllib.error
    body, boundary = build_multipart(team, found)
    url = server.rstrip("/") + "/submit"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode(errors="replace")[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]
    except urllib.error.URLError as e:
        return 0, f"connection failed: {e.reason}"


def main():
    ap = argparse.ArgumentParser(description="Upload hackathon artifacts to the scoreboard.")
    ap.add_argument("--team", default=os.environ.get("TEAM_NAME"))
    ap.add_argument("--server", default=DEFAULT_SERVER)
    ap.add_argument("--dir", default=".", help="project root to scan (default: cwd)")
    ap.add_argument("--check", action="store_true", help="discover only; print JSON, don't upload")
    for label in ("skill", "findings", "insight", "website", "logs"):
        ap.add_argument(f"--{label}", help=f"explicit path for {label} (overrides discovery)")
    args = ap.parse_args()

    cwd = Path(args.dir).expanduser().resolve()
    overrides = {k: getattr(args, k) for k in ("skill", "findings", "insight", "website", "logs")}
    result = discover(cwd, overrides)
    result["team"] = args.team
    result["server"] = args.server
    result["scanned_dir"] = str(cwd)

    if args.check:
        print(json.dumps(result, indent=2))
        return 0

    if not args.team:
        print(json.dumps({**result, "error":
              "No team name. Pass --team \"Your Team\" or set TEAM_NAME."}, indent=2))
        return 2
    if not any(result["found"].get(k) for k in ("skill", "findings", "insight", "website")) \
            and not result["found"].get("logs"):
        print(json.dumps({**result, "error":
              "Nothing found to upload. Re-run with explicit --<artifact> paths."}, indent=2))
        return 2

    status, msg = upload(args.server, args.team, result["found"])
    summary = {
        "uploaded": {k: v for k, v in result["found"].items() if v},
        "missing": result["missing"],
        "team": args.team,
        "server": args.server,
        "http_status": status,
        "server_response": msg,
    }
    print(json.dumps(summary, indent=2))
    return 0 if status in (200, 302) else 1


if __name__ == "__main__":
    sys.exit(main())
