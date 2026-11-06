import pytest

from mathnotes import library


def test_subjects_are_folders_with_notes(data_folder):
    assert library.list_subjects(data_folder) == ["alg", "calc"]


def test_missing_root_has_no_subjects(tmp_path):
    assert library.list_subjects(tmp_path / "nope") == []


def test_notes_are_sorted_qmd_files(data_folder):
    assert library.list_notes(data_folder, "alg") == ["a.qmd", "b.qmd"]
    assert library.list_notes(data_folder, "calc") == []


def test_unknown_subject_or_note(data_folder):
    with pytest.raises(library.NotFound):
        library.list_notes(data_folder, "nope")
    with pytest.raises(library.NotFound):
        library.note_path(data_folder, "alg", "zzz.qmd")
    with pytest.raises(library.NotFound):
        library.subject_dir(data_folder, "../alg")


def test_note_path(data_folder):
    assert library.note_path(data_folder, "alg", "a.qmd") == data_folder / "alg/notes/a.qmd"


def test_images_only_pictures(data_folder):
    assert [image["name"] for image in library.list_images(data_folder, "alg")] == ["p.png"]
    assert library.list_images(data_folder, "calc") == []


def test_has_jupyter(data_folder):
    assert not library.has_jupyter(data_folder, "alg")
    python = data_folder / "alg/experiments/jupyter_venv/bin/python"
    python.parent.mkdir(parents=True)
    python.touch()
    assert library.has_jupyter(data_folder, "alg")


def test_notebook_path(data_folder):
    assert library.notebook_path(data_folder, "alg", "x.ipynb").name == "x.ipynb"
    assert library.notebook_path(data_folder, "alg", None).name == "x.ipynb"  # the only one


def test_notebook_path_must_stay_inside_experiments(data_folder):
    for bad in ["../notes/a.qmd", "../../books/only.pdf", "/etc/passwd", "missing.ipynb"]:
        with pytest.raises(library.NotFound):
            library.notebook_path(data_folder, "alg", bad)


def test_safe_path(data_folder):
    assert library.safe_path(data_folder, "alg/styles/quarto.css").name == "quarto.css"


def test_safe_path_refuses_escapes_and_missing(data_folder):
    for bad in ["../data_secret", "alg/../../app_data/.env", "alg", "alg/notes/none.html", "/etc/passwd"]:
        with pytest.raises(library.NotFound):
            library.safe_path(data_folder, bad)


def test_list_books_returns_only_pdfs(tmp_path):
    (tmp_path / "alg" / "notes").mkdir(parents=True)
    (tmp_path / "alg" / "books").mkdir()
    (tmp_path / "alg" / "books" / "b.pdf").write_text("")
    (tmp_path / "alg" / "books" / "A.PDF").write_text("")
    (tmp_path / "alg" / "books" / "x.txt").write_text("")

    assert library.list_books(tmp_path, "alg") == ["A.PDF", "b.pdf"]
