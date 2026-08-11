import sys
from typing import TYPE_CHECKING

from conftest import make_task

from rich_utils.shimmer_progress import (
    ASCII_GLYPHS,
    UNICODE_GLYPHS,
    ShimmerBarColumn,
    ShimmerProgress,
    ShimmerSpinnerColumn,
    ShimmerStatsColumn,
    get_glyphs,
    lerp,
    supports_unicode,
)

if TYPE_CHECKING:
    import pytest

# --- supports_unicode / get_glyphs -----------------------------------------


def test_supports_unicode_ascii_env_override(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CODEGRAPH_ASCII", "1")
    assert supports_unicode() is False


def test_supports_unicode_unicode_env_override(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CODEGRAPH_ASCII", raising=False)
    monkeypatch.setenv("CODEGRAPH_UNICODE", "1")
    assert supports_unicode() is True


def test_supports_unicode_win32_is_false(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CODEGRAPH_ASCII", raising=False)
    monkeypatch.delenv("CODEGRAPH_UNICODE", raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    assert supports_unicode() is False


def test_supports_unicode_term_linux_is_false(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CODEGRAPH_ASCII", raising=False)
    monkeypatch.delenv("CODEGRAPH_UNICODE", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setenv("TERM", "linux")
    assert supports_unicode() is False


def test_supports_unicode_default_true(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CODEGRAPH_ASCII", raising=False)
    monkeypatch.delenv("CODEGRAPH_UNICODE", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setenv("TERM", "xterm-256color")
    assert supports_unicode() is True


def test_get_glyphs_returns_unicode_or_ascii(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CODEGRAPH_UNICODE", "1")
    monkeypatch.delenv("CODEGRAPH_ASCII", raising=False)
    assert get_glyphs() is UNICODE_GLYPHS

    monkeypatch.setenv("CODEGRAPH_ASCII", "1")
    assert get_glyphs() is ASCII_GLYPHS


# --- lerp --------------------------------------------------------------


def test_lerp_midpoint():
    assert lerp(0, 10, 0.5) == 5


def test_lerp_endpoints():
    assert lerp(10, 20, 0.0) == 10
    assert lerp(10, 20, 1.0) == 20


# --- ShimmerSpinnerColumn / ShimmerBarColumn / ShimmerStatsColumn -----------


def test_spinner_column_renders_a_single_glyph():
    column = ShimmerSpinnerColumn(start_time=0.0, glyphs=UNICODE_GLYPHS)
    task = make_task()

    text = column.render(task)

    assert str(text) in UNICODE_GLYPHS.spinner
    assert isinstance(text.style, str)
    assert text.style.startswith("bold rgb(")


def test_bar_column_no_total_returns_empty():
    column = ShimmerBarColumn(start_time=0.0, glyphs=UNICODE_GLYPHS)
    task = make_task(total=None)

    text = column.render(task)

    assert str(text) == ""


def test_bar_column_zero_percent_is_all_empty_glyphs():
    column = ShimmerBarColumn(start_time=0.0, glyphs=ASCII_GLYPHS)
    task = make_task(total=100, completed=0)

    text = column.render(task)

    assert str(text) == ASCII_GLYPHS.bar_empty * 25


def test_bar_column_full_percent_is_all_filled_glyphs():
    column = ShimmerBarColumn(start_time=0.0, glyphs=ASCII_GLYPHS)
    task = make_task(total=100, completed=100)

    text = column.render(task)

    assert str(text) == ASCII_GLYPHS.bar_filled * 25


def test_bar_column_partial_mixes_filled_and_empty():
    column = ShimmerBarColumn(start_time=0.0, glyphs=ASCII_GLYPHS)
    task = make_task(total=100, completed=40)

    text = column.render(task)
    rendered = str(text)

    assert len(rendered) == 25
    assert rendered.count(ASCII_GLYPHS.bar_filled) == 10
    assert rendered.count(ASCII_GLYPHS.bar_empty) == 15


def test_stats_column_with_total_shows_percentage():
    column = ShimmerStatsColumn(glyphs=UNICODE_GLYPHS)
    task = make_task(total=100, completed=50)

    assert str(column.render(task)) == " 50%"


def test_stats_column_without_total_shows_count():
    column = ShimmerStatsColumn(glyphs=UNICODE_GLYPHS)
    task = make_task(total=None, fields={"current_count": 7})

    assert str(column.render(task)) == " 7 found"


def test_stats_column_without_total_or_count_is_empty():
    column = ShimmerStatsColumn(glyphs=UNICODE_GLYPHS)
    task = make_task(total=None, fields={})

    assert str(column.render(task)) == ""


# --- ShimmerProgress ----------------------------------------------------


def test_shimmer_progress_can_be_constructed(console):
    progress = ShimmerProgress(console=console)
    assert progress.glyphs in (UNICODE_GLYPHS, ASCII_GLYPHS)


def test_shimmer_progress_start_stop(console):
    progress = ShimmerProgress(console=console)
    progress.start()
    assert progress._running is True
    progress.stop()
    assert progress._running is False


def test_shimmer_progress_context_manager(console):
    with ShimmerProgress(console=console) as progress:
        assert progress._running is True
    assert progress._running is False


def test_shimmer_progress_on_progress_creates_and_updates_task(console):
    with ShimmerProgress(console=console) as progress:
        progress.on_progress("Scanning", current=1, total=10)
        assert progress._current_task_id is not None
        assert progress._last_phase == "Scanning"

        progress.on_progress("Scanning", current=5, total=10)
        assert progress._last_count == 5


def test_shimmer_progress_phase_transition_finishes_previous_phase(console):
    with ShimmerProgress(console=console) as progress:
        progress.on_progress("Scanning", current=10, total=10)
        first_task_id = progress._current_task_id

        progress.on_progress("Linking", current=1, total=5)

        assert progress._last_phase == "Linking"
        assert progress._current_task_id != first_task_id


def test_shimmer_progress_starts_automatically_if_not_running(console):
    progress = ShimmerProgress(console=console)
    assert progress._running is False

    progress.on_progress("Scanning", current=1, total=10)

    assert progress._running is True
    progress.stop()
