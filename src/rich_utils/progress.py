import time
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from rich.console import Console, Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.spinner import Spinner
from rich.table import Table

from .rate_column import RateColumn

if TYPE_CHECKING:
    from collections.abc import Collection, Generator


# Define a function similar to `tqdm_pandas` for Rich
def rich_pandas(use_rate_column_class: bool = True, console: Console | None = None):
    from pandas.core.frame import DataFrame

    rate_column = (
        RateColumn()
        if use_rate_column_class
        else TextColumn("[red]{task.fields[speed]:.0f} it/s[/red]")
    )

    def inner(df, func, *args, **kwargs):
        with Progress(
            "[progress.description]{task.description}",
            TaskProgressColumn(show_speed=True),
            BarColumn(bar_width=None),
            MofNCompleteColumn(),
            TextColumn("["),
            TimeElapsedColumn(),
            TextColumn("<"),
            TimeRemainingColumn(),
            TextColumn(","),
            rate_column,
            TextColumn("]"),
            console=console,
        ) as progress:
            description = kwargs.pop("description", "Processing...")
            task = progress.add_task(f"[cyan]{description}", total=len(df), speed=0)

            def wrapper_timer(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()

                # Compute speed
                elapsed = end - start
                if elapsed > 0:
                    progress.tasks[task].fields["speed"] = round(1 / elapsed)

                progress.advance(task)
                return result

            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                progress.advance(task)
                return result

            wrapper = wrapper if use_rate_column_class else wrapper_timer

            if "axis" not in kwargs:
                kwargs["axis"] = 1
            return df.apply(wrapper, *args, **kwargs)

    DataFrame.progress_apply = inner


@contextmanager
def rich_progress(
    use_rate_column_class: bool = True, console: Console | None = None, **kwargs
):
    rate_column = (
        RateColumn()
        if use_rate_column_class
        else TextColumn("[red]{task.fields[speed]:.0f} it/s[/red]")
    )

    with Progress(
        "[progress.description]{task.description}",
        TaskProgressColumn(show_speed=True),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
        TextColumn("["),
        TimeElapsedColumn(),
        TextColumn("<"),
        TimeRemainingColumn(),
        TextColumn(","),
        rate_column,
        TextColumn("]"),
        console=console,
    ) as progress:
        description = kwargs.pop("description", "Processing...")
        speed = kwargs.pop("speed", 0)
        task = progress.add_task(description, speed=speed, **kwargs)

        def wrapper_timer(*args, **kwargs) -> None:
            start = time.time()
            # result = func(*args, **kwargs)
            end = time.time()

            # Compute speed
            elapsed = end - start
            if elapsed > 0:
                progress.tasks[task].fields["speed"] = round(1 / elapsed)

            progress.advance(task)

        def wrapper(*args, **kwargs) -> None:
            # result = func(*args, **kwargs)
            progress.advance(task)
            # return result

        wrapper = wrapper if use_rate_column_class else wrapper_timer

        yield progress, task


def rich_track(
    iterable: Collection,
    description: str = "Processing...",
    console: Console | None = None,
):
    with Progress(
        "[progress.description]{task.description}",
        TaskProgressColumn(show_speed=True),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
        TextColumn("["),
        TimeElapsedColumn(),
        TextColumn("<"),
        TimeRemainingColumn(),
        TextColumn(","),
        RateColumn(),
        TextColumn("]"),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]{description}", total=len(iterable))
        for item in iterable:
            if isinstance(item, str):
                progress.update(task, description=item)
            yield item
            progress.advance(task)


class RichTracker:
    def __init__(
        self,
        description: str = "Processing...",
        use_rate_column_class: bool = True,
        console: Console | None = None,
        unit: str | None = None,
        **kwargs,
    ) -> None:
        self.description = description
        # self.progress = Progress(
        #     "[progress.description]{task.description}",
        #     TaskProgressColumn(show_speed=True),
        #     BarColumn(bar_width=None),
        #     MofNCompleteColumn(),
        #     TextColumn("["),
        #     TimeElapsedColumn(),
        #     TextColumn("<"),
        #     TimeRemainingColumn(),
        #     TextColumn(","),
        #     RateColumn(),
        #     TextColumn("]"),
        #     console=console,
        # )
        # if unit is None:
        # unit = "it"
        self.unit = unit or "it"
        rate_column = (
            RateColumn(unit=self.unit)
            if use_rate_column_class
            else TextColumn(f"[red]{{task.fields[speed]:.0f}} {self.unit}/s[/red]")
        )

        self.progress = Progress(
            # "[progress.description]{task.description}",
            TaskProgressColumn(show_speed=True),
            BarColumn(bar_width=None),
            MofNCompleteColumn(),
            TextColumn("["),
            TimeElapsedColumn(),
            TextColumn("<"),
            TimeRemainingColumn(elapsed_when_finished=True),
            TextColumn(","),
            rate_column,
            TextColumn("]"),
            console=console,
            speed_estimate_period=kwargs.pop("speed_estimate_period", 60),
            # get_time=time.time,
        )

        description = kwargs.pop("description", "Processing...")
        self.task_id = self.progress.add_task(description, **kwargs)
        self.live = Live(
            self.generate_display(), console=console, refresh_per_second=10
        )

    def generate_display(self):
        # 1. Create a grid to hold the spinner and text on one line
        header_grid = Table.grid(padding=(0, 1))
        header_grid.add_column()  # For the Spinner
        header_grid.add_column()  # For the Description text

        # 2. Add the row (this keeps them on the same line)
        header_grid.add_row(
            Spinner("dots", style="bold cyan"), f"[bold white]{self.task.description}"
        )

        # 3. Use Group to stack the horizontal header over the progress bar
        return Group(
            header_grid,
            self.progress,
        )

    def start(self):
        """Starts the progress clock."""
        if not self.task.started:
            self.progress.start_task(self.task_id)
        self.live.update(self.generate_display())

    def update(self, *args, **kwargs):
        """Update the progress and trigger a Live refresh."""
        self.progress.update(self.task_id, **kwargs)
        # Update the Live display with the result of the new generate_display()
        self.live.update(self.generate_display())

    @property
    def task(self):
        return next(task for task in self.progress.tasks if task.id == self.task_id)

    def __enter__(self):
        # self.progress.__enter__()
        self.live.start()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # self.progress.__exit__(exc_type, exc_value, traceback)
        self.live.stop()

    def track(self, iterable: Collection) -> Generator[Any, Any]:
        task = self.progress.add_task(f"[cyan]{self.description}", total=len(iterable))
        for item in iterable:
            yield item
            self.progress.advance(task)
            # self.progress.update(task,)
