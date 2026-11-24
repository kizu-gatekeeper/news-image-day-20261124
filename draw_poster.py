"""Draw the 24 November 2026 world-news front page as a 1024x1024 PNG.

Pure Python standard library only: the image is rendered into an RGB
bytearray with a hand-written 5x7 bitmap font and encoded as PNG with
zlib/struct. No network, no randomness, no timestamps: repeated runs
produce byte-identical output.
"""

import struct
import zlib

W = 1024
H = 1024

PAPER = (248, 244, 232)
INK = (26, 26, 26)
RED = (176, 42, 30)
BLUE = (31, 78, 121)
GOLD = (176, 132, 32)
GREY = (112, 106, 94)
RULE = (196, 188, 170)
CARD_BG = (255, 253, 246)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, '#' = ink pixel. Uppercase letters, digits and the
# punctuation the poster copy needs. draw_text() upper-cases its input.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
}

CHAR_W = 5
CHAR_H = 7


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width=W, height=H, bg=PAPER):
        self.width = width
        self.height = height
        self.px = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, bg)

    def set(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, bg):
        self.fill_circle(cx, cy, r, color)
        self.fill_circle(cx, cy, max(0, r - 3), bg)

    def fill_poly(self, points, color):
        # Scanline fill of a simple polygon.
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, color)


# ---------------------------------------------------------------- text
def text_width(text, scale):
    return len(text) * (CHAR_W + 1) * scale - scale


def draw_text(cv, x, y, text, scale, color, align="left"):
    text = text.upper()
    for ch in text:
        if ch not in FONT:
            raise ValueError("unsupported character in poster copy: %r" % ch)
    if align == "center":
        x -= text_width(text, scale) // 2
    elif align == "right":
        x -= text_width(text, scale)
    cx = x
    for ch in text:
        glyph = FONT[ch]
        for row in range(CHAR_H):
            bits = glyph[row]
            for col in range(CHAR_W):
                if bits[col] == "#":
                    cv.fill_rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += (CHAR_W + 1) * scale
    return cx


def wrap(text, scale, max_width):
    words = text.upper().split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, lines, scale, color, leading=None):
    if leading is None:
        leading = CHAR_H * scale + 4
    for line in lines:
        draw_text(cv, x, y, line, scale, color)
        y += leading
    return y


# ---------------------------------------------------------------- icons
def icon_ship(cv, x, y, color):
    # Hull, mast, sail, waves.
    cv.fill_poly([(x, y + 34), (x + 64, y + 34), (x + 56, y + 50), (x + 8, y + 50)], color)
    cv.vline(x + 30, y + 6, 28, color)
    cv.fill_poly([(x + 33, y + 8), (x + 33, y + 30), (x + 56, y + 30)], color)
    cv.hline(x + 2, y + 56, 60, color)
    cv.hline(x + 10, y + 62, 44, color)


def icon_globe(cv, x, y, color, bg):
    cv.ring(x + 32, y + 32, 30, color, bg)
    cv.hline(x + 4, y + 32, 56, color)
    cv.hline(x + 12, y + 14, 40, color)
    cv.hline(x + 12, y + 50, 40, color)
    cv.vline(x + 32, y + 2, 60, color)


def icon_rocket(cv, x, y, color):
    cv.fill_poly([(x + 32, y + 2), (x + 44, y + 24), (x + 20, y + 24)], color)
    cv.fill_rect(x + 20, y + 24, 24, 26, color)
    cv.fill_poly([(x + 20, y + 34), (x + 8, y + 52), (x + 20, y + 50)], color)
    cv.fill_poly([(x + 44, y + 34), (x + 56, y + 52), (x + 44, y + 50)], color)
    cv.fill_circle(x + 32, y + 34, 5, PAPER)
    cv.fill_poly([(x + 26, y + 50), (x + 38, y + 50), (x + 32, y + 62)], RED)


def icon_fire(cv, x, y, color):
    cv.fill_poly(
        [(x + 32, y + 2), (x + 44, y + 22), (x + 52, y + 16), (x + 56, y + 36),
         (x + 48, y + 56), (x + 16, y + 56), (x + 8, y + 36), (x + 20, y + 22)],
        color,
    )
    cv.fill_poly(
        [(x + 32, y + 30), (x + 40, y + 42), (x + 38, y + 52), (x + 26, y + 52), (x + 24, y + 42)],
        PAPER,
    )


def icon_phone(cv, x, y, color):
    cv.fill_rect(x + 14, y + 2, 36, 60, color)
    cv.fill_rect(x + 18, y + 8, 28, 40, PAPER)
    cv.hline(x + 22, y + 14, 20, RED)
    cv.hline(x + 22, y + 22, 20, GREY)
    cv.hline(x + 22, y + 30, 12, GREY)
    cv.fill_circle(x + 32, y + 54, 3, PAPER)


def icon_chip(cv, x, y, color):
    # Microchip with pins and NVDA label.
    for i in range(4):
        cv.fill_rect(x - 8, y + 18 + i * 22, 8, 8, color)
        cv.fill_rect(x + 96, y + 18 + i * 22, 8, 8, color)
    for i in range(3):
        cv.fill_rect(x + 22 + i * 26, y - 8, 8, 8, color)
        cv.fill_rect(x + 22 + i * 26, y + 96, 8, 8, color)
    cv.fill_rect(x, y, 96, 96, color)
    cv.fill_rect(x + 10, y + 10, 76, 76, PAPER)
    draw_text(cv, x + 48, y + 34, "NVDA", 2, color, align="center")


def icon_bars(cv, x, y, color):
    cv.fill_rect(x, y + 30, 14, 26, color)
    cv.fill_rect(x + 20, y + 16, 14, 40, color)
    cv.fill_rect(x + 40, y + 2, 14, 54, RED)
    cv.hline(x - 4, y + 56, 62, color)


# ---------------------------------------------------------------- layout
# Layout of the front page (1024x1024, all y coordinates in pixels):
#   masthead        y  26-152  "THE WORLD TODAY", date line, tagline
#   lead story      y 168-364  NVIDIA / Huang reinstatement (lead) + chip icon
#   story grid      y 388-950  2 columns x 3 rows, 472x182 cards, 16px gaps
#     row 1: Ukraine/Russian warship off Libya | COP31 no-deal outcome
#     row 2: Pakistan astronaut on Tiangong    | Indonesia factory fire
#     row 3: states sue SpaceX over Grok       | markets box (dark)
#   footer          y 968-994  scope note ("events ... on 24 November 2026")
# Card internals: kicker at +16, headline at +44 (scale 3, leading 22),
# body below the headline (scale 2, leading 16). The leading values are
# chosen so the longest card (3-line headline + 4-line body) still ends
# inside the 182px card: 44 + 3*22 + 6 + 3*16 + 14 = 178.
LEAD = {
    "kicker": "TECHNOLOGY - UNITED STATES",
    "headline": "NVIDIA BRINGS BACK HUANG",
    "body": ("Board reinstates Jensen Huang as chief executive, 11 days after "
             "he resigned. Shares jump 31% in a day and the S&P 500 climbs "
             "4.7%, its best day in over a year."),
}

CARDS = [
    {
        "kicker": "CONFLICT - LIBYA",
        "headline": "UKRAINE SAYS IT SANK RUSSIAN WARSHIP OFF LIBYA",
        "body": ("Kyiv says naval drones sank the corvette Merkury at Benghazi. "
                 "Tripoli demands answers; the UN seeks a probe."),
        "icon": "ship",
        "accent": RED,
    },
    {
        "kicker": "CLIMATE - COP31",
        "headline": "CLIMATE SUMMIT ENDS WITH NO DEAL ON FOSSIL FUELS",
        "body": ("COP31 collapses as governments split over fossil fuels and "
                 "climate finance. Erdogan says talks laid groundwork."),
        "icon": "globe",
        "accent": BLUE,
    },
    {
        "kicker": "SPACE - CHINA-PAKISTAN",
        "headline": "PAKISTAN ASTRONAUT TO FLY ON CHINA SPACE STATION",
        "body": ("Zeeshan Ali will be the first foreign astronaut aboard "
                 "Tiangong, flying on the Shenzhou-24 mission."),
        "icon": "rocket",
        "accent": BLUE,
    },
    {
        "kicker": "DISASTER - INDONESIA",
        "headline": "FACTORY FIRE IN INDONESIA KILLS 26",
        "body": ("Blaze at a plant in Banten leaves 26 dead and dozens "
                 "missing, one of the day's deadliest disasters."),
        "icon": "fire",
        "accent": RED,
    },
    {
        "kicker": "TECHNOLOGY - UNITED STATES",
        "headline": "STATES SUE SPACEX OVER GROK IMAGES",
        "body": ("Oregon and Virginia sue Musk firms, alleging the Grok "
                 "chatbot made sexualised images, including of children."),
        "icon": "phone",
        "accent": RED,
    },
]

MARKETS = [
    "S&P 500  7,237  +4.7%",
    "NIKKEI 225  58,645  +3.9%",
    "BRENT CRUDE  $86.71",
]

ICONS = {
    "ship": icon_ship,
    "globe": icon_globe,
    "rocket": icon_rocket,
    "fire": icon_fire,
    "phone": icon_phone,
}


def draw_poster():
    cv = Canvas()

    # ---- masthead
    draw_text(cv, W // 2, 26, "THE WORLD TODAY", 6, INK, align="center")
    cv.fill_rect(32, 84, W - 64, 3, INK)
    draw_text(cv, W // 2, 98, "TUESDAY 24 NOVEMBER 2026", 3, RED, align="center")
    draw_text(cv, W // 2, 128, "THE DAY IN WORLD NEWS - ONE PAGE", 2, GREY, align="center")
    cv.fill_rect(32, 152, W - 64, 2, RULE)

    # ---- lead story
    ly = 168
    cv.fill_rect(32, ly, W - 64, 196, CARD_BG)
    cv.fill_rect(32, ly, W - 64, 5, RED)
    draw_text(cv, 52, ly + 20, LEAD["kicker"], 2, RED)
    draw_text(cv, 52, ly + 48, LEAD["headline"], 4, INK)
    y = draw_block(cv, 52, ly + 100, wrap(LEAD["body"], 2, 640), 2, INK)
    icon_chip(cv, 836, ly + 52, INK)
    cv.fill_rect(32, ly + 196, W - 64, 2, RULE)

    # ---- story grid: 2 columns x 3 rows (5 cards + markets box)
    gx, gy = 32, 388
    cw = (W - 64 - 16) // 2
    ch = 182
    gap = 16
    positions = [(gx, gy), (gx + cw + gap, gy),
                 (gx, gy + ch + gap), (gx + cw + gap, gy + ch + gap),
                 (gx, gy + 2 * (ch + gap)), (gx + cw + gap, gy + 2 * (ch + gap))]
    for (x, y), card in zip(positions[:5], CARDS):
        cv.fill_rect(x, y, cw, ch, CARD_BG)
        cv.fill_rect(x, y, cw, 4, card["accent"])
        draw_text(cv, x + 18, y + 16, card["kicker"], 2, card["accent"])
        ix, iy = x + cw - 84, y + 12
        if card["icon"] == "globe":
            icon_globe(cv, ix, iy, card["accent"], CARD_BG)
        else:
            ICONS[card["icon"]](cv, ix, iy, card["accent"])
        tw = cw - 18 - 96
        hy = draw_block(cv, x + 18, y + 44,
                        wrap(card["headline"], 3, tw), 3, INK, leading=22)
        draw_block(cv, x + 18, hy + 6, wrap(card["body"], 2, cw - 36), 2, INK,
                   leading=16)

    # ---- markets box
    mx, my = positions[5]
    cv.fill_rect(mx, my, cw, ch, INK)
    draw_text(cv, mx + 18, my + 16, "MARKETS - 24 NOVEMBER", 2, GOLD)
    yy = my + 48
    for line in MARKETS:
        draw_text(cv, mx + 18, yy, line, 2, (240, 236, 224))
        yy += 26
    icon_bars(cv, mx + cw - 92, my + 96, (240, 236, 224))
    draw_text(cv, mx + 18, my + 148, "STOCKS RALLY ON NVIDIA NEWS", 2, GOLD)

    # ---- footer
    cv.fill_rect(32, 968, W - 64, 2, RULE)
    draw_text(cv, W // 2, 980,
              "EVENTS THAT HAPPENED OR WERE FIRST REPORTED ON 24 NOVEMBER 2026",
              2, GREY, align="center")
    return cv


# ---------------------------------------------------------------- png out
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = b"".join(
        b"\x00" + bytes(cv.px[y * cv.width * 3:(y + 1) * cv.width * 3])
        for y in range(cv.height)
    )
    ihdr = struct.pack(">IIBBBBB", cv.width, cv.height, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(raw, 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)
