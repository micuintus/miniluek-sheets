#!/usr/bin/env python3
"""Printable worksheets for the miniLÜK control box (preschool mode: the open box lies on the sheet).

One A4 landscape page per exercise: 12 numbered tasks on top, the answer grid at the bottom under
the transparent lid (hinge at the lower paper edge), the control pattern printed in between.
Print at 100 % ("actual size").

Usage:
  python3 miniluek.py check SPEC.json
  python3 miniluek.py build SPEC.json -o sheets.pdf [--previews DIR] [--only S1,S3] [--key] [--fit]
  python3 miniluek.py fit-test -o fit.pdf
  python3 miniluek.py kinds
"""
import argparse
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art  # noqa: E402
from luek_model import check_pattern, pattern_library, pattern_of, placement_of, validate  # noqa: E402

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
DPI = 300
CM = DPI / 2.54
PW, PH = 29.7, 21.0
W, H = round(PW * CM), round(PH * CM)

PITCH = 4.10                                   # lid compartment pitch (cm), verified on a real box
COLS = [PW / 2 + (c - 2.5) * PITCH for c in range(6)]
LID_ROWS = [7.15, 3.05]                        # far from hinge, next to hinge (cm above lower edge)
CELL, TASK_CELL = 3.5, 3.4
TASK_ROWS = [18.7, 15.15]
TASK_POS = {t: (0, i) for i, t in enumerate([1, 2, 3, 7, 8, 9])}
TASK_POS.update({t: (1, i) for i, t in enumerate([4, 5, 6, 10, 11, 12])})

FONT_BOLD = str(ASSETS / "fonts" / "Andika-Bold.ttf")
FONT_REG = str(ASSETS / "fonts" / "Andika-Regular.ttf")
TILE_RGB = {"B": (30, 155, 215), "R": (230, 60, 47), "G": (46, 154, 78)}
CREAM = (250, 242, 205)
THEMES = {
    "pink": ((244, 167, 198), (194, 24, 91)), "lavender": ((199, 181, 234), (106, 63, 160)),
    "peach": ((250, 190, 160), (214, 84, 40)), "mint": ((160, 215, 185), (30, 130, 80)),
    "gold": ((240, 205, 120), (170, 115, 0)), "sky": ((160, 200, 240), (30, 100, 180)),
    "rose": ((235, 170, 190), (170, 40, 90)), "violet": ((200, 185, 240), (90, 60, 170)),
    "coral": ((248, 175, 165), (200, 60, 60)), "teal": ((150, 215, 215), (20, 120, 130)),
}
FAMILY = [  # a task and its answer share the frame colour
    {"frame": (236, 112, 170), "ink": (176, 30, 110), "fill": (252, 222, 236)},
    {"frame": (88, 150, 222), "ink": (30, 90, 180), "fill": (219, 234, 252)},
]
EMOJI_DIR = ASSETS / "emoji"
SPECIAL = {"dice", "numeral", "fingers", "jewelbox", "path", "princess", "compare"}


# ------------------------------------------------------------------ basics

def px(cm):
    return int(round(cm * CM))


def P(x, y):
    return px(x), px(PH - y)


_fonts = {}


def font(size_cm, bold=True):
    key = (size_cm, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, px(size_cm))
    return _fonts[key]


def text(d, x, y, s, size_cm, colour, bold=True, anchor="ls"):
    d.text(P(x, y), s, font=font(size_cm, bold), fill=colour, anchor=anchor)


def rrect(d, cx, cy, w, h, r, outline, fill=None, width=0.06):
    x0, y0 = P(cx - w / 2, cy + h / 2)
    x1, y1 = P(cx + w / 2, cy - h / 2)
    d.rounded_rectangle([x0, y0, x1, y1], radius=px(r), outline=outline, fill=fill, width=max(1, px(width)))


_sprites = {}


def emoji(name):
    key = ("emoji", name)
    if key not in _sprites:
        path = EMOJI_DIR / f"{name}.png"
        if not path.exists():
            raise SystemExit(f"unknown picture '{name}'; see: miniluek.py kinds")
        im = Image.open(path).convert("RGBA")
        _sprites[key] = im.crop(im.getbbox())
    return _sprites[key]


def princess_sprite(index, pose="down"):
    key = ("princess", index, pose)
    if key not in _sprites:
        _sprites[key] = art.princess_variant(index, pose)
    return _sprites[key]


def hand_sprite(n, side):
    key = ("hand", n, side)
    if key not in _sprites:
        _sprites[key] = art.hand(n, side=side)
    return _sprites[key]


def paste(img, sprite, cx, cy, h_cm=None, w_cm=None, box=None):
    """Paste centred at (cx, cy) cm, scaled to height h_cm or to fit box=(w, h)."""
    if box:
        k = min(px(box[0]) / sprite.width, px(box[1]) / sprite.height)
    elif h_cm:
        k = px(h_cm) / sprite.height
    else:
        k = px(w_cm) / sprite.width
    sp = sprite.resize((max(1, round(sprite.width * k)), max(1, round(sprite.height * k))), Image.LANCZOS)
    x, y = P(cx, cy)
    img.alpha_composite(sp, (x - sp.width // 2, y - sp.height // 2))


# ------------------------------------------------------------------ layouts

ROWS = {
    "row": {1: [1], 2: [2], 3: [3], 4: [2, 2], 5: [3, 2], 6: [3, 3], 7: [4, 3], 8: [4, 4]},
    "col": {1: [1], 2: [1, 1], 3: [1, 2], 4: [1, 2, 1], 5: [2, 1, 2], 6: [2, 2, 2], 7: [2, 3, 2], 8: [3, 2, 3]},
    "up": {1: [1], 2: [2], 3: [1, 2]},
    "down": {1: [1], 2: "diag", 3: [2, 1]},
}
DICE = {1: [(0, 0)], 2: [(-1, 1), (1, -1)], 3: [(-1, 1), (0, 0), (1, -1)],
        4: [(-1, 1), (1, 1), (-1, -1), (1, -1)], 5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)],
        6: [(-1, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)]}


def positions(n, style, sw, sh, seed=0, box=2.7):
    dx, dy = sw * 1.14, sh * 1.1
    if style == "scatter":
        if n == 1:
            return [(0.0, 0.0)]
        rnd = random.Random(seed * 101 + n)
        limx, limy = (box - sw) / 2, (box - sh) / 2
        for _ in range(4000):
            pts = []
            for _ in range(n):
                for _ in range(400):
                    p = (rnd.uniform(-limx, limx), rnd.uniform(-limy, limy))
                    if all(abs(p[0] - q[0]) >= dx or abs(p[1] - q[1]) >= dy for q in pts):
                        pts.append(p)
                        break
            if len(pts) == n:
                return pts
        raise RuntimeError("scatter failed")
    if style == "dice":
        return [(a * dx, b * dy) for a, b in DICE[n]]
    rows = ROWS[style][n]
    if rows == "diag":
        return [(-dx / 2, dy / 2), (dx / 2, -dy / 2)]
    pts, nr = [], len(rows)
    for i, k in enumerate(rows):
        y = ((nr - 1) / 2 - i) * dy
        pts += [((j - (k - 1) / 2) * dx, y) for j in range(k)]
    return pts


# ------------------------------------------------------------------ item drawing

def draw_dice(img, d, n, cx, cy, k, fam=None):
    side = 2.35 * k
    outline, pip = ((196, 70, 140), (92, 40, 120)) if fam is None else (FAMILY[fam]["frame"], FAMILY[fam]["ink"])
    rrect(d, cx, cy, side, side, 0.35 * k, outline=outline, fill=(255, 255, 255), width=0.07 * k)
    step, r = 0.62 * k, 0.22 * k
    for a, b in DICE[n]:
        x, y = P(cx + a * step, cy + b * step)
        d.ellipse([x - px(r), y - px(r), x + px(r), y + px(r)], fill=pip)


def draw_numeral(img, d, n, cx, cy, k, fam=None):
    rad = 1.25 * k
    fill, ink = ((250, 222, 238), (140, 40, 130)) if fam is None else (FAMILY[fam]["fill"], FAMILY[fam]["ink"])
    x, y = P(cx, cy)
    d.ellipse([x - px(rad), y - px(rad), x + px(rad), y + px(rad)], fill=fill)
    d.text((x, y + px(0.05 * k)), str(n), font=font(round(2.1 * k, 3)), fill=ink, anchor="mm")


def draw_fingers(img, d, n, cx, cy, k):
    if n <= 5:                                   # left hand first, index = 1, thumb = 5
        paste(img, hand_sprite(n, "left"), cx, cy, box=(2.6 * k, 2.6 * k))
    else:
        paste(img, hand_sprite(5, "left"), cx - 0.72 * k, cy, box=(1.4 * k, 2.4 * k))
        paste(img, hand_sprite(n - 5, "right"), cx + 0.72 * k, cy, box=(1.4 * k, 2.4 * k))


def draw_jewelbox(img, d, n, cx, cy, k, fam=None):
    cw = 0.56 * k
    w, h = 5 * cw, 2 * cw
    x0, y0 = cx - w / 2, cy + h / 2
    brown = (150, 100, 40)
    rrect(d, cx, cy, w + 0.24 * k, h + 0.24 * k, 0.12 * k, outline=brown, fill=(255, 236, 190), width=0.06 * k)
    for r in range(3):
        d.line([P(x0, y0 - r * cw), P(x0 + w, y0 - r * cw)], fill=brown, width=px(0.035 * k))
    for c in range(6):
        d.line([P(x0 + c * cw, y0), P(x0 + c * cw, y0 - h)], fill=brown, width=px(0.035 * k))
    for i in range(n):
        r, c = divmod(i, 5)
        paste(img, emoji("star" if fam == 1 else "gem"), x0 + (c + 0.5) * cw, y0 - (r + 0.5) * cw, box=(cw * 0.8, cw * 0.8))


def draw_path(img, d, n, cx, cy, k, length=6, seed=0, fam=None):
    sq = 0.46 * k
    x0 = cx - length * sq / 2
    ty = cy - 1.05 * k
    for i in range(length):
        fill = (252, 214, 230) if i % 2 == 0 else (232, 222, 250)
        if i == n - 1:
            fill = (250, 190, 90)
        rrect(d, x0 + (i + 0.5) * sq, ty, sq * 0.92, sq * 0.92, 0.06 * k, outline=(170, 120, 170), fill=fill, width=0.03 * k)
    if fam == 1:
        paste(img, emoji("frog"), x0 + (n - 0.5) * sq, ty + sq / 2 + 0.46 * k, box=(0.82 * k, 0.82 * k))
        return
    hh = 1.65 * k
    paste(img, princess_sprite(seed, "down"), x0 + (n - 0.5) * sq, ty + sq / 2 + 0.04 * k + hh / 2, h_cm=hh)


def draw_dots(d, n, cx, cy, k, r=0.13):
    step = 0.38 * k
    for dx, dy in positions(n, "row", step / 1.14, step / 1.1):
        x, y = P(cx + dx, cy + dy)
        d.ellipse([x - px(r * k), y - px(r * k), x + px(r * k), y + px(r * k)], fill=(92, 40, 120))


def draw_compare(img, d, item, cx, cy, k):
    """Two characters, each with a dot set; the child picks the one with more."""
    d.line([P(cx, cy + 1.3 * k), P(cx, cy - 1.3 * k)], fill=(215, 215, 215), width=px(0.03 * k))
    for side, (name, n) in zip((-1, 1), ((item["a"], item["na"]), (item["b"], item["nb"]))):
        x = cx + side * 0.78 * k
        paste(img, emoji(name), x, cy + 0.68 * k, box=(1.25 * k, 1.25 * k))
        if item.get("show") == "numeral":
            draw_numeral(img, d, n, x, cy - 0.62 * k, 0.42 * k)
        else:
            draw_dots(d, n, x, cy - 0.62 * k, k)


def draw_group(img, item, cx, cy, k):
    kind, n = item["kind"], item["n"]
    style = item.get("style", "row")
    seed = item.get("seed", 0)
    if kind == "princess":
        hh = item.get("princess_size", 1.8 if n <= 3 else 1.35) * k
        sprites = [princess_sprite(seed * 7 + i, item.get("pose", "down")) for i in range(n)]
        aspect = max(s.width / s.height for s in sprites)
        sw = hh * aspect
        st = style if style in ("row", "scatter") else "row"
        for (dx, dy), sp in zip(positions(n, st, sw, hh, seed, box=2.9 * k), sprites):
            paste(img, sp, cx + dx, cy + dy, h_cm=hh)
        return
    s = item.get("size", 0.9) * k
    sp = emoji(kind)
    for dx, dy in positions(n, style, s, s, seed, box=item.get("box", 2.8) * k):
        paste(img, sp, cx + dx, cy + dy, box=(s, s))


def draw_item(img, d, item, cx, cy, k=1.0):
    kind, fam = item["kind"], item.get("fam")
    if kind == "dice":
        draw_dice(img, d, item["n"], cx, cy, k, fam)
    elif kind == "numeral":
        draw_numeral(img, d, item["n"], cx, cy, k, fam)
    elif kind == "fingers":
        draw_fingers(img, d, item["n"], cx, cy, k)
    elif kind == "jewelbox":
        draw_jewelbox(img, d, item["n"], cx, cy, k, fam)
    elif kind == "path":
        draw_path(img, d, item["n"], cx, cy, k, seed=item.get("seed", 0), fam=fam)
    elif kind == "compare":
        draw_compare(img, d, item, cx, cy, k)
    else:
        draw_group(img, item, cx, cy, k)


# ------------------------------------------------------------------ spec handling

def parse_item(x, default):
    if isinstance(x, str) and "|" in x:
        (a, na), (b, nb) = (part.split(":") for part in x.split("|"))
        x = {"kind": "compare", "a": a, "na": int(na), "b": b, "nb": int(nb)}
    elif isinstance(x, str):
        x, _, fam = x.partition("@")
        kind, n = x.split(":")
        x = {"kind": kind, "n": int(n)}
        if fam:
            x["fam"] = int(fam)
    item = dict(default)
    item.update(x)
    return item


def family_of(sheet, it):
    """Index of the pair a task belongs to."""
    pairs = sheet["rule"]["pairs"]
    hits = [i for i, (a, _) in enumerate(pairs) if a == it["kind"]]
    if "fam" in it:
        if it["fam"] not in hits:
            raise SystemExit(f"{sheet.get('id')}: '{it['kind']}@{it['fam']}' does not start pair {it['fam']}")
        return it["fam"]
    if not hits:
        raise SystemExit(f"{sheet.get('id')}: '{it['kind']}' starts no pair; pairs run left to right only")
    if len(hits) > 1:
        raise SystemExit(f"{sheet.get('id')}: '{it['kind']}' starts both pairs, write '{it['kind']}:{it['n']}@0' or '@1'")
    return hits[0]


def make_answer_fn(sheet):
    rule = sheet.get("rule", {"type": "pair"})
    style = sheet.get("answer_style", "col")
    size = sheet.get("size", 0.9)

    def styled(kind, n, seed, fam=None):
        out = {"kind": kind, "n": n, "seed": seed}
        if kind not in SPECIAL - {"princess"}:
            out.update(style=style, size=size)
        if fam is not None:
            out["fam"] = fam
        return out

    if rule["type"] == "same":
        return lambda it: styled(it["kind"], it["n"], it["seed"])
    if rule["type"] == "more":
        size = sheet.get("answer_size", 1.9)

        def winner(it):
            if it["na"] == it["nb"]:
                raise SystemExit(f"{sheet.get('id')}: equal counts in {it}")
            name = it["a"] if it["na"] > it["nb"] else it["b"]
            return {"kind": name, "n": 1, "style": "row", "size": size, "seed": 0}
        return winner
    if rule["type"] == "plus_one":
        return lambda it: styled(it["kind"], it["n"] + 1, it["n"] + 11)
    if rule["type"] == "pair":
        pairs = rule["pairs"]
        if len(pairs) not in (1, 2):
            raise SystemExit(f"{sheet.get('id')}: one or two pairs")

        def partner(it):
            f = family_of(sheet, it)
            return styled(pairs[f][1], it["n"], it["n"] + 3, f if len(pairs) == 2 else None)
        return partner
    raise SystemExit(f"unknown rule {rule}")


def load_sheet(sheet):
    default = {"style": sheet.get("task_style", "row"), "size": sheet.get("size", 0.9)}
    if sheet.get("show"):
        default["show"] = sheet["show"]
    tasks = {i + 1: parse_item(x, default) for i, x in enumerate(sheet["tasks"])}
    for t, it in tasks.items():
        it.setdefault("seed", t)
    if len(tasks) != 12:
        raise SystemExit(f"{sheet.get('id')}: needs exactly 12 tasks")
    rule = sheet.get("rule", {"type": "pair"})
    if rule["type"] == "pair" and len(rule["pairs"]) == 2:
        for it in tasks.values():
            it["fam"] = family_of(sheet, it)
    answer = make_answer_fn(sheet)
    answers = {t: answer(it) for t, it in tasks.items()}
    keys = [item_key(a) for a in answers.values()]
    if len(set(keys)) != 12:
        raise SystemExit(f"{sheet.get('id')}: answers are not unique: {sorted(keys)}")
    if len({item_key(t) for t in tasks.values()}) != 12:
        raise SystemExit(f"{sheet.get('id')}: tasks are not unique")
    if rule["type"] != "plus_one":             # there the equal set is the intended lure
        where = {item_key(it)[:2]: t for t, it in tasks.items()}
        for u, a in answers.items():
            t = where.get(item_key(a)[:2])
            if t not in (None, u):
                raise SystemExit(f"{sheet.get('id')}: the answer to task {u} is a copy of task {t}; "
                                 "keep each kind on one side")
    if sheet.get("rule", {}).get("type") == "more":
        winners = {a["kind"] for a in answers.values()}
        losers = {t["b"] if t["na"] > t["nb"] else t["a"] for t in tasks.values()}
        if not losers <= winners:
            print(f"warning {sheet.get('id')}: {sorted(losers - winners)} never appear below, so they lure nobody")
    return tasks, answers


def item_key(it):
    if it["kind"] == "compare":
        return ("compare", it["a"], it["na"], it["b"], it["nb"])
    return (it["kind"], it["n"], it.get("fam"))


# ------------------------------------------------------------------ page

def draw_pattern(d, Pat, x_cm, y_top_cm, tile_cm=0.8, gap_cm=0.07):
    s, g = px(tile_cm), px(gap_cm)
    X0, Y0 = P(x_cm, y_top_cm)
    for r in range(2):
        for c in range(6):
            col, corner = Pat[r][c]
            x0, y0 = X0 + c * (s + g), Y0 + r * (s + g)
            d.rectangle([x0, y0, x0 + s, y0 + s], fill=TILE_RGB[col])
            h = s / 2
            tri = {"BL": [(x0, y0), (x0, y0 + s), (x0 + h, y0 + s)],
                   "BR": [(x0 + s, y0), (x0 + s, y0 + s), (x0 + s - h, y0 + s)],
                   "TL": [(x0, y0 + s), (x0, y0), (x0 + h, y0)],
                   "TR": [(x0 + s, y0 + s), (x0 + s, y0), (x0 + s - h, y0)]}[corner]
            d.polygon(tri, fill=CREAM)
            d.rectangle([x0, y0, x0 + s, y0 + s], outline=(120, 120, 120), width=2)


def dotted_arrow(d, x0, x1, y, colour):
    for i in range(6):
        a, b = P(x0 + (x1 - x0) * i / 6, y)
        r = px(0.045)
        d.ellipse([a - r, b - r, a + r, b + r], fill=colour)
    tx, ty = P(x1, y)
    d.polygon([(tx, ty), (tx - px(0.22), ty - px(0.13)), (tx - px(0.22), ty + px(0.13))], fill=colour)


def cell_colours(item, frame, accent):
    f = item.get("fam")
    return (frame, accent, 0.07) if f is None else (FAMILY[f]["frame"], FAMILY[f]["ink"], 0.13)


def render(sheet, Pat, index, labels):
    tasks, answers = load_sheet(sheet)
    frame, accent = THEMES[sheet.get("theme", "pink")]
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)

    for t, item in tasks.items():
        r, c = TASK_POS[t]
        cx, cy = COLS[c], TASK_ROWS[r]
        fr, ac, w = cell_colours(item, frame, accent)
        rrect(d, cx, cy, TASK_CELL, TASK_CELL, 0.3, outline=fr, fill=(255, 255, 255), width=w)
        if item.get("style") == "scatter":           # keep scattered items clear of the number badge
            draw_item(img, d, dict(item, box=2.6), cx + 0.15, cy - 0.25, sheet.get("task_scale", 0.95))
        else:
            draw_item(img, d, item, cx, cy - 0.12, sheet.get("task_scale", 0.95))
        lx, ly = cx - TASK_CELL / 2 + 0.38, cy + TASK_CELL / 2 - 0.38
        rrect(d, lx, ly, 0.56, 0.56, 0.08, outline=ac, fill=(255, 255, 255), width=0.04)
        d.text(P(lx, ly), str(t), font=font(0.38), fill=ac, anchor="mm")

    check_pattern(Pat)
    L = placement_of(Pat)
    assert pattern_of(L) == Pat
    for r in range(2):
        for c in range(6):
            cx, cy = COLS[c], LID_ROWS[r]
            a = answers[L[r][c]]
            fr, _, w = cell_colours(a, frame, accent)
            rrect(d, cx, cy, CELL, CELL, 0.3, outline=fr, fill=(255, 255, 255), width=w)
            draw_item(img, d, a, cx, cy, 1.0)

    left = COLS[0] - CELL / 2
    lines = sheet["title"] if isinstance(sheet["title"], list) else [sheet["title"]]
    for i, line in enumerate(lines):
        text(d, left, 12.25 - i * 0.62, line, 0.52, (90, 40, 100))
    yb = 12.25 - len(lines) * 0.62 - 0.55
    second = next((t for t, it in tasks.items() if it.get("fam") == 1), None)
    for j, t in enumerate([1] + ([second] if second else [])):
        ox = left + j * 4.75
        for bx, it in ((ox + 0.65, tasks[t]), (ox + 3.6, answers[t])):
            fr, _, _ = cell_colours(it, frame, accent)
            rrect(d, bx, yb, 1.3, 1.3, 0.15, outline=fr, fill=(255, 255, 255),
                  width=0.04 if it.get("fam") is None else 0.07)
            draw_item(img, d, it, bx, yb, 0.38)
        dotted_arrow(d, ox + 1.5, ox + 2.75, yb, (150, 150, 150))
    if sheet.get("prompt"):
        if second:
            text(d, left, 9.25, sheet["prompt"], 0.36, accent)
        else:
            text(d, left + 4.6, yb - 0.12, sheet["prompt"], 0.36, accent)

    pat_left = COLS[5] + CELL / 2 - (6 * 0.8 + 5 * 0.07)
    draw_pattern(d, Pat, pat_left, 12.15)
    sx, sy = pat_left - 1.95, 11.25
    x, y = P(sx, sy)
    rr = px(0.85)
    for a in range(0, 360, 12):
        d.arc([x - rr, y - rr, x + rr, y + rr], start=a, end=a + 6, fill=(200, 170, 210), width=px(0.04))
    paste(img, emoji("sparkles"), sx, sy + 0.18, box=(0.6, 0.6))
    d.text(P(sx, sy - 0.42), labels["done"], font=font(0.26), fill=(170, 140, 180), anchor="mm")
    if sheet.get("mascot", True):
        paste(img, princess_sprite(index * 5 + 3, "wand"), sx - 2.05, 10.95, h_cm=2.75)
    if sheet.get("goal"):
        right = COLS[5] + CELL / 2
        max_w = right - (sx - 1.1 if sheet.get("mascot", True) else left + 5.0)
        lines, cur = [], ""
        for word in sheet["goal"].split():
            trial = f"{cur} {word}".strip()
            if cur and d.textlength(trial, font=font(0.24, False)) / CM > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        lines.append(cur)
        for i, line in enumerate(reversed(lines)):
            text(d, right, 9.75 + i * 0.33, line, 0.24, (165, 165, 165), bold=False, anchor="rs")

    msg = labels["hinge"]
    text(d, PW / 2, 0.45, msg, 0.25, (175, 175, 175), bold=False, anchor="ms")
    half = d.textlength(msg, font=font(0.25, False)) / CM / 2
    for xm in (PW / 2 - half - 0.4, PW / 2 + half + 0.4):
        a, b = P(xm, 0.5)
        r = px(0.11)
        d.polygon([(a - r, b - r), (a + r, b - r), (a, b + r)], fill=(175, 175, 175))
    return img.convert("RGB"), L


def key_page(rows, labels):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    text(d, 1.5, 19.9, labels["key_title"], 0.5, (60, 60, 60))
    y = 18.6
    for sid, title, L, Pat in rows:
        text(d, 1.5, y, f"{sid}  {title}", 0.3, (60, 60, 60))
        text(d, 15.0, y, "  ".join(f"{t:>2}" for t in L[0]), 0.3, (60, 60, 60), bold=False)
        text(d, 15.0, y - 0.5, "  ".join(f"{t:>2}" for t in L[1]), 0.3, (60, 60, 60), bold=False)
        draw_pattern(d, Pat, 22.6, y + 0.22, tile_cm=0.42, gap_cm=0.04)
        y -= 1.45
    return img


def fit_test_page(labels):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    for r in range(2):
        for c in range(6):
            cx, cy = COLS[c], LID_ROWS[r]
            rrect(d, cx, cy, CELL, CELL, 0.3, outline=(230, 120, 170), width=0.07)
            d.line([P(cx - 0.3, cy), P(cx + 0.3, cy)], fill=(120, 120, 120), width=3)
            d.line([P(cx, cy - 0.3), P(cx, cy + 0.3)], fill=(120, 120, 120), width=3)
    x0, y = COLS[0] - CELL / 2, 11.5
    d.line([P(x0, y), P(x0 + 10, y)], fill=(40, 40, 40), width=px(0.03))
    for i in range(11):
        d.line([P(x0 + i, y), P(x0 + i, y + (0.25 if i % 5 == 0 else 0.15))], fill=(40, 40, 40), width=px(0.025))
    for i, line in enumerate(labels["fit"]):
        text(d, x0, 13.6 - i * 0.55, line, 0.34, (60, 60, 60), bold=False)
    return img


LABELS = {
    "en": {"done": "Done!", "hinge": "Box hinge on this edge, every picture in the middle of a compartment",
           "key_title": "Answer key: tiles in the lid, upper row / row at the hinge",
           "fit": ["Fit test: print at 100 % (actual size). The line below must be 10 cm.",
                   "Open the box, put the clear lid on this sheet, hinge on the lower edge.",
                   "Every pink frame should sit in the middle of one compartment. Centre 1 to centre 6: 20.5 cm."]},
    "de": {"done": "Geschafft!", "hinge": "Scharnier des Kastens an diese Blattkante, jedes Bild mittig in ein Fach",
           "key_title": "Lösungen: Plättchen im Deckel, obere Reihe / Reihe am Scharnier",
           "fit": ["Passtest: mit 100 % drucken (Tatsächliche Größe). Die Linie unten muss 10 cm lang sein.",
                   "Kasten aufklappen, durchsichtigen Teil auf das Blatt, Scharnier an die untere Kante.",
                   "Jeder Rahmen liegt mittig in einem Fach. Mitte 1 bis Mitte 6: 20,5 cm."]},
}


def check(spec_path):
    """Validate a set without rendering: kinds, 12 tasks, unique tasks and answers, patterns."""
    validate()
    spec = json.loads(Path(spec_path).read_text())
    lib = pattern_library()
    names = {p.stem for p in EMOJI_DIR.glob("*.png")}
    used = set()
    for i, sheet in enumerate(spec["sheets"]):
        tasks, answers = load_sheet(sheet)
        for it in list(tasks.values()) + list(answers.values()):
            pics = [it["a"], it["b"]] if it["kind"] == "compare" else [it["kind"]]
            for name in pics:
                if name not in SPECIAL and name not in names:
                    raise SystemExit(f"{sheet.get('id')}: unknown picture '{name}'")
        if sheet.get("theme", "pink") not in THEMES:
            raise SystemExit(f"{sheet.get('id')}: unknown theme '{sheet.get('theme')}'")
        k = sheet.get("pattern", i) % len(lib)
        if k in used:
            print(f"note {sheet.get('id')}: pattern {k} repeats an earlier sheet")
        used.add(k)
        L = placement_of(lib[k])
        print(f"{sheet.get('id', i + 1):>4}  ok  lid upper row {L[0]}  hinge row {L[1]}")
    print(f"{len(spec['sheets'])} sheets valid")


def build(spec_path, out, previews=None, only=None, key=False, fit=False):
    validate()
    spec = json.loads(Path(spec_path).read_text())
    labels = LABELS[spec.get("language", "en")]
    lib = pattern_library()
    pages, rows = [], []
    if fit:
        pages.append(fit_test_page(labels))
    for i, sheet in enumerate(spec["sheets"]):
        if only and sheet.get("id") not in only:
            continue
        Pat = lib[sheet.get("pattern", i) % len(lib)]
        img, L = render(sheet, Pat, i, labels)
        pages.append(img)
        title = " ".join(sheet["title"]) if isinstance(sheet["title"], list) else sheet["title"]
        rows.append((sheet.get("id", str(i + 1)), title, L, Pat))
    if key:
        pages.append(key_page(rows, labels))
    pages[0].save(out, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    if previews:
        Path(previews).mkdir(parents=True, exist_ok=True)
        for n, p in enumerate(pages):
            p.resize((W // 3, H // 3), Image.LANCZOS).save(Path(previews) / f"page{n + 1:02d}.png")
    print(f"wrote {out}: {len(pages)} pages")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("spec")
    b = sub.add_parser("build")
    b.add_argument("spec")
    b.add_argument("-o", "--out", required=True)
    b.add_argument("--previews")
    b.add_argument("--only", help="comma-separated sheet ids")
    b.add_argument("--key", action="store_true", help="append an answer-key page")
    b.add_argument("--fit", action="store_true", help="prepend a fit-test page")
    f = sub.add_parser("fit-test")
    f.add_argument("-o", "--out", required=True)
    f.add_argument("--language", default="en")
    sub.add_parser("kinds")
    a = ap.parse_args()
    if a.cmd == "check":
        check(a.spec)
    elif a.cmd == "build":
        build(a.spec, a.out, a.previews, a.only.split(",") if a.only else None, a.key, a.fit)
    elif a.cmd == "fit-test":
        fit_test_page(LABELS[a.language]).save(a.out, "PDF", resolution=DPI)
        print("wrote", a.out)
    else:
        names = sorted(p.stem for p in EMOJI_DIR.glob("*.png"))
        print("pictures:", ", ".join(names))
        print("special: dice, numeral, fingers (1-10), jewelbox (ten-frame), path (princess on a 1-6 track), princess,")
        print("         compare (written as \"dog:4|cat:1\", used with the rule \"more\")")
        print("pairs run left to right; with two pairs write \"kind:n@1\" when both start with the same kind")


if __name__ == "__main__":
    main()
