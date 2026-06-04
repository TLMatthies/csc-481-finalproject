# Cal Poly Dance Club Advisor

*Dance, Dance, Resolution* — CSC 481 Final Project

**Team Members:** Briana Kirkman, Timothy Matthies, Pragati Toppo

A natural language interface for Cal Poly's cultural dance clubs, powered by a Prolog knowledge base and a local LLM via Ollama.

---

## Prerequisites

- **Python 3.11 or later**
- **SWI-Prolog** — [https://www.swi-prolog.org/download/stable](https://www.swi-prolog.org/download/stable) (`swipl` must be on PATH)
- **Ollama** — [https://ollama.com/download](https://ollama.com/download) with the default model pulled:
  ```
  ollama pull gemma4:e2b
  ```

---

## Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. (Optional) Regenerate the knowledge base from source data
python generate_kb.py

# 3. Launch the app
python main.py
```

The app will automatically regenerate `kb/clubs_kb.pl` on first launch if it is missing.

---

## CLI Flags

| Flag | Default | Description |
|---|---|---|
| `--model <name>` | `gemma4:e2b` | Ollama model to use |
| `--no-thinking` | off | Disable extended-thinking mode |

Run `python main.py --help` for usage information.

**Examples:**
```bash
python main.py --model qwen2.5:3b
python main.py --no-thinking
```

---

## Regenerating the Knowledge Base

The knowledge base is generated from `data/clubs.json`:

```bash
python generate_kb.py
```

- **Input:** `data/clubs.json` — structured club data
- **Output:** `kb/clubs_kb.pl` — Prolog facts and rules

Run this whenever `data/clubs.json` is updated. The generator prints the number of clubs and lines written on success.

---

## Project Structure

```
├── main.py              # Entry point — run this to start the app
├── chat_gui.py          # tkinter GUI
├── chat_controller.py   # LLM ↔ Prolog KB orchestration
├── llm.py               # Ollama wrapper
├── generate_kb.py       # Converts clubs.json → clubs_kb.pl
├── data/
│   └── clubs.json       # Source of truth for club data
└── kb/
    └── clubs_kb.pl      # Generated Prolog knowledge base
```
