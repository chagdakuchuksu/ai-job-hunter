"""Deterministic skill extraction based on a configurable dictionary.

This is keyword matching, not real NLP: it finds known skill names and
aliases in text. It cannot tell "Python required" from "no Python needed",
and it only knows the skills listed in app/data/skills.json.
"""

import json
import re
from functools import lru_cache
from pathlib import Path

SKILLS_FILE = Path(__file__).resolve().parent.parent / "data" / "skills.json"

# Token boundaries. A skill only matches as a whole token, so "Java" does not
# match inside "JavaScript", "C" not inside "C++"/"C#", "SQL" not inside
# "PostgreSQL", "Go" not inside "good"/"Google", and "js" not inside "Node.js".
_NOT_BEFORE = r"(?<![\w+#.])"
_NOT_AFTER = r"(?![\w+#])"
# Extra rule for very short case-sensitive aliases (C, Go, CI): "C-level" and
# "Go-to-market" are ordinary phrases, not skills.
_NOT_AFTER_SHORT = r"(?![\w+#]|-\w)"


def _load_config(path: Path = SKILLS_FILE) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_skill_dictionary(path: Path = SKILLS_FILE) -> dict[str, list[str]]:
    return _load_config(path)["skills"]


def _alias_pattern(alias: str, case_sensitive: bool) -> re.Pattern[str]:
    words = [re.escape(word) for word in re.split(r"[\s-]+", alias.strip())]
    body = r"[\s-]+".join(words)
    after = _NOT_AFTER_SHORT if case_sensitive and len(alias) <= 2 else _NOT_AFTER
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(_NOT_BEFORE + body + after, flags)


@lru_cache(maxsize=1)
def _compiled_skills() -> list[tuple[str, list[re.Pattern[str]]]]:
    config = _load_config()
    case_sensitive = set(config.get("case_sensitive_aliases", []))
    return [
        (name, [_alias_pattern(alias, alias in case_sensitive) for alias in {name, *aliases}])
        for name, aliases in config["skills"].items()
    ]


def extract_skills(text: str) -> list[str]:
    """Return the canonical names of all known skills found in `text`, sorted."""
    found = [
        name
        for name, patterns in _compiled_skills()
        if any(p.search(text) for p in patterns)
    ]
    return sorted(found, key=str.lower)
