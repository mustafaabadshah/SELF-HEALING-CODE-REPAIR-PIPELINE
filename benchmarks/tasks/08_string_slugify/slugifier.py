import re

def slugify(text: str) -> str:
    # Bug: leaves consecutive hyphens and does not strip trailing hyphens
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text).lower()
    return cleaned
