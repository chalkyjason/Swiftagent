# Task Backlog

This file is used by the autonomous agent system to track and manage tasks.
Tasks are created via the MAUI app or the OpenClaw agent and executed by
OpenClaw, Claude CLI, or Goose.

## In Progress

## Pending

## Blocked

## Completed

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
- Agent: `@agent:openclaw`, `@agent:claude`, `@agent:goose`
