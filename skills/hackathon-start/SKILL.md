---
name: hackathon-start
description: Onboard a participant to the Wiz SE AI CLI hackathon. Run a quick environment pre-flight (CLI + Wiz MCP), then walk the six challenge cards with hints and "done looks like" criteria, and point to how to submit. Use when the user says "get started", "start the hackathon", "how do I begin", "what are the challenges", "give me the challenges", or similar.
---

# Wiz SE AI CLI Hackathon — Get Started

You are the participant's guide. Be brief and encouraging — simplicity is the #1
priority. Don't dump this whole file at once. Run the pre-flight, then show the
challenges, then answer questions and nudge. Reveal a card's **Hint** only after
they've attempted it or ask for it.

## What this hour is about

Four ideas, learned by doing: **context windows, subagents, skills, and MCP**.
The goal isn't polished code — it's using the tools *well*. ~50 minutes, work at
your own pace, hardest-last. You'll submit at the end (see "Submitting").

## Step 1 — Set up your workspace (~1 min)

Clone OWASP Juice Shop so it's ready for Card 5. Run a **shallow** clone (fast),
and skip if it's already there:

```bash
if [ -d juice-shop ]; then
  echo "juice-shop already present — skipping clone"
else
  git clone --depth 1 https://github.com/juice-shop/juice-shop.git
fi
```

You only need the **source code** for the AI security review — you do **not** need
to `npm install` or run the app unless you want to. If the clone fails (network /
proxy), flag a facilitator; you can still do Cards 1–4 and 6 without it.

Then scaffold the artifact templates so your work lands where the submit skill
expects it. Run `scaffold.py` (next to this SKILL.md — use its absolute path):

```bash
python /absolute/path/to/scaffold.py --dir "$(pwd)"
```

This drops light starter files in the right places — `insight.md` (Card 4),
`findings.md` (Card 5), `site/index.html` (Card 6), and
`.claude/skills/customer-summary/SKILL.md` (Card 3). They're just headers and
prompts, not answers — fill them in as you go. It **won't overwrite** anything you've
already written, so it's safe to run once at the start.

## Step 2 — Pre-flight (~1 min)

Confirm two things before the clock matters:

1. **Your AI CLI works** — ask it one question about the repo and get a sensible answer.
2. **The Wiz MCP responds** — this is the thing that silently breaks Card 4. Run one
   read-only call, e.g. ask: *"Use the Wiz MCP to get my security score."* If a number
   comes back, you're good. If it errors, flag a facilitator now — don't wait.

If either fails, fix it before starting. Everything else is just typing.

## Step 3 — The six challenges

Show this list. Each card teaches one idea through a real SE task. Cards 1–2 are
warm-ups (scored from your session log), 3–6 produce something you submit.

### Card 1 — Context is King · *Beginner · context windows*
- **Task:** "A customer sent you this repo and asked: is it safe?" Find and fix the
  bug by pointing the AI at the **one relevant file** — then try the vague version
  ("find the bug in this project") and notice the difference.
- **Hint:** Name the exact file. Narrow context beats more context — don't dump the repo.
- **Bonus:** Add a `CLAUDE.md` so the AI understands the project without you re-explaining.
- **Done when:** the bug's fixed using just the relevant file, and you can show the
  specific-vs-broad difference.

### Card 2 — Scout, Don't Stuff · *Intermediate · subagents*
- **Task:** Send a **subagent** to do the heavy digging ("which file holds the flaw,
  and why?") so only the summary comes back to your main thread. Then fix it.
- **Hint:** Ask the AI to *"use a subagent to investigate…"*. The whole point is what
  does **not** end up in your main context.
- **Bonus:** Fan out parallel subagents across several leads.
- **Done when:** a subagent did the searching and your main context stayed clean.

### Card 3 — Build a Skill · *Intermediate · skills*
- **Task:** Create a reusable **Skill** that gives a **customer-ready summary** of any
  code file (what it does, why it matters, security implications). Test it on 2–3 files.
- **Hint:** Save your best prompt as a Skill — a folder `.claude/skills/<name>/SKILL.md`
  with a short `description` in the frontmatter. To test it without leaving your open
  session, just **ask the AI to run your skill** (e.g. "use the customer-summary skill
  on `src/auth.py`"). Typing `/<name>` works too — both are valid; a freshly created
  skill may only show up as `/<name>` after the session reloads, but asking for it by
  name works right away. Write it once, reuse forever.
- **Bonus:** Make it take an **audience** parameter (technical vs. executive).
- **Done when:** it runs cleanly on a file you didn't build it for. *(Submit this.)*

### Card 4 — Talk to Wiz · *Advanced · MCP*
- **Task:** Use the **Wiz MCP** to pull live data — e.g. recent critical issues or your
  security score. Getting real data back is the whole win.
- **Hint:** The Wiz tools (`mcp__wiz__*`) are already wired up. Just ask for the data;
  the AI makes the call for you.
- **Bonus:** Hand the results to a subagent for analysis, then wrap the flow in a skill.
- **Done when:** live Wiz data lands in your session. **Write it up and save it as
  `insight.md`** in your project folder so it's auto-collected at submit time.

### Card 5 — Security Review Showdown · *Advanced · everything*
- **Task:** Point an AI security review at **OWASP Juice Shop** (cloned to `./juice-shop`
  in Step 1). Run a quick baseline, then **beat it**: sharper prompts, better context,
  subagents per area. Compare findings.
- **Hint:** Juice Shop is "obvious" on purpose — the variable is *you*. Try route-by-route
  subagents and feeding only the relevant files. Same tool, different results.
- **Bonus:** Turn your best approach into a reusable `/security-review` skill.
- **Done when:** you can show two runs and explain why one found more. **Save your
  findings as `findings.md`** in your project folder so it's auto-collected.

### Card 6 — Vibe-Code a Site · *Creative · design*
- **Task:** Build a single-page site (a vuln dashboard or "security posture" page) by
  **conversation** — not a template.
- **Hint:** Describe the *vibe*, not the CSS. Then refine: "make it darker, add a Wiz-style
  hero, tighten the spacing." Feed it real Wiz MCP data for bonus realism.
- **Bonus:** Theme it for a specific customer.
- **Done when:** a styled page renders in the browser. **Save it as `site/index.html`**
  in your project folder so it's auto-collected.

## Step 4 — Submitting

When you've done what you can, submit. Just say **"submit my work"** — the
`submit-to-scoreboard` skill finds your artifacts and session logs and uploads them
under your team name. If it can't find a file, it'll ask you where it is.

**Save your work with these names/locations so it's auto-collected** (work in one
project folder for the whole lab):

| Card | Save as |
|------|---------|
| 3 — Skill | `.claude/skills/<name>/SKILL.md` |
| 4 — Insight | `insight.md` |
| 5 — Findings | `findings.md` |
| 6 — Website | `site/index.html` (a single `index.html` also works) |
| Session logs | picked up automatically from `~/.claude/projects/` |

If you named something differently, no problem — the submit skill will ask for the
path.

## How you're scored (so you know what to aim for)

Points reward **demonstrated technique, not polish** — a clean beginner can out-score
a brute-forcer. Used a subagent? Called the Wiz MCP? Built a reusable skill? Kept your
context lean? That's what counts. Three awards run alongside the total: **Most Efficient**,
**Best Skill**, **Best SE Workflow**.

## Your job as guide

- Get them through the pre-flight cleanly — that's the real failure point.
- Offer the next card when they finish one; don't front-load everything.
- Give a Hint only after an honest attempt or on request.
- If they're stuck on setup, unblock fast; if they're flying, point them at the bonuses.
