# Task Backlog

This file is used by the autonomous agent system to track and manage tasks.
Tasks are created via the MAUI app or the OpenClaw agent and executed by
OpenClaw, Claude CLI, Goose, Aider, Codex, or Cline.

## In Progress

## Pending

- [ ] [P2] [Agent] Support task dependencies in BACKLOG.md (blocked-by field) @agent:openclaw
  > Tasks can't express ordering constraints; agents may pick up tasks with unmet prerequisites
- [ ] [P2] [UI] Add error banners to MAUI dashboard when agent IPC files are stale or missing @agent:openclaw
  > UI silently shows stale data when agent is not running; user has no indication
- [ ] [P3] [Agent] Add per-task cost tracking alongside daily budget @agent:openclaw
  > Current cost tracker only tracks daily totals; no visibility into individual task costs
- [ ] [P3] [Agent] Add configurable skill enable/disable via config or environment @agent:openclaw
  > All 14 skills are always active; operators may want to restrict capabilities per deployment
- [ ] [P3] [DevOps] Add Docker-based integration test runner for CI @agent:openclaw
  > Tests currently only run bare Python; a containerised runner would ensure reproducibility

## Blocked

## Completed

- [x] [P1] [Testing] Add MAUI UI unit tests for ViewModels and Services @agent:openclaw
  > AgentUI.Tests project created with BacklogViewModelTests and DashboardViewModelTests
- [x] [P1] [Agent] Add conversation context pruning to prevent unbounded memory growth @agent:openclaw
  > _prune_conversation() added; called before every API call in _run_task and _run_scan
- [x] [P1] [Agent] Validate LLM response structure before accessing fields @agent:openclaw
  > OpenAICompatibleProvider now validates choices list, message object, and empty content
- [x] [P2] [Agent] Add structured logging with JSON output for machine-parseable logs @agent:openclaw
  > _JSONFormatter + json_handler added to _setup_logging; writes openclaw.json.log
- [x] [P2] [DevOps] Add health-check endpoint or heartbeat file for external monitoring @agent:openclaw
  > _write_heartbeat() added; writes openclaw_heartbeat.json on every status update
- [x] [P2] [Security] Sanitize task input passed to subprocess in agent_delegate @agent:openclaw
  > All _run_* methods now use shlex.quote(task) instead of raw string interpolation
- [x] [P2] [Testing] Add SwiftTamagotchi XCTest unit tests for GameLogic and SaveManager @agent:openclaw
  > PetModelTests.swift and SaveManagerTests.swift added to SwiftTamagotchiTests/
- [x] [P3] [Docs] Write deployment and distribution guide for MAUI app and iOS game @agent:openclaw
  > docs/distribution-openclaw.md, docs/distribution-maui.md, docs/distribution-ios.md created

---

## Agent Instructions

When processing this backlog:

1. **Priority Order**: Process tasks marked `[P1]` first, then `[P2]`, then `[P3]`
2. **Agent Assignment**: Respect `@agent:` tags when present
3. **Testing**: Verify changes before marking tasks complete
4. **Commits**: Make atomic commits with clear messages
5. **Status Updates**: Update task status as you progress

### Task Format
```markdown
- [ ] [P2] [Category] Task title @agent:openclaw
```

### Task Status Legend
- `[ ]` - Pending
- `[x]` - Completed
- Priority: `[P1]` High, `[P2]` Medium, `[P3]` Low
- Agent: `@agent:openclaw`, `@agent:claude`, `@agent:goose`, `@agent:aider`, `@agent:codex`, `@agent:cline`
