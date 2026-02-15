# OpenClaw — Multi-Agent Task Orchestrator
#
# Autonomous agent that manages tasks from BACKLOG.md and delegates to
# other coding agents (Aider, Goose, Claude CLI, Codex, Cline).
# Runs on local LLMs (Ollama) for free or Anthropic Claude API.
#
# Quick start (local, free):
#   brew install ollama && ollama serve &
#   ollama pull llama3.1:8b
#   pip install -r requirements.txt
#   python -m OpenClaw --local --local-model llama3.1:8b
#
# Quick start (cloud):
#   export ANTHROPIC_API_KEY=sk-ant-...
#   python -m OpenClaw
#
# Enable agents:
#   --enable-aider       pip install aider-chat
#   --enable-goose       brew install block/goose/goose
#   --enable-claude-cli  npm install -g @anthropic-ai/claude-code
#   --enable-codex       npm install -g @openai/codex
#   --enable-cline       npm install -g cline
#
# Other flags:
#   --task "..."         Run a specific task
#   --scan-only          Scan and report, don't modify
#   --dry-run            Plan but don't execute
