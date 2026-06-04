# Design Document — kb-llm-integration

## Overview

This feature polishes the Cal Poly dance-club advisor application so it is production-ready on the `integration` branch. The system already works end-to-end; the changes are targeted:

1. **`main.py`** — a single, clean entry point that auto-regenerates the KB if missing, parses CLI flags, and wires `ChatController` → `ChatGui`.
2. **`chat_controller.py`** — an improved `KB_SYSTEM_PROMPT` that teaches the LLM *why* multi-variable queries fail and shows it how to write correct sequential queries.
3. **`requirements.txt`** — trimmed to runtime-only (`ollama>=0.4`), with exploration deps preserved under a `# dev / exploration` comment.
4. **`README.md`** — updated with Quick Start, Prerequisites, CLI flags, and KB-regeneration docs.
5. **`generate_kb.py`** — a `FileNotFoundError` guard added when `data/clubs.json` is absent.

No architectural rewrites. Every file that currently works is preserved; only the five changes above are made.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  python main.py [--model <name>] [--no-thinking]             │
│                                                              │
│  1. Parse CLI args                                           │
│  2. If kb/clubs_kb.pl missing → run generate_kb.generate()  │
│  3. ChatController(model, thinking)                          │
│  4. ChatGui(controller).run()   ← blocks until window close  │
└──────────────────────────────────────────────────────────────┘
             │                        │
             ▼                        ▼
  ┌──────────────────┐     ┌────────────────────────┐
  │  ChatController  │     │  ChatGui (tkinter)      │
  │                  │     │                        │
  │  LLM (ollama)    │     │  _poll_pending()        │
  │  query_clubs_kb  │     │  every 100 ms           │
  │  _disambiguate_  │     │  renders markdown /     │
  │    reused_vars   │     │  tables / query pane    │
  └──────────────────┘     └────────────────────────┘
             │
             ▼
  ┌──────────────────┐
  │  swipl (subprocess)                              │
  │  -s kb/clubs_kb.pl  -s <tmp_helper.pl>          │
  │  stdin ← prolog_query                           │
  │  stdout → JSON {rows: [...]}                     │
  └──────────────────┘
```

The threading model is unchanged: `ChatController` runs the LLM in a worker thread and puts `ChatResponse` objects on a `queue.Queue`; `ChatGui` drains that queue every 100 ms via `root.after`.

---

## Components and Interfaces

### `main.py` (new file)

```python
# Responsibilities
# - parse_args()  → argparse.Namespace  (--model, --no-thinking)
# - kb_guard()    → None  (regenerate KB if missing, print message)
# - main()        → None  (wire controller + gui, start event loop)
```

Key behaviour:

- `argparse.ArgumentParser` with `--model` (default `"gemma4:e2b"`) and `--no-thinking` (store_true).
- Before constructing `ChatController`, check `Path("kb/clubs_kb.pl").exists()`. If absent, print `"KB not found — regenerating kb/clubs_kb.pl from data/clubs.json…"` and call `generate_kb.generate()`.
- Construct `ChatController(model=args.model, thinking=not args.no_thinking)`.
- Construct `ChatGui(controller)` and call `.run()`.

`chat_gui.py` already contains a `parse_args` / `main` block inside `if __name__ == "__main__":`; `main.py` supersedes it for production use. The existing block is left intact for standalone development convenience.

---

### `chat_controller.py` — `KB_SYSTEM_PROMPT` (changed)

The most user-visible change. See the *System Prompt Strategy* section below for the full rationale.

The updated constant replaces the existing `KB_SYSTEM_PROMPT` string. All other logic in `chat_controller.py` (disambiguation, worker thread, Prolog runner) is unchanged.

---

### `generate_kb.py` — `FileNotFoundError` guard (changed)

Inside `generate()`, immediately after resolving `json_path`:

```python
if not json_path.exists():
    raise FileNotFoundError(
        f"clubs.json not found at expected path: {json_path}. "
        "Place the data file there and re-run."
    )
```

This replaces the implicit `FileNotFoundError` from `open()` with a descriptive message that includes the resolved absolute path.

---

### `requirements.txt` (changed)

```
ollama>=0.4

# dev / exploration
duckdb
ipython
matplotlib
pandas
rdflib
```

`ollama>=0.4` is the only runtime dependency. The `>=0.4` pin is the lowest version that shipped the `tools` parameter to `ollama.chat()`, which `llm.py` relies on.

---

### `README.md` (changed)

Sections to add/replace:

1. **Prerequisites** — Python ≥ 3.11, SWI-Prolog, Ollama with model pulled.
2. **Quick Start** — `pip install -r requirements.txt`, optionally `python generate_kb.py`, then `python main.py`.
3. **CLI Flags** — table of `--model` and `--no-thinking` with defaults.
4. **Regenerating the Knowledge Base** — `python generate_kb.py`, input `data/clubs.json`, output `kb/clubs_kb.pl`.

---

## Data Models

No new data models are introduced. The existing models are:

| Type | Location | Description |
|---|---|---|
| `KBToolCall` | `chat_controller.py` | Frozen dataclass: `query: str`, `response: str` |
| `ChatResponse` | `chat_controller.py` | Frozen dataclass: `content: str`, `is_error: bool`, `tool_calls: tuple[KBToolCall, ...]` |
| Prolog KB | `kb/clubs_kb.pl` | Auto-generated from `data/clubs.json`; see predicate listing in existing file header |

The Prolog query helper script (`PROLOG_QUERY_HELPER` constant) is unchanged; it reads a query from stdin and writes `{"rows": [...]}` JSON to stdout.

---

## System Prompt Strategy

### The root problem: Prolog variable unification

When the LLM writes a conjunctive query that reuses the same variable name across two different ground atoms, Prolog unifies that variable to the first value it binds and then fails to satisfy the second binding:

```prolog
% BAD — Prolog asks: "find Club where HoursPerWeek is X AND also X"
% If lion_dance_team_ldt has 2 hours and shan_wu_dance_team has 4 hours,
% this returns zero rows because Hours cannot be both 2 and 4 simultaneously.
hours_per_week(lion_dance_team_ldt, Hours),
hours_per_week(shan_wu_dance_team, Hours)
```

The zero-result response misleads the LLM into either inventing data or confusing the clubs.

### The correct pattern: distinct variables per club

```prolog
% GOOD — each club gets its own variable
hours_per_week(lion_dance_team_ldt, LionHours),
hours_per_week(shan_wu_dance_team, ShanWuHours)
```

Or split into two separate `query_clubs_kb` calls:

```
Call 1: hours_per_week(lion_dance_team_ldt, Hours), club(lion_dance_team_ldt, Name)
Call 2: hours_per_week(shan_wu_dance_team, Hours), club(shan_wu_dance_team, Name)
```

### What makes a "good" query

| Criterion | Good | Bad |
|---|---|---|
| Value variables | Unique per club (`LionHours`, `ShanWuHours`) | Shared across clubs (`Hours` used twice) |
| Scope of one call | One club or one category lookup | Two+ specific clubs in one conjunct |
| Display name | Always fetch `club(Club, Name)` alongside atom | Return raw atom (e.g., `lion_dance_team_ldt`) |
| Comparison operators | `Hours =< 4` after binding `hours_per_week(Club, Hours)` | Inline literal in wrong position |
| Category queries | `clubs_with_style(hip_hop, Club), club(Club, Name)` | Manually listing clubs for a style |

### What the improved system prompt includes

1. **Explicit sequential instruction** — a clear directive to issue one query per club when comparing two clubs' properties.
2. **Two worked examples of the correct sequential pattern** — shown side-by-side with the identical query applied to two different clubs.
3. **Description of the anti-pattern** — named and explained: "reusing the same variable for two different specific clubs asks Prolog to find a single value that satisfies both clubs at once, which almost always returns zero rows."
4. **Why it silently fails** — brief explanation of Prolog unification so the LLM understands the mechanism, not just the rule.
5. **DisplayName instruction** — explicit reminder to look up `club(Club, DisplayName)` and use `DisplayName` in the reply, never the internal atom like `lion_dance_team_ldt`.

### Automatic disambiguation (existing, unchanged logic)

`ChatController._disambiguate_reused_value_variables` already detects the anti-pattern at runtime: if a query returns zero rows and the query uses the same uppercase variable in the value position of a value-bearing predicate for two different ground atoms, it rewrites the variable names and retries. The improved prompt reduces how often this fallback is needed; the fallback remains as a safety net.

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Disambiguation rewrites reused value variables

*For any* valid Prolog query string that binds the same uppercase variable in the value position of a value-bearing predicate (e.g., `hours_per_week`, `dance_style`) for two or more distinct ground club atoms, `_disambiguate_reused_value_variables` SHALL return a new query string in which each occurrence of that variable has been renamed to a unique name (e.g., `Hours1`, `Hours2`), and the returned string SHALL differ from the input string.

**Validates: Requirements 2.4**

---

### Property 2: Disambiguation is identity for well-formed queries

*For any* valid Prolog query string that does NOT reuse the same uppercase variable in the value position of a value-bearing predicate for two distinct ground club atoms, `_disambiguate_reused_value_variables` SHALL return a string equal to the input string (i.e., the function is a no-op for already-correct queries).

**Validates: Requirements 2.4**

---

### Property 3: KB generator prints club count and line count for any valid data

*For any* non-empty list of valid club records passed through `generate_kb.generate()`, the output written to stdout SHALL contain both the number of clubs processed and the total number of lines written to the output file.

**Validates: Requirements 4.3**

---

### Property 4: Missing data file raises descriptive FileNotFoundError

*For any* file path string that does not correspond to an existing file on disk, calling `generate_kb.generate(json_path=<that path>)` SHALL raise a `FileNotFoundError` whose string message contains the given path.

**Validates: Requirements 4.4**

---

## Error Handling

| Scenario | Component | Handling |
|---|---|---|
| `kb/clubs_kb.pl` missing at startup | `main.py` | Auto-regenerate via `generate_kb.generate()`, print message to stdout |
| `data/clubs.json` missing when `generate_kb.py` runs | `generate_kb.py` | Raise `FileNotFoundError` with resolved absolute path |
| `swipl` not on PATH | `ChatController._run_prolog_query` | Return `"SWI-Prolog is not installed or swipl is not on PATH."` |
| Prolog query timeout (>5 s) | `ChatController._run_prolog_query` | Return `"The Prolog query timed out."` |
| Multi-variable query returns zero rows | `ChatController._query_clubs_kb` | Call `_disambiguate_reused_value_variables`, retry; include corrected query + explanation in response |
| LLM raises exception during chat | `ChatController._request_response` | Catch, put `ChatResponse(is_error=True)` on queue; GUI displays `**Error:** <message>` |
| Ollama not running / model not pulled | `LLM._chat_completion` | `ollama.chat()` raises; caught by controller error handler above |

---

## Testing Strategy

### Unit tests (example-based)

These cover specific behaviors that are not amenable to property-based testing:

- **`main.py` argument parsing** — verify `--model foo` sets `args.model == "foo"` and default is `"gemma4:e2b"`; verify `--no-thinking` sets flag; verify `--help` output contains both flags.
- **KB guard** — mock `Path.exists`: (a) returns False → `generate_kb.generate` called; (b) returns True → not called.
- **System prompt content** — assert `KB_SYSTEM_PROMPT` contains sequential-query instruction, ≥2 correct-example query lines, anti-pattern description, and `DisplayName` instruction.
- **Disambiguation response format** — for a known reused-variable query that returns empty then non-empty results (mocked Prolog), assert the returned string contains both the corrected query and a plain-language explanation.
- **`requirements.txt` structure** — parse file, verify runtime section contains only `ollama>=...`; verify `duckdb`, `rdflib`, `ipython`, `matplotlib`, `pandas` are absent from the runtime section; verify `# dev / exploration` comment exists.

### Property-based tests (universal properties)

Property-based testing applies here because `_disambiguate_reused_value_variables` and `generate_kb.generate` are pure-logic functions whose correctness must hold across a wide input space.

**Library**: [`hypothesis`](https://hypothesis.readthedocs.io/) (Python)  
**Minimum iterations**: 100 per property test

#### Property 1 — Disambiguation rewrites reused variables
```
Feature: kb-llm-integration, Property 1: disambiguation rewrites reused value variables
```
Generator: produce two distinct ground club atoms and a value-bearing predicate name; construct query `pred(atom1, V), pred(atom2, V)`; call `_disambiguate_reused_value_variables`; assert result != input and `V1`/`V2` (or equivalent distinct names) appear in result.

#### Property 2 — Disambiguation identity for well-formed queries
```
Feature: kb-llm-integration, Property 2: disambiguation is identity for well-formed queries
```
Generator: produce a query where no value variable is reused across distinct ground atoms (e.g., single-club queries, category queries); assert result == input.

#### Property 3 — KB generator stdout contains counts
```
Feature: kb-llm-integration, Property 3: KB generator prints club count and line count
```
Generator: produce a list of minimal valid club dicts (varying length 1–20); call `generate()` capturing stdout; assert stdout contains the club count integer and the line count integer.

#### Property 4 — Missing file raises descriptive error
```
Feature: kb-llm-integration, Property 4: missing data file raises descriptive FileNotFoundError
```
Generator: produce a random nonexistent path string (e.g., a UUID-based temp path); call `generate(json_path=path)`; assert `FileNotFoundError` is raised and `str(exc)` contains the path.

### Integration tests

- Run `generate_kb.generate()` against the real `data/clubs.json` and load the output with `swipl --halt -s kb/clubs_kb.pl` to confirm zero errors.
- Start `ChatController` with a real Ollama instance and verify `query_clubs_kb("club(X, Name)")` returns a non-empty JSON array.

### What is deliberately NOT tested

- `chat_gui.py` rendering logic — tkinter widgets require a display and are tested via visual inspection.
- The LLM's actual response quality — non-deterministic and not property-testable.
- README content — verified by human review.
