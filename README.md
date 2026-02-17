# Swiftagent

Multi-agent task orchestration with local LLM support. Run coding agents on your machine for free, or use cloud APIs when you need more power. Includes a .NET MAUI control panel for monitoring.

---

## Quick Start -- Local on macOS (Apple Silicon)

This is the fastest path. Three commands, no API keys, no Docker, completely free.

### 1. Install Ollama and Python deps

```bash
# Install Ollama (runs natively on Apple Silicon with Metal GPU acceleration)
brew install ollama

# Install Python dependencies
cd OpenClaw
pip install -r requirements.txt
```

### 2. Start Ollama and pull a model

```bash
# Start the Ollama server (runs in background)
ollama serve &

# Pull a model -- pick ONE based on your Mac:
ollama pull llama3.1:8b          # 32GB Mac (recommended default)
```

### 3. Run OpenClaw

```bash
python -m OpenClaw --local --local-model llama3.1:8b
```

That's it. OpenClaw is now running locally with zero API costs.

### Which model should I pick?

For a Mac with **32GB unified memory** (M2/M3/M4):

| Model | Memory Used | Speed | Best For |
|-------|------------|-------|----------|
| `llama3.1:8b` | ~8 GB | Fast | Day-to-day coding tasks (start here) |
| `codellama:13b` | ~10 GB | Good | Code generation and refactoring |
| `llama3.1:70b-q4_0` | ~26 GB | Slow | Complex reasoning (uses most of your RAM) |
| `llama3.2:3b` | ~4 GB | Very fast | Quick tasks, running alongside other apps |

> With 32GB you can comfortably run 8B-13B models while keeping other apps open. The 70B quantized model works but will use most of your memory.

### Run a specific task

```bash
python -m OpenClaw --local --local-model llama3.1:8b --task "Write unit tests for auth.py"
```

### Scan for improvements (read-only)

```bash
python -m OpenClaw --local --local-model llama3.1:8b --scan-only
```

---

## Quick Start -- Cloud (Anthropic Claude API)

If you want the highest quality output and don't mind API costs:

```bash
cd OpenClaw
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...
python -m OpenClaw
```

### Mix local and cloud

Use local for routine work, cloud for hard problems:

```bash
# Free -- local LLaMA for everyday tasks
python -m OpenClaw --local --local-model llama3.1:8b

# Paid -- Claude API for complex architecture work
export ANTHROPIC_API_KEY=sk-ant-...
python -m OpenClaw --task "Design the authentication system"
```

---

## Adding Coding Agents

OpenClaw can delegate sub-tasks to other coding agents. All are free and open-source. Start with the easiest one and add more as needed.

### Aider -- easiest to set up

AI pair programmer. Edits files safely through git (auto-commits, easy rollback). Does not run shell commands. Works with any LLM including your local Ollama.

```bash
pip install aider-chat
python -m OpenClaw --local --local-model llama3.1:8b --enable-aider
```

> Aider is the safest delegated agent -- it only edits files, never runs arbitrary commands, and every change is a git commit you can revert.

### Goose

Autonomous dev agent by Block. Runs entirely locally, supports 25+ LLM providers including Ollama.

```bash
# macOS
brew install block/goose/goose

python -m OpenClaw --local --local-model llama3.1:8b --enable-goose
```

### Claude CLI

Anthropic's CLI agent. Requires an Anthropic API key.

```bash
npm install -g @anthropic-ai/claude-code

export ANTHROPIC_API_KEY=sk-ant-...
python -m OpenClaw --enable-claude-cli
```

### Codex CLI

OpenAI's sandboxed coding agent. OS-level sandboxing (macOS Seatbelt). Requires an OpenAI API key.

```bash
npm install -g @openai/codex

export OPENAI_API_KEY=sk-...
python -m OpenClaw --enable-codex
```

### Cline

Autonomous multi-step agent. Plans, executes, and self-corrects. Supports local models via Ollama.

```bash
npm install -g cline

python -m OpenClaw --local --local-model llama3.1:8b --enable-cline
```

### Enable multiple agents at once

```bash
python -m OpenClaw --local --local-model llama3.1:8b \
  --enable-aider --enable-goose --enable-cline
```

OpenClaw will delegate sub-tasks to whichever agent is best suited for the job.

---

## MAUI Control Panel (Optional)

The .NET MAUI app gives you a GUI dashboard for monitoring agents, creating tasks, and viewing logs. This is optional -- OpenClaw works fine from the CLI alone.

### Prerequisites

| Component | Install |
|-----------|---------|
| .NET SDK 8.0+ | https://dotnet.microsoft.com/download |
| MAUI workload | `dotnet workload install maui` |
| Xcode 15+ (macOS) | App Store |

### Build and run

```bash
cd AgentUI
dotnet restore
dotnet build -f net8.0-maccatalyst
dotnet run -f net8.0-maccatalyst
```

Other platforms:

```bash
# Windows
dotnet build -f net8.0-windows10.0.19041.0 && dotnet run -f net8.0-windows10.0.19041.0

# iOS (from macOS)
dotnet build -f net8.0-ios && dotnet run -f net8.0-ios

# Android
dotnet build -f net8.0-android && dotnet run -f net8.0-android
```

The app has 7 pages: Dashboard, Tasks, Agents, Skills, Console, Safety & Cost, and Settings. It communicates with OpenClaw by polling `openclaw_status.json` and tailing `openclaw.log`.

---

## Ollama on Linux/Windows (Docker)

If you're not on macOS or prefer Docker:

```bash
# Start Ollama via Docker
docker compose up -d

# Pull a model
docker compose exec ollama ollama pull llama3.1:8b

# Run OpenClaw
cd OpenClaw
pip install -r requirements.txt
python -m OpenClaw --local --local-model llama3.1:8b
```

**GPU notes:**
- **NVIDIA**: Works out of the box (requires `nvidia-container-toolkit`)
- **AMD**: Edit `docker-compose.yml` -- uncomment the AMD section, comment out NVIDIA
- **CPU only**: Remove the `deploy` section (inference will be slower)
- **Apple Silicon**: Don't use Docker -- install Ollama natively with `brew install ollama` for Metal GPU acceleration. Docker on Mac runs in a VM and cannot access the GPU.

---

## All CLI Options

```
python -m OpenClaw [OPTIONS]

Core:
  --task TEXT              Run a specific task instead of the backlog loop
  --scan-only             Scan for improvements without modifying code
  --dry-run               Plan but don't execute file writes or commits

Model:
  --local                 Use local LLM via Ollama (free, no API key needed)
  --local-model TEXT      Model name (e.g. llama3.1:8b, codellama:13b)
  --local-api-base TEXT   Ollama API URL (default: http://localhost:11434/v1)
  --model TEXT            Override model (cloud mode)
  --budget FLOAT          Daily budget in USD (cloud mode)

Agents:
  --enable-aider          Enable Aider (easiest -- pip install aider-chat)
  --enable-goose          Enable Goose (brew install block/goose/goose)
  --enable-claude-cli     Enable Claude CLI (needs Anthropic API key)
  --enable-codex          Enable Codex CLI (needs OpenAI API key)
  --enable-cline          Enable Cline (npm install -g cline)

Advanced:
  --max-iterations INT    Max task iterations before stopping
```

---

## Creating Tasks

Tasks live in `BACKLOG.md`. Create them from the MAUI app, the CLI, or by editing the file directly:

```markdown
- [ ] [P1] [Backend] Implement user authentication @agent:openclaw
- [ ] [P2] [Frontend] Add dark mode toggle @agent:aider
- [ ] [P3] [Tests] Write unit tests for auth module @agent:cline
```

Priority: `[P1]` High, `[P2]` Medium, `[P3]` Low

Agent assignment: `@agent:openclaw`, `@agent:claude`, `@agent:goose`, `@agent:aider`, `@agent:codex`, `@agent:cline`

---

## Configuration Reference

All settings can be set via environment variables instead of CLI flags:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | -- | Claude API key (cloud mode only) |
| `OPENCLAW_PROVIDER` | `anthropic` | `anthropic` or `local` |
| `OPENCLAW_MODEL` | `claude-sonnet-4-5-20250929` | Model name |
| `OPENCLAW_WORKSPACE` | Parent of OpenClaw dir | Workspace root |
| `OPENCLAW_BUDGET` | `5.00` | Daily budget in USD |
| `OPENCLAW_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `OPENCLAW_DRY_RUN` | `false` | Plan without executing |
| `OPENCLAW_LOCAL_API_BASE` | `http://localhost:11434/v1` | Ollama API URL |
| `CLAUDE_CLI_ENABLED` | `false` | Enable Claude CLI |
| `CLAUDE_CLI_PATH` | `claude` | Path to binary |
| `GOOSE_ENABLED` | `false` | Enable Goose |
| `GOOSE_PATH` | `goose` | Path to binary |
| `AIDER_ENABLED` | `false` | Enable Aider |
| `AIDER_PATH` | `aider` | Path to binary |
| `CODEX_ENABLED` | `false` | Enable Codex CLI |
| `CODEX_PATH` | `codex` | Path to binary |
| `CLINE_ENABLED` | `false` | Enable Cline |
| `CLINE_PATH` | `cline` | Path to binary |

---

## Architecture

```
Swiftagent/
├── OpenClaw/          # Python agent orchestrator (Claude / local LLM)
│   ├── agent.py       # Main OODA loop + multi-agent coordination
│   ├── config.py      # Configuration (workspace, budget, models, agents)
│   ├── providers.py   # LLM provider abstraction (Anthropic + Ollama)
│   ├── safety.py      # Safety guardrails (sandboxing, command filtering)
│   ├── prompts/       # System prompts
│   └── skills/        # 14 tool definitions + executor
│
├── AgentUI/           # .NET MAUI control panel (optional)
│   ├── Models/        # Data models
│   ├── Services/      # Agent service layer
│   ├── ViewModels/    # MVVM view models
│   └── Views/         # 7 XAML pages
│
├── docker-compose.yml # Ollama via Docker (Linux/Windows)
├── BACKLOG.md         # Task queue
└── README.md
```

## Safety

- Commands sandboxed to workspace directory
- Blocked: `sudo`, `rm -rf /`, `chmod`, device writes, process kills
- Allowed: git, python, node, docker, go, cargo, make, curl, and delegated agents
- File size limit: 1 MB per file, 100 files per session
- Safe delete: files moved to `.openclaw_trash/` instead of permanent deletion
- Daily budget enforcement stops the agent when limit is reached

---

## Current Status

### What works today

| Component | Status | Notes |
|-----------|--------|-------|
| OpenClaw agent loop | Working | Local (Ollama) and cloud (Anthropic) |
| All 14 skills | Working | File ops, git, shell, search, delegation |
| Multi-agent delegation | Working | Aider, Goose, Claude CLI, Codex, Cline |
| Safety guardrails | Working | Command filtering, sandboxing, budget |
| MAUI dashboard | Working | Reads `openclaw_status.json` and logs |
| Backlog management | Working | BACKLOG.md parsed and written by agent |
| Cost/budget tracking | Working | Daily totals, stops at limit |
| Python test suite | Working | ~2,400 lines covering core agent logic |

### Known issues (fix before relying on this in production)

**P1 — Will cause failures:**
- **Local LLM response validation**: Local models (Ollama) can return empty or malformed responses. `response.content` is accessed without checking, which will raise an exception mid-task. Tracked in BACKLOG.md.
- **Unbounded context growth**: `self.conversation` grows indefinitely during long tasks. On models with a 4K–8K context window (common with smaller local models), this will cause the API call to fail mid-task. Tracked in BACKLOG.md.

**P2 — Security and reliability:**
- **Shell injection in `agent_delegate`**: Task strings are passed into subprocess shell commands with quoting only. Shell metacharacters in a task title can break out of the quote. Tracked in BACKLOG.md.
- **No health monitoring**: There is no heartbeat file or endpoint. External systems (including the MAUI UI) cannot distinguish a running agent from a crashed or hung one. Tracked in BACKLOG.md.
- **MAUI shows stale data silently**: The dashboard does not show an error when `openclaw_status.json` is missing or old — it just displays the last-known values as if the agent is live. Tracked in BACKLOG.md.

---

## Next Steps

Priority order to make this production-ready:

### 1. Fix P1 critical issues (do these first)

```bash
# These three items in BACKLOG.md:
# - Validate LLM response structure before accessing fields
# - Add conversation context pruning
# - Add MAUI UI unit tests for ViewModels and Services
python -m OpenClaw --task "Fix P1 backlog items"
```

**Validate LLM responses** — wrap `response.content` access in a guard that checks for empty or unexpected structures and retries or surfaces a clear error.

**Prune conversation context** — before each API call, trim `self.conversation` to keep the last N turns plus the system prompt, keeping total tokens under the model's context limit.

### 2. Fix the shell injection in agent_delegate (P2 security)

Task strings passed to `subprocess` should be sanitized with `shlex.quote` or restructured to use list-form subprocess args instead of shell string interpolation.

### 3. Add a heartbeat file (P2 reliability)

Write a `openclaw_heartbeat.json` with a timestamp every N seconds. The MAUI UI (and any external monitor) can check this file to know whether the agent is actually alive.

### 4. Add structured JSON logging (P2 observability)

Replace the current plain-text `openclaw.log` with newline-delimited JSON. This makes it trivial to grep for errors, feed logs into dashboards, or write alerting rules.

### 5. Test coverage gaps (P2/P3)

- **MAUI ViewModels**: Currently zero test coverage. The VM layer contains non-trivial business logic.
- **SwiftTamagotchi**: GameLogic and SaveManager have no XCTest coverage.

### 6. Distribution guides (P3)

No documentation exists for building release artifacts — `.app` bundles for MAUI on macOS, `.ipa` for iOS, or packaging OpenClaw as a standalone binary. Add a `docs/` directory with platform-specific guides.

---

### Quick checklist before using in anger

- [ ] Run `pytest OpenClaw/tests/` — all tests should pass
- [ ] Try a dry run: `python -m OpenClaw --dry-run --task "refactor foo.py"`
- [ ] Verify your Ollama model responds: `ollama run llama3.1:8b "hello"`
- [ ] Check the BACKLOG.md P1 items are addressed if running long tasks
- [ ] Set a `--budget` limit so a runaway agent can't rack up API costs
