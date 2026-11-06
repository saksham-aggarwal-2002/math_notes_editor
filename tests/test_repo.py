"""Guards against machine-specific things creeping back into the committed code."""
from pathlib import Path

from mathnotes import settings

SKIP_DIRS = {"venv", "node_modules", "build", "dist", "app_data", "__pycache__", ".git", "lib", "vendor", ".pytest_cache", "labextension"}
SOURCE_SUFFIXES = {".py", ".js", ".html", ".css", ".sh", ".md", ".ts", ".json", ".txt"}


def source_files():
    for path in settings.PROJECT_DIR.rglob("*"):
        parts = set(path.relative_to(settings.PROJECT_DIR).parts)
        if path.is_file() and not parts & SKIP_DIRS and path.suffix in SOURCE_SUFFIXES and path.name != "package-lock.json":
            yield path


def test_no_personal_paths_in_the_code():
    offenders = [
        str(path.relative_to(settings.PROJECT_DIR))
        for path in source_files()
        if "/Users/" in path.read_text(errors="ignore") and path.name != "test_repo.py"
    ]
    assert offenders == []


def test_ui_has_no_external_dependencies():
    for path in (settings.PROJECT_DIR / "ui").rglob("*"):
        if path.suffix in {".html", ".js", ".css"} and "vendor" not in path.parts:
            assert "https://" not in path.read_text(), f"{path} loads something from the internet"


def test_every_page_script_exists():
    index = (settings.PROJECT_DIR / "ui" / "index.html").read_text()
    import re

    for reference in re.findall(r'(?:src|href)="(/[^"]+)"', index):
        assert (settings.PROJECT_DIR / "ui" / reference.lstrip("/")).is_file(), reference
