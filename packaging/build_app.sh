#!/bin/sh
# Builds MathNotes.app (an alias build: it runs the code in this folder) and installs it
# in /Applications. Rerun only after changing the icon or packaging/setup.py, or after moving this folder.
set -e
cd "$(dirname "$0")/.."

[ -f packaging/MathNotes.icns ] || venv/bin/python packaging/make_icon.py

rm -rf build dist
venv/bin/python packaging/setup.py py2app -A > build.log 2>&1 || { tail -20 build.log; exit 1; }
rm -f build.log

rm -rf /Applications/MathNotes.app
cp -R dist/MathNotes.app /Applications/
echo "Installed /Applications/MathNotes.app"
