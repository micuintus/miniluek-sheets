"""Procedural picture-sheet scenes (MIT): one illustrated panel holding the 12 numbered tasks.

Drawn at 2x supersampling and downscaled. Characters and props are Noto emoji from
assets/emoji; sky, water, ground, containers, tokens and badges are drawn here.
Coordinates are cm inside the panel, origin top left, y down.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import art

ASSETS = Path(__file__).resolve().parent.parent / "assets"
FONT_BOLD = str(ASSETS / "fonts" / "Andika-Bold.ttf")
SS = 2

_emoji = {}
_fonts = {}


def emoji(name):
    if name not in _emoji:
        path = ASSETS / "emoji" / f"{name}.png"
        if not path.exists():
            raise SystemExit(f"unknown picture '{name}'; see: miniluek.py kinds")
        im = Image.open(path).convert("RGBA")
        _emoji[name] = im.crop(im.getbbox())
    return _emoji[name]


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def alpha(c, a):
    return tuple(c[:3]) + (round(a * 255),)


class Pen:
    """Drawing in cm on an RGBA image whose top left sits at (ox, oy) cm."""

    def __init__(self, img, k, ox=0.0, oy=0.0):
        self.img, self.k, self.ox, self.oy = img, k, ox, oy
        self.d = ImageDraw.Draw(img)

    def p(self, x, y):
        return ((x - self.ox) * self.k, (y - self.oy) * self.k)

    def w(self, v):
        return max(1, round(v * self.k))

    def poly(self, pts, fill=None, outline=None, width=0.0):
        q = [self.p(x, y) for x, y in pts]
        if fill is not None:
            self.d.polygon(q, fill=fill)
        if outline is not None and width:
            self.d.line(q + q[:1], fill=outline, width=self.w(width), joint="curve")

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=None, width=0.0):
        x0, y0 = self.p(cx - rx, cy - ry)
        x1, y1 = self.p(cx + rx, cy + ry)
        self.d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline,
                       width=self.w(width) if outline is not None else 0)

    def circle(self, cx, cy, r, **kw):
        self.ellipse(cx, cy, r, r, **kw)

    def line(self, pts, fill, width, caps=True):
        self.d.line([self.p(x, y) for x, y in pts], fill=fill, width=self.w(width), joint="curve")
        if caps:
            for x, y in (pts[0], pts[-1]):
                self.circle(x, y, width / 2, fill=fill)

    def rrect(self, x0, y0, x1, y1, r, fill=None, outline=None, width=0.0):
        a, b = self.p(x0, y0)
        c, d = self.p(x1, y1)
        self.d.rounded_rectangle([a, b, c, d], radius=r * self.k, fill=fill, outline=outline,
                                 width=self.w(width) if outline is not None else 0)

    def vgrad(self, x0, y0, x1, y1, c0, c1, pts=None):
        """Vertical gradient c0 (top) to c1 (bottom) over a box, clipped to pts if given."""
        X0, Y0 = (round(v) for v in self.p(x0, y0))
        X1, Y1 = (round(v) for v in self.p(x1, y1))
        w, h = max(1, X1 - X0), max(1, Y1 - Y0)
        g = Image.composite(Image.new("RGBA", (w, h), alpha(c1, 1) if len(c1) == 3 else c1),
                            Image.new("RGBA", (w, h), alpha(c0, 1) if len(c0) == 3 else c0),
                            Image.linear_gradient("L").resize((w, h)))
        if pts is not None:
            m = Image.new("L", (w, h), 0)
            ImageDraw.Draw(m).polygon([(a - X0, b - Y0) for a, b in (self.p(x, y) for x, y in pts)], fill=255)
            g.putalpha(Image.composite(g.getchannel("A"), Image.new("L", (w, h), 0), m))
        self.img.alpha_composite(g, (X0, Y0))

    def paste(self, sprite, cx, cy, h=None, w=None, box=None, flip=False, opacity=1.0, clip=None):
        if box:
            s = min(box[0] * self.k / sprite.width, box[1] * self.k / sprite.height)
        elif h:
            s = h * self.k / sprite.height
        else:
            s = w * self.k / sprite.width
        sp = sprite.resize((max(1, round(sprite.width * s)), max(1, round(sprite.height * s))), Image.LANCZOS)
        if flip:
            sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
        if opacity < 1:
            sp.putalpha(sp.getchannel("A").point(lambda v: round(v * opacity)))
        x, y = self.p(cx, cy)
        X, Y = round(x - sp.width / 2), round(y - sp.height / 2)
        if clip:
            (a, b), (c, d) = self.p(clip[0], clip[1]), self.p(clip[2], clip[3])
            a, b, c, d = max(round(a), X), max(round(b), Y), min(round(c), X + sp.width), min(round(d), Y + sp.height)
            if a >= c or b >= d:
                return 0, 0
            sp, X, Y = sp.crop((a - X, b - Y, c - X, d - Y)), a, b
        self.img.alpha_composite(sp, (X, Y))
        return sp.width / self.k, sp.height / self.k

    def text(self, x, y, s, size, fill, anchor="mm"):
        key = round(size * self.k)
        if key not in _fonts:
            _fonts[key] = ImageFont.truetype(FONT_BOLD, key)
        self.d.text(self.p(x, y), s, font=_fonts[key], fill=fill, anchor=anchor)


class Layer(Pen):
    """Transparent overlay on a box of the canvas, for translucent fills and blurred shadows."""

    def __init__(self, base, x0, y0, x1, y1):
        self.base = base
        w, h = max(1, round((x1 - x0) * base.k)), max(1, round((y1 - y0) * base.k))
        super().__init__(Image.new("RGBA", (w, h), (0, 0, 0, 0)), base.k, x0, y0)

    def commit(self, blur=0.0, opacity=1.0):
        im = self.img
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur * self.k))
        if opacity < 1:
            im.putalpha(im.getchannel("A").point(lambda v: round(v * opacity)))
        x, y = self.base.p(self.ox, self.oy)
        self.base.img.alpha_composite(im, (round(x), round(y)))


class Canvas(Pen):
    def __init__(self, w_cm, h_cm, dpi=300, bg=(255, 255, 255, 255)):
        k = dpi / 2.54 * SS
        super().__init__(Image.new("RGBA", (round(w_cm * k), round(h_cm * k)), bg), k)
        self.W, self.H, self.dpi = w_cm, h_cm, dpi

    def layer(self, x0, y0, x1, y1):
        return Layer(self, x0, y0, x1, y1)

    def shadow(self, cx, cy, rx, ry, strength=0.22, blur=0.08):
        lay = self.layer(cx - rx - 3 * blur, cy - ry - 3 * blur, cx + rx + 3 * blur, cy + ry + 3 * blur)
        lay.ellipse(cx, cy, rx, ry, fill=(40, 40, 70, round(255 * strength)))
        lay.commit(blur=blur)

    def image(self, radius=0.45, border=(214, 224, 238)):
        out = self.img.resize((round(self.img.width / SS), round(self.img.height / SS)), Image.LANCZOS)
        if radius is None:
            return out.crop(out.getbbox())
        k = self.dpi / 2.54
        m = Image.new("L", out.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, out.width - 1, out.height - 1], radius=radius * k, fill=255)
        out.putalpha(m)
        ImageDraw.Draw(out).rounded_rectangle([0, 0, out.width - 1, out.height - 1], radius=radius * k,
                                              outline=border, width=max(1, round(0.05 * k)))
        return out


# ------------------------------------------------------------------ shapes

def wave(x0, x1, y, amp, period, phase=0.0, step=0.1):
    n = max(2, int((x1 - x0) / step))
    return [(x0 + (x1 - x0) * i / n, y + amp * math.sin((x0 + (x1 - x0) * i / n) / period * 2 * math.pi + phase))
            for i in range(n + 1)]


def blob(cx, cy, rx, ry, seed, wobble=0.08, n=40, flat_bottom=False):
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.3) for _ in range(3)]
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + wobble * (math.sin(2 * a + ph[0]) + 0.6 * math.sin(3 * a + ph[1]) + 0.3 * math.sin(5 * a + ph[2])) / 1.9
        y = cy + ry * r * math.sin(a)
        if flat_bottom:
            y = min(y, cy + ry * 0.35)
        pts.append((cx + rx * r * math.cos(a), y))
    return pts


def rounded(pts, r, steps=6):
    """Polygon with its corners rounded by radius r (cm)."""
    out = []
    for i, p in enumerate(pts):
        a, b = pts[i - 1], pts[(i + 1) % len(pts)]
        ua = (a[0] - p[0], a[1] - p[1])
        ub = (b[0] - p[0], b[1] - p[1])
        la, lb = math.hypot(*ua), math.hypot(*ub)
        p0 = (p[0] + ua[0] / la * r, p[1] + ua[1] / la * r)
        p1 = (p[0] + ub[0] / lb * r, p[1] + ub[1] / lb * r)
        for k in range(steps + 1):
            t = k / steps
            out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p[0] + t * t * p1[0],
                        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p[1] + t * t * p1[1]))
    return out


def sparkle(c, cx, cy, r, fill=(255, 255, 255)):
    """Four-point glint."""
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.22
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    c.poly(pts, fill=fill)


def cloud(c, cx, cy, s, fill=(255, 255, 255, 240), tint=(255, 222, 238, 235)):
    lay = c.layer(cx - 1.6 * s, cy - 1.0 * s, cx + 1.6 * s, cy + 0.8 * s)
    blobs = ((-0.75, 0.1, 0.42), (-0.25, -0.22, 0.55), (0.35, -0.12, 0.5), (0.85, 0.12, 0.38), (0.05, 0.18, 0.45))
    for dx, dy, r in blobs:
        lay.circle(cx + dx * s, cy + (dy + 0.08) * s, r * s, fill=tint)
    lay.rrect(cx - 1.1 * s, cy + 0.13 * s, cx + 1.2 * s, cy + 0.63 * s, 0.25 * s, fill=tint)
    for dx, dy, r in blobs:
        lay.circle(cx + dx * s, cy + dy * s, r * s, fill=fill)
    lay.rrect(cx - 1.1 * s, cy + 0.05 * s, cx + 1.2 * s, cy + 0.5 * s, 0.25 * s, fill=fill)
    lay.commit()


def rainbow(c, cx, cy, r_out, band, opacity=0.55):
    cols = [(255, 150, 170), (255, 196, 140), (255, 236, 150), (170, 226, 170), (150, 200, 245), (196, 170, 240)]
    lay = c.layer(cx - r_out, cy - r_out, cx + r_out, cy + r_out)
    for i, col in enumerate(cols):
        r = r_out - i * band
        lay.ellipse(cx, cy, r, r, fill=alpha(col, 1))
    lay.ellipse(cx, cy, r_out - len(cols) * band, r_out - len(cols) * band, fill=(0, 0, 0, 0))
    lay.commit(opacity=opacity)


def sun(c, cx, cy, r, col=(255, 226, 120), core=(255, 236, 160), ray=(255, 214, 110, 150)):
    lay = c.layer(cx - 3.2 * r, cy - 3.2 * r, cx + 3.2 * r, cy + 3.2 * r)
    lay.circle(cx, cy, 1.7 * r, fill=alpha(core, 0.47))
    lay.commit(blur=0.3 * r)
    rays = c.layer(cx - 2.6 * r, cy - 2.6 * r, cx + 2.6 * r, cy + 2.6 * r)
    for k in range(12):
        a = k * math.pi / 6 + 0.13
        rays.poly([(cx + 1.3 * r * math.cos(a - 0.1), cy + 1.3 * r * math.sin(a - 0.1)),
                   (cx + 2.15 * r * math.cos(a), cy + 2.15 * r * math.sin(a)),
                   (cx + 1.3 * r * math.cos(a + 0.1), cy + 1.3 * r * math.sin(a + 0.1))], fill=ray)
    rays.commit()
    c.circle(cx, cy, r, fill=col)
    c.circle(cx - 0.18 * r, cy - 0.2 * r, 0.62 * r, fill=core)


GLITTER = [(255, 160, 205), (190, 160, 250), (140, 205, 250), (255, 220, 110), (160, 228, 196), (255, 255, 255)]


def glitter(c, pts, n, seed, spread=0.16, size=(0.022, 0.055), glints=6):
    """Glitter dust along a polyline: tiny pastel dots and a few white glints."""
    rnd = random.Random(seed)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    lay = c.layer(min(xs) - 0.6, min(ys) - 0.6, max(xs) + 0.6, max(ys) + 0.6)
    segs = list(zip(pts, pts[1:]))

    def at():
        (x0, y0), (x1, y1) = rnd.choice(segs)
        t = rnd.random()
        return x0 + (x1 - x0) * t + rnd.gauss(0, spread), y0 + (y1 - y0) * t + rnd.gauss(0, spread)
    for _ in range(n):
        x, y = at()
        lay.circle(x, y, rnd.uniform(*size), fill=alpha(rnd.choice(GLITTER), rnd.uniform(0.65, 1)))
    for _ in range(glints):
        x, y = at()
        sparkle(lay, x, y, rnd.uniform(0.08, 0.17), fill=(255, 255, 255, 245))
        sparkle(lay, x, y, rnd.uniform(0.04, 0.07), fill=(255, 226, 120, 255))
    lay.commit()


def curve(p0, p1, p2, n=30):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


def sandcastle(c, cx, base, s=1.0):
    sand, dark = (244, 218, 166), (204, 168, 112)
    c.shadow(cx, base, 1.0 * s, 0.14 * s, strength=0.2)
    for dx, h, w in ((-0.62, 1.0, 0.42), (0.62, 1.0, 0.42), (0.0, 0.72, 1.0)):
        c.rrect(cx + (dx - w / 2) * s, base - h * s, cx + (dx + w / 2) * s, base, 0.06 * s, fill=sand, outline=dark, width=0.03 * s)
    for dx in (-0.62, 0.62):
        for k in (-1, 1):
            x = cx + (dx + k * 0.13) * s
            c.rrect(x - 0.06 * s, base - 1.13 * s, x + 0.06 * s, base - 0.98 * s, 0.02 * s, fill=sand, outline=dark, width=0.02 * s)
        c.poly([(cx + (dx - 0.2) * s, base - 1.0 * s), (cx + (dx + 0.2) * s, base - 1.0 * s), (cx + dx * s, base - 1.42 * s)],
               fill=(250, 196, 214), outline=(214, 120, 160), width=0.025 * s)
    c.line([(cx, base - 0.72 * s), (cx, base - 1.5 * s)], fill=(160, 130, 100), width=0.03 * s)
    c.poly([(cx, base - 1.5 * s), (cx + 0.4 * s, base - 1.37 * s), (cx, base - 1.24 * s)], fill=(244, 120, 170))
    c.rrect(cx - 0.17 * s, base - 0.42 * s, cx + 0.17 * s, base + 0.01 * s, 0.17 * s, fill=(180, 140, 96))
    for x, y in ((cx - 0.62 * s, base - 0.55 * s), (cx + 0.62 * s, base - 0.55 * s)):
        c.circle(x, y, 0.07 * s, fill=(255, 255, 255), outline=(200, 190, 210), width=0.015 * s)


def bush(c, cx, base, w, h, flowers, seed):
    rnd = random.Random(seed)
    green, dark = (104, 176, 104), (80, 150, 86)
    for k in range(7):
        x = cx + (k / 6 - 0.5) * w * 0.8
        r = h * rnd.uniform(0.38, 0.55)
        c.circle(x, base - r * 0.9, r, fill=dark if k % 2 else green)
    for _ in range(int(w * 6)):
        x = cx + rnd.uniform(-0.45, 0.45) * w
        y = base - rnd.uniform(0.15, 0.95) * h
        col = rnd.choice(flowers)
        r = rnd.uniform(0.07, 0.11)
        for a in range(5):
            c.circle(x + r * 0.9 * math.cos(a * 1.2566), y + r * 0.9 * math.sin(a * 1.2566), r * 0.75, fill=col)
        c.circle(x, y, r * 0.5, fill=(255, 224, 120))


def rose_arch(c, cx, base, w, h, seed):
    rnd = random.Random(seed)
    post, post_d = (255, 252, 246), (214, 204, 214)
    r = w / 2
    for x in (cx - r, cx + r):
        c.rrect(x - 0.1, base - h + r, x + 0.1, base, 0.05, fill=post, outline=post_d, width=0.025)
    top = base - h + r
    arc = [(cx + r * math.cos(a), top + r * 0.95 * math.sin(a)) for a in [math.pi + math.pi * i / 40 for i in range(41)]]
    c.line(arc, fill=post_d, width=0.26)
    c.line(arc, fill=post, width=0.2)
    vine = arc + [(cx + r, top + (base - top) * t) for t in (0.3, 0.6, 0.9)]
    vine = [(cx - r, top + (base - top) * t) for t in (0.9, 0.6, 0.3)] + vine
    for i, (x, y) in enumerate(vine):
        for _ in range(2):
            lx, ly = x + rnd.uniform(-0.18, 0.18), y + rnd.uniform(-0.14, 0.14)
            c.ellipse(lx, ly, 0.11, 0.07, fill=(110, 178, 104))
        if i % 3 == 0:
            col = rnd.choice([(244, 110, 160), (255, 160, 196), (255, 255, 255), (230, 80, 120)])
            c.circle(x, y, 0.13, fill=col, outline=mix(col, (120, 40, 80), 0.3), width=0.015)
            c.circle(x, y, 0.05, fill=mix(col, (120, 40, 80), 0.25))


def fairy_lights(c, pts, every=0.55):
    lay = c.layer(min(p[0] for p in pts) - 0.4, min(p[1] for p in pts) - 0.4,
                  max(p[0] for p in pts) + 0.4, max(p[1] for p in pts) + 0.4)
    acc, last = 0.0, pts[0]
    for p in pts[1:]:
        acc += math.dist(p, last)
        last = p
        if acc >= every:
            acc = 0.0
            lay.circle(p[0], p[1] + 0.06, 0.12, fill=(255, 236, 150, 90))
            lay.circle(p[0], p[1] + 0.06, 0.05, fill=(255, 246, 200, 255))
    lay.commit()


def starfish(c, cx, cy, r, col=(250, 150, 120), rot=0.0):
    pts = []
    for i in range(10):
        a = rot + math.pi / 5 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    c.poly(pts, fill=col, outline=mix(col, (160, 70, 60), 0.4), width=0.025)
    for i in range(5):
        a = rot + 2 * math.pi / 5 * i - math.pi / 2
        c.circle(cx + 0.55 * r * math.cos(a), cy + 0.55 * r * math.sin(a), 0.05 * r + 0.02, fill=mix(col, (255, 255, 255), 0.5))


def rock(c, cx, cy, rx, ry, seed, col=(176, 172, 196)):
    c.shadow(cx + 0.05, cy + ry * 0.55, rx * 0.95, ry * 0.25, strength=0.18)
    pts = blob(cx, cy, rx, ry, seed, wobble=0.1, flat_bottom=True)
    c.poly(pts, fill=col, outline=mix(col, (90, 80, 120), 0.35), width=0.03)
    hi = blob(cx - rx * 0.18, cy - ry * 0.25, rx * 0.55, ry * 0.32, seed + 7, wobble=0.12)
    lay = c.layer(cx - rx, cy - ry, cx + rx, cy + ry)
    lay.poly(hi, fill=(255, 255, 255, 70))
    lay.commit()


def seaweed(c, x, ybase, h, col, seed):
    rnd = random.Random(seed)
    for k in range(3):
        dx = (k - 1) * 0.18
        ph = rnd.uniform(0, 6.3)
        pts = [(x + dx + 0.12 * math.sin(ph + i * 0.9), ybase - h * (0.75 + 0.25 * (k == 1)) * i / 8) for i in range(9)]
        c.line(pts, fill=mix(col, (255, 255, 255), 0.15 * k), width=0.11)


def coral(c, x, ybase, s, col):
    def branch(x0, y0, a, length, w, depth):
        x1, y1 = x0 + length * math.cos(a), y0 - length * math.sin(a)
        c.line([(x0, y0), (x1, y1)], fill=col, width=w)
        if depth:
            branch(x1, y1, a + 0.45, length * 0.72, w * 0.78, depth - 1)
            branch(x1, y1, a - 0.45, length * 0.72, w * 0.78, depth - 1)
    branch(x, ybase, math.pi / 2, 0.55 * s, 0.16 * s, 3)


# ------------------------------------------------------------------ containers and tokens

def pearl(c, cx, cy, r):
    c.shadow(cx + 0.03, cy + r * 0.55, r * 0.95, r * 0.45, strength=0.28, blur=0.04)
    c.circle(cx, cy, r, fill=(244, 240, 250), outline=(176, 166, 198), width=0.022)
    c.ellipse(cx + r * 0.12, cy + r * 0.18, r * 0.78, r * 0.7, fill=(250, 248, 255))
    c.ellipse(cx - r * 0.3, cy - r * 0.32, r * 0.34, r * 0.26, fill=(255, 255, 255))


ROWS = {1: [1], 2: [2], 3: [3], 4: [2, 2], 5: [3, 2], 6: [3, 3]}


def shell(c, cx, cy, n, fam, s=1.0):
    """Open clam: ribbed lid behind, a dish in front holding n pearls in rows; family 0 pink, 1 blue."""
    body = [(250, 196, 218), (186, 214, 248)][fam]
    edge = [(214, 92, 150), (66, 120, 206)][fam]
    velvet = [((236, 128, 176), (222, 104, 160)), ((118, 162, 234), (92, 140, 222))][fam]
    hx, hy = cx, cy + 0.3 * s
    c.shadow(cx, hy + 0.82 * s, 1.5 * s, 0.2 * s, strength=0.22)
    ribs, lid = 9, []
    for i in range(91):
        t = i / 90
        a = math.radians(-168 + 156 * t)
        bump = 0.07 * s * abs(math.sin(math.pi * ribs * t))
        lid.append((hx + (1.42 * s + bump) * math.cos(a), hy + (1.3 * s + bump) * math.sin(a)))
    c.poly(lid, fill=body, outline=edge, width=0.04 * s)
    sheen = [(250, 214, 238), (206, 226, 252)][fam], [(214, 196, 250), (190, 238, 226)][fam]
    c.vgrad(hx - 1.5 * s, hy - 1.42 * s, hx + 1.5 * s, hy, sheen[0], sheen[1],
            [(hx + (x - hx) * 0.93, hy + (y - hy) * 0.93) for x, y in lid])
    for i in range(1, ribs):
        a = math.radians(-168 + 156 * i / ribs)
        c.line([(hx + 0.55 * s * math.cos(a), hy + 0.5 * s * math.sin(a)),
                (hx + 1.4 * s * math.cos(a), hy + 1.28 * s * math.sin(a))], fill=mix(body, edge, 0.3), width=0.03 * s)
    dish = []
    for i in range(72):
        a = 2 * math.pi * i / 72
        wav = 0.035 * s * math.sin(12 * a)
        dish.append((hx + (1.5 * s + wav) * math.cos(a), hy + (0.84 * s + wav) * math.sin(a)))
    c.poly(dish, fill=body, outline=edge, width=0.04 * s)
    inner = [(hx + 1.3 * s * math.cos(2 * math.pi * i / 60), hy - 0.04 * s + 0.68 * s * math.sin(2 * math.pi * i / 60))
             for i in range(60)]
    c.vgrad(hx - 1.3 * s, hy - 0.72 * s, hx + 1.3 * s, hy + 0.64 * s, velvet[1], velvet[0], inner)
    sparkle(c, hx + 0.95 * s, hy - 1.08 * s, 0.13 * s, fill=(255, 255, 255))
    r, dx = 0.27 * s, 0.7 * s
    rows = ROWS[n]
    ys = [hy - 0.04 * s] if len(rows) == 1 else [hy - 0.39 * s, hy + 0.31 * s]
    for y, k in zip(ys, rows):
        for j in range(k):
            pearl(c, cx + (j - (k - 1) / 2) * dx, y, r)


def badge(c, x, y, t, fam, s=1.0):
    ink = [(214, 51, 132), (37, 99, 200)][fam]
    w = (0.66 if t < 10 else 0.86) * s
    h = 0.66 * s
    lay = c.layer(x - w, y - h, x + w, y + h)
    lay.rrect(x - w / 2 + 0.03, y - h / 2 + 0.05, x + w / 2 + 0.03, y + h / 2 + 0.05, 0.14 * s, fill=(30, 30, 60, 70))
    lay.commit(blur=0.04)
    c.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 0.14 * s, fill=ink, outline=(255, 255, 255), width=0.06 * s)
    c.text(x, y + 0.02 * s, str(t), 0.44 * s, (255, 255, 255))



# ------------------------------------------------------------------ trails: the stations in number order

def catmull(pts, n=14):
    """Smooth curve through all points (Catmull-Rom)."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def along(pts, step):
    """Points every step cm along a polyline, each with its direction."""
    out, d = [], 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.dist((x0, y0), (x1, y1))
        if seg == 0:
            continue
        a = math.atan2(y1 - y0, x1 - x0)
        while d < seg:
            out.append((x0 + (x1 - x0) * d / seg, y0 + (y1 - y0) * d / seg, a))
            d += step
        d -= seg
    return out


def paw(c, x, y, a, col, s=0.16):
    ca, sa = math.cos(a), math.sin(a)

    def at(f, g):
        return x + f * ca - g * sa, y + f * sa + g * ca
    c.ellipse(*at(-0.25 * s, 0), 0.5 * s, 0.42 * s, fill=col)
    for f, g in ((0.45, -0.52), (0.72, -0.18), (0.72, 0.18), (0.45, 0.52)):
        c.circle(*at(f * s, g * s), 0.19 * s, fill=col)


def trail(c, stations, style, cols=((236, 120, 172, 120), (96, 150, 222, 120)), last=None):
    """Join the stations in number order; the first seven in pink, the rest in blue."""
    pts = [(st["x"], st["y"]) for st in sorted(stations, key=lambda st: st["t"])]
    halves = [(pts[:7], cols[0]), (pts[6:] if last is None else pts[6:last], cols[1])]
    lay = c.layer(0, 0, c.W, c.H)
    for half, col in halves:
        if len(half) < 2:
            continue
        path = catmull(half)
        if style == "paws":
            for i, (x, y, a) in enumerate(along(path, 0.4)):
                side = 0.1 if i % 2 else -0.1
                paw(lay, x - side * math.sin(a), y + side * math.cos(a), a, col)
        elif style == "stones":
            for x, y, a in along(path, 0.62):
                lay.ellipse(x, y, 0.22, 0.13, fill=(238, 228, 214, 255), outline=(206, 192, 178, 255), width=0.02)
        elif style == "rails":
            for off in (-0.13, 0.13):
                side = [(x - off * math.sin(a), y + off * math.cos(a)) for x, y, a in along(path, 0.05)]
                lay.line(side, fill=col, width=0.05, caps=False)
            for x, y, a in along(path, 0.24):
                dx, dy = -0.19 * math.sin(a), 0.19 * math.cos(a)
                lay.line([(x - dx, y - dy), (x + dx, y + dy)], fill=mix(col, (120, 80, 50), 0.25) + (255,), width=0.07, caps=False)
        elif style == "skates":
            for off in (-0.06, 0.06):
                side = [(x - off * math.sin(a), y + off * math.cos(a)) for x, y, a in along(path, 0.05)]
                lay.line(side, fill=(150, 140, 226, 200), width=0.035, caps=False)
                lay.line([(px, py - 0.02) for px, py in side], fill=(255, 255, 255, 230), width=0.015, caps=False)
        elif style == "bubbles":
            rnd = random.Random(len(half))
            for x, y, a in along(path, 0.3):
                r = rnd.uniform(0.05, 0.09)
                lay.circle(x, y, r, outline=(255, 255, 255, 230), width=0.022)
                lay.circle(x - r * 0.3, y - r * 0.3, r * 0.25, fill=(255, 255, 255, 220))
    lay.commit()


UP = {1: [(0, 0)], 2: [(-0.4, 0), (0.4, 0)], 3: [(0, -0.38), (-0.4, 0.32), (0.4, 0.32)]}


PETALS = [(255, 196, 222), (210, 192, 246), (255, 214, 182), (190, 220, 250)]


def flower(c, cx, cy, n, kind, petal, s=1.0):
    """Big flower with n bugs on its white heart."""
    c.shadow(cx, cy + 1.3 * s, 1.05 * s, 0.15 * s, strength=0.14)
    edge = mix(petal, (150, 80, 120), 0.28)
    for k in range(8):
        a = k * math.pi / 4 + 0.2
        c.circle(cx + 0.82 * s * math.cos(a), cy + 0.82 * s * math.sin(a), 0.5 * s, fill=petal, outline=edge, width=0.025 * s)
    c.circle(cx, cy, 0.93 * s, fill=(255, 253, 244), outline=(248, 210, 110), width=0.06 * s)
    sp = emoji(kind)
    for dx, dy in UP[n]:
        c.paste(sp, cx + dx * s, cy + dy * s, box=(0.66 * s, 0.66 * s))


def train_window(c, cx, cy, n, fam, kind, s=1.0, glow=False):
    """Train window with n passengers looking out."""
    frame = [(236, 112, 170), (88, 150, 222)][fam]
    w, h = 0.92 * s, 0.74 * s
    if glow:
        lay = c.layer(cx - w - 0.5, cy - h - 0.5, cx + w + 0.5, cy + h + 0.5)
        lay.rrect(cx - w - 0.05, cy - h - 0.05, cx + w + 0.05, cy + h + 0.05, 0.3, fill=(255, 236, 170, 150))
        lay.commit(blur=0.12)
    c.rrect(cx - w, cy - h, cx + w, cy + h, 0.2 * s, fill=frame)
    inner = rounded([(cx - w + 0.1 * s, cy - h + 0.1 * s), (cx + w - 0.1 * s, cy - h + 0.1 * s),
                     (cx + w - 0.1 * s, cy + h - 0.1 * s), (cx - w + 0.1 * s, cy + h - 0.1 * s)], 0.14 * s)
    c.vgrad(cx - w, cy - h, cx + w, cy + h, (255, 248, 222) if glow else (232, 244, 255),
            (255, 232, 190) if glow else (255, 248, 232), inner)
    face = emoji(kind)
    rows = ROWS[n]
    ys = [cy] if len(rows) == 1 else [cy - 0.28 * s, cy + 0.3 * s]
    for y, k in zip(ys, rows):
        for j in range(k):
            c.paste(face, cx + (j - (k - 1) / 2) * 0.55 * s, y, box=(0.48 * s, 0.48 * s))
    c.rrect(cx - w - 0.06 * s, cy + h - 0.05 * s, cx + w + 0.06 * s, cy + h + 0.1 * s, 0.05 * s,
            fill=mix(frame, (255, 255, 255), 0.4))


def balloon(c, cx, cy, item, fam, s=1.0):
    """Balloon with a letter card painted on it (word captioned like the A3 cards)."""
    body = [(255, 196, 222), (192, 220, 252)][fam]
    ink = [(176, 30, 110), (30, 90, 180)][fam]
    rx, ry = 0.95 * s, 1.1 * s
    pts = [(cx + rx * math.cos(a), cy + ry * math.sin(a) * (1 + 0.1 * max(0.0, math.sin(a))))
           for a in [2 * math.pi * i / 80 for i in range(80)]]
    c.shadow(cx + 0.08, cy + 0.1, rx * 0.95, ry * 0.95, strength=0.12, blur=0.12)
    c.poly(pts, fill=body, outline=mix(body, ink, 0.4), width=0.04 * s)
    shine = c.layer(cx - rx, cy - ry, cx + rx, cy + ry)
    shine.ellipse(cx - 0.45 * s, cy - 0.55 * s, 0.2 * s, 0.32 * s, fill=(255, 255, 255, 150))
    shine.commit()
    ky = cy + ry * 1.1
    c.poly([(cx, ky - 0.04), (cx - 0.12 * s, ky + 0.14 * s), (cx + 0.12 * s, ky + 0.14 * s)], fill=mix(body, ink, 0.3))
    c.text(cx, cy - 0.08 * s, chr(65 + item["n"]), 1.0 * s, ink)
    if item.get("word"):
        c.text(cx, cy + 0.66 * s, item["word"], 0.25 * s, ink)


# ------------------------------------------------------------------ fairy-tale props, snow, toys

def pumpkin_coach(c, cx, base, s=1.0):
    """Cinderella's coach (Perrault): a pumpkin on gold wheels."""
    c.shadow(cx, base, 0.8 * s, 0.12 * s, strength=0.2)
    for dx in (-0.45, 0.45):
        c.circle(cx + dx * s, base - 0.2 * s, 0.2 * s, fill=(255, 214, 120), outline=(214, 160, 70), width=0.03 * s)
        c.circle(cx + dx * s, base - 0.2 * s, 0.06 * s, fill=(214, 160, 70))
    for k, (dx, r) in enumerate(((-0.42, 0.42), (0.42, 0.42), (0.0, 0.5))):
        c.ellipse(cx + dx * s, base - 0.72 * s, r * s, 0.5 * s, fill=(255, 168, 96) if k < 2 else (255, 182, 110),
                  outline=(222, 120, 60), width=0.03 * s)
    c.rrect(cx - 0.2 * s, base - 0.98 * s, cx + 0.2 * s, base - 0.62 * s, 0.14 * s, fill=(255, 240, 210),
            outline=(214, 160, 70), width=0.025 * s)
    c.line([(cx, base - 1.2 * s), (cx + 0.08 * s, base - 1.42 * s)], fill=(110, 170, 90), width=0.07 * s)
    for dx in (-0.62, 0.62):
        c.line(curve((cx + dx * s, base - 1.05 * s), (cx + dx * 1.5 * s, base - 1.4 * s), (cx + dx * 1.15 * s, base - 1.6 * s), 12),
               fill=(240, 196, 90), width=0.04 * s)


def glass_slipper(c, cx, cy, s=1.0):
    """The slipper Cinderella lost on the palace stairs, with a glint."""
    lay = c.layer(cx - 0.8 * s, cy - 0.6 * s, cx + 0.8 * s, cy + 0.4 * s)
    shoe = [(cx - 0.55 * s, cy + 0.12 * s), (cx - 0.5 * s, cy - 0.12 * s), (cx - 0.15 * s, cy - 0.22 * s),
            (cx + 0.2 * s, cy - 0.05 * s), (cx + 0.55 * s, cy - 0.32 * s), (cx + 0.6 * s, cy + 0.12 * s)]
    lay.poly(shoe, fill=(206, 230, 255, 220), outline=(130, 160, 230, 255), width=0.03 * s)
    lay.line([(cx + 0.5 * s, cy - 0.28 * s), (cx + 0.52 * s, cy + 0.3 * s)], fill=(130, 160, 230, 255), width=0.04 * s)
    lay.commit()
    sparkle(c, cx + 0.2 * s, cy - 0.3 * s, 0.16 * s, fill=(255, 255, 255))
    glitter(c, [(cx - 0.6 * s, cy - 0.3 * s), (cx + 0.7 * s, cy - 0.4 * s)], 20, 7, spread=0.12, glints=2)


def snowflake(c, cx, cy, r, col=(255, 255, 255), edge=(118, 104, 214)):
    arms = []
    for k in range(6):
        a = k * math.pi / 3 - math.pi / 2
        arms.append([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))])
        bx, by = cx + 0.55 * r * math.cos(a), cy + 0.55 * r * math.sin(a)
        for da in (-0.7, 0.7):
            arms.append([(bx, by), (bx + 0.38 * r * math.cos(a + da), by + 0.38 * r * math.sin(a + da))])
    for seg in arms:
        c.line(seg, fill=edge, width=0.3 * r)
    for seg in arms:
        c.line(seg, fill=col, width=0.13 * r)
    c.circle(cx, cy, 0.2 * r, fill=col, outline=edge, width=0.07 * r)


def snow_globe(c, cx, cy, n, fam, s=1.0):
    """Snow globe on a family-coloured stand with n snowflakes in rows."""
    base = [(244, 140, 190), (110, 160, 230)][fam]
    dark = mix(base, (60, 40, 90), 0.3)
    R, gy = 1.0 * s, cy - 0.2 * s
    c.shadow(cx, gy + 1.3 * s, 1.0 * s, 0.14 * s, strength=0.2)
    c.poly([(cx - 0.72 * s, gy + 0.8 * s), (cx + 0.72 * s, gy + 0.8 * s), (cx + 0.95 * s, gy + 1.24 * s),
            (cx - 0.95 * s, gy + 1.24 * s)], fill=base, outline=dark, width=0.03 * s)
    c.rrect(cx - 1.0 * s, gy + 1.18 * s, cx + 1.0 * s, gy + 1.34 * s, 0.06 * s, fill=mix(base, (255, 255, 255), 0.3),
            outline=dark, width=0.025 * s)
    ring = [(cx + R * math.cos(a), gy + R * math.sin(a)) for a in [2 * math.pi * i / 90 for i in range(90)]]
    c.vgrad(cx - R, gy - R, cx + R, gy + R, (214, 228, 252), (170, 194, 246), ring)
    c.ellipse(cx, gy + 0.8 * R, 0.58 * R, 0.14 * R, fill=(255, 255, 255))
    rows = ROWS[n]
    ys = [gy - 0.05 * s] if len(rows) == 1 else [gy - 0.34 * s, gy + 0.28 * s]
    for y, k in zip(ys, rows):
        for j in range(k):
            snowflake(c, cx + (j - (k - 1) / 2) * 0.62 * s, y, 0.25 * s)
    shine = c.layer(cx - R, gy - R, cx + R, gy + R)
    shine.ellipse(cx - 0.52 * R, gy - 0.55 * R, 0.15 * R, 0.28 * R, fill=(255, 255, 255, 170))
    shine.commit()
    c.circle(cx, gy, R, outline=(122, 118, 214), width=0.045 * s)


def ice_palace(c, cx, base, s=1.0):
    ice, edge, tip = (232, 242, 255), (140, 150, 226), (200, 172, 242)
    for dx, h, w in ((-1.3, 2.2, 0.5), (1.3, 2.2, 0.5), (-0.65, 2.95, 0.6), (0.65, 2.95, 0.6), (0.0, 3.8, 0.8)):
        x, hw = cx + dx * s, w / 2 * s
        shoulder = base - (h - 0.9) * s
        c.poly([(x - hw, base), (x + hw, base), (x + hw, shoulder), (x - hw, shoulder)], fill=ice, outline=edge, width=0.03 * s)
        c.poly([(x - hw, shoulder), (x + hw, shoulder), (x, base - h * s)], fill=tip, outline=edge, width=0.03 * s)
        c.line([(x, shoulder + 0.1 * s), (x, base - 0.15 * s)], fill=(206, 220, 252), width=0.035 * s)
    c.rrect(cx - 0.32 * s, base - 0.95 * s, cx + 0.32 * s, base + 0.01, 0.32 * s, fill=(176, 164, 238), outline=edge, width=0.03 * s)
    glitter(c, [(cx - 1.3 * s, base - 2.2 * s), (cx, base - 3.8 * s), (cx + 1.3 * s, base - 2.2 * s)], 50, 13, spread=0.16, glints=6)


def aurora(c, W, y):
    lay = c.layer(0, 0, W, y + 2.0)
    for k, col in enumerate(((255, 150, 210, 120), (196, 150, 250, 120), (140, 232, 214, 105))):
        pts = [(x, y + 0.33 * k + 0.32 * math.sin(x / 3.1 + k) + 0.14 * math.sin(x / 1.3 + 2 * k)) for x in [W * i / 120 for i in range(121)]]
        lay.line(pts, fill=col, width=0.48, caps=False)
    lay.commit(blur=0.22)


def cube(c, x, y, a, col):
    """One linking cube, a cm wide, centred at (x, y)."""
    dark, light = mix(col, (60, 40, 90), 0.32), mix(col, (255, 255, 255), 0.45)
    c.rrect(x - a / 2, y - a / 2, x + a / 2, y + a / 2, a * 0.14, fill=col, outline=dark, width=a * 0.07)
    c.rrect(x - a / 2 + a * 0.12, y - a / 2 + a * 0.1, x + a / 2 - a * 0.12, y - a / 2 + a * 0.26, a * 0.06, fill=light)


def tower(c, cx, cy, n, fam, a=0.44):
    """n linking cubes stacked on a play mat: the mat sits at cy, the tower rises above it."""
    col = [(244, 130, 182), (96, 150, 226)][fam]
    c.ellipse(cx, cy + 0.12, 0.8, 0.24, fill=mix(col, (255, 255, 255), 0.72), outline=mix(col, (255, 255, 255), 0.35), width=0.03)
    c.shadow(cx + 0.06, cy + 0.1, 0.36, 0.08, strength=0.3)
    for k in range(n):
        cube(c, cx, cy - (k + 0.5) * a, a, col)


def tower_sprite(n, fam, dpi=300):
    """A tower of n cubes on its own, for the answer grid."""
    c = Canvas(1.0, 0.44 * n + 0.2, dpi=dpi, bg=(0, 0, 0, 0))
    col = [(244, 130, 182), (96, 150, 226)][fam]
    for k in range(n):
        cube(c, 0.5, 0.44 * n + 0.1 - (k + 0.5) * 0.44, 0.44, col)
    return c.image(radius=None)


BLOCK_COLS = [(255, 196, 222), (214, 196, 250), (190, 236, 214), (255, 232, 160), (190, 220, 252)]


def letter_block(c, cx, cy, ch, col, s=1.0):
    """Wooden ABC toy block in three-quarter view with one letter on the front."""
    f, d = 0.85 * s, 0.32 * s
    dark = mix(col, (90, 60, 110), 0.35)
    c.shadow(cx + 0.15 * s, cy + f + 0.05, f * 1.1, 0.14 * s, strength=0.2)
    c.poly([(cx - f, cy - f), (cx - f + d, cy - f - d), (cx + f + d, cy - f - d), (cx + f, cy - f)],
           fill=mix(col, (255, 255, 255), 0.45), outline=dark, width=0.03 * s)
    c.poly([(cx + f, cy - f), (cx + f + d, cy - f - d), (cx + f + d, cy + f - d), (cx + f, cy + f)],
           fill=mix(col, (90, 60, 110), 0.15), outline=dark, width=0.03 * s)
    c.rrect(cx - f, cy - f, cx + f, cy + f, 0.1 * s, fill=col, outline=dark, width=0.035 * s)
    c.rrect(cx - f + 0.12 * s, cy - f + 0.12 * s, cx + f - 0.12 * s, cy + f - 0.12 * s, 0.08 * s,
            outline=mix(col, (255, 255, 255), 0.55), width=0.03 * s)
    c.text(cx, cy + 0.05 * s, ch, 1.15 * s, mix(col, (60, 30, 90), 0.72))


def dollhouse(c, cx, base, s=1.0):
    """Open-front dollhouse with kittens in its rooms."""
    wall, edge, roof = (255, 226, 238), (214, 150, 186), (196, 160, 240)
    w, h = 1.9 * s, 2.6 * s
    c.shadow(cx, base, w * 0.6, 0.15 * s, strength=0.2)
    c.poly([(cx - w / 2 - 0.2 * s, base - h), (cx + w / 2 + 0.2 * s, base - h), (cx, base - h - 1.1 * s)],
           fill=roof, outline=mix(roof, (80, 50, 120), 0.3), width=0.035 * s)
    c.rrect(cx - w / 2, base - h, cx + w / 2, base, 0.06 * s, fill=wall, outline=edge, width=0.04 * s)
    for r in range(2):
        for k in range(2):
            x0 = cx - w / 2 + 0.12 * s + k * (w - 0.24 * s) / 2
            y0 = base - h + 0.15 * s + r * (h - 0.3 * s) / 2
            x1, y1 = x0 + (w - 0.24 * s) / 2 - 0.08 * s, y0 + (h - 0.3 * s) / 2 - 0.1 * s
            c.rrect(x0, y0, x1, y1, 0.06 * s, fill=[(255, 244, 214), (226, 240, 255)][(r + k) % 2], outline=edge, width=0.025 * s)
            c.rrect(x0, y1 - 0.12 * s, x1, y1, 0.02 * s, fill=(236, 200, 160))
            c.paste(emoji("cat"), (x0 + x1) / 2, y1 - 0.42 * s, h=0.48 * s)
    c.circle(cx, base - h - 0.45 * s, 0.2 * s, fill=(255, 244, 214), outline=edge, width=0.03 * s)
    c.paste(emoji("pinkheart"), cx, base - h - 0.45 * s, h=0.22 * s)


def toy_room(c, stations, station_painter):
    W, H = c.W, c.H
    floor_y = 4.3
    c.vgrad(0, 0, W, floor_y, (246, 226, 246), (252, 238, 248))
    dots = c.layer(0, 0, W, floor_y)
    rnd = random.Random(4)
    for _ in range(90):
        sparkle(dots, rnd.uniform(0.2, W - 0.2), rnd.uniform(0.6, floor_y - 0.3), rnd.uniform(0.05, 0.1), fill=(255, 255, 255, 230))
    dots.commit()
    c.vgrad(0, floor_y, W, H, (246, 222, 196), (236, 206, 176), [(0, floor_y), (W, floor_y), (W, H), (0, H)])
    planks = c.layer(0, floor_y, W, H)
    for k in range(1, 6):
        y = floor_y + k * (H - floor_y) / 6
        planks.line([(0, y), (W, y)], fill=(214, 180, 150, 120), width=0.02, caps=False)
    planks.commit()
    c.rrect(0, floor_y - 0.12, W, floor_y + 0.05, 0.02, fill=(255, 250, 252), outline=(230, 206, 222), width=0.02)
    # window with a rainbow, fairy lights, a shelf of friends
    c.rrect(9.6, 0.45, 12.4, 2.6, 0.12, fill=(206, 230, 252), outline=(255, 255, 255), width=0.12)
    rainbow(c, 11.0, 2.75, 1.7, 0.13, opacity=0.6)
    c.line([(11.0, 0.45), (11.0, 2.6)], fill=(255, 255, 255), width=0.08)
    for x in (9.45, 12.55):
        c.rrect(x - 0.32, 0.3, x + 0.32, 2.85, 0.15, fill=(250, 186, 214), outline=(226, 140, 180), width=0.025)
    lights = [(x, 0.18 + 0.28 * math.sin(x / 2.0) ** 2) for x in [W * i / 80 for i in range(81)]]
    c.line(lights, fill=(170, 150, 180), width=0.02, caps=False)
    fairy_lights(c, lights, every=0.7)
    c.rrect(19.3, 1.7, 21.4, 1.85, 0.03, fill=(236, 196, 160), outline=(206, 160, 120), width=0.02)
    for x, nm, h in ((19.85, "unicorn", 0.8), (20.85, "teddy", 0.78)):
        c.paste(emoji(nm), x, 1.7 - h / 2, h=h)
    dollhouse(c, W / 2, 4.9, 0.95)
    c.ellipse(W / 2, 6.9, 2.0, 0.42, fill=(250, 200, 222), outline=(236, 160, 196), width=0.03)
    trail(c, stations, "rails", cols=((206, 168, 132, 255), (206, 168, 132, 255)))
    for st in stations:
        station_painter(c, st)
    c.paste(emoji("catfull"), W / 2 - 1.4, 4.6, h=0.75)
    c.paste(emoji("puppy"), W / 2 + 1.4, 4.6, h=0.75, flip=True)
    c.paste(art.princess_variant(11, "wand"), W / 2 - 0.25, 6.0, h=2.2)
    glitter(c, curve((W / 2 + 0.4, 5.0), (W / 2 + 1.2, 4.3), (W / 2 + 0.7, 3.6)), 50, 19, spread=0.13, glints=5)


def toys_towers(c, stations):
    def paint(c, st):
        tower(c, st["x"], st["y"], st["item"]["n"], st["fam"])
        badge(c, st["x"] - 0.98, st["y"] - 0.3, st["t"], st["fam"])
    toy_room(c, stations, paint)


def toys_blocks(c, stations):
    def paint(c, st):
        letter_block(c, st["x"], st["y"], chr(65 + st["item"]["n"]), BLOCK_COLS[st["t"] % len(BLOCK_COLS)])
        badge(c, st["x"] - 1.05, st["y"] - 1.05, st["t"], 0)
    toy_room(c, stations, paint)


def ice(c, stations):
    """The ice princess's snow globes (Andersen's Snow Queen country) under pink and violet northern lights."""
    W, H = c.W, c.H
    hz = 2.4
    c.vgrad(0, 0, W, hz + 0.3, (128, 118, 214), (240, 216, 246))
    aurora(c, W, 0.5)
    stars = c.layer(0, 0, W, hz)
    rnd = random.Random(6)
    for _ in range(40):
        sparkle(stars, rnd.uniform(0.3, W - 0.3), rnd.uniform(0.15, 1.7), rnd.uniform(0.04, 0.1), fill=(255, 255, 255, 235))
    for _ in range(70):
        stars.circle(rnd.uniform(0.2, W - 0.2), rnd.uniform(0.2, hz - 0.1), rnd.uniform(0.02, 0.045), fill=(255, 255, 255, 210))
    stars.commit()
    hills = [(x, hz - 0.25 - 0.3 * math.sin(x / 2.9 + 1.1) - 0.12 * math.sin(x / 1.1)) for x in [W * i / 120 for i in range(121)]]
    c.poly(hills + [(W, hz + 0.5), (0, hz + 0.5)], fill=(236, 236, 252))
    for x, h in ((3.0, 1.2), (4.1, 0.95), (24.2, 1.15), (25.3, 0.9)):
        c.paste(emoji("evergreen"), x, hz - h / 2 + 0.2, h=h)
    c.paste(emoji("unicorn"), 21.4, hz - 0.3, h=0.85)
    c.vgrad(0, hz - 0.1, W, H, (252, 252, 255), (222, 232, 252), [(0, hz), (W, hz), (W, H), (0, H)])
    lake = [(W / 2 + 4.2 * math.cos(a), 6.25 + 0.95 * math.sin(a)) for a in [2 * math.pi * i / 80 for i in range(80)]]
    c.vgrad(W / 2 - 4.2, 5.3, W / 2 + 4.2, 7.2, (218, 238, 252), (186, 220, 248), lake)
    shine = c.layer(W / 2 - 4.2, 5.3, W / 2 + 4.2, 7.2)
    for dx, dy, w in ((-2.4, -0.2, 1.2), (0.8, 0.3, 1.6), (2.2, -0.35, 0.9)):
        shine.line([(W / 2 + dx, 6.25 + dy), (W / 2 + dx + w, 6.25 + dy - 0.1)], fill=(255, 255, 255, 200), width=0.05, caps=False)
    shine.commit()
    ice_palace(c, W / 2, hz + 0.75, 0.78)
    c.paste(emoji("snowman"), 0.85, 6.85, h=1.15)
    trail(c, stations, "skates")
    for st in stations:
        snow_globe(c, st["x"], st["y"], st["item"]["n"], st["fam"])
        badge(c, st["x"] - 0.95, st["y"] - 1.15, st["t"], st["fam"])
    queen = art.princess(skin=0, style="braid", pose="wand", crown="tiara", seed=8, hair_col=(246, 238, 220), dress_col=(168, 212, 250))
    c.paste(queen, W / 2 - 0.1, 5.2, h=2.5)
    glitter(c, curve((W / 2 + 0.55, 4.2), (W / 2 + 1.6, 3.4), (W / 2 + 0.9, 2.6)), 70, 15, spread=0.15, glints=7)
    for x, y, h, fl in ((W / 2 - 0.95, 7.05, 0.46, False), (W / 2 + 0.95, 7.08, 0.44, True)):
        c.paste(emoji("penguin"), x, y, h=h, flip=fl)


def rapunzel_tower(c, x, base, top):
    stone, edge = (214, 204, 232), (160, 146, 196)
    c.rrect(x - 0.62, top + 0.9, x + 0.62, base, 0.08, fill=stone, outline=edge, width=0.04)
    for k in range(int((base - top - 0.9) / 0.42)):
        y = top + 1.1 + k * 0.42
        c.line([(x - 0.6, y), (x + 0.6, y)], fill=(196, 184, 220), width=0.02, caps=False)
        for bx in ((x - 0.2, x + 0.35) if k % 2 else (x + 0.05,)):
            c.line([(bx, y), (bx, y + 0.42)], fill=(196, 184, 220), width=0.02, caps=False)
    c.poly([(x - 0.85, top + 0.95), (x + 0.85, top + 0.95), (x, top - 0.3)], fill=(206, 160, 236), outline=(150, 110, 200), width=0.035)
    c.line([(x, top - 0.3), (x, top - 0.75)], fill=(150, 130, 160), width=0.03)
    c.poly([(x, top - 0.75), (x + 0.38, top - 0.62), (x, top - 0.5)], fill=(244, 120, 170))
    wy0, wy1 = top + 1.15, top + 1.95
    c.rrect(x - 0.4, wy0, x + 0.4, wy1, 0.4, fill=(255, 246, 222), outline=edge, width=0.04)
    c.paste(art.princess(skin=1, hair=2, dress=1, style="long", pose="wave", crown="crown", seed=4), x, wy0 + 0.95, h=2.3,
            clip=(x - 0.36, wy0 + 0.04, x + 0.36, wy1 - 0.04))
    for k in range(9):
        lx, ly = x + (0.5 if k % 2 else -0.5), base - 0.3 - k * 0.52
        c.ellipse(lx, ly, 0.15, 0.09, fill=(120, 186, 110))
    return (x, wy1 - 0.06)


def braid(c, path):
    """Rapunzel's golden braid along a path: a gold band with two crossing strands."""
    c.line(path, fill=(214, 160, 60), width=0.34, caps=True)
    c.line(path, fill=(244, 196, 90), width=0.26, caps=True)
    pts = along(path, 0.035)
    for sign in (1, -1):
        strand = []
        for i, (x, y, a) in enumerate(pts):
            off = sign * 0.075 * math.sin(i * 0.035 / 0.24 * math.pi)
            strand.append((x - off * math.sin(a), y + off * math.cos(a)))
        c.line(strand, fill=(255, 226, 140), width=0.07, caps=False)


# ------------------------------------------------------------------ scenes

def lagoon(c, stations):
    W, H = c.W, c.H
    hz, sy = 1.75, 4.72                                # horizon, mean shoreline
    c.vgrad(0, 0, W, hz + 0.1, (168, 214, 252), (252, 234, 244))
    rainbow(c, W / 2, hz + 1.9, 3.6, 0.24, opacity=0.55)
    edge = [(W / 2 + 3.65 * math.cos(a), hz + 1.9 + 3.65 * math.sin(a)) for a in [math.pi * (1 + i / 60) for i in range(61)]]
    glitter(c, [p for p in edge if p[1] < hz - 0.1], 70, 31, spread=0.08, glints=5)
    sun(c, 21.2, 0.72, 0.42)
    for x, y, s in ((3.2, 0.7, 0.62), (11.0, 0.5, 0.48), (18.3, 0.62, 0.55)):
        cloud(c, x, y, s)
    c.poly(blob(25.7, hz + 0.05, 2.4, 0.42, 5, wobble=0.05, flat_bottom=True), fill=(176, 214, 170))
    c.paste(emoji("castle"), 25.9, hz - 0.5, h=1.12)
    c.paste(emoji("palm"), 24.0, hz - 0.38, h=0.85)
    shore = [(x, sy + 0.18 * math.sin(x / 2.3) + 0.1 * math.sin(x / 0.9 + 1)) for x in [W * i / 140 for i in range(141)]]
    c.vgrad(0, hz, W, sy + 0.4, (136, 216, 238), (88, 190, 226), [(0, hz), (W, hz)] + shore[::-1])
    lay = c.layer(0, hz, W, sy + 0.4)
    rnd = random.Random(4)
    for _ in range(40):
        x, y = rnd.uniform(0.3, W - 0.3), rnd.uniform(hz + 0.2, sy - 0.3)
        lay.line(wave(x, x + rnd.uniform(0.4, 0.9), y, 0.04, 0.5), fill=(255, 255, 255, 120), width=0.035, caps=False)
    lay.commit()
    c.vgrad(0, sy - 0.35, W, H, (252, 236, 200), (246, 218, 170), shore + [(W, H), (0, H)])
    foam = c.layer(0, sy - 0.5, W, sy + 0.6)
    foam.line(shore, fill=(255, 255, 255, 200), width=0.12, caps=False)
    foam.line([(x, y + 0.13) for x, y in shore], fill=(255, 255, 255, 90), width=0.06, caps=False)
    foam.commit()
    grain = c.layer(0, sy, W, H)
    rnd = random.Random(9)
    for _ in range(260):
        grain.circle(rnd.uniform(0, W), rnd.uniform(sy + 0.3, H - 0.1), 0.018, fill=(210, 170, 120, 120))
    grain.commit()
    rnd = random.Random(2)
    glints = c.layer(0, hz, W, sy)
    for _ in range(30):
        sparkle(glints, rnd.uniform(0.5, W - 0.5), rnd.uniform(hz + 0.2, sy - 0.4), rnd.uniform(0.06, 0.15),
                fill=(255, 255, 255, 235))
    glints.commit()
    # friends: a jumping dolphin with glitter spray, whale, seal, fish
    c.paste(emoji("dolphin"), 8.3, 0.95, h=0.95, flip=True)
    jump = curve((6.9, 1.85), (8.3, -0.2), (9.75, 1.85))
    arc = c.layer(6.5, 0.2, 10.1, 2.0)
    arc.line(jump, fill=(255, 255, 255, 170), width=0.07, caps=False)
    arc.commit()
    glitter(c, jump, 60, 12, spread=0.1, glints=4)
    c.paste(emoji("tropicalfish"), 4.37, 2.55, h=0.45)
    c.paste(emoji("fish"), 20.0, 2.45, h=0.4, flip=True)
    # the mermaid princess on her rock divides the pink half from the blue half
    coral(c, 12.05, sy + 0.2, 1.0, (250, 150, 190))
    rock(c, W / 2, 3.95, 1.65, 0.9, 11)
    c.paste(emoji("seal"), 15.4, 3.62, h=0.85)
    mermaid = art.princess(skin=1, hair=5, dress=0, style="long", pose="wave", crown="tiara", seed=3, tail=(70, 196, 196))
    c.paste(mermaid, W / 2 + 0.05, 2.45, h=2.95)
    glitter(c, curve((W / 2 - 0.6, 3.9), (W / 2 + 0.2, 2.6), (W / 2 + 1.1, 3.75)), 55, 5, spread=0.14, glints=5)
    c.paste(emoji("bubbles"), W / 2 - 1.35, 1.55, h=0.5)
    c.paste(emoji("bubbles"), W / 2 + 1.45, 1.2, h=0.38)
    # the puppy plays on the beach, the sandcastle waits in the corner
    sandcastle(c, 0.95, 7.45, 0.78)
    c.paste(emoji("puppy"), W / 2, 6.95, h=0.95)
    c.paste(emoji("turtle"), 27.45, 7.05, h=0.6, flip=True)
    starfish(c, 26.6, 7.25, 0.22, col=(255, 190, 120), rot=0.5)
    for st in stations:
        if st["y"] < sy:                       # shells in the water sit on a flat stone
            rock(c, st["x"], st["y"] + 1.12, 1.58, 0.36, st["t"], col=(190, 184, 206))
    trail(c, stations, "bubbles")
    for st in stations:
        shell(c, st["x"], st["y"], st["item"]["n"], st["fam"])
        badge(c, st["x"] - 1.5, st["y"] - 0.78, st["t"], st["fam"])



def scatter(n, w, h, d, seed):
    """n points in a w x h box (centred on 0), at least d apart; deterministic."""
    rnd = random.Random(seed * 7919 + n)
    for _ in range(3000):
        pts = []
        for _ in range(n):
            for _ in range(300):
                q = (rnd.uniform(-w / 2, w / 2), rnd.uniform(-h / 2, h / 2))
                if all(math.dist(q, r) >= d for r in pts):
                    pts.append(q)
                    break
        if len(pts) == n:
            return pts
    raise RuntimeError("scatter failed")


def rug(c, cx, cy, n, fam, token, seed, s=1.0):
    """Play rug in slight perspective with n scattered tokens."""
    base = [(255, 222, 236), (214, 232, 252)][fam]
    band = [(240, 140, 186), (110, 160, 230)][fam]
    top, bot, hh = 1.25 * s, 1.5 * s, 0.86 * s
    c.shadow(cx + 0.05, cy + hh + 0.02, bot * 0.98, 0.16 * s, strength=0.2)
    outer = [(cx - top, cy - hh), (cx + top, cy - hh), (cx + bot, cy + hh), (cx - bot, cy + hh)]
    c.poly(rounded(outer, 0.22 * s), fill=band, outline=mix(band, (80, 60, 110), 0.25), width=0.03 * s)
    i = 0.13 * s
    inner = [(cx - top + i, cy - hh + i), (cx + top - i, cy - hh + i), (cx + bot - i * 1.1, cy + hh - i), (cx - bot + i * 1.1, cy + hh - i)]
    c.poly(rounded(inner, 0.14 * s), fill=base)
    stitch = c.layer(cx - bot, cy - hh, cx + bot, cy + hh)
    j = 0.065 * s
    ring = rounded([(cx - top + j, cy - hh + j), (cx + top - j, cy - hh + j), (cx + bot - j * 1.1, cy + hh - j),
                    (cx - bot + j * 1.1, cy + hh - j)], 0.18 * s, steps=8)
    for k in range(0, len(ring), 2):
        stitch.line([ring[k], ring[(k + 1) % len(ring)]], fill=(255, 255, 255, 190), width=0.025 * s, caps=False)
    stitch.commit()
    sp = emoji(token)
    for dx, dy in scatter(n, 1.9 * s, 0.95 * s, 0.68 * s, seed):
        c.paste(sp, cx + dx, cy + dy, box=(0.6 * s, 0.6 * s))


def drawn_castle(c, cx, base, s=1.0):
    wall, wall_d = (255, 228, 238), (230, 176, 202)
    roof, roof_d = (190, 156, 234), (146, 110, 200)
    win = (156, 118, 196)
    for side in (-1, 1):
        tx = cx + side * 1.55 * s
        c.rrect(tx - 0.45 * s, base - 3.05 * s, tx + 0.45 * s, base, 0.04 * s, fill=wall, outline=wall_d, width=0.04 * s)
        c.poly([(tx - 0.62 * s, base - 3.0 * s), (tx + 0.62 * s, base - 3.0 * s), (tx, base - 4.3 * s)],
               fill=roof, outline=roof_d, width=0.035 * s)
        c.line([(tx, base - 4.28 * s), (tx, base - 4.82 * s)], fill=(150, 130, 160), width=0.035 * s)
        c.poly([(tx, base - 4.82 * s), (tx + 0.5 * s, base - 4.66 * s), (tx, base - 4.5 * s)],
               fill=[(244, 120, 170), (110, 160, 230)][side > 0])
        c.rrect(tx - 0.16 * s, base - 2.45 * s, tx + 0.16 * s, base - 1.9 * s, 0.16 * s, fill=win)
    c.rrect(cx - 1.15 * s, base - 2.3 * s, cx + 1.15 * s, base, 0.04 * s, fill=wall, outline=wall_d, width=0.04 * s)
    for k in range(5):
        x = cx - 1.15 * s + (k + 0.5) * 2.3 * s / 5
        c.rrect(x - 0.17 * s, base - 2.58 * s, x + 0.17 * s, base - 2.25 * s, 0.03 * s, fill=wall, outline=wall_d, width=0.035 * s)
    c.poly([(cx - 0.75 * s, base - 2.3 * s), (cx + 0.75 * s, base - 2.3 * s), (cx, base - 3.55 * s)], fill=roof, outline=roof_d, width=0.035 * s)
    c.circle(cx, base - 3.62 * s, 0.11 * s, fill=(255, 210, 90))
    for x in (cx - 0.62 * s, cx + 0.62 * s):
        c.rrect(x - 0.15 * s, base - 1.75 * s, x + 0.15 * s, base - 1.25 * s, 0.15 * s, fill=win)
    c.rrect(cx - 0.45 * s, base - 1.15 * s, cx + 0.45 * s, base + 0.02 * s, 0.45 * s, fill=(132, 96, 170))
    c.rrect(cx - 0.33 * s, base - 1.0 * s, cx + 0.33 * s, base + 0.02 * s, 0.33 * s, fill=(176, 132, 96))
    c.circle(cx, base - 0.36 * s, 0.05 * s, fill=(255, 210, 90))


def hedge(c, x0, x1, y, h, col, seed):
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        r = rnd.uniform(0.35, 0.55) * h
        c.circle(x, y - r * 0.6, r, fill=col)
        x += r * 1.1
    c.rrect(x0 - 0.3, y - h * 0.35, x1 + 0.3, y + 0.05, 0.1, fill=col)


def castle_garden(c, stations):
    W, H = c.W, c.H
    hz = 2.45
    c.vgrad(0, 0, W, hz + 0.3, (176, 214, 252), (248, 232, 250))
    rainbow(c, W / 2, hz + 1.5, 3.4, 0.22, opacity=0.5)
    sun(c, 24.9, 0.75, 0.42)
    for x, y, s in ((3.4, 0.65, 0.6), (9.6, 0.95, 0.45), (19.8, 0.62, 0.55)):
        cloud(c, x, y, s)
    hills = [(x, hz - 0.25 - 0.35 * math.sin(x / 3.1 + 0.6) - 0.18 * math.sin(x / 1.3)) for x in [W * i / 120 for i in range(121)]]
    c.poly(hills + [(W, hz + 0.5), (0, hz + 0.5)], fill=(190, 226, 170))
    c.vgrad(0, hz - 0.1, W, H, (170, 220, 150), (140, 204, 126), [(0, hz), (W, hz), (W, H), (0, H)])
    c.paste(emoji("unicorn"), 8.2, 1.78, h=0.95)            # peeks over the hedge
    hedge(c, 0.2, 11.2, hz + 0.15, 0.9, (110, 180, 110), 3)
    hedge(c, 17.1, W - 0.2, hz + 0.15, 0.9, (110, 180, 110), 4)
    drawn_castle(c, W / 2, hz + 0.9, 0.72)
    tops = [(W / 2 - 1.12, 1.25), (W / 2 + 1.12, 1.25)]
    bunting(c, tops[0][0], tops[1][0], tops[0][1], 0.3, [(255, 160, 196), (150, 196, 245), (255, 222, 130)], flag=0.18)
    for x in (W / 2 - 1.1, W / 2 + 1.1):
        c.paste(emoji("sunflower"), x, 3.0, h=0.7)
    gate = hz + 0.9
    path = [(W / 2 - 0.38 - 1.3 * t + 0.25 * math.sin(t * 5), gate + (H - gate) * t) for t in [i / 20 for i in range(21)]]
    back = [(W / 2 + 0.38 + 1.3 * t - 0.25 * math.sin(t * 5), gate + (H - gate) * t) for t in [i / 20 for i in range(20, -1, -1)]]
    c.poly(path + back, fill=(246, 176, 204))
    for side in (path, back):
        c.line(side, fill=(238, 196, 96), width=0.07, caps=False)
    grass = c.layer(0, hz, W, H)
    rnd = random.Random(5)
    for _ in range(170):
        x, y = rnd.uniform(0.2, W - 0.2), rnd.uniform(hz + 0.5, H - 0.1)
        if abs(x - W / 2) < 1.9:
            continue
        grass.line([(x, y), (x - 0.05, y - 0.16)], fill=(96, 170, 96, 150), width=0.025, caps=False)
        grass.line([(x + 0.06, y), (x + 0.09, y - 0.13)], fill=(96, 170, 96, 150), width=0.025, caps=False)
    for _ in range(40):
        x, y = rnd.uniform(0.3, W - 0.3), rnd.uniform(hz + 0.6, H - 0.2)
        if abs(x - W / 2) < 1.9:
            continue
        col = rnd.choice([(255, 255, 255), (255, 214, 232), (255, 236, 150)])
        for a in range(5):
            grass.circle(x + 0.06 * math.cos(a * 1.2566), y + 0.06 * math.sin(a * 1.2566), 0.045, fill=alpha(col, 0.95))
        grass.circle(x, y, 0.035, fill=(250, 200, 80, 255))
    grass.commit()
    c.paste(emoji("rose"), 16.75, 3.2, h=0.75)
    pumpkin_coach(c, 12.05, 3.25, 0.9)
    for x, y in ((11.15, 3.25), (12.85, 3.25)):
        c.paste(emoji("mouse"), x, y, h=0.34)
    trail(c, stations, "paws")
    for st in stations:
        rug(c, st["x"], st["y"], st["item"]["n"], st["fam"], st["item"]["kind"], st["t"])
        badge(c, st["x"] - 1.45, st["y"] - 0.82, st["t"], st["fam"])
    c.paste(art.princess_variant(4, "wave"), W / 2, 5.05, h=2.25)
    glass_slipper(c, W / 2 + 0.05, 6.95, 0.75)
    glitter(c, curve((W / 2 + 0.55, 4.05), (W / 2 + 0.9, 3.2), (W / 2 + 0.05, 2.75)), 50, 8, spread=0.12, glints=5)
    for x, y, h, flip in ((12.3, 4.6, 1.0, False), (0.75, 5.35, 0.9, False)):
        c.paste(emoji("catfull"), x, y, h=h, flip=flip)
    for x, y, h, flip in ((16.0, 4.6, 0.95, True), (27.55, 5.35, 0.9, True)):
        c.paste(emoji("puppy"), x, y, h=h, flip=flip)
    c.paste(emoji("pinkheart"), 12.6, 3.85, h=0.32)
    c.paste(emoji("lightblueheart"), 15.7, 3.9, h=0.32)
    c.paste(emoji("butterfly"), 8.4, 0.95, h=0.5)
    c.paste(emoji("butterfly"), 20.6, 1.85, h=0.45)
    bush(c, 0.55, H + 0.05, 1.3, 0.9, [(255, 150, 190), (255, 255, 255), (250, 110, 150)], 1)
    bush(c, W - 0.55, H + 0.05, 1.3, 0.9, [(150, 196, 245), (255, 255, 255), (200, 170, 245)], 2)
    for x, y, r in ((12.4, 0.9, 0.16), (15.95, 0.65, 0.13), (13.0, 2.0, 0.1), (15.4, 1.75, 0.11)):
        sparkle(c, x, y, r, fill=(255, 214, 90))



def halo(c, cx, cy, fam, rx=1.22, ry=1.05):
    """Soft family-coloured spot that marks a picture as a task."""
    fill = [(255, 205, 226), (200, 224, 252)][fam]
    ring = [(236, 112, 170), (88, 150, 222)][fam]
    lay = c.layer(cx - rx - 0.4, cy - ry - 0.4, cx + rx + 0.4, cy + ry + 0.4)
    lay.ellipse(cx, cy, rx, ry, fill=alpha(fill, 0.85))
    lay.commit(blur=0.08)
    lay = c.layer(cx - rx - 0.1, cy - ry - 0.1, cx + rx + 0.1, cy + ry + 0.1)
    lay.ellipse(cx, cy, rx, ry, outline=alpha(ring, 0.75), width=0.045)
    lay.commit()


def bunting(c, x0, x1, y, sag, cols, flag=0.42):
    pts = [(x0 + (x1 - x0) * t, y + sag * 4 * t * (1 - t)) for t in [i / 40 for i in range(41)]]
    c.line(pts, fill=(170, 150, 170), width=0.025)
    n = max(2, int((x1 - x0) / (flag * 1.65)))
    for k in range(n):
        t = (k + 0.5) / n
        x = x0 + (x1 - x0) * t
        yy = y + sag * 4 * t * (1 - t)
        c.poly([(x - flag * 0.52, yy), (x + flag * 0.52, yy), (x, yy + flag)], fill=cols[k % len(cols)])
    return pts


def garden(c, stations):
    W, H = c.W, c.H
    hz = 2.3
    c.vgrad(0, 0, W, hz + 0.3, (184, 222, 252), (252, 244, 234))
    for x, y, s in ((3.0, 0.75, 0.55), (11.6, 0.55, 0.45), (19.6, 0.9, 0.5)):
        cloud(c, x, y, s)
    hills = [(x, hz - 0.2 - 0.3 * math.sin(x / 2.7 + 1.4) - 0.15 * math.sin(x / 1.1)) for x in [W * i / 120 for i in range(121)]]
    c.poly(hills + [(W, hz + 0.5), (0, hz + 0.5)], fill=(196, 228, 176))
    c.vgrad(0, hz - 0.1, W, H, (176, 222, 156), (146, 206, 130), [(0, hz), (W, hz), (W, H), (0, H)])
    c.paste(emoji("tree"), 0.9, hz - 0.8 + 0.35, h=1.6)
    grass = c.layer(0, hz, W, H)
    rnd = random.Random(8)
    for _ in range(170):
        x, y = rnd.uniform(0.2, W - 0.2), rnd.uniform(hz + 0.4, H - 0.1)
        grass.line([(x, y), (x - 0.05, y - 0.16)], fill=(96, 170, 96, 150), width=0.025, caps=False)
        grass.line([(x + 0.06, y), (x + 0.09, y - 0.13)], fill=(96, 170, 96, 150), width=0.025, caps=False)
    grass.commit()
    for pts in (bunting(c, 0.3, 12.0, 0.15, 0.55, [(255, 160, 196), (196, 170, 240), (255, 222, 130)]),
                bunting(c, 16.3, 24.4, 0.15, 0.45, [(150, 196, 245), (196, 170, 240), (255, 222, 130)])):
        fairy_lights(c, pts)
    for x, y, nm in ((0.7, 4.7, "tulip"), (27.7, 4.6, "rose")):
        c.paste(emoji(nm), x, y, h=0.7)
    # the princess hosts under her rose arch
    rose_arch(c, W / 2 + 0.1, 6.15, 2.8, 3.7, 4)
    for x in (12.85,):                            # a flower pot at the arch foot
        c.poly([(x - 0.26, 6.05), (x + 0.26, 6.05), (x + 0.19, 6.5), (x - 0.19, 6.5)], fill=(240, 160, 196),
               outline=(214, 112, 160), width=0.02)
        c.paste(emoji("tulip"), x, 5.72, h=0.62)
    c.ellipse(14.85, 5.05, 0.75, 0.24, fill=(255, 255, 255), outline=(230, 200, 220), width=0.03)
    c.rrect(14.8, 5.05, 14.9, 6.2, 0.03, fill=(200, 170, 200))
    c.paste(emoji("teapot"), 14.7, 4.78, h=0.5)
    c.rrect(15.15, 4.83, 15.35, 5.0, 0.04, fill=(255, 255, 255), outline=(236, 150, 186), width=0.02)
    c.paste(emoji("book"), 14.3, 4.88, h=0.3)
    c.paste(art.princess_variant(9, "wave"), 13.6, 4.75, h=2.45)
    for bx, by, h in ((12.45, 2.35, 0.8), (12.95, 2.05, 0.7)):
        c.line([(bx, by + h * 0.5), (12.85, 3.6)], fill=(170, 160, 180), width=0.015, caps=False)
        c.paste(emoji("balloon"), bx, by, h=h)
    glitter(c, curve((14.0, 3.7), (14.6, 2.9), (15.3, 3.35)), 45, 9, spread=0.12, glints=4)
    c.paste(emoji("butterfly"), 8.3, 1.75, h=0.45)
    c.paste(emoji("butterfly"), 20.4, 1.6, h=0.4)
    bush(c, 0.6, H + 0.05, 1.4, 0.95, [(255, 150, 190), (255, 255, 255), (250, 110, 150)], 5)
    bush(c, W - 0.6, H + 0.05, 1.4, 0.95, [(150, 196, 245), (255, 255, 255), (200, 170, 245)], 6)
    trail(c, stations, "stones", last=11)
    order = sorted(stations, key=lambda st: st["t"])
    glitter(c, curve((order[10]["x"], order[10]["y"]), (order[10]["x"] + 0.6, (order[10]["y"] + order[11]["y"]) / 2 + 0.6),
                     (order[11]["x"], order[11]["y"])), 70, 3, spread=0.1, glints=6)
    for st in stations:
        halo(c, st["x"], st["y"], st["fam"])
        c.paste(emoji(st["item"]["pic"]), st["x"], st["y"], box=(1.75, 1.75))
        badge(c, st["x"] - 1.25, st["y"] - 0.85, st["t"], st["fam"])



def hot_air_balloon(c, cx, cy, s=1.0):
    cols = [(255, 160, 196), (255, 226, 130), (150, 206, 246), (196, 170, 240)]
    for k in range(4):
        x0 = cx - 0.62 * s + k * 0.31 * s
        c.ellipse(cx, cy, 0.62 * s, 0.72 * s, fill=cols[0]) if k == 0 else None
        lay = c.layer(x0, cy - 0.8 * s, x0 + 0.31 * s, cy + 0.8 * s)
        lay.ellipse(cx, cy, 0.62 * s, 0.72 * s, fill=alpha(cols[k], 1))
        lay.commit()
    for dx in (-0.28, 0.28):
        c.line([(cx + dx * s, cy + 0.6 * s), (cx + dx * 0.55 * s, cy + 1.0 * s)], fill=(150, 120, 100), width=0.02 * s, caps=False)
    c.rrect(cx - 0.18 * s, cy + 0.98 * s, cx + 0.18 * s, cy + 1.22 * s, 0.04 * s, fill=(196, 150, 104))


def cottage(c, x, base, w, h, wall, roof, seed):
    rnd = random.Random(seed)
    edge = mix(wall, (90, 60, 110), 0.3)
    c.rrect(x - w / 2, base - h, x + w / 2, base, 0.05, fill=wall, outline=edge, width=0.03)
    c.poly([(x - w / 2 - 0.15, base - h + 0.02), (x + w / 2 + 0.15, base - h + 0.02), (x, base - h - w * 0.55)],
           fill=roof, outline=mix(roof, (80, 50, 100), 0.3), width=0.03)
    c.rrect(x + w * 0.18, base - h - w * 0.5, x + w * 0.32, base - h - w * 0.2, 0.02, fill=mix(roof, (90, 60, 110), 0.2))
    for dx in (-0.25, 0.25):
        wx, wy = x + dx * w, base - h * 0.62
        c.rrect(wx - 0.17, wy - 0.17, wx + 0.17, wy + 0.17, 0.05, fill=(255, 248, 222), outline=edge, width=0.025)
        for k in range(3):
            c.circle(wx - 0.12 + k * 0.12, wy + 0.24, 0.05, fill=rnd.choice([(244, 120, 170), (255, 200, 90), (190, 150, 240)]))
    c.rrect(x - 0.17, base - 0.62, x + 0.17, base, 0.17, fill=mix(roof, (90, 60, 110), 0.15))


def market_stall(c, cx, base, w=3.0):
    """Flower stall with a striped awning."""
    wood = (226, 190, 150)
    for x in (cx - w / 2 + 0.12, cx + w / 2 - 0.12):
        c.rrect(x - 0.06, base - 2.2, x + 0.06, base, 0.02, fill=wood)
    c.rrect(cx - w / 2, base - 0.85, cx + w / 2, base - 0.15, 0.06, fill=(244, 214, 180), outline=(206, 160, 120), width=0.03)
    n = 8
    for k in range(n):
        x0 = cx - w / 2 - 0.1 + k * (w + 0.2) / n
        col = (244, 140, 186) if k % 2 == 0 else (255, 255, 255)
        c.poly([(x0, base - 2.45), (x0 + (w + 0.2) / n, base - 2.45), (x0 + (w + 0.2) / n, base - 1.95), (x0, base - 1.95)], fill=col)
        c.ellipse(x0 + (w + 0.2) / (2 * n), base - 1.95, (w + 0.2) / (2 * n), 0.14, fill=col)
    c.rrect(cx - w / 2 - 0.1, base - 2.55, cx + w / 2 + 0.1, base - 2.42, 0.04, fill=(226, 110, 160))
    for k, nm in enumerate(("tulip", "rose", "tulip", "rose", "tulip")):
        c.paste(emoji(nm), cx - w / 2 + 0.4 + k * (w - 0.8) / 4, base - 1.0, h=0.5)


def village(c, stations):
    """Market day in the village: twelve things to name and read, each on a family-coloured halo."""
    W, H = c.W, c.H
    hz = 2.5
    c.vgrad(0, 0, W, hz + 0.3, (186, 222, 252), (252, 244, 236))
    for x, y, s in ((4.2, 0.55, 0.5), (12.4, 0.45, 0.42), (19.8, 0.6, 0.48)):
        cloud(c, x, y, s)
    hills = [(x, hz - 0.3 - 0.3 * math.sin(x / 2.6 + 0.8) - 0.12 * math.sin(x / 1.1)) for x in [W * i / 120 for i in range(121)]]
    c.poly(hills + [(W, hz + 0.5), (0, hz + 0.5)], fill=(200, 230, 182))
    walls = [(255, 214, 230), (226, 214, 250), (206, 238, 220), (255, 226, 200), (210, 230, 252), (255, 236, 196), (240, 208, 240)]
    roofs = [(226, 120, 160), (150, 120, 210), (110, 180, 150), (230, 140, 100), (110, 150, 220), (220, 170, 90), (190, 110, 190)]
    tops = []
    for k, x in enumerate((1.2, 4.0, 7.2, 10.4, 17.9, 21.0, 23.9)):
        h = 1.25 + 0.25 * (k % 3)
        cottage(c, x, hz + 0.35, 1.7, h, walls[k], roofs[k], k)
        tops.append((x, hz + 0.35 - h - 0.95))
    for a, b in zip(tops, tops[1:]):
        if b[0] - a[0] < 5:
            fairy_lights(c, bunting(c, a[0] + 0.3, b[0] - 0.3, a[1] + 0.25, 0.35,
                                    [(255, 160, 196), (196, 170, 240), (150, 196, 245), (255, 222, 130)], flag=0.24))
    c.vgrad(0, hz - 0.1, W, H, (182, 224, 160), (152, 208, 134), [(0, hz), (W, hz), (W, H), (0, H)])
    grass = c.layer(0, hz, W, H)
    rnd = random.Random(13)
    for _ in range(160):
        x, y = rnd.uniform(0.2, W - 0.2), rnd.uniform(hz + 0.3, H - 0.1)
        grass.line([(x, y), (x - 0.05, y - 0.16)], fill=(96, 170, 96, 150), width=0.025, caps=False)
        grass.line([(x + 0.06, y), (x + 0.09, y - 0.13)], fill=(96, 170, 96, 150), width=0.025, caps=False)
    grass.commit()
    market_stall(c, W / 2, 5.35, 3.0)
    trail(c, stations, "stones", last=11)
    order = sorted(stations, key=lambda st: st["t"])
    glitter(c, curve((order[10]["x"], order[10]["y"]), (order[10]["x"] + 0.6, (order[10]["y"] + order[11]["y"]) / 2 + 0.6),
                     (order[11]["x"], order[11]["y"])), 70, 31, spread=0.1, glints=6)
    for st in stations:
        halo(c, st["x"], st["y"], st["fam"])
        c.paste(emoji(st["item"]["pic"]), st["x"], st["y"], box=(1.7, 1.7))
        badge(c, st["x"] - 1.25, st["y"] - 0.85, st["t"], st["fam"])
    c.paste(art.princess_variant(3, "wave"), W / 2 - 0.5, 5.75, h=2.3)
    c.paste(emoji("puppy"), W / 2 + 0.85, 6.6, h=0.85, flip=True)
    glitter(c, curve((W / 2 - 0.1, 4.6), (W / 2 + 0.7, 3.9), (W / 2 + 0.3, 3.3)), 40, 33, spread=0.12, glints=4)
    c.paste(emoji("butterfly"), 8.6, 2.05, h=0.42)
    c.paste(emoji("butterfly"), 20.0, 2.2, h=0.38)
    bush(c, 0.6, H + 0.05, 1.4, 0.95, [(255, 150, 190), (255, 255, 255), (250, 110, 150)], 15)
    bush(c, W - 0.6, H + 0.05, 1.4, 0.95, [(150, 196, 245), (255, 255, 255), (200, 170, 245)], 16)


def sky_train(c, stations):
    """Hanging rainbow train with 12 windows on a diagonal, after the Wuppertal Schwebebahn, at sunset."""
    W, H = c.W, c.H
    c.vgrad(0, 0, W, 4.4, (176, 186, 246), (255, 214, 206))
    c.vgrad(0, 4.2, W, H, (255, 214, 206), (255, 232, 210))
    sun(c, 2.1, 1.25, 0.55, col=(255, 186, 130), core=(255, 214, 160), ray=(255, 170, 120, 120))
    pink = (255, 214, 214, 235)
    for x, y, s in ((6.2, 0.7, 0.5), (12.2, 0.45, 0.42)):
        cloud(c, x, y, s, fill=(255, 246, 244, 240), tint=pink)
    hot_air_balloon(c, 9.2, 0.95, 0.85)
    for x, y, s in ((15.3, 0.5, 0.16), (15.8, 0.75, 0.12), (16.4, 0.45, 0.14), (4.8, 1.85, 0.12)):
        c.line([(x - s, y - s * 0.5), (x, y), (x + s, y - s * 0.5)], fill=(120, 100, 150), width=0.03, caps=True)
    phi = math.radians(4.4)
    cxt, cyt, TW, TH = W / 2, 3.85, 27.0, 3.9

    def to_main(lx, ly):
        dx, dy = lx - TW / 2, ly - TH / 2
        return cxt + dx * math.cos(phi) + dy * math.sin(phi), cyt - dx * math.sin(phi) + dy * math.cos(phi)
    hills = [(x, 5.6 - 0.9 * x / W - 0.25 * math.sin(x / 2.2)) for x in [W * i / 100 for i in range(101)]]
    c.poly(hills + [(W, H), (0, H)], fill=(196, 214, 170))
    river = [(x, 6.85 - 0.25 * x / W + 0.12 * math.sin(x / 1.7)) for x in [W * i / 100 for i in range(101)]]
    c.vgrad(0, 6.4, W, H, (214, 198, 236), (160, 186, 236), river + [(W, H), (0, H)])
    waves = c.layer(0, 6.3, W, H)
    rnd = random.Random(3)
    for _ in range(26):
        x, y = rnd.uniform(0.3, W - 0.3), rnd.uniform(7.0, H - 0.15)
        waves.line(wave(x, x + rnd.uniform(0.4, 0.8), y, 0.03, 0.45), fill=(255, 236, 220, 160), width=0.03, caps=False)
    for _ in range(14):
        sparkle(waves, rnd.uniform(0.5, W - 0.5), rnd.uniform(6.95, H - 0.15), rnd.uniform(0.05, 0.1), fill=(255, 246, 210, 230))
    waves.commit()
    c.paste(emoji("swan"), 7.6, 7.05, h=0.7)
    for x, h in ((17.6, 1.1), (19.2, 1.3), (21.0, 1.05), (23.3, 1.25)):
        c.paste(emoji("tree"), x, 5.55 - h / 2, h=h)
    c.paste(emoji("castle"), 25.7, 4.95, h=1.05)
    r0, r1 = to_main(-4, 0.06), to_main(TW + 4, 0.06)

    def rail_y(x):
        return r0[1] + (r1[1] - r0[1]) * (x - r0[0]) / (r1[0] - r0[0])
    for px in (1.6, 13.3, 24.4):
        top, foot = rail_y(px), 7.3
        for dx in (-1.0, 1.0):
            c.line([(px, top), (px + dx, foot)], fill=(118, 196, 160), width=0.12)
        for k in range(1, 5):
            y = top + (foot - top) * k / 5
            w = (y - top) / (foot - top)
            c.line([(px - w, y), (px + w, y)], fill=(140, 208, 176), width=0.05)
        c.line([(px - 1.0, foot), (px + 1.0, foot)], fill=(118, 196, 160), width=0.1)
    for k, col in enumerate([(255, 160, 196), (255, 214, 120), (150, 206, 246)]):
        off = (k - 1) * 0.09
        c.line([(r0[0], r0[1] + off), (r1[0], r1[1] + off)], fill=col, width=0.1, caps=False)
    T = Canvas(TW, TH, dpi=c.dpi, bg=(0, 0, 0, 0))
    top, bot, win, gap = 1.05, 3.55, 1.84, 0.16
    length = 6 * win + 7 * gap
    wagons = [(0.2, 0.2 + length, 0), (0.5 + length, 0.5 + 2 * length, 1)]
    for a, b, fam in wagons:
        for x in (a + 2.0, b - 2.0):
            T.line([(x, 0.45), (x, top + 0.1)], fill=(150, 150, 170), width=0.12, caps=False)
            T.rrect(x - 0.5, 0.18, x + 0.5, 0.52, 0.08, fill=(176, 176, 196))
            for dx in (-0.26, 0.26):
                T.circle(x + dx, 0.14, 0.13, fill=(120, 120, 140))
        body = [(255, 222, 236), (214, 232, 252)][fam]
        stripe = [(240, 140, 186), (110, 160, 230)][fam]
        T.rrect(a, top, b, bot, 0.45, fill=body, outline=mix(body, (90, 70, 110), 0.3), width=0.04)
        T.rrect(a + 0.25, top - 0.1, b - 0.25, top + 0.16, 0.08, fill=mix(body, (255, 255, 255), 0.5),
                outline=mix(body, (90, 70, 110), 0.25), width=0.03)
        T.rrect(a + 0.1, bot - 0.42, b - 0.1, bot - 0.2, 0.1, fill=stripe)
        for k in range(8):
            x = a + 0.45 + k * (b - a - 0.9) / 7
            T.circle(x, bot - 0.31, 0.05, fill=(255, 236, 150))
    # the locomotive: the princess drives behind the front window
    la, lb = 0.8 + 2 * length, TW - 0.1
    gold, edge = (255, 224, 140), (214, 170, 80)
    x = la + 0.85
    T.line([(x, 0.45), (x, top + 0.1)], fill=(150, 150, 170), width=0.12, caps=False)
    T.rrect(x - 0.45, 0.18, x + 0.45, 0.52, 0.08, fill=(176, 176, 196))
    T.rrect(la, top - 0.05, lb, bot, 0.55, fill=gold, outline=edge, width=0.05)
    wbox = (la + 0.22, top + 0.22, lb - 0.3, top + 1.45)
    T.rrect(*wbox, 0.2, fill=(255, 244, 216), outline=edge, width=0.05)
    T.paste(art.princess_variant(2, "wave"), (wbox[0] + wbox[2]) / 2, top + 1.62, h=2.6,
            clip=(wbox[0] + 0.05, wbox[1] + 0.05, wbox[2] - 0.05, wbox[3] - 0.03))
    T.rrect(la, bot - 0.42, lb, bot - 0.2, 0.1, fill=(255, 190, 110))
    T.circle(lb - 0.18, top + 1.85, 0.15, fill=(255, 250, 220), outline=edge, width=0.03)
    T.paste(emoji("pinkheart"), (la + lb) / 2 - 0.1, top + 1.85, h=0.38)
    windows = []
    for a, b, fam in wagons:
        for i in range(6):
            windows.append((a + gap + win / 2 + i * (win + gap), (top + bot) / 2 - 0.12, fam))
    order = sorted(stations, key=lambda st: st["t"])
    for (wx, wy, fam), st in zip(windows, order):
        train_window(T, wx, wy, st["item"]["n"], st["fam"], st["item"]["kind"], glow=True)
    turned = T.img.rotate(math.degrees(phi), resample=Image.BICUBIC, expand=True)
    X, Y = c.p(cxt, cyt)
    c.img.alpha_composite(turned, (round(X - turned.width / 2), round(Y - turned.height / 2)))
    hx, hy = to_main(lb + 0.25, 1.4)
    for k, (dx, dy, h) in enumerate(((0.35, -0.5, 0.36), (0.8, -0.95, 0.3), (0.55, -1.35, 0.24))):
        c.paste(emoji("pinkheart" if k % 2 == 0 else "lightblueheart"), min(hx + dx, W - 0.3), hy + dy, h=h)
    glitter(c, [to_main(lb - 0.3, 1.2), to_main(lb + 1.4, 0.2)], 36, 4, spread=0.14, glints=4)
    for (wx, wy, fam), st in zip(windows, order):
        bx, by = to_main(wx - 0.82, wy - 0.66)
        badge(c, bx, by, st["t"], st["fam"])


def meadow(c, stations):
    """Rapunzel's meadow (Grimm): her golden braid runs from the tower window past the flowers in number order."""
    W, H = c.W, c.H
    hz = 1.9
    c.vgrad(0, 0, W, hz + 0.3, (180, 220, 252), (250, 240, 246))
    sun(c, 24.4, 0.85, 0.45)
    for x, y, s in ((4.6, 0.65, 0.55), (15.5, 0.55, 0.5), (20.6, 0.8, 0.45)):
        cloud(c, x, y, s)
    hills = [(x, hz - 0.2 - 0.35 * math.sin(x / 3.3 + 0.3) - 0.15 * math.sin(x / 1.2)) for x in [W * i / 120 for i in range(121)]]
    c.poly(hills + [(W, hz + 0.5), (0, hz + 0.5)], fill=(196, 230, 176))
    c.paste(emoji("castle"), 13.8, hz - 0.45, h=0.95)
    c.paste(emoji("horse"), 9.2, hz - 0.35, h=0.95)
    c.paste(emoji("unicorn"), 22.3, hz - 0.3, h=0.8)
    c.paste(emoji("rabbit"), 17.3, hz - 0.35, h=0.7)
    c.vgrad(0, hz - 0.1, W, H, (182, 226, 160), (150, 210, 132), [(0, hz), (W, hz), (W, H), (0, H)])
    grass = c.layer(0, hz, W, H)
    rnd = random.Random(11)
    for _ in range(180):
        x, y = rnd.uniform(0.2, W - 0.2), rnd.uniform(hz + 0.3, H - 0.1)
        grass.line([(x, y), (x - 0.05, y - 0.16)], fill=(96, 170, 96, 150), width=0.025, caps=False)
        grass.line([(x + 0.06, y), (x + 0.09, y - 0.13)], fill=(96, 170, 96, 150), width=0.025, caps=False)
    grass.commit()
    window = rapunzel_tower(c, 0.95, H + 0.05, 0.45)
    order = sorted(stations, key=lambda st: st["t"])
    for st in order:                                   # stems and leaves
        x, y = st["x"], st["y"]
        c.line([(x, y + 1.0), (x + 0.05, y + 1.75)], fill=(96, 170, 96), width=0.1)
        c.ellipse(x - 0.28, y + 1.45, 0.26, 0.11, fill=(110, 186, 104))
        c.ellipse(x + 0.32, y + 1.3, 0.24, 0.1, fill=(110, 186, 104))
    end = (order[-1]["x"] + 1.1, order[-1]["y"] + 1.0)
    braid(c, catmull([window, (1.75, 3.0)] + [(st["x"], st["y"]) for st in order] + [end]))
    c.paste(emoji("ribbon"), end[0], end[1], h=0.45)
    for i, st in enumerate(order):
        flower(c, st["x"], st["y"], st["item"]["n"], st["item"]["kind"], PETALS[i % 4])
        badge(c, st["x"] - 1.3, st["y"] - 1.0, st["t"], 0)
    c.paste(emoji("fairy"), 5.15, 1.1, h=0.9, flip=True)
    glitter(c, curve((4.7, 1.35), (6.4, 0.9), (8.6, 1.2)), 50, 27, spread=0.12, glints=5)
    c.paste(emoji("puppy"), 2.15, 7.05, h=0.85, flip=True)
    c.paste(emoji("catfull"), 27.7, 1.45, h=0.75, flip=True)
    c.paste(emoji("bird"), 11.6, 1.2, h=0.5)


def arc_points(n, cx, cy, rx, ry, a0, a1):
    """n points evenly spaced by arc length on an ellipse from angle a0 to a1 (degrees)."""
    fine = [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / 2000)),
             cy - ry * math.sin(math.radians(a0 + (a1 - a0) * i / 2000))) for i in range(2001)]
    acc = [0.0]
    for p, q in zip(fine, fine[1:]):
        acc.append(acc[-1] + math.dist(p, q))
    out, j = [], 0
    for k in range(n):
        target = acc[-1] * k / (n - 1)
        while acc[j] < target:
            j += 1
        out.append(fine[j])
    return out


BALLOON_ARC = arc_points(12, 14.15, 6.95, 12.75, 4.65, 168, 12)


def balloons(c, stations):
    W, H = c.W, c.H
    c.vgrad(0, 0, W, H, (186, 222, 252), (252, 238, 246))
    for x, y, s in ((3.4, 1.2, 0.5), (24.9, 1.1, 0.55), (14.2, 0.45, 0.4)):
        cloud(c, x, y, s)
    hill = [(x, 6.6 - 1.6 * math.exp(-((x - W / 2) / 4.2) ** 2) + 0.1 * math.sin(x / 1.7)) for x in [W * i / 120 for i in range(121)]]
    c.poly(hill + [(W, H), (0, H)], fill=(176, 222, 156))
    c.paste(emoji("castle"), 4.4, 6.0, h=1.0)
    for x in (20.8, 22.3):
        c.paste(emoji("tree"), x, 5.95, h=1.05)
    hand = (W / 2 + 0.42, 4.45)
    order = sorted(stations, key=lambda st: st["t"])
    for st in order:
        knot = (st["x"], st["y"] + 1.25)
        mid = ((knot[0] + hand[0]) / 2, (knot[1] + hand[1]) / 2 + 0.6)
        c.line(curve(knot, mid, hand, 24), fill=(170, 160, 186), width=0.018, caps=False)
    c.paste(art.princess_variant(5, "up"), W / 2, 5.55, h=2.4)
    c.paste(emoji("ribbon"), hand[0], hand[1] + 0.05, h=0.4)
    c.paste(emoji("catfull"), W / 2 - 1.3, 6.6, h=0.85)
    c.paste(emoji("puppy"), W / 2 + 1.3, 6.6, h=0.85, flip=True)
    for x, y, nm in ((W / 2 - 1.3, 5.75, "pinkheart"), (W / 2 + 1.3, 5.75, "lightblueheart")):
        c.paste(emoji(nm), x, y, h=0.3)
    for st in order:
        balloon(c, st["x"], st["y"], st["item"], st["fam"])
        side = -1 if st["x"] < W / 2 else 1
        badge(c, st["x"] + side * 0.95, st["y"] - 0.92, st["t"], st["fam"])
    glitter(c, [(p[0], p[1] - 1.5) for p in BALLOON_ARC[3:9]], 80, 17, spread=0.22, glints=8)
    bush(c, 0.55, H + 0.05, 1.3, 0.9, [(255, 150, 190), (255, 255, 255), (250, 110, 150)], 9)
    bush(c, W - 0.55, H + 0.05, 1.3, 0.9, [(150, 196, 245), (255, 255, 255), (200, 170, 245)], 10)


SCENES = {
    "lagoon": {"paint": lagoon, "size": (28.3, 7.6),
               "spots": [(1.95, 2.95), (3.95, 6.1), (5.95, 3.3), (7.95, 6.25), (9.95, 2.9), (11.55, 6.05),
                         (16.75, 6.05), (18.35, 2.9), (20.35, 6.25), (22.35, 3.3), (24.35, 6.1), (26.35, 2.95)]},
    "castle": {"paint": castle_garden, "size": (28.3, 7.6),
               "spots": [(1.95, 3.55), (3.95, 6.35), (5.95, 3.35), (7.95, 6.4), (9.95, 3.6), (11.1, 6.3),
                         (17.2, 6.3), (18.35, 3.6), (20.35, 6.4), (22.35, 3.35), (24.35, 6.35), (26.35, 3.55)]},
    "garden": {"paint": garden, "size": (28.3, 7.6),
               "spots": [(1.9, 3.3), (3.85, 6.25), (5.85, 3.35), (7.85, 6.3), (9.75, 3.3), (11.0, 6.25),
                         (17.3, 6.3), (18.55, 3.35), (20.45, 6.3), (22.4, 3.3), (24.4, 6.25), (26.35, 1.55)]},
    "train": {"paint": sky_train, "size": (28.3, 7.6), "spots": [(0.0, 0.0)] * 12},
    "meadow": {"paint": meadow, "size": (28.3, 7.6),
               "spots": [(3.0 + i * 2.155, 2.9 if i % 2 == 0 else 5.9) for i in range(12)]},
    "ice": {"paint": ice, "size": (28.3, 7.6),
            "spots": [(1.95, 3.0), (3.95, 6.1), (5.95, 3.15), (7.95, 6.2), (9.95, 3.0), (11.5, 6.0),
                      (16.8, 6.0), (18.35, 3.0), (20.35, 6.2), (22.35, 3.15), (24.35, 6.1), (26.35, 3.0)]},
    "towers": {"paint": toys_towers, "size": (28.3, 7.6),
               "spots": [(1.95, 3.95), (3.95, 6.95), (5.95, 3.95), (7.95, 6.95), (9.95, 3.95), (11.4, 6.95),
                         (16.9, 6.95), (18.35, 3.95), (20.35, 6.95), (22.35, 3.95), (24.35, 6.95), (26.35, 3.95)]},
    "village": {"paint": village, "size": (28.3, 7.6),
                "spots": [(1.9, 3.75), (3.85, 6.3), (5.85, 3.8), (7.85, 6.35), (9.75, 3.75), (11.0, 6.3),
                          (17.3, 6.3), (18.55, 3.8), (20.45, 6.35), (22.4, 3.8), (24.4, 6.3), (26.35, 1.55)]},
    "blocks": {"paint": toys_blocks, "size": (28.3, 7.6),
               "spots": [(1.95, 3.25), (3.95, 6.1), (5.95, 3.35), (7.95, 6.15), (9.95, 3.25), (11.45, 6.05),
                         (16.85, 6.05), (18.35, 3.25), (20.35, 6.15), (22.35, 3.35), (24.35, 6.1), (26.35, 3.25)]},
    "balloons": {"paint": balloons, "size": (28.3, 7.6), "spots": BALLOON_ARC},
}
def station(name, item, dpi=300):
    """One task station without its badge, for the worked examples; None where the plain picture is the task."""
    fam = item.get("fam") or 0
    c = Canvas(3.6, 3.0, dpi=dpi, bg=(0, 0, 0, 0))
    if name == "lagoon":
        shell(c, 1.8, 1.3, item["n"], fam)
    elif name == "castle":
        rug(c, 1.8, 1.4, item["n"], fam, item["kind"], item.get("seed", 1))
    elif name == "train":
        train_window(c, 1.8, 1.5, item["n"], fam, item["kind"])
    elif name == "meadow":
        flower(c, 1.8, 1.5, item["n"], item["kind"], PETALS[0])
    elif name == "balloons":
        balloon(c, 1.8, 1.4, item, fam)
    elif name == "ice":
        snow_globe(c, 1.8, 1.45, item["n"], fam)
    elif name == "towers":                  # the worked example uses the answer scale, so one more looks taller
        return None
    elif name == "blocks":
        letter_block(c, 1.7, 1.6, chr(65 + item["n"]), BLOCK_COLS[1])
    else:
        return None
    return c.image(radius=None)


CHECKS = {"lagoon": (("pearl",), 6), "castle": (("yarn", "bone"), 6), "train": (("cat", "dog"), 6),
          "meadow": (("ladybug", "bee", "snail", "butterfly"), 3), "ice": (("snowflake",), 6), "towers": (("tower",), 6)}


def check_tasks(name, tasks):
    """Validate what a picture sheet asks: known scene, known kinds, countable sets."""
    if name not in SCENES:
        raise SystemExit(f"unknown picture '{name}'")
    if name in CHECKS:
        kinds, most = CHECKS[name]
        for t, it in tasks.items():
            if it["kind"] not in kinds or not 1 <= it["n"] <= most:
                raise SystemExit(f"{name} station {t} holds {' or '.join(kinds)}, 1 to {most}")
    elif name in ("garden", "village"):
        for t, it in tasks.items():
            if it["kind"] != "pict" or "pic" not in it:
                raise SystemExit(f"{name} station {t} shows a picture")
    elif name == "balloons":
        for t, it in tasks.items():
            if it["kind"] != "card":
                raise SystemExit(f"balloon {t} carries a letter card")
    elif name == "blocks":
        for t, it in tasks.items():
            if it["kind"] != "letter":
                raise SystemExit(f"block {t} carries an uppercase letter")


def panel(name, tasks, spots=None, dpi=300):
    sc = SCENES[name]
    c = Canvas(*sc["size"], dpi=dpi)
    spots = spots or sc["spots"]
    stations = [{"t": t, "x": x, "y": y, "fam": it.get("fam") or 0, "item": it}
                for (t, it), (x, y) in zip(sorted(tasks.items()), spots)]
    sc["paint"](c, stations)
    return c.image()


if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "lagoon"
    counts = [4, 1, 6, 2, 5, 3, 3, 5, 2, 6, 1, 4]
    demo = {}
    for t, n in zip(range(1, 13), counts):
        fam = 0 if t <= 6 else 1
        it = {"fam": fam, "n": n, "seed": t}
        if name == "lagoon":
            it["kind"] = "pearl"
        elif name == "castle":
            it["kind"] = ("yarn", "bone")[fam]
        elif name == "train":
            it["kind"] = ("cat", "dog")[fam]
        elif name == "meadow":
            it.update(kind=["ladybug", "bee", "snail", "butterfly"][t % 4], n=(t % 3) + 1, fam=None)
        elif name == "village":
            it.update(kind="pict", pic=["cat", "hat", "cap", "pig", "pen", "hen", "fox", "box", "bus", "nut", "cup", "sun"][t - 1])
        elif name == "garden":
            it.update(kind="pict", pic=["cat", "dog", "fox", "gift", "pig", "otter", "panda", "mouse",
                                        "cookie", "bunny", "daisy", "sun"][t - 1])
        elif name == "balloons":
            words = ["DOG", "GIFT", "CAT", "PIG", "OTTER", "FOX", "SUN", "BUNNY", "PANDA", "COOKIE", "MOUSE", "DAISY"]
            it.update(kind="card", word=words[t - 1], n=ord(words[t - 1][0]) - 65)
        elif name == "ice":
            it["kind"] = "snowflake"
        elif name == "towers":
            it["kind"] = "tower"
        elif name == "blocks":
            it.update(kind="letter", n=[2, 5, 0, 7, 3, 6, 1, 4, 8, 11, 9, 10][t - 1], fam=None)
        demo[t] = it
    panel(name, demo).save(sys.argv[2] if len(sys.argv) > 2 else "panel.png")
