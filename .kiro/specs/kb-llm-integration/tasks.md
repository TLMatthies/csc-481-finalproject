# Implementation Plan: kb-llm-integration

## Overview

Five targeted file changes that polish the Cal Poly dance-club advisor into a production-ready application. No architectural rewrites — each task is isolated to a single file. Property-based tests use `hypothesis` to verify the two pure-logic functions across a wide input space.

## Tasks

- [x] 1. Add `FileNotFoundError` guard to `generate_kb.py`
  - In `generate()`, immediately after `json_path = base / json_path`, add an `if not json_path.exists()` check that raises `FileNotFoundError` with a message containing the resolved absolute path and a hint to place the file there.
  - This replaces the implicit error from `open()` with a descriptive one.
  - _Requirements: 4.4_

  - [ ]* 1.1 Write property test — missing data file raises descriptive `FileNotFoundError`
    - **Property 4: Missing data file raises descriptive FileNotFoundError**
    - Use `hypothesis` `st.text()` / `st.uuids()` to generate nonexistent path strings; call `generate_kb.generate(json_path=path)` and assert `FileNotFoundError` is raised and `str(exc)` contains the path.
    - **Validates: Requirements 4.4**

- [x] 2. Verify and improve `generate_kb.py` stdout output
  - Confirm (and update if needed) that the `print()` call at the end of `generate()` outputs both the number of clubs and the number of lines written, so the output is clearly readable by users and testable by property tests.
  - Current line: `print(f"Written {out_path}  ({len(lines)} lines, {len(data['clubs'])} clubs)")` — verify the integers are present as standalone tokens parseable by a test.
  - _Requirements: 4.3_

  - [ ]* 2.1 Write property test — KB generator prints club count and line count
    - **Property 3: KB generator prints club count and line count**
    - Use `hypothesis` `st.lists(...)` to generate 1–20 minimal valid club dicts (each with at least a `"name"` key); call `generate()` capturing stdout via `capsys` or `io.StringIO`; assert stdout contains both the integer club count and the integer line count.
    - **Validates: Requirements 4.3**

- [x] 3. Improve `KB_SYSTEM_PROMPT` in `chat_controller.py`
  - Replace the existing `KB_SYSTEM_PROMPT` constant with an updated version that:
    - Explicitly instructs the LLM to issue one query per club when comparing properties across clubs.
    - Provides at least two concrete worked examples of the correct sequential pattern (same predicate, different club atoms, different variable names).
    - Names and explains the multi-variable anti-pattern: "Reusing the same variable for two different specific clubs asks Prolog to find a single value that satisfies both at once, which almost always returns zero rows."
    - Briefly explains Prolog unification so the LLM understands the mechanism, not just the rule.
    - Explicitly instructs the LLM to always look up `club(Club, DisplayName)` and use `DisplayName` in all user-facing replies.
  - All other logic in `chat_controller.py` (disambiguation, worker thread, Prolog runner) remains unchanged.
  - _Requirements: 2.1, 2.2, 2.3, 2.6_

  - [ ]* 3.1 Write unit test — system prompt content assertions
    - Assert `KB_SYSTEM_PROMPT` contains the sequential-query instruction, at least two correct-example query lines, the anti-pattern description, and the `DisplayName` instruction.
    - _Requirements: 2.1, 2.2, 2.3, 2.6_

- [ ] 4. Write property tests for `_disambiguate_reused_value_variables`
  - These tests validate the pure disambiguation logic already present in `chat_controller.py`.
  - Create a test file (e.g., `tests/test_disambiguation.py`) that imports `ChatController` and exercises the static/instance method directly.
  - _Requirements: 2.4_

  - [ ]* 4.1 Write property test — disambiguation rewrites reused value variables
    - **Property 1: Disambiguation rewrites reused value variables**
    - Use `hypothesis` to generate two distinct ground club atoms (lowercase snake_case) and a predicate name from `ChatController.VALUE_PROPERTY_PREDICATES`; construct the query `pred(atom1, V), pred(atom2, V)`; call `_disambiguate_reused_value_variables`; assert result differs from input and contains `V1` and `V2` (or other distinct suffixed names).
    - **Validates: Requirements 2.4**

  - [ ]* 4.2 Write property test — disambiguation is identity for well-formed queries
    - **Property 2: Disambiguation is identity for well-formed queries**
    - Use `hypothesis` to generate queries that do NOT reuse the same variable for two distinct ground atoms (e.g., single-club queries, category queries using `clubs_with_style`); assert `_disambiguate_reused_value_variables(query) == query`.
    - **Validates: Requirements 2.4**

- [ ] 5. Checkpoint — run existing tests and property tests
  - Ensure all property tests pass (`pytest tests/ --tb=short`). Fix any failures before continuing.
  - Ask the user if questions arise.

- [x] 6. Update `requirements.txt`
  - Replace the current contents with a runtime-only section containing `ollama>=0.4`, followed by a `# dev / exploration` comment block listing `duckdb`, `ipython`, `matplotlib`, `pandas`, `rdflib`.
  - Verify no other package is imported by `main.py`, `chat_gui.py`, `chat_controller.py`, or `llm.py` beyond the standard library.
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 6.1 Write unit test — `requirements.txt` structure
    - Parse `requirements.txt`; assert runtime section contains only `ollama>=...`; assert `duckdb`, `rdflib`, `ipython`, `matplotlib`, `pandas` are absent from the runtime section; assert `# dev / exploration` comment exists.
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 7. Create `main.py` entry point
  - Implement three functions:
    - `parse_args() -> argparse.Namespace` — `--model` (default `"gemma4:e2b"`) and `--no-thinking` (store_true).
    - `kb_guard() -> None` — check `Path("kb/clubs_kb.pl").exists()`; if absent, print `"KB not found — regenerating kb/clubs_kb.pl from data/clubs.json…"` and call `generate_kb.generate()`.
    - `main() -> None` — call `parse_args()`, call `kb_guard()`, construct `ChatController(model=args.model, thinking=not args.no_thinking)`, construct `ChatGui(controller)`, call `.run()`.
  - Add `if __name__ == "__main__": main()` guard.
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.3, 5.5_

  - [ ]* 7.1 Write unit tests — argument parsing and KB guard
    - Verify `--model foo` sets `args.model == "foo"` and default is `"gemma4:e2b"`.
    - Verify `--no-thinking` sets the flag.
    - Mock `Path.exists` returning `False` → assert `generate_kb.generate` is called.
    - Mock `Path.exists` returning `True` → assert `generate_kb.generate` is not called.
    - _Requirements: 1.1, 1.2, 1.4_

- [x] 8. Update `README.md`
  - Add or replace the following sections:
    - **Prerequisites** — Python ≥ 3.11, SWI-Prolog, Ollama with the default model pulled.
    - **Quick Start** — `pip install -r requirements.txt`, then (optionally) `python generate_kb.py`, then `python main.py`.
    - **CLI Flags** — table of `--model` and `--no-thinking` with defaults.
    - **Regenerating the Knowledge Base** — documents `python generate_kb.py`, input `data/clubs.json`, output `kb/clubs_kb.pl`.
  - _Requirements: 4.1, 4.5, 5.1, 5.2, 5.3, 5.4_

- [ ] 9. Final checkpoint — ensure all tests pass
  - Run `pytest tests/ --tb=short` and confirm all tests pass.
  - Verify `python main.py --help` prints usage with `--model` and `--no-thinking`.
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP.
- Each task references specific requirements for traceability.
- Property tests use [`hypothesis`](https://hypothesis.readthedocs.io/) with a minimum of 100 iterations per property.
- Checkpoints (tasks 5 and 9) validate incremental correctness before moving to the next phase.
- `main.py` supersedes `chat_gui.py`'s `if __name__ == "__main__":` block for production use; that block is left intact for standalone development convenience.
