import io
import time

import pytest
from rich.console import Console
from rich.progress import Task, TaskID


@pytest.fixture
def console() -> Console:
    return Console(file=io.StringIO(), force_terminal=False, width=120)


def make_task(
    total: float | None = 100,
    completed: float = 0,
    description: str = "task",
    finished_speed: float | None = None,
    fields: dict | None = None,
) -> Task:
    return Task(
        id=TaskID(0),
        description=description,
        total=total,
        completed=completed,
        _get_time=time.time,
        finished_speed=finished_speed,
        fields=fields or {},
    )
