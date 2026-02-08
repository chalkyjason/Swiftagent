"""OpenClaw skill definitions.

Each skill is a tool the agent can invoke during task execution.
Skills are declared as structured tool schemas for the Claude API.
"""

from .definitions import ALL_SKILLS, get_skill_schemas

__all__ = ["ALL_SKILLS", "get_skill_schemas"]
