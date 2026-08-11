#!/usr/bin/env -S uv run --script
"""Demo for `rich_pandas`."""

import time

import pandas as pd

from rich_utils.progress import rich_pandas


def main() -> None:
    rich_pandas()
    df = pd.DataFrame({"value": range(1, 26)})

    def double(row: pd.Series) -> int:
        time.sleep(0.05)
        return row["value"] * 2

    df.progress_apply(double, description="Doubling")


if __name__ == "__main__":
    main()
