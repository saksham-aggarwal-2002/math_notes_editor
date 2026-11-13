import main
from mathnotes import settings


def test_picker_saves_the_chosen_folder_and_opens_the_app(data_folder, tmp_path, monkeypatch):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    calls = []

    class Events:
        closed = []

    class Window:
        events = Events()
        set_title = lambda self, t: calls.append(("title", t))
        resize = lambda self, w, h: calls.append(("resize", w, h))
        move = lambda self, x, y: calls.append(("move", x, y))
        load_url = lambda self, url: calls.append(("load", url))

    Events.closed = type("E", (), {"__iadd__": lambda self, f: self})()
    picker = main.Picker.__new__(main.Picker)
    picker.window = Window()

    assert picker.open(str(tmp_path)) is None
    assert settings.data_folder() == tmp_path
    assert ("load", settings.APP_ORIGIN) in calls


def test_picker_refuses_a_missing_folder(data_folder, tmp_path, monkeypatch):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    picker = main.Picker.__new__(main.Picker)

    assert picker.open(str(tmp_path / "gone")) is not None
    assert settings.data_folder() is None
