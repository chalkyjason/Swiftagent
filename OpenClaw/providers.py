"""LLM provider abstraction — Anthropic and OpenAI-compatible (Ollama, etc).

Gives the agent a single interface regardless of which backend is in use.
The OpenAI-compatible provider works with Ollama, llama.cpp, LM Studio,
vLLM, or any server that speaks the OpenAI chat completions API.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("openclaw.providers")


# ---------------------------------------------------------------------------
# Normalised response types used by agent.py
# ---------------------------------------------------------------------------

@dataclass
class TextBlock:
    type: str = "text"
    text: str = ""


@dataclass
class ToolUseBlock:
    type: str = "tool_use"
    name: str = ""
    input: dict = None
    id: str = ""

    def __post_init__(self):
        if self.input is None:
            self.input = {}


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class LLMResponse:
    """Provider-agnostic response matching what agent.py expects."""
    content: list[TextBlock | ToolUseBlock]
    stop_reason: str  # "end_turn" or "tool_use"
    usage: Usage


# ---------------------------------------------------------------------------
# Base provider
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """Interface that every LLM backend must implement."""

    @abstractmethod
    def create_message(
        self,
        model: str,
        max_tokens: int,
        temperature: float,
        system: str,
        tools: list[dict],
        messages: list[dict],
    ) -> LLMResponse:
        ...

    @staticmethod
    def for_config(config) -> "LLMProvider":
        """Factory: return the right provider for the current config."""
        if config.provider == "local":
            return OpenAICompatibleProvider(
                api_base=config.local_api_base,
                api_key=config.local_api_key,
            )
        return AnthropicProvider(api_key=config.api_key)


# ---------------------------------------------------------------------------
# Anthropic provider (existing behaviour)
# ---------------------------------------------------------------------------

class AnthropicProvider(LLMProvider):
    """Calls the Anthropic Messages API."""

    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)

    def create_message(self, model, max_tokens, temperature, system, tools, messages):
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            tools=tools,
            messages=messages,
        )

        content = []
        for block in response.content:
            if block.type == "text":
                content.append(TextBlock(text=block.text))
            elif block.type == "tool_use":
                content.append(ToolUseBlock(
                    name=block.name,
                    input=block.input,
                    id=block.id,
                ))

        return LLMResponse(
            content=content,
            stop_reason=response.stop_reason,  # "end_turn" / "tool_use"
            usage=Usage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            ),
        )


# ---------------------------------------------------------------------------
# OpenAI-compatible provider (Ollama, llama.cpp, LM Studio, vLLM)
# ---------------------------------------------------------------------------

def _anthropic_tools_to_openai(tools: list[dict]) -> list[dict]:
    """Convert Anthropic tool schemas to OpenAI function-calling format."""
    openai_tools = []
    for tool in tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
            },
        })
    return openai_tools


def _anthropic_messages_to_openai(system: str, messages: list[dict]) -> list[dict]:
    """Convert Anthropic-style messages to OpenAI chat format.

    Anthropic format:
      - {"role": "user", "content": "text"}
      - {"role": "assistant", "content": [TextBlock, ToolUseBlock, ...]}
      - {"role": "user", "content": [{"type": "tool_result", "tool_use_id": ..., "content": ...}]}

    OpenAI format:
      - {"role": "system", "content": "..."}
      - {"role": "user", "content": "..."}
      - {"role": "assistant", "content": "...", "tool_calls": [...]}
      - {"role": "tool", "tool_call_id": "...", "content": "..."}
    """
    openai_msgs: list[dict] = []

    if system:
        openai_msgs.append({"role": "system", "content": system})

    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            # Could be plain text or tool_result blocks
            if isinstance(content, str):
                openai_msgs.append({"role": "user", "content": content})
            elif isinstance(content, list):
                # Tool results
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_result":
                        openai_msgs.append({
                            "role": "tool",
                            "tool_call_id": item["tool_use_id"],
                            "content": item.get("content", ""),
                        })
                    elif isinstance(item, str):
                        openai_msgs.append({"role": "user", "content": item})

        elif role == "assistant":
            if isinstance(content, str):
                openai_msgs.append({"role": "assistant", "content": content})
            elif isinstance(content, list):
                text_parts = []
                tool_calls = []
                for block in content:
                    if hasattr(block, "type"):
                        # These are TextBlock / ToolUseBlock dataclass instances
                        if block.type == "text":
                            text_parts.append(block.text)
                        elif block.type == "tool_use":
                            tool_calls.append({
                                "id": block.id,
                                "type": "function",
                                "function": {
                                    "name": block.name,
                                    "arguments": json.dumps(block.input),
                                },
                            })
                    elif isinstance(block, dict):
                        btype = block.get("type", "")
                        if btype == "text":
                            text_parts.append(block.get("text", ""))
                        elif btype == "tool_use":
                            tool_calls.append({
                                "id": block.get("id", ""),
                                "type": "function",
                                "function": {
                                    "name": block.get("name", ""),
                                    "arguments": json.dumps(block.get("input", {})),
                                },
                            })

                assistant_msg: dict[str, Any] = {"role": "assistant"}
                assistant_msg["content"] = "\n".join(text_parts) if text_parts else None
                if tool_calls:
                    assistant_msg["tool_calls"] = tool_calls
                openai_msgs.append(assistant_msg)

    return openai_msgs


class OpenAICompatibleProvider(LLMProvider):
    """Calls any OpenAI-compatible API (Ollama, llama.cpp, LM Studio, vLLM).

    Ollama exposes this at http://localhost:11434/v1 by default.
    """

    def __init__(self, api_base: str, api_key: str = "ollama"):
        from openai import OpenAI
        self.client = OpenAI(
            base_url=api_base,
            api_key=api_key,
        )
        logger.info(f"Local LLM provider initialized: {api_base}")

    def create_message(self, model, max_tokens, temperature, system, tools, messages):
        openai_tools = _anthropic_tools_to_openai(tools)
        openai_messages = _anthropic_messages_to_openai(system, messages)

        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": openai_messages,
        }
        if openai_tools:
            kwargs["tools"] = openai_tools

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message

        # Build normalised content blocks
        content: list[TextBlock | ToolUseBlock] = []

        if message.content:
            content.append(TextBlock(text=message.content))

        if message.tool_calls:
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {}
                content.append(ToolUseBlock(
                    name=tc.function.name,
                    input=args,
                    id=tc.id,
                ))

        # Map finish reasons
        stop_reason = "end_turn"
        if choice.finish_reason == "tool_calls":
            stop_reason = "tool_use"

        # Extract usage (some local servers omit this)
        usage = Usage()
        if response.usage:
            usage.input_tokens = response.usage.prompt_tokens or 0
            usage.output_tokens = response.usage.completion_tokens or 0

        return LLMResponse(
            content=content,
            stop_reason=stop_reason,
            usage=usage,
        )
