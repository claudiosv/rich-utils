#!/usr/bin/env -S uv run --script
"""Demo for `RateColumn`."""

import time

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
)

from rich_utils.rate_column import RateColumn


def main() -> None:
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        RateColumn(unit="rows"),
    ) as progress:
        task = progress.add_task("Importing rows...", total=25)
        for _ in range(25):
            time.sleep(0.05)
            progress.advance(task)


if __name__ == "__main__":
    main()
