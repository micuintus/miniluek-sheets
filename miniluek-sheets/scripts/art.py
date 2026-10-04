"""Procedural artwork (MIT): full-body princesses and counting hands.

Drawn at 2x supersampling and downscaled for smooth edges. No external images.
"""
import math
import random

from PIL import Image, ImageDraw

SS = 2                      # supersampling factor
W0, H0 = 600, 860           # design canvas

SKIN = [(255, 224, 196), (241, 194, 160), (214, 157, 118), (166, 108, 72), (110, 70, 48)]
HAIR = [(64, 40, 28), (28, 24, 26), (231, 186, 84), (190, 92, 46), (125, 78, 44), (242, 140, 190), (150, 120, 200)]
DRESS = [(244, 120, 170), (178, 140, 230), (110, 190, 240), (100, 200, 170), (255, 160, 120),
         (255, 205, 90), (236, 80, 120), (90, 205, 220)]
GOLD, GOLD_D = (252, 205, 70), (210, 150, 30)
GEMS = [(230, 40, 70), (60, 140, 230), (40, 180, 110), (240, 90, 200)]


def darker(c, f=0.72):
    return tuple(max(0, int(v * f)) for v in c[:3])


def lighter(c, f=0.45):
    return tuple(int(v + (255 - v) * f) for v in c[:3])


class Pen:
    def __init__(self, w, h):
        self.img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def p(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def poly(self, pts, fill, outline=None, width=6):
        self.d.polygon(self.p(pts), fill=fill)
        if outline:
            q = self.p(pts) + [self.p(pts)[0]]
            self.d.line(q, fill=outline, width=width * SS, joint="curve")

    def ell(self, cx, cy, rx, ry, fill, outline=None, width=6):
        box = [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS]
        self.d.ellipse(box, fill=fill, outline=outline, width=(width * SS if outline else 0))

    def line(self, pts, fill, width):
        self.d.line(self.p(pts), fill=fill, width=width * SS, joint="curve")
        for x, y in pts[:1] + pts[-1:]:
            self.ell(x, y, width / 2, width / 2, fill)

    def arc(self, cx, cy, rx, ry, a0, a1, fill, width):
        box = [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS]
        self.d.arc(box, a0, a1, fill=fill, width=width * SS)

    def done(self, w, h):
        return self.img.resize((w, h), Image.LANCZOS)


def bezier(p0, p1, p2, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out


def princess(skin=0, hair=0, dress=0, style="long", pose="down", crown="crown", seed=0):
    rnd = random.Random(seed)
    S, Hc, Dc = SKIN[skin % len(SKIN)], HAIR[hair % len(HAIR)], DRESS[dress % len(DRESS)]
    so, ho, do = darker(S, 0.75), darker(Hc, 0.65), darker(Dc, 0.68)
    pen = Pen(W0, H0)
    cx, hy, hr = 300, 228, 118            # head centre and radius

    # back hair
    if style == "long":
        pen.poly(bezier((175, 230), (150, 420), (205, 520)) + bezier((395, 520), (450, 420), (425, 230))[0:] +
                 bezier((425, 230), (300, 60), (175, 230)), Hc, ho)
    elif style == "curly":
        for a in range(0, 360, 30):
            r = math.radians(a)
            pen.ell(cx + math.cos(r) * 112, hy - 10 + math.sin(r) * 118, 62, 62, Hc, ho)
        pen.ell(cx, hy - 10, 135, 140, Hc)
    elif style == "buns":
        pen.ell(cx - 112, 118, 52, 52, Hc, ho)
        pen.ell(cx + 112, 118, 52, 52, Hc, ho)
        pen.ell(cx, hy + 5, 128, 128, Hc, ho)
    elif style == "bob":
        pen.poly(bezier((180, 240), (170, 360), (215, 360)) + [(385, 360)] + bezier((385, 360), (430, 360), (420, 240)) +
                 bezier((420, 240), (300, 70), (180, 240)), Hc, ho)
    elif style == "braid":
        pen.ell(cx, hy, 128, 128, Hc, ho)
        for i in range(5):
            pen.ell(cx + 118 + i * 6, 330 + i * 46, 30 - i * 2, 30 - i * 2, Hc, ho)

    # skirt
    waist_y, hem_y = 455, 790
    left = bezier((248, waist_y), (170, 640), (92, hem_y))
    right = bezier((508, hem_y), (430, 640), (352, waist_y))
    hem = []
    n = 6
    for i in range(n):
        x0 = 92 + (508 - 92) * i / n
        x1 = 92 + (508 - 92) * (i + 1) / n
        hem += bezier((x0, hem_y), ((x0 + x1) / 2, hem_y + 34), (x1, hem_y), 10)
    pen.poly(left + hem + right, Dc, do)
    # ruffle band and sparkles
    for i in range(n):
        x0 = 92 + (508 - 92) * i / n
        pen.ell(x0 + (508 - 92) / (2 * n), hem_y - 6, 30, 16, lighter(Dc, 0.35))
    for _ in range(9):
        y = rnd.uniform(waist_y + 60, hem_y - 50)
        half = 52 + (y - waist_y) / (hem_y - waist_y) * 150
        x = rnd.uniform(cx - half + 20, cx + half - 20)
        pen.ell(x, y, 7, 7, lighter(Dc, 0.7))
    # shoes
    pen.ell(cx - 55, hem_y + 30, 34, 18, darker(Dc, 0.55))
    pen.ell(cx + 55, hem_y + 30, 34, 18, darker(Dc, 0.55))

    # arms (behind bodice for 'down', raised otherwise)
    arm_w = 30
    hand_l, hand_r = (188, 548), (412, 548)
    if pose == "up":
        hand_l, hand_r = (176, 300), (424, 300)
    elif pose == "wave":
        hand_r = (440, 290)
    elif pose == "wand":
        hand_r = (446, 380)
    pen.line([(255, 420), hand_l], so, arm_w + 8)
    pen.line([(255, 420), hand_l], S, arm_w)
    pen.line([(345, 420), hand_r], so, arm_w + 8)
    pen.line([(345, 420), hand_r], S, arm_w)
    pen.ell(*hand_l, 22, 22, S, so, 4)
    pen.ell(*hand_r, 22, 22, S, so, 4)
    if pose == "wand":
        pen.line([(hand_r[0], hand_r[1]), (hand_r[0] + 40, hand_r[1] - 120)], (120, 90, 60), 9)
        sx, sy = hand_r[0] + 44, hand_r[1] - 140
        star = []
        for k in range(10):
            r = 34 if k % 2 == 0 else 15
            a = math.radians(-90 + k * 36)
            star.append((sx + r * math.cos(a), sy + r * math.sin(a)))
        pen.poly(star, GOLD, GOLD_D, 4)

    # bodice + puff sleeves + sash
    pen.poly(bezier((250, 380), (300, 360), (350, 380)) + [(356, waist_y + 5), (244, waist_y + 5)], Dc, do)
    pen.ell(242, 392, 40, 36, lighter(Dc, 0.3), do, 5)
    pen.ell(358, 392, 40, 36, lighter(Dc, 0.3), do, 5)
    pen.poly([(240, waist_y - 14), (360, waist_y - 14), (362, waist_y + 12), (238, waist_y + 12)], lighter(Dc, 0.55), do, 4)
    pen.ell(cx, waist_y - 1, 16, 14, GEMS[(dress + 1) % len(GEMS)], darker(GEMS[(dress + 1) % len(GEMS)], 0.6), 3)

    # neck + head
    pen.poly([(282, 330), (318, 330), (318, 378), (282, 378)], S, so, 4)
    pen.ell(cx, hy, hr, hr, S, so, 6)
    # ears hint
    pen.ell(cx - hr + 4, hy + 18, 16, 22, S, so, 4)
    pen.ell(cx + hr - 4, hy + 18, 16, 22, S, so, 4)

    # fringe
    top = []
    for a in range(200, 341, 4):
        r = math.radians(a)
        top.append((cx + (hr + 8) * math.cos(r), hy + (hr + 8) * math.sin(r)))
    x_r, x_l = top[-1][0], top[0][0]
    scal = []
    k = 4
    for i in range(k):
        xa = x_r - (x_r - x_l) * i / k
        xb = x_r - (x_r - x_l) * (i + 1) / k
        scal += bezier((xa, hy - 30 + (8 if i in (0, k - 1) else 0)), ((xa + xb) / 2, hy - 2), (xb, hy - 30 + (8 if i in (0, k - 1) else 0)), 10)
    pen.poly(top + scal, Hc, ho, 5)
    if style in ("long", "bob"):
        pen.poly([(cx - hr - 6, hy - 40), (cx - hr + 26, hy - 30), (cx - hr + 16, hy + 70), (cx - hr - 10, hy + 60)], Hc, ho, 4)
        pen.poly([(cx + hr + 6, hy - 40), (cx + hr - 26, hy - 30), (cx + hr - 16, hy + 70), (cx + hr + 10, hy + 60)], Hc, ho, 4)

    # face
    eye_y = hy + 18
    for ex in (cx - 42, cx + 42):
        pen.ell(ex, eye_y, 14, 19, (45, 34, 40))
        pen.ell(ex + 5, eye_y - 7, 5, 5, (255, 255, 255))
    pen.ell(cx - 70, hy + 52, 22, 13, (255, 150, 165, 170))
    pen.ell(cx + 70, hy + 52, 22, 13, (255, 150, 165, 170))
    pen.arc(cx, hy + 50, 22, 16, 20, 160, (170, 60, 70), 6)

    # crown / tiara
    base_y = hy - hr + 12
    if crown == "crown":
        pts = [(cx - 62, base_y), (cx - 72, base_y - 62), (cx - 36, base_y - 30), (cx, base_y - 78),
               (cx + 36, base_y - 30), (cx + 72, base_y - 62), (cx + 62, base_y)]
        pen.poly(pts, GOLD, GOLD_D, 5)
        for x, y in ((cx - 72, base_y - 66), (cx, base_y - 82), (cx + 72, base_y - 66)):
            pen.ell(x, y, 10, 10, GOLD, GOLD_D, 3)
        pen.ell(cx, base_y - 22, 11, 11, GEMS[dress % len(GEMS)], darker(GEMS[dress % len(GEMS)], 0.6), 3)
    else:
        pen.arc(cx, base_y + 20, 70, 40, 200, 340, GOLD_D, 14)
        pen.arc(cx, base_y + 20, 70, 40, 200, 340, GOLD, 9)
        pen.ell(cx, base_y - 22, 13, 15, GEMS[dress % len(GEMS)], darker(GEMS[dress % len(GEMS)], 0.6), 3)
    img = pen.done(W0, H0)
    return img.crop(img.getbbox())


def hand(fingers_up, side="right", skin=1):
    """Back of a hand as the child sees her own raised hand, fingers up, counting from the index finger.

    side='right': thumb on the viewer's left; side='left': thumb on the right.
    """
    S = SKIN[skin % len(SKIN)]
    so = darker(S, 0.7)
    pen = Pen(420, 560)
    # palm
    pen.poly(bezier((110, 300), (100, 470), (170, 520)) + bezier((250, 520), (330, 480), (320, 300)) + [(110, 300)], S, so, 6)
    order = ["index", "middle", "ring", "little", "thumb"]   # American habit: index = 1, thumb = 5
    up = set(order[:fingers_up])
    fingers = {"index": (145, 300, 175, 70), "middle": (200, 296, 200, 72), "ring": (255, 300, 182, 68),
               "little": (303, 312, 140, 60)}
    for name, (x, y, length, wdt) in fingers.items():
        L = length if name in up else 46
        pen.line([(x, y), (x, y - L)], so, wdt + 10)
        pen.line([(x, y), (x, y - L)], S, wdt)
        if name in up:
            pen.ell(x, y - L + 10, wdt * 0.28, wdt * 0.34, lighter(S, 0.55))
    if "thumb" in up:
        pen.line([(120, 410), (40, 300)], so, 74)
        pen.line([(120, 410), (40, 300)], S, 64)
        pen.ell(46, 306, 18, 20, lighter(S, 0.55))
    else:
        pen.line([(130, 420), (185, 380)], so, 64)
        pen.line([(130, 420), (185, 380)], S, 54)
    img = pen.done(420, 560)
    img = img.crop(img.getbbox())
    if side == "left":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


STYLES = ["long", "curly", "buns", "bob", "braid"]


def princess_variant(index, pose="down"):
    """Deterministic variety: skin, hair, dress, hairstyle and crown cycle at different rates."""
    return princess(skin=index % 5, hair=(index * 3 + 1) % 7, dress=(index * 5 + 2) % 8,
                    style=STYLES[(index * 2) % 5], pose=pose,
                    crown="crown" if index % 3 else "tiara", seed=index)


if __name__ == "__main__":
    import sys
    out = Image.new("RGBA", (6 * 330, 2 * 480 + 500), (255, 255, 255, 255))
    for i in range(12):
        im = princess_variant(i, ["down", "wand", "up", "wave"][i % 4])
        im.thumbnail((300, 450), Image.LANCZOS)
        out.alpha_composite(im, ((i % 6) * 330 + 15, (i // 6) * 480 + 10))
    for n in range(1, 6):
        h = hand(n)
        h.thumbnail((280, 380), Image.LANCZOS)
        out.alpha_composite(h, ((n - 1) * 330 + 25, 2 * 480 + 60))
    out.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 else "art_demo.png")
