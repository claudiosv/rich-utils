from conftest import make_task

from rich_utils.rate_column import RateColumn


def test_render_no_speed_returns_empty_text():
    column = RateColumn()
    task = make_task(finished_speed=None)

    text = column.render(task)

    assert str(text) == ""
    assert text.style == "progress.percentage"


def test_render_fast_speed_uses_units_per_second():
    column = RateColumn()
    task = make_task(finished_speed=5.0)

    text = column.render(task)

    assert str(text) == "5 it/s"
    assert text.style == "red"


def test_render_slow_speed_uses_seconds_per_unit():
    column = RateColumn()
    task = make_task(finished_speed=0.5)

    text = column.render(task)

    assert str(text) == "2 s/it"


def test_render_large_speed_uses_suffix():
    column = RateColumn()
    task = make_task(finished_speed=5_000.0)

    text = column.render(task)

    assert str(text) == "5x10³ it/s"


def test_render_custom_unit():
    column = RateColumn(unit="rows")
    task = make_task(finished_speed=10.0)

    text = column.render(task)

    assert str(text) == "10 rows/s"


def test_render_prefers_finished_speed_over_task_speed():
    column = RateColumn()
    task = make_task(finished_speed=42.0)
    # task.speed would be None here since no progress samples were recorded.

    text = column.render(task)

    assert str(text) == "42 it/s"
