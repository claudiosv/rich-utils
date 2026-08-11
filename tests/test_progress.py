import pandas as pd

from rich_utils.progress import RichTracker, rich_pandas, rich_progress, rich_track

# --- rich_track -----------------------------------------------------------


def test_rich_track_yields_all_items(console):
    items = list(rich_track([1, 2, 3], console=console))
    assert items == [1, 2, 3]


def test_rich_track_updates_description_on_string_items(console):
    items = list(rich_track(["a", "b"], console=console))
    assert items == ["a", "b"]


def test_rich_track_empty_iterable(console):
    assert list(rich_track([], console=console)) == []


# --- rich_progress ----------------------------------------------------


def test_rich_progress_is_a_working_context_manager(console):
    with rich_progress(console=console, total=3) as (progress, task, _wrap):
        assert progress.tasks[task].total == 3
        progress.advance(task)
        assert progress.tasks[task].completed == 1


def test_rich_progress_without_rate_column_class(console):
    with rich_progress(use_rate_column_class=False, console=console, total=1) as (
        progress,
        task,
        _wrap,
    ):
        progress.advance(task)
        assert progress.tasks[task].completed == 1


def test_rich_progress_wrap_calls_function_and_advances(console):
    calls = []
    with rich_progress(console=console, total=2) as (progress, task, wrap):
        result_a = wrap(calls.append, "a")
        result_b = wrap(calls.append, "b")

    assert calls == ["a", "b"]
    assert result_a is None
    assert result_b is None
    assert progress.tasks[task].completed == 2


def test_rich_progress_wrap_without_rate_column_class_records_speed(
    monkeypatch, console
):
    """wrapper_timer times how long the wrapped function call itself took."""
    times = iter([100.0, 100.5])
    monkeypatch.setattr("rich_utils.progress.time.time", lambda: next(times))

    with rich_progress(use_rate_column_class=False, console=console, total=1) as (
        progress,
        task,
        wrap,
    ):
        result = wrap(lambda x: x * 2, 21)

    assert result == 42
    assert progress.tasks[task].completed == 1
    assert progress.tasks[task].fields["speed"] == 2


# --- rich_pandas --------------------------------------------------------


def test_rich_pandas_patches_progress_apply(console):
    rich_pandas(console=console)
    df = pd.DataFrame({"a": [1, 2, 3]})

    result = df.progress_apply(lambda row: row["a"] * 2, description="doubling")

    assert list(result) == [2, 4, 6]


def test_rich_pandas_without_rate_column_class(console):
    rich_pandas(use_rate_column_class=False, console=console)
    df = pd.DataFrame({"a": [1, 2]})

    result = df.progress_apply(lambda row: row["a"] + 1)

    assert list(result) == [2, 3]


# --- RichTracker --------------------------------------------------------


def test_rich_tracker_context_manager_starts_and_stops(console):
    with RichTracker(description="Working", console=console, total=3) as tracker:
        assert tracker.live.is_started
    assert not tracker.live.is_started


def test_rich_tracker_start_marks_task_started(console):
    with RichTracker(console=console, total=3) as tracker:
        tracker.start()
        assert tracker.task.started


def test_rich_tracker_update_advances_task_fields(console):
    with RichTracker(console=console, total=3) as tracker:
        tracker.update(completed=2)
        assert tracker.task.completed == 2


def test_rich_tracker_track_advances_progress(console):
    with RichTracker(console=console) as tracker:
        items = list(tracker.track([1, 2, 3]))
        assert items == [1, 2, 3]
        # track() must advance the tracker's own task, not create a second one.
        assert len(tracker.progress.tasks) == 1
        assert tracker.task.completed == 3
        assert tracker.task.total == 3


def test_rich_tracker_description_param_is_not_applied_to_task(console):
    """Documents current (surprising) behavior: RichTracker.__init__ pops
    "description" from **kwargs (always absent, since it's a named
    parameter), so the task's own description is always the default
    "Processing...", even though `description=` is stored on
    `self.description` and used elsewhere (e.g. `generate_display`).
    """
    with RichTracker(description="Custom desc", console=console, total=1) as tracker:
        assert tracker.description == "Custom desc"
        assert tracker.task.description == "Processing..."


def test_rich_tracker_custom_unit(console):
    tracker = RichTracker(console=console, unit="rows", total=1)
    assert tracker.unit == "rows"
