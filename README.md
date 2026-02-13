# Swiftagent - Multi-Agent Task Orchestration Platform

A production-ready platform for managing tasks through multiple open-source AI agents, with a cross-platform .NET MAUI control panel for real-time monitoring and task creation. Supports both cloud (Anthropic Claude) and local LLM backends (LLaMA via Ollama) to save on API credits.

## Architecture

```
Swiftagent/
├── OpenClaw/          # Python agent orchestrator (Claude / LLaMA)
│   ├── agent.py       # Main OODA loop + multi-agent coordination
│   ├── config.py      # Configuration (workspace, budget, models, agents)
│   ├── providers.py   # LLM provider abstraction (Anthropic + OpenAI-compatible)
│   ├── safety.py      # Safety guardrails (sandboxing, command filtering)
│   ├── scanner.py     # Workspace scanner for improvements
│   ├── __main__.py    # CLI entry point
│   ├── prompts/       # System prompts for the agent
│   └── skills/        # 14 tool definitions + executor
│
├── AgentUI/           # .NET MAUI cross-platform control panel
│   ├── Models/        # Data models (tasks, agents, status)
│   ├── Services/      # Agent/backlog/OpenClaw service layer
│   ├── ViewModels/    # MVVM view models
│   └── Views/         # 7 XAML pages (Dashboard, Tasks, Agents, etc.)
│
├── docker-compose.yml # Ollama local LLM (LLaMA) setup
├── BACKLOG.md         # Task queue (shared between agents + MAUI)
└── README.md
```

---

## Prerequisites

| Component | Required Version | Install Guide |
|-----------|-----------------|---------------|
| Python | 3.10+ | https://python.org |
| .NET SDK | 9.0+ | https://dotnet.microsoft.com/download |
| .NET MAUI workload | 9.0+ | `dotnet workload install maui` |
| Docker & Docker Compose | latest | https://docs.docker.com/get-docker/ |
| Git | 2.x+ | https://git-scm.com |

**Platform-specific requirements:**

- **Windows**: Visual Studio 2022 17.12+ with the `.NET MAUI` workload, or the .NET 9 SDK with MAUI workload installed via CLI.
- **macOS**: Xcode 16+ (for iOS/Mac Catalyst builds) and the .NET 9 SDK.
- **Linux**: MAUI builds target Android only on Linux. You need the Android SDK and JDK 17+.

---

## Quick Start — Running the MAUI App

### Step 1: Clone the repo

```bash
git clone https://github.com/chalkyjason/Swiftagent.git
cd Swiftagent
```

### Step 2: Install the MAUI workload

```bash
# Install the .NET MAUI workload (one-time setup)
dotnet workload install maui
```

### Step 3: Restore NuGet packages

```bash
cd AgentUI
dotnet restore
```

### Step 4: Build and run

Choose the target platform for your OS:

#### Windows

```bash
# Build and run for Windows
dotnet build -f net9.0-windows10.0.19041.0
dotnet run -f net9.0-windows10.0.19041.0
```

#### macOS (Mac Catalyst)

```bash
# Build and run for Mac Catalyst
dotnet build -f net9.0-maccatalyst
dotnet run -f net9.0-maccatalyst
```

#### iOS (from macOS)

```bash
# Build for iOS simulator
dotnet build -f net9.0-ios

# Run on iOS simulator
dotnet run -f net9.0-ios
```

#### Android

```bash
# Build for Android
dotnet build -f net9.0-android

# Deploy to connected device or emulator
dotnet run -f net9.0-android
```

### Step 5: Verify the app

Once launched, the Swiftagent MAUI app opens with 7 pages accessible from the navigation shell:

| Page | What you see |
|------|-------------|
| **Dashboard** | Agent status, OODA phase indicator, cost tracker, task progress |
| **Tasks** | Create/view/filter tasks by priority, category, and agent |
| **Agents** | Chat interface with the agent, session history |
| **Skills** | Browse and toggle the 14 agent skills |
| **Console** | Live streaming log output with filtering |
| **Safety & Cost** | Blocked command events, daily budget graph |
| **Settings** | Workspace path, model selection, budget, safety toggles |

The app communicates with OpenClaw through file-based IPC — it polls `openclaw_status.json` and tails `openclaw.log` from the workspace directory.

---

## Setting Up the OpenClaw Agent

### Option A: Cloud mode (Anthropic Claude API)

```bash
cd OpenClaw
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...
export OPENCLAW_WORKSPACE=/path/to/your/project

# Run the backlog loop
python -m OpenClaw

# Or run a specific task
python -m OpenClaw --task "Write unit tests for the auth module"
```

### Option B: Local LLaMA mode (free, no API credits)

This is the recommended setup for saving credits. OpenClaw connects to a locally running LLaMA model via Ollama, which exposes an OpenAI-compatible API. All inference runs on your machine — zero API costs.

#### 1. Start Ollama with Docker

```bash
# From the repo root
docker compose up -d
```

This starts an Ollama server on `http://localhost:11434`.

**GPU support:**
- **NVIDIA GPU**: Works out of the box (requires `nvidia-container-toolkit`).
- **AMD GPU**: Edit `docker-compose.yml` — uncomment the AMD section, comment out NVIDIA.
- **CPU only**: Remove the `deploy` section in `docker-compose.yml` (inference will be slower).

#### 2. Pull a LLaMA model

```bash
# Recommended: LLaMA 3.1 8B — good balance of speed and quality
docker compose exec ollama ollama pull llama3.1:8b

# Higher quality (needs 16GB+ VRAM)
docker compose exec ollama ollama pull llama3.1:70b

# Smaller/faster option (needs ~4GB VRAM)
docker compose exec ollama ollama pull llama3.2:3b

# Code-focused alternative
docker compose exec ollama ollama pull codellama:13b
```

#### 3. Install Python dependencies

```bash
cd OpenClaw
pip install -r requirements.txt
```

#### 4. Run OpenClaw with LLaMA

```bash
# Use LLaMA 3.1 8B (recommended default)
python -m OpenClaw --local --local-model llama3.1:8b

# Or specify a different LLaMA model
python -m OpenClaw --local --local-model llama3.1:70b

# Use CodeLlama for code-heavy tasks
python -m OpenClaw --local --local-model codellama:13b

# Custom Ollama server URL
python -m OpenClaw --local --local-model llama3.1:8b --local-api-base http://192.168.1.100:11434/v1

# Run a specific task with LLaMA
python -m OpenClaw --local --local-model llama3.1:8b --task "Refactor the database layer"
```

When running in local mode, the cost tracker shows $0.00 since inference is free.

#### 5. Verify Ollama is working

```bash
# Check the Ollama server is up
curl http://localhost:11434/api/tags

# Test a quick completion
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "Hello"}]}'
```

### LLaMA Model Recommendations

| Model | VRAM Needed | Best For |
|-------|------------|----------|
| `llama3.2:3b` | ~4 GB | Quick tasks, low-resource machines |
| `llama3.1:8b` | ~8 GB | General development tasks (recommended) |
| `codellama:13b` | ~10 GB | Code generation and refactoring |
| `llama3.1:70b` | ~40 GB | Complex reasoning, architecture decisions |

> **Tip:** If you have limited VRAM, start with `llama3.2:3b`. For most dev work, `llama3.1:8b` is the sweet spot. Use Claude API only when you need the highest quality output.

---

## Hybrid Mode — Mix Local and Cloud

You can run OpenClaw in local mode for most tasks and switch to Claude for complex work:

```bash
# Day-to-day tasks — free with LLaMA
python -m OpenClaw --local --local-model llama3.1:8b

# Complex architecture task — use Claude API
export ANTHROPIC_API_KEY=sk-ant-...
python -m OpenClaw --task "Design microservice migration strategy"
```

You can also use environment variables instead of CLI flags:

```bash
export OPENCLAW_PROVIDER=local
export OPENCLAW_MODEL=llama3.1:8b
export OPENCLAW_LOCAL_API_BASE=http://localhost:11434/v1
python -m OpenClaw
```

---

## All CLI Options

```
python -m OpenClaw [OPTIONS]

Options:
  --task TEXT              Run a specific task instead of the backlog loop
  --scan-only             Scan for improvements without modifying code
  --dry-run               Plan but don't execute file writes or commits
  --model TEXT             Override the model to use
  --budget FLOAT           Override the daily budget in USD
  --max-iterations INT     Override max task iterations
  --enable-claude-cli     Enable Claude CLI agent delegation
  --enable-goose          Enable Goose agent delegation
  --local                 Use local LLM via Ollama instead of Anthropic
  --local-model TEXT       Local model name (e.g. llama3.1:8b, codellama:13b)
  --local-api-base TEXT    Local LLM API URL (default: http://localhost:11434/v1)
```

---

## Creating Tasks

Tasks can be created from multiple sources:

- **MAUI app**: Tasks page → "+ New Task" button
- **BACKLOG.md**: Add markdown lines directly
- **OpenClaw agent**: Uses the `task_create` skill
- **CLI**: Edit `BACKLOG.md` and the agent picks them up on the next loop

Task format in `BACKLOG.md`:

```markdown
- [ ] [P1] [Backend] Implement user authentication @agent:openclaw
- [ ] [P2] [Frontend] Add dark mode toggle @agent:openclaw
- [x] [P1] [Tests] Write unit tests for auth module @agent:openclaw
```

---

## Agents

### OpenClaw (Primary Orchestrator)
- Powered by Claude API or local LLaMA (via Ollama)
- OODA loop: reads backlog, plans, executes, verifies, commits
- 14 skills: file I/O, shell, git, task management, code search, agent delegation
- Safety sandbox with command filtering and file size limits
- Cost tracking with daily budget enforcement

### Claude CLI (Delegated)
- Anthropic's open-source CLI agent
- Delegated sub-tasks from OpenClaw via `agent_delegate` skill
- Install: `npm install -g @anthropic-ai/claude-code`
- Enable: `CLAUDE_CLI_ENABLED=true` or `--enable-claude-cli`

### Goose (Delegated)
- Block's open-source autonomous development agent
- Delegated sub-tasks from OpenClaw via `agent_delegate` skill
- Install: https://github.com/block/goose
- Enable: `GOOSE_ENABLED=true` or `--enable-goose`

---

## Configuration Reference

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required for cloud) | Claude API key |
| `OPENCLAW_PROVIDER` | `anthropic` | `anthropic` or `local` |
| `OPENCLAW_MODEL` | `claude-sonnet-4-5-20250929` | Model name |
| `OPENCLAW_WORKSPACE` | Parent of OpenClaw dir | Workspace root |
| `OPENCLAW_BUDGET` | `5.00` | Daily budget in USD |
| `OPENCLAW_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARN, ERROR) |
| `OPENCLAW_DRY_RUN` | `false` | Plan without executing |
| `OPENCLAW_LOCAL_API_BASE` | `http://localhost:11434/v1` | Local LLM API URL |
| `OPENCLAW_LOCAL_API_KEY` | `ollama` | Local LLM API key (usually not needed) |
| `CLAUDE_CLI_ENABLED` | `false` | Enable Claude CLI agent |
| `CLAUDE_CLI_PATH` | `claude` | Path to Claude CLI binary |
| `GOOSE_ENABLED` | `false` | Enable Goose agent |
| `GOOSE_PATH` | `goose` | Path to Goose CLI binary |

---

## Safety

- Commands sandboxed to workspace directory
- Blocked: `sudo`, `rm -rf /`, `chmod`, device writes, process kills
- Allowed: git, python, node, docker, go, cargo, make, curl, etc.
- File size limit: 1 MB per file, 100 files per session
- Safe delete: files moved to `.openclaw_trash/` instead of permanent deletion
- Daily budget enforcement stops the agent when exhausted
