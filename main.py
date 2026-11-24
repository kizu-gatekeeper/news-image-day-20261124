"""Entry point for the news-image-20261124 bounty.

Draws the 24 November 2026 world-news front page (see draw_poster.py)
and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Standard library only, no network, deterministic: the same bytes are
written on every run.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from draw_poster import draw_poster, write_png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    poster = draw_poster()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(poster, path)
    print("wrote %s (%dx%d, %d bytes)" % (path, poster.width, poster.height, size))


if __name__ == "__main__":
    main()
