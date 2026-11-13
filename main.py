"""Entry point: `python main.py` opens the Math Notes window."""
import atexit
import signal
import sys
import threading
import time
import urllib.request
from pathlib import Path

import uvicorn
import webview

from mathnotes import api, jupyter, settings


APP_SIZE = (1500, 950)
APP_MIN_SIZE = (1000, 600)


def open_main():
    window = webview.create_window(
        "Math Notes", settings.APP_ORIGIN, width=APP_SIZE[0], height=APP_SIZE[1], min_size=APP_MIN_SIZE
    )
    # Cmd+Q can end the process without returning from webview.start().
    window.events.closed += jupyter.stop

    return window


class Picker:
    """The "Select data folder" window (ui/choose_folder.html): a search-bar style
    button that opens Finder's folder box, then Open turns this same window into the app.
    (Swapping in a second window leaves the app unable to quit.)"""

    def __init__(self):
        self.window = webview.create_window(
            "Select data folder", settings.APP_ORIGIN + "/choose_folder.html", js_api=self,
            width=520, height=330
        )

    def pick(self):
        """Finder's folder box; the folder chosen, or None if cancelled."""
        chosen = self.window.create_file_dialog(webview.FileDialog.FOLDER, directory=str(Path.home()))
        return chosen[0] if chosen else None

    def open(self, folder):
        """Save the chosen folder and turn this window into the app. Returns an error message or None."""
        if not folder or not Path(folder).is_dir():
            return "That folder doesn't exist."

        settings.save(data_folder=str(folder))
        self.window.events.closed += jupyter.stop
        self.window.set_title("Math Notes")
        self.window.resize(*APP_SIZE)
        self.window.move(60, 40)
        self.window.load_url(settings.APP_ORIGIN)


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
    web = uvicorn.Server(
        uvicorn.Config(api.app, host="127.0.0.1", port=settings.APP_PORT, log_level="warning")
    )
    threading.Thread(target=web.run, daemon=True).start()

    try:
        wait_for_server()

        if settings.data_folder_is_usable():
            open_main()
        else:
            Picker()
        atexit.register(jupyter.stop)
        signal.signal(signal.SIGTERM, lambda *_: (jupyter.stop(), sys.exit(0)))
        webview.start()
    finally:
        jupyter.stop()
        web.should_exit = True


if __name__ == "__main__":
    main()
