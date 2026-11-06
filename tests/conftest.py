import pytest

from mathnotes import settings


@pytest.fixture
def data_folder(tmp_path, monkeypatch):
    """A data folder with subjects `alg` (two notes, an image, a notebook) and `calc` (no notes),
    and an empty app_data/, both outside the real ones."""
    root = tmp_path / "data"

    for path in [
        "alg/notes/a.qmd", "alg/notes/b.qmd", "alg/notes/a.html", "alg/notes/images/p.png",
        "alg/notes/images/readme.txt", "alg/styles/quarto.css", "alg/experiments/x.ipynb",
        "calc/notes/.keep", "books/only.pdf", ".hidden/notes/z.qmd",
    ]:
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("")

    (root / "alg/notes/a.qmd").write_text("# A\n")
    (root / "alg/experiments/x.ipynb").write_text(
        '{"cells": [{"cell_type": "code", "source": ["x = 1\\n", "y = 2"]},'
        ' {"cell_type": "markdown", "source": ["words"]}]}'
    )

    app_data = tmp_path / "app_data"
    monkeypatch.setattr(settings, "APP_DATA_DIR", app_data)
    monkeypatch.setattr(settings, "CONFIG_FILE", app_data / "config.json")
    monkeypatch.setattr(settings, "ENV_FILE", app_data / ".env")
    monkeypatch.setattr(settings, "JUPYTER_LOG", app_data / "jupyter.log")
    monkeypatch.setenv("MATH_EDITOR_DATA", str(root))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    return root
