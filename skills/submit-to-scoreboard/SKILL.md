---
name: submit-to-scoreboard
description: Find this team's hackathon artifacts (skill, Juice Shop findings, customer insight, website) and Claude Code session logs, then upload them to the scoreboard against the team name. Use when the user says "submit my work", "upload to the scoreboard", "submit my challenge results", or similar.
---

# Submit to the hackathon scoreboard

This skill collects the files a team produced during the SE AI CLI hackathon
and uploads them to the scoreboard server. A helper script does the file
discovery and the upload; your job is to run it, interpret what it found, and
fill any gaps by asking the user.

The helper is `submit.py`, located next to this SKILL.md. Always invoke it with
that absolute path. It uses only the Python standard library.

## What gets submitted

| Artifact   | What it is                                          |
|------------|-----------------------------------------------------|
| `skill`    | The Card 3 customer-summary Skill (`.claude/skills/<name>/SKILL.md`) |
| `findings` | Card 5 — security review findings (OWASP Juice Shop)|
| `insight`  | Card 4 — customer-facing insight from live MCP data |
| `website`  | Card 6 — the single-page site (`index.html`)        |
| `logs`     | Claude Code session logs (`~/.claude/projects/...`) |

Logs are how the objective signals (subagent used, MCP called, token efficiency)
are scored — always try to include them.

## Steps

1. **Determine the team name.** Use the `TEAM_NAME` environment variable if it
   is set. Otherwise ask the user: *"What's your team name?"* Do not invent one.

2. **Discover what's present.** Run a dry check from the user's project directory:

   ```bash
   python /absolute/path/to/submit.py --check --dir "$(pwd)"
   ```

   This prints JSON: `found` (label → path) and `missing` (labels not located).
   It does not upload anything.

3. **Show the user a short summary** of what was found and what's missing — e.g.
   "Found your skill and website and 2 session logs; couldn't find Juice Shop
   findings or a customer insight."

4. **Fill gaps by asking.** For each missing artifact the user expects to submit,
   ask where it is: *"I couldn't find your Juice Shop findings — what's the path
   to that file?"* Accept a path or a "skip it, I didn't do that one." Do not
   guess paths or upload an unrelated file. If session `logs` are missing, tell
   the user they live under `~/.claude/projects/<project>/` and ask whether to
   point at a specific `.jsonl`.

5. **Upload.** Run the real submission, passing the team name and any paths the
   user supplied for previously-missing items:

   ```bash
   python /absolute/path/to/submit.py --team "TEAM" --dir "$(pwd)" \
       --findings "/path/they/gave" --insight "/path/they/gave"
   ```

   (Only add `--<artifact>` flags for items discovery missed and the user
   located. Discovered items upload automatically.)

6. **Confirm the result.** The script prints `http_status` and the uploaded
   files. Tell the user: which artifacts were uploaded, anything still missing,
   and that they can re-run anytime to update (re-submitting overwrites their
   previous upload under the same team name). Submissions are collected now and
   scored offline by the facilitator after the round — there is no live
   leaderboard, so nothing is revealed to other teams at submit time.

## Configuration

- Server URL comes from `SCOREBOARD_URL` (default `http://localhost:5000`). The
  facilitator sets this to the live scoreboard URL on team workstations before
  the lab starts, so the skill "just works". If the upload fails with a
  connection error, the env var is likely unset or stale — confirm the current
  server URL with the user and re-run with `--server http://<host>`.
- No auth is needed to submit: `/submit` is public. The admin token only gates
  the facilitator's bundle download, which teams never touch.

## Guardrails

- Never upload under a team name the user did not confirm — submitting under
  another team's name overwrites their results.
- If discovery finds several candidates and you're unsure which is the real
  artifact, show the path and confirm with the user before uploading.
- If nothing is found and the user can't provide paths, stop and explain — don't
  submit an empty entry.
