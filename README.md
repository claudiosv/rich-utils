# rich-utils

Small collection of [Rich](https://github.com/Textualize/rich)-based progress bar and
tracking utilities: a pandas `.progress_apply` integration, a context-manager and
generator-based progress helper, a live "tracker" widget with a spinner header, a
human-readable rate/throughput column, and a self-contained animated "shimmer" progress
display for CLI tools.

## Installation

```bash
uv add rich-utils
```

or, from a local checkout:

```bash
uv sync
```

Requires Python 3.14+.

## Usage

### `rich_track` — drop-in `tqdm`-style iterator wrapper

```python
from rich_utils import rich_track

for item in rich_track(range(100), description="Processing..."):
    ...
```

### `RichTracker` — a live tracker with a spinner header

```python
from rich_utils.progress import RichTracker

with RichTracker(description="Crunching numbers", total=100) as tracker:
    for item in tracker.track(range(100)):
        ...
```

### `rich_progress` — context manager over a preconfigured `rich.progress.Progress`

```python
from rich_utils.progress import rich_progress

with rich_progress(total=100, description="Working...") as (progress, task, wrap):
    for _ in range(100):
        progress.advance(task)  # advance manually, or...
        wrap(some_function, arg)  # ...call `wrap` to run + advance + track speed in one step
```

### `rich_pandas` — `progress_apply` for pandas DataFrames

```python
import pandas as pd
from rich_utils.progress import rich_pandas

rich_pandas()  # monkey-patches DataFrame.progress_apply
df = pd.DataFrame({"a": range(1000)})
df.progress_apply(lambda row: row["a"] * 2, description="Doubling")
```

### `RateColumn` — human-readable rate column for `rich.progress.Progress`

```python
from rich.progress import Progress
from rich_utils.rate_column import RateColumn

with Progress(RateColumn(unit="rows")) as progress:
    ...
```

### `ShimmerProgress` — animated phase-based progress display

```python
from rich_utils.shimmer_progress import ShimmerProgress

with ShimmerProgress() as progress:
    for i in range(1, 101):
        progress.on_progress("Scanning", current=i, total=100)
```

## Development

```bash
uv sync                                                          # install deps
uv run pytest                                                    # run tests
uv run pytest --cov=rich_utils --cov-report=html --cov-report=term-missing
open htmlcov/index.html                                          # view coverage report
```
