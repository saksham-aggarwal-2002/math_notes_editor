"""Reading the data folder. Pure functions of its layout:

    <root>/<subject>/notes/*.qmd          notes (rendered .html beside each)
    <root>/<subject>/notes/images/        pictures the notes use
    <root>/<subject>/styles/quarto.css
    <root>/<subject>/books/               .pdf files
    <root>/<subject>/experiments/         .ipynb files, jupyter_venv/
"""
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


class NotFound(Exception):
    """A subject, note or file that isn't there (or isn't allowed)."""


def list_subjects(root):
    """Names of the folders in `root` that have a notes/ folder."""
    root = Path(root)

    if not root.is_dir():
        return []

    return sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir()
        and not path.name.startswith(".")
        and (path / "notes").is_dir()
    )


def subject_dir(root, subject):
    if subject not in list_subjects(root):
        raise NotFound(f"Unknown subject: {subject}")

    return Path(root) / subject


def list_notes(root, subject):
    """File names of the .qmd notes in a subject, sorted."""
    notes_dir = subject_dir(root, subject) / "notes"

    return sorted(path.name for path in notes_dir.glob("*.qmd"))


def note_path(root, subject, note):
    if note not in list_notes(root, subject):
        raise NotFound(f"Unknown note: {note}")

    return Path(root) / subject / "notes" / note


def list_images(root, subject):
    """Images in the subject's notes/images/, newest first."""
    image_dir = subject_dir(root, subject) / "notes" / "images"

    if not image_dir.is_dir():
        return []

    images = [
        {"name": path.name, "modified": path.stat().st_mtime}
        for path in image_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]

    return sorted(images, key=lambda image: image["modified"], reverse=True)


def list_books(root, subject):
    """File names of the PDFs in the subject's books/ folder, sorted (none if there is no folder)."""
    books_dir = subject_dir(root, subject) / "books"

    if not books_dir.is_dir():
        return []

    return sorted(
        path.name for path in books_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf" and not path.name.startswith(".")
    )


def has_jupyter(root, subject):
    return (subject_dir(root, subject) / "experiments" / "jupyter_venv" / "bin" / "python").exists()


def notebook_path(root, subject, relative_path):
    """An .ipynb inside the subject's experiments/ folder, or the only one there."""
    experiments = (subject_dir(root, subject) / "experiments").resolve()

    if relative_path:
        path = (experiments / relative_path).resolve()

        if experiments not in path.parents or path.suffix != ".ipynb" or not path.is_file():
            raise NotFound(f"Unknown notebook: {relative_path}")

        return path

    notebooks = sorted(experiments.glob("*.ipynb"))

    if len(notebooks) != 1:
        raise NotFound("Open a notebook in Jupyter first.")

    return notebooks[0]


def safe_path(root, relative_path):
    """A file under `root`, refusing anything that escapes it."""
    root = Path(root).resolve()
    path = (root / relative_path).resolve()

    if root not in path.parents or not path.is_file():
        raise NotFound("Not found.")

    return path
