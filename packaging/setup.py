"""Builds MathNotes.app. Run packaging/build_app.sh rather than calling this directly."""
from setuptools import setup

setup(
    name="MathNotes",
    app=["main.py"],
    options={
        "py2app": {
            "iconfile": "packaging/MathNotes.icns",
            "plist": {
                "CFBundleName": "MathNotes",
                "CFBundleDisplayName": "Math Notes",
                "CFBundleIdentifier": "com.saksham.mathnotes",
                "CFBundleShortVersionString": "0.1.0",
                "NSHighResolutionCapable": True,
            },
        }
    },
)
