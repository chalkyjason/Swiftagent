# Swiftagent - Multi-Agent Task Orchestration Platform

A production-ready platform for managing tasks through multiple open-source AI agents, with a cross-platform .NET MAUI control panel for real-time monitoring and task creation.

## Architecture

```
Swiftagent/
├── OpenClaw/          # Python agent orchestrator (Claude API)
│   ├── agent.py       # Main OODA loop + multi-agent coordination
│   ├── config.py      # Configuration (workspace, budget, models, agents)
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
├── BACKLOG.md         # Task queue (shared between agents + MAUI)
└── README.md
```

## Agents

### OpenClaw (Primary Orchestrator)
- Powered by Claude API (Anthropic)
- OODA loop: reads backlog, plans, executes, verifies, commits
- 14 skills: file I/O, shell, git, task management, code search, agent delegation
- Safety sandbox with command filtering and file size limits
- Cost tracking with daily budget enforcement

### Claude CLI
- Anthropic's open-source CLI agent
- Delegated sub-tasks from OpenClaw via `agent_delegate` skill
- Install: `npm install -g @anthropic-ai/claude-code`
- Enable: `CLAUDE_CLI_ENABLED=true`

### Goose
- Block's open-source autonomous development agent
- Delegated sub-tasks from OpenClaw via `agent_delegate` skill
- Install: https://github.com/block/goose
- Enable: `GOOSE_ENABLED=true`

## MAUI Control Panel

Cross-platform app (iOS, macOS, Android, Windows) with 7 pages:

| Page | Purpose |
|------|---------|
| **Dashboard** | Agent status, OODA phase, cost, tasks progress |
| **Tasks** | Create, view, filter tasks with priority/category/agent assignment |
| **Agents** | Chat interface, agent connection management, session history |
| **Skills** | Browse and toggle 14 agent skills with safety ratings |
| **Console** | Live streaming log output with filtering |
| **Safety & Cost** | Blocked commands, budget tracking, safety events |
| **Settings** | Workspace, model, budget, safety configuration |

## Quick Start

### 1. Set up the agent

```bash
# Install dependencies
cd OpenClaw
pip install -r requirements.txt

# Configure
export ANTHROPIC_API_KEY=sk-ant-...
export OPENCLAW_WORKSPACE=/path/to/your/project

# Optional: enable additional agents
export CLAUDE_CLI_ENABLED=true
export GOOSE_ENABLED=true
```

### 2. Run the agent

```bash
# Run the backlog loop (picks tasks from BACKLOG.md)
python -m OpenClaw

# Run a specific task
python -m OpenClaw --task "Write unit tests for the auth module"

# Scan for improvements (read-only)
python -m OpenClaw --scan-only

# Dry run (plan without executing)
python -m OpenClaw --dry-run

# Enable multi-agent delegation
python -m OpenClaw --enable-claude-cli --enable-goose
```

### 3. Create tasks

Tasks can be created from:
- **MAUI app**: Tasks page -> "+ New Task" button
- **BACKLOG.md**: Add markdown lines directly
- **OpenClaw agent**: Uses the `task_create` skill
- **CLI**: Edit BACKLOG.md and the agent picks them up

Task format:
```markdown
- [ ] [P1] [Backend] Implement user authentication @agent:openclaw
```

### 4. Monitor via MAUI

```bash
cd AgentUI
dotnet build
dotnet run
```

The MAUI app polls `openclaw_status.json` and `openclaw.log` from the workspace to show real-time status, cost, and agent activity.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Claude API key |
| `OPENCLAW_MODEL` | `claude-sonnet-4-5-20250929` | Model to use |
| `OPENCLAW_WORKSPACE` | Parent of OpenClaw dir | Workspace root |
| `OPENCLAW_BUDGET` | `5.00` | Daily budget in USD |
| `OPENCLAW_LOG_LEVEL` | `INFO` | Log level |
| `OPENCLAW_DRY_RUN` | `false` | Plan without executing |
| `CLAUDE_CLI_ENABLED` | `false` | Enable Claude CLI agent |
| `CLAUDE_CLI_PATH` | `claude` | Path to Claude CLI |
| `GOOSE_ENABLED` | `false` | Enable Goose agent |
| `GOOSE_PATH` | `goose` | Path to Goose CLI |

## Safety

- Commands sandboxed to workspace directory
- Blocked: `sudo`, `rm -rf /`, `chmod`, device writes, process kills
- Allowed: git, python, node, docker, go, cargo, make, curl, etc.
- File size limit: 1 MB per file, 100 files per session
- Safe delete: files moved to `.openclaw_trash/` instead of permanent deletion
- Daily budget enforcement stops the agent when exhausted
