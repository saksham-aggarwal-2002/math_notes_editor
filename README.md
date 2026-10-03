# mathAI

Personal Quarto-based AI notebook environment.

## Structure

### Application

```text
~/Local_storage/mathAI/
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

**mathAI:**

```text
mathAI/venv/
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

`mathAI` sets:

```bash
export JUPYTER_PATH="$SUBJECT_DIR/experiments"
```

This makes the subject kernelspec discoverable:

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
"$MATHAI_DIR/venv/bin/python" -m uvicorn main:app --reload
```

## Current Example

```text
mathAI/
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
cd /Users/sakshamaggarwal/Local_storage/mathAI/jupyter_extension
npm install
npm run build

pip install -e .
jupyter labextension list (to see if mathai-jupyter-bridge appears)

# Requirements

Python requirements in venv
Quarto requirement?

# Executable
~/Local_storage/mathAI/
└── bin/
    └── mathNotes          # source of truth, tracked by Git
            ↑
            │ symlink
            │
~/personal_binaries/
└── mathNotes              # PATH entry