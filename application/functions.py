import re


def to_camel_case(name: str) -> str:
    """Convert name to camel case."""
    words = [w for w in re.split(r'[_\-\s]|(?=[A-Z])', name) if w]
    if not words:
        return ""
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def to_pascal_case(name: str) -> str:
    """Convert name to pascal case."""
    words = [w for w in re.split(r'[_\-\s]|(?=[A-Z])', name) if w]
    return ''.join(word.capitalize() for word in words)


def to_snake_case(name: str) -> str:
    """Convert name to snake case."""
    s = re.sub(r'[-\s]', '_', name)
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', s)
    return re.sub(r'_+', '_', s).lower()
