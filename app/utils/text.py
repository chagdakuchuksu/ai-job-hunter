"""Small text helpers shared by the CV and job description services."""

import re
import unicodedata

_SPACES = re.compile(r"[ \t\f\v ]+")
_MANY_NEWLINES = re.compile(r"\n{3,}")


def normalize_text(text: str) -> str:
    """Clean up whitespace and unicode so texts can be compared consistently.

    - NFKC unicode normalization (e.g. ligatures like "ﬁ" -> "fi")
    - unify line endings, collapse runs of spaces/tabs
    - strip each line and collapse 3+ blank lines into one blank line
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_SPACES.sub(" ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    return _MANY_NEWLINES.sub("\n\n", text).strip()


def word_count(text: str) -> int:
    return len(text.split())
