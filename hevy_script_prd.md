# PRD: Hevy Dumbbell Weight Correction Tool (Script-Based)

## 1. Meta

```yaml
name: hevy-dumbbell-corrector-script
type: batch_script
language: python
external_api: Hevy
```

## 2. Objective

```yaml
goal: >
  Correct historical dumbbell weights in all Hevy workouts using a Python CLI script with a clean service layer.
```

## 3. Scope

```yaml
in_scope:
  - fetch_workouts
  - detect_dumbbell_exercises
  - transform_weights
  - backup_data
  - dry_run_preview
  - apply_changes

out_of_scope:
  - web_ui
  - real_time_tracking
  - multi_user_support
```

## 4. Inputs

```yaml
inputs:
  - api_key: string
  - correction_mode: enum[divide, multiply]
  - dry_run: boolean
```

## 5. Outputs

```yaml
outputs:
  - updated_workouts: int
  - modified_sets: int
  - skipped_sets: int
  - backup_file: json
  - logs: file
```

## 6. Architecture

```yaml
layers:
  - cli_entry
  - services
  - external_api_client
```

## 7. Project Structure

```yaml
structure:
  - run.py
  - services/
    - processor.py
    - transformer.py
    - detector.py
    - hevy_client.py
    - backup.py
  - utils/
    - logger.py
  - config.py
  - data/
    - backups/
    - logs/
```

## 8. Core Logic

### Detection

```yaml
rule: exercise.name contains ["dumbbell", "db"]
```

### Transformation

```yaml
divide: new_weight = old_weight / 2
multiply: new_weight = old_weight * 2
```

### Idempotency

```yaml
rule: skip if new_weight == old_weight
```

## 9. Workflow

```yaml
steps:
  - load_config
  - fetch_workouts
  - filter_date_range
  - detect_dumbbell_exercises
  - transform_weights
  - preview_changes
  - backup_data
  - if dry_run == false:
      - apply_updates
  - log_results
```

## 10. CLI Interface

```yaml
commands:
  - python run.py --dry-run
  - python run.py --apply
```

## 11. Backup

```yaml
backup:
  format: json
  filename: backup_<timestamp>.json
  content: full_original_data
```

## 12. Logging

```yaml
logging:
  fields:
    - workout_id
    - exercise_name
    - set_index
    - old_weight
    - new_weight
    - status
```

## 13. Error Handling

```yaml
errors:
  - api_failure: retry
  - rate_limit: delay
  - invalid_data: skip
```

## 14. Constraints

```yaml
constraints:
  - modify_only_dumbbell_exercises
  - must_backup_before_apply
  - must_support_dry_run
```

## 15. Edge Cases

```yaml
edge_cases:
  - null_weight
  - zero_weight
  - already_corrected
  - non_numeric_values
```

## 16. Success Criteria

```yaml
success:
  - no_data_loss
  - correct_transformation
  - reproducible_runs
```
