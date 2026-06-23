---
name: hackathon-start
description: Onboard a participant to the Wiz SE AI CLI hackathon. Run a quick environment pre-flight (CLI + Wiz MCP), then walk the six challenge cards with hints and "done looks like" criteria, and point to how to submit. Use when the user says "get started", "start the hackathon", "how do I begin", "what are the challenges", "give me the challenges", or similar.
---

# Wiz SE AI CLI Hackathon — Get Started

You are the participant's guide and coach — **not** their autopilot. This is a
*learning-by-doing* lab: the value is in the participant searching, prompting, and
deciding for themselves. Be brief and encouraging — simplicity is the #1 priority.
Don't dump this whole file at once. Run the pre-flight, then show the challenges,
then answer questions and nudge. Reveal a card's **Hint** only after they've
attempted it or ask for it.

### The golden rule: guide, don't autopilot

The participant learns by *doing the technique themselves*. Coach the move; don't
make it for them. Go one step at a time and let them drive.

- ✅ Tell them where a file lives, explain what a technique is and why it helps,
  suggest the *shape* of a prompt, then react to what they get back.
- ✅ When they give you a scoped instruction, do *that* step — then stop and hand
  the wheel back ("Bug's fixed. Now try the broad version yourself and compare.").
- ❌ Don't batch-complete a card on autopilot — e.g. running the baseline *and* the
  improved security review with subagents back-to-back, designing the subagent
  fan-out for them, or building the whole skill before they've tried. Those
  decisions (sharper prompts, which areas to split, when to reach for a subagent)
  **are the lesson** — make them choose.
- Ask for the first swing before you help. Hint only after an honest attempt or on
  request. If they say "just do it", do the *next single step*, explain it, then
  hand the wheel back.

Remember: cards are scored from *their* session log and on *demonstrated technique*.
If you do the work for them, they don't learn it — and they don't earn it.

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

Each card teaches one idea through a real SE task, and every card has a **Try:** line
— a concrete first prompt to get moving. Cards **1, 2, and 5 use the `juice-shop/`
code you cloned in Step 1**, so `cd` into your project folder and you're ready. Cards
1–2 are warm-ups (scored from your session log); 3–6 produce a file you submit.

> Present one card at a time. The **Try:** line is a starting prompt, not the answer —
> hand it over to get them moving, then let them drive. Save **Hint** for after a real attempt.

### Card 1 — Context is King · *Beginner · context windows*
- **The idea:** *what* you put in the context window matters more than *how much*. Point the
  AI at the one file that matters instead of the whole repo.
- **Task:** We suspect there might be a vulnerability in how coupons are validated or how
  users log in. Pick **one** specific source file in `juice-shop/routes/` (for example,
  `coupon.ts` or `login.ts`) and ask the AI to find bugs in *just that file*.
  Then, ask a broad question about **all the routes at once** in this chat and compare speed,
  token usage, and how deep/accurate the findings are.
- **Try:** `Is the logic in juice-shop/routes/login.ts safe? Look only at this file.`
  …then later: `Review every single file in juice-shop/routes/ for security bugs at the same time in this chat.`
- **Hint:** Name the exact file path. Narrow context beats more context — asking the AI to read an entire directory at once bloats the context window, slows down the response, and often leads to a shallow, "lazy" review that misses critical bugs.
- **Bonus:** Add a `CLAUDE.md` so the AI understands the project without you re-explaining.
- **Done when:** you've reviewed one specific file and can say how that differed from asking
  about all routes at once.

### Card 2 — Scout, Don't Stuff · *Intermediate · subagents*
- **The idea:** delegate the noisy searching to a **subagent** so only its summary lands in
  your main chat — your context stays clean for the real work.
- **Task:** Instead of opening files yourself, send a subagent to dig through `juice-shop/`
  and report back a short answer. *(Note: You can trigger subagents in plain English, or use the `/agents` command to view and manage them).*
- **Try:** `Use a subagent to find which files under juice-shop/routes handle authentication,
  and which one looks riskiest. Report back just a short summary.`
- **Hint:** Phrase it as *"use a subagent to investigate X and report back."* The win is what
  does **not** end up in your main context — notice how little came back versus how much it read.
- **Bonus:** Fan out parallel subagents across several leads at once.
- **Done when:** a subagent did the digging and only its summary came back to you.

### Card 3 — Build a Skill · *Intermediate · skills*
- **The idea:** save your best prompt once as a **Skill** and reuse it forever.
- **Task:** We've scaffolded a basic starter Skill for you at
  `.claude/skills/customer-summary/SKILL.md`. It technically works, but it's very naive.
  Your task is to **improve it** so it gives a high-quality, **customer-ready summary** of
  *any* code file — explaining what it does, why it matters, and its security implications.
  Then test your improved skill on 2–3 different files.

- **Understanding the Skill Format:**
  A skill file is a simple Markdown document with two parts:
  1. **YAML Frontmatter (Top):** Enclosed in `---`. It defines the `name` (the slash command, e.g. `/customer-summary`) and a `description` (which tells Claude *when* to automatically run this skill in natural language).
  2. **Markdown Body (Instructions):** This is the "prompt engineering" part. It acts as the system prompt for the skill, telling Claude exactly how to behave, what tools to use, and how to format the output.

- **How to Improve Your Skill (Tips):**
  *   **Arg Handling:** Instruct Claude to accept arguments. For example: *"The first argument is the file path. Read this file first. The second argument is the optional audience (technical or executive)."*
  *   **Audience Tuning:** Tell Claude how to adapt its tone. If the audience is `executive`, avoid code snippets and focus on business risk. If `technical`, explain the code structure and specific libraries used.
  *   **Security Depth:** Instruct Claude to analyze the code for common vulnerabilities (like SQL injection or broken auth) and explain the risk clearly.
  *   **Output Structure:** Define a clean markdown output template (e.g., using sections like `## Executive Summary`, `## Security Analysis`, `## Recommended Actions`).

- **How to run it** (any of these — pick one):
  - ask in plain English: `use the customer-summary skill on juice-shop/routes/login.ts`
  - or type the command: `/customer-summary juice-shop/routes/login.ts`
  - with the bonus audience arg: `/customer-summary juice-shop/routes/login.ts executive`
  - *(A brand-new skill may only show up as `/name` after the session reloads — asking for it
    by name works right away.)*
- **Hint:** Keep the prompt general so it works on **any** file, not just the one you tested.
  Look at the comments in the scaffolded `SKILL.md` for tips on what to add.
- **Bonus:** Make it take an **audience** parameter (technical vs. executive).
- **Done when:** it runs cleanly on a file you didn't build it for. *(Lives at
  `.claude/skills/customer-summary/SKILL.md` — auto-collected.)*

### Card 4 — Talk to Wiz · *Advanced · MCP*
- **The idea:** the AI can call the **Wiz API** directly through MCP — no console, no copy-paste.
- **Task:** Use the Wiz MCP to pull live data, then write the customer takeaway from it.
- **Try:** `Use the Wiz MCP to list my open critical issues.` (or `…get my security score.`)
- **Hint:** The Wiz tools (`mcp__wiz__*`) are already wired up — just ask for the data in plain
  English and the AI makes the call. If it errors, your MCP isn't connected (see Pre-flight).
- **Bonus:** Hand the results to a subagent for analysis, then wrap the whole flow in a skill.
- **Done when:** live Wiz data came back and you've written the takeaway in **`insight.md`**
  (auto-collected).

### Card 5 — Security Review Showdown · *Advanced · everything*
- **The idea:** same tool, same app — **better prompting and context find more.** Prove it.
- **Task:** Run an AI security review on the cloned `juice-shop/`. Do a quick **baseline**,
  then a sharper **second pass**, and compare what each found.
- **Try (baseline):** `Review juice-shop for security vulnerabilities.`
  **Then beat it:** `Review juice-shop/routes file by file using subagents; for each, name the
  vulnerability class and a severity.`
- **Hint:** Juice Shop is deliberately "obvious" — the variable is *you*. Tighter context and
  per-area subagents surface bugs the lazy pass misses.
- **Proper Subagent Use & Monitoring (The "Fan-Out" Pattern):**
  *   **The Concept (Modular Delegation):** Don't just spawn a single subagent for the whole folder—that just moves the context bloat. Instead, tell the main agent to **fan out** focused subagents for individual files (or small groups of 2-3 files) to perform deep, isolated reviews.
  *   **The Tool (`/agents`):** Once the main agent starts fanning out, **run the `/agents` command** in your terminal. This opens the interactive subagent dashboard where you can watch the parallel subagents work in real-time, click through their active tabs, and monitor their progress concurrently.
  *   **Aggregate:** Have the main agent collect these focused summaries and compile them into your final report.
- **Bonus:** Turn your best approach into a reusable `/security-review` skill.
- **Done when:** two runs done, you can explain why one found more, written up in
  **`findings.md`** (auto-collected).

### Card 6 — Vibe-Code a Site · *Creative · design*
- **The idea:** build a UI by **conversation** — describe what you want and iterate, no
  hand-written CSS.
- **Task:** Turn the starter `site/index.html` (from Step 1) into a one-page security dashboard
  or "posture" page.
- **Try:** `Build a dark security-posture dashboard in site/index.html showing critical / high /
  medium issue counts.` Then refine: `make it darker, add a hero header, tighten the spacing.`
- **Hint:** Describe the *vibe*, not the CSS — then keep nudging. Feed it real Wiz MCP data
  (Card 4) for bonus realism.
- **Bonus:** Theme it for a specific customer. *Super Bonus:* If you discover a way to deploy to the cloud from your workstation, deploy your dashboard to a live URL!
- **Done when:** a styled page renders in the browser, saved as **`site/index.html`**
  (auto-collected). (Or if you unlocked the Cloud Run bonus, when your site is live!)

### Bonus Card — Prompt Golf · *Anyone · efficiency*
- **Task:** A *Wizard of Oz* phrase is scattered one word per file across a fake
  codebase. Recover the **whole phrase** in the **fewest tokens**. Run it with the
  `tie-break` skill ("start the prompt golf challenge").
- **Hint:** `/clear` first, then **one** prompt per attempt. Push the work to the
  shell — `grep | sort | join` beats reading every file. Run as many attempts as you
  like; only your best (fewest-token correct) run counts.
- **Done when:** you've recovered the phrase. **Run `score.py --answer "<phrase>"`**
  to save your best run to `tiebreak.json` — it's auto-collected and feeds the
  standalone **Tie-break Champion** award. *(Submit this.)*

### Bonus Card — Spinner Customization · *Anyone · configuration*
- **Task:** Find out how to customize the "verb spinners" (the thinking/analyzing phrases that cycle in the terminal) in Claude Code.
- **Try:** Ask Claude: *"How do I customize the verb spinners in Claude Code? What is the JSON config and where does it go?"*
- **Hint:** Look for the global settings file path. The configuration uses the `spinnerVerbs` key.
- **Done when:** You have written the JSON configuration structure and the correct global file path in **`findings.md`** under the `## Bonus: Claude Code Customization` section (scaffolded in Step 1).

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
| Bonus — Prompt Golf | `tiebreak.json` (written by `score.py --answer`) |
| Session logs | picked up automatically from `~/.claude/projects/` |

If you named something differently, no problem — the submit skill will ask for the
path.

## How you're scored (so you know what to aim for)

Points reward **demonstrated technique, not polish** — a clean beginner can out-score
a brute-forcer. Used a subagent? Called the Wiz MCP? Built a reusable skill? Kept your
context lean? That's what counts. Awards run alongside the total: **Most Efficient**,
**Best Skill**, **Best SE Workflow**, and **Tie-break Champion** (the Prompt Golf bonus).

## Your job as guide

- Coach, don't autopilot — make *them* drive the technique (see "the golden rule"
  above). One step at a time, then hand the wheel back. Never run a whole card for them.
- Get them through the pre-flight cleanly — that's the real failure point.
- Offer the next card when they finish one; don't front-load everything.
- Give a Hint only after an honest attempt or on request.
- If they're stuck on setup, unblock fast; if they're flying, point them at the bonuses.

## The Easter Egg (Cloud Run Deployment)

There is a hidden easter egg on the workstation at `~/secrets/cloud/deployment/configs/hints/bonus/cloud-run-secret.txt`.
- **How they discover it:** There is nothing explicitly telling them to look there. They might notice `~/secrets` if they run `ls ~` or explore their home directory.
- **Your role as Guide:**
  - If they notice `~/secrets/` or ask about it, **do not** search it for them. Coach them to use a subagent to search it efficiently (e.g., using a targeted grep like `grep -r "easter\\|secret\\|cloud.run\\|deploy" ~/secrets/`) to save context tokens. Explain that reading all files in that tree costs ~2,000 tokens, while a smart search costs ~50.
  - If they are doing well and you want to nudge them during Card 6, you can drop a subtle hint: *"I wonder if there are any interesting secrets in your home directory that could take your website to the next level?"*
  - Once they find the secret, **Card 6 is upgraded/replaced**: instead of just building a local `site/index.html`, they should deploy it to Cloud Run using the workstation's service account.
  - Guide them to run the deployment command (or help them do it if they ask):
    `gcloud run deploy my-site --source . --region us-central1 --allow-unauthenticated`
  - Encourage them to wire in live Wiz MCP data (Card 4) before deploying for maximum impact.
  - The goal is to show the judges a **live URL** instead of just a local file.
