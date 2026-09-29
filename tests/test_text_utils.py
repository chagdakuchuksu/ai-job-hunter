from app.utils.text import normalize_text, word_count


def test_normalize_collapses_whitespace_and_blank_lines():
    raw = "  Hello\t\tworld  \r\n\r\n\r\n\r\nNext   line  "
    assert normalize_text(raw) == "Hello world\n\nNext line"


def test_normalize_unicode_ligatures():
    assert normalize_text("ﬁle") == "file"


def test_word_count():
    assert word_count("one two\nthree") == 3
