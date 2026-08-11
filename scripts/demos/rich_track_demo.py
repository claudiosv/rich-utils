#!/usr/bin/env -S uv run --script
"""Demo for `rich_track`."""

import time

from rich_utils.progress import rich_track


def main() -> None:
    items = [f"file_{i:02d}.py" for i in range(1, 26)]
    for _item in rich_track(items, description="Scanning files..."):
        time.sleep(0.05)


if __name__ == "__main__":
    main()
