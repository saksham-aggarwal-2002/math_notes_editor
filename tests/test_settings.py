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


def test_parallel_saves_never_lose_the_folder(tmp_path, monkeypatch, data_folder):
    import threading

    monkeypatch.delenv("MATH_EDITOR_DATA")
    settings.save(data_folder=str(tmp_path))

    def save_many(n):
        for i in range(100):
            settings.save(**{f"key{n}": i})

    threads = [threading.Thread(target=save_many, args=(n,)) for n in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]

    assert settings.data_folder() == tmp_path


def test_session_and_folder_live_in_separate_files(tmp_path, monkeypatch, data_folder):
    monkeypatch.delenv("MATH_EDITOR_DATA")
    settings.save(data_folder=str(tmp_path), subject="alg")

    assert settings.CONFIG_FILE.read_text().count("alg") == 0
    assert settings.STATE_FILE.read_text().count(str(tmp_path)) == 0

    settings.STATE_FILE.write_text("garbage")   # a broken state file loses the place, not the folder
    assert settings.get("subject") is None
    assert settings.data_folder() == tmp_path

