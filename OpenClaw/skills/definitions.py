"""Skill (tool) definitions for the OpenClaw agent.

Each skill maps to a Claude tool_use schema and a local executor function.
"""

ALL_SKILLS = [
    {
        "name": "shell_exec",
        "description": (
            "Execute a shell command in the workspace. Only allowed commands "
            "will run (swift, git, ls, grep, etc). Dangerous or out-of-sandbox "
            "commands are blocked by the safety guard."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute."
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory (relative to workspace root). Optional."
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "file_read",
        "description": (
            "Read the contents of a file in the workspace. "
            "Path must be relative to the workspace root."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to workspace root."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "file_write",
        "description": (
            "Create or overwrite a file in the workspace. The file content is "
            "written atomically. Path must be within the sandbox."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to workspace root."
                },
                "content": {
                    "type": "string",
                    "description": "Full content to write to the file."
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "file_patch",
        "description": (
            "Apply a targeted edit to an existing file by replacing an exact "
            "string match. Use this instead of file_write when making small "
            "changes to preserve the rest of the file."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to workspace root."
                },
                "old_string": {
                    "type": "string",
                    "description": "The exact string to find and replace."
                },
                "new_string": {
                    "type": "string",
                    "description": "The replacement string."
                }
            },
            "required": ["path", "old_string", "new_string"]
        }
    },
    {
        "name": "file_list",
        "description": (
            "List files and directories under a given path. "
            "Supports optional glob pattern filtering."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path relative to workspace root."
                },
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern filter (e.g. '**/*.swift'). Optional."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "swift_build",
        "description": (
            "Build a Swift package. Runs 'swift build' in the specified "
            "package directory and returns the build output."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "package_path": {
                    "type": "string",
                    "description": "Path to the Swift package directory, relative to workspace root."
                }
            },
            "required": ["package_path"]
        }
    },
    {
        "name": "swift_test",
        "description": (
            "Run tests for a Swift package. Runs 'swift test' in the "
            "specified package directory and returns test results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "package_path": {
                    "type": "string",
                    "description": "Path to the Swift package directory, relative to workspace root."
                }
            },
            "required": ["package_path"]
        }
    },
    {
        "name": "git_status",
        "description": "Show the current git status of the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {},
        }
    },
    {
        "name": "git_diff",
        "description": "Show unstaged changes in the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Optional path to diff. If omitted, diffs entire workspace."
                }
            },
        }
    },
    {
        "name": "git_commit",
        "description": (
            "Stage specified files and create a git commit. "
            "Only committed if all files are within the sandbox."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file paths to stage (relative to workspace root)."
                },
                "message": {
                    "type": "string",
                    "description": "Commit message."
                }
            },
            "required": ["files", "message"]
        }
    },
    {
        "name": "backlog_read",
        "description": "Read the current BACKLOG.md and return its contents.",
        "input_schema": {
            "type": "object",
            "properties": {},
        }
    },
    {
        "name": "backlog_update_task",
        "description": (
            "Update the status of a task in BACKLOG.md. "
            "Can mark tasks as in-progress, completed, or add new tasks."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task_description": {
                    "type": "string",
                    "description": "The task description to find/update."
                },
                "new_status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"],
                    "description": "The new status for the task."
                }
            },
            "required": ["task_description", "new_status"]
        }
    },
    {
        "name": "search_code",
        "description": (
            "Search for a pattern across the codebase. "
            "Uses grep-like matching across all source files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Search pattern (supports basic regex)."
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob to filter files (e.g. '*.swift'). Optional."
                },
                "path": {
                    "type": "string",
                    "description": "Directory to search in (relative to workspace). Optional."
                }
            },
            "required": ["pattern"]
        }
    },
]


def get_skill_schemas() -> list[dict]:
    """Return tool schemas formatted for the Claude API."""
    return ALL_SKILLS
