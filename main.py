"""
main.py
Entry point for the Cal Poly Dance Club Advisor.
Run with: python main.py [--model <name>] [--no-thinking]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cal Poly Dance Club Advisor — chat with an LLM backed by a Prolog KB.",
    )
    parser.add_argument(
        "--model",
        default="gemma4:e2b",
        help="Ollama model name to use (default: gemma4:e2b)",
    )
    parser.add_argument(
        "--no-thinking",
        action="store_true",
        help="Disable extended-thinking mode in the LLM",
    )
    return parser.parse_args()


def kb_guard() -> None:
    """Regenerate the Prolog KB from clubs.json if it is missing."""
    kb_path = Path(__file__).parent / "kb" / "clubs_kb.pl"
    if not kb_path.exists():
        print("KB not found — regenerating kb/clubs_kb.pl from data/clubs.json…")
        import generate_kb
        generate_kb.generate()


def main() -> None:
    args = parse_args()
    kb_guard()

    from chat_controller import ChatController
    from chat_gui import ChatGui

    controller = ChatController(
        model=args.model,
        thinking=not args.no_thinking,
    )
    ChatGui(controller).run()


if __name__ == "__main__":
    main()
