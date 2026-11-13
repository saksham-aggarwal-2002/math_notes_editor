"""Per-machine settings, kept in app_data/ (gitignored, so a fresh clone has none):

    config.json   {"data_folder": "/path/to/subjects"}, set once from the folder picker
    state.json    {"subject": ..., "note": ..., "positions": {...}}, rewritten as you work
                  (separate, so a bad write there can never lose the data folder)
    .env          OPENAI_API_KEY=...
    jupyter.log   output of the running JupyterLab

The notes themselves are never in here: they're in the data folder.
MATH_EDITOR_DATA, if set (tests), is used instead of config.json's data_folder.
"""
import json
import os
import threading
from pathlib import Path

from dotenv import dotenv_values

# resolve(): inside the .app this file is reached through a symlink.
PROJECT_DIR = Path(__file__).resolve().parent.parent

APP_DATA_DIR = PROJECT_DIR / "app_data"
CONFIG_FILE = APP_DATA_DIR / "config.json"
STATE_FILE = APP_DATA_DIR / "state.json"
CONFIG_KEYS = {"data_folder"}
ENV_FILE = APP_DATA_DIR / ".env"
JUPYTER_LOG = APP_DATA_DIR / "jupyter.log"

APP_PORT = 8000
JUPYTER_PORT = 8890
APP_ORIGIN = f"http://127.0.0.1:{APP_PORT}"
JUPYTER_ORIGIN = f"http://127.0.0.1:{JUPYTER_PORT}"


_write_lock = threading.Lock()


def _load(file):
    try:
        return json.loads(file.read_text())
    except (FileNotFoundError, ValueError):
        return {}


def _read(key):
    """The settings in the file that holds `key`."""
    return _load(CONFIG_FILE if key in CONFIG_KEYS else STATE_FILE)


def _write(file, settings):
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = file.with_suffix(".tmp")
    temporary.write_text(json.dumps(settings, indent=2) + "\n")
    os.replace(temporary, file)   # all at once, so a reader never sees half a file


def get(key, default=None):
    return _read(key).get(key, default)


def save(**values):
    """Change these settings, keeping the others. Values go to config.json or state.json by key.

    Saves arrive from parallel requests, hence the lock."""
    with _write_lock:
        for file, keys in [(CONFIG_FILE, CONFIG_KEYS), (STATE_FILE, None)]:
            mine = {k: v for k, v in values.items() if (k in CONFIG_KEYS) == (keys is not None)}

            if mine:
                first = next(iter(mine))
                _write(file, {**_read(first), **mine})


def data_folder():
    """The folder holding the subjects, or None if none has been chosen yet."""
    folder = os.environ.get("MATH_EDITOR_DATA") or get("data_folder")
    return Path(folder) if folder else None


def data_folder_is_usable():
    folder = data_folder()
    return folder is not None and folder.is_dir()


def openai_key():
    """The key from app_data/.env (read each time, so editing it needs no restart)."""
    return dotenv_values(ENV_FILE).get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")


def positions():
    """Where you were in each note and book: {"<subject>/notes/<file>": scroll, ...}."""
    return get("positions", {})


def save_position(key, value):
    save(positions={**positions(), key: value})
