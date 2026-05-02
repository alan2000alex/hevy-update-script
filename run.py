from typing import Annotated

import typer

from config import load_config
from services.hevy_client import HevyClient
from services.processor import process
from services.transformer import CorrectionMode
from utils.logger import get_logger, setup_logging

app = typer.Typer(help="Correct historical dumbbell weights in Hevy workouts.")
logger = get_logger("run")


@app.command()
def main(
    mode: Annotated[
        CorrectionMode,
        typer.Option("--mode", "-m", help="Weight correction: divide by 2 or multiply by 2"),
    ] = CorrectionMode.divide,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run/--apply",
            help="Preview changes (--dry-run) or apply them (--apply)",
        ),
    ] = True,
    api_key: Annotated[
        str,
        typer.Option("--api-key", envvar="HEVY_API_KEY", help="Hevy API key"),
    ] = "",
) -> None:
    setup_logging()

    try:
        config = load_config(api_key or None)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)

    label = "DRY RUN (no changes will be written)" if dry_run else "APPLY (changes will be written)"
    typer.echo(f"Mode: {mode.value} | {label}")

    with HevyClient(config) as client:
        result = process(client, mode, dry_run)

    typer.echo("\nSummary")
    typer.echo(f"  Updated workouts : {result.updated_workouts}")
    typer.echo(f"  Modified sets    : {result.modified_sets}")
    typer.echo(f"  Skipped sets     : {result.skipped_sets}")
    if result.backup_path:
        typer.echo(f"  Backup           : {result.backup_path}")

    if dry_run and result.modified_sets > 0:
        typer.echo(f"\n{result.modified_sets} sets would be changed. Run with --apply to commit.")


if __name__ == "__main__":
    app()
