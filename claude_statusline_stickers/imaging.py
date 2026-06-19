"""Image → glyph helpers: outline tracing, tile colour, PNG encoding.

Pure PIL / fontTools-pen utilities with no knowledge of the build, the cell
layout or codepoints. trace_outline is the heart of the renderer-independent
path; the sbix colour bitmap is layered on top of it in fontcanvas.py.
"""
import io

from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image


def png_bytes(img):
    """Encode a PIL image as PNG bytes."""
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def trace_outline(img, w_units, h_units, y0, x0=0, alpha_threshold=128):
    """Trace an RGBA image into a TrueType outline of pixel-run rectangles.

    Opaque pixels become rectangles (horizontal runs merged per row), scaled
    to a w_units x h_units box whose bottom-left corner sits at (x0, y0).
    Renders in any font engine — no color-bitmap table support required.
    """
    pen = TTGlyphPen(None)
    w_px, h_px = img.size
    alpha = img.getchannel("A").load()

    def x(col):
        return x0 + round(col * w_units / w_px)

    def y(row_from_bottom):
        return y0 + round(row_from_bottom * h_units / h_px)

    for py in range(h_px):
        px = 0
        while px < w_px:
            if alpha[px, py] < alpha_threshold:
                px += 1
                continue
            run = px
            while px < w_px and alpha[px, py] >= alpha_threshold:
                px += 1
            xa, xb = x(run), x(px)
            yb, yt = y(h_px - 1 - py), y(h_px - py)
            pen.moveTo((xa, yb))
            pen.lineTo((xa, yt))
            pen.lineTo((xb, yt))
            pen.lineTo((xb, yb))
            pen.closePath()

    return pen.glyph()


def normalize(img, size):
    """Contain-fit an image onto a transparent size×size RGBA canvas.

    Keeps aspect ratio (no distortion), centring the art and padding with
    transparency, so every fetched sprite is a uniform size×size input.
    """
    img = img.convert("RGBA")
    if img.size == (size, size):
        return img

    fit = min(size / img.width, size / img.height)
    scaled = img.resize(
        (max(1, round(img.width * fit)), max(1, round(img.height * fit))),
        Image.LANCZOS,
    )
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(scaled, ((size - scaled.width) // 2, (size - scaled.height) // 2))
    return canvas
