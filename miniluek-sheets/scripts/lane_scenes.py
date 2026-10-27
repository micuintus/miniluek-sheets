"""Lane pictures (MIT): the story worlds of the numbers, letters and logic lanes, drawn like scenes.py.

Numbers: one day at the unicorn circus, morning to night. Letters: the mermaid's sea post.
Logic: the ice palace. Each scene paints its twelve stations from the task items the
generator also derives the answers from, so a station cannot show something other than what
its answer counts, names or continues. Registered into scenes.SCENES and scenes.KINDS on import.
Coordinates are cm inside the 28.3 x 7.6 cm panel, origin top left, y down.
"""
import math
import random

from PIL import Image

import art
import scenes as S
from scenes import Canvas, alpha, badge, curve, emoji, glitter, mix, sparkle

W, H = 28.3, 7.6
FAM = [(236, 112, 170), (88, 150, 222)]        # frame colours of the two task families
INK = [(176, 30, 110), (30, 90, 180)]
FILL = [(252, 222, 236), (219, 234, 252)]
GOLD, GOLD_DARK = (255, 214, 110), (206, 150, 50)
CIRCUS_RED, CREAM = (226, 92, 92), (255, 246, 232)
FLAGS = [(226, 92, 92), (250, 205, 80), (170, 140, 220), (120, 186, 120), (245, 150, 60)]


def mirror(left):
    """Pink stations 1-6 on the left, blue 7-12 mirrored on the right, read left to right."""
    return list(left) + [(W - x, y) for x, y in reversed(left)]


def zigzag(top, bottom, xs_top, xs_bottom):
    """Six spots per half, alternating top and bottom row, mirrored for the blue half."""
    left = []
    for i in range(3):
        left += [(xs_top[i], top[i]), (xs_bottom[i], bottom[i])]
    return mirror(left)


def register(name, paint, spots, station=None, check=None, example=None):
    S.SCENES[name] = {"paint": paint, "size": (W, H), "spots": spots}
    if example:
        S.SCENES[name]["example_box"] = example
    if station:
        S.SCENES[name]["station"] = station
    if check:
        S.SCENES[name]["check"] = check


def sprite(draw, w=3.6, h=3.0):
    """A station drawn alone on a transparent canvas: the worked example uses it."""
    c = Canvas(w, h, bg=(0, 0, 0, 0))
    draw(c, w / 2, h / 2)
    return c.image(radius=None)


def need(tasks, kinds, lo, hi, name):
    for t, it in tasks.items():
        if it["kind"] not in kinds or not lo <= it["n"] <= hi:
            raise SystemExit(f"{name} station {t} holds {' or '.join(kinds)}, {lo} to {hi}")


# ------------------------------------------------------------------ circus world

def bunting_line(c, x0, y0, x1, y1, sag, flag=0.36, seed=0):
    pts = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)) for t in [i / 40 for i in range(41)]]
    c.line(pts, fill=(176, 150, 150), width=0.022, caps=False)
    n = max(2, int(math.dist((x0, y0), (x1, y1)) / (flag * 1.7)))
    for k in range(n):
        t = (k + 0.5) / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
        c.poly([(x - flag * 0.5, y), (x + flag * 0.5, y), (x, y + flag * 0.95)], fill=FLAGS[(k + seed) % len(FLAGS)])


def big_top(c, cx, base, s=1.0, fade=0.0):
    """The circus tent seen from outside: striped cone roof, flag, curtained entrance."""
    def f(col):
        return mix(col, (255, 248, 240), fade)
    rw, wall, roof = 3.4 * s, 1.5 * s, 2.0 * s
    top = base - wall - roof
    for k in range(8):
        a, b = -rw + k * 2 * rw / 8, -rw + (k + 1) * 2 * rw / 8
        c.poly([(cx + a, base - wall), (cx + b, base - wall), (cx + b, base), (cx + a, base)],
               fill=f(CIRCUS_RED if k % 2 else CREAM))
    for k in range(8):
        a, b = -rw + k * 2 * rw / 8, -rw + (k + 1) * 2 * rw / 8
        c.poly([(cx + a, base - wall), (cx + b, base - wall), (cx, top)], fill=f(CREAM if k % 2 else CIRCUS_RED))
    scallop = [(cx - rw + 2 * rw * i / 60, base - wall + 0.12 * s * abs(math.sin(math.pi * 8 * i / 60))) for i in range(61)]
    c.line(scallop, fill=f(GOLD), width=0.09 * s, caps=False)
    c.poly([(cx - 0.55 * s, base), (cx + 0.55 * s, base), (cx + 0.42 * s, base - 1.05 * s), (cx - 0.42 * s, base - 1.05 * s)],
           fill=f((120, 60, 90)))
    for d in (-1, 1):
        c.poly([(cx + d * 0.05 * s, base - 1.1 * s), (cx + d * 0.62 * s, base - 1.1 * s), (cx + d * 0.66 * s, base),
                (cx + d * 0.3 * s, base)], fill=f((200, 70, 80)))
    c.line([(cx, top), (cx, top - 0.6 * s)], fill=f((150, 120, 110)), width=0.04 * s)
    c.poly([(cx, top - 0.6 * s), (cx + 0.45 * s, top - 0.47 * s), (cx, top - 0.34 * s)], fill=f(FLAGS[2]))
    return top


def fairground(c, sky_top, sky_low, hz=3.1):
    c.vgrad(0, 0, W, hz + 0.4, sky_top, sky_low)
    for x, y, s in ((2.6, 0.75, 0.5), (9.4, 0.5, 0.42), (19.8, 0.62, 0.48), (25.6, 0.42, 0.4)):
        S.cloud(c, x, y, s)
    hills = [(x, hz - 0.35 - 0.28 * math.sin(x / 3.3 + 0.7) - 0.1 * math.sin(x / 1.2)) for x in [W * i / 120 for i in range(121)]]
    c.poly(hills + [(W, hz + 0.6), (0, hz + 0.6)], fill=(196, 226, 170))
    c.vgrad(0, hz, W, H, (200, 230, 168), (170, 214, 140), [(0, hz), (W, hz), (W, H), (0, H)])


def ticket_shape(cx, cy, w, h, notch, r):
    """Ticket outline: rounded corners and a half-moon notch in the middle of each short side."""
    pts = []
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    def arc(ox, oy, a0, a1, rad, n=8):
        return [(ox + rad * math.cos(a0 + (a1 - a0) * i / n), oy + rad * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    pts += arc(x0 + r, y0 + r, math.pi, 1.5 * math.pi, r)
    pts += arc(x1 - r, y0 + r, 1.5 * math.pi, 2 * math.pi, r)
    pts += arc(x1, cy, 1.5 * math.pi, 0.5 * math.pi, notch, 12)
    pts += arc(x1 - r, y1 - r, 0, 0.5 * math.pi, r)
    pts += arc(x0 + r, y1 - r, 0.5 * math.pi, math.pi, r)
    pts += arc(x0, cy, 0.5 * math.pi, -0.5 * math.pi, notch, 12)
    return pts


def ticket(c, cx, cy, n, fam, s=1.0):
    """Circus ticket in the family colour: a star stub, a perforation, the numeral."""
    w, h = 2.3 * s, 1.34 * s
    c.shadow(cx + 0.06, cy + h / 2 + 0.05, w * 0.46, 0.09 * s, strength=0.2)
    c.poly(ticket_shape(cx, cy, w, h, 0.2 * s, 0.14 * s), fill=FILL[fam], outline=FAM[fam], width=0.06 * s)
    c.poly(ticket_shape(cx, cy, w - 0.22 * s, h - 0.22 * s, 0.13 * s, 0.08 * s), outline=mix(FAM[fam], (255, 255, 255), 0.45),
           width=0.025 * s)
    px = cx - w / 2 + 0.62 * s
    for k in range(7):
        y = cy - h / 2 + 0.16 * s + k * (h - 0.32 * s) / 6.5
        c.line([(px, y), (px, y + 0.07 * s)], fill=FAM[fam], width=0.035 * s, caps=False)
    sx = cx - w / 2 + 0.33 * s
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = (0.2 if i % 2 == 0 else 0.085) * s
        pts.append((sx + rr * math.cos(a), cy + rr * math.sin(a)))
    c.poly(pts, fill=GOLD, outline=GOLD_DARK, width=0.02 * s)
    c.text(cx + 0.3 * s, cy + 0.02 * s, str(n), 1.12 * s, INK[fam])


def booth(c, cx, base):
    """Ticket booth: striped awning, the circus princess in the window, a star on the roof."""
    w = 3.3
    c.shadow(cx, base, w * 0.55, 0.16, strength=0.22)
    c.rrect(cx - w / 2, base - 2.5, cx + w / 2, base, 0.1, fill=(250, 236, 214), outline=(196, 160, 120), width=0.04)
    for k in range(5):
        x = cx - w / 2 + (k + 0.5) * w / 5
        c.line([(x, base - 1.0), (x, base - 0.1)], fill=(236, 214, 186), width=0.12, caps=False)
    c.rrect(cx - 1.15, base - 2.35, cx + 1.15, base - 1.05, 0.12, fill=(255, 250, 236), outline=(196, 160, 120), width=0.035)
    queen = art.princess(skin=0, style="braid", pose="wave", crown="tiara", seed=8, hair_col=(246, 238, 220),
                         dress_col=(206, 186, 246))
    c.paste(queen, cx, base - 0.55, h=2.6, clip=(cx - 1.1, base - 2.3, cx + 1.1, base - 1.1))
    c.rrect(cx - w / 2 - 0.15, base - 1.12, cx + w / 2 + 0.15, base - 0.92, 0.06, fill=(214, 170, 110), outline=(170, 124, 70),
            width=0.03)
    aw_top, aw_bot = base - 3.25, base - 2.45
    for k in range(7):
        a, b = cx - w / 2 - 0.2 + k * (w + 0.4) / 7, cx - w / 2 - 0.2 + (k + 1) * (w + 0.4) / 7
        c.poly([(a + 0.12, aw_top), (b + 0.12, aw_top), (b, aw_bot), (a, aw_bot)], fill=CIRCUS_RED if k % 2 == 0 else CREAM)
        c.ellipse((a + b) / 2, aw_bot, (b - a) / 2, 0.16, fill=CIRCUS_RED if k % 2 == 0 else CREAM)
    c.line([(cx - w / 2 - 0.08, aw_top), (cx + w / 2 + 0.32, aw_top)], fill=GOLD_DARK, width=0.07)
    star = [(cx + (0.42 if i % 2 == 0 else 0.18) * math.cos(-math.pi / 2 + i * math.pi / 5),
             aw_top - 0.5 + (0.42 if i % 2 == 0 else 0.18) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    c.poly(star, fill=GOLD, outline=GOLD_DARK, width=0.03)
    glitter(c, curve((cx - 1.0, aw_top - 0.45), (cx, aw_top - 1.2), (cx + 1.0, aw_top - 0.45)), 40, 21, spread=0.12, glints=4)


GUESTS = ["bunny", "fox", "panda", "cat", "owl", "puppy", "teddy", "mouse", "chick", "hamster", "frog", "penguin"]


def ticket_queue(c, stations):
    """Afternoon at the ticket booth: twelve guests, each with a ticket that says how many."""
    fairground(c, (255, 226, 206), (255, 246, 230))
    S.sun(c, 26.9, 0.75, 0.42)
    top = big_top(c, W / 2, 3.6, 0.95)
    bunting_line(c, 0.0, 0.7, W / 2 - 0.1, top + 0.35, 0.55, seed=0)
    bunting_line(c, W / 2 + 0.1, top + 0.35, W, 0.7, 0.55, seed=2)
    plaza = [(W / 2 + 3.9 * math.cos(a), 6.35 + 1.1 * math.sin(a)) for a in [2 * math.pi * i / 80 for i in range(80)]]
    c.vgrad(W / 2 - 3.9, 5.2, W / 2 + 3.9, 7.5, (246, 228, 196), (236, 212, 172), plaza)
    booth(c, W / 2, 6.25)
    rnd = random.Random(4)
    for x, y in ((0.7, 7.05), (12.0, 7.2), (16.4, 7.2), (27.7, 7.05)):
        for _ in range(3):
            c.paste(emoji("tulip"), x + rnd.uniform(-0.45, 0.45), y + rnd.uniform(-0.12, 0.12), h=0.5)
    queue_rope(c, stations)
    for st in stations:
        x, y, fam = st["x"], st["y"], st["fam"]
        look = 1 if x < W / 2 else -1
        c.paste(emoji(GUESTS[st["t"] - 1]), x + 0.62 * look, y - 0.95, h=1.08, flip=look < 0)
        ticket(c, x, y, st["item"]["n"], fam)
        badge(c, x - 1.15, y - 0.67, st["t"], fam)


def queue_rope(c, stations):
    """The queue barrier: a velvet rope on gold posts joins the guests in number order."""
    pts = [(st["x"], st["y"] + 0.95) for st in sorted(stations, key=lambda st: st["t"])]
    for half, col in ((pts[:6], FAM[0]), (pts[6:], FAM[1])):
        posts = [half[0]] + [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(half, half[1:])] + [half[-1]]
        for (x0, y0), (x1, y1) in zip(posts, posts[1:]):
            c.line(curve((x0, y0 - 0.5), ((x0 + x1) / 2, (y0 + y1) / 2 - 0.15), (x1, y1 - 0.5), 16), fill=col, width=0.08)
        for x, y in posts:
            c.rrect(x - 0.05, y - 0.62, x + 0.05, y, 0.02, fill=GOLD, outline=GOLD_DARK, width=0.02)
            c.circle(x, y - 0.64, 0.08, fill=GOLD, outline=GOLD_DARK, width=0.02)
            c.ellipse(x, y, 0.16, 0.05, fill=GOLD_DARK)


TICKET_SPOTS = mirror([(1.75, 2.6), (3.2, 5.7), (5.2, 2.85), (7.05, 5.95), (8.95, 2.7), (10.55, 5.55)])


def check_tickets(tasks):
    need(tasks, ("ticket",), 1, 6, "ticket booth")


# ------------------------------------------------------------------ circus: inside the big top

def tent_inside(c, tint=0.0, bulbs=True):
    """Inside the big top: striped canvas, a ring of sawdust, garlands of bulbs."""
    def f(col):
        return mix(col, (170, 110, 60), tint)
    c.vgrad(0, 0, W, H, f((255, 248, 232)), f((252, 238, 214)))
    apex = (W / 2, -9.0)
    for k in range(-14, 15):
        if k % 2:
            continue
        x0 = W / 2 + k * 1.25
        c.poly([apex, (x0 - 0.62 * 8.5 / 7.0, H), (x0 + 0.62 * 8.5 / 7.0, H)], fill=alpha(f((255, 226, 168)), 0.8))
    if bulbs:
        pts = [(x, 0.55 + 0.45 * math.sin(math.pi * x / W)) for x in [W * i / 80 for i in range(81)]]
        c.line(pts, fill=f((176, 150, 150)), width=0.025, caps=False)
        for i in range(0, 81, 3):
            x, y = pts[i]
            c.circle(x, y + 0.11, 0.085, fill=(255, 226, 120) if i % 2 else (255, 246, 200))
    ring = [(W / 2 + 4.6 * math.cos(a), 7.25 + 0.95 * math.sin(a)) for a in [2 * math.pi * i / 90 for i in range(90)]]
    c.vgrad(W / 2 - 4.6, 6.2, W / 2 + 4.6, H, (246, 226, 186), (236, 210, 166), ring)
    c.line(ring + ring[:1], fill=f(CIRCUS_RED), width=0.22, caps=False)
    for i in range(0, 90, 5):
        c.circle(*ring[i], 0.05, fill=GOLD)


def spotlight(c, x_from, x_to, y_to, width=1.3):
    lay = c.layer(0, 0, W, H)
    lay.poly([(x_from - 0.15, 0), (x_from + 0.15, 0), (x_to + width, y_to), (x_to - width, y_to)], fill=(255, 244, 196, 70))
    lay.commit(blur=0.15)


def tightrope(c, cx, cy, n, fam, s=1.0, who=0):
    """A rope between two posts with six pads; the acrobat stands on pad n, counted from the flag."""
    L = 3.3 * s
    x0, x1 = cx - L / 2, cx + L / 2
    wood, dark = (214, 176, 120), (160, 120, 70)
    for x in (x0, x1):
        c.rrect(x - 0.06 * s, cy - 0.12 * s, x + 0.06 * s, cy + 0.95 * s, 0.03 * s, fill=wood, outline=dark, width=0.02 * s)
        c.ellipse(x, cy + 0.97 * s, 0.24 * s, 0.07 * s, fill=dark)
    c.line([(x0, cy - 0.12 * s), (x0, cy - 0.78 * s)], fill=dark, width=0.035 * s)
    c.poly([(x0, cy - 0.78 * s), (x0 + 0.48 * s, cy - 0.64 * s), (x0, cy - 0.5 * s)], fill=FAM[fam])
    c.line([(x0, cy), (x1, cy)], fill=(150, 120, 90), width=0.05 * s, caps=False)
    gap = (L - 0.8 * s) / 5
    pads = [x0 + 0.55 * s + i * gap for i in range(6)]
    px = pads[n - 1]
    if who == 0:
        acro = art.princess_variant(7 + n * 3 + fam * 11, "up")
        c.paste(acro, px, cy - 0.78 * s, h=1.45 * s)
    else:
        c.paste(emoji("frog"), px, cy - 0.42 * s, h=0.72 * s)
    for i, x in enumerate(pads):
        on = i == n - 1
        c.ellipse(x, cy, 0.2 * s, 0.13 * s, fill=(255, 214, 110) if on else FILL[fam],
                  outline=GOLD_DARK if on else FAM[fam], width=0.035 * s)


def tightrope_tent(c, stations):
    """The tightrope act in the big top: twelve ropes, twelve acrobats, count from the flag."""
    tent_inside(c)
    for st in stations:
        spotlight(c, st["x"] * 0.5 + W / 4, st["x"], st["y"] + 0.2, 1.0)
    queen = art.princess(skin=0, style="braid", pose="up", crown="tiara", seed=8, hair_col=(246, 238, 220),
                         dress_col=(206, 186, 246))
    c.shadow(W / 2, 6.95, 0.75, 0.13)
    c.rrect(W / 2 - 0.7, 5.95, W / 2 + 0.7, 6.95, 0.1, fill=CIRCUS_RED, outline=(170, 60, 70), width=0.04)
    c.line([(W / 2 - 0.7, 6.45), (W / 2 + 0.7, 6.45)], fill=GOLD, width=0.08, caps=False)
    c.paste(queen, W / 2, 4.6, h=2.75)
    glitter(c, curve((W / 2 - 1.4, 3.6), (W / 2, 2.2), (W / 2 + 1.4, 3.6)), 60, 9, spread=0.14, glints=6)
    c.paste(emoji("unicorn"), W / 2 - 2.6, 6.55, h=1.0)
    c.paste(emoji("seal"), W / 2 + 2.6, 6.6, h=0.9, flip=True)
    for st in stations:
        tightrope(c, st["x"], st["y"], st["item"]["n"], st["fam"], s=0.92, who=st["fam"])
        badge(c, st["x"] - 1.85, st["y"] - 0.95, st["t"], st["fam"])


ROPE_SPOTS = mirror([(2.35, 2.25), (2.55, 5.75), (6.35, 2.95), (6.5, 6.4), (10.3, 2.35), (10.4, 5.6)])


def check_ropes(tasks):
    need(tasks, ("rope",), 1, 6, "tightrope")


# ------------------------------------------------------------------ the sea: the mermaid's bottle post

def sea(c, hz=1.65):
    c.vgrad(0, 0, W, hz + 0.1, (196, 226, 252), (255, 240, 246))
    S.sun(c, 24.2, 0.62, 0.36)
    for x, y, s in ((3.4, 0.6, 0.48), (11.0, 0.42, 0.38), (18.4, 0.55, 0.44)):
        S.cloud(c, x, y, s)
    isle = S.blob(26.6, hz + 0.05, 1.5, 0.35, 3, wobble=0.05, flat_bottom=True)
    c.poly(isle, fill=(238, 222, 180))
    lighthouse(c, 26.9, hz - 0.05, 0.62)
    c.vgrad(0, hz, W, H, (150, 216, 238), (70, 160, 212), [(0, hz), (W, hz), (W, H), (0, H)])
    lay = c.layer(0, hz, W, H)
    rnd = random.Random(7)
    for _ in range(46):
        x, y = rnd.uniform(0.3, W - 0.3), rnd.uniform(hz + 0.25, H - 0.2)
        lay.line(S.wave(x, x + rnd.uniform(0.5, 1.1), y, 0.05, 0.55), fill=(255, 255, 255, 110), width=0.035, caps=False)
    lay.commit()
    glints = c.layer(0, hz, W, H)
    for _ in range(24):
        sparkle(glints, rnd.uniform(0.5, W - 0.5), rnd.uniform(hz + 0.2, H - 0.3), rnd.uniform(0.05, 0.12), fill=(255, 255, 255, 220))
    glints.commit()


def lighthouse(c, cx, base, s=1.0):
    for k in range(4):
        y0, y1 = base - (k + 1) * 0.5 * s, base - k * 0.5 * s
        w0, w1 = (0.32 - 0.03 * (k + 1)) * s, (0.32 - 0.03 * k) * s
        c.poly([(cx - w1, y1), (cx + w1, y1), (cx + w0, y0), (cx - w0, y0)], fill=CIRCUS_RED if k % 2 == 0 else CREAM)
    top = base - 2.0 * s
    c.rrect(cx - 0.24 * s, top - 0.36 * s, cx + 0.24 * s, top, 0.04 * s, fill=(255, 236, 150), outline=(150, 110, 80), width=0.02)
    c.poly([(cx - 0.3 * s, top - 0.36 * s), (cx + 0.3 * s, top - 0.36 * s), (cx, top - 0.68 * s)], fill=(150, 110, 120))


def bottle(c, cx, cy, ch, fam, s=1.0, cork_right=True, word=None):
    """A floating bottle with a rolled letter inside; the letter faces the child, upright."""
    w, h = 2.0 * s, 1.08 * s
    d = 1 if cork_right else -1
    glass = mix(FILL[fam], (210, 240, 236), 0.45)
    body = S.rounded([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], 0.42 * s)
    neck_x = cx + d * w / 2
    neck = [(neck_x - d * 0.05 * s, cy - 0.26 * s), (neck_x + d * 0.52 * s, cy - 0.2 * s),
            (neck_x + d * 0.52 * s, cy + 0.2 * s), (neck_x - d * 0.05 * s, cy + 0.26 * s)]
    c.poly(neck, fill=glass, outline=FAM[fam], width=0.05 * s)
    c.rrect(min(neck_x + d * 0.5 * s, neck_x + d * 0.84 * s), cy - 0.19 * s, max(neck_x + d * 0.5 * s, neck_x + d * 0.84 * s),
            cy + 0.19 * s, 0.06 * s, fill=(206, 164, 112), outline=(160, 118, 70), width=0.025 * s)
    c.poly(body, fill=glass, outline=FAM[fam], width=0.06 * s)
    c.rrect(cx - 0.62 * s, cy - 0.4 * s, cx + 0.62 * s, cy + 0.4 * s, 0.1 * s, fill=(255, 250, 236), outline=(222, 196, 152),
            width=0.025 * s)
    for x in (cx - 0.62 * s, cx + 0.62 * s):
        c.ellipse(x, cy, 0.09 * s, 0.4 * s, fill=(246, 232, 204), outline=(222, 196, 152), width=0.02 * s)
    c.text(cx, cy - (0.15 if word else -0.02) * s, ch, (0.62 if word else 0.86) * s, INK[fam])
    if word:
        c.text(cx, cy + 0.27 * s, word, min(0.22, 1.1 / (0.70 * len(word))) * s, INK[fam])
    shine = c.layer(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    shine.rrect(cx - 0.82 * s, cy - 0.44 * s, cx + 0.2 * s, cy - 0.34 * s, 0.05 * s, fill=(255, 255, 255, 170))
    shine.commit()


def bobbing(c, cx, cy, w):
    lay = c.layer(cx - w, cy, cx + w, cy + 0.8)
    for k, dy in enumerate((0.58, 0.72)):
        lay.line(S.wave(cx - w * (0.75 - 0.15 * k), cx + w * (0.75 - 0.15 * k), cy + dy, 0.04, 0.42, k),
                 fill=(255, 255, 255, 200 - 60 * k), width=0.05, caps=False)
    lay.commit()


def bottle_post(c, stations):
    """The mermaid's bottle post: twelve bottles drift in, each with one letter."""
    sea(c)
    S.rock(c, W / 2, 5.6, 2.0, 1.0, 11)
    mer = art.princess(skin=1, hair=5, dress=0, style="long", pose="wave", crown="tiara", seed=3, tail=(70, 196, 196))
    c.paste(mer, W / 2 + 0.05, 4.05, h=3.0)
    glitter(c, curve((W / 2 - 0.9, 5.2), (W / 2, 3.4), (W / 2 + 1.0, 5.1)), 50, 5, spread=0.14, glints=5)
    c.paste(emoji("dolphin"), 5.1, 1.55, h=0.7, flip=True)
    c.paste(emoji("spoutwhale"), 21.6, 1.6, h=0.75)
    S.trail(c, stations, "bubbles")
    for st in stations:
        right = st["x"] < W / 2
        bobbing(c, st["x"], st["y"], 1.5)
        bottle(c, st["x"] - (0.25 if right else -0.25), st["y"], chr(65 + st["item"]["n"]), st["fam"], cork_right=right,
               word=st["item"].get("word"))
        badge(c, st["x"] - (1.1 if right else 0.6), st["y"] - 0.66, st["t"], st["fam"])


BOTTLE_SPOTS = mirror([(1.85, 2.75), (2.45, 6.05), (5.15, 4.3), (8.1, 2.65), (8.55, 6.15), (10.85, 4.2)])


def check_bottles(tasks):
    need(tasks, ("card",), 0, 25, "bottle post")
    for t, it in tasks.items():
        if "pic" not in it:
            raise SystemExit(f"bottle {t} carries a letter card bound to a course word")


# ------------------------------------------------------------------ the sea post: under water

def seafloor(c, sand_y=6.55):
    """Under the sea: light from above, a sandy floor, seaweed and coral at the edges."""
    c.vgrad(0, 0, W, sand_y + 0.3, (170, 226, 240), (90, 170, 214))
    beams = c.layer(0, 0, W, sand_y)
    for i in range(7):
        x0 = 1.0 + i * 4.3
        beams.poly([(x0, 0), (x0 + 1.4, 0), (x0 + 3.2, sand_y), (x0 + 0.6, sand_y)], fill=(255, 255, 255, 26))
    beams.commit()
    floor = [(x, sand_y + 0.15 * math.sin(x / 2.1 + 0.4)) for x in [W * i / 120 for i in range(121)]]
    c.vgrad(0, sand_y - 0.2, W, H, (244, 226, 186), (226, 200, 150), floor + [(W, H), (0, H)])
    rnd = random.Random(21)
    grain = c.layer(0, sand_y, W, H)
    for _ in range(120):
        grain.circle(rnd.uniform(0, W), rnd.uniform(sand_y + 0.25, H - 0.1), 0.018, fill=(200, 160, 110, 120))
    grain.commit()
    for x, h, col in ((0.45, 2.6, (110, 186, 120)), (27.85, 2.4, (120, 196, 130)), (12.0, 1.4, (110, 186, 120)), (16.4, 1.5, (120, 196, 130))):
        S.seaweed(c, x, sand_y + 0.2, h, col, round(x * 10))
    S.coral(c, 1.3, sand_y + 0.35, 0.8, (250, 170, 120))
    S.coral(c, 27.0, sand_y + 0.35, 0.75, (255, 196, 120))
    bub = c.layer(0, 0, W, H)
    for _ in range(26):
        x, y, r = rnd.uniform(0.4, W - 0.4), rnd.uniform(0.3, sand_y - 0.3), rnd.uniform(0.05, 0.12)
        bub.circle(x, y, r, outline=(255, 255, 255, 170), width=0.02)
    bub.commit()


def mermaid(c, x, y, h=2.9, pose="wave"):
    mer = art.princess(skin=1, hair=5, dress=0, style="long", pose=pose, crown="tiara", seed=3, tail=(70, 196, 196))
    c.paste(mer, x, y, h=h)
    glitter(c, curve((x - 0.9, y + 1.0), (x, y - 0.8), (x + 1.0, y + 0.9)), 45, 5, spread=0.14, glints=5)


def letter_shell(c, cx, cy, ch, fam, s=1.0):
    """An open scallop: a ribbed fan behind, a pearl in the dish with one letter on it."""
    body, edge = mix(FAM[fam], (255, 255, 255), 0.45), mix(FAM[fam], (60, 30, 70), 0.25)
    c.shadow(cx, cy + 0.72 * s, 1.15 * s, 0.14 * s, strength=0.2)
    fan = []
    for i in range(61):
        t = i / 60
        a = math.radians(-170 + 160 * t)
        bump = 0.06 * s * abs(math.sin(math.pi * 8 * t))
        fan.append((cx + (1.15 * s + bump) * math.cos(a), cy + 0.35 * s + (1.1 * s + bump) * math.sin(a)))
    c.poly(fan + [(cx, cy + 0.45 * s)], fill=body, outline=edge, width=0.04 * s)
    for k in range(1, 8):
        a = math.radians(-170 + 160 * k / 8)
        c.line([(cx + 0.3 * s * math.cos(a), cy + 0.35 * s + 0.3 * s * math.sin(a)),
                (cx + 1.1 * s * math.cos(a), cy + 0.35 * s + 1.05 * s * math.sin(a))], fill=mix(body, edge, 0.35), width=0.025 * s)
    c.ellipse(cx, cy + 0.45 * s, 1.2 * s, 0.38 * s, fill=FAM[fam], outline=edge, width=0.04 * s)
    c.circle(cx, cy + 0.02 * s, 0.56 * s, fill=(250, 248, 255), outline=(190, 180, 214), width=0.025 * s)
    c.ellipse(cx - 0.22 * s, cy - 0.22 * s, 0.14 * s, 0.1 * s, fill=(255, 255, 255))
    c.text(cx, cy + 0.04 * s, ch, 0.78 * s, INK[fam])


def twin_shells(c, stations):
    """The storm mixed up the mermaid's letter shells; every shell has a twin below."""
    seafloor(c)
    mermaid(c, W / 2, 4.3)
    c.paste(emoji("tropicalfish"), 9.6, 1.0, h=0.55, flip=True)
    c.paste(emoji("crab"), W / 2 + 1.9, 7.0, h=0.55)
    S.trail(c, stations, "bubbles")
    for st in stations:
        letter_shell(c, st["x"], st["y"], chr(65 + st["item"]["n"]), st["fam"], s=1.1)
        badge(c, st["x"] - 1.32, st["y"] - 0.85, st["t"], st["fam"])


SHELL_SPOTS = zigzag((2.1, 2.45, 2.15), (5.6, 5.9, 5.55), (1.75, 5.55, 9.35), (3.65, 7.45, 11.15))


def check_letters(tasks):
    need(tasks, ("letter",), 0, 25, "letter shell")


def big_fish(c, cx, cy, ch, fam, s=1.0, face_right=True):
    """A big fish in the family colour carrying an uppercase letter on its side."""
    d = 1 if face_right else -1
    body = FAM[fam]
    edge = mix(body, (60, 30, 70), 0.35)
    tail = [(cx - d * 1.0 * s, cy), (cx - d * 1.55 * s, cy - 0.5 * s), (cx - d * 1.45 * s, cy), (cx - d * 1.55 * s, cy + 0.5 * s)]
    c.poly(tail, fill=mix(body, (255, 255, 255), 0.2), outline=edge, width=0.03 * s)
    c.poly([(cx - d * 0.2 * s, cy - 0.6 * s), (cx + d * 0.3 * s, cy - 0.95 * s), (cx + d * 0.45 * s, cy - 0.55 * s)],
           fill=mix(body, (255, 255, 255), 0.2), outline=edge, width=0.025 * s)
    c.ellipse(cx, cy, 1.15 * s, 0.68 * s, fill=body, outline=edge, width=0.04 * s)
    c.circle(cx + d * 0.72 * s, cy - 0.16 * s, 0.11 * s, fill=(255, 255, 255), outline=edge, width=0.02 * s)
    c.circle(cx + d * 0.74 * s, cy - 0.16 * s, 0.05 * s, fill=(40, 40, 60))
    c.circle(cx - d * 0.12 * s, cy + 0.02 * s, 0.48 * s, fill=(255, 255, 255))
    c.text(cx - d * 0.12 * s, cy + 0.04 * s, ch, 0.7 * s, INK[fam])


def fish_school(c, stations):
    """Big fish swim through the reef; each one carries a big letter. Its little one has the small letter."""
    seafloor(c)
    mermaid(c, W / 2, 4.2, pose="wand")
    S.trail(c, stations, "bubbles")
    for st in stations:
        right = st["x"] < W / 2
        big_fish(c, st["x"], st["y"], chr(65 + st["item"]["n"]), st["fam"], face_right=right)
        badge(c, st["x"] - (1.45 if right else -1.45), st["y"] - 0.75, st["t"], st["fam"])


FISH_SPOTS = zigzag((1.75, 2.05, 1.8), (4.75, 5.05, 4.7), (2.05, 5.85, 9.65), (3.95, 7.75, 11.2))


def find_bubble(c, cx, cy, pic, fam, s=1.0):
    """A big air bubble rising from the sea floor with one found thing inside."""
    lay = c.layer(cx - 0.9 * s, cy - 0.9 * s, cx + 0.9 * s, cy + 0.9 * s)
    lay.circle(cx, cy, 0.78 * s, fill=(255, 255, 255, 95))
    lay.commit()
    c.circle(cx, cy, 0.78 * s, outline=FAM[fam], width=0.06 * s)
    c.paste(emoji(pic), cx, cy, box=(1.0 * s, 1.0 * s))
    hl = c.layer(cx - 0.8 * s, cy - 0.8 * s, cx + 0.8 * s, cy + 0.8 * s)
    hl.ellipse(cx - 0.42 * s, cy - 0.45 * s, 0.14 * s, 0.09 * s, fill=(255, 255, 255, 220))
    hl.commit()
    for k, (dx, dy, r) in enumerate(((0.15, 1.0, 0.1), (-0.05, 1.3, 0.07), (0.1, 1.55, 0.05))):
        c.circle(cx + dx * s, cy + dy * s, r * s, outline=(255, 255, 255, 220), width=0.02)


def sea_finds(c, stations):
    """The mermaid's finds rise in bubbles. With which letter does each start?"""
    seafloor(c)
    mermaid(c, W / 2, 4.3)
    S.rock(c, W / 2, 6.95, 1.5, 0.45, 4)
    for st in stations:
        find_bubble(c, st["x"], st["y"], st["item"]["pic"], st["fam"], s=1.3)
        badge(c, st["x"] - 1.15, st["y"] - 0.85, st["t"], st["fam"])


FIND_SPOTS = mirror([(1.75, 1.6), (2.7, 4.65), (5.0, 2.55), (6.85, 5.05), (8.75, 1.75), (10.85, 4.25)])


def check_finds(tasks):
    need(tasks, ("pict",), 0, 25, "sea find")


def syllable_fish(c, cx, cy, text, fam, s=1.0, face_right=True):
    """A small fish blowing one big bubble with a syllable in it."""
    d = 1 if face_right else -1
    fx, fy = cx - d * 0.95 * s, cy + 0.55 * s
    c.poly([(fx - d * 0.35 * s, fy), (fx - d * 0.65 * s, fy - 0.24 * s), (fx - d * 0.65 * s, fy + 0.24 * s)], fill=FILL[fam],
           outline=FAM[fam], width=0.025 * s)
    c.ellipse(fx, fy, 0.42 * s, 0.26 * s, fill=FAM[fam], outline=mix(FAM[fam], (60, 30, 70), 0.3), width=0.025 * s)
    c.circle(fx + d * 0.2 * s, fy - 0.06 * s, 0.05 * s, fill=(40, 40, 60))
    for k, (dx, dy, r) in enumerate(((0.55, -0.12, 0.06), (0.72, -0.28, 0.08))):
        c.circle(fx + d * dx * s, fy + dy * s, r * s, outline=(255, 255, 255), width=0.02)
    lay = c.layer(cx - 0.9 * s, cy - 0.9 * s, cx + 0.9 * s, cy + 0.9 * s)
    lay.circle(cx, cy - 0.15 * s, 0.7 * s, fill=(255, 255, 255, 200))
    lay.commit()
    c.circle(cx, cy - 0.15 * s, 0.7 * s, outline=FAM[fam], width=0.05 * s)
    c.text(cx, cy - 0.12 * s, text, (0.6 if len(text) <= 2 else 0.48) * s, INK[fam])


def syllable_bubbles(c, stations):
    """The little fish blow syllable bubbles. Whose name starts like that?"""
    seafloor(c)
    mermaid(c, W / 2, 4.3)
    for st in stations:
        syllable_fish(c, st["x"], st["y"], st["item"]["text"], st["fam"], s=1.25, face_right=st["x"] < W / 2)
        badge(c, st["x"] - 1.0, st["y"] - 1.1, st["t"], st["fam"])


SYLL_SPOTS = zigzag((1.75, 2.05, 1.8), (4.95, 5.3, 4.9), (2.55, 6.25, 9.95), (4.4, 8.05, 11.4))


def check_syllables(tasks):
    need(tasks, ("syll",), 0, 25, "syllable bubble")


def boat(c, cx, cy, word, fam, s=1.0, face_right=True):
    """A little sailboat; its name is painted on the hull."""
    d = 1 if face_right else -1
    hull = [(cx - 1.2 * s, cy - 0.25 * s), (cx + 1.2 * s, cy - 0.25 * s), (cx + 0.95 * s, cy + 0.35 * s), (cx - 0.95 * s, cy + 0.35 * s)]
    c.line([(cx - d * 0.1 * s, cy - 0.25 * s), (cx - d * 0.1 * s, cy - 1.7 * s)], fill=(150, 110, 80), width=0.05 * s)
    c.poly([(cx - d * 0.05 * s, cy - 1.65 * s), (cx + d * 0.95 * s, cy - 0.4 * s), (cx - d * 0.05 * s, cy - 0.4 * s)],
           fill=FILL[fam], outline=FAM[fam], width=0.04 * s)
    c.poly([(cx - d * 0.18 * s, cy - 1.5 * s), (cx - d * 0.85 * s, cy - 0.45 * s), (cx - d * 0.18 * s, cy - 0.45 * s)],
           fill=mix(FAM[fam], (255, 255, 255), 0.25), outline=FAM[fam], width=0.035 * s)
    c.poly(hull, fill=(255, 250, 240), outline=FAM[fam], width=0.05 * s)
    size = 0.44 * s if len(word) <= 4 else (0.38 * s if len(word) <= 6 else 0.31 * s)
    c.text(cx, cy + 0.05 * s, word, size, INK[fam])
    lay = c.layer(cx - 1.4 * s, cy + 0.2 * s, cx + 1.4 * s, cy + 0.7 * s)
    lay.line(S.wave(cx - 1.25 * s, cx + 1.25 * s, cy + 0.42 * s, 0.04, 0.4), fill=(255, 255, 255, 220), width=0.05, caps=False)
    lay.commit()


def post_boats(c, stations):
    """The post boats come in. Each has a name; find its picture."""
    sea(c)
    S.rock(c, W / 2, 5.7, 2.0, 1.0, 11)
    mermaid(c, W / 2 + 0.05, 4.15, h=3.0)
    for st in stations:
        boat(c, st["x"], st["y"], st["item"]["word"], st["fam"], s=1.3, face_right=st["x"] < W / 2)
        badge(c, st["x"] - 1.75, st["y"] - 0.75, st["t"], st["fam"])


BOAT_SPOTS = zigzag((3.05, 3.3, 3.1), (6.55, 6.8, 6.5), (2.0, 5.85, 9.7), (3.95, 7.8, 11.3))


def check_boats(tasks):
    need(tasks, ("wcard",), 0, 25, "post boat")


def parcel(c, cx, cy, pic, fam, s=1.0):
    """A parcel for the sea post: string, a picture on top, no name yet."""
    w, h = 1.7 * s, 1.25 * s
    c.shadow(cx, cy + h / 2 + 0.04, w * 0.55, 0.1 * s, strength=0.22)
    c.rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 0.08 * s, fill=(232, 204, 160), outline=(180, 140, 90), width=0.03 * s)
    c.line([(cx - w / 2, cy), (cx + w / 2, cy)], fill=FAM[fam], width=0.08 * s, caps=False)
    c.line([(cx, cy - h / 2), (cx, cy + h / 2)], fill=FAM[fam], width=0.08 * s, caps=False)
    c.rrect(cx - 0.5 * s, cy - 0.48 * s, cx + 0.5 * s, cy + 0.48 * s, 0.08 * s, fill=(255, 255, 255), outline=FAM[fam], width=0.04 * s)
    c.paste(emoji(pic), cx, cy, box=(0.8 * s, 0.8 * s))


def beach_post(c, stations):
    """The beach post office: twelve parcels with pictures wait for their name labels."""
    hz, sy = 1.6, 3.1
    c.vgrad(0, 0, W, hz + 0.1, (196, 226, 252), (255, 240, 246))
    S.sun(c, 24.4, 0.62, 0.36)
    for x, y, sc in ((4.4, 0.6, 0.46), (12.0, 0.42, 0.38), (19.4, 0.55, 0.44)):
        S.cloud(c, x, y, sc)
    shore = [(x, sy + 0.12 * math.sin(x / 2.3)) for x in [W * i / 120 for i in range(121)]]
    c.vgrad(0, hz, W, sy + 0.3, (150, 216, 238), (100, 190, 226), [(0, hz), (W, hz)] + shore[::-1])
    c.vgrad(0, sy - 0.2, W, H, (252, 238, 204), (244, 220, 172), shore + [(W, H), (0, H)])
    foam = c.layer(0, sy - 0.3, W, sy + 0.4)
    foam.line(shore, fill=(255, 255, 255, 210), width=0.1, caps=False)
    foam.commit()
    S.rock(c, W / 2, 4.6, 1.7, 0.75, 7)
    mermaid(c, W / 2 + 0.05, 3.55, h=2.6)
    lighthouse(c, 26.9, hz + 0.9, 0.55)
    S.sandcastle(c, W / 2 - 2.3, 7.35, 0.6)
    S.starfish(c, W / 2 + 2.2, 7.1, 0.2, col=(255, 190, 120), rot=0.4)
    for st in stations:
        parcel(c, st["x"], st["y"], st["item"]["pic"], st["fam"], s=1.35)
        badge(c, st["x"] - 1.3, st["y"] - 0.95, st["t"], st["fam"])


PARCEL_SPOTS = zigzag((2.45, 2.75, 2.5), (5.85, 6.15, 5.8), (1.75, 5.45, 9.15), (3.6, 7.3, 10.95))


def check_parcels(tasks):
    for t, it in tasks.items():
        if it["kind"] != "pict" or not it.get("word"):
            raise SystemExit(f"parcel {t} shows a picture bound to a printed course word")


# ------------------------------------------------------------------ the ice palace: necklaces

def palace_hall(c):
    c.vgrad(0, 0, W, H, (244, 240, 255), (232, 236, 252))
    for k in range(7):
        x = 1.6 + k * 4.18
        c.rrect(x - 0.22, 0, x + 0.22, H, 0.1, fill=(236, 240, 255), outline=(206, 210, 244), width=0.03)
    x, hw = W / 2, 1.9
    arch = [(x - hw, 7.15), (x - hw, 2.0)] + [(x - hw + 2 * hw * t, 2.0 - 1.6 * math.sin(math.pi * t)) for t in
                                              [i / 30 for i in range(31)]] + [(x + hw, 7.15)]
    c.vgrad(x - hw, 0.4, x + hw, 7.15, (130, 120, 214), (240, 214, 246), arch)
    rnd = random.Random(5)
    for _ in range(16):
        sparkle(c, rnd.uniform(x - hw + 0.2, x + hw - 0.2), rnd.uniform(0.8, 3.0), rnd.uniform(0.05, 0.12), fill=(255, 255, 255))
    S.ice_palace(c, x + 0.95, 5.9, 0.5)
    c.line(arch, fill=(196, 196, 240), width=0.16, caps=False)
    S.aurora(c, W, -0.3)
    floor = [(0, 7.15), (W, 7.15), (W, H), (0, H)]
    c.vgrad(0, 7.15, W, H, (236, 236, 252), (220, 226, 250), floor)
    c.line([(0, 7.15), (W, 7.15)], fill=(206, 210, 244), width=0.04, caps=False)


def charm(c, x, y, pic, s=1.0):
    c.circle(x, y, 0.42 * s, fill=(255, 255, 255), outline=(214, 214, 236), width=0.03 * s)
    c.paste(emoji(pic), x, y, box=(0.62 * s, 0.62 * s))


def necklace(c, cx, cy, a, b, fam, s=1.0):
    """A B A B and an empty clasp ring at the end: the next charm is a again."""
    L, sag = 4.9 * s, 0.3 * s
    x0 = cx - L / 2

    def at(u):
        return x0 + L * u, cy + sag * 4 * u * (1 - u)
    for u in (0.0, 1.0):
        x, y = at(u)
        c.circle(x, y - 0.06 * s, 0.1 * s, fill=(206, 210, 230), outline=(150, 156, 196), width=0.02 * s)
    c.line([at(i / 40) for i in range(41)], fill=FAM[fam], width=0.06 * s, caps=False)
    slots = [at((k + 0.55) / 5.1) for k in range(5)]
    for k, (x, y) in enumerate(slots[:4]):
        charm(c, x, y, a if k % 2 == 0 else b, s)
    x, y = slots[4]
    c.circle(x, y, 0.42 * s, fill=FILL[fam])
    for j in range(18):
        a0 = 2 * math.pi * j / 18
        c.line([(x + 0.42 * s * math.cos(a0), y + 0.42 * s * math.sin(a0)),
                (x + 0.42 * s * math.cos(a0 + 0.2), y + 0.42 * s * math.sin(a0 + 0.2))], fill=FAM[fam], width=0.06 * s, caps=False)


def workshop(c, stations):
    """The ice princess threads twelve necklaces; each needs one more charm."""
    palace_hall(c)
    queen = art.princess(skin=0, style="braid", pose="wand", crown="tiara", seed=8, hair_col=(246, 238, 220),
                         dress_col=(206, 186, 246))
    c.paste(queen, W / 2, 5.25, h=3.1)
    glitter(c, curve((W / 2 + 0.5, 3.6), (W / 2 + 1.7, 2.6), (W / 2 + 0.9, 1.7)), 60, 15, spread=0.15, glints=6)
    c.shadow(W / 2, 7.35, 1.9, 0.14)
    c.rrect(W / 2 - 1.8, 6.4, W / 2 + 1.8, 6.75, 0.08, fill=(222, 206, 246), outline=(170, 150, 216), width=0.03)
    for x in (W / 2 - 1.55, W / 2 + 1.55):
        c.rrect(x - 0.1, 6.75, x + 0.1, 7.35, 0.04, fill=(222, 206, 246), outline=(170, 150, 216), width=0.03)
    c.paste(emoji("penguin"), W / 2 - 2.55, 6.85, h=0.75)
    c.paste(emoji("snowman"), W / 2 + 2.6, 6.75, h=1.0)
    for st in stations:
        it = st["item"]
        necklace(c, st["x"], st["y"], it["pic"], it["other"], st["fam"])
        badge(c, st["x"] - 2.3, st["y"] - 0.66, st["t"], st["fam"])


NECK_LEFT = [(3.05, 1.2), (8.65, 1.45), (3.05, 3.65), (8.65, 3.9), (3.05, 6.1), (8.65, 6.35)]
NECK_SPOTS = NECK_LEFT + [(x + 16.6, y) for x, y in NECK_LEFT]


def check_necklaces(tasks):
    for t, it in tasks.items():
        if it["kind"] != "necklace" or not it.get("pic") or not it.get("other") or it["pic"] == it["other"]:
            raise SystemExit(f"necklace {t} needs two different charms, 'pic' (the next one) and 'other'")
        for name in (it["pic"], it["other"]):
            emoji(name)


# ------------------------------------------------------------------ the ice palace: windows, guests, maps

SHAPES = ["circle", "square", "triangle", "rectangle", "star", "heart"]


def shape_pts(n, cx, cy, r):
    """Outline of shape n, fitting a box about 2r wide."""
    name = SHAPES[n]
    if name == "circle":
        return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in [2 * math.pi * i / 72 for i in range(72)]]
    if name == "square":
        q = r * 0.86
        return [(cx - q, cy - q), (cx + q, cy - q), (cx + q, cy + q), (cx - q, cy + q)]
    if name == "triangle":
        return [(cx, cy - r), (cx + r * 1.05, cy + r * 0.8), (cx - r * 1.05, cy + r * 0.8)]
    if name == "rectangle":
        return [(cx - r * 1.15, cy - r * 0.6), (cx + r * 1.15, cy - r * 0.6), (cx + r * 1.15, cy + r * 0.6), (cx - r * 1.15, cy + r * 0.6)]
    if name == "star":
        return [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + i * math.pi / 5),
                 cy + 0.06 * r + (r if i % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    pts = []
    for i in range(80):
        t = 2 * math.pi * i / 80
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * r / 16.5, cy + 0.12 * r + y * r / 16.5))
    return pts


def window(c, cx, cy, n, fam, r=0.72):
    """A palace window cut in shape n: night sky behind the glass, a frame in the family colour."""
    pts = shape_pts(n, cx, cy, r)
    c.vgrad(cx - 1.3 * r, cy - 1.1 * r, cx + 1.3 * r, cy + 1.1 * r, (90, 80, 170), (170, 150, 220), pts)
    rnd = random.Random(n * 7 + fam)
    stars = c.layer(cx - r, cy - r, cx + r, cy + r)
    for _ in range(4):
        stars.circle(cx + rnd.uniform(-0.45, 0.45) * r, cy + rnd.uniform(-0.35, 0.3) * r, 0.03, fill=(255, 255, 255, 230))
    stars.commit()
    c.poly(pts, outline=FAM[fam], width=0.13)
    c.poly(pts, outline=(255, 255, 255, 200), width=0.03)


def shape_token(item):
    """The answer: the same shape, solid gold and smaller than its window."""
    c = Canvas(3.0, 3.0, bg=(0, 0, 0, 0))
    pts = shape_pts(item["n"], 1.5, 1.5, 0.78)
    c.poly(pts, fill=(250, 205, 80), outline=(200, 150, 50), width=0.06)
    return full_image(c)


def palace_front(c, stations):
    """The ice palace at dusk: two wings with twelve windows of six shapes."""
    c.vgrad(0, 0, W, H, (130, 120, 214), (236, 214, 246))
    S.aurora(c, W, 0.5)
    rnd = random.Random(31)
    stars = c.layer(0, 0, W, 3)
    for _ in range(40):
        stars.circle(rnd.uniform(0.2, W - 0.2), rnd.uniform(0.1, 2.0), rnd.uniform(0.02, 0.045), fill=(255, 255, 255, 220))
    stars.commit()
    ice, edge = (236, 242, 255), (170, 176, 230)
    for x0, x1 in ((0.35, 12.05), (16.25, 27.95)):
        c.rrect(x0, 0.95, x1, 7.25, 0.15, fill=ice, outline=edge, width=0.04)
        for k in range(int((x1 - x0) / 1.2)):
            x = x0 + 0.3 + k * 1.2
            c.rrect(x, 0.6, x + 0.75, 1.0, 0.05, fill=ice, outline=edge, width=0.03)
        for y in (2.55, 4.6, 6.4):
            c.line([(x0 + 0.1, y), (x1 - 0.1, y)], fill=(222, 228, 250), width=0.03, caps=False)
    S.ice_palace(c, W / 2, 7.3, 1.05)
    c.vgrad(0, 7.15, W, H, (248, 250, 255), (226, 232, 252), [(0, 7.15), (W, 7.15), (W, H), (0, H)])
    queen = art.princess(skin=0, style="braid", pose="wave", crown="tiara", seed=8, hair_col=(246, 238, 220),
                         dress_col=(206, 186, 246))
    c.paste(queen, W / 2, 6.3, h=2.1)
    for st in stations:
        window(c, st["x"], st["y"], st["item"]["n"], st["fam"])
        badge(c, st["x"] - 1.15, st["y"] - 0.75, st["t"], st["fam"])


WINDOW_SPOTS = zigzag((2.6, 2.6, 2.6), (5.5, 5.5, 5.5), (2.15, 6.2, 10.25), (2.15, 6.2, 10.25))


def check_shapes(tasks):
    need(tasks, ("shape",), 0, len(SHAPES) - 1, "palace window")


def odd_group(c, cx, cy, it, fam, s=1.0):
    """Four guests on a bench in the family colour: three of one kind, one of another."""
    c.shadow(cx, cy + 0.62 * s, 1.85 * s, 0.12 * s, strength=0.2)
    c.rrect(cx - 1.85 * s, cy + 0.3 * s, cx + 1.85 * s, cy + 0.55 * s, 0.08 * s, fill=FAM[fam], outline=mix(FAM[fam], (60, 30, 70), 0.3),
            width=0.03 * s)
    for x in (cx - 1.6 * s, cx + 1.6 * s):
        c.rrect(x - 0.07 * s, cy + 0.55 * s, x + 0.07 * s, cy + 0.82 * s, 0.03, fill=mix(FAM[fam], (60, 30, 70), 0.3))
    for k in range(4):
        c.paste(emoji(it["pic"] if k == it["at"] else it["same"]), cx + (k - 1.5) * 0.9 * s, cy, box=(0.8 * s, 0.8 * s))


def winter_party(c, stations):
    """The winter party in the palace garden: the guests sit in fours."""
    c.vgrad(0, 0, W, 3.0, (196, 210, 250), (246, 240, 255))
    S.ice_palace(c, W / 2, 3.2, 0.62)
    for x, y, s in ((4.0, 0.7, 0.45), (22.6, 0.55, 0.4)):
        S.cloud(c, x, y, s)
    hills = [(x, 2.75 - 0.2 * math.sin(x / 2.9 + 0.4)) for x in [W * i / 120 for i in range(121)]]
    c.vgrad(0, 2.4, W, H, (250, 252, 255), (226, 234, 252), hills + [(W, H), (0, H)])
    for x, h in ((0.8, 1.3), (27.5, 1.2), (12.3, 0.9), (16.0, 0.95)):
        c.paste(emoji("evergreen"), x, 3.0 - h / 2 + 0.25, h=h)
    lanterns(c, 0.0, 0.4, W / 2 - 1.2, 1.6, 0.4, seed=1)
    lanterns(c, W / 2 + 1.2, 1.6, W, 0.4, 0.4, seed=3)
    queen = art.princess(skin=0, style="braid", pose="wave", crown="tiara", seed=8, hair_col=(246, 238, 220),
                         dress_col=(206, 186, 246))
    c.paste(queen, W / 2, 5.75, h=2.6)
    c.paste(emoji("snowman"), W / 2 + 1.45, 6.6, h=1.0)
    for st in stations:
        odd_group(c, st["x"], st["y"], st["item"], st["fam"])
        badge(c, st["x"] - 1.75, st["y"] - 0.72, st["t"], st["fam"])


ODD_SPOTS = zigzag((3.0, 3.2, 3.0), (6.25, 6.4, 6.2), (2.2, 6.15, 10.1), (2.2, 6.15, 10.1))


def check_odd(tasks):
    for t, it in tasks.items():
        if it["kind"] != "odd" or not it.get("pic") or not it.get("same") or it["pic"] == it["same"] or it.get("at") not in range(4):
            raise SystemExit(f"winter guests {t}: 'same' three times and a different 'pic' at 'at' 0 to 3")
        emoji(it["pic"]), emoji(it["same"])


def mini_castle(c, cx, cy, n, fam, s=1.0):
    """A little ice castle with nine windows; the princess looks out of window n (row by row)."""
    w, h = 2.0 * s, 1.95 * s
    ice, edge = (240, 244, 255), mix(FAM[fam], (120, 120, 160), 0.35)
    c.shadow(cx, cy + h / 2 + 0.05, w * 0.55, 0.1 * s, strength=0.2)
    for d in (-1, 1):
        x = cx + d * (w / 2 - 0.12 * s)
        c.poly([(x - 0.22 * s, cy - h / 2 + 0.05), (x + 0.22 * s, cy - h / 2 + 0.05), (x, cy - h / 2 - 0.55 * s)], fill=FAM[fam], outline=edge,
               width=0.025)
    c.rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 0.08 * s, fill=ice, outline=edge, width=0.04 * s)
    c.poly([(cx - 0.35 * s, cy - h / 2), (cx + 0.35 * s, cy - h / 2), (cx, cy - h / 2 - 0.7 * s)], fill=FAM[fam], outline=edge, width=0.025)
    cw = 0.5 * s
    for r in range(3):
        for k in range(3):
            x, y = cx + (k - 1) * cw * 1.18, cy - 0.05 * s + (r - 1) * cw * 1.12
            c.rrect(x - cw / 2, y - cw / 2, x + cw / 2, y + cw / 2, 0.08 * s, fill=(206, 214, 246), outline=edge, width=0.025)
            if r * 3 + k == n:
                c.paste(emoji("princess-emoji"), x, y, box=(cw * 0.88, cw * 0.88))


def map_card(item):
    """The answer: a plain 3 x 3 map with a gold star where the princess was."""
    c = Canvas(3.0, 3.0, bg=(0, 0, 0, 0))
    cw = 0.78
    for r in range(3):
        for k in range(3):
            x, y = 1.5 + (k - 1) * cw, 1.5 + (r - 1) * cw
            c.rrect(x - cw / 2 + 0.03, y - cw / 2 + 0.03, x + cw / 2 - 0.03, y + cw / 2 - 0.03, 0.06, fill=(255, 255, 255),
                    outline=(170, 160, 200), width=0.035)
            if r * 3 + k == item["n"]:
                pts = [(x + (0.3 if i % 2 == 0 else 0.13) * math.cos(-math.pi / 2 + i * math.pi / 5),
                        y + 0.02 + (0.3 if i % 2 == 0 else 0.13) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
                c.poly(pts, fill=(250, 205, 80), outline=(200, 150, 50), width=0.03)
    return full_image(c)


def castle_hills(c, stations):
    """Twelve little castles in the snow; in each, the princess looks out of one window."""
    c.vgrad(0, 0, W, 2.6, (170, 196, 246), (246, 240, 255))
    S.sun(c, 25.6, 0.7, 0.36)
    for x, y, s in ((3.5, 0.6, 0.42), (11.0, 0.45, 0.36), (19.2, 0.6, 0.4)):
        S.cloud(c, x, y, s)
    hills = [(x, 2.45 - 0.25 * math.sin(x / 2.6 + 0.9)) for x in [W * i / 120 for i in range(121)]]
    c.vgrad(0, 2.0, W, H, (252, 252, 255), (228, 234, 252), hills + [(W, H), (0, H)])
    S.trail(c, stations, "skates")
    queen = art.princess(skin=0, style="braid", pose="wave", crown="tiara", seed=8, hair_col=(246, 238, 220),
                         dress_col=(206, 186, 246))
    c.paste(queen, W / 2, 5.4, h=2.6)
    c.paste(emoji("penguin"), W / 2 - 1.25, 6.45, h=0.7)
    c.paste(emoji("penguin"), W / 2 + 1.25, 6.5, h=0.65, flip=True)
    for st in stations:
        mini_castle(c, st["x"], st["y"], st["item"]["n"], st["fam"], s=1.12)
        badge(c, st["x"] - 1.45, st["y"] - 0.9, st["t"], st["fam"])


CASTLE_SPOTS = zigzag((2.4, 2.65, 2.45), (5.8, 6.05, 5.75), (1.85, 5.65, 9.45), (3.75, 7.55, 11.25))


def check_castles(tasks):
    need(tasks, ("castle",), 0, 8, "little castle")


# ------------------------------------------------------------------ circus day: shared pieces

ROWS = {1: [1], 2: [2], 3: [3], 4: [2, 2], 5: [3, 2], 6: [3, 3], 7: [4, 3]}
DICE = {1: [(0, 0)], 2: [(-1, 1), (1, -1)], 3: [(-1, 1), (0, 0), (1, -1)],
        4: [(-1, 1), (1, 1), (-1, -1), (1, -1)], 5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)],
        6: [(-1, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)]}
BALL_COLS = [(226, 84, 84), (250, 200, 70), (110, 180, 110), (170, 140, 220), (245, 150, 60), (226, 84, 84), (250, 200, 70)]


def rotated(c, w, h, cx, cy, deg, draw):
    """Draw on a w x h side canvas centred at (cx, cy), turned by deg (clockwise on the page)."""
    sub = Canvas(w, h, dpi=c.dpi, bg=(0, 0, 0, 0))
    draw(sub, w / 2, h / 2)
    im = sub.img.rotate(-deg, resample=Image.BICUBIC, expand=True)
    x, y = c.p(cx, cy)
    c.img.alpha_composite(im, (round(x - im.width / 2), round(y - im.height / 2)))


def full_image(c):
    """The canvas downscaled without cropping, so sprites of one kind share a floor line."""
    return c.img.resize((round(c.img.width / S.SS), round(c.img.height / S.SS)), Image.LANCZOS)


def caravan(c, cx, base, s=1.0, col=(250, 205, 80), roof=(170, 140, 220)):
    """A circus caravan on wheels: arched roof, round window, steps to the door."""
    w, h = 2.2 * s, 1.1 * s
    c.shadow(cx, base, w * 0.55, 0.1 * s, strength=0.18)
    for dx in (-0.65, 0.65):
        c.circle(cx + dx * s, base - 0.22 * s, 0.22 * s, fill=(170, 120, 80), outline=(120, 80, 50), width=0.03 * s)
        c.circle(cx + dx * s, base - 0.22 * s, 0.07 * s, fill=(120, 80, 50))
    c.rrect(cx - w / 2, base - 0.35 * s - h, cx + w / 2, base - 0.35 * s, 0.12 * s, fill=col, outline=mix(col, (90, 60, 50), 0.4),
            width=0.03 * s)
    top = base - 0.35 * s - h
    c.poly([(cx - w / 2 - 0.1 * s, top + 0.1 * s)] + [(cx - w / 2 - 0.1 * s + (w + 0.2 * s) * t, top + 0.1 * s - 0.45 * s *
                                                          math.sin(math.pi * t)) for t in [i / 20 for i in range(21)]],
           fill=roof, outline=mix(roof, (60, 40, 90), 0.35), width=0.03 * s)
    c.circle(cx - 0.45 * s, top + 0.5 * s, 0.22 * s, fill=(255, 246, 214), outline=mix(col, (90, 60, 50), 0.4), width=0.03 * s)
    c.rrect(cx + 0.2 * s, top + 0.25 * s, cx + 0.72 * s, base - 0.38 * s, 0.1 * s, fill=mix(col, (150, 90, 60), 0.35))


def camp(c, sky_top, sky_low, hz=3.15, sun_at=(2.4, 1.05)):
    """The circus camp on the meadow: caravans and the big top on the horizon."""
    c.vgrad(0, 0, W, hz + 0.4, sky_top, sky_low)
    S.sun(c, sun_at[0], sun_at[1], 0.42)
    for x, y, s in ((7.6, 0.6, 0.48), (19.6, 0.45, 0.42), (25.2, 0.75, 0.5)):
        S.cloud(c, x, y, s)
    far = [(x, hz - 0.5 - 0.3 * math.sin(x / 2.7 + 0.4) - 0.12 * math.sin(x / 1.1)) for x in [W * i / 120 for i in range(121)]]
    c.poly(far + [(W, hz + 0.6), (0, hz + 0.6)], fill=(206, 230, 184))
    big_top(c, W / 2, hz - 0.05, 0.62)
    caravan(c, W / 2 - 3.05, hz + 0.02, 0.42, col=(250, 205, 80), roof=(226, 92, 92))
    caravan(c, W / 2 + 3.05, hz + 0.02, 0.42, col=(150, 205, 140), roof=(170, 140, 220))
    near = [(x, hz - 0.12 * math.sin(x / 3.1 + 1.3)) for x in [W * i / 120 for i in range(121)]]
    c.vgrad(0, hz - 0.2, W, H, (196, 228, 166), (166, 212, 136), near + [(W, H), (0, H)])


def tulips(c, spots, seed=4):
    rnd = random.Random(seed)
    for x, y in spots:
        for _ in range(3):
            c.paste(emoji("tulip"), x + rnd.uniform(-0.4, 0.4), y + rnd.uniform(-0.1, 0.1), h=0.46)


def ringmaster(c, x, feet, h=2.6, pose="wave"):
    queen = art.princess(skin=0, style="braid", pose=pose, crown="tiara", seed=8, hair_col=(246, 238, 220),
                         dress_col=(206, 186, 246))
    c.paste(queen, x, feet - h / 2, h=h)


# ------------------------------------------------------------------ morning practice: juggling (same number)

ARC = {1: [(0.0, -0.45)], 2: [(-0.48, -0.26), (0.48, -0.26)], 3: [(-0.62, -0.06), (0.0, -0.56), (0.62, -0.06)]}


def juggler(c, cx, feet, kind, n, fam, idx, s=1.0):
    c.ellipse(cx, feet, 0.92 * s, 0.24 * s, fill=FILL[fam], outline=FAM[fam], width=0.05 * s)
    h = 1.5 * s
    c.paste(art.princess_variant(idx, "up"), cx, feet - h / 2 + 0.06 * s, h=h)
    head = feet - h - 0.05 * s
    guide = [(cx + 0.75 * s * math.cos(a), head + 0.1 * s - 0.62 * s * math.sin(a)) for a in [math.pi * i / 30 for i in range(31)]]
    lay = c.layer(cx - 1.0 * s, head - 1.0 * s, cx + 1.0 * s, head + 0.4 * s)
    for i in range(0, 30, 2):
        lay.line(guide[i:i + 2], fill=(255, 255, 255, 230), width=0.035 * s, caps=False)
    lay.commit()
    for dx, dy in ARC[n]:
        c.paste(emoji(kind), cx + dx * s, head + dy * s, box=(0.5 * s, 0.5 * s))


def juggling(c, stations):
    """Morning practice on the meadow: twelve acrobats juggle one, two or three things."""
    camp(c, (255, 226, 206), (255, 246, 232))
    tulips(c, ((0.6, 7.25), (12.4, 7.3), (15.9, 7.3), (27.7, 7.25)))
    ringmaster(c, W / 2 - 0.55, 6.95)
    c.paste(emoji("unicorn"), W / 2 + 1.05, 6.45, h=1.05, flip=True)
    glitter(c, curve((W / 2 - 1.6, 4.6), (W / 2 - 0.5, 3.6), (W / 2 + 0.6, 4.4)), 40, 3, spread=0.12, glints=4)
    for st in stations:
        it = st["item"]
        juggler(c, st["x"], st["y"], it["kind"], it["n"], st["fam"], st["t"] * 5 + 2, s=1.2)
        badge(c, st["x"] - 1.3, st["y"] - 0.7, st["t"], st["fam"])


JUGGLE_SPOTS = zigzag((3.45, 3.7, 3.5), (7.15, 7.25, 7.1), (1.8, 5.4, 9.0), (3.6, 7.2, 10.8))
JUGGLE_KINDS = (("heart", "star"), ("strawberry", "moon"))


def check_jugglers(tasks):
    for t, it in tasks.items():
        fam = it.get("fam") or 0
        if it["kind"] not in JUGGLE_KINDS[fam] or not 1 <= it["n"] <= 3:
            raise SystemExit(f"juggler {t} juggles 1 to 3 of {' or '.join(JUGGLE_KINDS[fam])}")


# ------------------------------------------------------------------ breakfast: count and match

def drum(c, cx, top, fam, w=2.6, h=0.5):
    """A circus podium: a low drum in the family colour with a gold band."""
    c.shadow(cx, top + h + 0.05, w * 0.5, 0.12, strength=0.2)
    side = [(cx - w / 2, top)] + [(cx - w / 2 + w * t, top + h + 0.16 * math.sin(math.pi * t)) for t in
                                  [i / 30 for i in range(31)]] + [(cx + w / 2, top)]
    c.poly(side, fill=FAM[fam], outline=mix(FAM[fam], (60, 30, 70), 0.35), width=0.03)
    c.line([(cx - w / 2 + w * t, top + h * 0.5 + 0.13 * math.sin(math.pi * t)) for t in [i / 30 for i in range(31)]],
           fill=GOLD, width=0.08, caps=False)
    c.ellipse(cx, top, w / 2, 0.2, fill=FILL[fam], outline=mix(FAM[fam], (60, 30, 70), 0.35), width=0.03)


def crowd(c, cx, base, kind, n, h, flip=False, gap=0.74):
    """n animals standing in rows on a surface at y = base; the back row is raised and staggered."""
    rows = ROWS[n]
    back = len(rows) == 2
    for r, k in enumerate(rows):
        y = base - (0.5 if back and r == 0 else 0.0)
        shift = (gap / 2 if back and r == 0 and k == rows[-1] else 0.0)
        for j in range(k):
            c.paste(emoji(kind), cx + (j - (k - 1) / 2) * gap + shift, y - h / 2, h=h, flip=flip)


def breakfast(c, stations):
    """Breakfast in the camp: seals and puppies wait on their podiums."""
    camp(c, (255, 232, 210), (255, 248, 236))
    tulips(c, ((0.6, 7.3), (27.7, 7.3)))
    ringmaster(c, W / 2, 6.9)
    c.paste(emoji("unicorn"), W / 2 + 1.55, 6.55, h=0.95, flip=True)
    for st in stations:
        it, x, y = st["item"], st["x"], st["y"]
        drum(c, x, y, st["fam"], w=3.0)
        crowd(c, x, y + 0.08, it["kind"], it["n"], 0.64 if it["kind"] == "seal" else 0.7, flip=x < W / 2, gap=0.84)
        badge(c, x - 1.6, y - 0.15, st["t"], st["fam"])


FEED_SPOTS = zigzag((2.5, 2.85, 2.55), (6.1, 6.4, 6.05), (1.95, 5.65, 9.35), (3.8, 7.5, 11.1))


def check_breakfast(tasks):
    need(tasks, ("seal", "puppy"), 1, 6, "breakfast")


# ------------------------------------------------------------------ giant dice on the meadow

def big_die(c, cx, cy, n, fam, s=1.0):
    """A die resting on the grass, pips on the front face only, in the family colour."""
    f, d = 0.8 * s, 0.34 * s
    rim = mix(FAM[fam], (60, 30, 70), 0.2)
    c.shadow(cx + 0.18 * s, cy + f + 0.04, f * 1.25, 0.14 * s, strength=0.22)
    c.poly([(cx - f, cy - f), (cx - f + d, cy - f - d), (cx + f + d, cy - f - d), (cx + f, cy - f)], fill=(255, 255, 255),
           outline=rim, width=0.035 * s)
    c.poly([(cx + f, cy - f), (cx + f + d, cy - f - d), (cx + f + d, cy + f - d), (cx + f, cy + f)], fill=FILL[fam], outline=rim,
           width=0.035 * s)
    c.rrect(cx - f, cy - f, cx + f, cy + f, 0.16 * s, fill=(255, 255, 255), outline=rim, width=0.06 * s)
    for a, b in DICE[n]:
        c.circle(cx + a * 0.44 * s, cy - b * 0.44 * s, 0.15 * s, fill=INK[fam])


def dice_meadow(c, stations):
    """Late morning: the princess and the unicorn roll giant dice across the meadow."""
    camp(c, (226, 236, 252), (255, 246, 232), sun_at=(5.5, 0.8))
    tulips(c, ((0.6, 7.3), (12.0, 7.35), (16.3, 7.35), (27.7, 7.3)))
    ringmaster(c, W / 2 - 0.4, 6.95, pose="up")
    c.paste(emoji("unicorn"), W / 2 + 1.15, 6.45, h=1.0, flip=True)
    glitter(c, curve((W / 2 - 1.3, 4.0), (W / 2 - 0.4, 3.2), (W / 2 + 0.7, 3.9)), 50, 8, spread=0.14, glints=5)
    for st in stations:
        big_die(c, st["x"], st["y"], st["item"]["n"], st["fam"])
        badge(c, st["x"] - 1.05, st["y"] - 1.1, st["t"], st["fam"])


DICE_SPOTS = zigzag((2.0, 2.35, 2.05), (5.75, 6.0, 5.7), (1.55, 5.2, 8.9), (3.4, 7.1, 10.75))


def check_dice(tasks):
    need(tasks, ("dice",), 1, 6, "dice meadow")


# ------------------------------------------------------------------ the balloon contest and the bubble act (comparing)

def balloon_bunch(c, ax, ay, n, s=1.0):
    """n balloons above an animal at (ax, ay); the strings meet at its head."""
    rows = list(reversed(ROWS[n]))
    pts = []
    for r, k in enumerate(rows):
        y = ay - (1.05 + 0.5 * (len(rows) - 1 - r)) * s
        for j in range(k):
            pts.append((ax + (j - (k - 1) / 2) * 0.42 * s, y))
    for x, y in pts:
        c.line([(x, y + 0.22 * s), (ax, ay - 0.38 * s)], fill=(170, 160, 170), width=0.015, caps=False)
    for x, y in sorted(pts, key=lambda p: p[1]):
        c.paste(emoji("balloon"), x, y, h=0.5 * s)


def bubble_cloud(c, ax, ay, n, s=1.0):
    """n soap bubbles of one size floating in rows above an animal at (ax, ay)."""
    rows = list(reversed(ROWS[n]))
    for r, k in enumerate(rows):
        y = ay - (0.95 + 0.46 * (len(rows) - 1 - r)) * s
        for j in range(k):
            x = ax + (j - (k - 1) / 2) * 0.44 * s
            lay = c.layer(x - 0.25 * s, y - 0.25 * s, x + 0.25 * s, y + 0.25 * s)
            lay.circle(x, y, 0.19 * s, fill=(236, 244, 255, 170), outline=(150, 170, 220, 255), width=0.03 * s)
            lay.ellipse(x - 0.07 * s, y - 0.08 * s, 0.05 * s, 0.035 * s, fill=(255, 255, 255, 240))
            lay.commit()


def duel(c, cx, cy, it, fam, s=1.0, bunch=balloon_bunch, apart=0.78):
    c.rrect(cx - 1.55 * s, cy + 0.32 * s, cx + 1.55 * s, cy + 0.58 * s, 0.1 * s, fill=FILL[fam], outline=FAM[fam], width=0.045 * s)
    for side, (name, n) in zip((-1, 1), ((it["a"], it["na"]), (it["b"], it["nb"]))):
        ax = cx + side * apart * s
        bunch(c, ax, cy, n, s)
        c.paste(emoji(name), ax, cy, box=(0.72 * s, 0.72 * s))


def bubble_act(c, stations):
    """Evening in the big top: the bubble act. Every animal blows bubbles; who blew more?"""
    tent_inside(c, 0.16, bulbs=False)
    for st in stations:
        spotlight(c, st["x"] * 0.5 + W / 4, st["x"], st["y"] + 0.3, 1.2)
    c.shadow(W / 2, 6.95, 0.75, 0.13)
    c.rrect(W / 2 - 0.7, 5.95, W / 2 + 0.7, 6.95, 0.1, fill=CIRCUS_RED, outline=(170, 60, 70), width=0.04)
    c.line([(W / 2 - 0.7, 6.45), (W / 2 + 0.7, 6.45)], fill=GOLD, width=0.08, caps=False)
    ringmaster(c, W / 2, 6.0, pose="wave")
    for st in stations:
        duel(c, st["x"], st["y"], st["item"], st["fam"], s=1.15, bunch=bubble_cloud, apart=0.9)
        badge(c, st["x"] - 1.62, st["y"] + 0.12, st["t"], st["fam"])


def contest(c, stations):
    """Noon: the balloon contest. Every animal holds a bunch; who holds more?"""
    camp(c, (190, 222, 252), (250, 246, 236), sun_at=(14.2, 0.55))
    bunting_line(c, 0.0, 0.25, W, 0.25, 0.75, seed=1)
    tulips(c, ((0.6, 7.3), (27.7, 7.3)))
    ringmaster(c, W / 2, 6.95)
    for st in stations:
        duel(c, st["x"], st["y"], st["item"], st["fam"], s=1.15)
        badge(c, st["x"] - 1.62, st["y"] + 0.12, st["t"], st["fam"])


CONTEST_SPOTS = zigzag((2.95, 3.25, 3.0), (6.7, 6.85, 6.65), (2.0, 5.9, 9.75), (3.95, 7.8, 11.6))


def check_contest(tasks):
    for t, it in tasks.items():
        if it["kind"] != "compare" or not (1 <= it["na"] <= 6 and 1 <= it["nb"] <= 6):
            raise SystemExit(f"contest {t} compares two bunches of 1 to 6 balloons")


# ------------------------------------------------------------------ the circus trains bring presents and stars

def wagon(c, cx, cy, kind, n, fam):
    """Open circus wagon; (cx, cy) is the middle of its wheel line. n things ride in two rows."""
    w = 1.74
    for dx in (-0.52, 0.52):
        c.circle(cx + dx, cy, 0.2, fill=(120, 90, 80), outline=(80, 60, 50), width=0.03)
        c.circle(cx + dx, cy, 0.06, fill=GOLD)
    rows = ROWS[n]
    back = len(rows) == 2
    for r, k in enumerate(rows):
        y = cy - 0.78 - (0.3 if back and r == 0 else 0.0)
        for j in range(k):
            c.paste(emoji(kind), cx + (j - (k - 1) / 2) * 0.44 + (0.22 if back and r == 0 and k == rows[-1] else 0), y, box=(0.4, 0.4))
    c.rrect(cx - w / 2, cy - 0.72, cx + w / 2, cy - 0.12, 0.1, fill=FAM[fam], outline=mix(FAM[fam], (60, 30, 70), 0.35),
            width=0.03)
    c.line([(cx - w / 2 + 0.1, cy - 0.42), (cx + w / 2 - 0.1, cy - 0.42)], fill=GOLD, width=0.06, caps=False)


def locomotive(c, cx, cy, face_right=True):
    d = 1 if face_right else -1
    c.circle(cx - d * 0.55, cy, 0.24, fill=(120, 90, 80), outline=(80, 60, 50), width=0.03)
    c.circle(cx + d * 0.45, cy, 0.24, fill=(120, 90, 80), outline=(80, 60, 50), width=0.03)
    c.rrect(cx - 0.45 - d * 0.35, cy - 1.45, cx + 0.45 - d * 0.35, cy - 0.15, 0.08, fill=CIRCUS_RED, outline=(150, 50, 50), width=0.03)
    c.rrect(cx - 0.35 - d * 0.35, cy - 1.32, cx + 0.35 - d * 0.35, cy - 0.85, 0.06, fill=(255, 246, 214))
    c.rrect(min(cx + d * 0.1, cx + d * 1.15), cy - 0.85, max(cx + d * 0.1, cx + d * 1.15), cy - 0.15, 0.25, fill=(250, 205, 80),
            outline=(200, 150, 50), width=0.03)
    c.rrect(cx + d * 0.72 - 0.11, cy - 1.35, cx + d * 0.72 + 0.11, cy - 0.8, 0.04, fill=(90, 80, 90))
    for k, (dx, dy, r) in enumerate(((0.75, -1.6, 0.2), (0.55, -1.95, 0.26), (0.2, -2.25, 0.3))):
        c.circle(cx + d * dx, cy + dy, r, fill=(255, 255, 255, 230))


def track_path(left=True):
    pts = [(0.1, 2.15), (3.3, 2.55), (6.5, 3.95), (9.4, 5.35), (12.4, 6.05)]
    if not left:
        pts = [(W - x, y) for x, y in reversed(pts)]
    return S.catmull(pts, 18)


def along_at(path, dist):
    """Point and slope angle (degrees) at arc length dist along a polyline."""
    d = 0.0
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        seg = math.dist((x0, y0), (x1, y1))
        if d + seg >= dist and seg > 0:
            t = (dist - d) / seg
            return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t), math.degrees(math.atan2(y1 - y0, x1 - x0))
        d += seg
    (x0, y0), (x1, y1) = path[-2], path[-1]
    return path[-1], math.degrees(math.atan2(y1 - y0, x1 - x0))


def path_len(path):
    return sum(math.dist(a, b) for a, b in zip(path, path[1:]))


def rails(c, path):
    for x, y, a in S.along(path, 0.32):
        dx, dy = -0.2 * math.sin(a), 0.2 * math.cos(a)
        c.line([(x - dx, y - dy), (x + dx, y + dy)], fill=(176, 140, 110), width=0.08, caps=False)
    for off in (-0.13, 0.13):
        c.line([(x - off * math.sin(a), y + off * math.cos(a)) for x, y, a in S.along(path, 0.05)], fill=(150, 150, 160), width=0.045,
               caps=False)


TRAIN_STEP, LOCO_AT, FIRST_AT = 1.86, 0.95, 2.62      # arc lengths from the station end of each track


def train_spots():
    """Wagon spots along the two tracks: pink 1-6 from the far left, blue 7-12 from the station out."""
    left, right = track_path(True), track_path(False)
    end = path_len(left)
    spots = [along_at(left, end - FIRST_AT - (5 - k) * TRAIN_STEP)[0] for k in range(6)]
    spots += [along_at(right, FIRST_AT + k * TRAIN_STEP)[0] for k in range(6)]
    return [(round(x, 3), round(y, 3)) for x, y in spots]


def trains(c, stations):
    """Afternoon: two circus trains bring presents and stars; the princess waits on the platform."""
    camp(c, (255, 226, 200), (255, 244, 226), sun_at=(25.8, 0.9))
    c.shadow(W / 2, 7.15, 2.0, 0.14)
    c.rrect(W / 2 - 1.95, 6.45, W / 2 + 1.95, 7.05, 0.08, fill=(236, 214, 186), outline=(196, 160, 120), width=0.035)
    ringmaster(c, W / 2, 6.5)
    left, right = track_path(True), track_path(False)
    rails(c, left)
    rails(c, right)
    for path, fwd, at in ((left, True, path_len(left) - LOCO_AT), (right, False, LOCO_AT)):
        (x, y), a = along_at(path, at)
        rotated(c, 3.0, 5.0, x, y, a, lambda sub, ox, oy, f=fwd: locomotive(sub, ox, oy, face_right=f))
    for st in stations:
        path = left if st["t"] <= 6 else right
        it = st["item"]
        best = min(range(200), key=lambda i: math.dist(along_at(path, i * path_len(path) / 199)[0], (st["x"], st["y"])))
        _, a = along_at(path, best * path_len(path) / 199)
        rotated(c, 2.6, 3.6, st["x"], st["y"], a, lambda sub, ox, oy, it=it, fam=st["fam"]: wagon(sub, ox, oy, it["kind"], it["n"], fam))
    for st in stations:
        badge(c, st["x"], st["y"] + 0.66, st["t"], st["fam"])


def check_trains(tasks):
    need(tasks, ("gift", "star"), 1, 6, "train")


# ------------------------------------------------------------------ the finger theatre (fingers to dice)

def puppet_booth(c, cx, base, fam, w=2.2, h=0.95):
    """A little puppet theatre: a striped front in the family colour under a gold ledge."""
    dark = mix(FAM[fam], (60, 30, 70), 0.35)
    c.shadow(cx, base, w * 0.55, 0.1, strength=0.2)
    c.rrect(cx - w / 2, base - h, cx + w / 2, base, 0.08, fill=FAM[fam], outline=dark, width=0.03)
    for k in range(1, 6, 2):
        x0 = cx - w / 2 + k * w / 6
        c.rrect(x0, base - h + 0.12, x0 + w / 6, base - 0.06, 0.03, fill=mix(FAM[fam], (255, 255, 255), 0.35))
    c.rrect(cx - w / 2 - 0.1, base - h - 0.14, cx + w / 2 + 0.1, base - h + 0.05, 0.05, fill=GOLD, outline=GOLD_DARK, width=0.025)
    for d in (-1, 1):
        x = cx + d * (w / 2 + 0.06)
        drape = [(x, base - h - 1.6)] + [(x - d * (0.08 + 0.28 * t * t), base - h - 1.6 + 1.5 * t) for t in [i / 10 for i in range(11)]]
        drape += [(x, base - h - 0.1)]
        c.poly(drape, fill=CIRCUS_RED, outline=(170, 60, 70), width=0.02)
    c.rrect(cx - w / 2 - 0.12, base - h - 1.72, cx + w / 2 + 0.12, base - h - 1.56, 0.05, fill=GOLD, outline=GOLD_DARK, width=0.02)


def hands(c, cx, top, n, start="index", h=1.6):
    """Raised hands as the child sees her own: up to five on the left hand, then the right one."""
    if n <= 5:
        sp = art.hand(n, side="left", start=start)
        c.paste(sp, cx, top - h / 2 + 0.32, h=h)
        return
    for dx, k, side in ((-0.5, 5, "left"), (0.5, n - 5, "right")):
        sp = art.hand(k, side=side, start=start)
        c.paste(sp, cx + dx, top - h * 0.88 / 2 + 0.32, h=h * 0.88)


def finger_booth(c, cx, base, n, fam, start="index"):
    hands(c, cx, base - 0.95, n, start)
    puppet_booth(c, cx, base, fam)


def finger_theatre(c, stations):
    """Late morning: the finger theatre. Hands rise above twelve little stages."""
    camp(c, (236, 232, 252), (255, 246, 232), sun_at=(4.8, 0.75))
    tulips(c, ((0.6, 7.3), (12.3, 7.35), (16.0, 7.35), (27.7, 7.3)))
    ringmaster(c, W / 2, 7.0, pose="up")
    c.paste(emoji("unicorn"), W / 2 + 1.25, 6.55, h=0.95, flip=True)
    for st in stations:
        it = st["item"]
        finger_booth(c, st["x"], st["y"], it["n"], st["fam"], it.get("fingers", "index"))
        badge(c, st["x"] - 1.38, st["y"] - 0.55, st["t"], st["fam"])


FINGER_SPOTS = zigzag((3.65, 3.9, 3.7), (7.2, 7.35, 7.15), (1.85, 5.6, 9.35), (3.7, 7.5, 11.15))


def check_fingers(tasks):
    need(tasks, ("fingers",), 1, 6, "finger theatre")


# ------------------------------------------------------------------ lights out: spotlights (counting a scattered set)

def spot_disc(c, cx, cy, kind, n, fam, seed, r=1.05):
    """A spotlight on the tent wall with n tokens scattered inside, none touching."""
    glow = c.layer(cx - r - 0.3, cy - r - 0.3, cx + r + 0.3, cy + r + 0.3)
    glow.circle(cx, cy, r + 0.12, fill=(255, 244, 196, 150))
    glow.commit(blur=0.12)
    c.circle(cx, cy, r, fill=(255, 251, 232), outline=FAM[fam], width=0.07)
    for dx, dy in S.scatter(n, 1.3, 1.08, 0.5, seed):
        c.paste(emoji(kind), cx + dx, cy + dy, box=(0.42, 0.42))


def spotlights(c, stations):
    """The show begins: the lights go down and twelve spotlights shine on the tent wall."""
    tent_inside(c, 0.12, bulbs=False)
    shade = c.layer(0, 0, W, H)
    shade.poly([(0, 0), (W, 0), (W, H), (0, H)], fill=(60, 40, 80, 40))
    shade.commit()
    for st in stations:
        spotlight(c, st["x"] * 0.5 + W / 4, st["x"], st["y"] + 0.6, 1.1)
    c.shadow(W / 2, 6.95, 0.75, 0.13)
    c.rrect(W / 2 - 0.7, 5.95, W / 2 + 0.7, 6.95, 0.1, fill=CIRCUS_RED, outline=(170, 60, 70), width=0.04)
    c.line([(W / 2 - 0.7, 6.45), (W / 2 + 0.7, 6.45)], fill=GOLD, width=0.08, caps=False)
    ringmaster(c, W / 2, 6.0, pose="wave")
    for st in stations:
        it = st["item"]
        spot_disc(c, st["x"], st["y"], it["kind"], it["n"], st["fam"], st["t"] * 13 + it["n"])
        badge(c, st["x"] - 1.05, st["y"] - 0.92, st["t"], st["fam"])


SPOT_SPOTS = zigzag((1.7, 2.0, 1.75), (5.5, 5.8, 5.45), (2.0, 5.85, 9.7), (3.95, 7.8, 11.4))


def check_spots(tasks):
    for t, it in tasks.items():
        if it["kind"] != ("heart" if (it.get("fam") or 0) == 0 else "star") or not 1 <= it["n"] <= 6:
            raise SystemExit(f"spotlight {t} shows 1 to 6 hearts (pink) or stars (blue)")


# ------------------------------------------------------------------ the ring toss (comparing written numbers)

def score_sign(c, x, y, n, fam, s=1.0):
    c.line([(x, y + 0.4 * s), (x, y + 0.85 * s)], fill=(170, 124, 70), width=0.07 * s)
    c.rrect(x - 0.44 * s, y - 0.44 * s, x + 0.44 * s, y + 0.44 * s, 0.1 * s, fill=(255, 255, 255), outline=FAM[fam], width=0.06 * s)
    c.text(x, y + 0.03 * s, str(n), 0.66 * s, INK[fam])


def score_duel(c, cx, cy, it, fam, s=1.0):
    c.rrect(cx - 1.4 * s, cy + 0.32 * s, cx + 1.4 * s, cy + 0.56 * s, 0.1 * s, fill=FILL[fam], outline=FAM[fam], width=0.045 * s)
    for side, (name, n) in zip((-1, 1), ((it["a"], it["na"]), (it["b"], it["nb"]))):
        ax = cx + side * 0.72 * s
        score_sign(c, ax, cy - 1.25 * s, n, fam, s)
        c.paste(emoji(name), ax, cy, box=(0.86 * s, 0.86 * s))


def toss_peg(c, x, base):
    c.shadow(x, base, 0.5, 0.08)
    c.ellipse(x, base - 0.05, 0.45, 0.12, fill=(214, 176, 120), outline=(160, 120, 70), width=0.025)
    c.rrect(x - 0.05, base - 1.0, x + 0.05, base - 0.05, 0.03, fill=(214, 176, 120), outline=(160, 120, 70), width=0.02)
    c.ellipse(x, base - 0.25, 0.32, 0.09, outline=(250, 200, 70), width=0.07)


def ring_toss(c, stations):
    """Evening in the big top: the ring toss. Each sign shows how many rings landed."""
    tent_inside(c, 0.15)
    ringmaster(c, W / 2 - 0.35, 6.95)
    toss_peg(c, W / 2 + 1.1, 7.1)
    for st in stations:
        score_duel(c, st["x"], st["y"], st["item"], st["fam"], s=1.1)
        badge(c, st["x"] - 1.5, st["y"] + 0.1, st["t"], st["fam"])


TOSS_SPOTS = zigzag((2.95, 3.2, 2.95), (6.65, 6.85, 6.6), (1.95, 5.8, 9.65), (3.9, 7.75, 11.5))


def check_toss(tasks):
    check_contest(tasks)


# ------------------------------------------------------------------ the magic show: coin chests (five and some more)

def coin(c, x, y, r):
    c.circle(x, y, r, fill=(255, 210, 90), outline=(200, 150, 40), width=0.025)
    c.circle(x, y, r * 0.62, outline=(236, 180, 60), width=0.02)
    c.circle(x - r * 0.3, y - r * 0.3, r * 0.22, fill=(255, 244, 200))


def chest(c, cx, cy, n, fam, s=1.0):
    """An open chest whose front tray is a ten-frame: five on top, then the rest below."""
    w, h = 2.5 * s, 1.15 * s
    dark = mix(FAM[fam], (60, 30, 70), 0.45)
    top = cy - h / 2
    lid = [(cx - w / 2 + 0.06 * s, top), (cx + w / 2 - 0.06 * s, top), (cx + w / 2 - 0.16 * s, top - 0.62 * s)]
    lid += [(cx + (w / 2 - 0.16 * s) * math.cos(math.pi * t), top - 0.62 * s - 0.22 * s * math.sin(math.pi * t)) for t in
            [i / 16 for i in range(17)]]
    lid += [(cx - w / 2 + 0.16 * s, top - 0.62 * s)]
    c.poly(lid, fill=(120, 80, 70), outline=GOLD_DARK, width=0.05 * s)
    c.poly([(x, y + 0.08 * s) for x, y in lid[3:-1]] + [(cx + w / 2 - 0.3 * s, top - 0.1 * s), (cx - w / 2 + 0.3 * s, top - 0.1 * s)],
           fill=(150, 104, 90))
    c.rrect(cx - w / 2, top, cx + w / 2, cy + h / 2, 0.12 * s, fill=FAM[fam], outline=dark, width=0.035 * s)
    for x in (cx - w / 2 + 0.16 * s, cx + w / 2 - 0.16 * s):
        c.rrect(x - 0.07 * s, top + 0.02, x + 0.07 * s, cy + h / 2 - 0.02, 0.03 * s, fill=GOLD, outline=GOLD_DARK, width=0.015)
    cw = 0.42 * s
    tx, ty = cx - 2.5 * cw, cy - cw
    c.rrect(tx - 0.06 * s, ty - 0.06 * s, tx + 5 * cw + 0.06 * s, ty + 2 * cw + 0.06 * s, 0.06 * s, fill=(255, 246, 222),
            outline=GOLD_DARK, width=0.03 * s)
    for r in range(3):
        c.line([(tx, ty + r * cw), (tx + 5 * cw, ty + r * cw)], fill=(214, 180, 120), width=0.02 * s, caps=False)
    for k in range(6):
        c.line([(tx + k * cw, ty), (tx + k * cw, ty + 2 * cw)], fill=(214, 180, 120), width=0.02 * s, caps=False)
    for i in range(n):
        r, k = divmod(i, 5)
        coin(c, tx + (k + 0.5) * cw, ty + (r + 0.5) * cw, 0.165 * s)


def magic_cloud(c, cx, cy, w):
    lay = c.layer(cx - w, cy - 0.5, cx + w, cy + 0.5)
    for dx, r in ((-0.55, 0.22), (-0.2, 0.28), (0.2, 0.26), (0.55, 0.2)):
        lay.circle(cx + dx * w, cy, r, fill=(255, 255, 255, 220))
    lay.commit(blur=0.03)


def magic_show(c, stations):
    """Evening in the big top: the magician princess makes twelve chests float."""
    tent_inside(c, 0.2, bulbs=False)
    for st in stations:
        spotlight(c, st["x"] * 0.5 + W / 4, st["x"], st["y"] + 0.9, 1.1)
    c.shadow(W / 2, 6.95, 0.75, 0.13)
    c.rrect(W / 2 - 0.7, 5.95, W / 2 + 0.7, 6.95, 0.1, fill=(170, 140, 220), outline=(120, 90, 170), width=0.04)
    c.line([(W / 2 - 0.7, 6.45), (W / 2 + 0.7, 6.45)], fill=GOLD, width=0.08, caps=False)
    queen = art.princess(skin=0, style="braid", pose="wand", crown="tiara", seed=8, hair_col=(246, 238, 220),
                         dress_col=(206, 186, 246))
    c.paste(queen, W / 2, 4.6, h=2.75)
    glitter(c, curve((W / 2 + 0.6, 3.6), (W / 2 + 2.4, 1.8), (W / 2 + 4.6, 1.6)), 90, 9, spread=0.18, glints=9)
    glitter(c, curve((W / 2 - 0.6, 3.6), (W / 2 - 2.4, 1.8), (W / 2 - 4.6, 1.6)), 90, 10, spread=0.18, glints=9)
    for st in stations:
        magic_cloud(c, st["x"], st["y"] + 0.72, 1.1)
        chest(c, st["x"], st["y"], st["item"]["n"], st["fam"])
        badge(c, st["x"] - 1.45, st["y"] - 0.95, st["t"], st["fam"])


CHEST_SPOTS = zigzag((1.85, 2.3, 1.9), (5.55, 5.9, 5.5), (1.85, 5.65, 9.5), (3.75, 7.6, 11.1))


def check_chests(tasks):
    need(tasks, ("chest",), 3, 8, "magic chest")


# ------------------------------------------------------------------ the seals' ball towers (one more)

def ball(c, x, y, r, col):
    c.circle(x, y, r, fill=col, outline=mix(col, (60, 30, 50), 0.3), width=0.025)
    c.ellipse(x, y, r, r * 0.3, fill=(255, 255, 255, 200))
    c.circle(x - r * 0.35, y - r * 0.4, r * 0.22, fill=(255, 255, 255, 210))


def ball_stack(c, x, base, n, r=0.17):
    for k in range(n):
        ball(c, x, base - r - k * 2 * r * 0.96, r, BALL_COLS[k])


def seal_act(c, cx, top, n, fam, s=1.0, face_right=False):
    """A seal on a drum balancing n balls on its head."""
    drum(c, cx, top, fam, w=1.55 * s, h=0.4 * s)
    sw = 1.15 * s
    sp = emoji("seal")
    sh = sw * sp.height / sp.width
    c.paste(sp, cx, top + 0.06 - sh / 2, w=sw, flip=face_right)
    hx = cx + (1 if face_right else -1) * (0.5 - 0.277) * sw
    ball_stack(c, hx, top + 0.06 - sh + 0.03, n, 0.235 * s)


def ball_tower_sprite(item):
    """The answer: n balls on one floor line, so one more is one ball taller."""
    c = Canvas(3.0, 3.0, bg=(0, 0, 0, 0))
    c.ellipse(1.5, 2.8, 0.45, 0.1, fill=(214, 206, 226))
    ball_stack(c, 1.5, 2.8, item["n"], 0.2)
    return full_image(c)


def seal_show(c, stations):
    """Later in the evening: the seals' act. Each balances a tower of balls, and one more is coming."""
    tent_inside(c, 0.32, bulbs=False)
    for st in stations:
        spotlight(c, st["x"] * 0.5 + W / 4, st["x"], st["y"] + 0.5, 0.9)
    ringmaster(c, W / 2 + 0.45, 6.95, pose="up")
    c.paste(emoji("unicorn"), W / 2 - 0.85, 6.55, h=0.95)
    lay_x, lay_y = W / 2 + 1.45, 3.6
    ball(c, lay_x, lay_y, 0.24, (110, 180, 110))
    for k in range(5):
        c.circle(lay_x - 0.35 - k * 0.22, lay_y + 0.35 + k * 0.28, 0.035, fill=(255, 255, 255, 220))
    for st in stations:
        seal_act(c, st["x"], st["y"], st["item"]["n"], st["fam"], face_right=st["x"] < W / 2)
        badge(c, st["x"] - (0.62 if st["x"] < W / 2 else -0.62), st["y"] - 1.45, st["t"], st["fam"])


SEAL_SPOTS = mirror([(1.25 + 2.02 * k, 6.15 if k % 2 == 0 else 6.65) for k in range(6)])


def check_seals(tasks):
    need(tasks, ("balls",), 1, 6, "seal act")


# ------------------------------------------------------------------ the party after the show (take-away)

def cookie(c, x, y, r):
    c.circle(x, y, r, fill=(222, 170, 110), outline=(170, 120, 70), width=0.025)
    rnd = random.Random(round(x * 100 + y * 10))
    for _ in range(5):
        a, d = rnd.uniform(0, 6.3), rnd.uniform(0, r * 0.65)
        c.circle(x + d * math.cos(a), y + d * math.sin(a), r * 0.14, fill=(110, 70, 50))


def crumbs(c, x, y, r):
    rnd = random.Random(round(x * 100 + y * 7))
    for _ in range(9):
        a, d = rnd.uniform(0, 6.3), rnd.uniform(0, r * 0.9)
        c.circle(x + d * math.cos(a), y + d * math.sin(a), rnd.uniform(0.02, 0.04), fill=(200, 150, 96))


def plate(c, cx, cy, n, fam, s=1.0):
    """A plate that held n + 1 cookies; one place is crumbs now, n cookies are left."""
    c.shadow(cx, cy + 0.42 * s, 1.35 * s, 0.14 * s, strength=0.25)
    c.ellipse(cx, cy, 1.4 * s, 0.62 * s, fill=(255, 255, 255), outline=FAM[fam], width=0.07 * s)
    c.ellipse(cx, cy, 1.08 * s, 0.42 * s, outline=mix(FAM[fam], (255, 255, 255), 0.5), width=0.03 * s)
    rows = ROWS[n + 1]
    spots = []
    for r, k in enumerate(rows):
        y = cy + ((r - (len(rows) - 1) / 2) * 0.44) * s
        for j in range(k):
            spots.append((cx + (j - (k - 1) / 2) * 0.52 * s, y))
    gone = spots[(n * 7 + 3) % len(spots)]
    for x, y in spots:
        if (x, y) == gone:
            crumbs(c, x, y, 0.2 * s)
        else:
            cookie(c, x, y, 0.21 * s)


def lanterns(c, x0, y0, x1, y1, sag, seed=0):
    pts = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)) for t in [i / 40 for i in range(41)]]
    c.line(pts, fill=(120, 100, 140), width=0.02, caps=False)
    glow = c.layer(min(x0, x1) - 0.5, min(y0, y1) - 0.5, max(x0, x1) + 0.5, max(y0, y1) + sag + 0.8)
    for i in range(2, 40, 4):
        x, y = pts[i]
        glow.circle(x, y + 0.2, 0.22, fill=(255, 220, 140, 120))
    glow.commit(blur=0.1)
    for i in range(2, 40, 4):
        x, y = pts[i]
        col = FLAGS[(i // 4 + seed) % len(FLAGS)]
        c.rrect(x - 0.11, y + 0.05, x + 0.11, y + 0.36, 0.08, fill=mix(col, (255, 240, 200), 0.3), outline=mix(col, (60, 40, 50), 0.3),
                width=0.02)


def party(c, stations):
    """Night: the party after the show. The unicorn has nibbled one cookie from every plate."""
    c.vgrad(0, 0, W, 3.6, (70, 58, 128), (150, 116, 178))
    rnd = random.Random(12)
    stars = c.layer(0, 0, W, 3.4)
    for _ in range(60):
        stars.circle(rnd.uniform(0.2, W - 0.2), rnd.uniform(0.15, 2.8), rnd.uniform(0.02, 0.05), fill=(255, 255, 255, 220))
    for _ in range(12):
        sparkle(stars, rnd.uniform(0.4, W - 0.4), rnd.uniform(0.2, 2.4), rnd.uniform(0.05, 0.1), fill=(255, 250, 220, 235))
    stars.commit()
    c.paste(emoji("moon"), 4.3, 0.85, h=0.95)
    top = big_top(c, W / 2, 3.35, 0.7, fade=0.0)
    hills = [(x, 3.3 - 0.18 * math.sin(x / 3.0 + 0.5)) for x in [W * i / 120 for i in range(121)]]
    c.vgrad(0, 3.0, W, H, (116, 150, 120), (86, 120, 100), hills + [(W, H), (0, H)])
    lanterns(c, 0.0, 0.45, W / 2 - 0.2, top + 0.4, 0.6, seed=0)
    lanterns(c, W / 2 + 0.2, top + 0.4, W, 0.45, 0.6, seed=2)
    c.shadow(W / 2, 7.2, 1.2, 0.12)
    c.paste(emoji("unicorn"), W / 2, 6.25, h=1.6, flip=True)
    for dx, dy in ((-0.55, 7.05), (-0.2, 7.2), (0.3, 7.1), (0.6, 7.25)):
        c.circle(W / 2 + dx, dy, 0.045, fill=(222, 170, 110))
    for st in stations:
        plate(c, st["x"], st["y"], st["item"]["n"], st["fam"], s=1.12)
        badge(c, st["x"] - 1.45, st["y"] - 0.72, st["t"], st["fam"])


PARTY_SPOTS = zigzag((3.0, 3.3, 3.05), (6.35, 6.65, 6.3), (2.15, 5.85, 9.5), (4.0, 7.65, 11.15))


def check_plates(tasks):
    need(tasks, ("plate",), 1, 6, "party plate")


# ------------------------------------------------------------------ registration

register("ticket_booth", ticket_queue, TICKET_SPOTS, check=check_tickets, example=(1.9, 1.3),
         station=lambda it: sprite(lambda c, x, y: ticket(c, x, y, it["n"], it.get("fam") or 0)))
register("tightrope", tightrope_tent, ROPE_SPOTS, check=check_ropes, example=(2.3, 1.6),
         station=lambda it: sprite(lambda c, x, y: tightrope(c, x, y + 0.45, it["n"], it.get("fam") or 0,
                                                              s=0.9, who=it.get("fam") or 0)))
register("bottle_post", bottle_post, BOTTLE_SPOTS, check=check_bottles, example=(2.1, 1.3),
         station=lambda it: sprite(lambda c, x, y: bottle(c, x - 0.25, y, chr(65 + it["n"]), it.get("fam") or 0, word=it.get("word"))))
register("necklaces", workshop, NECK_SPOTS, check=check_necklaces, example=(3.4, 1.3),
         station=lambda it: sprite(lambda c, x, y: necklace(c, x, y - 0.2, it["pic"], it["other"], it.get("fam") or 0),
                                   w=5.4, h=1.6))
register("juggling", juggling, JUGGLE_SPOTS, check=check_jugglers, example=(1.6, 1.6),
         station=lambda it: sprite(lambda c, x, y: juggler(c, x, y + 1.2, it["kind"], it["n"], it.get("fam") or 0, 12), w=2.4, h=3.0))
register("breakfast", breakfast, FEED_SPOTS, check=check_breakfast, example=(1.8, 1.6),
         station=lambda it: sprite(lambda c, x, y: (drum(c, x, y + 0.3, it.get("fam") or 0),
                                                    crowd(c, x, y + 0.38, it["kind"], it["n"], 0.6 if it["kind"] == "seal" else 0.66,
                                                          flip=True)), w=3.0, h=2.4))
register("dice_meadow", dice_meadow, DICE_SPOTS, check=check_dice, example=(1.4, 1.4),
         station=lambda it: sprite(lambda c, x, y: big_die(c, x - 0.15, y + 0.15, it["n"], it.get("fam") or 0), w=2.4, h=2.4))
register("contest", contest, CONTEST_SPOTS, check=check_contest, example=(1.9, 1.6),
         station=lambda it: sprite(lambda c, x, y: duel(c, x, y + 0.75, it, it.get("fam") or 0), w=3.4, h=3.2))
register("bubble_act", bubble_act, CONTEST_SPOTS, check=check_contest, example=(1.9, 1.6),
         station=lambda it: sprite(lambda c, x, y: duel(c, x, y + 0.7, it, it.get("fam") or 0, bunch=bubble_cloud, apart=0.9), w=3.6, h=3.0))
register("trains", trains, train_spots(), check=check_trains, example=(1.6, 1.4),
         station=lambda it: sprite(lambda c, x, y: wagon(c, x, y + 0.7, it["kind"], it["n"], it.get("fam") or 0), w=2.4, h=2.4))
register("magic_show", magic_show, CHEST_SPOTS, check=check_chests, example=(1.8, 1.4),
         station=lambda it: sprite(lambda c, x, y: chest(c, x, y + 0.3, it["n"], it.get("fam") or 0), w=2.8, h=2.4))
register("seal_show", seal_show, SEAL_SPOTS, check=check_seals, example=(1.4, 2.0),
         station=lambda it: sprite(lambda c, x, y: seal_act(c, x, y + 0.9, it["n"], it.get("fam") or 0, face_right=True), w=2.2, h=3.4))
register("party", party, PARTY_SPOTS, check=check_plates, example=(1.9, 1.3),
         station=lambda it: sprite(lambda c, x, y: plate(c, x, y, it["n"], it.get("fam") or 0), w=3.0, h=1.6))
register("finger_theatre", finger_theatre, FINGER_SPOTS, check=check_fingers, example=(1.5, 1.6),
         station=lambda it: sprite(lambda c, x, y: finger_booth(c, x, y + 1.05, it["n"], it.get("fam") or 0, it.get("fingers", "index")),
                                   w=2.8, h=3.0))
register("spotlights", spotlights, SPOT_SPOTS, check=check_spots, example=(1.4, 1.4),
         station=lambda it: sprite(lambda c, x, y: spot_disc(c, x, y, it["kind"], it["n"], it.get("fam") or 0, 1 * 13 + it["n"]),
                                   w=2.6, h=2.6))
register("ring_toss", ring_toss, TOSS_SPOTS, check=check_toss, example=(1.7, 1.6),
         station=lambda it: sprite(lambda c, x, y: score_duel(c, x, y + 0.75, it, it.get("fam") or 0), w=3.0, h=3.0))
register("twin_shells", twin_shells, SHELL_SPOTS, check=check_letters, example=(1.5, 1.4),
         station=lambda it: sprite(lambda c, x, y: letter_shell(c, x, y + 0.15, chr(65 + it["n"]), it.get("fam") or 0), w=2.6, h=2.4))
register("fish_school", fish_school, FISH_SPOTS, check=check_letters, example=(1.7, 1.3),
         station=lambda it: sprite(lambda c, x, y: big_fish(c, x + 0.2, y + 0.1, chr(65 + it["n"]), it.get("fam") or 0), w=3.4, h=2.2))
register("sea_finds", sea_finds, FIND_SPOTS, check=check_finds, example=(1.3, 1.3),
         station=lambda it: sprite(lambda c, x, y: find_bubble(c, x, y - 0.3, it["pic"], it.get("fam") or 0), w=2.0, h=2.6))
register("syllable_bubbles", syllable_bubbles, SYLL_SPOTS, check=check_syllables, example=(1.6, 1.4),
         station=lambda it: sprite(lambda c, x, y: syllable_fish(c, x + 0.4, y, it["text"], it.get("fam") or 0), w=3.0, h=2.4))
register("post_boats", post_boats, BOAT_SPOTS, check=check_boats, example=(1.8, 1.5),
         station=lambda it: sprite(lambda c, x, y: boat(c, x, y + 0.6, it["word"], it.get("fam") or 0), w=3.0, h=2.8))
register("beach_post", beach_post, PARCEL_SPOTS, check=check_parcels, example=(1.5, 1.3),
         station=lambda it: sprite(lambda c, x, y: parcel(c, x, y, it["pic"], it.get("fam") or 0), w=2.2, h=1.8))
register("palace_windows", palace_front, WINDOW_SPOTS, check=check_shapes, example=(1.4, 1.4),
         station=lambda it: sprite(lambda c, x, y: window(c, x, y, it["n"], it.get("fam") or 0), w=2.2, h=2.2))
register("winter_party", winter_party, ODD_SPOTS, check=check_odd, example=(2.6, 1.3),
         station=lambda it: sprite(lambda c, x, y: odd_group(c, x, y - 0.1, it, it.get("fam") or 0), w=4.2, h=1.9))
register("castle_hills", castle_hills, CASTLE_SPOTS, check=check_castles, example=(1.5, 1.6),
         station=lambda it: sprite(lambda c, x, y: mini_castle(c, x, y + 0.35, it["n"], it.get("fam") or 0), w=2.6, h=3.2))
S.KINDS["shape"] = shape_token
S.KINDS["map"] = map_card
S.KINDS["balls"] = ball_tower_sprite
S.SCENES["seal_show"]["example_answer"] = (1.1, 2.0)
