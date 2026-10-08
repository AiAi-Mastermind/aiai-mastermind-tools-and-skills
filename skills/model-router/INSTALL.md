# FabSol / model-router — agent install guide

**Audience: the AI agent (Claude Code) doing the install.** If you are a human,
just tell your Claude Code session:

> Clone https://github.com/AiAi-Mastermind/aiai-mastermind-tools-and-skills and follow
> skills/model-router/INSTALL.md to set up FabSol.

## What you are installing

FabSol lets this machine's Claude Code delegate 100% of build work to a model
from another subscription the user already pays for (default: GPT-5.6 via
their ChatGPT plan) — no API keys, no per-token billing. A local proxy
(CLIProxyAPI, open source) holds the other subscription's login; Claude Code
stays on its normal Anthropic login and reaches out through the proxy.

**Safety rule you must respect:** never route the user's Claude/Anthropic
subscription login through the proxy, and never set `ANTHROPIC_BASE_URL` /
`ANTHROPIC_AUTH_TOKEN` in the main session's environment. Routed env vars
belong only on individual headless worker calls. Anthropic's terms ban
subscription OAuth in third-party tools; this design keeps the user compliant.

## Install — macOS / Linux (automated)

From the cloned repo root:

```bash
bash skills/model-router/install.sh
```

The script is idempotent. It downloads the latest CLIProxyAPI release for this
OS/arch (sha256-verified), writes `~/cli-proxy-api/config.yaml` with a
generated local key, installs the `fabsol` + `model-router` skills, `/fabsol`
command, and `worker` agent globally into `~/.claude/`, keeps a full plugin
copy (with helper scripts) at `~/.claude/model-router/`, and appends
`MODEL_ROUTER_*` env vars to the user's shell profile.

## The one human step: subscription sign-in

This opens a browser once; the login is stored locally in `~/.cli-proxy-api`.
Run it and tell the user a browser window needs their approval:

```bash
cd ~/cli-proxy-api && ./cli-proxy-api -config config.yaml -codex-login
```

- `-codex-login` = ChatGPT / Codex (the default worker, `gpt-5.6-sol`)
- Also available: `-antigravity-login` (Gemini), `-xai-login` (Grok),
  `-kimi-login` (Kimi)
- Headless/SSH machine? Use `-codex-device-login` (device-code flow) or add
  `-no-browser` and give the user the printed URL.

Do NOT try to copy or convert existing credential files (e.g. Codex CLI's
`~/.codex/auth.json`) instead of running the login — use the official flow.

## Verify (do all three)

```bash
source ~/.zshrc 2>/dev/null || source ~/.bashrc
bash ~/.claude/model-router/scripts/start-proxy.sh
curl -s "$MODEL_ROUTER_URL/v1/models" -H "Authorization: Bearer $MODEL_ROUTER_KEY"
bash ~/.claude/model-router/scripts/worker.sh "Reply with exactly: routing works"
```

Success = the models list includes `gpt-5.6-sol` and the worker call answers
`routing works`. Then have the user open a fresh terminal (or fully quit and
reopen VSCode — a window reload is not enough to pick up new env vars) and try
`/fabsol build me a small test page`.

## Using the routed model day-to-day

Three commands land in the user's global Claude Code after install:

- `/fabsol <brief>` — the orchestrated build flow (Claude plans/verifies,
  GPT-5.6 Sol builds).
- `/sol <task>` — one-shot: run any quick task or question directly on the
  routed model from inside a normal Claude session. A different model can be
  named in the task ("on terra", "with gemini").
- `/codex-usage` — shows the ChatGPT/Codex weekly limit windows (percent
  used, reset time, per-model extras) pulled from the proxy's Management API.
  Tokens never leave the proxy; the script uses the `$TOKEN$` placeholder
  substituted server-side.

For a WHOLE session on the routed model, use `scripts/session.sh [model]`
(terminal) or `scripts/vscode.sh [folder]` (VSCode window) — the main-session
`/model` picker can only list Anthropic models, so a routed session is
launched from the outside, never by re-pointing an existing session.

## SolFab — dispatch FabSol from Codex / the ChatGPT app (optional)

SolFab is the reverse entry point: Codex (the ChatGPT app, the Codex app, or
the Codex VSCode extension) acts as the remote control. Codex wakes up, hands
the brief to Claude Fable via `scripts/solfab.sh`, Fable orchestrates the
usual fabsol flow, and GPT-5.6 Sol still does the building. Chain:
**Sol → Fable → Sol.** This is what makes remote dispatch from the ChatGPT
mobile app work, with project-directory control Claude's mobile dispatch
doesn't offer.

If `~/.codex` exists when `install.sh` runs, it installs automatically: a
`solfab` skill into `~/.codex/skills/` and a dispatch section appended to
`~/.codex/AGENTS.md`. If the user installs Codex later, re-run `install.sh`.

Verify from any Codex session (CLI, app, or VSCode):

```
solfab: create hello.txt containing exactly 'chain works'
```

Codex should run `solfab.sh` (give it a long timeout — builds take minutes)
and relay Fable's 5-line report. Requirements: Claude Code signed in on its
normal login, plus the proxy setup above.

Note: the Fable orchestrator runs on Claude Code's own direct login — never
through the proxy. That keeps the whole chain within Anthropic's terms.

## Install — Windows

No script; do the equivalent by hand (agent-executable, ~5 minutes):

1. Download the latest `CLIProxyAPI_*_windows_amd64.zip` (or `_aarch64`) from
   https://github.com/router-for-me/CLIProxyAPI/releases and unzip to
   `%USERPROFILE%\cli-proxy-api`.
2. Copy this folder's `proxy/config.example.yaml` there as `config.yaml` and
   replace `my-proxy-key` with a generated value.
3. Copy `skills\fabsol` and `skills\model-router` into `%USERPROFILE%\.claude\skills\`,
   `commands\fabsol.md` into `%USERPROFILE%\.claude\commands\`, and
   `agents\worker.md` into `%USERPROFILE%\.claude\agents\`. Copy this whole
   folder to `%USERPROFILE%\.claude\model-router`.
4. Persist the four env vars (PowerShell):
   ```powershell
   [Environment]::SetEnvironmentVariable("MODEL_ROUTER_URL", "http://127.0.0.1:8317", "User")
   [Environment]::SetEnvironmentVariable("MODEL_ROUTER_KEY", "<your generated key>", "User")
   [Environment]::SetEnvironmentVariable("MODEL_ROUTER_MODEL", "gpt-5.6-sol", "User")
   [Environment]::SetEnvironmentVariable("MODEL_ROUTER_EFFORT", "low", "User")
   ```
5. Sign in: `.\cli-proxy-api.exe -config config.yaml -codex-login`
6. Verify with `scripts\start-proxy.ps1` and `scripts\worker.ps1 "Reply with exactly: routing works"`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` | Proxy not running — `bash ~/.claude/model-router/scripts/start-proxy.sh` |
| Auth error from proxy | Provider login expired — re-run the login flag |
| `Unknown provider for model X` | That provider isn't signed in, or wrong model ID — check `/v1/models` |
| `/fabsol` env vars empty in VSCode | Fully quit VSCode (Cmd+Q) and reopen — reload window is not enough |
| Worker output weak | The spec must carry the thinking; also try `MODEL_ROUTER_EFFORT=medium` |

## Credits & license

This folder repackages the **model-router** plugin by
[RoboNuggets](https://github.com/robonuggets/model-router) (CC BY 4.0 — see
`LICENSE` in this folder) together with install automation by AiAi
Mastermind. CLIProxyAPI is by [router-for-me](https://github.com/router-for-me/CLIProxyAPI)
(MIT). This folder's contents are CC BY 4.0 (the repo itself is MIT).
