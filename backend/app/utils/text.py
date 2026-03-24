import re

PUNCTUATION_PATTERN = re.compile(r"[^\w\s]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    cleaned = PUNCTUATION_PATTERN.sub(" ", value.lower().strip())
    return WHITESPACE_PATTERN.sub(" ", cleaned).strip()


def tokenize(value: str | None) -> set[str]:
    normalized = normalize_text(value)
    if not normalized:
        return set()
    return {token for token in normalized.split(" ") if token}
