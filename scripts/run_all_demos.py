#!/usr/bin/env -S uv run --script
"""Run every demo in scripts/demos/ back to back, for recording purposes."""

import time

from demos import (
    rate_column_demo,
    rich_pandas_demo,
    rich_progress_demo,
    rich_track_demo,
    rich_tracker_demo,
    shimmer_progress_demo,
)
from rich.console import Console

console = Console()

DEMOS = [
    ("rich_track", rich_track_demo.main),
    ("RichTracker", rich_tracker_demo.main),
    ("rich_progress", rich_progress_demo.main),
    ("rich_pandas", rich_pandas_demo.main),
    ("RateColumn", rate_column_demo.main),
    ("ShimmerProgress", shimmer_progress_demo.main),
]


def main() -> None:
    for name, demo in DEMOS:
        console.rule(f"[bold cyan]{name}")
        demo()
        time.sleep(0.4)


if __name__ == "__main__":
    main()
