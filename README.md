# rich-utils

Small collection of [Rich](https://github.com/Textualize/rich)-based progress bar and
tracking utilities: a pandas `.progress_apply` integration, a context-manager and
generator-based progress helper, a live "tracker" widget with a spinner header, a
human-readable rate/throughput column, and a self-contained animated "shimmer" progress
display for CLI tools.

<!-- demo:start -->
![Demo of every rich-utils helper running in sequence: rich_track, RichTracker, rich_progress, rich_pandas, RateColumn, and ShimmerProgress](https://github.com/user-attachments/assets/2dd860c2-13cc-46bc-b47b-e8e7bd28e7eb)

<sub>Prefer a WebM? [WebM](https://github.com/user-attachments/assets/02e5e28f-9054-443c-9de1-63deaabf921b)</sub>
<!-- demo:end -->

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
from rich_utils.progress import rich_track

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
    for item in items:
        # `wrap` calls the function, advances the task, and (with
        # use_rate_column_class=False) records how long the call took.
        wrap(do_work, item)
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

### Demos

Each helper has a standalone, runnable demo script under `scripts/demos/`:

```bash
uv run python scripts/demos/rich_track_demo.py
uv run python scripts/demos/rich_tracker_demo.py
uv run python scripts/demos/rich_progress_demo.py
uv run python scripts/demos/rich_pandas_demo.py
uv run python scripts/demos/rate_column_demo.py
uv run python scripts/demos/shimmer_progress_demo.py
```

`scripts/run_all_demos.py` runs all of them back to back, and
`scripts/build_demo_gif.sh` re-records it with [VHS](https://github.com/charmbracelet/vhs)
(GIF + WebM), uploads both via the [`gh-image`](https://github.com/drogers0/gh-image) `gh`
extension, and rewrites the demo embed at the top of this README (between the demo-block
HTML comment markers) to point at the freshly uploaded files:

```bash
uv run python scripts/run_all_demos.py   # run every demo in one go
./scripts/build_demo_gif.sh              # re-record, upload, and update the README
```

Requires `vhs` (`brew install vhs`) and `gh` authenticated against this repo.
