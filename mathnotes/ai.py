"""The two AI features: write Quarto text or Python code to insert at the cursor."""
import json

from openai import OpenAI

from mathnotes import settings

MODEL = "gpt-5-mini"
PROMPTS_DIR = settings.PROJECT_DIR / "prompts"


class NoKey(Exception):
    pass


def _complete(prompt_name, what, document, request):
    key = settings.openai_key()

    if not key:
        raise NoKey(f"No OpenAI key: add OPENAI_API_KEY to {settings.ENV_FILE}")

    instructions = (PROMPTS_DIR / f"{prompt_name}.md").read_text()

    prompt = f"""
{instructions}

Here is {what}:

--- BEGIN NOTEBOOK ---

{document}

--- END NOTEBOOK ---

The user's request is:

{request}

Return ONLY the content that should be inserted.
Do not use a Markdown code fence.
Do not explain your answer.
"""

    response = OpenAI(api_key=key).responses.create(model=MODEL, input=prompt)

    return response.output_text.strip()


def quarto(note_text, request):
    return _complete(
        "quarto", "the current Quarto notebook (the user wants to insert something at the cursor)",
        note_text, request
    )


def python(notebook_path, request):
    """Only the notebook's code cells are sent, not its markdown, outputs or metadata."""
    notebook = json.loads(notebook_path.read_text())

    code = "\n\n".join(
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    )

    return _complete("python", "the Python code currently in the Jupyter notebook", code, request)
