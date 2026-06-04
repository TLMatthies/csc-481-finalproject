"""
generate_kb.py
Converts data/clubs.json into a Prolog knowledge base at kb/clubs_kb.pl.
Run with: python generate_kb.py
"""

import json
import re
from pathlib import Path


def to_atom(text: str) -> str:
    """Convert a human-readable string to a safe Prolog atom (lowercase, underscores)."""
    import unicodedata
    # Normalize unicode → decompose accents, then drop non-ASCII
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)   # replace non-alphanumeric runs with _
    text = text.strip("_")
    return text

def pl_bool(val) -> str:
    """Convert Python bool / None to a Prolog atom."""
    if val is True:
        return "true"
    if val is False:
        return "false"
    return "unknown"

def pl_val(val) -> str:
    """Render a scalar value as a Prolog term."""
    if val is None:
        return "unknown"
    if isinstance(val, bool):
        return pl_bool(val)
    if isinstance(val, (int, float)):
        return str(val)
    return to_atom(str(val))

def pl_list(items: list) -> str:
    """Render a Python list as a Prolog list of atoms."""
    return "[" + ", ".join(to_atom(i) for i in items) + "]"

# ── main ──────────────────────────────────────────────────────────────────────

def generate(json_path: str = "data/clubs.json",
             out_path:  str = "kb/clubs_kb.pl") -> None:

    # Resolve paths relative to this script's directory, not the cwd
    base = Path(__file__).parent
    json_path = base / json_path
    out_path  = base / out_path

    if not json_path.exists():
        raise FileNotFoundError(
            f"clubs.json not found at expected path: {json_path.resolve()}. "
            "Place the data file there and re-run."
        )

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    lines: list[str] = []

    lines += [
        "%% clubs_kb.pl",
        "%% Auto-generated from data/clubs.json — do not edit by hand.",
        "%% Regenerate with:  python generate_kb.py",
        "%%",
        "%% Facts",
        "%%   club/2            club(Atom, DisplayName)",
        "%%   alias/2           alias(ClubAtom, AliasAtom)",
        "%%   hours_per_week/2  hours_per_week(ClubAtom, Hours)",
        "%%   performances_per_year/2",
        "%%   competes/1        competes(ClubAtom)          — only asserted when true",
        "%%   travels/1         travels(ClubAtom)",
        "%%   performs_downtown/1",
        "%%   collects_dues/1",
        "%%   big_little/1",
        "%%   performance_contract/1",
        "%%   does_covers/1",
        "%%   dance_style/2     dance_style(ClubAtom, StyleAtom)",
        "%%   culture/2         culture(ClubAtom, CultureAtom)",
        "%%   skill_level/2     skill_level(ClubAtom, Level)  — beginner/intermediate/advanced",
        "%%   sister_club/2     sister_club(ClubA, ClubB)     — bidirectional",
        "%%",
        "%% Rules",
        "%%   clubs_with_style/2, clubs_with_culture/2, beginner_friendly/1,",
        "%%   low_commitment/2, high_performance/2, recommend/3",
        "",
        ":- discontiguous club/2, alias/2, hours_per_week/2, performances_per_year/2.",
        ":- discontiguous competes/1, travels/1, performs_downtown/1.",
        ":- discontiguous collects_dues/1, big_little/1, performance_contract/1, does_covers/1.",
        ":- discontiguous dance_style/2, culture/2, skill_level/2, sister_club/2.",
        "",
    ]

   
    for club in data["clubs"]:
        name_display = club["name"]
        atom = to_atom(name_display)

        lines.append(f"%% {name_display}")
        lines.append(f"club({atom}, '{name_display}').")

        # optional alias
        if club.get("alias"):
            lines.append(f"alias({atom}, {to_atom(club['alias'])}).")

        # scalar numeric facts
        if club.get("hours_per_week") is not None:
            lines.append(f"hours_per_week({atom}, {club['hours_per_week']}).")
        if club.get("performances_per_year") is not None:
            lines.append(f"performances_per_year({atom}, {club['performances_per_year']}).")

        # boolean facts — only assert when true (closed-world: absence = false)
        for field, predicate in [
            ("competes",             "competes"),
            ("travels",              "travels"),
            ("performs_downtown",    "performs_downtown"),
            ("collects_dues",        "collects_dues"),
            ("big_little_program",   "big_little"),
            ("performance_contract", "performance_contract"),
            ("does_covers",          "does_covers"),
        ]:
            if club.get(field) is True:
                lines.append(f"{predicate}({atom}).")

        # list facts
        for style in (club.get("dance_styles") or []):
            lines.append(f"dance_style({atom}, {to_atom(style)}).")

        for culture in (club.get("cultural_association") or []):
            lines.append(f"culture({atom}, {to_atom(culture)}).")

        for level in (club.get("skill_levels") or []):
            lines.append(f"skill_level({atom}, {to_atom(level)}).")

        # sister clubs — emit both directions so the relation is symmetric
        for sister in (club.get("sister_clubs") or []):
            s_atom = to_atom(sister)
            lines.append(f"sister_club({atom}, {s_atom}).")

        lines.append("")

    lines += [
        "%% ── Rules ──────────────────────────────────────────────────────────",
        "",
        "%% Which clubs perform a given dance style?",
        "%% ?- clubs_with_style(hip_hop, X).",
        "clubs_with_style(Style, Club) :-",
        "    dance_style(Club, Style).",
        "",
        "%% Which clubs are associated with a given culture?",
        "%% ?- clubs_with_culture(korean, X).",
        "clubs_with_culture(Culture, Club) :-",
        "    culture(Club, Culture).",
        "",
        "%% Clubs that accept beginners.",
        "beginner_friendly(Club) :-",
        "    skill_level(Club, beginner).",
        "",
        "%% Clubs with at most MaxHours practice hours per week.",
        "%% ?- low_commitment(3, X).",
        "low_commitment(MaxHours, Club) :-",
        "    hours_per_week(Club, H),",
        "    H =< MaxHours.",
        "",
        "%% Clubs that perform at least MinPerfs times per year.",
        "%% ?- high_performance(6, X).",
        "high_performance(MinPerfs, Club) :-",
        "    performances_per_year(Club, P),",
        "    P >= MinPerfs.",
        "",
        "%% General recommendation: style + skill level.",
        "%% ?- recommend(hip_hop, beginner, X).",
        "recommend(Style, Level, Club) :-",
        "    dance_style(Club, Style),",
        "    skill_level(Club, Level).",
        "",
        "%% Clubs that do NOT collect dues.",
        "free_to_join(Club) :-",
        "    club(Club, _),",
        "    \\+ collects_dues(Club).",
        "",
        "%% Clubs with a big/little mentorship program.",
        "has_mentorship(Club) :-",
        "    big_little(Club).",
        "",
        "%% Clubs that compete AND travel.",
        "competitive_travel(Club) :-",
        "    competes(Club),",
        "    travels(Club).",
        "",
    ]

    out = "\n".join(lines)
    Path(out_path).write_text(out, encoding="utf-8")
    print(f"Written {out_path}  ({len(lines)} lines, {len(data['clubs'])} clubs)")


if __name__ == "__main__":
    generate()
