from dataclasses import dataclass, field
from pathlib import Path

from services.backup import save_backup
from services.detector import is_dumbbell_exercise
from services.hevy_client import HevyClient
from services.transformer import CorrectionMode, transform_weight
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ChangeRecord:
    workout_id: str
    exercise_name: str
    set_index: int
    old_weight: float | None
    new_weight: float | None
    status: str = "modified"


@dataclass
class ProcessResult:
    updated_workouts: int = 0
    modified_sets: int = 0
    skipped_sets: int = 0
    backup_path: Path | None = None
    changes: list[ChangeRecord] = field(default_factory=list)


def _build_updated_workout(workout: dict, mode: CorrectionMode, client: HevyClient) -> tuple[dict, list[ChangeRecord]]:
    changes: list[ChangeRecord] = []
    updated_exercises = []

    _exercise_ro = {"index", "id", "title"}
    _set_ro = {"index", "id"}

    for exercise in workout.get("exercises", []):
        template_id = exercise.get("exercise_template_id")
        template = client.get_exercise_template(template_id) if template_id else None
        if not is_dumbbell_exercise(exercise, template):
            updated_exercises.append({k: v for k, v in exercise.items() if k not in _exercise_ro})
            continue

        updated_sets = []
        for i, s in enumerate(exercise.get("sets", [])):
            old_w = s.get("weight_kg")

            if old_w is None or not isinstance(old_w, (int, float)):
                updated_sets.append({k: v for k, v in s.items() if k not in _set_ro})
                changes.append(
                    ChangeRecord(
                        workout_id=workout["id"],
                        exercise_name=exercise.get("title", ""),
                        set_index=i,
                        old_weight=old_w,
                        new_weight=old_w,
                        status="skipped_invalid",
                    )
                )
                continue

            new_w = transform_weight(old_w, mode)

            if new_w == old_w:
                updated_sets.append({k: v for k, v in s.items() if k not in _set_ro})
                changes.append(
                    ChangeRecord(
                        workout_id=workout["id"],
                        exercise_name=exercise.get("title", ""),
                        set_index=i,
                        old_weight=old_w,
                        new_weight=new_w,
                        status="skipped_no_change",
                    )
                )
                continue

            changes.append(
                ChangeRecord(
                    workout_id=workout["id"],
                    exercise_name=exercise.get("title", ""),
                    set_index=i,
                    old_weight=old_w,
                    new_weight=new_w,
                    status="modified",
                )
            )
            updated_sets.append({k: v for k, v in s.items() if k not in _set_ro} | {"weight_kg": new_w})

        updated_exercises.append({k: v for k, v in exercise.items() if k not in _exercise_ro} | {"sets": updated_sets})

    return {**workout, "exercises": updated_exercises}, changes


def process(client: HevyClient, mode: CorrectionMode, dry_run: bool) -> ProcessResult:
    result = ProcessResult()

    logger.info(f"Fetching all workouts (mode={mode.value}, dry_run={dry_run})")
    all_workouts = list(client.iter_workouts())
    logger.info(f"Fetched {len(all_workouts)} workouts total")

    if not dry_run:
        result.backup_path = save_backup(all_workouts)
        logger.info(f"Backup saved → {result.backup_path}")

    for workout in all_workouts:
        updated_workout, changes = _build_updated_workout(workout, mode, client)

        modified = [c for c in changes if c.status == "modified"]
        skipped = [c for c in changes if c.status != "modified"]

        result.modified_sets += len(modified)
        result.skipped_sets += len(skipped)
        result.changes.extend(changes)

        for c in modified:
            tag = "DRY RUN" if dry_run else "APPLY"
            logger.info(
                f"[{tag}] workout={c.workout_id} exercise={c.exercise_name!r} "
                f"set={c.set_index} {c.old_weight}kg → {c.new_weight}kg"
            )

        if modified and not dry_run:
            client.update_workout(workout["id"], updated_workout)
            result.updated_workouts += 1
            logger.info(f"Updated workout {workout['id']}")

    return result
