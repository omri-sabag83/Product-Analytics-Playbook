"""Shared chart style: a thin black frame around every chart image.

Import once in a notebook (`import chart_style`). Every PNG that matplotlib produces (what
the notebook displays, and any chart saved to a .png file) gets a white margin and a thin
black frame around the whole image, including legends placed outside the axes. This makes
charts stand out on a white page (e.g. GitHub).

The frame should *look* the same thickness everywhere, so it is drawn thicker when the
image will be shown smaller than its pixel size:
- images wider than a notebook column (DISPLAY_MAX_PX) are shrunk by the viewer;
- seaborn.objects charts render at double resolution and are displayed at
  Plot.config.display["scaling"] / 2 of their size.
"""
import io
import os

import matplotlib.backend_bases as _bb
from PIL import Image, ImageOps

WHITE_MARGIN_PX = 8
FRAME_PX = 2
DISPLAY_MAX_PX = 800   # chosen: about the width of a notebook output column

_print_figure = _bb.FigureCanvasBase.print_figure


def _display_scale(width_px: int, dpi) -> float:
    """How much the image will be shrunk on screen (1 = shown at its own size)."""
    scale = 1.0
    try:
        from seaborn._core.plot import Plot
        cfg = Plot.config.display
        if cfg.get("hidpi") and dpi == 96 * 2:
            scale = cfg["scaling"] / 2
    except Exception:
        pass
    shown = width_px * scale
    if shown > DISPLAY_MAX_PX:
        scale *= DISPLAY_MAX_PX / shown
    return scale


def _add_frame(img: Image.Image, scale: float) -> Image.Image:
    grow = 1 / scale
    img = ImageOps.expand(img, border=max(WHITE_MARGIN_PX, round(WHITE_MARGIN_PX * grow)), fill="white")
    return ImageOps.expand(img, border=max(FRAME_PX, round(FRAME_PX * grow)), fill="black")


def _framed_print_figure(self, filename, *args, **kwargs):
    fmt = kwargs.get("format")
    if fmt is None and isinstance(filename, (str, os.PathLike)):
        fmt = os.path.splitext(str(filename))[1].lstrip(".")
    if (fmt or "").lower() != "png":
        return _print_figure(self, filename, *args, **kwargs)
    buf = io.BytesIO()
    result = _print_figure(self, buf, *args, **{**kwargs, "format": "png"})
    img = Image.open(io.BytesIO(buf.getvalue()))
    img = _add_frame(img, _display_scale(img.size[0], kwargs.get("dpi")))
    img.save(filename, format="PNG")
    return result


_bb.FigureCanvasBase.print_figure = _framed_print_figure
