# OpenClaw Agent for Swiftagent
#
# Autonomous agent that improves the Swiftagent repository by:
#   - Scanning for code quality issues, missing tests, and TODOs
#   - Pulling tasks from BACKLOG.md
#   - Implementing features, fixes, and improvements
#   - Verifying changes via swift build / swift test
#   - Committing validated changes
#
# Usage:
#   python -m openclaw.agent                  # Run the improvement loop
#   python -m openclaw.agent --scan-only      # Scan and report, don't modify
#   python -m openclaw.agent --task "..."     # Run a specific task
#
# Configuration via environment:
#   ANTHROPIC_API_KEY     - Claude API key (required)
#   OPENCLAW_MODEL        - Model to use (default: claude-sonnet-4-5-20250929)
#   OPENCLAW_WORKSPACE    - Workspace root (default: parent of this dir)
#   OPENCLAW_BUDGET       - Daily budget in USD (default: 5.00)
#   OPENCLAW_LOG_LEVEL    - Log level (default: INFO)
#   OPENCLAW_DRY_RUN      - If "true", plan but don't execute (default: false)
