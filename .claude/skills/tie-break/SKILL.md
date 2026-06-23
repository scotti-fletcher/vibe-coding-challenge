---
name: tie-break
description: Run the Prompt Golf bonus challenge — recover a phrase hidden across a fake codebase using the fewest tokens. Everyone plays; run as many attempts as you like and your best (fewest-token correct) run is captured to tiebreak.json and submitted. Use when the user says "prompt golf", "tie-break", "start the prompt golf challenge", "golf challenge", or similar.
---

# Prompt Golf 🏌️ — bonus challenge

A hidden phrase (a line from *The Wizard of Oz*) is scattered, one word per file,
across a small fake codebase. Recover the **whole phrase** using the **fewest
tokens**. Everyone plays, **run as many attempts as you like**, and your best
correct run is what counts. Precise search wins; stuffing the repo into context
loses.

## ⚠️ Setting up — don't reveal the answer

When this skill runs, your job is to set up the challenge and explain the rules —
**not** to solve it. **Do not** search for the phrase, read `tie-break-vault/`, or
open `planter.py`. Seeing the answer would poison the player's attempts. Plant,
brief, hand over.

## Step 1 — Plant the flag (quietly)

Run the planter as a black box from the skill directory (it prints a count, never
the phrase):

```bash
python <skill-dir>/planter.py --dir "$(pwd)" --quiet
```

- Default phrase id is `0`; everyone should use the **same** `--phrase-id` for a fair race.
- Harder variant: add `--rot13` (words are rot13-encoded; the solver must decode).
- Re-running replants cleanly; `--clean` removes the vault.

Do not read the files it creates.

## Step 2 — Play: many attempts, keep your best

Tell the player the rules, then **let them drive**:

> **The rules**
> 1. **Each attempt starts clean** — run `/clear`, then a single prompt to recover
>    the phrase.
> 2. **Fewest tokens wins.** Push the work to the shell; keep context lean.
> 3. **Unlimited attempts.** Refine your prompt, `/clear`, try again — only your
>    best correct run is kept.
> 4. **How the flag is laid out.** Every file under `tie-break-vault/` hides one
>    line shaped like `OZFLAG:3:attention`:
>    - `OZFLAG` — the real marker; grab **only** lines with this exact prefix.
>    - `3` — the word's position in the phrase.
>    - `attention` — the actual word.
>
>    Some files also carry **decoy** lines under a *different* marker (e.g.
>    `DECOY:3:bears`). A too-loose search will scoop these up and corrupt your
>    answer — match the `OZFLAG` prefix precisely. Then collect every `OZFLAG`
>    line, **sort numerically by the middle number** (1, 2, 3 … not
>    alphabetically), and join the words in that order — that's the phrase.

Spell that layout out for the player up front — don't make them ask. The elegant
solutions are usually one `grep | sort | join` pipeline, but discovering *that
pipeline* is their job, not yours.

## Step 3 — Score each attempt (keeps your best)

After **each** attempt, in a **separate terminal** (so scoring doesn't add tokens
to the attempt you're measuring):

```bash
python <skill-dir>/verify.py "<your recovered phrase>"             # quick PASS/FAIL (+ reveals the reference solution)
python <skill-dir>/score.py --answer "<your recovered phrase>"     # scores it and keeps your best in tiebreak.json
```

`score.py --answer` reports the attempt's **new-token** cost and updates
**`tiebreak.json`** (`{solved, tokens, phrase_id, attempts}`) only when this run
beats your stored best (fewest tokens among correct attempts). Loop: tweak the
prompt → `/clear` → attempt → score. Pass `--phrase-id N` if a non-default phrase
was planted.

`tiebreak.json` is collected by `submit-to-scoreboard` on a normal "submit my
work", and feeds the **Tie-break Champion** award (fewest tokens among teams that
solved it). The award is **standalone** — it never changes the main leaderboard.

## Notes

- Run `verify.py` / `score.py` in a side terminal, **not** through the AI, so they
  don't count toward the attempt you're scoring.
- This skill's folder is excluded from scoreboard artifact collection — it won't be
  mistaken for a team's Card 3 skill.
