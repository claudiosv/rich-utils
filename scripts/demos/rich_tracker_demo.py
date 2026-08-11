#!/usr/bin/env -S uv run --script
"""Demo for `RichTracker`."""

import time

from rich_utils.progress import RichTracker


def main() -> None:
    items = range(1, 26)
    with RichTracker(description="Crunching numbers", total=len(items)) as tracker:
        tracker.start()
        for _item in tracker.track(items):
            time.sleep(0.05)


if __name__ == "__main__":
    main()
