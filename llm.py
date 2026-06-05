from __future__ import annotations

from collections.abc import Callable
from typing import Any

import ollama


class LLM:
    """Small stateful wrapper around Ollama chat models."""

    def __init__(
        self,
        model: str = "gemma4:e2b",
        system_prompt: str | None = None,
        thinking: bool = True,
        tools: dict[str, Callable[..., object]] | None = None,
    ) -> None:
        self.model = model
        self.system_prompt = system_prompt
        self.thinking = thinking
        self.tools = tools or {}
        self._messages: list[Any] = []
        self.clear()

    def chat(self, user_chat: str) -> str:
        """Send a user message to the model and return the assistant response."""
        self._messages.append({"role": "user", "content": user_chat})

        while True:
            response = self._chat_completion()
            message = self._get_message(response)
            self._messages.append(message)

            tool_calls = self._get_tool_calls(message)
            if not tool_calls:
                return self._get_message_content(message)

            for tool_call in tool_calls:
                tool_name, arguments = self._get_tool_call_parts(tool_call)
                result = self._call_tool(tool_name, arguments)
                self._messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": str(result),
                    }
                )

    def clear(self) -> None:
        """Clear conversation history while preserving the configured system prompt."""
        self._messages = []
        if self.system_prompt:
            self._messages.append({"role": "system", "content": self.system_prompt})

    def _chat_completion(self) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": self._messages,
            "think": self.thinking,
        }
        if self.tools:
            kwargs["tools"] = list(self.tools.values())
        return ollama.chat(**kwargs)

    def _call_tool(self, tool_name: str, arguments: dict[str, Any]) -> object:
        tool = self.tools.get(tool_name)
        if tool is None:
            for candidate in self.tools.values():
                if getattr(candidate, "__name__", None) == tool_name:
                    tool = candidate
                    break

        if tool is None:
            return f"Unknown tool: {tool_name}"
        return tool(**arguments)

    @staticmethod
    def _get_message(response: Any) -> Any:
        if isinstance(response, dict):
            return response["message"]
        return response.message

    @staticmethod
    def _get_message_content(message: Any) -> str:
        if isinstance(message, dict):
            return message.get("content", "")
        return message.content

    @staticmethod
    def _get_tool_calls(message: Any) -> list[Any]:
        if isinstance(message, dict):
            return message.get("tool_calls") or []
        return message.tool_calls or []

    @staticmethod
    def _get_tool_call_parts(tool_call: Any) -> tuple[str, dict[str, Any]]:
        if isinstance(tool_call, dict):
            function = tool_call["function"]
            return function["name"], function.get("arguments", {})
        return tool_call.function.name, tool_call.function.arguments
