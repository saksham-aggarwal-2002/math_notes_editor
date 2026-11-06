"""Quarto rendering: one background worker, and a note queued while it's busy is
rendered once more afterwards, so the latest save always wins."""
import os
import subprocess
import threading

_condition = threading.Condition()
_pending = []        # notes waiting to be rendered, oldest first
_rendering = None    # the note being rendered now
_worker = None

# A Finder-launched app gets a minimal PATH, and quarto lives in /usr/local/bin.
_ENV = {**os.environ, "PATH": ":".join(["/usr/local/bin", "/opt/homebrew/bin", os.environ.get("PATH", "")])}


def html_path(qmd_path):
    return qmd_path.with_suffix(".html")


def is_stale(qmd_path):
    html = html_path(qmd_path)

    return not html.exists() or html.stat().st_mtime < qmd_path.stat().st_mtime


def request(qmd_path):
    """Queue a render of this note."""
    global _worker

    with _condition:
        if qmd_path not in _pending:
            _pending.append(qmd_path)

        if _worker is None:
            _worker = threading.Thread(target=_run, daemon=True)
            _worker.start()

        _condition.notify()


def is_busy(qmd_path):
    with _condition:
        return qmd_path in _pending or qmd_path == _rendering


def _run():
    global _rendering

    while True:
        with _condition:
            while not _pending:
                _condition.wait()

            qmd_path = _pending.pop(0)
            _rendering = qmd_path

        try:
            subprocess.run(
                ["quarto", "render", str(qmd_path)],
                cwd=qmd_path.parent, env=_ENV, check=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Quarto render failed: {qmd_path}")

        with _condition:
            _rendering = None
