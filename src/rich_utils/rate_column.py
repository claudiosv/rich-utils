from rich.progress import Column, ProgressColumn, Task, filesize
from rich.text import Text


class RateColumn(ProgressColumn):
    """Renders human readable processing rate."""

    def __init__(
        self, table_column: Column | None = None, unit: str | None = None
    ) -> None:
        super().__init__(table_column)
        self.unit = unit or "it"

    def render(self, task: Task) -> Text:
        """Render the speed in iterations per second.

        Returns
        -------
        Text
            The formatted rate string, or empty text if no speed is available.
        """
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("", style="progress.percentage")
        unit, suffix = filesize.pick_unit_and_suffix(
            int(speed),
            ["", "x10³", "x10⁶", "x10⁹", "x10¹²"],
            1000,
        )
        data_speed = speed / unit
        if data_speed < 1:
            data_speed = unit / speed
            text = f"{data_speed:,.0f}{suffix} s/{self.unit}"
        else:
            text = f"{data_speed:,.0f}{suffix} {self.unit}/s"

        return Text(text, style="red")  # or progress.percentage
