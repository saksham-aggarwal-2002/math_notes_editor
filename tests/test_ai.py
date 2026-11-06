import pytest

from mathnotes import ai, settings


class FakeClient:
    prompts = []

    def __init__(self, api_key):
        self.responses = self
        FakeClient.api_key = api_key

    def create(self, model, input):
        FakeClient.prompts.append(input)

        class Response:
            output_text = "  generated  "

        return Response()


@pytest.fixture
def fake_openai(data_folder, monkeypatch):
    FakeClient.prompts = []
    monkeypatch.setattr(ai, "OpenAI", FakeClient)
    settings.APP_DATA_DIR.mkdir()
    settings.ENV_FILE.write_text("OPENAI_API_KEY=secret\n")


def test_no_key_is_a_clear_error(data_folder):
    with pytest.raises(ai.NoKey, match="OPENAI_API_KEY"):
        ai.quarto("text", "do it")


def test_quarto_prompt_has_instructions_note_and_request(fake_openai):
    assert ai.quarto("MY NOTE", "add a theorem") == "generated"
    prompt = FakeClient.prompts[0]
    assert "MY NOTE" in prompt and "add a theorem" in prompt
    assert (ai.PROMPTS_DIR / "quarto.md").read_text().strip() in prompt
    assert FakeClient.api_key == "secret"


def test_python_prompt_sends_only_code_cells(fake_openai, data_folder):
    ai.python(data_folder / "alg/experiments/x.ipynb", "plot it")
    prompt = FakeClient.prompts[0]
    assert "x = 1\ny = 2" in prompt
    assert "words" not in prompt
    assert (ai.PROMPTS_DIR / "python.md").read_text().strip() in prompt
