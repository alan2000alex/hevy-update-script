# hevy-update-tool

A CLI tool that corrects historical dumbbell weights across all your [Hevy](https://hevy.com) workouts. If you've been logging per-dumbbell weights instead of total load (or vice versa), this tool divides or multiplies every dumbbell set's weight by 2 in bulk.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (dependency manager)
- A Hevy API key

## Installation

```bash
git clone https://github.com/yourusername/hevy-update-tool.git
cd hevy-update-tool
uv sync
```

## Configuration

Provide your Hevy API key via environment variable or the `--api-key` flag:

```bash
export HEVY_API_KEY=your_api_key_here
```

## Usage

**Always do a dry run first** to preview what will change before writing anything.

```bash
# Preview changes (default — nothing is written)
uv run python run.py --dry-run --mode divide

# Apply changes
uv run python run.py --apply --mode divide

# Multiply instead of divide (if you logged totals and need per-dumbbell)
uv run python run.py --apply --mode multiply

# Pass the API key inline
uv run python run.py --apply --mode divide --api-key your_api_key_here
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--dry-run` / `--apply` | `--dry-run` | Preview changes or write them |
| `--mode divide\|multiply` | `divide` | Divide weights by 2 or multiply by 2 |
| `--api-key` | `$HEVY_API_KEY` | Hevy API key |

### Output

```
Mode: divide | DRY RUN (no changes will be written)

Summary
  Updated workouts : 0
  Modified sets    : 42
  Skipped sets     : 7

42 sets would be changed. Run with --apply to commit.
```

## How It Works

1. **Fetch** — pages through all workouts via the Hevy API.
2. **Detect** — identifies dumbbell exercises by checking the exercise template's `equipment` field first, then falling back to name matching (`dumbbell` or `db`, case-insensitive).
3. **Transform** — divides or multiplies `weight_kg` by 2, rounded to 4 decimal places. Sets with `null` or zero weight are skipped unchanged.
4. **Backup** — before writing anything, saves a full JSON snapshot of all workouts to `data/backups/backup_<timestamp>.json`.
5. **Apply** — updates each workout via the Hevy API, appending a note to each modified exercise for traceability.

Runs are idempotent: sets where the transformation would produce no change are skipped.

## Project Structure

```
hevy-update-tool/
├── run.py                 # CLI entry point (Typer)
├── config.py              # API key and base URL config
├── services/
│   ├── hevy_client.py     # Hevy API client (GET/PUT with retry + rate-limit backoff)
│   ├── detector.py        # Dumbbell exercise detection
│   ├── transformer.py     # Weight divide/multiply logic
│   ├── processor.py       # Orchestrates fetch → detect → transform → apply
│   └── backup.py          # JSON backup writer
├── utils/
│   └── logger.py          # Structured logging
└── data/
    ├── backups/            # Pre-apply snapshots
    └── logs/              # Run logs
```

## Logs

Logs are written to `data/logs/hevy_update.log`. Each modified set is recorded with workout ID, exercise name, set index, and the before/after weight.

## Safety

- Default mode is `--dry-run` — no accidental writes.
- A full backup is saved before any API writes occur.
- The tool only modifies detected dumbbell exercises; all other exercises are passed through unchanged.
- API requests retry up to 3 times with exponential backoff on rate limits and transient errors.

## Planned Features

### Workout Selection
- Select a single workout by ID to modify only that workout.
- Select workouts in a date range (`--from`/`--to` flags) instead of processing all workouts.
- Select the N most recent workouts (`--last N`).
- Select workouts by exercise name (e.g. only workouts that contain a specific exercise).

### Performance
- Cache exercise template GET responses so each template is fetched at most once per run, rather than re-fetched for every workout that contains it.
