from __future__ import annotations

import json
import queue
import re
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from llm import LLM


KB_SYSTEM_PROMPT = """CRITICAL RULE — YOU MUST FOLLOW THIS WITHOUT EXCEPTION:
For ANY factual question about Cal Poly dance clubs — hours, performances, style, culture, dues,
skill level, travel, competitions, or any other club property — you MUST call query_clubs_kb.
Never answer from memory or training data. The knowledge base is the only authoritative source.
If you are unsure whether a fact is in the KB, call query_clubs_kb to check.

═══════════════════════════════════════════════════════════
SEQUENTIAL QUERY RULE — ONE CLUB PER CALL WHEN COMPARING
═══════════════════════════════════════════════════════════

When a user asks you to compare the SAME property across TWO OR MORE specific clubs,
issue ONE separate query_clubs_kb call for each club. Do NOT try to retrieve both
values in one conjunctive query.

WHY THIS MATTERS — PROLOG UNIFICATION:
Prolog uses unification: when you write a variable like "Hours", Prolog binds it to
the first value it finds and then requires every other use of "Hours" in that same query
to equal that same value. If lion_dance_team_ldt practices 2 hours/week and
shan_wu_dance_team practices 4 hours/week, a query that uses "Hours" for both clubs
asks Prolog: "find Hours such that Hours = 2 AND Hours = 4 simultaneously." That is
impossible, so the query returns zero rows — silently, with no error message.

THE MULTI-VARIABLE ANTI-PATTERN (DO NOT DO THIS):
  hours_per_week(lion_dance_team_ldt, Hours), hours_per_week(shan_wu_dance_team, Hours)
This reuses the variable Hours for two different specific clubs. Prolog must find one
value that satisfies both at once, which almost always returns zero rows, because the
two clubs typically have different values. The response looks like neither club has any
data, which is wrong.

CORRECT PATTERN — EXAMPLE 1 (distinct variables in one call):
  Call 1: hours_per_week(lion_dance_team_ldt, LionHours), club(lion_dance_team_ldt, LionName)
  Call 2: hours_per_week(shan_wu_dance_team, ShanWuHours), club(shan_wu_dance_team, ShanWuName)
Each call uses its own uniquely named variable (LionHours, ShanWuHours). Prolog can
bind each independently and both calls return results.

CORRECT PATTERN — EXAMPLE 2 (performances comparison):
  Call 1: performances_per_year(kaba_modern_cal_poly, KabaPerfs), club(kaba_modern_cal_poly, KabaName)
  Call 2: performances_per_year(ballroom_dance_club, BallroomPerfs), club(ballroom_dance_club, BallroomName)
Again, KabaPerfs and BallroomPerfs are distinct variables — Prolog binds them
independently and both calls succeed.

DISPLAY NAME RULE:
ALWAYS fetch the club's display name alongside any other data you retrieve.
Use the fact: club(Club, DisplayName)
Use DisplayName in every user-facing reply. NEVER expose the internal atom
(e.g., lion_dance_team_ldt, shan_wu_dance_team) to the user. The display name
is the human-readable club name such as "Lion Dance Team @ LDT" or "Shan Wu Dance Team".

═══════════════════════════════════════════════════════════
PROLOG QUERY SYNTAX REFERENCE
═══════════════════════════════════════════════════════════

The Prolog KB is queried with read-only Prolog goals. Use variables that begin with
uppercase letters, atoms in lowercase snake_case, and conjunctions with commas.

Available fact predicates:
- club(Club, DisplayName)
- alias(Club, Alias)
- hours_per_week(Club, Hours)
- performances_per_year(Club, Count)
- competes(Club)
- travels(Club)
- performs_downtown(Club)
- collects_dues(Club)
- big_little(Club)
- performance_contract(Club)
- does_covers(Club)
- dance_style(Club, Style)
- culture(Club, Culture)
- skill_level(Club, Level)
- sister_club(ClubA, ClubB)

Available rule predicates:
- clubs_with_style(Style, Club)
- clubs_with_culture(Culture, Club)
- beginner_friendly(Club)
- low_commitment(MaxHours, Club)
- high_performance(MinPerfs, Club)
- recommend(Style, Level, Club)
- free_to_join(Club)
- has_mentorship(Club)
- competitive_travel(Club)
- club_by_name(SearchName, Club, DisplayName)  ← use this to look up a club by its human-readable name

LOOKING UP A CLUB BY NAME:
When the user refers to a club by its human-readable name (e.g., "PCE Kasayahan", "Lion Dance Team"),
use club_by_name to resolve it to its atom before querying other predicates:
  club_by_name('PCE Kasayahan', Club, DisplayName)
  club_by_name('Lion Dance Team (LDT)', Club, DisplayName)
Do NOT use club(Club, DisplayName), club(Club, "Some Name") — that is invalid Prolog syntax.
Do NOT guess atom names like pce_kasayahan — always use club_by_name to resolve them.

Available comparison operators:
- Hours =< 4
- Hours >= 4
- Hours < 4
- Hours > 4
- Value = expected_atom

Useful examples:
- club(Club, Name)
- dance_style(Club, hip_hop), club(Club, Name)
- recommend(hip_hop, beginner, Club), club(Club, Name)
- low_commitment(3, Club), beginner_friendly(Club), club(Club, Name)
- free_to_join(Club), club(Club, Name)
"""

PROLOG_QUERY_HELPER = """
:- use_module(library(http/json)).
:- initialization(main, main).

allowed(club, 2).
allowed(alias, 2).
allowed(hours_per_week, 2).
allowed(performances_per_year, 2).
allowed(competes, 1).
allowed(travels, 1).
allowed(performs_downtown, 1).
allowed(collects_dues, 1).
allowed(big_little, 1).
allowed(performance_contract, 1).
allowed(does_covers, 1).
allowed(dance_style, 2).
allowed(culture, 2).
allowed(skill_level, 2).
allowed(sister_club, 2).
allowed(clubs_with_style, 2).
allowed(clubs_with_culture, 2).
allowed(beginner_friendly, 1).
allowed(low_commitment, 2).
allowed(high_performance, 2).
allowed(recommend, 3).
allowed(free_to_join, 1).
allowed(has_mentorship, 1).
allowed(competitive_travel, 1).
allowed(club_by_name, 3).
allowed(=<, 2).
allowed(>=, 2).
allowed(<, 2).
allowed(>, 2).
allowed(=, 2).

main(_) :-
    read_string(user_input, _, QueryString),
    normalize_space(string(QueryAtom), QueryString),
    catch(run_query(QueryAtom), Error, write_error(Error)).

run_query(QueryAtom) :-
    read_term_from_atom(QueryAtom, Query, [variable_names(Names)]),
    safe_goal(Query),
    findall(Bindings, (call(Query), bindings_dict(Names, Bindings)), Rows),
    json_write_dict(current_output, _{rows: Rows}, [width(0)]),
    nl.

safe_goal((Left, Right)) :-
    !,
    safe_goal(Left),
    safe_goal(Right).
safe_goal(Goal) :-
    callable(Goal),
    functor(Goal, Name, Arity),
    allowed(Name, Arity),
    Goal =.. [_ | Args],
    maplist(safe_arg, Args).

safe_arg(Arg) :-
    var(Arg),
    !.
safe_arg(Arg) :-
    atomic(Arg).

bindings_dict(Names, Dict) :-
    findall(Name-Value, (
        member(Name=Var, Names),
        term_string(Var, Value, [quoted(false)])
    ), Pairs),
    dict_create(Dict, _, Pairs).

write_error(Error) :-
    message_to_string(Error, Message),
    json_write_dict(current_output, _{error: Message}, [width(0)]),
    nl.
"""


@dataclass(frozen=True)
class KBToolCall:
    query: str
    response: str


@dataclass(frozen=True)
class ChatResponse:
    content: str
    is_error: bool = False
    tool_calls: tuple[KBToolCall, ...] = ()


class ChatController:
    """Coordinates GUI chat requests with the underlying LLM."""

    VALUE_PROPERTY_PREDICATES = {
        "alias",
        "club",
        "culture",
        "dance_style",
        "hours_per_week",
        "performances_per_year",
        "sister_club",
        "skill_level",
    }

    def __init__(
        self,
        model: str = "gemma4:e2b",
        system_prompt: str | None = None,
        thinking: bool = True,
        kb_path: str | Path | None = None,
    ) -> None:
        self.kb_path = Path(kb_path) if kb_path else Path(__file__).parent / "kb" / "clubs_kb.pl"
        full_system_prompt = self._build_system_prompt(system_prompt)
        self.llm = LLM(
            model=model,
            system_prompt=full_system_prompt,
            thinking=thinking,
            tools={"query_clubs_kb": self.query_clubs_kb},
        )
        self._responses: queue.Queue[ChatResponse] = queue.Queue()
        self._requests: queue.Queue[tuple[str, int, str]] = queue.Queue()
        self._generation_lock = threading.Lock()
        self._generation = 0
        self._kb_tool_calls: list[KBToolCall] = []
        self._worker = threading.Thread(target=self._run_worker, daemon=True)
        self._worker.start()

    @property
    def model(self) -> str:
        return self.llm.model

    def send_message(self, message: str) -> None:
        with self._generation_lock:
            generation = self._generation
        self._requests.put(("chat", generation, message))

    def get_responses(self) -> list[ChatResponse]:
        responses: list[ChatResponse] = []
        while True:
            try:
                responses.append(self._responses.get_nowait())
            except queue.Empty:
                return responses

    def clear(self) -> None:
        with self._generation_lock:
            self._generation += 1
            generation = self._generation
        self._drain_responses()
        self._requests.put(("clear", generation, ""))

    def query_clubs_kb(self, prolog_query: str) -> str:
        """Query the Cal Poly dance clubs Prolog knowledge base.

        Args:
            prolog_query: A read-only Prolog query using only the available KB
                predicates. Example: dance_style(Club, hip_hop), club(Club, Name)

        Returns:
            JSON rows containing variable bindings from the query.
        """
        result = self._query_clubs_kb(prolog_query)
        if hasattr(self, "_kb_tool_calls"):
            self._kb_tool_calls.append(
                KBToolCall(
                    query=prolog_query.strip().rstrip("."),
                    response=result,
                )
            )
        return result

    def _query_clubs_kb(self, prolog_query: str) -> str:
        query = prolog_query.strip().rstrip(".")
        if not query:
            return "No Prolog query was provided."
        if len(query) > 1000:
            return "The Prolog query is too long."
        if not self.kb_path.exists():
            return f"Knowledge base not found: {self.kb_path}"

        rows, error = self._run_prolog_query(query)
        if error:
            return error

        if not rows:
            corrected_query = self._disambiguate_reused_value_variables(query)
            if corrected_query != query:
                corrected_rows, corrected_error = self._run_prolog_query(corrected_query)
                if corrected_error:
                    return corrected_error
                if corrected_rows:
                    return (
                        "Original query returned no rows. It reused the same variable "
                        "for values from multiple specific clubs, which asks Prolog to "
                        "find one identical value. Retried with distinct value variables.\n\n"
                        f"Corrected query: {corrected_query}\n\n"
                        f"{self._format_rows(corrected_rows)}"
                    )
            return "[]"
        return self._format_rows(rows)

    def _run_prolog_query(self, query: str) -> tuple[list[dict[str, str]] | None, str | None]:
        helper = NamedTemporaryFile("w", suffix=".pl", delete=False)
        try:
            helper.write(PROLOG_QUERY_HELPER)
            helper.flush()
            helper.close()
            try:
                completed = subprocess.run(
                    [
                        "swipl",
                        "-q",
                        "-s",
                        str(self.kb_path),
                        "-s",
                        helper.name,
                    ],
                    capture_output=True,
                    input=query,
                    text=True,
                    timeout=10,
                    check=False,
                )
            except FileNotFoundError:
                return None, "SWI-Prolog is not installed or swipl is not on PATH."
            except subprocess.TimeoutExpired:
                return None, "The Prolog query timed out."
        finally:
            Path(helper.name).unlink(missing_ok=True)

        output = completed.stdout.strip()
        if completed.returncode != 0:
            error = completed.stderr.strip() or output or "Unknown Prolog error."
            return None, f"Prolog query failed: {error}"

        try:
            payload = json.loads(output)
        except json.JSONDecodeError:
            return None, output or "The Prolog query returned no output."

        if "error" in payload:
            return None, f"Prolog query failed: {payload['error']}"

        return payload.get("rows", []), None

    @staticmethod
    def _format_rows(rows: list[dict[str, str]]) -> str:
        return json.dumps(rows[:50], indent=2, ensure_ascii=False)

    def _disambiguate_reused_value_variables(self, query: str) -> str:
        predicate_names = "|".join(sorted(self.VALUE_PROPERTY_PREDICATES))
        call_pattern = re.compile(rf"\b(?P<name>{predicate_names})\s*\((?P<args>[^()]*)\)")
        variable_uses: dict[str, list[tuple[int, int]]] = {}

        for match in call_pattern.finditer(query):
            args = self._split_args_with_spans(match.group("args"), match.start("args"))
            if len(args) < 2:
                continue

            first_arg = args[0][0].strip()
            raw_value_arg, value_start, _ = args[1]
            value_arg = raw_value_arg.strip()
            if not self._is_ground_atom(first_arg) or not self._is_variable(value_arg):
                continue

            stripped_start = value_start + len(raw_value_arg) - len(raw_value_arg.lstrip())
            stripped_end = value_start + len(raw_value_arg.rstrip())
            variable_uses.setdefault(value_arg, []).append((stripped_start, stripped_end))

        replacements: list[tuple[int, int, str]] = []
        for variable, spans in variable_uses.items():
            if len(spans) < 2:
                continue
            for index, (start, end) in enumerate(spans, start=1):
                replacements.append((start, end, f"{variable}{index}"))

        corrected_query = query
        for start, end, replacement in sorted(replacements, reverse=True):
            corrected_query = corrected_query[:start] + replacement + corrected_query[end:]
        return corrected_query

    @staticmethod
    def _split_args_with_spans(args: str, offset: int) -> list[tuple[str, int, int]]:
        spans: list[tuple[str, int, int]] = []
        start = 0
        for index, char in enumerate(args):
            if char == ",":
                spans.append((args[start:index], offset + start, offset + index))
                start = index + 1
        spans.append((args[start:], offset + start, offset + len(args)))
        return spans

    @staticmethod
    def _is_variable(value: str) -> bool:
        return value != "_" and re.fullmatch(r"[A-Z_][A-Za-z0-9_]*", value) is not None

    @staticmethod
    def _is_ground_atom(value: str) -> bool:
        return re.fullmatch(r"[a-z][A-Za-z0-9_]*|'[^']+'|[0-9]+", value) is not None

    def _run_worker(self) -> None:
        while True:
            command, generation, message = self._requests.get()
            if command == "clear":
                self.llm.clear()
            elif command == "chat":
                self._request_response(message, generation)

    def _request_response(self, message: str, generation: int) -> None:
        try:
            if self._is_stale(generation):
                return
            self._kb_tool_calls = []
            content = self.llm.chat(message)
            tool_calls = tuple(self._kb_tool_calls)
            if self._is_stale(generation):
                return
            self._responses.put(ChatResponse(content=content, tool_calls=tool_calls))
        except Exception as exc:
            if self._is_stale(generation):
                return
            self._responses.put(ChatResponse(content=f"**Error:** {exc}", is_error=True))

    def _is_stale(self, generation: int) -> bool:
        with self._generation_lock:
            return generation != self._generation

    def _drain_responses(self) -> None:
        while True:
            try:
                self._responses.get_nowait()
            except queue.Empty:
                return

    @staticmethod
    def _build_system_prompt(system_prompt: str | None) -> str:
        if system_prompt:
            return f"{system_prompt.rstrip()}\n\n{KB_SYSTEM_PROMPT}"
        return KB_SYSTEM_PROMPT
