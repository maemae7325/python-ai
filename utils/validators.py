import re

_INJECTION_PATTERNS = [
    r"以上の指示を無視",
    r"上記の指示を無視",
    r"指示を無視",
    r"プロンプトを無視",
    r"システムプロンプト",
    r"あなたの役割を(変更|忘れ|無視)",
    r"ignore\s+(previous|all|above|your)?\s*instructions?",
    r"forget\s+(your|all|previous)?\s*instructions?",
    r"disregard\s+(your|all|previous)?\s*instructions?",
    r"system\s*prompt",
    r"you\s+are\s+now",
    r"new\s+instructions?",
]

_PATTERN = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)


def contains_injection(*texts: str) -> bool:
    return any(_PATTERN.search(t) for t in texts if t)
