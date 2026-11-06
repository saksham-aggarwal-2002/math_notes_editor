"""Draws the MathNotes icon (purple rounded square, white sigma) and saves MathNotes.icns.

Run: venv/bin/python packaging/make_icon.py
"""
import subprocess
import tempfile
from pathlib import Path

from AppKit import (
    NSBezierPath, NSBitmapImageRep, NSCalibratedRGBColorSpace, NSColor,
    NSGraphicsContext, NSPNGFileType, NSLineCapStyleRound, NSLineJoinStyleRound,
)

HERE = Path(__file__).parent
SIZE = 1024


def draw_png(path):
    rep = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
        None, SIZE, SIZE, 8, 4, True, False, NSCalibratedRGBColorSpace, 0, 0)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.setCurrentContext_(NSGraphicsContext.graphicsContextWithBitmapImageRep_(rep))

    # Apple's icon grid: the shape sits inside the canvas with a margin.
    margin, radius = 100, 185
    NSColor.colorWithCalibratedRed_green_blue_alpha_(0x6B / 255, 0x3F / 255, 0xD9 / 255, 1).setFill()
    NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
        ((margin, margin), (SIZE - 2 * margin, SIZE - 2 * margin)), radius, radius).fill()

    # The sigma (y goes up in AppKit).
    sigma = NSBezierPath.bezierPath()
    sigma.moveToPoint_((700, 730))
    sigma.lineToPoint_((340, 730))
    sigma.lineToPoint_((560, 512))
    sigma.lineToPoint_((340, 294))
    sigma.lineToPoint_((700, 294))
    sigma.setLineWidth_(80)
    sigma.setLineCapStyle_(NSLineCapStyleRound)
    sigma.setLineJoinStyle_(NSLineJoinStyleRound)
    NSColor.whiteColor().setStroke()
    sigma.stroke()

    NSGraphicsContext.restoreGraphicsState()
    rep.representationUsingType_properties_(NSPNGFileType, {}).writeToFile_atomically_(str(path), True)


def main():
    png = HERE / "MathNotes.png"
    draw_png(png)
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "MathNotes.iconset"
        iconset.mkdir()
        for size in (16, 32, 128, 256, 512):
            for scale in (1, 2):
                name = f"icon_{size}x{size}{'@2x' if scale == 2 else ''}.png"
                px = size * scale
                subprocess.run(["sips", "-z", str(px), str(px), str(png), "--out", str(iconset / name)],
                               check=True, capture_output=True)
        subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(HERE / "MathNotes.icns")], check=True)
    print("wrote", HERE / "MathNotes.icns")


if __name__ == "__main__":
    main()
