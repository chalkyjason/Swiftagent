# OpenClaw — Multi-Agent Task Orchestrator
#
# General-purpose autonomous agent that:
#   - Manages tasks from BACKLOG.md
#   - Coordinates with Claude CLI, Goose, Aider, Codex, and Cline agents
#   - Executes tasks using file I/O, shell, git, and code search skills
#   - Reports status to the MAUI control panel in real-time
#
# Usage:
#   python -m OpenClaw                          # Run the backlog loop
#   python -m OpenClaw --scan-only              # Scan and report, don't modify
#   python -m OpenClaw --task "..."             # Run a specific task
#   python -m OpenClaw --enable-claude-cli      # Enable Claude CLI delegation
#   python -m OpenClaw --enable-goose           # Enable Goose delegation
#   python -m OpenClaw --enable-aider           # Enable Aider delegation
#   python -m OpenClaw --enable-codex           # Enable Codex CLI delegation
#   python -m OpenClaw --enable-cline           # Enable Cline delegation
#   python -m OpenClaw --dry-run                # Plan but don't execute
#
# Configuration via environment:
#   ANTHROPIC_API_KEY     - Claude API key (required)
#   OPENCLAW_MODEL        - Model to use (default: claude-sonnet-4-5-20250929)
#   OPENCLAW_WORKSPACE    - Workspace root (default: parent of this dir)
#   OPENCLAW_BUDGET       - Daily budget in USD (default: 5.00)
#   OPENCLAW_LOG_LEVEL    - Log level (default: INFO)
#   OPENCLAW_DRY_RUN      - If "true", plan but don't execute (default: false)
#   CLAUDE_CLI_ENABLED    - Enable Claude CLI agent (default: false)
#   CLAUDE_CLI_PATH       - Path to claude CLI (default: claude)
#   GOOSE_ENABLED         - Enable Goose agent (default: false)
#   GOOSE_PATH            - Path to goose CLI (default: goose)
#   AIDER_ENABLED         - Enable Aider agent (default: false)
#   AIDER_PATH            - Path to aider CLI (default: aider)
#   CODEX_ENABLED         - Enable Codex CLI agent (default: false)
#   CODEX_PATH            - Path to codex CLI (default: codex)
#   CLINE_ENABLED         - Enable Cline agent (default: false)
#   CLINE_PATH            - Path to cline CLI (default: cline)
