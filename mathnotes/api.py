"""The web API. Stateless: every request names its subject and note.

The only thing the server remembers is the running JupyterLab (mathnotes/jupyter.py).
"""
import subprocess

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from mathnotes import ai, jupyter, library, render, settings

UI_DIR = settings.PROJECT_DIR / "ui"

app = FastAPI()


@app.exception_handler(library.NotFound)
def not_found(request, error):
    return JSONResponse({"detail": str(error)}, status_code=404)


def root():
    folder = settings.data_folder()

    if folder is None:
        raise HTTPException(status_code=409, detail="No data folder is set.")

    return folder


# --------------------------------------------------
# App state and settings
# --------------------------------------------------

@app.get("/api/state")
def get_state():
    folder = settings.data_folder()
    subjects = library.list_subjects(folder) if folder else []
    subject = settings.get("subject") if settings.get("subject") in subjects else (subjects[0] if subjects else None)

    return {
        "subjects": subjects,
        "session": {"subject": subject, "note": settings.get("note")},
        "positions": settings.positions(),
        "dataFolder": str(folder) if folder else None,
        "appDataDir": str(settings.APP_DATA_DIR),
        "hasOpenAIKey": bool(settings.openai_key()),
        "jupyterOrigin": settings.JUPYTER_ORIGIN,
    }


class Session(BaseModel):

    subject: str | None
    note: str | None


@app.put("/api/session")
def put_session(session: Session):
    settings.save(subject=session.subject, note=session.note)

    return {"success": True}


class Position(BaseModel):

    key: str
    value: float | str


@app.put("/api/positions")
def put_position(position: Position):
    settings.save_position(position.key, position.value)

    return {"success": True}


class FolderChoice(BaseModel):

    which: str


@app.post("/api/open-folder")
def open_folder(choice: FolderChoice):
    """Show the data folder or app_data/ in Finder."""
    folders = {"data": settings.data_folder(), "app_data": settings.APP_DATA_DIR}
    folder = folders.get(choice.which)

    if folder is None:
        raise HTTPException(status_code=400, detail="Unknown folder.")

    folder.mkdir(parents=True, exist_ok=True)
    subprocess.run(["open", str(folder)], check=False)

    return {"success": True}


# --------------------------------------------------
# Subjects and notes
# --------------------------------------------------

@app.get("/api/subjects/{subject}")
def get_subject(subject: str):
    return {"notes": library.list_notes(root(), subject)}


@app.get("/api/subjects/{subject}/notes/{note}")
def get_note(subject: str, note: str):
    path = library.note_path(root(), subject, note)

    if render.is_stale(path):
        render.request(path)

    return {"content": path.read_text()}


class NoteContent(BaseModel):

    content: str


@app.put("/api/subjects/{subject}/notes/{note}")
def put_note(subject: str, note: str, body: NoteContent):
    path = library.note_path(root(), subject, note)

    path.write_text(body.content)
    render.request(path)

    return {"success": True}


@app.get("/api/subjects/{subject}/notes/{note}/preview")
def get_preview(subject: str, note: str):
    path = library.note_path(root(), subject, note)
    html = render.html_path(path)

    return {
        "modified": html.stat().st_mtime if html.exists() else 0,
        "rendering": render.is_busy(path),
    }


@app.get("/api/subjects/{subject}/images")
def get_images(subject: str):
    return library.list_images(root(), subject)


@app.get("/api/subjects/{subject}/books")
def get_books(subject: str):
    return {"books": library.list_books(root(), subject)}


@app.get("/files/{path:path}")
def get_file(path: str):
    """Files of the data folder: rendered notes, styles, images."""
    return FileResponse(library.safe_path(root(), path))


# --------------------------------------------------
# Jupyter and AI
# --------------------------------------------------

@app.post("/api/subjects/{subject}/jupyter")
def start_jupyter(subject: str):
    library.subject_dir(root(), subject)

    return jupyter.ensure(subject)


class QuartoRequest(BaseModel):

    content: str   # the note as it is in the editor, including unsaved edits
    request: str


class PythonRequest(BaseModel):

    notebook: str | None = None
    request: str


def run_ai(function, *args):
    try:
        return {"content": function(*args)}
    except ai.NoKey as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/api/subjects/{subject}/ai/quarto")
def ai_quarto(subject: str, body: QuartoRequest):
    library.subject_dir(root(), subject)

    return run_ai(ai.quarto, body.content, body.request)


@app.post("/api/subjects/{subject}/ai/python")
def ai_python(subject: str, body: PythonRequest):
    path = library.notebook_path(root(), subject, body.notebook)

    return run_ai(ai.python, path, body.request)


# The page itself, last so it doesn't shadow the routes above.
app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")
