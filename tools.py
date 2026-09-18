import shutil
import subprocess
import re
from datetime import datetime
from pathlib import Path


QMD_FILE = Path("notes/linalg_1.qmd")
HISTORY_DIR = Path(".history")
PLACEHOLDER_IMAGE_PATTERN = re.compile(
    r"!\[([^\]]*)\]\(\s*https?://via\.placeholder\.com/[^)\s]*\s*\)",
    re.IGNORECASE,
)


def normalise_placeholder_images(content):
    """Convert placeholder-image URLs into the notebook's local placeholder box."""

    def replacement(match):
        description = match.group(1).strip() or "Placeholder image"
        return f"::: {{.placeholder-image}}\n\n{description}\n\n:::"

    return PLACEHOLDER_IMAGE_PATTERN.sub(replacement, content)


def backup_notebook():
    """Save the current notebook before it is changed."""

    HISTORY_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    backup_file = HISTORY_DIR / f"notebook-{timestamp}.qmd"
    shutil.copy2(QMD_FILE, backup_file)


def undo_last_change():
    """Restore the notebook state before the most recent edit."""

    backups = sorted(HISTORY_DIR.glob("notebook-*.qmd")) if HISTORY_DIR.exists() else []

    if not backups:
        return "Nothing to undo."

    latest_backup = backups[-1]
    shutil.copy2(latest_backup, QMD_FILE)
    latest_backup.unlink()

    return "Last change undone successfully."


def read_notebook():
    """Read and return the current Quarto notebook."""

    return QMD_FILE.read_text()


def insert_content(content):
    """Append content to the end of the Quarto notebook."""

    content = normalise_placeholder_images(content)
    backup_notebook()

    with QMD_FILE.open("a") as file:
        file.write("\n\n")
        file.write(content)
        file.write("\n")

    return "Content inserted successfully."


def delete_content(content):
    """Delete the first exact occurrence of content from the notebook."""

    notebook = read_notebook()

    if content not in notebook:
        return "The specified content was not found."

    notebook = notebook.replace(content, "", 1)

    backup_notebook()
    QMD_FILE.write_text(notebook)

    return "Content deleted successfully."


def replace_content(old_content, new_content):
    """Replace the first exact occurrence of content in the notebook."""

    notebook = read_notebook()

    if old_content not in notebook:
        return "The specified content was not found."

    notebook = notebook.replace(old_content, new_content, 1)

    backup_notebook()
    QMD_FILE.write_text(notebook)

    return "Content replaced successfully."


def render_quarto():
    """Render the Quarto notebook."""

    subprocess.run(
        ["quarto", "render", QMD_FILE],
        check=True
    )

    return "Quarto rendered successfully."
