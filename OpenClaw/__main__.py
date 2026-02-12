"""Entry point: python -m OpenClaw"""

import argparse

from .agent import OpenClawAgent
from .config import OpenClawConfig


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw — autonomous multi-agent task orchestrator"
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
        help="Override the Claude model to use"
    )
    parser.add_argument(
        "--budget", type=float, default=None,
        help="Override the daily budget in USD"
    )
    parser.add_argument(
        "--max-iterations", type=int, default=None,
        help="Override max task iterations"
    )
    parser.add_argument(
        "--enable-claude-cli", action="store_true",
        help="Enable Claude CLI agent delegation"
    )
    parser.add_argument(
        "--enable-goose", action="store_true",
        help="Enable Goose agent delegation"
    )

    args = parser.parse_args()

    config = OpenClawConfig()
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

    agent = OpenClawAgent(config)
    agent.run(task=args.task, scan_only=args.scan_only)


if __name__ == "__main__":
    main()
