"""Tests for LLM provider abstraction."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from OpenClaw.config import OpenClawConfig
from OpenClaw.providers import (
    AnthropicProvider,
    LLMProvider,
    LLMResponse,
    OpenAICompatibleProvider,
    TextBlock,
    ToolUseBlock,
    Usage,
    _anthropic_messages_to_openai,
    _anthropic_tools_to_openai,
)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class TestDataTypes:
    def test_text_block(self):
        b = TextBlock(text="hello")
        assert b.type == "text"
        assert b.text == "hello"

    def test_tool_use_block(self):
        b = ToolUseBlock(name="git_status", input={"key": "val"}, id="t1")
        assert b.type == "tool_use"
        assert b.name == "git_status"
        assert b.input == {"key": "val"}
        assert b.id == "t1"

    def test_tool_use_block_default_input(self):
        b = ToolUseBlock(name="test")
        assert b.input == {}

    def test_usage(self):
        u = Usage(input_tokens=100, output_tokens=50)
        assert u.input_tokens == 100
        assert u.output_tokens == 50

    def test_llm_response(self):
        r = LLMResponse(
            content=[TextBlock(text="hi")],
            stop_reason="end_turn",
            usage=Usage(input_tokens=10, output_tokens=20),
        )
        assert r.stop_reason == "end_turn"
        assert len(r.content) == 1


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

class TestProviderFactory:
    def test_anthropic_provider_selected(self, tmp_path):
        config = OpenClawConfig(
            workspace_root=tmp_path,
            provider="anthropic",
            api_key="test-key",
        )
        with patch.dict("sys.modules", {"anthropic": MagicMock()}):
            provider = LLMProvider.for_config(config)
        assert isinstance(provider, AnthropicProvider)

    def test_local_provider_selected(self, tmp_path):
        config = OpenClawConfig(
            workspace_root=tmp_path,
            provider="local",
            local_api_base="http://localhost:11434/v1",
        )
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            provider = LLMProvider.for_config(config)
        assert isinstance(provider, OpenAICompatibleProvider)


# ---------------------------------------------------------------------------
# Tool schema conversion
# ---------------------------------------------------------------------------

class TestToolConversion:
    def test_converts_anthropic_to_openai_format(self):
        tools = [{
            "name": "git_status",
            "description": "Show git status",
            "input_schema": {
                "type": "object",
                "properties": {},
            },
        }]
        result = _anthropic_tools_to_openai(tools)
        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "git_status"
        assert result[0]["function"]["description"] == "Show git status"
        assert result[0]["function"]["parameters"] == {"type": "object", "properties": {}}

    def test_converts_multiple_tools(self):
        tools = [
            {"name": "a", "description": "desc_a", "input_schema": {"type": "object", "properties": {}}},
            {"name": "b", "description": "desc_b", "input_schema": {"type": "object", "properties": {"x": {"type": "string"}}}},
        ]
        result = _anthropic_tools_to_openai(tools)
        assert len(result) == 2
        assert result[0]["function"]["name"] == "a"
        assert result[1]["function"]["name"] == "b"

    def test_missing_description(self):
        tools = [{"name": "test", "input_schema": {"type": "object", "properties": {}}}]
        result = _anthropic_tools_to_openai(tools)
        assert result[0]["function"]["description"] == ""


# ---------------------------------------------------------------------------
# Message conversion
# ---------------------------------------------------------------------------

class TestMessageConversion:
    def test_system_message_added(self):
        result = _anthropic_messages_to_openai("You are helpful.", [])
        assert result[0]["role"] == "system"
        assert result[0]["content"] == "You are helpful."

    def test_no_system_when_empty(self):
        result = _anthropic_messages_to_openai("", [{"role": "user", "content": "hi"}])
        assert result[0]["role"] == "user"

    def test_plain_user_message(self):
        msgs = [{"role": "user", "content": "hello"}]
        result = _anthropic_messages_to_openai("sys", msgs)
        assert result[1]["role"] == "user"
        assert result[1]["content"] == "hello"

    def test_tool_result_message(self):
        msgs = [
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "ok"},
            ]},
        ]
        result = _anthropic_messages_to_openai("", msgs)
        assert result[0]["role"] == "tool"
        assert result[0]["tool_call_id"] == "t1"
        assert result[0]["content"] == "ok"

    def test_assistant_text_message(self):
        msgs = [{"role": "assistant", "content": "I'll help"}]
        result = _anthropic_messages_to_openai("", msgs)
        assert result[0]["role"] == "assistant"
        assert result[0]["content"] == "I'll help"

    def test_assistant_with_tool_use_blocks(self):
        msgs = [
            {"role": "assistant", "content": [
                TextBlock(text="Let me check."),
                ToolUseBlock(name="git_status", input={}, id="t1"),
            ]},
        ]
        result = _anthropic_messages_to_openai("", msgs)
        assert result[0]["role"] == "assistant"
        assert result[0]["content"] == "Let me check."
        assert len(result[0]["tool_calls"]) == 1
        tc = result[0]["tool_calls"][0]
        assert tc["id"] == "t1"
        assert tc["function"]["name"] == "git_status"

    def test_assistant_with_dict_blocks(self):
        """Handles raw dict blocks (as stored in conversation history)."""
        msgs = [
            {"role": "assistant", "content": [
                {"type": "text", "text": "Checking..."},
                {"type": "tool_use", "name": "file_read", "input": {"path": "x"}, "id": "t2"},
            ]},
        ]
        result = _anthropic_messages_to_openai("", msgs)
        assert result[0]["content"] == "Checking..."
        assert result[0]["tool_calls"][0]["function"]["name"] == "file_read"

    def test_full_conversation_round_trip(self):
        """Converts a full multi-turn tool-use conversation."""
        msgs = [
            {"role": "user", "content": "check status"},
            {"role": "assistant", "content": [
                TextBlock(text="I'll check."),
                ToolUseBlock(name="git_status", input={}, id="t1"),
            ]},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "(clean)"},
            ]},
            {"role": "assistant", "content": [
                TextBlock(text="Working tree is clean."),
            ]},
        ]
        result = _anthropic_messages_to_openai("You are an agent.", msgs)
        assert len(result) == 5  # system + user + assistant(tool) + tool_result + assistant
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"
        assert result[2]["role"] == "assistant"
        assert result[3]["role"] == "tool"
        assert result[4]["role"] == "assistant"


# ---------------------------------------------------------------------------
# Anthropic provider (mocked)
# ---------------------------------------------------------------------------

class TestAnthropicProvider:
    def _make_provider(self):
        with patch.dict("sys.modules", {"anthropic": MagicMock()}):
            provider = AnthropicProvider(api_key="test")
        provider.client = MagicMock()
        return provider

    def test_creates_message(self):
        provider = self._make_provider()

        mock_block = SimpleNamespace(type="text", text="Hello!")
        mock_response = SimpleNamespace(
            content=[mock_block],
            stop_reason="end_turn",
            usage=SimpleNamespace(input_tokens=10, output_tokens=5),
        )
        provider.client.messages.create.return_value = mock_response

        result = provider.create_message(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            temperature=0.0,
            system="sys",
            tools=[],
            messages=[{"role": "user", "content": "hi"}],
        )

        assert isinstance(result, LLMResponse)
        assert result.stop_reason == "end_turn"
        assert len(result.content) == 1
        assert result.content[0].type == "text"
        assert result.content[0].text == "Hello!"
        assert result.usage.input_tokens == 10

    def test_handles_tool_use_response(self):
        provider = self._make_provider()

        mock_tool = SimpleNamespace(
            type="tool_use", name="git_status", input={}, id="t1",
        )
        mock_response = SimpleNamespace(
            content=[mock_tool],
            stop_reason="tool_use",
            usage=SimpleNamespace(input_tokens=5, output_tokens=10),
        )
        provider.client.messages.create.return_value = mock_response

        result = provider.create_message(
            model="m", max_tokens=1, temperature=0,
            system="", tools=[], messages=[],
        )

        assert result.stop_reason == "tool_use"
        assert result.content[0].type == "tool_use"
        assert result.content[0].name == "git_status"


# ---------------------------------------------------------------------------
# OpenAI-compatible provider (mocked)
# ---------------------------------------------------------------------------

class TestOpenAIProvider:
    def _make_provider(self):
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            provider = OpenAICompatibleProvider(api_base="http://localhost:11434/v1")
        provider.client = MagicMock()
        return provider

    def test_text_response(self):
        provider = self._make_provider()

        mock_msg = SimpleNamespace(content="Hello from local!", tool_calls=None)
        mock_choice = SimpleNamespace(message=mock_msg, finish_reason="stop")
        mock_usage = SimpleNamespace(prompt_tokens=8, completion_tokens=3)
        mock_response = SimpleNamespace(choices=[mock_choice], usage=mock_usage)
        provider.client.chat.completions.create.return_value = mock_response

        result = provider.create_message(
            model="qwen2.5:14b",
            max_tokens=1024,
            temperature=0.0,
            system="sys",
            tools=[{"name": "git_status", "description": "status", "input_schema": {"type": "object", "properties": {}}}],
            messages=[{"role": "user", "content": "hello"}],
        )

        assert isinstance(result, LLMResponse)
        assert result.stop_reason == "end_turn"
        assert len(result.content) == 1
        assert result.content[0].text == "Hello from local!"
        assert result.usage.input_tokens == 8

    def test_tool_call_response(self):
        provider = self._make_provider()

        mock_tc = SimpleNamespace(
            id="call_1",
            function=SimpleNamespace(name="git_status", arguments="{}"),
        )
        mock_msg = SimpleNamespace(content=None, tool_calls=[mock_tc])
        mock_choice = SimpleNamespace(message=mock_msg, finish_reason="tool_calls")
        mock_usage = SimpleNamespace(prompt_tokens=10, completion_tokens=5)
        mock_response = SimpleNamespace(choices=[mock_choice], usage=mock_usage)
        provider.client.chat.completions.create.return_value = mock_response

        result = provider.create_message(
            model="qwen2.5:14b", max_tokens=1024, temperature=0.0,
            system="", tools=[], messages=[],
        )

        assert result.stop_reason == "tool_use"
        assert len(result.content) == 1
        assert result.content[0].type == "tool_use"
        assert result.content[0].name == "git_status"
        assert result.content[0].id == "call_1"

    def test_handles_missing_usage(self):
        provider = self._make_provider()

        mock_msg = SimpleNamespace(content="ok", tool_calls=None)
        mock_choice = SimpleNamespace(message=mock_msg, finish_reason="stop")
        mock_response = SimpleNamespace(choices=[mock_choice], usage=None)
        provider.client.chat.completions.create.return_value = mock_response

        result = provider.create_message(
            model="m", max_tokens=1, temperature=0,
            system="", tools=[], messages=[],
        )

        assert result.usage.input_tokens == 0
        assert result.usage.output_tokens == 0

    def test_handles_malformed_tool_arguments(self):
        provider = self._make_provider()

        mock_tc = SimpleNamespace(
            id="call_1",
            function=SimpleNamespace(name="file_read", arguments="not json"),
        )
        mock_msg = SimpleNamespace(content=None, tool_calls=[mock_tc])
        mock_choice = SimpleNamespace(message=mock_msg, finish_reason="tool_calls")
        mock_usage = SimpleNamespace(prompt_tokens=1, completion_tokens=1)
        mock_response = SimpleNamespace(choices=[mock_choice], usage=mock_usage)
        provider.client.chat.completions.create.return_value = mock_response

        result = provider.create_message(
            model="m", max_tokens=1, temperature=0,
            system="", tools=[], messages=[],
        )

        # Should not crash — just return empty dict for input
        assert result.content[0].input == {}

    def test_mixed_text_and_tool_calls(self):
        provider = self._make_provider()

        mock_tc = SimpleNamespace(
            id="call_1",
            function=SimpleNamespace(name="git_status", arguments="{}"),
        )
        mock_msg = SimpleNamespace(content="Let me check.", tool_calls=[mock_tc])
        mock_choice = SimpleNamespace(message=mock_msg, finish_reason="tool_calls")
        mock_usage = SimpleNamespace(prompt_tokens=5, completion_tokens=5)
        mock_response = SimpleNamespace(choices=[mock_choice], usage=mock_usage)
        provider.client.chat.completions.create.return_value = mock_response

        result = provider.create_message(
            model="m", max_tokens=1, temperature=0,
            system="", tools=[], messages=[],
        )

        assert len(result.content) == 2
        assert result.content[0].type == "text"
        assert result.content[1].type == "tool_use"


# ---------------------------------------------------------------------------
# Config validation for providers
# ---------------------------------------------------------------------------

class TestConfigValidation:
    def test_local_provider_no_api_key_needed(self, tmp_path):
        config = OpenClawConfig(
            workspace_root=tmp_path,
            provider="local",
            api_key="",  # no anthropic key
            local_api_base="http://localhost:11434/v1",
        )
        errors = config.validate()
        assert not any("ANTHROPIC_API_KEY" in e for e in errors)

    def test_local_provider_needs_api_base(self, tmp_path):
        config = OpenClawConfig(
            workspace_root=tmp_path,
            provider="local",
            local_api_base="",
        )
        errors = config.validate()
        assert any("LOCAL_API_BASE" in e for e in errors)

    def test_unknown_provider_rejected(self, tmp_path):
        config = OpenClawConfig(
            workspace_root=tmp_path,
            provider="gpt4all",
            api_key="x",
        )
        errors = config.validate()
        assert any("Unknown provider" in e for e in errors)
