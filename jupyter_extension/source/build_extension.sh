#!/usr/bin/env bash
set -euo pipefail

EXTENSION_NAME="math_notes_editor-jupyter-bridge"
PACKAGE_LABEXTENSION_DIR="math_notes_editor_jupyter_bridge/labextension"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(cd "$SOURCE_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$EXTENSION_ROOT/.." && pwd)"
BUILD_DIR="$EXTENSION_ROOT/build"
JUPYTER_DATA_DIR="$BUILD_DIR/jupyter_data"
SHARED_LABEXTENSION_DIR="$JUPYTER_DATA_DIR/labextensions/$EXTENSION_NAME"
BUILD_PYTHON="${BUILD_PYTHON:-$PROJECT_ROOT/venv/bin/python}"

if [[ ! -x "$BUILD_PYTHON" ]]; then
    cat >&2 <<EOF
Error: build Python is not executable:
  $BUILD_PYTHON

By default this script uses the app/project venv:
  $PROJECT_ROOT/venv/bin/python

Create the app venv first, or pass a different project build Python:
  BUILD_PYTHON="/path/to/python" ./jupyter_extension/source/build_extension.sh
EOF
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "Error: npm is required but was not found on PATH." >&2
    exit 1
fi

PYTHON_SCRIPTS_DIR="$($BUILD_PYTHON -c 'import sysconfig; print(sysconfig.get_path("scripts"))')"

cd "$SOURCE_DIR"

echo "Using project build Python: $BUILD_PYTHON"
echo "Using Python scripts dir: $PYTHON_SCRIPTS_DIR"
echo "Extension source dir: $SOURCE_DIR"
echo "Shared built extension will be installed to: $SHARED_LABEXTENSION_DIR"

echo "Cleaning generated files..."
rm -rf \
    node_modules \
    lib \
    "$PACKAGE_LABEXTENSION_DIR" \
    tsconfig.tsbuildinfo \
    "$BUILD_DIR"

echo "Installing Python build requirements into the project build environment..."
"$BUILD_PYTHON" -m pip install -r requirements-build.txt

echo "Installing npm dependencies from package-lock.json..."
npm ci

echo "Building JupyterLab extension..."
PATH="$PYTHON_SCRIPTS_DIR:$PATH" npm run build

echo "Copying built extension to shared generated Jupyter data directory..."
mkdir -p "$(dirname "$SHARED_LABEXTENSION_DIR")"
cp -R "$PACKAGE_LABEXTENSION_DIR" "$SHARED_LABEXTENSION_DIR"

if [[ ! -f "$SHARED_LABEXTENSION_DIR/package.json" ]]; then
    echo "Error: built extension package.json was not created at: $SHARED_LABEXTENSION_DIR/package.json" >&2
    exit 1
fi

cat <<EOF

Done.

Shared built extension location:

  $SHARED_LABEXTENSION_DIR

When launching JupyterLab from a notes environment, include this shared data directory in JUPYTER_PATH before the notes data directory:

  export JUPYTER_PATH="$JUPYTER_DATA_DIR:\$SUBJECT_DIR/experiments"

EOF
