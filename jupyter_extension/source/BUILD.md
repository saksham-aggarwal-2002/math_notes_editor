# Building the math_notes_editor JupyterLab extension

This folder contains the source files required to rebuild the JupyterLab extension.

The built extension is generated into a separate folder:

```text
jupyter_extension/build/
```

That generated folder is not committed to Git.

## Directory layout

```text
jupyter_extension/
├── source/                         # committed source/build definition
│   ├── BUILD.md
│   ├── build_extension.sh
│   ├── requirements-build.txt
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   └── src/
│       └── index.ts
└── build/                          # generated, not committed
    └── jupyter_data/
        └── labextensions/
            └── math_notes_editor-jupyter-bridge/
```

## Generated files

These files/directories are generated and should not be committed:

```text
jupyter_extension/source/node_modules/
jupyter_extension/source/lib/
jupyter_extension/source/labextension/
jupyter_extension/source/tsconfig.tsbuildinfo
jupyter_extension/build/
```

## Shared extension architecture

The extension source lives in this repo. The built extension is generated once into:

```text
jupyter_extension/build/jupyter_data/labextensions/math_notes_editor-jupyter-bridge/
```

Any notes/Jupyter environment can use that single built copy as long as JupyterLab is launched with this shared Jupyter data directory in `JUPYTER_PATH`.

The app sets this when it starts a subject's JupyterLab (`mathnotes/jupyter.py`):

```bash
export JUPYTER_PATH="<repo>/jupyter_extension/build/jupyter_data"
```

This directory provides the shared app extension. Kernels are not registered by the app: each subject uses its own venv's default `python3` kernel.

This means extension updates require only one rebuild in the app repo.

## Build the shared extension

From the repository root:

```bash
./jupyter_extension/source/build_extension.sh
```

By default, the script uses the app/project Python environment:

```text
./venv/bin/python
```

That environment is used only to install the Python build tool `jupyter-builder`. It is not the user's notes/Jupyter runtime environment.

If you want to use a different build Python, pass `BUILD_PYTHON`:

```bash
BUILD_PYTHON="/path/to/build/python" \
  ./jupyter_extension/source/build_extension.sh
```

You also need `npm` available on your shell `PATH`.

## What the build script does

The script will:

1. remove generated source/build files,
2. install Python build requirements into the project build environment,
3. install npm dependencies using `npm ci`,
4. build the extension,
5. copy the built extension to:

   ```text
   jupyter_extension/build/jupyter_data/labextensions/math_notes_editor-jupyter-bridge/
   ```

## Runtime requirement for notes environments

The user's notes/Jupyter environment does not need to build the extension.

The app launches JupyterLab with this shared generated Jupyter data directory in `JUPYTER_PATH` (see above).

## Important compatibility note

Because all notes environments share one built extension, they should use a compatible JupyterLab major version. The recommended policy for notes environments is:

```bash
python -m pip install 'jupyterlab>=4,<5'
```
