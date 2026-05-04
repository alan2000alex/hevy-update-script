import re

# Matches "dumbbell" or standalone "db" (word boundary), case-insensitive
_DUMBBELL_RE = re.compile(r"\bdumbbell\b|\bdb\b", re.IGNORECASE)


def is_dumbbell_exercise(exercise: dict, template: dict | None = None) -> bool:
    if template is not None and "equipment" in template:
        return template["equipment"] == "dumbbell"
    title = exercise.get("title") or exercise.get("name") or ""
    return bool(_DUMBBELL_RE.search(title))
