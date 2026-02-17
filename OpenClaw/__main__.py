"""Entry point: python -m OpenClaw"""

import argparse
from pathlib import Path

from .agent import OpenClawAgent
from .config import OpenClawConfig


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw — autonomous multi-agent task orchestrator"
    )
    parser.add_argument(
        "--project", type=str, default=None,
        metavar="PATH",
        help="Path to the project workspace root (default: parent of OpenClaw directory, "
             "or OPENCLAW_WORKSPACE env var)"
    )
    parser.add_argument(
        "--task", type=str, default=None,
        help="Run a specific task instead of the backlog loop"
    )
    parser.add_argument(
        "--scan-only", action="store_true",
        help="Scan for improvements without modifying code"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Plan but don't execute file writes or commits"
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help="Override the model to use"
    )
    parser.add_argument(
        "--budget", type=float, default=None,
        help="Override the daily budget in USD"
    )
    parser.add_argument(
        "--max-iterations", type=int, default=None,
        help="Override max task iterations"
    )
    # Agent delegation (easiest first, API-key-required last)
    parser.add_argument(
        "--enable-aider", action="store_true",
        help="Enable Aider agent (pip install aider-chat)"
    )
    parser.add_argument(
        "--enable-goose", action="store_true",
        help="Enable Goose agent (brew install block/goose/goose)"
    )
    parser.add_argument(
        "--enable-cline", action="store_true",
        help="Enable Cline agent (npm install -g cline)"
    )
    parser.add_argument(
        "--enable-claude-cli", action="store_true",
        help="Enable Claude CLI agent (needs ANTHROPIC_API_KEY)"
    )
    parser.add_argument(
        "--enable-codex", action="store_true",
        help="Enable Codex CLI agent (needs OPENAI_API_KEY)"
    )

    # Local LLM options
    parser.add_argument(
        "--local", action="store_true",
        help="Use a local LLM via Ollama/OpenAI-compatible API instead of Anthropic"
    )
    parser.add_argument(
        "--local-model", type=str, default=None,
        help="Local model name (e.g. llama3.1:8b, llama3.2:3b, codellama:13b)"
    )
    parser.add_argument(
        "--local-api-base", type=str, default=None,
        help="Local LLM API base URL (default: http://localhost:11434/v1)"
    )

    args = parser.parse_args()

    config = OpenClawConfig()
    if args.project:
        project_path = Path(args.project).expanduser().resolve()
        if not project_path.exists():
            parser.error(f"Project path does not exist: {project_path}")
        config.workspace_root = project_path
    if args.dry_run:
        config.dry_run = True
    if args.model:
        config.model = args.model
    if args.budget:
        config.daily_budget = args.budget
    if args.max_iterations:
        config.max_iterations = args.max_iterations
    if args.enable_claude_cli:
        config.claude_cli_enabled = True
    if args.enable_goose:
        config.goose_enabled = True
    if args.enable_aider:
        config.aider_enabled = True
    if args.enable_codex:
        config.codex_enabled = True
    if args.enable_cline:
        config.cline_enabled = True

    # Local LLM config
    if args.local:
        config.provider = "local"
        config.cost_per_input_token = 0.0
        config.cost_per_output_token = 0.0
        if not args.local_model and not args.model:
            config.model = "llama3.1:8b"
    if args.local_model:
        config.provider = "local"
        config.model = args.local_model
        config.cost_per_input_token = 0.0
        config.cost_per_output_token = 0.0
    if args.local_api_base:
        config.local_api_base = args.local_api_base

    agent = OpenClawAgent(config)
    agent.run(task=args.task, scan_only=args.scan_only)


if __name__ == "__main__":
    main()
