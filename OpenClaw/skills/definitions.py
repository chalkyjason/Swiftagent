"""Skill (tool) definitions for the OpenClaw agent.

General-purpose task execution skills with multi-agent delegation.
"""

ALL_SKILLS = [
    {
        "name": "shell_exec",
        "description": (
            "Execute a shell command in the workspace. Supports general-purpose "
            "dev tools (git, python, node, docker, go, cargo, etc). "
            "Dangerous commands are blocked by the safety guard."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to execute."},
                "working_dir": {"type": "string", "description": "Working directory relative to workspace root. Optional."}
            },
            "required": ["command"]
        }
    },
    {
        "name": "file_read",
        "description": "Read a file's contents. Path is relative to workspace root.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "File path relative to workspace root."}},
            "required": ["path"]
        }
    },
    {
        "name": "file_write",
        "description": "Create or overwrite a file. Path must be within the sandbox.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace root."},
                "content": {"type": "string", "description": "Full content to write."}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "file_patch",
        "description": "Apply a targeted edit by replacing an exact string match in a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace root."},
                "old_string": {"type": "string", "description": "The exact string to find and replace."},
                "new_string": {"type": "string", "description": "The replacement string."}
            },
            "required": ["path", "old_string", "new_string"]
        }
    },
    {
        "name": "file_list",
        "description": "List files under a path with optional glob filtering.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path relative to workspace root."},
                "pattern": {"type": "string", "description": "Glob pattern (e.g. '**/*.py'). Optional."}
            },
            "required": ["path"]
        }
    },
    {
        "name": "git_status",
        "description": "Show git status of the workspace.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "git_diff",
        "description": "Show unstaged changes.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Optional path to diff."}}
        }
    },
    {
        "name": "git_commit",
        "description": "Stage files and create a git commit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "files": {"type": "array", "items": {"type": "string"}, "description": "Files to stage."},
                "message": {"type": "string", "description": "Commit message."}
            },
            "required": ["files", "message"]
        }
    },
    {
        "name": "task_create",
        "description": "Create a new task in BACKLOG.md tracked by the MAUI UI.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short task title."},
                "description": {"type": "string", "description": "Detailed description."},
                "priority": {"type": "string", "enum": ["P1", "P2", "P3"], "description": "P1=high, P2=medium, P3=low."},
                "category": {"type": "string", "description": "Category (Backend, Frontend, DevOps, etc)."},
                "agent": {"type": "string", "enum": ["openclaw", "claude", "goose", "any"], "description": "Assigned agent."}
            },
            "required": ["title", "priority"]
        }
    },
    {
        "name": "task_list",
        "description": "List all tasks from the backlog with current status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status_filter": {"type": "string", "enum": ["all", "pending", "in_progress", "completed", "blocked"]}
            }
        }
    },
    {
        "name": "task_update",
        "description": "Update a task's status in BACKLOG.md.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_title": {"type": "string", "description": "Task title to find/update."},
                "new_status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"]},
                "notes": {"type": "string", "description": "Optional notes."}
            },
            "required": ["task_title", "new_status"]
        }
    },
    {
        "name": "search_code",
        "description": "Search for a regex pattern across the codebase.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern."},
                "file_pattern": {"type": "string", "description": "Glob filter (e.g. '*.py'). Optional."},
                "path": {"type": "string", "description": "Directory to search. Optional."}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "agent_delegate",
        "description": "Delegate a sub-task to Claude CLI or Goose agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string", "enum": ["claude", "goose"], "description": "Target agent."},
                "task": {"type": "string", "description": "Task prompt for the agent."},
                "working_dir": {"type": "string", "description": "Working dir relative to workspace. Optional."}
            },
            "required": ["agent", "task"]
        }
    },
    {
        "name": "agent_status",
        "description": "Check availability of all agents (OpenClaw, Claude CLI, Goose).",
        "input_schema": {"type": "object", "properties": {}}
    },
]


def get_skill_schemas() -> list[dict]:
    """Return tool schemas formatted for the Claude API."""
    return ALL_SKILLS
