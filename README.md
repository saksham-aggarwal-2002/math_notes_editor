# Math Notes

A personal Mac app for studying maths: a Quarto note editor with live preview, an embedded JupyterLab for each subject, and AI help (`Cmd+Shift+L`) that writes text or code at your cursor.

## The three places

| | What | In git? |
|---|---|---|
| **This repo** | the app's code | yes |
| **`app_data/`** (inside the repo folder) | what the app needs on this computer: `config.json` (where your data folder is, the subject and note you were last on), `.env` (`OPENAI_API_KEY=...`), `jupyter.log` | no |
| **The data folder** (anywhere else) | your content | no |

The app is a wrapper over the data folder, like Obsidian over a folder of text files. It never needs anything from the data folder beyond the layout below, and everything in it opens without the app.

## Data folder requirements

```text
<data folder>/
└── <subject>/                 any folder with a notes/ folder is a subject
    ├── notes/                 *.qmd notes; Quarto writes the .html beside each
    │   └── images/            pictures for the image picker (Cmd+Shift+I)
    ├── books/                 *.pdf files for the Books tab
    ├── styles/                whatever your notes link, e.g. css: ../styles/quarto.css
    └── experiments/           .ipynb notebooks
        └── jupyter_venv/      this subject's Python environment (for the Experiments tab); the name is fixed
```

- **Notes:** plain Quarto Markdown. Add a note by adding a `.qmd` file to `notes/`.
- **Experiments tab:** needs a venv at exactly `experiments/jupyter_venv/` (the app looks for `experiments/jupyter_venv/bin/python`; any other name isn't found) with JupyterLab 4 and ipykernel. The app runs that venv's JupyterLab in `experiments/` and uses its default `python3` kernel, so notebooks should use "Python 3 (ipykernel)". Create it with:

  ```bash
  python3 -m venv <subject>/experiments/jupyter_venv
  <subject>/experiments/jupyter_venv/bin/pip install "jupyterlab>=4,<5" ipykernel   # plus the packages you use
  ```

  (JupyterLab 4 because the app's extension is built for it.) A virtualenv has absolute paths inside it, so recreate it rather than copying it to another computer. Without it, only the Python tab is unavailable.
- To open the notebooks without the app: run `experiments/jupyter_venv/bin/jupyter lab` in `experiments/`.

## Setting up on a new Mac

Needs Python 3.11+, Node/npm and [Quarto](https://quarto.org) (in `/usr/local/bin` or `/opt/homebrew/bin`).

```bash
git clone <this repo> && cd math_notes_editor
./install.sh      # venv, JupyterLab extension, /Applications/MathNotes.app
```

Then put `OPENAI_API_KEY=...` in `app_data/.env` and open Math Notes. It asks for your data folder the first time (and again if the folder has gone missing).

The app is an alias build, so code changes need no rebuild; rerun `packaging/build_app.sh` only after changing the icon, `packaging/setup.py`, or moving this folder. To change the data folder later, edit `data_folder` in `app_data/config.json` (or delete that file to be asked again). Settings has "Open in Finder" buttons for the data folder and `app_data/`.

## Using it

- **Notes** tab: pick the subject (top bar) and the note (bar above the editor). Saves automatically; Quarto re-renders after each save.
- `Cmd+Shift+L` AI text · `Cmd+Shift+P` placeholder box · `Cmd+Shift+O` reference · `Cmd+Shift+I` image.
- **Books** tab: the PDFs in the subject's `books/` folder; switch between them with the dropdown.
- **Experiments** tab (JupyterLab): JupyterLab for the subject, started the first time you open it for that subject. `Cmd+Shift+L` there inserts generated code in a new cell below the active one.

## How it fits together

```text
main.py                 asks for the data folder if needed, starts the server (port 8000) in a thread,
                        opens the window, stops Jupyter on exit
mathnotes/
  api.py                the web API (stateless: every request names its subject and note) + serves ui/
  library.py            reads the data folder: subjects, notes, images, safe paths
  settings.py           app_data/: config.json, .env, ports
  render.py             Quarto, one background worker, latest save wins
  jupyter.py            one JupyterLab (port 8890) from the subject's own jupyter_venv, default kernel
  ai.py                 the OpenAI calls; prompts are in prompts/
ui/                     index.html, app.css, js/ (one module per feature), vendor/codemirror (works offline)
jupyter_extension/      TypeScript bridge so Cmd+Shift+L works inside JupyterLab (source/ -> build/)
packaging/              py2app setup, icon, build_app.sh
tests/
```

The app and each subject have separate Python environments, invoked directly rather than activated: `venv/` (FastAPI, pywebview, ...) and `<subject>/experiments/jupyter_venv/` (JupyterLab, ipykernel, the subject's own packages).

Tests: `venv/bin/python -m pytest`. They use temporary data and `app_data/` folders and never touch yours.
