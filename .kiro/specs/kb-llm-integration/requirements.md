# Requirements Document

## Introduction

This feature integrates the Cal Poly dance club Prolog knowledge base with the LLM chat stack into a polished, production-ready application on the `integration` branch. The work covers: a single clean entry point (`main.py`), an improved LLM system prompt that steers the model toward correct sequential Prolog queries, a trimmed `requirements.txt` containing only runtime dependencies, and a verified data pipeline from `data/clubs.json` through `generate_kb.py` to `kb/clubs_kb.pl`.

The existing system already works end-to-end — the goal is integration polish, not a rewrite.

## Glossary

- **System**: The complete Cal Poly dance club advisor application composed of the components below.
- **Entry_Point**: `main.py`, the single file a user invokes to start the application.
- **Chat_GUI**: The tkinter window defined in `chat_gui.py`.
- **Chat_Controller**: The orchestration layer in `chat_controller.py` that wires the LLM to the Prolog KB.
- **LLM**: The Ollama-backed language model wrapper defined in `llm.py`.
- **KB**: The SWI-Prolog knowledge base at `kb/clubs_kb.pl` encoding facts about Cal Poly dance clubs.
- **KB_Generator**: The script `generate_kb.py` that converts `data/clubs.json` into `kb/clubs_kb.pl`.
- **System_Prompt**: The instruction text prepended to the conversation that guides LLM query behavior.
- **Query_Tool**: The `query_clubs_kb` Python function exposed to the LLM as a tool call.
- **Prolog_Runner**: The subprocess invocation of `swipl` inside `chat_controller.py`.
- **Sequential_Query**: A Prolog query that retrieves data for exactly one club or one list lookup per invocation.
- **Multi_Variable_Query**: A Prolog query that reuses the same variable across predicates for different clubs, causing unintended unification.

---

## Requirements

### Requirement 1: Clean Entry Point

**User Story:** As a developer or end user, I want to launch the application with `python main.py`, so that I do not need to know which internal module to invoke.

#### Acceptance Criteria

1. THE Entry_Point SHALL accept a `--model` command-line argument that specifies the Ollama model name, defaulting to `gemma4:e2b`.
2. THE Entry_Point SHALL accept a `--no-thinking` flag that disables extended-thinking mode in the LLM.
3. WHEN the Entry_Point is executed, THE Entry_Point SHALL construct a `ChatController` and a `ChatGui`, then start the GUI event loop.
4. WHEN the KB file at `kb/clubs_kb.pl` does not exist on startup, THE Entry_Point SHALL automatically invoke the KB_Generator to regenerate `kb/clubs_kb.pl` before launching the GUI, printing a descriptive message to stdout indicating that the KB is being regenerated.
5. THE Entry_Point SHALL be the sole file a user needs to invoke; no other module SHALL require direct execution for normal use.

---

### Requirement 2: Improved System Prompt for Sequential Queries

**User Story:** As a developer, I want the LLM to issue one Prolog query per club or lookup at a time, so that Prolog variable unification does not silently constrain results to a single matching value.

#### Acceptance Criteria

1. THE System_Prompt SHALL explicitly instruct the LLM to issue one Sequential_Query per piece of information rather than combining multiple club lookups into one conjunctive query.
2. THE System_Prompt SHALL provide at least two concrete correct examples of Sequential_Query patterns for retrieving the same property from two different clubs.
3. THE System_Prompt SHALL explicitly describe the Multi_Variable_Query anti-pattern and explain why it returns incorrect results.
4. WHEN the LLM issues a Multi_Variable_Query that returns zero rows, THE Chat_Controller SHALL attempt to automatically disambiguate it using `_disambiguate_reused_value_variables` and retry the corrected query.
5. WHEN disambiguation produces results, THE Chat_Controller SHALL include the corrected query and a plain-language explanation in the JSON response returned to the LLM.
6. THE System_Prompt SHALL instruct the LLM to use the club's `DisplayName` from `club(Club, DisplayName)` in all user-facing responses rather than the internal atom.

---

### Requirement 3: Runtime-Only Dependencies in requirements.txt

**User Story:** As a developer setting up the project, I want `requirements.txt` to list only the packages the running application needs, so that installation is fast and does not pull in unused exploration libraries.

#### Acceptance Criteria

1. THE `requirements.txt` SHALL contain exactly the packages required to run `python main.py`: `ollama` and no others beyond standard library modules.
2. THE `requirements.txt` SHALL NOT contain exploration or notebook packages (`duckdb`, `rdflib`, `ipython`, `matplotlib`, `pandas`) unless they are imported by `main.py`, `chat_gui.py`, `chat_controller.py`, or `llm.py`.
3. WHERE a developer wishes to record notebook or exploration dependencies, THE `requirements.txt` SHALL separate them under a clearly labeled comment such as `# dev / exploration`.
4. THE `requirements.txt` SHALL pin each runtime package to a minimum version using `>=` to allow compatible upgrades while preventing regression on untested older versions.

---

### Requirement 4: Verified Data Pipeline

**User Story:** As a developer, I want the `data/clubs.json` → `generate_kb.py` → `kb/clubs_kb.pl` pipeline to be documented and verifiable, so that regenerating the KB after data updates is straightforward and correct.

#### Acceptance Criteria

1. THE `README.md` SHALL include a "Regenerating the Knowledge Base" section that documents the command `python generate_kb.py` and describes the input (`data/clubs.json`) and output (`kb/clubs_kb.pl`).
2. WHEN `generate_kb.py` is executed, THE KB_Generator SHALL write a valid SWI-Prolog file to `kb/clubs_kb.pl` that loads without errors under `swipl`.
3. WHEN `generate_kb.py` is executed, THE KB_Generator SHALL print the number of clubs and lines written to stdout.
4. IF `data/clubs.json` does not exist when `generate_kb.py` is executed, THEN THE KB_Generator SHALL raise a descriptive `FileNotFoundError` that includes the expected file path.
5. THE `README.md` SHALL include a "Quick Start" section documenting the end-to-end commands: install dependencies, (optionally) regenerate the KB, and launch the app.

---

### Requirement 5: Application Launch Documentation

**User Story:** As a new developer or user, I want the README to explain how to install dependencies and start the app, so that I can get it running without reading source code.

#### Acceptance Criteria

1. THE `README.md` SHALL document the minimum system requirements: Python version (3.11 or later), SWI-Prolog, and Ollama with the default model pulled.
2. THE `README.md` SHALL include the exact command to install Python dependencies: `pip install -r requirements.txt`.
3. THE `README.md` SHALL include the exact command to start the application: `python main.py`.
4. THE `README.md` SHALL list the available command-line flags for `main.py` and their default values.
5. WHEN `python main.py --help` is run, THE Entry_Point SHALL print usage information including all supported flags.
