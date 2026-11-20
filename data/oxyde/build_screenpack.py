#!/usr/bin/env python3
"""
Builds the Oxyde screenpack: system.sff, fight.sff and three fonts.

Everything the pack draws is generated here, so the whole look is one file you
can edit and re-run:

    python3 data/oxyde/build_screenpack.py

Writes  data/oxyde/system.sff
        data/oxyde/fight.sff
        data/oxyde/font/oxyde-s.fnt   11px
        data/oxyde/font/oxyde-m.fnt   15px
        data/oxyde/font/oxyde-l.fnt   19px

The look is the engine's own, moved out of the binary and into a pack: a black
circuit board with etched traces, the OXYDE wordmark with its hexagonal O in
ember and the rest in cold steel, a hairline rule, and Oxyde orange for
whatever the player is about to choose. The board and the rule are ported from
`oxyde-render`'s `splash.rs` and the wordmark from its `brand.rs`, so the pack
and the engine's own screens are the same design rather than two designs that
resemble each other. The title screen itself is the engine's: `[Title Info]
title.style = oxyde` hands it over, and `title_bg` below is what an engine
that ignores the key shows instead.

The pack is authored at 640x480 (`[Info] localcoord`), twice the 320x240 every
WinMugen pack uses, because the archive it fronts is shown on a 1080p panel and
a 320-unit grid cannot hold a thousand legible cells.
"""

import math
import os
import struct

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 640, 480

# ---------------------------------------------------------------- the theme
#
# `oxyde-render/src/splash.rs`, module `theme`. Keep the two in step: the
# engine falls back to drawing these screens itself when a pack cannot supply
# one, and the seam should not show.

VOID      = (6, 7, 9)          # the board
TRACE     = (24, 29, 36)       # an etched run
TRACE_LIT = (46, 56, 68)       # one catching the light
PAD       = (38, 47, 58)       # where a run terminates at a via
STEEL_HI  = (226, 232, 242)    # cold steel, top
STEEL_LO  = (96, 106, 124)     # cold steel, bottom
RUST_HI   = (198, 92, 26)      # OXYDE, top
RUST_LO   = (88, 32, 8)        # OXYDE, bottom
EMBER     = (255, 140, 44)
CYAN      = (96, 214, 246)
INK       = (196, 204, 216)
DIM       = (112, 122, 138)

# Player colours. The engine's own select screen has used these since it had
# one: player one cool, player two warm.
P1COL = (98, 168, 255)
P2COL = (255, 95, 95)

# --------------------------------------------------------------- palette
#
# Index 0 is MUGEN's transparency key and is never drawn into. The rest is a
# set of ramps wide enough that a gradient across one does not band.


def ramp(a, b, n):
    return [
        tuple(round(a[c] + (b[c] - a[c]) * i / (n - 1)) for c in range(3))
        for i in range(n)
    ]


BAND_INK    = (1,   64)        # board black up to steel white: the workhorse
BAND_CYAN   = (64,  96)
BAND_RUST   = (96,  136)       # molten orange, the widest of the accents
BAND_CRIM   = (136, 160)
BAND_AZURE  = (160, 184)
BAND_GREEN  = (184, 200)
BAND_BOARD  = (200, 224)       # the narrow range the traces live in
BAND_WARM   = (224, 248)
BAND_MONO   = (248, 256)

PALETTE = [(255, 0, 255)]
PALETTE += ramp(VOID,          STEEL_HI,          63)
PALETTE += ramp((4, 26, 34),   (170, 236, 254),   32)
# The rust band runs along the wordmark's own axis rather than along a
# straight line to peach: `OXYDE` is the one thing on the screen whose exact
# colour matters, and a generic warm ramp quantises it to red.
PALETTE += ramp((14, 5, 1), RUST_LO, 8)
PALETTE += ramp(RUST_LO, RUST_HI, 16)
PALETTE += ramp(RUST_HI, EMBER, 8)
PALETTE += ramp(EMBER, (255, 214, 168), 8)
PALETTE += ramp((40, 6, 8),    (255, 150, 150),   24)
PALETTE += ramp((4, 16, 42),   (150, 194, 255),   24)
PALETTE += ramp((4, 30, 12),   (140, 240, 160),   16)
PALETTE += ramp(VOID,          (72, 86, 106),     24)
PALETTE += ramp((18, 14, 10),  (242, 234, 222),   24)
PALETTE += ramp((0, 0, 0),     (255, 255, 255),   8)
assert len(PALETTE) == 256, len(PALETTE)


_PAL_CACHE = {}


def pal_image(palette=None):
    palette = palette or PALETTE
    key = id(palette)
    im = _PAL_CACHE.get(key)
    if im is None:
        im = Image.new("P", (1, 1))
        flat = []
        for c in palette:
            flat.extend(c)
        im.putpalette(flat)
        _PAL_CACHE[key] = im
    return im


PAL = pal_image()


def quantise(rgba, dither=False, palette=None, matte=None):
    """RGBA image -> (width, height, index bytes). Alpha < 128 becomes index 0.

    `dither` is for the full-screen backdrops only. A 256-colour palette cannot
    hold a smooth ember bloom across 640 pixels, and without dithering the
    bloom quantises into a set of hard concentric ellipses -- a blobby oval
    rather than a glow. Error diffusion costs nothing on the traces, whose
    colours are in the palette exactly, so it leaves them crisp.
    """
    pal = palette or PALETTE
    # What a half-covered edge pixel is mixed against. The menus keep the
    # first palette entry they always had; the HUD passes a near-black matte,
    # because its pieces are dark glass and a light fringe round every
    # anti-aliased edge read as a white halo on the stage.
    rgb = Image.new("RGB", rgba.size, matte or pal[1])
    rgb.paste(rgba, (0, 0), rgba)
    q = rgb.quantize(
        palette=pal_image(pal),
        dither=Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE,
    )
    idx = bytearray(q.tobytes())
    alpha = rgba.getchannel("A").tobytes()
    dark = min(range(1, len(pal)), key=lambda i: sum(pal[i]))
    for i, a in enumerate(alpha):
        if a < 128:
            idx[i] = 0
        elif idx[i] == 0:
            # An opaque pixel must never land on the transparency key. With a
            # matte it goes to the darkest real colour rather than to entry 1,
            # which in the HUD's table is near-white: an opaque black row was
            # coming out as a white line.
            idx[i] = dark if matte else 1
    return rgba.size[0], rgba.size[1], bytes(idx)


# ------------------------------------------------------------------- PCX

def write_pcx(w, h, idx, palette=PALETTE):
    """8bpp, one plane, RLE - the only PCX variant SFF v1 carries."""
    hdr = bytearray(128)
    hdr[0] = 0x0A            # ZSoft
    hdr[1] = 5               # version 3.0 with palette
    hdr[2] = 1               # RLE
    hdr[3] = 8               # bits per pixel per plane
    struct.pack_into("<HHHH", hdr, 4, 0, 0, w - 1, h - 1)
    struct.pack_into("<HH", hdr, 12, 72, 72)
    hdr[65] = 1              # planes
    stride = w + (w & 1)     # PCX scanlines are an even number of bytes
    struct.pack_into("<H", hdr, 66, stride)
    struct.pack_into("<H", hdr, 68, 1)   # palette info: colour

    out = bytearray(hdr)
    for y in range(h):
        row = idx[y * w:(y + 1) * w]
        if stride > w:
            row = row + bytes([row[-1] if row else 0])
        x = 0
        n = len(row)
        while x < n:
            v = row[x]
            run = 1
            while x + run < n and row[x + run] == v and run < 63:
                run += 1
            if run > 1 or v >= 0xC0:
                out.append(0xC0 | run)
                out.append(v)
            else:
                out.append(v)
            x += run
    out.append(0x0C)
    for c in palette:
        out.extend(c)
    return bytes(out)


# ------------------------------------------------------------------- SFF

def write_sff(path, sprites, palette=None):
    """`sprites` is a list of (group, image, axis, width, height, indices).

    `palette` is the one every sprite in the file is indexed against; the
    first sprite declares it and the rest say "same as the previous", which
    is how MUGEN's own packs are written.
    """
    palette = palette or PALETTE
    hdr = bytearray(512)
    hdr[0:12] = b"ElecbyteSpr\0"
    hdr[12:16] = bytes([0, 1, 0, 1])          # v1.01, stored low byte first
    groups = len({s[0] for s in sprites})
    struct.pack_into("<IIII", hdr, 16, groups, len(sprites), 512, 32)
    hdr[32] = 0                                # shared palette
    hdr[36:36 + 60] = b"Oxyde screenpack"[:60].ljust(60, b"\0")

    body = bytearray()
    payloads = []
    for i, (g, im, axis, w, h, idx) in enumerate(sprites):
        # Every sprite carries the same palette; only the first declares it, as
        # MUGEN's own packs do.
        payloads.append((g, im, axis, write_pcx(w, h, idx, palette), i == 0))

    offset = 512
    for i, (g, im, axis, pcx, own_pal) in enumerate(payloads):
        last = i == len(payloads) - 1
        nxt = 0 if last else offset + 32 + len(pcx)
        sub = bytearray(32)
        struct.pack_into("<II", sub, 0, nxt, len(pcx))
        struct.pack_into("<hh", sub, 8, axis[0], axis[1])
        struct.pack_into("<HHH", sub, 12, g & 0xFFFF, im & 0xFFFF, 0)
        sub[18] = 0 if own_pal else 1          # palletSame
        body.extend(sub)
        body.extend(pcx)
        offset += 32 + len(pcx)

    with open(path, "wb") as f:
        f.write(hdr)
        f.write(body)
    return len(hdr) + len(body)


# ------------------------------------------------------------------- FNT
#
# Bank order is what every `font = n, bank, align` line in system.def and
# fight.def refers to, so it is part of the pack's interface. Changing the
# colours here is free; changing the order means editing both .def files.

BANKS = [
    INK,                # 0 ink        - the default
    CYAN,               # 1 cyan       - the one thing about to be chosen
    EMBER,              # 2 ember      - the stage, the announcements
    P2COL,              # 3 crimson    - player two
    P1COL,              # 4 azure      - player one
    DIM,                # 5 dim        - inactive rows
    (110, 242, 154),    # 6 green      - confirmations
    STEEL_HI,           # 7 steel      - headings
]
LEVELS = 7             # antialiasing steps inside one bank
COLORS = LEVELS + 1    # `Colors =` in the .fnt: the stride between banks

GLYPHS = "".join(chr(c) for c in range(32, 127))


def font_palette():
    pal = [(0, 0, 0)] * 256
    for b, base in enumerate(BANKS):
        for k in range(1, LEVELS + 1):
            t = 0.20 + 0.80 * (k - 1) / (LEVELS - 1)
            pal[b * COLORS + k] = tuple(round(c * t) for c in base)
    return pal


def build_fnt(path, ttf, px, cell_h, tracking=0, name=""):
    face = ImageFont.truetype(ttf, px)
    # Measure every glyph first: the sheet is one row, glyphs side by side.
    metrics = []
    for ch in GLYPHS:
        box = face.getbbox(ch)
        adv = round(face.getlength(ch))
        w = max(adv, (box[2] if box else 0)) + tracking
        metrics.append((ch, max(1, w)))

    sheet_w = sum(m[1] for m in metrics)
    sheet = Image.new("L", (sheet_w, cell_h), 0)
    draw = ImageDraw.Draw(sheet)
    # Sit the ascenders one pixel below the top of the cell.
    asc, _desc = face.getmetrics()
    baseline = min(cell_h - 1, asc + 1)
    x = 0
    xs = []
    for ch, w in metrics:
        xs.append(x)
        draw.text((x, baseline), ch, font=face, fill=255, anchor="ls")
        x += w

    # Alpha -> palette index inside bank 0.
    src = sheet.tobytes()
    idx = bytearray(len(src))
    for i, a in enumerate(src):
        if a < 24:
            continue
        k = 1 + round((a - 24) * (LEVELS - 1) / 231.0)
        idx[i] = max(1, min(LEVELS, k))

    pal = font_palette()
    pcx = write_pcx(sheet_w, cell_h, bytes(idx), pal)

    lines = [
        "; %s - part of the Oxyde screenpack" % (name or os.path.basename(path)),
        "; generated by data/oxyde/build_screenpack.py",
        "[Def]",
        "Type = variable",
        "Size = %d,%d" % (metrics[0][1], cell_h),
        "Spacing = 0,1",
        "Colors = %d" % COLORS,
        "Offset = 0,0",
        "[Map]",
    ]
    for (ch, w), sx in zip(metrics, xs):
        # A map line that begins with `;`, `[` or a space cannot be read back
        # as itself, so those characters are named by code.
        key = ch if ch not in ' ;[' else "0x%02X" % ord(ch)
        lines.append("%s %d %d" % (key, sx, w))
    txt = ("\r\n".join(lines) + "\r\n").encode("latin-1")

    hdr = bytearray(64)
    hdr[0:12] = b"ElecbyteFnt\0"
    hdr[12:16] = bytes([0, 0, 1, 0])
    struct.pack_into("<IIII", hdr, 16, 64, len(pcx), 64 + len(pcx), len(txt))
    with open(path, "wb") as f:
        f.write(hdr)
        f.write(pcx)
        f.write(txt)
    return sheet_w, cell_h


# --------------------------------------------------------------- the board
#
# A port of `splash.rs::draw_circuit_backdrop`, seed and all, so the pack's
# board is the same board the engine draws when it has no pack.


class Etch:
    """The engine's little LCG. The traces must not shimmer, so the board is
    generated from a fixed seed rather than from anything random."""

    def __init__(self, seed):
        self.state = seed & 0xFFFFFFFF

    def next(self):
        self.state = (self.state * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.state >> 8

    def range(self, lo, hi):
        if hi <= lo:
            return lo
        return lo + self.next() % (hi - lo)


def circuit_board(w, h, bloom=1.0, seed=0x0C11CE5):
    """The black board with etched traces, drawn at 1:1.

    Everything is axis-aligned with square elbows, which is how a real board is
    routed and, more practically, the only way thin lines stay crisp without
    antialiasing -- so this one is *not* drawn supersampled like the rest of
    the pack. Traces are quiet through the middle third, where the wordmark and
    the menu live.
    """
    img = Image.new("RGBA", (w, h), VOID + (255,))
    d = ImageDraw.Draw(img)
    s = max(h // 240, 1)

    def rect(x, y, rw, rh, colour):
        if rw <= 0 or rh <= 0:
            return
        d.rectangle([x, y, x + rw - 1, y + rh - 1], fill=colour + (255,))

    e = Etch(seed)
    count = min(400, max(40, (w * h) // (9000 * s)))
    for _ in range(count):
        x = e.range(-w // 8, w + w // 8)
        y = e.range(-h // 8, h + h // 8)
        centre = abs(y - h // 2) < h // 5 and abs(x - w // 2) < w // 3
        lit = (not centre) and e.next() % 5 == 0
        colour = TRACE_LIT if lit else TRACE
        thickness = s
        legs = e.range(2, 5)
        horizontal = e.next() % 2 == 0
        for _ in range(legs):
            run = e.range(8 * s, 60 * s)
            step = 1 if e.next() % 2 == 0 else -1
            if horizontal:
                x2 = x + run * step
                rect(min(x, x2), y, max(abs(x2 - x), thickness), thickness, colour)
                x = x2
            else:
                y2 = y + run * step
                rect(x, min(y, y2), thickness, max(abs(y2 - y), thickness), colour)
                y = y2
            horizontal = not horizontal
        # A pad at the end of the run, the way a trace terminates at a via.
        r = 2 * s
        rect(x - r, y - r, r * 2, r * 2, PAD)
        rect(x - r // 2, y - r // 2, max(r, 1), max(r, 1), VOID)

    # A slow ember bloom behind where the wordmark sits, and a vignette that
    # pulls the eye back to the middle.
    px = img.load()
    for yy in range(h):
        ny = (yy / h) * 2.0 - 1.0
        for xx in range(w):
            nx = (xx / w) * 2.0 - 1.0
            b = max(0.0, 1.0 - (nx * nx * 1.6 + (ny + 0.45) ** 2 * 2.4)) * bloom
            vig = min(0.85, (nx * nx + ny * ny) * 0.35)
            if b <= 0.0 and vig <= 0.0:
                continue
            r, g, bl, a = px[xx, yy]
            px[xx, yy] = (
                min(255, int(r * (1 - vig) + 34.0 * b)),
                min(255, int(g * (1 - vig) + 13.0 * b)),
                min(255, int(bl * (1 - vig) + 4.0 * b)),
                a,
            )
    return img


# ------------------------------------------------------- the wordmark faces
#
# `splash.rs::LOGO_GLYPHS`. Nine hand-drawn 8x12 letterforms rather than the UI
# face scaled up: an upscaled 5x7 reads as a placeholder, and this is the one
# mark on the screen that has to look deliberate.

LOGO_W, LOGO_H = 8, 12
LOGO_GLYPHS = {
    "M": ["##....##", "##....##", "###..###", "###..###", "########", "########",
          "##.##.##", "##.##.##", "##....##", "##....##", "##....##", "##....##"],
    "U": ["##....##", "##....##", "##....##", "##....##", "##....##", "##....##",
          "##....##", "##....##", "##....##", "###..###", ".######.", "..####.."],
    "G": ["..####..", ".######.", "##....##", "##......", "##......", "##..####",
          "##..####", "##....##", "##....##", "###..###", ".######.", "..####.."],
    "E": ["########", "########", "##......", "##......", "######..", "######..",
          "##......", "##......", "##......", "##......", "########", "########"],
    "N": ["##....##", "###...##", "####..##", "####..##", "##.##.##", "##.##.##",
          "##..####", "##..####", "##...###", "##....##", "##....##", "##....##"],
    "O": ["..####..", ".######.", "##....##", "##....##", "##....##", "##....##",
          "##....##", "##....##", "##....##", "##....##", ".######.", "..####.."],
    "X": ["##....##", "##....##", ".##..##.", ".##..##.", "..####..", "..####..",
          "..####..", ".##..##.", ".##..##.", "##....##", "##....##", "##....##"],
    "Y": ["##....##", "##....##", ".##..##.", ".##..##.", "..####..", "..####..",
          "...##...", "...##...", "...##...", "...##...", "...##...", "...##..."],
    "D": ["#######.", "########", "##....##", "##....##", "##....##", "##....##",
          "##....##", "##....##", "##....##", "##....##", "########", "#######."],
    " ": ["........"] * 12,
}


def logo_width(word, scale):
    n = len(word)
    return 0 if n == 0 else n * (LOGO_W + 1) * scale - scale


def logo_mask(word, scale):
    """Every filled cell of the wordmark, as (x, y) pixel corners."""
    out = []
    cx = 0
    for ch in word.upper():
        art = LOGO_GLYPHS.get(ch)
        if art:
            for row, line in enumerate(art):
                for col, c in enumerate(line):
                    if c != ".":
                        out.append((cx + col * scale, row * scale))
        cx += (LOGO_W + 1) * scale
    return out


def draw_logo(d, x, y, word, scale, top, bottom, outline=True):
    """The wordmark, with a vertical gradient and a dark outline.

    The outline is what keeps it legible over a board that has traces running
    behind it.
    """
    cells = logo_mask(word, scale)
    if outline:
        o = max(1, round(scale * 0.34))
        for gx, gy in cells:
            for dy in range(-o, o + 1):
                for dx in range(-o, o + 1):
                    if dx == 0 and dy == 0:
                        continue
                    d.rectangle(
                        [x + gx + dx, y + gy + dy,
                         x + gx + dx + scale - 1, y + gy + dy + scale - 1],
                        fill=(10, 11, 15, 255),
                    )
    span = max(1, LOGO_H * scale - 1)
    for gx, gy in cells:
        t = gy / span
        c = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.rectangle([x + gx, y + gy, x + gx + scale - 1, y + gy + scale - 1],
                    fill=c + (255,))


# ------------------------------------------------------------ the wordmark
#
# `oxyde-render/src/brand.rs`, ported line for line: OXYDE, with the O cut as
# the hexagon the HUD's plates are made of, the letters leaned on the bars'
# slant, rendered from a signed distance so the edge, the rim, the shadow and
# the ember glow are one evaluation per pixel. Keep the two in step -- the
# engine draws the same mark on its own screens, and the seam should not show.

WM_LEAN, WM_STROKE, WM_GAP = 0.16, 0.205, 0.15
WM_W = dict(O=1.10, X=0.86, Y=0.88, D=0.84, E=0.70)
WM_STEEL = ((250, 251, 255), (204, 211, 226), (118, 128, 150))
WM_EMBER = ((255, 206, 128), (255, 138, 40), (196, 70, 14))


def wordmark_width(height):
    return (sum(WM_W.values()) + 4 * WM_GAP + WM_LEAN) * height


def _convex(pts):
    import numpy as np
    n = len(pts)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    edges = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = max(math.hypot(dx, dy), 1e-6)
        nx, ny = dy / ln, -dx / ln
        if nx * (cx - a[0]) + ny * (cy - a[1]) > 0:
            nx, ny = -nx, -ny
        edges.append((nx, ny, nx * a[0] + ny * a[1]))
    return edges


def _sd(edges, u, v):
    import numpy as np
    d = None
    for nx, ny, c in edges:
        e = nx * u + ny * v - c
        d = e if d is None else np.maximum(d, e)
    return d


def _diag(run, t):
    a = t
    for _ in range(8):
        a = t * math.sqrt((run - a) ** 2 + 1.0)
    return a


def _wordmark_parts():
    """[(edges, ring_thickness_or_None)] for the O, then for the rest."""
    t = WM_STROKE
    x = 0.0
    w = WM_W["O"]
    c = 0.27 * min(w, 1.15)
    o = [(_convex([(x, .5), (x + c, 0), (x + w - c, 0), (x + w, .5), (x + w - c, 1), (x + c, 1)]), t)]
    x += w + WM_GAP
    rest = []
    w = WM_W["X"]
    a = _diag(w, t * 1.04)
    rest.append((_convex([(x, 0), (x + a, 0), (x + w, 1), (x + w - a, 1)]), None))
    rest.append((_convex([(x + w - a, 0), (x + w, 0), (x + a, 1), (x, 1)]), None))
    x += w + WM_GAP
    w = WM_W["Y"]
    jy, cx = 0.54, x + w / 2
    a = _diag(w / 2, t)
    rest.append((_convex([(x, 0), (x + a, 0), (cx + t / 2, jy), (cx - t / 2, jy)]), None))
    rest.append((_convex([(x + w - a, 0), (x + w, 0), (cx + t / 2, jy), (cx - t / 2, jy)]), None))
    rest.append((_convex([(cx - t / 2, jy - .06), (cx + t / 2, jy - .06), (cx + t / 2, 1), (cx - t / 2, 1)]), None))
    x += w + WM_GAP
    w, c = WM_W["D"], 0.30
    rest.append((_convex([(x, 0), (x + w - c, 0), (x + w, c), (x + w, 1 - c), (x + w - c, 1), (x, 1)]), t))
    x += w + WM_GAP
    w = WM_W["E"]
    for box in ((x, 0, x + t, 1), (x, 0, x + w, t), (x, .5 - t / 2, x + w * .82, .5 + t / 2), (x, 1 - t, x + w, 1)):
        x0, y0, x1, y1 = box
        rest.append((_convex([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), None))
    return o, rest


def _union(parts, u, v):
    import numpy as np
    d = None
    for edges, ring in parts:
        e = _sd(edges, u, v)
        if ring is not None:
            e = np.maximum(e, -(e + ring))
        d = e if d is None else np.minimum(d, e)
    return d


def oxyde_wordmark(height):
    """The wordmark with letters `height` pixels tall, as an RGBA image with
    room round it for the glow. Returns (image, pad)."""
    import numpy as np
    pad = int(math.ceil(height * 0.42)) + 2
    w = int(math.ceil(wordmark_width(height))) + pad * 2
    h = int(math.ceil(height)) + pad * 2
    iy, ix = np.mgrid[0:h, 0:w].astype(np.float64)
    sy, sx = iy - pad + 0.5, ix - pad + 0.5
    unit = 1.0 / height
    o, rest = _wordmark_parts()

    def dist(sx, sy):
        v = sy * unit
        u = sx * unit - WM_LEAN * (1.0 - v)
        return _union(o, u, v) * height, _union(rest, u, v) * height, u, v

    d_o, d_r, u, v = dist(sx, sy)
    d = np.minimum(d_o, d_r)
    shadow_dy = max(height * 0.045, 1.0)
    shadow_soft = max(height * 0.06, 1.5)
    do_s, dr_s, _, _ = dist(sx, sy - shadow_dy)
    ds = np.minimum(do_s, dr_s)
    rim = max(height * 0.03, 1.1)
    glow_r = height * 0.15
    reach = max(pad - 1.5, 1.0)

    def smooth(e0, e1, x):
        t = np.clip((x - e0) / (e1 - e0), 0, 1)
        return t * t * (3 - 2 * t)

    def mix(a, b, t):
        t = np.clip(t, 0, 1)[..., None]
        return np.array(a, float) * (1 - t) + np.array(b, float) * t

    def ramp3(c, t):
        return np.where((t < 0.5)[..., None], mix(c[0], c[1], t * 2), mix(c[1], c[2], (t - 0.5) * 2))

    acc = np.zeros((h, w, 3))
    alpha = np.zeros((h, w))

    def over(col, a):
        nonlocal acc, alpha
        a = np.clip(a, 0, 1)[..., None]
        acc = acc * (1 - a) + col * a
        alpha = alpha * (1 - a[..., 0]) + a[..., 0]

    fade = lambda dd: 1 - smooth(reach * 0.45, reach, dd)
    g = np.exp(-np.maximum(d_o, 0) / glow_r) * 0.60 * fade(d_o) * (d_o < reach)
    over(mix(WM_EMBER[1], WM_EMBER[2], np.full((h, w), 0.35)), g)
    g = np.exp(-np.maximum(d_r, 0) / (glow_r * 0.5)) * 0.10 * fade(d_r) * (d_r < reach)
    over(mix(WM_EMBER[1], WM_EMBER[2], np.full((h, w), 0.5)), g)
    over(np.zeros((h, w, 3)), (1 - smooth(-shadow_soft, shadow_soft, ds)) * 0.75)
    over(np.broadcast_to(np.array((7.0, 8.0, 12.0)), (h, w, 3)), np.clip(rim + 0.5 - d, 0, 1))
    fc = np.clip(0.5 - d, 0, 1)
    steel = ramp3(WM_STEEL, v)
    ember = ramp3(WM_EMBER, v)
    depth = -d_o
    mid = np.abs(depth - WM_STROKE * height * 0.5)
    line = 1 - smooth(0.0, max(height * 0.025, 0.8), mid - height * 0.012)
    lit = np.clip(line * 0.55, 0, 1)[..., None]
    ember = ember + (np.array((255.0, 236.0, 200.0)) - ember) * lit
    over(np.where((d_o <= d_r)[..., None], ember, steel), fc)
    rgb_ = np.where(alpha[..., None] > 0, acc / np.maximum(alpha, 1e-6)[..., None], 0)
    out = np.dstack([np.clip(rgb_, 0, 255), np.clip(alpha * 255, 0, 255)]).round().astype(np.uint8)
    return Image.fromarray(out, "RGBA"), pad


def hud_rule(d, cx, y, half_width, gap, s):
    """`splash.rs::draw_rule`: a hairline broken by tick marks, with a space in
    the middle for the infinity mark."""
    s = max(1, s)
    for step in (-1, 1):
        near = cx + step * gap
        far = cx + step * half_width
        x0, x1 = (near, far) if near < far else (far, near)
        d.rectangle([x0, y, x1, y + s - 1], fill=TRACE_LIT + (255,))
        span = max(1, half_width - gap)
        for n, tint in enumerate((PAD, TRACE_LIT, CYAN)):
            at = far - step * (n + 1) * span // 5
            d.rectangle([at, y - 2 * s, at + s - 1, y + 3 * s - 1], fill=tint + (255,))
        run = 12 * s
        start = near if step > 0 else near - run
        d.rectangle([start, y, start + run - 1, y + s - 1], fill=EMBER + (255,))


def infinity(d, cx, cy, s, colour):
    """`splash.rs::draw_infinity`: two rings that meet in the middle, drawn
    from the distance to each centre. At this size a square annulus reads as
    two little windows rather than as a lemniscate."""
    # A shade finer than the engine's own `thickness = s`: the pack is
    # authored at 640x480 and then scaled up to the window, which doubles the
    # stroke, and at that width the two rings close into a blob.
    r = max(3.0, 3.2 * s)
    thick = max(1.0, s * 0.6)
    lobes = ((cx - r, cy), (cx + r, cy))
    reach = int(math.ceil(r + thick))
    for y in range(cy - reach, cy + reach + 1):
        for x in range(cx - reach * 2, cx + reach * 2 + 1):
            on = False
            for lx, ly in lobes:
                dist = math.hypot(x - lx, y - ly)
                if abs(dist - r) <= thick:
                    on = True
                    break
            if on:
                d.point((x, y), fill=colour + (255,))


# ------------------------------------------------------------------- art
#
# Everything else is drawn at 2x and downsampled, so edges and curves come out
# antialiased before they are quantised. The board is the exception, above.

SS = 2


def canvas(w, h, fill=(0, 0, 0, 0)):
    return Image.new("RGBA", (w * SS, h * SS), fill)


def finish(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def s(v):
    return v * SS


def rule(d, y, x0, x1, colour, alpha=170, weight=1):
    d.rectangle([x0, y, x1, y + weight * SS - 1], fill=colour + (alpha,))


def bracket(d, box, colour, alpha=255, arm=10, weight=2):
    """Four corner brackets - the pack's one repeated motif, and the shape a
    trace makes when it turns."""
    x0, y0, x1, y1 = box
    a = arm * SS
    w = weight * SS
    c = colour + (alpha,)
    for (cx, sx) in ((x0, 1), (x1 - w + 1, -1)):
        for (cy, sy) in ((y0, 1), (y1 - w + 1, -1)):
            hx = cx if sx > 0 else cx - a + w
            d.rectangle([hx, cy, hx + a - 1, cy + w - 1], fill=c)
            vy = cy if sy > 0 else cy - a + w
            d.rectangle([cx, vy, cx + w - 1, vy + a - 1], fill=c)


def panel(d, box, fill=(10, 12, 17), alpha=215, edge=TRACE_LIT, inset=True):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=fill + (alpha,))
    d.rectangle([x0, y0, x1, y1], outline=edge + (255,), width=1 * SS)
    if inset:
        d.rectangle([x0 + 2 * SS, y0 + 2 * SS, x1 - 2 * SS, y1 - 2 * SS],
                    outline=TRACE + (200,), width=1)


def text(d, xy, string, ttf, px, fill, anchor="la", spacing=0):
    f = ImageFont.truetype(ttf, px * SS)
    if spacing == 0:
        d.text((xy[0], xy[1]), string, font=f, fill=fill, anchor=anchor)
        return
    # Letter-spaced runs. At these sizes the tracking is most of the
    # difference between a title screen and a directory listing.
    widths = [f.getlength(c) + spacing * SS for c in string]
    total = sum(widths) - spacing * SS
    x = xy[0] - (total / 2 if anchor[0] == "m" else (total if anchor[0] == "r" else 0))
    for c, w in zip(string, widths):
        d.text((x, xy[1]), c, font=f, fill=fill, anchor="l" + anchor[1])
        x += w


BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
COND = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"


# ---------------------------------------------------------------- screens

# Select screen geometry, in the pack's own 640x480 units. Kept here because
# system.def and the backdrop art have to agree about it to the pixel.
GRID = dict(x=21, y=156, cell=28, gap=2, cols=20, rows=10)
FACE_BOX = (18, 32, 102, 130)          # p1; p2 is the mirror about x=320


def board_bg(bloom=1.0, seed=0x0C11CE5):
    """A board at final resolution, as an RGBA canvas ready to draw over."""
    return circuit_board(W, H, bloom=bloom, seed=seed).convert("RGBA")


def bare_bg():
    """A transparent canvas for a backdrop whose board the engine draws itself.

    Title and options say `board = bloom, seed` in their BGdef, so Oxyde paints
    `circuit_board` at the window's own resolution and full width, and only the
    decoration over it comes from the pack. Baked in, the board was a 640x480
    copy scaled up by 1.5 or 2.25 and pillarboxed on a 16:9 screen -- softer
    and narrower than the same board on the screens the engine draws, which is
    what made the title look different from Online.
    """
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def overlay(base, draw_fn):
    """Draw supersampled decoration over a 1:1 board."""
    layer = canvas(W, H)
    draw_fn(ImageDraw.Draw(layer))
    return Image.alpha_composite(base, finish(layer, W, H))


def title_bg():
    """The title screen: board, wordmark, tagline, rule, and nothing else.

    Oxyde draws its own title over this pack (`title.style = oxyde`), so this
    is the backdrop an engine that ignores the key shows -- WinMUGEN, or an
    older Oxyde. The menu is text laid out from `[Title Info]`, so the art
    stops where the menu starts, which is also why the board is quiet through
    the middle third.
    """
    img = bare_bg()          # board = 1.0, 12655845 in [TitleBGdef]

    # The wordmark, centred: the hexagonal O in ember, the rest in steel.
    mark_h = 64
    wm, pad = oxyde_wordmark(mark_h)
    lw = wordmark_width(mark_h)
    img.alpha_composite(wm, (int(round(W / 2 - lw / 2)) - pad, 40 - pad))

    def deco(dd):
        text(dd, (s(W // 2), s(134)), "A MUGEN-COMPATIBLE FIGHTING ENGINE", COND, 12,
             DIM + (255,), anchor="mm", spacing=4)
    img = overlay(img, deco)
    d = ImageDraw.Draw(img)

    # The HUD rule, with the infinity mark sitting in the gap it leaves.
    hud_rule(d, W // 2, 158, 268, 34, 2)
    infinity(d, W // 2, 159, 3, EMBER)

    def frame(dd):
        bracket(dd, (s(12), s(12), s(628), s(468)), TRACE_LIT, 200, arm=26, weight=2)
    return overlay(img, frame)


def select_bg():
    img = board_bg(bloom=0.35, seed=0x51EEC7)
    g = GRID
    gx1 = g["x"] + g["cols"] * (g["cell"] + g["gap"]) - g["gap"]
    gy1 = g["y"] + g["rows"] * (g["cell"] + g["gap"]) - g["gap"]

    def deco(d):
        # The roster plate, darker than the board so a page of two hundred
        # cells reads as one block rather than as confetti on a gradient.
        plate = (s(g["x"] - 7), s(g["y"] - 7), s(gx1 + 6), s(gy1 + 6))
        d.rectangle(plate, fill=(4, 5, 7, 215))
        d.rectangle(plate, outline=TRACE_LIT + (255,), width=SS)
        bracket(d, plate, CYAN, 190, arm=16)

        # Portrait wells, one each side, in the side's own colour.
        for box, col in ((FACE_BOX, P1COL),
                         ((W - FACE_BOX[2], FACE_BOX[1], W - FACE_BOX[0], FACE_BOX[3]),
                          P2COL)):
            x0, y0, x1, y1 = [s(v) for v in box]
            well = (x0 - s(3), y0 - s(3), x1 + s(3), y1 + s(3))
            panel(d, well)
            bracket(d, well, col, 220, arm=12)
            rule(d, y1 + s(6), x0 - s(3), x1 + s(3), col, 150)

        rule(d, s(29), s(16), s(624), TRACE_LIT, 200)
        rule(d, s(152), s(16), s(624), TRACE, 255)
        rule(d, s(458), s(16), s(624), TRACE, 255)
        # One ember run under the header, where the eye lands.
        rule(d, s(29), s(16), s(96), EMBER, 200)
    return overlay(img, deco)


def versus_bg():
    img = board_bg(bloom=0.8, seed=0x5AB0)

    def wells(d):
        for x0, x1, col in ((s(24), s(250), P1COL), (s(390), s(616), P2COL)):
            panel(d, (x0, s(60), x1, s(330)))
            bracket(d, (x0, s(60), x1, s(330)), col, 230, arm=22)
            rule(d, s(334), x0, x1, col, 190, 2)
    img = overlay(img, wells)

    # The VS mark, in the wordmark's ember, with its own glow behind it.
    glow = canvas(W, H)
    gd = ImageDraw.Draw(glow)
    text(gd, (s(320), s(180)), "VS", BOLD, 86, EMBER + (150,), anchor="mm")
    img = Image.alpha_composite(img, finish(glow.filter(ImageFilter.GaussianBlur(9 * SS)), W, H))

    def mark(d):
        text(d, (s(322), s(182)), "VS", BOLD, 86, (8, 10, 16, 255), anchor="mm")
        text(d, (s(320), s(180)), "VS", BOLD, 86, EMBER + (255,), anchor="mm")
        rule(d, s(250), s(272), s(368), CYAN, 190)
        rule(d, s(392), s(60), s(580), TRACE_LIT, 200)
        text(d, (s(320), s(410)), "O X Y D E", COND, 14,
             DIM + (255,), anchor="mm")
        bracket(d, (s(12), s(12), s(628), s(468)), TRACE_LIT, 190, arm=24, weight=2)
    return overlay(img, mark)


def options_bg():
    img = bare_bg()          # board = 0.5, 462981 in [OptionBGdef]

    def deco(d):
        # Corner brackets only. The settings panel carries its own accent rule,
        # and a full-width one here pokes out either side of it.
        bracket(d, (s(12), s(12), s(628), s(468)), TRACE_LIT, 200, arm=26, weight=2)
    return overlay(img, deco)


def trace_tile():
    """A 64x64 add-blended tile that drifts over the backdrops: a second, much
    fainter layer of routing, so the board has depth without the traces
    themselves ever moving."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(0, 64, 16):
        d.rectangle([i, 0, i, 63], fill=(8, 10, 14, 255))
    for i in range(8, 64, 32):
        d.rectangle([0, i, 63, i], fill=(7, 9, 12, 255))
    d.rectangle([14, 6, 16, 8], fill=(11, 14, 18, 255))
    d.rectangle([46, 38, 48, 40], fill=(11, 14, 18, 255))
    return img


def wordmark():
    """The wordmark as its own sprite, for the select banner and any screen
    that wants it away from the backdrop. As tall as the stacked two-line
    logotype it replaced, so nothing laid out round it moves; wider, because
    the name is now one line."""
    scale = 3
    w = 300
    h = LOGO_H * scale * 2 + 14
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mark_h = min(h * 0.56, (w - 8) / (wordmark_width(1.0) + 0.84))
    wm, pad = oxyde_wordmark(mark_h)
    lw = wordmark_width(mark_h)
    x = int(round(w / 2 - lw / 2)) - pad
    y = int(round(h / 2 - mark_h / 2)) - pad
    img.alpha_composite(wm.crop((max(0, -x), max(0, -y), wm.size[0], wm.size[1])), (max(0, x), max(0, y)))
    return img


def select_banner():
    # Deep enough for the stacked wordmark, the rule under it and the caption:
    # the wordmark is 2 x LOGO_H at scale 3 plus its gaps, so this is measured
    # against it rather than guessed.
    scale = 3
    wm_h = LOGO_H * scale * 2 + 14
    w, h = 404, wm_h + 40
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer = canvas(w, h)
    d = ImageDraw.Draw(layer)
    panel(d, (0, 0, s(w) - 1, s(h) - 1), (6, 8, 11), 190)
    bracket(d, (0, 0, s(w) - 1, s(h) - 1), TRACE_LIT, 220, arm=14)
    text(d, (s(w // 2), s(h - 13)), "SELECT YOUR FIGHTER", COND, 12,
         DIM + (255,), anchor="mm", spacing=2)
    img = Image.alpha_composite(img, finish(layer, w, h))

    wm = wordmark()
    img.alpha_composite(wm, (w // 2 - wm.size[0] // 2, 6))
    d = ImageDraw.Draw(img)
    hud_rule(d, w // 2, wm_h + 10, 150, 26, 1)
    infinity(d, w // 2, wm_h + 10, 2, EMBER)
    return img


def cell_bg():
    n = GRID["cell"]
    img = canvas(n, n)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, s(n) - 1, s(n) - 1], fill=(11, 13, 18, 255))
    d.rectangle([0, 0, s(n) - 1, s(n) - 1], outline=TRACE_LIT + (255,), width=SS)
    # A lit top edge, the way a pad catches the light.
    d.line([(SS, SS), (s(n) - 2 * SS, SS)], fill=PAD + (255,), width=SS)
    return finish(img, n, n)


def random_cell(frame, total):
    n = GRID["cell"]
    img = canvas(n, n)
    d = ImageDraw.Draw(img)
    t = frame / total
    d.rectangle([0, 0, s(n) - 1, s(n) - 1], fill=(20, 12, 6, 255))
    d.rectangle([0, 0, s(n) - 1, s(n) - 1], outline=RUST_HI + (255,), width=SS)
    pulse = 0.55 + 0.45 * math.sin(t * 2 * math.pi)
    col = tuple(round(c * (0.45 + 0.55 * pulse)) for c in EMBER)
    text(d, (s(n) // 2, s(n) // 2 + SS), "?", BOLD, 19, col + (255,), anchor="mm")
    # A tick travelling round the border, so the cell reads as "still rolling".
    per = s(n) * 4 - 4 * SS
    p = int(t * per)
    side, run = divmod(p, s(n) - SS)
    seg = [(run, 0), (s(n) - SS, run), (s(n) - SS - run, s(n) - SS),
           (0, s(n) - SS - run)][side % 4]
    d.rectangle([seg[0], seg[1], seg[0] + 3 * SS, seg[1] + SS], fill=EMBER + (255,))
    return finish(img, n, n)


def cursor(colour, frame, total, done=False):
    n = GRID["cell"] + 4
    img = canvas(n, n)
    d = ImageDraw.Draw(img)
    if done:
        d.rectangle([0, 0, s(n) - 1, s(n) - 1], outline=colour + (255,), width=2 * SS)
        bracket(d, (0, 0, s(n) - 1, s(n) - 1), STEEL_HI, 220, arm=9, weight=2)
        return finish(img, n, n)
    t = frame / total
    grow = int(round(2 * SS * math.sin(t * 2 * math.pi)))
    a = 200 + int(55 * math.sin(t * 2 * math.pi))
    bracket(d, (grow, grow, s(n) - 1 - grow, s(n) - 1 - grow), colour, a, arm=11, weight=2)
    d.rectangle([grow, grow, s(n) - 1 - grow, s(n) - 1 - grow],
                outline=colour + (70,), width=SS)
    return finish(img, n, n)


def caret(colour):
    """`splash.rs::draw_caret`: the solid triangle the engine's own menus use.
    The one mark on the screen that has to read instantly at any scale, so it
    is a shape rather than a glyph."""
    img = canvas(14, 16)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (s(13), s(8)), (0, s(15))], fill=colour + (255,))
    return finish(img, 14, 16)


def team_icon(colour, filled):
    img = canvas(14, 14)
    d = ImageDraw.Draw(img)
    box = [SS, SS, s(13) - SS, s(13) - SS]
    if filled:
        d.ellipse(box, fill=colour + (255,), outline=STEEL_HI + (255,), width=SS)
    else:
        d.ellipse(box, outline=TRACE_LIT + (255,), width=SS)
    return finish(img, 14, 14)


# ------------------------------------------------------------------ main

CURSOR_FRAMES = 6
RANDOM_FRAMES = 8


def build():
    sprites = []

    def add(group, image, img, axis=None):
        full = img.size == (W, H)
        w, h, idx = quantise(img, dither=full)
        if axis is None:
            axis = (w // 2, 0) if full else (0, 0)
        sprites.append((group, image, axis, w, h, idx))

    add(100, 0, title_bg())
    add(100, 1, select_bg())
    add(100, 2, versus_bg())
    add(100, 3, options_bg())
    add(101, 0, trace_tile())

    wm = wordmark()
    add(110, 0, wm, (wm.size[0] // 2, 0))
    bn = select_banner()
    add(111, 0, bn, (bn.size[0] // 2, 0))

    add(150, 0, cell_bg())
    for i in range(RANDOM_FRAMES):
        add(151, i, random_cell(i, RANDOM_FRAMES))

    off = (2, 2)
    for i in range(CURSOR_FRAMES):
        add(160, i, cursor(CYAN, i, CURSOR_FRAMES), off)
    add(161, 0, cursor(CYAN, 0, 1, done=True), off)
    for i in range(CURSOR_FRAMES):
        add(170, i, cursor(P2COL, i, CURSOR_FRAMES), off)
    add(171, 0, cursor(P2COL, 0, 1, done=True), off)

    add(180, 0, caret(CYAN), (0, 8))
    add(181, 0, team_icon(CYAN, True), (0, 7))
    add(182, 0, team_icon(DIM, False), (0, 7))
    add(190, 0, caret(P2COL), (13, 8))
    add(191, 0, team_icon(P2COL, True), (0, 7))
    add(192, 0, team_icon(DIM, False), (0, 7))

    sff = os.path.join(HERE, "system.sff")
    size = write_sff(sff, sprites)
    print("system.sff   %d sprites, %d KiB" % (len(sprites), size // 1024))

    fonts = [
        ("oxyde-s.fnt", COND, 11, 14, "Oxyde small"),
        ("oxyde-m.fnt", COND, 15, 19, "Oxyde body"),
        ("oxyde-l.fnt", BOLD, 19, 24, "Oxyde display"),
        # The clock. fight.def is authored at 1280x720, so a motif font is
        # drawn at its own pixel size on a 720p screen rather than the 1.5x a
        # 640x480 pack got - the count needs its own size to fill the badge.
        ("oxyde-xl.fnt", BOLD, 46, 56, "Oxyde clock"),
    ]
    for name, ttf, px, cell, label in fonts:
        p = os.path.join(HERE, "font", name)
        w, h = build_fnt(p, ttf, px, cell, name=label)
        print("%-13s %dx%d sheet, %d glyphs" % (name, w, h, len(GLYPHS)))

    build_hud()


# ------------------------------------------------------------- the HUD
#
# fight.def's side of the pack: life and power bars, portrait frames, the
# centre clock and the round announcements.
#
# Authored at **1280x720**, not the 640x480 the menus use. The HUD is a
# reconstruction of the pack's own mockup -- MugenOxyde_HUD/preview, which is
# drawn on a 1280x720 canvas -- and giving fight.def that same `localcoord`
# means every box below is the box in the picture, at the same number. The
# engine fits a motif to the window by its own `localcoord`
# (`View::fit(fb, motif.fight_local(), ..)`), so this costs nothing: at 720p
# the HUD is 1:1, at 1080p it is scaled by 1.5, and nothing has to be
# converted by hand between the reference and the file.
#
# `data/oxyde/fight.def` is generated from the same table, at the bottom of
# this file. It used to be written by hand against a second copy of these
# numbers, and the two drifted -- the clock ended up 56 units wide in a
# 56-unit gap, and the "n HITS" popup sat on top of a life bar.

# The layout, in fight.def's own 1280x720 units.
#
# This is the pack mockup's design re-proportioned for play rather than a
# uniform shrink of it. The mockup is a display piece: it is 385 units tall on
# a 720-unit canvas -- over half the screen -- and stacks the portrait *above*
# the bars, so scaling it down to a sane height also drags it into the middle
# 40% of the width and leaves the bars floating in two big empty margins.
#
# What carries the design is not its size but its parts and their order:
# rusted octagon portrait at the outer edge, a nameplate carrying P1 / P2 and
# the OXYDE tag, LIFE stencilled at the outer end of an acid-green trough,
# PWR and the 1 / 2 / 3 marks under the plasma tubes, and the clock in a
# rusted octagon over a MUGEN OXYDE plate in the middle. So the portrait moves
# alongside the bars instead of over them, the troughs run out to the screen
# edge the way the mockup's do, and the band comes in at 132 units -- under a
# fifth of the picture, which is what leaves room to actually fight.
#
# Boxes are (x0, y0, x1, y1), inclusive, for the player-one side. Player two
# is the mirror about x = 640: the *art* is flipped, the lettering is not,
# which is why the two sides are composed by the same function rather than one
# being a flip of the other.
LAYOUT = dict(
    # 2026-10-09, the modern pass. The solid band is gone: every piece floats
    # on its own dark glass over a soft scrim that fades into the stage, the
    # way current fighting games carry their HUD, and the whole thing is
    # 108 units tall instead of 140 -- a fifth of the height back for the
    # fight. The parts and their order are the same: portrait at the outer
    # edge, the player's chip and name above a long sheared life bar, the
    # super gauge and its level under it, the clock in the middle.
    #
    # The sheared boxes (`*_house`) name their *bottom* edge: the top edge is
    # the same length moved inward by SHEAR x height, so the bar leans towards
    # the clock. The fills are worked out from them (`fill_rect`).
    portrait=(12, 6, 88, 82),
    pmark=(98, 6, 132, 26),
    nameplate=(98, 4, 470, 28),
    life_house=(96, 31, 573, 60),
    pwr_house=(96, 68, 372, 84),
    lvplate=(382, 65, 438, 87),
    # The player's initials and their winning streak (`[PlayerTag]`), on the
    # gauge row between the level and the clock.
    tag=(446, 66, 490, 86),
    streak_icon=(496, 67, 510, 85),
    streak_text=(514, 67),
    # The score, when there is one: right-aligned against the clock, under
    # the streak.
    score=(500, 88, 586, 102),
    # Rounds won: centres, starting next to the clock and marching outward,
    # so the first round won always sits in the same place.
    pips=(573, 17, -29),
    badge=(596, 0, 684, 86),
    word=(570, 90, 710, 108),
)

# The bottom of the band, for everything positioned under it.
HUD_BOTTOM = 108

MIRROR_AXIS = 640.0


def hbox(name, mirror=False):
    """One layout box, optionally mirrored about the centre line."""
    x0, y0, x1, y1 = LAYOUT[name]
    if mirror:
        x0, x1 = int(2 * MIRROR_AXIS) - x1, int(2 * MIRROR_AXIS) - x0
    return (x0, y0, x1, y1)


def hbox_named(name, mirror=False):
    return hbox(name, mirror)


def bandsize(name, mirror=False):
    x0, y0, x1, y1 = hbox(name, mirror)
    return (max(1, x1 - x0 + 1), max(1, y1 - y0 + 1))



# --------------------------------------------------------------- HUD art
#
# The bars are the Oxyde HUD art pack rather than shapes drawn here:
# rusted copper housings, an acid-green life fill, a molten-rust damage fill
# and a cyan-to-violet plasma power fill. The pieces live in `hud/` beside
# this script so the motif stays self-contained if the source pack moves.
HUD_ART = os.path.join(HERE, "hud")
_ART = {}


def art(name):
    img = _ART.get(name)
    if img is None:
        img = Image.open(os.path.join(HUD_ART, name + ".png")).convert("RGBA")
        _ART[name] = img
    return img


def trim_caption(img):
    """Drop the sheet caption some layers were cropped with.

    Two of the fills - the molten damage bar and the plasma power bar - were
    cut from the reference sheet with the tail of its printed label still
    attached on the left ("...MID-DAMAGE)"). The label is separated from the
    bar by a clear gutter of fully empty columns, so the bar is whatever comes
    after the last such gutter in the left third of the image. Without this
    the caption is scaled into the bar and shows up as debris on the HUD.
    """
    w, h = img.size
    px = img.load()
    cov = [sum(1 for y in range(h) if px[x, y][3] > 128) for x in range(w)]
    cut, run = 0, 0
    for x in range(w // 3):
        if cov[x] == 0:
            run += 1
        else:
            if run >= 8:
                cut = x
            run = 0
    return img.crop((cut, 0, w, h)) if cut else img


def art_scaled(name, w, h, mirror=False):
    """One HUD layer as its own `w` x `h` image."""
    img = trim_caption(art(name)).resize((max(1, w), max(1, h)), Image.LANCZOS)
    if mirror:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def art_into(dst, name, box, mirror=False, ss=True):
    """Scale one HUD layer into `box`, an inclusive rect in canvas units."""
    x0, y0, x1, y1 = box
    w, h = max(1, x1 - x0 + 1), max(1, y1 - y0 + 1)
    k = SS if ss else 1
    img = trim_caption(art(name)).resize((w * k, h * k), Image.LANCZOS)
    if mirror:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    dst.alpha_composite(img, (x0 * k, y0 * k))


# --------------------------------------------------------------- lettering
#
# The mockup letters the housings: LIFE at the outer end of the life trough,
# PWR under the power tubes, P1 / P2 on a plate over the bar and a small
# boxed OXYDE tag beside it. They are what makes the HUD read as a designed
# object rather than two coloured rectangles, and they are drawn here rather
# than being part of the source art because the source art is one seamless
# housing per element with no room reserved for them.

STENCIL = (214, 219, 226)          # cold steel, the mockup's label colour
STENCIL_DIM = (150, 156, 166)
PIP_RING = (206, 211, 219)
PIP_FACE = (26, 24, 22)


def stencil(d, box, string, px=None, spacing=2, colour=STENCIL):
    """A letterspaced label, centred in `box`, with a soft drop shadow.

    Sized to the box rather than to a point size: every one of these is
    lettering *inside* a piece of metal, and the metal is what has already
    been scaled.
    """
    x0, y0, x1, y1 = box
    if px is None:
        px = max(6, int((y1 - y0 + 1) * 0.62))
    cx, cy = (x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2
    text(d, (s(cx) + SS, s(cy) + SS), string, BOLD, px, (0, 0, 0, 190),
         anchor="mm", spacing=spacing)
    text(d, (s(cx), s(cy)), string, BOLD, px, colour + (255,),
         anchor="mm", spacing=spacing)


# ------------------------------------------------------- the bars, drawn
#
# The housings and the fills used to be scaled crops of the Oxyde HUD art
# art pack: rusted copper tubing, an acid-green life trough and a violet
# plasma power fill. It is a handsome pack and it was the wrong pack. Nothing
# else in this motif has a rusted rivet on it -- the board is black, the runs
# are etched, the only warm colour is one ember accent and the only cool one
# is cyan -- so the HUD read as somebody else's artwork bolted to the top of
# the screen, and photographic copper does not survive being quantised to a
# shared 256-colour table and scaled to a fifth of its authored size.
#
# These are drawn instead, from the same five colours as the rest of the pack:
#
#   the recess   VOID, with etched TRACE ticks every tenth of the bar
#   the housing  a steel bevel, one pixel of PAD, and a hairline accent edge
#   life         CYAN, deep at the bottom, white-hot along the top
#   damage       the ember-to-rust ramp, so what you just lost is burning
#   power        ember, cut into the three cells the 1 / 2 / 3 marks count
#
# Everything is a hard edge on an angle. Nothing is round.

# The shear on the ends of every bar and plate, in pixels of run per pixel of
# rise. One number, so the whole band leans the same way.
SHEAR = 0.42

# -------------------------------------------------------- the super meter
#
# 2026-10-19, the "Charge" pass. The old super gauge was one thin sheared
# trough with an ember plasma fill and a tiny LV chip beside it -- the thing
# the player asked to be rid of. In its place is a row of angular cells that
# light up with a glowing cyan charge as super level climbs, the way a modern
# fighter reads its drive/EX stock at a glance. The engine clips the front
# sprite (group 20/21) by `power / power_max`, so three cells drawn across the
# gauge with transparent gaps fill outer-to-inner, one cell per 1000 power --
# which is one super on a stock-of-three character, the common case. The LV
# chip stays beside them for the exact count.
POWER_CELLS = 3
# The gap between cells, as a fraction of the gauge's length. Same fraction is
# used for the empty housing and the lit fill, so their gaps line up.
POWER_CELL_GAP = 0.055

# The charge colours: hot along the top, saturated cyan through the body, deep
# teal at the foot, with a white-hot rim and a soft glow around each lit cell.
CYAN_HOT  = (198, 248, 255)
CYAN_CORE = CYAN                 # (96, 214, 246)
CYAN_DEEP = (16, 86, 126)

# The raw life NUMBER (the "1000" HP readout). Off by default -- the bar shows
# health -- but kept as one switch here so it is a one-line change to bring it
# back. When on, a counter is written into every [Lifebar] block.
# NOTE: drawing it also needs the engine's lifebar counter support; the stock
# MUGEN [Lifebar] has no counter field, so this is the pack's half of the
# switch, held ready for the day the number is wanted again.
SHOW_LIFE_NUMBER = False


def _cell_spans(n=POWER_CELLS, gap=POWER_CELL_GAP):
    """`n` cells as (start, end) fractions of the gauge length, with `gap`
    between them. One source of truth for the housing, the shade and the
    fill, so every layer's cells and gaps land on the same lines."""
    cw = (1.0 - gap * (n - 1)) / n
    spans, x = [], 0.0
    for _ in range(n):
        spans.append((x, x + cw))
        x += cw + gap
    return spans


def power_cells(x0, y0, w, h, lean=1):
    """The `POWER_CELLS` cell parallelograms over a `w` x `h` gauge whose
    top-left bounding corner is `(x0, y0)`, each leaning on the band's angle.
    Returned in the coordinate frame of `(x0, y0)`."""
    k = h * SHEAR * lean
    out = []
    for a, b in _cell_spans():
        cx0, cx1 = x0 + a * w, x0 + b * w
        out.append([(cx0 + k, y0), (cx1 + k, y0), (cx1, y0 + h), (cx0, y0 + h)])
    return out


def _sheared(d, box, fill, outline=None, width=1, lean=1, flat_left=False,
             flat_right=False):
    """A bar whose ends are cut on the band's angle.

    `lean` is +1 for the player-one side and -1 mirrored, so both sides slope
    away from the middle of the screen rather than both leaning the same way,
    which is what makes the two halves read as one object.
    """
    x0, y0, x1, y1 = box
    k = (y1 - y0) * SHEAR * lean
    if flat_left:
        pts = [(x0, y0), (x1 + (0 if flat_right else k), y0), (x1, y1), (x0, y1)]
    elif flat_right:
        pts = [(x0 + k, y0), (x1, y0), (x1, y1), (x0, y1)]
    else:
        pts = [(x0 + k, y0), (x1 + k, y0), (x1, y1), (x0, y1)]
    d.polygon(pts, fill=fill, outline=outline)
    if outline is not None and width > 1:
        d.line(pts + [pts[0]], fill=outline, width=width, joint="curve")
    return pts


def _vgrad(w, h, stops):
    """A vertical gradient from (position, colour) stops, at 1x."""
    img = Image.new("RGBA", (w, h))
    px = img.load()
    stops = sorted(stops)
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            a, ca = stops[i]
            b, cb = stops[i + 1]
            if t <= b or i == len(stops) - 2:
                u = 0.0 if b <= a else min(1.0, max(0.0, (t - a) / (b - a)))
                c = tuple(round(ca[j] + (cb[j] - ca[j]) * u) for j in range(3))
                break
        for x in range(w):
            px[x, y] = c + (255,)
    return img


def shear_k(box):
    """How far a sheared box's top edge sits inward of its bottom edge."""
    return (box[3] - box[1]) * SHEAR


def house_poly(box, lean=1):
    """The four corners of a sheared housing: `box` names the bottom edge,
    the top edge is the same length moved `shear_k` towards the clock."""
    x0, y0, x1, y1 = box
    k = shear_k(box) * lean
    return [(x0 + k, y0), (x1 + k, y0), (x1, y1), (x0, y1)]


def fill_rect(name, inset=3):
    """The rectangle a fill sprite occupies inside a sheared housing (player
    one's side), and the polygon of the housing's inner face in that
    rectangle's own coordinates -- the fill art is cut to it, so a full bar
    keeps the housing's slanted ends and a draining one is cut straight."""
    x0, y0, x1, y1 = LAYOUT[name]
    h = y1 - y0
    k = shear_k(LAYOUT[name])

    def xl(y):
        return x0 + k * (y1 - y) / h + inset

    def xr(y):
        return x1 + k * (y1 - y) / h - inset

    fy0, fy1 = y0 + inset, y1 - inset
    fx0, fx1 = int(round(xl(fy1))), int(round(xr(fy0)))
    rect = (fx0, fy0, fx1, fy1)
    poly = [(xl(fy0) - fx0, 0), (xr(fy0) - fx0, 0),
            (xr(fy1) - fx0, fy1 - fy0), (xl(fy1) - fx0, fy1 - fy0)]
    return rect, poly


def cut_to(img, poly):
    """Keep only what lies inside `poly` (1x coordinates), anti-aliased."""
    w, h = img.size
    m = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(m).polygon([(px * SS, py * SS) for px, py in poly], fill=255)
    m = m.resize((w, h), Image.LANCZOS)
    out = img.copy()
    out.putalpha(m)
    return out


def trough(d, box, lean, accent):
    """A bar's housing: dark glass, a hairline rim catching the light along the
    top, and the side's colour along the foot."""
    pts = [(s(px), s(py)) for px, py in house_poly(box, lean)]
    # The interior is not drawn here: it is smoked glass, in the shade sprite
    # (`bar_shade`), which the engine draws subtractively under this one.
    d.line(pts + [pts[0]], fill=(66, 78, 96, 255), width=SS)
    # The glass: a light hairline one pixel inside the top edge.
    x0, y0, x1, y1 = box
    k = shear_k(box) * lean
    d.line([(s(x0 + k + 2 * lean), s(y0 + 1)), (s(x1 + k - 2 * lean), s(y0 + 1))],
           fill=(255, 255, 255, 46), width=SS)
    # The foot, in the player's colour: the one mark that says whose bar it is.
    d.line([(s(x0), s(y1)), (s(x1), s(y1))], fill=accent + (235,), width=2 * SS)

def glass(img, top=0.42, lift=26):
    """A glass sheen over the top part of a fill: lighter, fading down."""
    px = img.load()
    w, h = img.size
    edge = max(1, int(h * top))
    for y in range(edge):
        a = int(lift * (1.0 - y / edge))
        for x in range(w):
            r, g, b, al = px[x, y]
            px[x, y] = (min(255, r + a), min(255, g + a), min(255, b + a), al)
    return img


# Life colours, outer(empty) end to inner(full) end: a bright green that warms
# to amber towards the middle of the screen, the way the pack's own mockup
# draws it. The hue runs along the bar's length; a glass sheen runs down it.
LIFE_OUT = (72, 198, 96)         # green, at the outer end
LIFE_MID = (170, 226, 72)        # yellow-green
LIFE_IN  = (250, 206, 72)        # amber, at the full end


def life_fill_art(w, h, damaged=False):
    """The life bar: a bright green-to-amber gradient along its length, with a
    glass highlight along the top. The damage trail behind it burns ember.

    The fill is authored for the player-one side -- local x = 0 is the outer
    (empty) end, x = w the full end nearest the clock -- and mirrored for
    player two, so amber always sits at the full end on both sides."""
    if damaged:
        img = glass(_vgrad(w, h, [(0.0, (255, 236, 214)), (0.20, (255, 176, 96)),
                                  (0.55, EMBER), (1.0, RUST_HI)]))
        px = img.load()
        for x in range(w):
            px[x, h - 1] = (0, 0, 0, 255)
        return img

    def hue(t):
        if t < 0.5:
            u, a, b = t / 0.5, LIFE_OUT, LIFE_MID
        else:
            u, a, b = (t - 0.5) / 0.5, LIFE_MID, LIFE_IN
        return tuple(round(a[i] + (b[i] - a[i]) * u) for i in range(3))

    img = Image.new("RGBA", (w, h))
    px = img.load()
    for x in range(w):
        base = hue(x / max(1, w - 1))
        for y in range(h):
            shade = 1.14 - 0.44 * (y / max(1, h - 1))
            px[x, y] = tuple(min(255, round(base[i] * shade)) for i in range(3)) + (255,)
    img = glass(img, 0.42, 28)
    px = img.load()
    for x in range(w):
        px[x, h - 1] = (0, 0, 0, 255)
    return img

def red_fill_art(w, h):
    """Red life: the ceiling the life bar climbs back to.

    Drawn behind the damage trail, so it is the layer furthest out and has to
    read as *darker* than the ember of a fresh wound rather than brighter. A
    deep oxide red, which is the pack's own rust taken down to something that
    does not compete with the bar in front of it.
    """
    img = _vgrad(w, h, [(0.0, (150, 52, 48)), (0.30, (110, 30, 34)),
                        (0.70, (72, 18, 24)), (1.0, (32, 8, 12))])
    px = img.load()
    for x in range(w):
        for y in range(h):
            if x % 7:
                continue
            r, g, b, _ = px[x, y]
            px[x, y] = (min(255, r + 18), min(255, g + 10), min(255, b + 10), 255)
    return img


def stun_fill_art(w, h):
    """The stun meter: violet running to a hot gold at the top.

    It reads in the opposite direction from life -- it *fills* as a fighter is
    beaten towards a dizzy -- so it is deliberately the one colour on the band
    that is neither of the pack's two accents. Nobody should be able to
    mistake a full stun bar for a full anything else.
    """
    img = _vgrad(w, h, [(0.0, (255, 236, 190)), (0.22, (226, 166, 255)),
                        (0.55, (168, 92, 236)), (1.0, (56, 20, 92))])
    px = img.load()
    # A fine diagonal hatch, so a bar this thin still has texture at 1:1.
    for x in range(w):
        for y in range(h):
            if (x + y) % 6:
                continue
            r, g, b, _ = px[x, y]
            px[x, y] = (min(255, r + 22), min(255, g + 22), min(255, b + 22), 255)
    return img


def guard_fill_art(w, h):
    """The guard meter: steel blue, emptying towards a break."""
    img = _vgrad(w, h, [(0.0, (236, 250, 255)), (0.25, (150, 214, 255)),
                        (0.60, (62, 140, 200)), (1.0, (12, 42, 70))])
    px = img.load()
    for x in range(w):
        for y in range(h):
            if x % 9:
                continue
            r, g, b, _ = px[x, y]
            px[x, y] = (min(255, r + 30), min(255, g + 30), min(255, b + 30), 255)
    return img


def power_fill_art(w, h):
    """The lit super meter: `POWER_CELLS` angular cells glowing cyan, with a
    soft glow behind and a white-hot rim.

    The gaps between cells are left transparent, so when the engine clips this
    sprite by `power / power_max` the cells light outer-to-inner -- one cell
    per 1000 power -- rather than a single bar creeping across. Drawn at `SS`
    and reduced, so the angled edges stay clean at a fifth of authored size."""
    k = SS
    W, Hh = max(1, w) * k, max(1, h) * k
    polys = [[(px * k, py * k) for px, py in poly]
             for poly in power_cells(0, 0, w, h, lean=1)]

    # The cell mask: only the cells are opaque, the gaps stay clear.
    mask = Image.new("L", (W, Hh), 0)
    md = ImageDraw.Draw(mask)
    for poly in polys:
        md.polygon(poly, fill=255)

    # The charge: a cyan vertical gradient, hot at the top, with a glass sheen.
    grad = glass(_vgrad(W, Hh, [(0.0, CYAN_HOT), (0.34, CYAN_CORE),
                                (1.0, CYAN_DEEP)]), 0.5, 44)
    fill = grad.copy()
    fill.putalpha(mask)

    # The glow: the cell silhouettes, blurred, so each lit cell sits in its own
    # pool of light the way a charged stock reads in a modern fighter.
    glow = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for poly in polys:
        gd.polygon(poly, fill=CYAN_CORE + (210,))
    glow = glow.filter(ImageFilter.GaussianBlur(2 * k))

    out = Image.alpha_composite(glow, fill)
    rd = ImageDraw.Draw(out)
    for poly in polys:
        # A white-hot rim, and a brighter top lip for the glassy catch-light.
        rd.line(poly + [poly[0]], fill=CYAN_HOT + (255,), width=max(1, k))
        rd.line([poly[0], poly[1]], fill=(255, 255, 255, 220), width=max(1, k))
    return out.resize((max(1, w), max(1, h)), Image.LANCZOS)


def power_housing(d, box, lean, accent):
    """The empty super meter: `POWER_CELLS` dark-glass cells, each with a steel
    rim and a dim cyan inner edge, so the stock reads even before it is charged.
    Drawn in place of the old single sheared trough."""
    x0, y0, x1, y1 = box
    for poly in power_cells(x0, y0, x1 - x0, y1 - y0, lean):
        pts = [(s(px), s(py)) for px, py in poly]
        # A touch lifted so each cell reads against the near-black gap between
        # them -- the three compartments must be legible at play scale even
        # before any charge, so the meter never looks like one solid trough.
        d.polygon(pts, fill=(16, 22, 31, 255))
        d.line(pts + [pts[0]], fill=(92, 112, 138, 255), width=SS * 2)
        # A bright charge-colour inner edge: the cells read as cyan stocks
        # whether lit or not, so three bars are always visible.
        d.line(pts + [pts[0]], fill=CYAN + (170,), width=SS)

def hex_ring(box, accent, lean=1):
    """The portrait surround and the clock badge: a cut-cornered plate.

    Six sides rather than eight, cut on the band's own angle, in steel over a
    black well -- the same shape the select screen's cells use, so the HUD and
    the menus are the same object seen twice.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0 + 1, y1 - y0 + 1
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    c = min(w, h) * 0.26
    pts = [(0, c), (c, 0), (w - 1 - c, 0), (w - 1, c),
           (w - 1, h - 1 - c), (w - 1 - c, h - 1), (c, h - 1), (0, h - 1 - c)]
    outer = [(s(px), s(py)) for px, py in pts]
    d.polygon(outer, fill=(12, 14, 18, 255))
    d.line(outer + [outer[0]], fill=STEEL_LO + (255,), width=2 * SS)
    # One lit facet along the top-left, which is where every other edge in
    # this pack takes its light from.
    d.line(outer[7:] + outer[:3], fill=STEEL_HI + (215,), width=SS)
    inset = 3
    ipts = [(0 + inset, c + inset), (c + inset, 0 + inset),
            (w - 1 - c - inset, 0 + inset), (w - 1 - inset, c + inset),
            (w - 1 - inset, h - 1 - c - inset),
            (w - 1 - c - inset, h - 1 - inset),
            (c + inset, h - 1 - inset), (0 + inset, h - 1 - c - inset)]
    d.line([(s(px), s(py)) for px, py in ipts] +
           [(s(ipts[0][0]), s(ipts[0][1]))], fill=accent + (170,), width=SS)
    return img


def bar_frame(mirror):
    """Everything static on one side: the scrim, the portrait, the player's
    chip, and the housings the fills land in.

    One sprite per side, because `fight.def` names one `bg0.spr` per side.
    There is no band any more: a soft scrim fading from the top edge into the
    stage keeps the lettering readable over the brightest art in the archive,
    and every piece carries its own dark glass.
    """
    half = int(MIRROR_AXIS)
    x0 = half if mirror else 0
    w, h = half, HUD_BOTTOM + 1
    lean = -1 if mirror else 1
    accent = P2COL if mirror else P1COL
    img = canvas(w, h)

    d = ImageDraw.Draw(img)

    def local(box):
        a, b, c, e = hbox_named(box, mirror)
        return (a - x0, b, c - x0, e)

    def local_house(name):
        bx0, by0, bx1, by1 = LAYOUT[name]
        if mirror:
            bx0, bx1 = int(2 * MIRROR_AXIS) - bx1, int(2 * MIRROR_AXIS) - bx0
        return (bx0 - x0, by0, bx1 - x0, by1)

    trough(d, local_house("life_house"), lean, accent)
    power_housing(d, local_house("pwr_house"), lean, accent)

    # The portrait.
    pb = local("portrait")
    ring = hex_ring(pb, accent, lean)
    img.alpha_composite(ring, (s(pb[0]), s(pb[1])))

    # The player's chip: P1 / P2 knocked out of a solid plate of their colour.
    mb = local("pmark")
    pts = [(s(px), s(py)) for px, py in house_poly(mb, lean)]
    d.polygon(pts, fill=accent + (255,))
    cx, cy = (mb[0] + mb[2] + shear_k(mb) * lean) / 2.0, (mb[1] + mb[3]) / 2.0 + 0.5
    text(d, (s(cx), s(cy)), "P2" if mirror else "P1", BOLD, 15, (8, 10, 14, 255),
         anchor="mm", spacing=1)

    lv_plate(d, local("lvplate"))
    return finish(img, w, h)

def bar_shade(mirror):
    """What the HUD takes off the stage behind it: a scrim fading from the top
    edge, and the smoked glass inside each housing.

    Drawn subtractively (`S` in fight.def's action 201/202): each grey takes
    its own value off every channel of the stage, so the picture behind the
    bars stays visible -- darkened, not covered -- which is what reads as
    glass rather than as a black plate. Zero is left transparent: an opaque
    black pixel would land on the transparency key.
    """
    half = int(MIRROR_AXIS)
    x0 = half if mirror else 0
    w, h = half, HUD_BOTTOM + 1
    lean = -1 if mirror else 1
    val = Image.new("L", (w * SS, h * SS), 0)
    vp = val.load()
    for y in range(h * SS):
        t = 1.0 - y / (h * SS)
        v = int(118 * t * t)
        for x in range(w * SS):
            vp[x, y] = v
    glass = Image.new("L", (w * SS, h * SS), 0)
    gd = ImageDraw.Draw(glass)

    def local_house(name):
        bx0, by0, bx1, by1 = LAYOUT[name]
        if mirror:
            bx0, bx1 = int(2 * MIRROR_AXIS) - bx1, int(2 * MIRROR_AXIS) - bx0
        return (bx0 - x0, by0, bx1 - x0, by1)

    gd.polygon([(s(px), s(py)) for px, py in house_poly(local_house("life_house"), lean)],
               fill=150)
    # The super meter smokes its glass per cell, so the gaps between the cells
    # stay clear of the stage behind rather than sitting on one dark plate.
    hx0, hy0, hx1, hy1 = local_house("pwr_house")
    for poly in power_cells(hx0, hy0, hx1 - hx0, hy1 - hy0, lean):
        gd.polygon([(s(px), s(py)) for px, py in poly], fill=150)
    # Inside a housing the glass value replaces the scrim's.
    val = Image.composite(glass, val, glass.point(lambda v: 255 if v else 0))
    val = val.resize((w, h), Image.LANCZOS)
    img = Image.new("RGBA", (w, h))
    px, vp = img.load(), val.load()
    for y in range(h):
        for x in range(w):
            v = vp[x, y]
            px[x, y] = (v, v, v, 255 if v >= 6 else 0)
    return img


def lv_plate(d, box):
    """The super level beside the gauge: a dark chip, LV, and a well for the
    one number that changes. `fight.def` centres the count in the well."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0 + 1, y1 - y0 + 1
    c = h * 0.30
    pts = [(x0, y0 + c), (x0 + c, y0), (x1 - c, y0), (x1, y0 + c),
           (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c)]
    pts = [(s(px), s(py)) for px, py in pts]
    d.polygon(pts, fill=(9, 11, 15, 255))
    # Rimmed in the super meter's cyan, so the level readout belongs to the
    # cells beside it rather than to the ember clock.
    d.line(pts + [pts[0]], fill=CYAN + (210,), width=max(1, SS))
    split = x0 + int(w * 0.46)
    stencil(d, (x0 + 4, y0 + 4, split - 2, y1 - 4), "LV", px=10, spacing=1,
            colour=(178, 186, 200))
    well = [(s(split), s(y0 + 4)), (s(x1 - 5), s(y0 + 4)),
            (s(x1 - 5), s(y1 - 4)), (s(split), s(y1 - 4))]
    d.polygon(well, fill=(3, 4, 6, 220))

def timer_badge():
    """The clock: a cut-cornered glass plate, an ember rim, and the engine's
    maker's mark -- OXYDE, letterspaced in ember -- along its lower lip, so
    the name is on the screen in every round of every mode."""
    bw, bh = bandsize("badge")
    img = hex_ring((0, 0, bw - 1, bh - 1), EMBER)
    d = ImageDraw.Draw(img)
    # A hairline above the mark, the lip the count sits over.
    lip = bh - 22
    d.line([(s(18), s(lip)), (s(bw - 19), s(lip))], fill=(58, 68, 84, 255), width=SS)
    cx = bw / 2.0
    text(d, (s(cx) + SS, s(lip + 10) + SS), "OXYDE", BOLD, 11, (0, 0, 0, 200),
         anchor="mm", spacing=3)
    text(d, (s(cx), s(lip + 10)), "OXYDE", BOLD, 11, EMBER + (255,),
         anchor="mm", spacing=3)
    return finish(img, bw, bh)

def round_plate():
    """The plate the round counter sits on, under the clock: dark glass cut
    to point at the middle, a hairline rim and an ember foot."""
    ww, wh = bandsize("word")
    img = canvas(ww, wh)
    d = ImageDraw.Draw(img)
    pts = [(s(0), s(0)), (s(ww - 1), s(0)), (s(ww - 9), s(wh - 1)), (s(8), s(wh - 1))]
    d.polygon(pts, fill=(8, 10, 14, 255))
    d.line(pts + [pts[0]], fill=(58, 68, 84, 255), width=SS)
    d.line([(s(12), s(wh - 1) - SS), (s(ww - 13), s(wh - 1) - SS)],
           fill=EMBER + (235,), width=SS)
    return finish(img, ww, wh)


def tag_chip(accent):
    """The player's initials sit on this: a dark chip rimmed in their colour."""
    x0, y0, x1, y1 = LAYOUT["tag"]
    w, h = x1 - x0 + 1, y1 - y0 + 1
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    c = h * 0.30
    pts = [(0, c), (c, 0), (w - 1 - c, 0), (w - 1, c), (w - 1, h - 1 - c),
           (w - 1 - c, h - 1), (c, h - 1), (0, h - 1 - c)]
    pts = [(s(px), s(py)) for px, py in pts]
    d.polygon(pts, fill=(9, 11, 15, 255))
    d.line(pts + [pts[0]], fill=accent + (255,), width=SS)
    return finish(img, w, h)


def streak_icon():
    """A flame, for a winning streak: ember, white-hot at the core."""
    x0, y0, x1, y1 = LAYOUT["streak_icon"]
    w, h = x1 - x0 + 1, y1 - y0 + 1
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    # One flame outline in unit coordinates (x across -1..1, y down 0..1),
    # drawn three times, each smaller about the base: rust, ember, white.
    shape = [(0.0, 0.0), (0.30, 0.34), (0.95, 0.62), (0.78, 0.92), (0.0, 1.0),
             (-0.78, 0.92), (-0.95, 0.62), (-0.42, 0.46), (-0.12, 0.20)]
    for k, colour in ((1.0, (196, 72, 18, 255)), (0.74, EMBER + (255,)),
                      (0.44, (255, 236, 190, 255))):
        pts = []
        for ux, uy in shape:
            px = w / 2.0 + ux * (w / 2.0 - 0.5) * k
            py = (h - 0.5) - (1.0 - uy) * (h - 1.0) * k
            pts.append((s(px), s(py)))
        d.polygon(pts, fill=colour)
    return finish(img, w, h)

def announce(word, colour, px=52, width=560):
    """A round banner: the word, a soft glow behind it and a hard outline.

    Drawn rather than lettered into art so the three of them - ROUND n, FIGHT
    and K.O. - are one family, and so each takes its colour from the theme.
    """
    img = canvas(width, 90)
    glow = canvas(width, 90)
    gd = ImageDraw.Draw(glow)
    text(gd, (s(width // 2), s(45)), word, BOLD, px, colour + (170,), anchor="mm", spacing=3)
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(6 * SS)))
    d = ImageDraw.Draw(img)
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)):
        text(d, (s(width // 2) + dx * SS, s(45) + dy * SS), word, BOLD, px,
             (4, 6, 10, 255), anchor="mm", spacing=3)
    text(d, (s(width // 2), s(45)), word, BOLD, px, colour + (255,), anchor="mm", spacing=3)
    return finish(img, width, 90)


PIP = 26


def win_pip(kind):
    """One slot of the round-win row, by `[WinIcon]` kind.

    A diamond, the band's one round shape turned on its point, sized so it
    reads at a glance at 640x480 as well as 1080p: `empty` is the slot a win
    would fill, rimmed in steel; a won round is ember with a white-hot core,
    and the way it was won changes the core rather than the colour, so the
    row stays one ember family. A perfect is the one that is not ember.
    """
    n = PIP
    img = canvas(n, n)
    d = ImageDraw.Draw(img)
    c = n / 2.0

    def dia(r, **kw):
        pts = [(s(c), s(c - r)), (s(c + r), s(c)), (s(c), s(c + r)), (s(c - r), s(c))]
        d.polygon(pts, **kw)
        return pts

    if kind == "empty":
        dia(c - 1, fill=STEEL_LO + (255,))
        dia(c - 3, fill=(12, 14, 18, 255))
        dia(c - 9, fill=TRACE_LIT + (255,))
        return finish(img, n, n)

    if kind == "perfect":
        dia(c - 1, fill=(255, 255, 255, 255))
        dia(c - 3, fill=(255, 226, 170, 255))
        dia(c - 7, fill=(255, 255, 255, 255))
        return finish(img, n, n)

    rim = (255, 214, 160)
    dia(c - 1, fill=rim + (255,))
    if kind == "c":
        # Chip: worn through the guard, so only half full.
        dia(c - 3, fill=(12, 14, 18, 255))
        d.polygon([(s(3), s(c)), (s(n - 3), s(c)), (s(c), s(n - 3))],
                  fill=EMBER + (255,))
        return finish(img, n, n)
    if kind == "t":
        # Time over: the outline of a win, the round taken on the clock.
        dia(c - 3, fill=(12, 14, 18, 255))
        dia(c - 9, fill=EMBER + (255,))
        return finish(img, n, n)
    dia(c - 3, fill=EMBER + (255,))
    if kind == "h":
        # A hyper: a second ring.
        dia(c - 6, fill=rim + (255,))
        dia(c - 8, fill=EMBER + (255,))
        dia(c - 11, fill=(255, 255, 255, 255))
    elif kind == "s":
        # A special: a cyan core, the pack's other accent.
        dia(c - 8, fill=CYAN + (255,))
    elif kind == "throw":
        # A throw: a dark bar across, like a hand closing.
        d.rectangle([s(7), s(c - 2), s(n - 7), s(c + 2)], fill=(12, 14, 18, 255))
    else:
        dia(c - 9, fill=(255, 238, 210, 255))
    return finish(img, n, n)


def fight_palette():
    """The 256 colours fight.sff is indexed against.

    Everything in the HUD is now drawn from the theme, so the table is built
    from the theme rather than median-cut out of photographs: three long ramps
    for the three gradients that actually have to be smooth -- life, damage
    and power -- and then the flat colours the housings and the lettering use.
    A ramp of 40 across a 27-pixel-tall bar cannot band.
    """
    keep = [(0, 0, 0)]
    # Life: green at the empty end warming to amber at the full end, plus the
    # lit top and the shadowed foot the glass sheen and the vertical shading
    # of the fill produce.
    keep += ramp(LIFE_OUT, LIFE_MID, 8)                    # green -> yellow-green
    keep += ramp(LIFE_MID, LIFE_IN, 8)                     # -> amber
    keep += ramp((150, 236, 168), (255, 238, 150), 12)     # the glassy top
    keep += ramp((48, 138, 64), (176, 150, 50), 8)         # the shadowed foot
    # The super meter charge: hot cyan through saturated cyan to deep teal,
    # the gradient the lit cells and their glow are drawn from.
    keep += ramp(CYAN_HOT, CYAN_DEEP, 22)                  # power
    keep += ramp((255, 236, 214), RUST_LO, 24)             # damage
    keep += ramp(STEEL_HI, (10, 12, 16), 24)               # metal and shadow
    # Neutral greys: the shade sprite is drawn subtractively, and a grey
    # takes the same amount off every channel, so the stage under the HUD
    # darkens without changing colour.
    keep += [(v, v, v) for v in range(8, 216, 8)]
    keep += ramp(CYAN, (8, 30, 44), 18)                    # cyan edges
    # The two optional meters. Short ramps, because the bars are six and
    # eight units tall and nothing that thin can band — but they have to be
    # *here*: quantised against the table above, the violet came out grey.
    # Segment by segment, through the same stops the art uses: a single
    # straight ramp from cream to dark violet passes through desaturated
    # mauve and has nothing near the saturated middle of the gradient, so the
    # bar came out grey.
    keep += ramp((150, 52, 48), (110, 30, 34), 5)          # red life
    keep += ramp((110, 30, 34), (72, 18, 24), 6)
    keep += ramp((72, 18, 24), (32, 8, 12), 6)
    keep += ramp((255, 236, 190), (226, 166, 255), 6)      # stun
    keep += ramp((226, 166, 255), (168, 92, 236), 8)
    keep += ramp((168, 92, 236), (56, 20, 92), 10)
    keep += ramp((236, 250, 255), (150, 214, 255), 6)      # guard
    keep += ramp((150, 214, 255), (62, 140, 200), 8)
    keep += ramp((62, 140, 200), (12, 42, 70), 10)
    keep += [CYAN, EMBER, P1COL, P2COL, INK, DIM, STENCIL, STENCIL_DIM,
             PIP_RING, PIP_FACE, VOID, TRACE, TRACE_LIT, PAD,
             STEEL_HI, STEEL_LO, RUST_HI, RUST_LO,
             (4, 6, 10), (14, 12, 9), (255, 255, 255), (255, 214, 160)]
    keep += ramp(P1COL, (6, 20, 40), 10)
    keep += ramp(P2COL, (40, 8, 8), 10)
    seen, pal = set(), []
    for c in keep:
        c = tuple(c)
        if c in seen:
            continue
        seen.add(c)
        pal.append(c)
    pal += [(0, 0, 0)] * (256 - len(pal))
    return pal[:256]


def derive_layout():
    """The fill rectangles, worked out from the sheared housings they sit in,
    so the art and `fight.def` agree about them to the pixel."""
    LAYOUT["life_fill"], LIFE_POLY[:] = fill_rect("life_house")
    LAYOUT["pwr_fill"], PWR_POLY[:] = fill_rect("pwr_house")
    lf, pf = LAYOUT["life_fill"], LAYOUT["pwr_fill"]
    # Stun and guard are hairlines under the bars they belong with, off
    # unless the session's house rules switch them on.
    LAYOUT["stun_fill"] = (lf[0] + 4, LAYOUT["life_house"][3] + 2, lf[2] - 18,
                           LAYOUT["life_house"][3] + 5)
    LAYOUT["guard_fill"] = (pf[0] + 4, LAYOUT["pwr_house"][3] + 2, pf[2] - 10,
                            LAYOUT["pwr_house"][3] + 4)
    # The count in the clock, centred over the badge's lip.
    b = LAYOUT["badge"]
    LAYOUT["digits"] = (b[0] + 10, b[1] + 8, b[2] - 10, b[3] - 24)


LIFE_POLY = []
PWR_POLY = []


def build_hud():
    derive_layout()
    sprites = []
    pal = fight_palette()

    def add(group, image, img, axis=(0, 0)):
        w, h, idx = quantise(img, palette=pal, matte=(5, 6, 9))
        sprites.append((group, image, axis, w, h, idx))

    add(1, 0, bar_frame(False))
    add(2, 0, bar_frame(True))
    add(3, 0, bar_shade(False))
    add(4, 0, bar_shade(True))

    lf, pf = hbox("life_fill"), hbox("pwr_fill")
    lf2, pf2 = hbox("life_fill", True), hbox("pwr_fill", True)

    def sized(box, fn, *a, **k):
        x0, y0, x1, y1 = box
        return fn(x1 - x0 + 1, y1 - y0 + 1, *a, **k)

    def cut(box, poly, fn, *a, mirror=False):
        img = cut_to(sized(box, fn, *a), poly)
        return ImageOps.mirror(img) if mirror else img

    add(10, 0, cut(lf, LIFE_POLY, life_fill_art))                       # p1 life
    add(11, 0, cut(lf, LIFE_POLY, life_fill_art, True))                 # p1 damage
    add(12, 0, cut(lf2, LIFE_POLY, life_fill_art, mirror=True))         # p2 life
    add(13, 0, cut(lf2, LIFE_POLY, life_fill_art, True, mirror=True))   # p2 damage
    # The super meter is drawn as its own cells, gaps and all, so it is NOT
    # cut to the housing polygon the way the solid bars are: `cut_to` replaces
    # the alpha outright and would fill the gaps back in. The cells carry their
    # own sheared ends, so they land inside the housing without the cut.
    add(20, 0, sized(pf, power_fill_art))                               # p1 power
    add(21, 0, ImageOps.mirror(sized(pf2, power_fill_art)))             # p2 power

    sf, gf = hbox("stun_fill"), hbox("guard_fill")
    sf2, gf2 = hbox("stun_fill", True), hbox("guard_fill", True)
    add(14, 0, cut(lf, LIFE_POLY, red_fill_art))                     # p1 red life
    add(15, 0, cut(lf2, LIFE_POLY, red_fill_art, mirror=True))       # p2 red life
    add(22, 0, sized(sf, stun_fill_art))                    # p1 stun
    add(23, 0, sized(sf2, stun_fill_art))                   # p2 stun
    add(24, 0, sized(gf, guard_fill_art))                   # p1 guard
    add(25, 0, sized(gf2, guard_fill_art))                  # p2 guard

    badge = timer_badge()
    add(30, 0, badge, (badge.size[0] // 2, 0))

    def centred(group, image, img):
        add(group, image, img, (img.size[0] // 2, img.size[1] // 2))

    for n in range(1, 10):
        centred(40, n, announce("ROUND %d" % n, CYAN))
    centred(41, 0, announce("FIGHT!", EMBER))
    centred(42, 0, announce("K.O.", P2COL, px=64, width=420))

    centred(43, 0, announce("DOUBLE K.O.", P2COL, px=44))
    centred(44, 0, announce("TIME OVER", EMBER, px=44))
    centred(45, 0, announce("DRAW", INK, px=52, width=420))

    # The round-win row: 50 an ordinary win, then one per kind MUGEN tells
    # apart, and 59 the empty slot (`[WinIcon] p1.empty`, an Oxyde key).
    for image, kind in enumerate(["n", "s", "h", "throw", "c", "t", "perfect"]):
        centred(50 + image, 0, win_pip(kind))
    centred(59, 0, win_pip("empty"))
    plate = round_plate()
    add(31, 0, plate, (plate.size[0] // 2, 0))
    # `[PlayerTag]`: the initials' chip per side, and the streak's flame.
    add(32, 0, tag_chip(P1COL))
    add(33, 0, tag_chip(P2COL))
    add(34, 0, streak_icon())

    p = os.path.join(HERE, "fight.sff")
    size = write_sff(p, sprites, pal)
    print("fight.sff    %d sprites, %d KiB" % (len(sprites), size // 1024))
    write_fight_def()


# ---------------------------------------------------------------- fight.def
#
# Generated, because every number in it is one of the boxes above. Written
# by hand against a second copy of the geometry, the two drifted apart.

FIGHT_DEF = """\
;------------------------------------------------------------------------------
;  M U G E N   O X Y D E   --   fight.def
;
;  GENERATED by data/oxyde/build_screenpack.py -- edit the geometry there.
;
;  The in-match HUD, authored at 1280x720: the same canvas the pack's own
;  mockup (MugenOxyde_HUD/preview/01_hud_1280x720.jpg) is drawn on, so the
;  layout below is that picture's own geometry rather than a conversion of
;  it. The engine fits the motif to the window by this `localcoord`, so the
;  HUD is 1:1 at 720p and scaled at anything larger.
;
;  Paths are written relative to data/, so they resolve whether the engine
;  looks beside this file, from the game root, or under data/.
;------------------------------------------------------------------------------

[Info]
name       = "Oxyde"
author     = "the Oxyde project"
localcoord = 1280, 720

[Files]
sff         = oxyde/fight.sff
snd         = fight.snd
; The pack's own effects rather than Elecbyte's 2000-vintage set. Written
; relative to data/ like every other path here, so it resolves whether the
; engine looks beside this file, from the game root, or under data/.
; Put `fightfx.sff`/`fightfx.air` back to use the ones the install shipped.
fightfx.sff = oxyde/fightfx.sff
fightfx.air = oxyde/fightfx.air
common.snd  = common.snd
font1       = oxyde/font/oxyde-s.fnt
font2       = oxyde/font/oxyde-m.fnt
font3       = oxyde/font/oxyde-l.fnt
font4       = oxyde/font/oxyde-xl.fnt

;--------------------------------------------------------------- life bars
;
; `range.x` is (full, empty): P1's bar empties towards its own outer edge,
; P2's towards the other one, so damage always travels away from the middle.

[Lifebar]
p1.pos          = 0, 0
p1.bg0.anim     = 201
p1.bg0.offset   = 0, 0
p1.bg0.layerno  = 0
p1.bg1.spr      = 1, 0
p1.bg1.offset   = 0, 0
p1.bg1.layerno  = 0
p1.mid.spr      = 11, 0
p1.mid.offset   = {lf_x0}, {lf_y0}
p1.mid.layerno  = 0
p1.red.spr      = 14, 0
p1.red.offset   = {lf_x0}, {lf_y0}
p1.red.layerno  = 0
p1.front.spr    = 10, 0
p1.front.offset = {lf_x0}, {lf_y0}
p1.front.layerno = 0
p1.range.x      = {lf_x1}, {lf_x0}

p2.pos          = 0, 0
p2.bg0.anim     = 202
p2.bg0.offset   = {half}, 0
p2.bg0.layerno  = 0
p2.bg1.spr      = 2, 0
p2.bg1.offset   = {half}, 0
p2.bg1.layerno  = 0
p2.mid.spr      = 13, 0
p2.mid.offset   = {lf2_x0}, {lf_y0}
p2.mid.layerno  = 0
p2.red.spr      = 15, 0
p2.red.offset   = {lf2_x0}, {lf_y0}
p2.red.layerno  = 0
p2.front.spr    = 12, 0
p2.front.offset = {lf2_x0}, {lf_y0}
p2.front.layerno = 0
p2.range.x      = {lf2_x0}, {lf2_x1}

[Simul Lifebar]
p1.pos          = 0, 0
p1.bg0.anim     = 201
p1.bg0.offset   = 0, 0
p1.bg1.spr      = 1, 0
p1.bg1.offset   = 0, 0
p1.mid.spr      = 11, 0
p1.mid.offset   = {lf_x0}, {lf_y0}
p1.red.spr      = 14, 0
p1.red.offset   = {lf_x0}, {lf_y0}
p1.red.layerno  = 0
p1.front.spr    = 10, 0
p1.front.offset = {lf_x0}, {lf_y0}
p1.range.x      = {lf_x1}, {lf_x0}

p2.pos          = 0, 0
p2.bg0.anim     = 202
p2.bg0.offset   = {half}, 0
p2.bg1.spr      = 2, 0
p2.bg1.offset   = {half}, 0
p2.mid.spr      = 13, 0
p2.mid.offset   = {lf2_x0}, {lf_y0}
p2.red.spr      = 15, 0
p2.red.offset   = {lf2_x0}, {lf_y0}
p2.red.layerno  = 0
p2.front.spr    = 12, 0
p2.front.offset = {lf2_x0}, {lf_y0}
p2.range.x      = {lf2_x0}, {lf2_x1}

; The two fighters a side share one trough: the housing is drawn once, by
; p1 and p2, and each pair of bars is squeezed to half its height and stacked
; inside it. Repeating the *housing* at an offset -- which is what this did --
; drops a second copy of the whole band on top of the power row, and the
; second row of a Team Co-op HUD landed over PWR with the LV plate showing
; through it.
p1.mid.scale    = 1, {half_h}
p1.front.scale  = 1, {half_h}
p2.mid.scale    = 1, {half_h}
p2.front.scale  = 1, {half_h}

p3.pos          = 0, {row2}
p3.mid.spr      = 11, 0
p3.mid.offset   = {lf_x0}, {lf_y0}
p3.mid.scale    = 1, {half_h}
p3.front.spr    = 10, 0
p3.front.offset = {lf_x0}, {lf_y0}
p3.front.scale  = 1, {half_h}
p3.range.x      = {lf_x1}, {lf_x0}

p4.pos          = 0, {row2}
p4.mid.spr      = 13, 0
p4.mid.offset   = {lf2_x0}, {lf_y0}
p4.mid.scale    = 1, {half_h}
p4.front.spr    = 12, 0
p4.front.offset = {lf2_x0}, {lf_y0}
p4.front.scale  = 1, {half_h}
p4.range.x      = {lf2_x0}, {lf2_x1}

[Turns Lifebar]
p1.pos          = 0, 0
p1.bg0.anim     = 201
p1.bg0.offset   = 0, 0
p1.bg1.spr      = 1, 0
p1.bg1.offset   = 0, 0
p1.mid.spr      = 11, 0
p1.mid.offset   = {lf_x0}, {lf_y0}
p1.red.spr      = 14, 0
p1.red.offset   = {lf_x0}, {lf_y0}
p1.red.layerno  = 0
p1.front.spr    = 10, 0
p1.front.offset = {lf_x0}, {lf_y0}
p1.range.x      = {lf_x1}, {lf_x0}

p2.pos          = 0, 0
p2.bg0.anim     = 202
p2.bg0.offset   = {half}, 0
p2.bg1.spr      = 2, 0
p2.bg1.offset   = {half}, 0
p2.mid.spr      = 13, 0
p2.mid.offset   = {lf2_x0}, {lf_y0}
p2.red.spr      = 15, 0
p2.red.offset   = {lf2_x0}, {lf_y0}
p2.red.layerno  = 0
p2.front.spr    = 12, 0
p2.front.offset = {lf2_x0}, {lf_y0}
p2.range.x      = {lf2_x0}, {lf2_x1}

;-------------------------------------------------------------- power bars

[Powerbar]
p1.pos            = 0, 0
p1.front.spr      = 20, 0
p1.front.offset   = {pf_x0}, {pf_y0}
p1.front.layerno  = 0
p1.range.x        = {pf_x1}, {pf_x0}
p1.counter.offset = {p1cnt_x}, {cnt_y}
p1.counter.font   = 2, 7, 0
p1.counter.layerno = 1

p2.pos            = 0, 0
p2.front.spr      = 21, 0
p2.front.offset   = {pf2_x0}, {pf_y0}
p2.front.layerno  = 0
p2.range.x        = {pf2_x0}, {pf2_x1}
p2.counter.offset = {p2cnt_x}, {cnt_y}
p2.counter.font   = 2, 7, 0
p2.counter.layerno = 1

level1.snd = 1, 0
level2.snd = 1, 0
level3.snd = 1, 0
level4.snd = 1, 0
level5.snd = 1, 0
level6.snd = 1, 0
level7.snd = 1, 0
level8.snd = 1, 0
level9.snd = 1, 0

;------------------------------------------------------------- extra meters
;
; Stun, guard and score: three readings MUGEN has no lifebar sections for,
; and which this engine draws only when the session's house rules ask for
; them. A `fight.def` without these three sections shows none of them, which
; is every `fight.def` written before they existed.
;
; The two bars sit in the strip under the life and power fills, inside the
; housings those already have, so switching them on does not move anything
; else on the band. The stun bar fills towards a dizzy; the guard bar empties
; towards a break.

[Stunbar]
p1.pos           = 0, 0
p1.front.spr     = 22, 0
p1.front.offset  = {sf_x0}, {sf_y0}
p1.front.layerno = 1
p1.range.x       = {sf_x1}, {sf_x0}

p2.pos           = 0, 0
p2.front.spr     = 23, 0
p2.front.offset  = {sf2_x0}, {sf_y0}
p2.front.layerno = 1
p2.range.x       = {sf2_x0}, {sf2_x1}

[Guardbar]
p1.pos           = 0, 0
p1.front.spr     = 24, 0
p1.front.offset  = {gf_x0}, {gf_y0}
p1.front.layerno = 1
p1.range.x       = {gf_x1}, {gf_x0}

p2.pos           = 0, 0
p2.front.spr     = 25, 0
p2.front.offset  = {gf2_x0}, {gf_y0}
p2.front.layerno = 1
p2.range.x       = {gf2_x0}, {gf2_x1}

[Score]
p1.pos             = 0, 0
p1.counter.offset  = {score_x}, {score_y}
p1.counter.font    = 2, 7, -1
p1.counter.layerno = 1

p2.pos             = 0, 0
p2.counter.offset  = {score2_x}, {score_y}
p2.counter.font    = 2, 7, 1
p2.counter.layerno = 1

;---------------------------------------------------------------- portraits
;
; The face goes *in front of* the housing and is scaled to the opening, so
; the rust ring frames it rather than being covered by it.

[Face]
p1.pos           = 0, 0
p1.face.spr      = 9000, 0
p1.face.offset   = {face_x0}, {face_y0}
p1.face.scale    = {face_scale}, {face_scale}
p1.face.layerno  = 1
p2.pos           = 0, 0
p2.face.spr      = 9000, 0
p2.face.offset   = {face2_x1}, {face_y0}
p2.face.scale    = {face_scale}, {face_scale}
p2.face.facing   = -1
p2.face.layerno  = 1

[Simul Face]
p1.pos          = 0, 0
p1.face.spr     = 9000, 0
p1.face.offset  = {face_x0}, {face_y0}
p1.face.scale   = {face_scale}, {face_scale}
p2.pos          = 0, 0
p2.face.spr     = 9000, 0
p2.face.offset  = {face2_x1}, {face_y0}
p2.face.scale   = {face_scale}, {face_scale}
p2.face.facing  = -1
p3.pos          = 0, {face_row2}
p3.face.spr     = 9000, 0
p3.face.offset  = {face_x0}, {face_y0}
p3.face.scale   = {face_half}, {face_half}
p4.pos          = 0, {face_row2}
p4.face.spr     = 9000, 0
p4.face.offset  = {face2_x1}, {face_y0}
p4.face.scale   = {face_half}, {face_half}
p4.face.facing  = -1

[Turns Face]
p1.pos          = 0, 0
p1.face.spr     = 9000, 0
p1.face.offset  = {face_x0}, {face_y0}
p1.face.scale   = {face_scale}, {face_scale}
p2.pos          = 0, 0
p2.face.spr     = 9000, 0
p2.face.offset  = {face2_x1}, {face_y0}
p2.face.scale   = {face_scale}, {face_scale}
p2.face.facing  = -1

;-------------------------------------------------------------------- names
;
; On the nameplate, beside the P1 / P2 mark, in the display face: the plate
; has the room since it stopped carrying an OXYDE tag. Two a side share the
; plate on two lines, the partner smaller, both inside its edges.

[Name]
p1.pos           = 0, 0
p1.name.offset   = {name_x}, {name_y_big}
p1.name.font     = 3, 7, 1
p1.name.layerno  = 1
p2.pos           = 0, 0
p2.name.offset   = {name2_x}, {name_y_big}
p2.name.font     = 3, 7, -1
p2.name.layerno  = 1

[Simul Name]
p1.pos          = 0, 0
p1.name.offset  = {name_x}, {name_y_simul}
p1.name.font    = 2, 7, 1
p2.pos          = 0, 0
p2.name.offset  = {name2_x}, {name_y_simul}
p2.name.font    = 2, 7, -1
p3.pos          = 0, {name_row2}
p3.name.offset  = {name_x}, {name_y_simul}
p3.name.font    = 1, 0, 1
p4.pos          = 0, {name_row2}
p4.name.offset  = {name2_x}, {name_y_simul}
p4.name.font    = 1, 0, -1

[Turns Name]
p1.pos          = 0, 0
p1.name.offset  = {name_x}, {name_y_big}
p1.name.font    = 3, 7, 1
p2.pos          = 0, 0
p2.name.offset  = {name2_x}, {name_y_big}
p2.name.font    = 3, 7, -1

;--------------------------------------------------------- timer and combo

[Time]
pos             = 640, 0
bg0.spr         = 30, 0
bg0.offset      = 0, {badge_y0}
bg0.layerno     = 0
counter.offset  = 0, {digit_y}
counter.font    = 4, 7, 0
framespercount  = 60

[Combo]
; Under the bars on the player's own side, well clear of the clock.
; `style = panel` is Oxyde's: the engine draws its combo panel here (count,
; damage, share of life, counter/juggle tags, the round's best) and MUGEN,
; which ignores the key, draws the counter and text below.
style           = panel
pos             = {combo_x}, {combo_y}
start.x         = {combo_start}
counter.font    = 4, 2, 1
counter.offset  = 0, 0
text.font       = 3, 2, 1
text.offset     = {combo_text_x}, {combo_text_y}
text.text       = "HITS"
displaytime     = 90
counter.shake   = 1

;------------------------------------------------------------------- round

[Round]
match.wins         = 2
match.maxdrawgames = 1
pos                = 640, {round_y}
start.waittime     = 30
ctrl.time          = 30

; No sprites for the announcements on purpose. ROUND, FIGHT, K.O. and the
; rest are drawn by the engine instead, from the font, at whatever size the
; window is: a 420-pixel bitmap scaled onto a 4K panel is soft exactly where
; the eye is, and these are the only words in the game that have to read from
; across a room. Sprites 40-45 are still in fight.sff for anyone who wants
; them back - put the .spr lines below back and they are used again.
round.default.anim = -1
round.time         = 0
round.sndtime      = 0

fight.time = 0
fight.snd  = 2, 0

KO.time         = 0
KO.snd          = 3, 0
DKO.time        = 0
TO.time         = 0
draw.displaytime = 90

win.text  = "%s WINS"
win.font  = 3, 2, 0
win.offset = 0, {win_y}
win2.text = "%s AND %s WIN"
win2.font = 3, 2, 0
win2.offset = 0, {win_y}
; Oxyde's: the engine's own banner says the win instead -- the winner's name
; large over the fighters' heads, WINS in gold under it. MUGEN ignores the
; key and draws win.text above.
win.style  = banner

slow.time      = 60
over.waittime  = 45
over.hittime   = 10
over.wintime   = 45
over.time      = 210
win.time       = 60

;---------------------------------------------------------------- win icons
;
; The round-win row: one slot per round it takes to win, between the
; nameplate and the clock, filling towards the clock. `p1.empty` is an Oxyde
; key -- the slot drawn under every win, so the row reads "one of two" before
; anyone has won anything; MUGEN ignores it. Each kind of win changes the
; mark's core: a cyan one for a special, a double ring for a hyper, a bar for
; a throw, half full for chip, an outline for a time over, white for a
; perfect.

[WinIcon]
p1.pos          = {icon_x}, {icon_y}
p1.iconoffset   = {icon_step}, 0
p1.empty.spr    = 59, 0
p1.n.spr        = 50, 0
p1.s.spr        = 51, 0
p1.h.spr        = 52, 0
p1.throw.spr    = 53, 0
p1.c.spr        = 54, 0
p1.t.spr        = 55, 0
p1.perfect.spr  = 56, 0
p1.suicide.spr  = 50, 0
p1.teammate.spr = 50, 0
p1.counter.font = 2, 2, 1
p1.counter.offset = -10, -9

p2.pos          = {icon2_x}, {icon_y}
p2.iconoffset   = {icon2_step}, 0
p2.empty.spr    = 59, 0
p2.n.spr        = 50, 0
p2.s.spr        = 51, 0
p2.h.spr        = 52, 0
p2.throw.spr    = 53, 0
p2.c.spr        = 54, 0
p2.t.spr        = 55, 0
p2.perfect.spr  = 56, 0
p2.suicide.spr  = 50, 0
p2.teammate.spr = 50, 0
p2.counter.font = 2, 2, -1
p2.counter.offset = 10, -9

useiconupto = 4

;------------------------------------------------------------- round counter
;
; Which round this is, on the plate under the clock for the whole round, and
; MATCH POINT when either side is one round from the match. An Oxyde section:
; MUGEN says the round once, before the fight, and never again. Practice, the
; bonus games and the one-long-round modes have no rounds and show no plate.

[RoundCounter]
pos            = 640, {plate_y}
bg0.spr        = 31, 0
bg0.offset     = 0, 0
counter.font   = 2, 7, 0
counter.offset = 0, 1
counter.text   = "ROUND %i"
final.text     = "MATCH POINT"

;---------------------------------------------------------------- player tag
;
; Who is playing and the streak they are on, on the gauge row between the
; level and the clock: the initials on a chip in the player's colour, then a
; flame and the streak once it is two or more. An Oxyde section; a pack
; without it shows neither.

[PlayerTag]
streak.min        = 2
p1.pos            = 0, 0
p1.tag.bg0.spr    = 32, 0
p1.tag.bg0.offset = {tag_x0}, {tag_y0}
p1.tag.font       = 2, 7, 0
p1.tag.offset     = {tag_cx}, {tag_ty}
p1.tag.text       = "%s"
p1.streak.bg0.spr    = 34, 0
p1.streak.bg0.offset = {fl_x0}, {fl_y0}
p1.streak.font    = 2, 2, 1
p1.streak.offset  = {st_x}, {st_y}
p1.streak.text    = "%i STREAK"

p2.pos            = 0, 0
p2.tag.bg0.spr    = 33, 0
p2.tag.bg0.offset = {tag2_x0}, {tag_y0}
p2.tag.font       = 2, 7, 0
p2.tag.offset     = {tag2_cx}, {tag_ty}
p2.tag.text       = "%s"
p2.streak.bg0.spr    = 34, 0
p2.streak.bg0.offset = {fl2_x0}, {fl_y0}
p2.streak.font    = 2, 2, -1
p2.streak.offset  = {st2_x}, {st_y}
p2.streak.text    = "%i STREAK"

;------------------------------------------------------------------- actions
;
; The shade under each side's HUD: a scrim and the smoked glass inside the
; bars, drawn subtractively (`S`), so the stage stays visible behind them.

[Begin Action 201]
3,0, 0,0, -1, , S

[Begin Action 202]
4,0, 0,0, -1, , S
"""


def simul_np_sections(n, vals):
    """`[Simul_<n>P Lifebar]`, `Face` and `Name` for n fighters a side.

    The n bars share the one trough, stacked and squeezed to fit it the way
    the two-a-side bars are, so the band does not grow: a side's whole team
    is one glance. The portrait and the name are the point fighter's, with
    the partner's name under it as in two a side; past that there is no room
    for a third line of lettering that could be read.
    """
    lf, lf2 = hbox("life_fill"), hbox("life_fill", True)
    trough_h = lf[3] - lf[1] + 1
    gap = 1
    bar_h = (trough_h - (n - 1) * gap) / n
    scale = round(bar_h / trough_h, 3)
    step = bar_h + gap
    out = ["\n[Simul_%dP Lifebar]\n" % n]
    for i in range(n):
        for side in (0, 1):
            k = 2 * i + side + 1
            mirror = side == 1
            x0 = (lf2 if mirror else lf)[0]
            front, mid, red = (12, 13, 15) if mirror else (10, 11, 14)
            rng = (lf2[0], lf2[2]) if mirror else (lf[2], lf[0])
            out.append("p%d.pos          = 0, %s\n" % (k, ("%.2f" % (i * step)).rstrip("0").rstrip(".")))
            if i == 0:
                out.append("p%d.bg0.anim     = %d\n" % (k, 202 if mirror else 201))
                out.append("p%d.bg0.offset   = %d, 0\n" % (k, int(MIRROR_AXIS) if mirror else 0))
                out.append("p%d.bg1.spr      = %d, 0\n" % (k, 2 if mirror else 1))
                out.append("p%d.bg1.offset   = %d, 0\n" % (k, int(MIRROR_AXIS) if mirror else 0))
            for part, spr in (("mid", mid), ("red", red), ("front", front)):
                out.append("p%d.%s.spr%s= %d, 0\n" % (k, part, " " * (9 - len(part)), spr))
                out.append("p%d.%s.offset%s= %d, %d\n" % (k, part, " " * (6 - len(part)), x0, lf[1]))
                out.append("p%d.%s.scale%s= 1, %s\n" % (k, part, " " * (7 - len(part)), scale))
            out.append("p%d.range.x      = %d, %d\n" % (k, rng[0], rng[1]))
        out.append("\n")
    out.append("[Simul_%dP Face]\n" % n)
    out.append("p1.pos          = 0, 0\np1.face.spr     = 9000, 0\n")
    out.append("p1.face.offset  = %d, %d\np1.face.scale   = %s, %s\n"
               % (vals["face_x0"], vals["face_y0"], vals["face_scale"], vals["face_scale"]))
    out.append("p2.pos          = 0, 0\np2.face.spr     = 9000, 0\n")
    out.append("p2.face.offset  = %d, %d\np2.face.scale   = %s, %s\np2.face.facing  = -1\n\n"
               % (vals["face2_x1"], vals["face_y0"], vals["face_scale"], vals["face_scale"]))
    out.append("[Simul_%dP Name]\n" % n)
    out.append("p1.pos          = 0, 0\np1.name.offset  = %d, %d\np1.name.font    = 2, 7, 1\n"
               % (vals["name_x"], vals["name_y_simul"]))
    out.append("p2.pos          = 0, 0\np2.name.offset  = %d, %d\np2.name.font    = 2, 7, -1\n"
               % (vals["name2_x"], vals["name_y_simul"]))
    out.append("p3.pos          = 0, %d\np3.name.offset  = %d, %d\np3.name.font    = 1, 0, 1\n"
               % (vals["name_row2"], vals["name_x"], vals["name_y_simul"]))
    out.append("p4.pos          = 0, %d\np4.name.offset  = %d, %d\np4.name.font    = 1, 0, -1\n\n"
               % (vals["name_row2"], vals["name2_x"], vals["name_y_simul"]))
    return "".join(out)


def write_fight_def():
    derive_layout()
    lf, lf2 = hbox("life_fill"), hbox("life_fill", True)
    pf, pf2 = hbox("pwr_fill"), hbox("pwr_fill", True)
    sf, sf2 = hbox("stun_fill"), hbox("stun_fill", True)
    gf, gf2 = hbox("guard_fill"), hbox("guard_fill", True)
    sc, sc2 = hbox("score"), hbox("score", True)
    face, face2 = hbox("portrait"), hbox("portrait", True)
    plate, plate2 = hbox("nameplate"), hbox("nameplate", True)
    house, house2 = hbox("pwr_house"), hbox("pwr_house", True)
    badge, digits = hbox("badge"), hbox("digits")

    # The face is drawn into the octagon's opening. `face_fit` normalises any
    # portrait to a nominal 25 units first, whatever size its author drew it,
    # so the scale is simply "how many of those the opening is wide".
    opening = (face[2] - face[0] + 1) * 0.70
    face_scale = round(opening / 25.0, 3)
    inset = int(((face[2] - face[0] + 1) - opening) / 2.0)

    vals = dict(
        half=int(MIRROR_AXIS),
        # Two fighters a side share the band rather than being given a second
        # copy of it: the bars stack inside one trough, the names take a
        # second line on the one plate, and the portraits halve and sit one
        # above the other in the one octagon.
        row2=12,
        half_h=".47",
        # The partner's name goes under the gauge row: the name row above the
        # bar has room for one line of lettering, not two.
        name_row2=82,
        face_row2=36,
        lf_x0=lf[0], lf_y0=lf[1], lf_x1=lf[2],
        lf2_x0=lf2[0], lf2_x1=lf2[2],
        pf_x0=pf[0], pf_y0=pf[1], pf_x1=pf[2],
        pf2_x0=pf2[0], pf2_x1=pf2[2],
        sf_x0=sf[0], sf_y0=sf[1], sf_x1=sf[2],
        sf2_x0=sf2[0], sf2_x1=sf2[2],
        gf_x0=gf[0], gf_y0=gf[1], gf_x1=gf[2],
        gf2_x0=gf2[0], gf2_x1=gf2[2],
        # The score sits right-aligned against the clock badge on each side,
        # so the two figures read inward towards the middle the way the life
        # numbers do.
        score_x=sc[2], score2_x=sc2[0], score_y=sc[1],
        # The level digit sits in the well of its own side's LV plate. The
        # offset is measured from the plate's *left* edge on both sides, not
        # mirrored with the art: "LV" then the number is the reading order
        # whichever end of the screen the plate is at.
        p1cnt_x=hbox("lvplate")[0] + int((hbox("lvplate")[2] - hbox("lvplate")[0]) * 0.76),
        p2cnt_x=hbox("lvplate", True)[0] + int((hbox("lvplate")[2] - hbox("lvplate")[0]) * 0.76),
        cnt_y=hbox("lvplate")[1] + 1,
        face_x0=face[0] + inset,
        face2_x1=face2[2] - inset,
        face_y0=face[1] + inset,
        face_scale=face_scale,
        face_half=round(face_scale * 0.6, 3),
        # The character's name goes on the plate, between the P1 mark and the
        # OXYDE tag, which is the space the mockup leaves empty.
        name_x=hbox("pmark")[2] + 10,
        name2_x=hbox("pmark", True)[0] - 10,
        name_y=plate[1] + 9,
        name_y_big=plate[1],
        name_y_simul=plate[1] + 2,
        badge_y0=badge[1],
        # The count is centred in the badge's recess, and a motif counter is
        # drawn from its top edge, so it starts half a line height above.
        digit_y=digits[1] + (digits[3] - digits[1]) // 2 - 26,
        # The popup goes under the band on the attacker's own side.
        combo_x=36,
        combo_y=HUD_BOTTOM + 40,
        combo_start=-120,
        combo_text_x=4,
        combo_text_y=34,
        round_y=300,
        win_y=60,
        # The round-win row, centres, between the nameplate and the clock.
        icon_x=LAYOUT["pips"][0],
        icon2_x=int(2 * MIRROR_AXIS) - LAYOUT["pips"][0],
        icon_y=LAYOUT["pips"][1],
        icon_step=LAYOUT["pips"][2],
        icon2_step=-LAYOUT["pips"][2],
        plate_y=hbox("word")[1],
        tag_x0=hbox("tag")[0], tag2_x0=hbox("tag", True)[0], tag_y0=hbox("tag")[1],
        tag_cx=(hbox("tag")[0] + hbox("tag")[2]) // 2 + 1,
        tag2_cx=(hbox("tag", True)[0] + hbox("tag", True)[2]) // 2 + 1,
        tag_ty=hbox("tag")[1] + 1,
        fl_x0=hbox("streak_icon")[0], fl2_x0=hbox("streak_icon", True)[0],
        fl_y0=hbox("streak_icon")[1],
        st_x=LAYOUT["streak_text"][0],
        st2_x=int(2 * MIRROR_AXIS) - LAYOUT["streak_text"][0],
        st_y=LAYOUT["streak_text"][1],
    )
    text = FIGHT_DEF.format(**vals)
    # Three and four a side, written from the same geometry. Without them a
    # four-a-side match borrowed `[Simul Lifebar]`, which has room for two a
    # side, and half the fighters on the stage had no bar at all.
    marker = ";-------------------------------------------------------------- power bars"
    text = text.replace(marker, simul_np_sections(3, vals) + simul_np_sections(4, vals) + marker, 1)
    # The raw life NUMBER, off by default (SHOW_LIFE_NUMBER). When switched on,
    # a counter is written into [Lifebar] on each side, right-aligned into the
    # gap between the bar's inner end and the clock. (Shipping off: the bar is
    # the readout, and the engine's stock [Lifebar] has no counter field to
    # draw this through yet -- this is the pack half of the switch.)
    if SHOW_LIFE_NUMBER:
        counter = (
            "p1.counter.offset = %d, %d\n"
            "p1.counter.font   = 2, 7, 1\n"
            "p1.counter.layerno = 1\n"
            "\np2.pos" % (lf[2] + 8, lf[1] - 2)
        )
        text = text.replace("\np2.pos", counter, 1)
    p = os.path.join(HERE, "fight.def")
    with open(p, "w") as f:
        f.write(text)
    print("fight.def    written (localcoord 1280x720, band %d units)" % HUD_BOTTOM)


if __name__ == "__main__":
    build()
