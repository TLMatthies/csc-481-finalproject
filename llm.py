from __future__ import annotations

from typing import Any

import ollama


class LLM:
    """Small stateful wrapper around Ollama chat models."""

    def __init__(
        self,
        model: str = "gemma4:e2b",
        system_prompt: str | None = None,
        thinking: bool = True,
    ) -> None:
        self.model = model
        self.system_prompt = system_prompt
        self.thinking = thinking
        self._messages: list[dict[str, str]] = []
        self.clear()

    def chat(self, user_chat: str) -> str:
        """Send a user message to the model and return the assistant response."""
        self._messages.append({"role": "user", "content": user_chat})
        response = ollama.chat(
            model=self.model,
            messages=self._messages,
            think=self.thinking,
        )

        assistant_message = self._get_assistant_message(response)
        self._messages.append({"role": "assistant", "content": assistant_message})
        return assistant_message

    def clear(self) -> None:
        """Clear conversation history while preserving the configured system prompt."""
        self._messages = []
        if self.system_prompt:
            self._messages.append({"role": "system", "content": self.system_prompt})

    @staticmethod
    def _get_assistant_message(response: Any) -> str:
        message = response["message"]
        if isinstance(message, dict):
            return message.get("content", "")
        return message.content
