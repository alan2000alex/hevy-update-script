import re

# Matches "dumbbell" or standalone "db" (word boundary), case-insensitive
_DUMBBELL_RE = re.compile(r"\bdumbbell\b|\bdb\b", re.IGNORECASE)


def is_dumbbell_exercise(exercise: dict) -> bool:
    title = exercise.get("title") or exercise.get("name") or ""
    return bool(_DUMBBELL_RE.search(title))
