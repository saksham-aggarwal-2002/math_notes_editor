import pytest
from fastapi.testclient import TestClient

from mathnotes import ai, api, jupyter, render, settings


@pytest.fixture
def client(data_folder, monkeypatch):
    monkeypatch.setattr(render, "request", lambda path: renders.append(path))
    monkeypatch.setattr(render, "is_busy", lambda path: False)
    renders.clear()
    return TestClient(api.app)


renders = []


def test_state_lists_subjects_and_defaults_to_the_first(client):
    state = client.get("/api/state").json()
    assert state["subjects"] == ["alg", "calc"]
    assert state["session"] == {"subject": "alg", "note": None}
    assert state["hasOpenAIKey"] is False
    assert state["dataFolder"]


def test_session_is_remembered(client):
    client.put("/api/session", json={"subject": "calc", "note": "x.qmd"})
    assert client.get("/api/state").json()["session"] == {"subject": "calc", "note": "x.qmd"}


def test_session_pointing_at_a_deleted_subject_falls_back(client):
    client.put("/api/session", json={"subject": "gone", "note": None})
    assert client.get("/api/state").json()["session"]["subject"] == "alg"


def test_subject_info(client):
    assert client.get("/api/subjects/alg").json() == {"notes": ["a.qmd", "b.qmd"]}
    assert client.get("/api/subjects/nope").status_code == 404


def test_read_a_note(client):
    assert client.get("/api/subjects/alg/notes/a.qmd").json() == {"content": "# A\n"}


def test_reading_a_note_renders_it_only_if_stale(client, data_folder):
    client.get("/api/subjects/alg/notes/b.qmd")  # b.html doesn't exist
    assert renders == [data_folder / "alg/notes/b.qmd"]


def test_saving_writes_the_right_note_and_queues_a_render(client, data_folder):
    assert client.put("/api/subjects/alg/notes/b.qmd", json={"content": "new"}).status_code == 200
    assert (data_folder / "alg/notes/b.qmd").read_text() == "new"
    assert (data_folder / "alg/notes/a.qmd").read_text() == "# A\n"
    assert renders == [data_folder / "alg/notes/b.qmd"]


def test_unknown_notes_and_traversal_are_rejected(client, data_folder):
    for note in ["nope.qmd", "a.html", "..%2Fb.qmd"]:
        assert client.get(f"/api/subjects/alg/notes/{note}").status_code == 404
        assert client.put(f"/api/subjects/alg/notes/{note}", json={"content": "x"}).status_code in (404, 405)
    assert client.get("/api/subjects/..%2Fbooks/notes/a.qmd").status_code == 404
    assert (data_folder / "alg/notes/b.qmd").read_text() == ""
    assert not (data_folder / "alg/b.qmd").exists()


def test_preview_status(client):
    assert client.get("/api/subjects/alg/notes/a.qmd/preview").json()["modified"] > 0
    assert client.get("/api/subjects/alg/notes/b.qmd/preview").json() == {"modified": 0, "rendering": False}


def test_images(client):
    assert [image["name"] for image in client.get("/api/subjects/alg/images").json()] == ["p.png"]


def test_files_are_served_from_the_data_folder_only(client):
    assert client.get("/files/alg/styles/quarto.css").status_code == 200
    assert client.get("/files/alg/notes/images/p.png").status_code == 200
    for bad in ["../app_data/config.json", "alg/%2e%2e/%2e%2e/app_data/config.json", "nope.css", "alg"]:
        assert client.get(f"/files/{bad}").status_code == 404


def test_api_needs_a_data_folder(client, monkeypatch):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    assert client.get("/api/subjects/alg").status_code == 409
    assert client.get("/api/state").json()["subjects"] == []


def test_jupyter_start_is_per_subject(client, monkeypatch):
    started = []
    monkeypatch.setattr(jupyter, "ensure", lambda subject: started.append(subject) or {"available": True, "reason": ""})
    assert client.post("/api/subjects/alg/jupyter").json() == {"available": True, "reason": ""}
    assert started == ["alg"]
    assert client.post("/api/subjects/nope/jupyter").status_code == 404


def test_ai_quarto_sends_the_editor_text(client, monkeypatch):
    seen = []
    monkeypatch.setattr(ai, "quarto", lambda text, request: seen.append((text, request)) or "out")
    response = client.post("/api/subjects/alg/ai/quarto", json={"content": "unsaved <!-- AI_GENERATING -->", "request": "hi"})
    assert response.json() == {"content": "out"}
    assert seen == [("unsaved <!-- AI_GENERATING -->", "hi")]
    assert client.post("/api/subjects/nope/ai/quarto", json={"content": "x", "request": "hi"}).status_code == 404


def test_ai_without_a_key_explains_how_to_fix_it(client):
    response = client.post("/api/subjects/alg/ai/quarto", json={"content": "x", "request": "hi"})
    assert response.status_code == 400
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_ai_python_reads_the_open_notebook_only_inside_experiments(client, monkeypatch):
    monkeypatch.setattr(ai, "python", lambda path, request: path.name)
    ok = client.post("/api/subjects/alg/ai/python", json={"notebook": "x.ipynb", "request": "r"})
    assert ok.json() == {"content": "x.ipynb"}
    bad = client.post("/api/subjects/alg/ai/python", json={"notebook": "../notes/a.qmd", "request": "r"})
    assert bad.status_code == 404


def test_open_folder(client, monkeypatch, data_folder):
    opened = []
    monkeypatch.setattr(api.subprocess, "run", lambda command, **kw: opened.append(command))
    assert client.post("/api/open-folder", json={"which": "data"}).status_code == 200
    assert client.post("/api/open-folder", json={"which": "app_data"}).status_code == 200
    assert client.post("/api/open-folder", json={"which": "etc"}).status_code == 400
    assert opened == [["open", str(data_folder)], ["open", str(settings.APP_DATA_DIR)]]


def test_positions_are_remembered(client):
    client.put("/api/positions", json={"key": "alg/notes/a.qmd", "value": 120.5})
    client.put("/api/positions", json={"key": "alg/books/b.pdf", "value": "#page=3"})
    client.put("/api/positions", json={"key": "alg/notes/a.qmd", "value": 7})

    assert client.get("/api/state").json()["positions"] == {"alg/notes/a.qmd": 7, "alg/books/b.pdf": "#page=3"}
