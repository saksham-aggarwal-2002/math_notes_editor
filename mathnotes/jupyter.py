"""Runs one JupyterLab at a time, from the subject's own experiments/jupyter_venv, with that
venv's default kernel (ipykernel's "python3"), so the notebooks also open without this app.

The port is fixed, so switching subject stops the old server before starting the new one.
"""
import json
import os
import signal
import socket
import subprocess
import threading
import time

from mathnotes import library, settings

_lock = threading.Lock()
_process = None
_subject = None


def _port_open():
    with socket.socket() as sock:
        sock.settimeout(0.3)
        return sock.connect_ex(("127.0.0.1", settings.JUPYTER_PORT)) == 0


def _clean_env():
    """The environment for Jupyter and its kernels.

    The app's own Python settings (set by py2app and by the app's venv) must not leak
    in, or the subject's kernel looks for its packages in the wrong place.
    """
    env = {
        key: value for key, value in os.environ.items()
        if not key.startswith("PYTHON")
        and key not in {"VIRTUAL_ENV", "__PYVENV_LAUNCHER__", "RESOURCEPATH", "EXECUTABLEPATH", "ARGVZERO"}
    }
    env["PATH"] = ":".join(["/usr/local/bin", "/opt/homebrew/bin", env.get("PATH", "")])
    env["JUPYTER_PATH"] = str(settings.PROJECT_DIR / "jupyter_extension" / "build" / "jupyter_data")

    return env


def _server_options(experiments):
    """JupyterLab's command line. It is local-only and tokenless, and may be shown in
    the app's window (an iframe on the app's origin) and nowhere else."""
    headers = {"Content-Security-Policy": f"frame-ancestors 'self' {settings.APP_ORIGIN}"}

    return [
        "--no-browser",
        f"--port={settings.JUPYTER_PORT}",
        "--ServerApp.port_retries=0",
        f"--notebook-dir={experiments}",
        "--ServerApp.token=",
        "--ServerApp.password=",
        f"--ServerApp.allow_origin={settings.APP_ORIGIN}",
        f"--ServerApp.tornado_settings={json.dumps({'headers': headers})}",
    ]


def _wait_for_port(process, seconds=30):
    deadline = time.time() + seconds

    while time.time() < deadline:
        if process.poll() is not None:
            return False

        if _port_open():
            return True

        time.sleep(0.3)

    return False


def stop():
    with _lock:
        _stop_locked()


def _stop_locked():
    global _process, _subject

    if _process is not None and _process.poll() is None:
        try:
            os.killpg(_process.pid, signal.SIGTERM)
            _process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            os.killpg(_process.pid, signal.SIGKILL)
            _process.wait()
        except ProcessLookupError:
            pass

    _process = None
    _subject = None


def ensure(subject):
    """Make JupyterLab run for `subject`. Returns {"available": bool, "reason": str}."""
    global _process, _subject

    root = settings.data_folder()

    with _lock:
        if _subject == subject and _process is not None and _process.poll() is None:
            return {"available": True, "reason": ""}

        _stop_locked()

        if not library.has_jupyter(root, subject):
            return {"available": False, "reason": f"No experiments/jupyter_venv found in {subject}. See the README, section Data folder."}

        if _port_open():
            return {"available": False, "reason": f"Port {settings.JUPYTER_PORT} is already in use by another program."}

        experiments = root / subject / "experiments"
        settings.APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

        with open(settings.JUPYTER_LOG, "w") as log:
            _process = subprocess.Popen(
                [str(experiments / "jupyter_venv" / "bin" / "python"), "-m", "jupyterlab", *_server_options(experiments)],
                env=_clean_env(),
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,  # own process group, so stop() reaches its kernels too
            )

        if not _wait_for_port(_process):
            _stop_locked()
            return {"available": False, "reason": f"JupyterLab did not start. See {settings.JUPYTER_LOG}."}

        _subject = subject

        return {"available": True, "reason": ""}
