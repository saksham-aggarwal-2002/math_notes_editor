from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

import os
import time
import subprocess
import threading


load_dotenv()

client = OpenAI()
app = FastAPI()


app.mount(
    "/notes",
    StaticFiles(directory="notes"),
    name="notes"
)

app.mount(
    "/styles",
    StaticFiles(directory="styles"),
    name="styles"
)


IMAGE_DIR = Path("notes/images")
QMD_FILE = "notes/linalg_1.qmd"
HTML_FILE = "notes/linalg_1.html"


def load_instructions(files):

    return "\n\n".join(
        open(file, "r").read()
        for file in files
    )


def render_quarto():

    print("Rendering Quarto...")

    try:

        subprocess.run(
            ["quarto", "render", QMD_FILE],
            check=True
        )

        print("Quarto rendering complete.")

    except subprocess.CalledProcessError:

        print("Quarto rendering failed.")


def watch_quarto():

    last_modified = os.path.getmtime(QMD_FILE)

    while True:

        time.sleep(1)

        current_modified = os.path.getmtime(QMD_FILE)

        if current_modified != last_modified:

            last_modified = current_modified

            render_quarto()


render_quarto()


watcher_thread = threading.Thread(
    target=watch_quarto,
    daemon=True
)

watcher_thread.start()


class Message(BaseModel):

    message: str


class NotebookUpdate(BaseModel):

    content: str


@app.get("/")
def home():

    return FileResponse("index.html")


@app.get("/notebook")
def notebook():

    with open(QMD_FILE, "r") as file:

        content = file.read()

    return {
        "content": content
    }


@app.post("/notebook")
def save_notebook(data: NotebookUpdate):

    with open(QMD_FILE, "w") as file:

        file.write(data.content)

    return {
        "success": True
    }


@app.get("/images")
def get_images():

    IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    images = []

    for path in IMAGE_DIR.iterdir():

        if (
            path.is_file()
            and path.suffix.lower()
            in {
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".svg",
                ".webp"
            }
        ):

            images.append({

                "name":
                    path.name,

                "modified":
                    path.stat().st_mtime,

            })


    images.sort(
        key=lambda x: x["modified"],
        reverse=True
    )


    return images


@app.get("/quarto-version")
def quarto_version():

    return {

        "modified":
            os.path.getmtime(HTML_FILE)

    }


# --------------------------------------------------
# Quarto / Markdown AI generation
# --------------------------------------------------

@app.post("/ai/generate")
def generate(data: Message):

    instructions = load_instructions([
        "instructions/quarto_editing.md"
    ])


    with open(QMD_FILE, "r") as file:

        notebook = file.read()


    prompt = f"""
{instructions}

Here is the current Quarto notebook:

--- BEGIN NOTEBOOK ---

{notebook}

--- END NOTEBOOK ---

The user wants to insert something at the current cursor position.

Generate the Quarto/Markdown content requested by the user.

The user's request is:

{data.message}

Return ONLY the content that should be inserted.
Do not use a Markdown code fence.
Do not explain your answer.
"""


    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )


    return {

        "content":
            response.output_text.strip()

    }


# --------------------------------------------------
# Python AI generation
# --------------------------------------------------

@app.post("/ai/generate-python")
def generate_python(data: Message):

    instructions = load_instructions([
        "instructions/python_editing.md"
    ])

    with open("experiments/linalg.ipynb", "r") as file:
        notebook = file.read()

    prompt = f"""
{instructions}

Here is the current Jupyter notebook:

--- BEGIN NOTEBOOK ---

{notebook}

--- END NOTEBOOK ---

The user's request is:

{data.message}

Return ONLY the Python code that should be inserted.
Do not use a Markdown code fence.
Do not explain your answer.
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return {
        "content": response.output_text.strip()
    }