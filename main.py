"""Entry point: `python main.py` opens the Math Notes window."""
import atexit
import signal
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

import uvicorn
import webview

from mathnotes import api, jupyter, settings


def choose_folder(message):
    """Mac's own "choose a folder" box. Returns the folder picked, or None if cancelled."""
    script = ["on run argv", "POSIX path of (choose folder with prompt (item 1 of argv))", "end run"]
    result = subprocess.run(
        ["osascript", *[a for line in script for a in ("-e", line)], message],
        capture_output=True, text=True
    )

    return Path(result.stdout.strip()) if result.returncode == 0 else None


def ensure_data_folder():
    """Ask for the data folder if there isn't a usable one. False if the box is cancelled."""
    if settings.data_folder_is_usable():
        return True

    folder = settings.data_folder()

    picked = choose_folder(
        "Choose your Math Notes data folder (the one containing your subjects)"
        if folder is None else
        f"Your data folder wasn't found at {folder}. Choose it again."
    )

    if picked is None:
        return False

    settings.save(data_folder=str(picked))

    return True


def wait_for_server(seconds=20):
    deadline = time.time() + seconds

    while time.time() < deadline:
        try:
            urllib.request.urlopen(settings.APP_ORIGIN + "/api/state", timeout=1)
            return
        except OSError:
            time.sleep(0.2)

    raise RuntimeError("The server did not start.")


def main():
    if not ensure_data_folder():
        return  # no data folder chosen: nothing to open

    web = uvicorn.Server(
        uvicorn.Config(api.app, host="127.0.0.1", port=settings.APP_PORT, log_level="warning")
    )
    threading.Thread(target=web.run, daemon=True).start()

    try:
        wait_for_server()

        window = webview.create_window(
            "Math Notes", settings.APP_ORIGIN, width=1500, height=950, min_size=(1000, 600)
        )
        # Cmd+Q can end the process without returning from webview.start().
        window.events.closed += jupyter.stop
        atexit.register(jupyter.stop)
        signal.signal(signal.SIGTERM, lambda *_: (jupyter.stop(), sys.exit(0)))
        webview.start()
    finally:
        jupyter.stop()
        web.should_exit = True


if __name__ == "__main__":
    main()
