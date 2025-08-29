import re


def split_words(name: str):
    """
    Split identifier into words in an acronym-aware way.
    Keeps acronyms (e.g. HTTP, XML) as single units.
    """
    if not name:
        return []

    # Replace separators with underscore
    s = re.sub(r'[-\s]', '_', name)

    # Split into words while keeping acronyms
    return re.findall(
        r'[A-Z]+(?=[A-Z][a-z]|[0-9]|\b)|'  # acronyms (HTTP, XML, ID)
        r'[A-Z][a-z0-9]*|'
        r'[a-z0-9]+',
        s
    )


def normalize_word(word: str, upper_first: bool) -> str:
    """Normalize a split word (acronyms become capitalized words)."""
    if not word:
        return ""
    if upper_first:
        return word[0].upper() + word[1:].lower()
    return word.lower()


def to_camel_case(name: str) -> str:
    """Convert name to camel case."""
    words = split_words(name)
    if not words:
        return ""
    return words[0].lower() + ''.join(normalize_word(w, True) for w in words[1:])


def to_pascal_case(name: str) -> str:
    """Convert name to pascal case."""
    words = split_words(name)
    return ''.join(normalize_word(w, True) for w in words)


def to_snake_case(name: str) -> str:
    """Convert name to snake case."""
    words = split_words(name)
    return '_'.join(w.lower() for w in words)
