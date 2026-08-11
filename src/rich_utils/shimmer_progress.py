import math
import os
import sys
import time
from dataclasses import dataclass
from types import TracebackType
from typing import Self

from rich.console import Console
from rich.progress import Progress, ProgressColumn, Task, TaskID, TextColumn
from rich.text import Text


@dataclass
class Glyphs:
    """Terminal glyph sets mapped to their respective environments."""

    ok: str
    err: str
    info: str
    warn: str
    spinner: list[str]
    bar_filled: str
    bar_empty: str
    rail: str
    phase_done: str
    dash: str


UNICODE_GLYPHS = Glyphs(
    ok="✓",
    err="✗",
    info="ℹ",
    warn="⚠",
    spinner=["·", "✢", "✳", "✶", "✻", "✽"],
    bar_filled="█",
    bar_empty="░",
    rail="│",
    phase_done="◆",
    dash="—",
)

ASCII_GLYPHS = Glyphs(
    ok="[OK]",
    err="[ERR]",
    info="[i]",
    warn="[!]",
    spinner=[".", "*", "+", "x", "o", "O"],
    bar_filled="#",
    bar_empty="-",
    rail="|",
    phase_done="*",
    dash="-",
)


def supports_unicode() -> bool:
    """
    Determine if the current terminal environment supports unicode rendering.

    Returns
    -------
    bool
        True if the environment supports unicode, False otherwise.
    """
    if os.environ.get("CODEGRAPH_ASCII") == "1":
        return False
    if os.environ.get("CODEGRAPH_UNICODE") == "1":
        return True
    if sys.platform == "win32":
        return False
    return os.environ.get("TERM") != "linux"


def get_glyphs() -> Glyphs:
    """
    Retrieve the optimal glyph set for the terminal.

    Returns
    -------
    Glyphs
        The dataclass containing appropriate string glyphs.
    """
    return UNICODE_GLYPHS if supports_unicode() else ASCII_GLYPHS


def lerp(a: float, b: float, t: float) -> int:
    """Linear interpolation helper.

    Returns
    -------
    int
        The value at `t` between `a` and `b`, rounded to the nearest int.
    """
    return round(a + (b - a) * t)


class ShimmerSpinnerColumn(ProgressColumn):
    """A progress column that cycles spinner glyphs.

    Applies the sine-wave shimmer color effect over time.
    """

    def __init__(self, start_time: float, glyphs: Glyphs) -> None:
        self.start_time = start_time
        self.glyphs = glyphs
        super().__init__()

    def render(self, task: Task) -> Text:
        frame = int((time.time() - self.start_time) / 0.150)
        t = (math.sin(frame * 2 * math.pi / 13) + 1) / 2

        r = lerp(160, 251, t)
        g = lerp(100, 191, t)
        b = lerp(9, 36, t)

        frames_per_glyph = 3
        glyph_idx = (frame // frames_per_glyph) % len(self.glyphs.spinner)
        glyph = self.glyphs.spinner[glyph_idx]

        return Text(glyph, style=f"bold rgb({r},{g},{b})")


class ShimmerBarColumn(ProgressColumn):
    """A progress column that draws a bar with a sweeping shimmer light effect."""

    def __init__(self, start_time: float, glyphs: Glyphs) -> None:
        self.start_time = start_time
        self.glyphs = glyphs
        super().__init__()

    def render(self, task: Task) -> Text:
        if task.total is None:
            return Text("")

        frame = int((time.time() - self.start_time) / 0.150)
        percent = (
            min(1.0, max(0.0, task.percentage / 100.0)) if task.percentage else 0.0
        )

        bar_width = 25
        filled = round(bar_width * percent)
        empty = bar_width - filled

        if filled == 0:
            return Text(self.glyphs.bar_empty * empty, style="dim")

        cycle_frames = 24
        shimmer_pos = ((frame % cycle_frames) / cycle_frames) * (filled + 6) - 3
        shimmer_width = 3

        text = Text()
        for i in range(filled):
            dist = abs(i - shimmer_pos)
            t = max(0.0, 1.0 - dist / shimmer_width)
            r = lerp(160, 251, t)
            g = lerp(100, 191, t)
            b = lerp(9, 36, t)
            text.append(self.glyphs.bar_filled, style=f"bold rgb({r},{g},{b})")

        if empty > 0:
            text.append(self.glyphs.bar_empty * empty, style="dim")

        return text


class ShimmerStatsColumn(ProgressColumn):
    """A progress column handling percentage rendering or indeterminate counts."""

    def __init__(self, glyphs: Glyphs) -> None:
        self.glyphs = glyphs
        super().__init__()

    def render(self, task: Task) -> Text:
        if task.total is not None:
            percentage = int(task.percentage) if task.percentage else 0
            return Text(f" {percentage}%")

        count = task.fields.get("current_count", 0)
        if count > 0:
            return Text(f" {count:,} found")

        return Text("")


class ShimmerProgress:
    """Main orchestration class that matches your TypeScript worker API.

    Handles phase transitions and logs them dynamically above the active
    progress bar.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()
        self.glyphs = get_glyphs()
        self.start_time = time.time()

        self._progress = Progress(
            TextColumn(f"[dim]{self.glyphs.rail}[/dim] "),
            ShimmerSpinnerColumn(self.start_time, self.glyphs),
            TextColumn(" {task.description}"),
            ShimmerBarColumn(self.start_time, self.glyphs),
            ShimmerStatsColumn(self.glyphs),
            console=self.console,
            transient=True,  # Removes the task bar on finish naturally
            refresh_per_second=20,  # Equivalent to 50ms interval loop
        )
        self._current_task_id: TaskID | None = None
        self._last_phase: str = ""
        self._last_count: int = 0
        self._last_total: int = 0
        self._running: bool = False

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.stop()

    def start(self) -> None:
        """Start the rich Progress live context."""
        self._progress.start()
        self._running = True

    def _finish_phase(self, phase: str, count: int, total: int) -> None:
        if not phase:
            return

        detail = ""
        if total > 0:
            detail = f" {self.glyphs.dash} done"
        elif count > 0:
            detail = f" {self.glyphs.dash} {count:,} found"

        # Prints directly above the live progressing task
        self._progress.console.print(
            f"[dim]{self.glyphs.rail}[/dim]  "
            f"[green]{self.glyphs.phase_done}[/green] "
            f"{phase}{detail}"
        )

    def on_progress(self, phase: str, current: int = 0, total: int = 0) -> None:
        """
        Updates the progress bar and transitions to a new phase if the phase changes.

        Parameters
        ----------
        phase : str
            The name of the current execution phase.
        current : int
            The current progress or count.
        total : int
            The total items (if 0, treats the progress as indeterminate).
        """
        if not self._running:
            self.start()

        # Handle Phase changes
        if phase != self._last_phase and self._last_phase:
            self._finish_phase(self._last_phase, self._last_count, self._last_total)
            if self._current_task_id is not None:
                self._progress.remove_task(self._current_task_id)
            self._current_task_id = None

        self._last_phase = phase
        self._last_count = current
        self._last_total = total

        target_total = total if total > 0 else None
        target_completed = current if total > 0 else 0

        if self._current_task_id is None:
            self._current_task_id = self._progress.add_task(
                f"{phase}...",
                total=target_total,
                completed=target_completed,
                current_count=current,
            )
        else:
            self._progress.update(
                self._current_task_id,
                description=f"{phase}...",
                completed=target_completed,
                total=target_total,
                current_count=current,
            )

    def stop(self) -> None:
        """Stops the live display and finalizes the last phase."""
        if self._running:
            if self._last_phase:
                self._finish_phase(self._last_phase, self._last_count, self._last_total)
            self._progress.stop()
            self._running = False


def main() -> None:
    mode = "release"
    with ShimmerProgress() as progress:
        match mode:
            case "debug":
                phases = [
                    ("Scanning AST", 0, 45, 0.04),  # Indeterminate
                    ("Linking", 100, 100, 0.02),  # Determinate
                ]
            case "release":
                phases = [
                    ("Scanning AST", 0, 30, 0.03),  # Indeterminate
                    ("Transpiling", 200, 200, 0.01),  # Determinate
                    ("Minifying", 50, 50, 0.02),  # Determinate
                ]
            case _:
                phases = [("Generic processing", 10, 10, 0.1)]

        for phase_name, total, iterations, delay in phases:
            for i in range(1, iterations + 1):
                # Using total=0 renders the indeterminate counter instead of a percentage bar
                progress.on_progress(phase_name, current=i, total=max(0, total))
                time.sleep(delay)


if __name__ == "__main__":
    main()
