---
name: tie-break
description: Run the hackathon tie-break — a one-shot prompt-golf challenge. Plant a hidden phrase scattered across a fake codebase, then have the participant recover it in a single attempt using the fewest tokens. Use when the user says "tie-break", "start the tie break", "run the tiebreaker", or "prompt golf", or when facilitators need to break a scoreboard tie.
---

# Tie-break — Prompt Golf 🏌️

A sudden-death efficiency duel. A hidden phrase (a line from *The Wizard of Oz*)
is scattered, one word per file, across a small fake codebase. The participant
gets **one shot** to recover the full phrase — and is ranked on **fewest tokens**.
Precise search wins; stuffing the repo into context loses.

## ⚠️ Administer this — do NOT solve it

When this skill runs, your ONLY job is to set up the challenge and explain the
rules. **Do not** search for the phrase, **do not** read `tie-break-vault/`, and
**do not** open `planter.py`. Seeing the answer would poison the attempt. Plant,
brief, stop.

## Step 1 — Plant the flag (quietly)

Run the planter as a black box from the skill directory (it prints a count, never
the phrase). Use the project root as `--dir`:

```bash
python <skill-dir>/planter.py --dir "$(pwd)" --quiet
```

- Default phrase id is `0`. A facilitator can vary it with `--phrase-id 0|1|2`.
- Harder variant: add `--rot13` (words are rot13-encoded; the solver must decode).
- Re-running replants cleanly; `--clean` removes the vault afterwards.

Do not read the files it creates.

## Step 2 — Brief the rules, then hand over

Tell the participant, then **stop and let them drive**:

> **The rules**
> 1. **Clear your context now** — run `/clear`. Your attempt must start clean.
> 2. **One shot.** A single prompt. The model must actually *find* the phrase
>    (the session log proves it) — no pasting an answer you read yourself.
> 3. **Fewest tokens wins.** Push the work to the shell; keep context lean.
> 4. The phrase is a *Wizard of Oz* line, scattered one word per file under
>    `tie-break-vault/` behind the marker `OZFLAG:<index>:<word>`. Decoys under a
>    different marker are there to punish loose patterns. Order by index.

That's the whole brief. The elegant solutions are usually one `grep | sort | join`
pipeline — but discovering that is *their* job, not yours.

## Step 3 — Verify & score (after their shot)

These are plain commands the participant runs after their one attempt (verifying
does not need to count against the score):

```bash
python <skill-dir>/verify.py "<their recovered phrase>"   # PASS/FAIL (+ reveals the reference solution)
python <skill-dir>/score.py                               # token cost of the attempt
```

`score.py` reads the session log and reports **attempt cost (new tokens)** — prompt
+ context growth + output, excluding the fixed cached baseline. **Lower wins.**
Record PASS/FAIL and the token number; lowest tokens among correct answers takes
the tie. (No log? `/context` in Claude Code shows the count too.)

## Facilitator notes

- Keep everyone on the **same `--phrase-id`** (and same `--rot13` setting) for a fair race.
- For a clean room, plant from a **separate terminal** before participants start,
  so nothing touches their attempt session.
- This skill's folder is excluded from scoreboard artifact collection — it won't be
  mistaken for a participant's Card 3 skill.
