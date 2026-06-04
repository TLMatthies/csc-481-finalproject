"""Unit tests for KB_SYSTEM_PROMPT content — Requirements 2.1, 2.2, 2.3, 2.6"""

from chat_controller import KB_SYSTEM_PROMPT


def test_contains_sequential_query_instruction():
    """Req 2.1 — prompt must instruct LLM to issue one query per club."""
    prompt_lower = KB_SYSTEM_PROMPT.lower()
    # Should mention issuing separate/sequential queries per club
    assert "one" in prompt_lower or "separate" in prompt_lower or "sequential" in prompt_lower
    assert "club" in prompt_lower


def test_contains_always_use_tool_directive():
    """Req 2.1 — prompt must explicitly direct LLM to always call query_clubs_kb."""
    assert "query_clubs_kb" in KB_SYSTEM_PROMPT
    # Strong directive: MUST or ALWAYS or CRITICAL
    directive_words = {"must", "always", "critical", "never answer from memory"}
    prompt_lower = KB_SYSTEM_PROMPT.lower()
    assert any(word in prompt_lower for word in directive_words), (
        "Prompt should contain a strong directive (MUST/ALWAYS/CRITICAL) to use the tool"
    )


def test_contains_at_least_two_correct_example_queries():
    """Req 2.2 — prompt must show ≥2 correct sequential query examples."""
    # Count lines that look like Prolog query calls (contain a predicate with parens
    # and a comma-separated variable)
    import re
    example_lines = [
        line for line in KB_SYSTEM_PROMPT.splitlines()
        if re.search(r"\w+\(\w+,\s*[A-Z]\w*\)", line)
    ]
    assert len(example_lines) >= 2, (
        f"Expected ≥2 example query lines, found {len(example_lines)}: {example_lines}"
    )


def test_contains_multi_variable_antipattern_description():
    """Req 2.3 — prompt must name and explain the multi-variable anti-pattern."""
    prompt_lower = KB_SYSTEM_PROMPT.lower()
    # Should mention the anti-pattern concept
    assert "anti-pattern" in prompt_lower or "do not" in prompt_lower or "never" in prompt_lower
    # Should explain zero rows result
    assert "zero rows" in prompt_lower or "no rows" in prompt_lower or "returns zero" in prompt_lower


def test_contains_prolog_unification_explanation():
    """Req 2.3 — prompt must briefly explain Prolog unification."""
    prompt_lower = KB_SYSTEM_PROMPT.lower()
    assert "unif" in prompt_lower  # unification / unify / unifies


def test_contains_displayname_instruction():
    """Req 2.6 — prompt must instruct LLM to use DisplayName, not internal atom."""
    assert "DisplayName" in KB_SYSTEM_PROMPT or "displayname" in KB_SYSTEM_PROMPT.lower()
    prompt_lower = KB_SYSTEM_PROMPT.lower()
    # Should instruct to use it in replies
    assert "user-facing" in prompt_lower or "display name" in prompt_lower or "displayname" in prompt_lower


def test_preserves_all_fact_predicates():
    """Predicate reference docs should still be present."""
    required_predicates = [
        "club(",
        "alias(",
        "hours_per_week(",
        "performances_per_year(",
        "competes(",
        "travels(",
        "performs_downtown(",
        "collects_dues(",
        "big_little(",
        "performance_contract(",
        "does_covers(",
        "dance_style(",
        "culture(",
        "skill_level(",
        "sister_club(",
    ]
    for pred in required_predicates:
        assert pred in KB_SYSTEM_PROMPT, f"Missing predicate reference: {pred}"


def test_preserves_all_rule_predicates():
    """Rule predicate reference docs should still be present."""
    required_rules = [
        "clubs_with_style(",
        "clubs_with_culture(",
        "beginner_friendly(",
        "low_commitment(",
        "high_performance(",
        "recommend(",
        "free_to_join(",
        "has_mentorship(",
        "competitive_travel(",
    ]
    for rule in required_rules:
        assert rule in KB_SYSTEM_PROMPT, f"Missing rule predicate reference: {rule}"
