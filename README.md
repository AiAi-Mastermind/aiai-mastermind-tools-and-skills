# AiAi Mastermind — Tools & Skills

A public collection of shareable [Agent Skills](https://agentskills.io) for Claude Code (and other agents like Codex, Gemini, Aider, Cursor). Drop them into your agent and go.

## Skills

### 🧠 [`wiki-llm`](skills/wiki-llm) — build a compounding knowledge wiki from your documents

Turn a folder of source documents (books, PDFs, papers, articles, transcripts) into a **persistent, interlinked Obsidian knowledge base maintained by an LLM** — the opposite of RAG. The LLM reads each source once and *compiles* it into cross-referenced markdown pages that sit between you and the raw sources, so the synthesis and contradictions are already there and the wiki gets richer with every source you add.

Implements [Andrej Karpathy's `llm-wiki` idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Domain-agnostic — works for research, a company knowledge base, a single book, a hobby deep-dive, or a business.

It ships with:
- the three-layer **RAW → WIKI → OUTPUT** architecture and the hard extraction-vs-editorial boundary,
- a domain-agnostic schema template (`CLAUDE.md.template`) + five page templates (source / author / concept / framework / synthesis),
- ready-to-drop `.obsidian/` config — graph color groups, properties, and a CSS snippet that color-codes page types in note view,
- the **parallel-ingestion fan-out pattern** for ingesting dozens of sources at once,
- the **raw-traceback protocol** (page-cited quotes that trace back to the original file).

### 🖼️ [`gpt-image`](skills/gpt-image) — generate images from Claude Code using your ChatGPT subscription (no API key)

Let Claude Code create images (hero shots, product mockups, illustrations, icons, textures) by delegating to **Codex CLI's built-in `image_gen` tool** over your **ChatGPT OAuth login** — no `OPENAI_API_KEY`, no per-image API billing. The core insight: a ChatGPT OAuth token is *not* an API key (the Images API returns `401 missing scope` on it), so the skill routes every request through Codex's built-in tool instead of the API.

It enforces the things that are easy to get wrong:
- **OAuth, not API** — built-in `image_gen` via the signed-in ChatGPT session, never a raw API call.
- **One copy on disk** — `mv` (never `cp`) each output out of Codex's cache, so generated images never silently duplicate.
- absolute output paths, one call per image, a network-enabled sandbox, and a fill-in-the-blanks brief template for any use case.

Auto-triggers on "generate / create / make an image"; also ships an optional `/gpt-image` slash command. Requires the Codex CLI installed and signed in to ChatGPT.

### 📸 [`generate-me`](skills/generate-me), generate images of yourself while preserving your real facial identity

A **blank, personalizable template** for generating images of the skill owner across photoreal, illustrated, cartoon, cinematic and stylized scenes. It intentionally ships with no photos and no personal details. Point Claude Code, Codex or another coding agent at it, and the agent customizes it for the member: it sorts about five photos into identity slots, writes an identity profile from what it observes, runs a test image and grades it. Setup takes about fifteen minutes.

It ships with:
- three generation paths: an OpenAI image model through the model-router, a Google Gemini image model through the same router, and the Codex CLI built-in image tool as a fallback when no router is available,
- a bundled health check that reports which generation paths are available,
- parallel router generation that sends the same prompt to both image models at the same time, producing two versions to compare without running them one after another,
- a fully agent-runnable setup with step-by-step instructions in [`SETUP.md`](skills/generate-me/SETUP.md).

### 🔀 [`model-router`](skills/model-router) — run Claude Code builds on the subscriptions you already pay for

Adds a local "switchboard" ([CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI)) that holds your OTHER subscription logins — ChatGPT, Gemini, Grok, Kimi — so Claude Code can send work to those models with **no API keys and no per-token bills**. Repackages the [RoboNuggets model-router plugin](https://github.com/robonuggets/model-router) (CC BY 4.0) with a one-command installer.

What you get after install:
- **`/fabsol <brief>`** — the flagship flow: Claude plans, specs, and verifies while GPT-5.6 Sol does 100% of the building (≈33% cheaper than Claude building alone in the upstream benchmark),
- **`/sol <task>`** — one-shot any task on the routed model from inside a normal Claude session,
- **`/codex-usage`** — your ChatGPT/Codex weekly limit bars (percent used, reset times) without leaving Claude Code,
- **SolFab** — the reverse direction: say `solfab: <brief>` in Codex (ChatGPT app / VSCode) and it hands the brief to Claude, which orchestrates while Sol builds — remote build dispatch from your phone,
- full routed sessions via `scripts/session.sh` / `scripts/vscode.sh`.

Your Claude login never touches the proxy (that keeps you inside Anthropic's terms), and all logins stay on your machine. Setup is agent-runnable: see the install prompt below.

### 📊 [`gam-campaign-checkup`](skills/gam-campaign-checkup) — is my Google Ads campaign actually working?

Turns Claude into a **Google Ads campaign evaluation coach for captive insurance agents**, built from the AiAi Mastermind *Google Ads Mastery Deep Dive* workshop. For agents whose campaign is already launched: upload your Google Ads screenshots/CSV and your carrier campaign-report export, and Claude walks the workshop's belt progression — find your six numbers, compute **Cost Per Quote** and **Cost Per Acquisition**, get a **Green / Yellow / Red Signal Light**, diagnose search-term waste and competition, and commit to **one** tuning move for the week.

What makes it different from asking Claude about Google Ads cold:
- every benchmark and decision rule comes from the curated workshop methodology (transcribed live teaching + real coaching calls), not generic internet ad advice,
- it refuses to grade a campaign on clicks and impressions — spend, leads, and households are the only scoreboard,
- it never drifts into campaign *setup* territory; it evaluates and tunes what's already installed,
- one action per cycle, with a date — the way the workshop actually coaches it.

Web-first: this one is designed for **claude.ai** — upload [`gam-campaign-checkup.zip`](skills/gam-campaign-checkup/gam-campaign-checkup.zip) under Settings > Capabilities > Skills (see the [skill README](skills/gam-campaign-checkup/README.md)). It also works as a Claude Code skill folder.

## Install

**Tip:** You can grab a single skill folder instead of cloning the whole repository:

```bash
curl -L https://github.com/AiAi-Mastermind/aiai-mastermind-tools-and-skills/archive/refs/heads/main.tar.gz | tar -xz --strip-components=2 '*/skills/generate-me'
```

Swap the skill name at the end of that command to grab any skill in this repository.

**Claude Code** (personal skills):

```bash
git clone https://github.com/AiAi-Mastermind/aiai-mastermind-tools-and-skills.git

# wiki-llm
cp -R aiai-mastermind-tools-and-skills/skills/wiki-llm ~/.claude/skills/wiki-llm

# gpt-image (+ optional /gpt-image slash command)
cp -R aiai-mastermind-tools-and-skills/skills/gpt-image ~/.claude/skills/gpt-image
cp aiai-mastermind-tools-and-skills/skills/gpt-image/gpt-image.command.md ~/.claude/commands/gpt-image.md

# generate-me
cp -R aiai-mastermind-tools-and-skills/skills/generate-me ~/.claude/skills/generate-me

# gam-campaign-checkup (claude.ai users: upload the zip instead — see its README)
cp -R aiai-mastermind-tools-and-skills/skills/gam-campaign-checkup ~/.claude/skills/gam-campaign-checkup
```

Then just ask: *"build a wiki LLM from these PDFs"* or *"generate a hero image of …"* and the matching skill activates. (`gpt-image` needs the Codex CLI installed and signed in to ChatGPT via `codex login`.)

**Other agents:** copy the skill folder into your agent's skills directory (e.g. `~/.agents/skills/` for Codex), or point your agent at `skills/wiki-llm/SKILL.md`.

**model-router** is a full setup, not a copy-paste skill — paste this into Claude Code and it does the rest (one browser sign-in needed):

```
Clone https://github.com/AiAi-Mastermind/aiai-mastermind-tools-and-skills and follow
skills/model-router/INSTALL.md to set up FabSol. Do every step yourself, and tell
me when you need me to approve the browser sign-in.
```

## Browser research skills (Mac only)

Five skills that let Claude Code or Codex do research with the consumer subscriptions you already pay for, instead of paid APIs. Each one drives a real website inside **Agent Chrome**, a separate signed-in browser just for your agents, and returns cited, dated results your agent can use.

| Skill | What it does |
|---|---|
| [`perplexity-browser`](skills/perplexity-browser) | Perplexity Search or Deep research, always in Incognito with a neutral preface so your personal profile doesn't shape the answer |
| [`grok-browser`](skills/grok-browser) | What people are saying on X (Twitter), through Grok in Private Chat, with each post's link and date checked |
| [`muse-browser`](skills/muse-browser) | **Experimental.** Facebook groups and Instagram trends, by asking Meta's own AI agent Muse in a fresh side chat |
| [`facebook-personal-browser`](skills/facebook-personal-browser) | Reads a few specific Facebook posts on your own account, strictly read-only and slowly |
| [`last30days-plus`](skills/last30days-plus) | Runs the open-source [last30days](https://github.com/mvanhorn/last30days-skill) research skill and adds the X, web and Facebook/Instagram lanes above |

Safety rules built into every one of them:
- Research questions only. Never client names, customer or policy data, or private files.
- Isolation first: Perplexity runs only in Incognito, Grok only in Private Chat, Muse only in a fresh side chat. If the driver can't prove isolation, it sends nothing.
- Agents never type passwords or solve sign-in, code or captcha screens. They stop and ask you.
- Facebook is read-only and paced. Any checkpoint screen stops all Facebook work for the day.
- Everything a site returns is treated as untrusted content, never as instructions.
- Personal volume only: one research job at a time, a handful a day, no loops. These are consumer subscriptions with their own terms.

Known limits: `muse-browser` is experimental (its side-chat isolation check failed in testing on 2026-10-07, so it may refuse to run until updated). Perplexity changes its Deep research toggle often; if a Deep research run returns `ui_changed` or only a few sources, follow the "Drive it yourself" steps in `perplexity-browser`.

### What you need

- A Mac. These skills do not work on Windows or Linux.
- The **[aiai-agent-chrome](https://github.com/AiAi-Mastermind/aiai-agent-chrome)** kit, installed and running (`~/.local/share/agent-chrome/bin/agent-chrome doctor` passes).
- Your own accounts, signed in inside the Agent Chrome window: Perplexity (a plan with Deep research for the web lane), Grok (free works) and, for the Meta lanes, Facebook and muse.ai.
- For `last30days-plus`: the upstream last30days skill from https://github.com/mvanhorn/last30days-skill, installed by following that repo's instructions.

### Install for Claude Code

```bash
git clone https://github.com/AiAi-Mastermind/aiai-mastermind-tools-and-skills.git
cd aiai-mastermind-tools-and-skills/skills
for s in perplexity-browser grok-browser muse-browser facebook-personal-browser last30days-plus; do
  cp -R "$s" ~/.claude/skills/"$s"
  chmod +x ~/.claude/skills/"$s"/bin/*
done
```

Then ask in plain words, for example *"Use Perplexity deep research on ..."* or *"Run last30days-plus on ..."*.

### Install for Codex

Copy the same folders into `~/.codex/skills/` (or `~/.agents/skills/`):

```bash
for s in perplexity-browser grok-browser muse-browser facebook-personal-browser last30days-plus; do
  mkdir -p ~/.codex/skills && cp -R "$s" ~/.codex/skills/"$s"
  chmod +x ~/.codex/skills/"$s"/bin/*
done
```

Start Codex with the browser profile the kit created (`codex -p browser`) so it can reach Agent Chrome. The drivers save a private copy of each answer under `~/Library/Application Support/BrowserResearch/runs/`. If Codex's sandbox blocks that folder, add it to the profile's `writable_roots`, or set `BROWSER_RESEARCH_DIR` to a folder Codex can write to.

### Example last30days-plus prompts for insurance agency owners

1. "Run last30days-plus on what homeowners are saying about rising home insurance premiums and non-renewals in California."
2. "last30days-plus with X and Facebook: how are independent and captive insurance agents using AI assistants for quoting and follow-up?"
3. "Use last30days-plus to find what small business owners are asking about commercial auto insurance costs this month."
4. "What are people saying in the last 30 days about life insurance for young families? Use last30days-plus and pull the questions they keep asking."
5. "Run last30days-plus on hurricane and wildfire season claims experiences, focused on what frustrated policyholders most."
6. "last30days-plus: what video and Reel formats are insurance agents posting on Instagram and Facebook that get the most engagement?"
7. "Run last30days-plus on how renters are talking about renters insurance, and list the five objections that come up most."

Your agent sends only the topic to each site. Keep prompts about public topics, never about a specific client.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, share it.

## Starter kits

### `maya-starter/` - Your Automated Social Media Content Team

The complete starter kit for the AIAI Mastermind course "Your Automated Social Media Content Team". It sets up MAYA, the AI agent that runs your content team, with Codex as the copywriter and designer she manages.

Includes: MAYA's standing instructions (CLAUDE.md), a fill-in-the-blanks job description brief, a compliance knowledge-base template, three content-lane skills (newsjacking, problem-solution, entertain), a compliance-check skill, a Mai Marketing Machine posting skill, an image and brand skill, and the brain folder where your My Agency Context document lives.

Setup (covered step by step in the course):

```bash
git clone https://github.com/AiAi-Mastermind/aiai-mastermind-tools-and-skills.git
cp -R aiai-mastermind-tools-and-skills/maya-starter ~/Documents/your-agency-content-team
```

Then open the folder in VS Code, drop your `My_Agency_Context.md` into `brain/`, and follow `JOB-DESCRIPTION.md`.
