#!/usr/bin/env -S uv run --script
"""Demo for `ShimmerProgress`."""

import time

from rich_utils.shimmer_progress import ShimmerProgress


def main() -> None:
    phases = [
        ("Scanning AST", 30, 0.03),
        ("Transpiling", 200, 0.02),
        ("Minifying", 50, 0.02),
    ]

    with ShimmerProgress() as progress:
        for phase_name, iterations, delay in phases:
            for i in range(1, iterations + 1):
                progress.on_progress(phase_name, current=i, total=iterations)
                time.sleep(delay)


if __name__ == "__main__":
    main()
