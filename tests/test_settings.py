from mathnotes import settings


def test_no_folder_chosen_yet(tmp_path, monkeypatch, data_folder):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    assert settings.data_folder() is None
    assert not settings.data_folder_is_usable()


def test_save_keeps_other_settings(data_folder):
    settings.save(subject="alg")
    settings.save(note="a.qmd")
    assert settings.get("subject") == "alg"
    assert settings.get("note") == "a.qmd"
    assert settings.get("missing", "fallback") == "fallback"


def test_folder_comes_from_config(tmp_path, monkeypatch, data_folder):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    settings.save(data_folder=str(tmp_path))
    assert settings.data_folder() == tmp_path
    assert settings.data_folder_is_usable()


def test_missing_folder_is_not_usable(tmp_path, monkeypatch, data_folder):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    settings.save(data_folder=str(tmp_path / "gone"))
    assert not settings.data_folder_is_usable()


def test_env_var_overrides_config(data_folder):
    settings.save(data_folder="/somewhere/else")
    assert settings.data_folder() == data_folder


def test_key_read_from_env_file_each_time(data_folder):
    assert settings.openai_key() is None
    settings.APP_DATA_DIR.mkdir()
    settings.ENV_FILE.write_text("OPENAI_API_KEY=abc\n")
    assert settings.openai_key() == "abc"
    settings.ENV_FILE.write_text("OPENAI_API_KEY=def\n")
    assert settings.openai_key() == "def"
