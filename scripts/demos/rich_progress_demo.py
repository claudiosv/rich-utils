#!/usr/bin/env -S uv run --script
"""Demo for `rich_progress`."""

import time

from rich_utils.progress import rich_progress


def do_work(_item: str) -> None:
    time.sleep(0.05)


def main() -> None:
    items = [f"job-{i:02d}" for i in range(1, 26)]
    with rich_progress(total=len(items), description="Working...") as (
        _progress,
        _task,
        wrap,
    ):
        for item in items:
            wrap(do_work, item)


if __name__ == "__main__":
    main()
