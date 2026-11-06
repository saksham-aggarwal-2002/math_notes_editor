import json

from mathnotes import jupyter, settings


def test_environment_drops_the_apps_python_settings(monkeypatch):
    for key in ["PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV", "RESOURCEPATH", "__PYVENV_LAUNCHER__"]:
        monkeypatch.setenv(key, "/app/python")
    monkeypatch.setenv("HOME", "/home/me")

    env = jupyter._clean_env()

    for key in ["PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV", "RESOURCEPATH", "__PYVENV_LAUNCHER__"]:
        assert key not in env
    assert env["HOME"] == "/home/me"


def test_environment_adds_only_the_extension_and_quarto():
    env = jupyter._clean_env()

    assert env["JUPYTER_PATH"] == str(settings.PROJECT_DIR / "jupyter_extension" / "build" / "jupyter_data")
    assert "/usr/local/bin" in env["PATH"].split(":")


def test_server_is_local_tokenless_and_embeddable_only_by_the_app(tmp_path):
    options = jupyter._server_options(tmp_path)

    assert f"--port={settings.JUPYTER_PORT}" in options
    assert f"--notebook-dir={tmp_path}" in options
    assert "--ServerApp.token=" in options
    assert f"--ServerApp.allow_origin={settings.APP_ORIGIN}" in options

    tornado = next(o for o in options if o.startswith("--ServerApp.tornado_settings="))
    headers = json.loads(tornado.split("=", 1)[1])["headers"]
    assert settings.APP_ORIGIN in headers["Content-Security-Policy"]


def test_subject_without_a_venv_is_reported_not_crashed(data_folder):
    result = jupyter.ensure("alg")
    assert result["available"] is False
    assert "jupyter_venv" in result["reason"]
