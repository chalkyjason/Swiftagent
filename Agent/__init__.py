"""
Autonomous Game Development Agent

A continuous agent system for building reusable iOS game components
using Swift Package Manager and the Claude Agent SDK.
"""

from .config import AgentConfig, get_config, set_config
from .safety_wrapper import SafetyWrapper, SafetyPolicy
from .checkpoint_manager import CheckpointManager, BacklogManager, TaskCheckpoint, TaskStatus
from .context_manager import ContextManager, VectorStore
from .game_agent import GameDevelopmentAgent, AgentState

__version__ = "0.1.0"

__all__ = [
    "AgentConfig",
    "get_config",
    "set_config",
    "SafetyWrapper",
    "SafetyPolicy",
    "CheckpointManager",
    "BacklogManager",
    "TaskCheckpoint",
    "TaskStatus",
    "ContextManager",
    "VectorStore",
    "GameDevelopmentAgent",
    "AgentState",
]
