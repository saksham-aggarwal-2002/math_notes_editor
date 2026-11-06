import os
import threading
import time

from mathnotes import render


def wait_until(condition, seconds=3):
    deadline = time.time() + seconds

    while time.time() < deadline:
        if condition():
            return True
        time.sleep(0.01)

    return False


def test_stale_when_html_missing_or_older(tmp_path):
    qmd = tmp_path / "n.qmd"
    qmd.write_text("x")
    assert render.is_stale(qmd)

    html = tmp_path / "n.html"
    html.write_text("x")
    os.utime(qmd, (1, 1))
    assert not render.is_stale(qmd)

    os.utime(qmd, (html.stat().st_mtime + 10,) * 2)
    assert render.is_stale(qmd)


def test_requests_render_once_each_in_order_and_report_busy(tmp_path, monkeypatch):
    first, second = tmp_path / "a.qmd", tmp_path / "b.qmd"
    gate = threading.Event()
    rendered = []

    def fake_run(command, **kwargs):
        rendered.append(command[2])
        gate.wait(3)

    monkeypatch.setattr(render.subprocess, "run", fake_run)

    render.request(first)
    assert wait_until(lambda: rendered == [str(first)])
    assert render.is_busy(first)

    render.request(second)
    render.request(second)  # already waiting: not queued twice
    assert render.is_busy(second)

    gate.set()
    assert wait_until(lambda: not render.is_busy(second))
    assert rendered == [str(first), str(second)]
    assert not render.is_busy(first)


def test_failed_render_does_not_kill_the_worker(tmp_path, monkeypatch):
    import subprocess

    calls = []

    def fake_run(command, **kwargs):
        calls.append(command[2])
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(render.subprocess, "run", fake_run)

    render.request(tmp_path / "bad.qmd")
    assert wait_until(lambda: not render.is_busy(tmp_path / "bad.qmd") and calls)

    render.request(tmp_path / "again.qmd")
    assert wait_until(lambda: len(calls) == 2)
