import main
from mathnotes import settings


def test_first_run_asks_for_the_folder_and_remembers_it(data_folder, tmp_path, monkeypatch):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    asked = []
    monkeypatch.setattr(main, "choose_folder", lambda message: asked.append(message) or tmp_path)

    assert main.ensure_data_folder() is True
    assert len(asked) == 1
    assert settings.data_folder() == tmp_path

    assert main.ensure_data_folder() is True   # remembered: no second question
    assert len(asked) == 1


def test_cancelling_the_first_run_box_quits(data_folder, monkeypatch):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    monkeypatch.setattr(main, "choose_folder", lambda message: None)

    assert main.ensure_data_folder() is False
    assert settings.data_folder() is None


def test_a_missing_folder_is_asked_for_again(data_folder, tmp_path, monkeypatch):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    settings.save(data_folder=str(tmp_path / "gone"))
    asked = []
    monkeypatch.setattr(main, "choose_folder", lambda message: asked.append(message) or tmp_path)

    assert main.ensure_data_folder() is True
    assert "gone" in asked[0]
    assert settings.data_folder() == tmp_path


def test_a_usable_folder_is_not_asked_about(data_folder, monkeypatch):
    monkeypatch.setattr(main, "choose_folder", lambda message: 1 / 0)
    assert main.ensure_data_folder() is True
