# math_notes_editor

Personal Quarto-based AI notebook environment.

## Structure

### Application

```text
~/Local_storage/math_notes_editor/
├── venv/
├── main.py
├── ...
└── README.md
```

### Subjects

Subjects are stored separately:

```text
~/Local_storage/subjects/<subject>/
```

Current example:

```text
~/Local_storage/subjects/linalg/
└── experiments/
    ├── *.ipynb
    ├── jupyter_venv/
    │   └── bin/python
    └── kernels/
        └── linalg/
            └── kernel.json
```

## Python Environments

The application and each subject have separate Python environments.

**math_notes_editor:**

```text
math_notes_editor/venv/
```

Used for FastAPI and application dependencies.

**Subject:**

```text
<subject>/experiments/jupyter_venv/
```

Used for JupyterLab, `ipykernel`, and subject-specific notebook dependencies.

Environments are invoked directly rather than activated.

## Jupyter

Jupyter is launched using the subject environment:

```bash
"$SUBJECT_DIR/experiments/jupyter_venv/bin/python" -m jupyterlab
```

`math_notes_editor` sets:

```bash
export JUPYTER_PATH="$MATH_NOTES_EDITOR_DIR/jupyter_extension/build/jupyter_data:$SUBJECT_DIR/experiments"
```

This makes both the shared app JupyterLab extension and the subject kernelspec discoverable.

The shared extension is generated at:

```text
math_notes_editor/jupyter_extension/build/jupyter_data/labextensions/math_notes_editor-jupyter-bridge/
```

The subject kernelspec is discovered from:

```text
<subject>/experiments/kernels/<subject>/kernel.json
```

The kernelspec points to:

```text
<subject>/experiments/jupyter_venv/bin/python
```

Subject kernels should **not** be installed globally with:

```bash
ipykernel install --user
```

## FastAPI

FastAPI is launched using the application environment:

```bash
"$MATH_NOTES_EDITOR_DIR/venv/bin/python" -m uvicorn main:app --reload
```

## Current Example

```text
math_notes_editor/
└── venv/

subjects/
└── linalg/
    └── experiments/
        ├── linalg.ipynb
        ├── jupyter_venv/
        └── kernels/
            └── linalg/
                └── kernel.json
```


# Building Jupyter Extension

The extension source and rebuild instructions live in:

```text
jupyter_extension/source/
```

The built shared extension is generated into:

```text
jupyter_extension/build/jupyter_data/
```

Generated extension artifacts are not committed. To rebuild the shared extension using the app/project venv, run from the repo root:

```bash
./jupyter_extension/source/build_extension.sh
```

See `jupyter_extension/source/BUILD.md` for details.

# Requirements

Python requirements in venv
Quarto requirement?
npm requirement


# Executable
~/Local_storage/math_notes_editor/
└── bin/
    └── mathNotes          # source of truth, tracked by Git
            ↑
            │ symlink
            │
~/personal_binaries/
└── mathNotes              # PATH entry


# Building Jupyter Extension
From the repository root:

```bash
./jupyter_extension/source/build_extension.sh
```
