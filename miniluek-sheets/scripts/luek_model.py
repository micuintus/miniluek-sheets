"""miniLÜK tile-back model and control-pattern library.

Base view = the red base after the box is closed, turned over and reopened, base towards the
child. This is the orientation of the patterns printed in the Hefte. Each tile back is blue (B),
red (R) or green (G) with a cream right triangle in one corner: full vertical side, horizontal leg
half the tile width. BL = bottom-left, TR = top-right, ...

A tile placed in the lid row far from the hinge appears in the base row away from the hinge,
same column. All patterns used here are top-bottom symmetric, so they do not depend on how the
closed box is turned over. The table was mapped from published example exercises and checked
on a physical box.
"""

BACK = {
    1: ("G", "BL"), 2: ("B", "BL"), 3: ("R", "BR"), 4: ("G", "BR"),
    5: ("R", "TR"), 6: ("B", "BR"), 7: ("G", "TR"), 8: ("B", "TL"),
    9: ("R", "BL"), 10: ("G", "TL"), 11: ("R", "TL"), 12: ("B", "TR"),
}
TILE_OF = {v: k for k, v in BACK.items()}

MIR_TB = {"BL": "TL", "TL": "BL", "BR": "TR", "TR": "BR"}
MIR_LR = {"BL": "BR", "BR": "BL", "TL": "TR", "TR": "TL"}


def pattern_of(L):
    """L[0] = lid row far from the hinge (upper grid row on the sheet), L[1] = row at the hinge.
    Returns P[0] = upper row of the printed pattern, P[1] = lower row."""
    return [[BACK[t] for t in L[1]], [BACK[t] for t in L[0]]]


def placement_of(P):
    return [[TILE_OF[x] for x in P[1]], [TILE_OF[x] for x in P[0]]]



BLOCK = {
    "HG": (("BL", "BR"), ("TL", "TR")),  # hourglass
    "M": (("TR", "TL"), ("BR", "BL")),
    "K": (("BR", "TL"), ("TR", "BL")),
    "GT": (("TR", "BL"), ("BR", "TL")),
}


def block_pattern(spec):
    """spec: three (colour, shape) pairs, one 2x2 block per colour, left to right."""
    top, bot = [], []
    for col, shape in spec:
        (a, b), (c, d) = BLOCK[shape]
        top += [(col, a), (col, b)]
        bot += [(col, c), (col, d)]
    return [top, bot]


def nested_pattern(spec):
    """spec: colours for the column pairs (1,6), (2,5), (3,4) with the corner of the left tile."""
    top, bot = [None] * 6, [None] * 6
    for i, (col, x) in enumerate(spec):
        j = 5 - i
        top[i], top[j] = (col, x), (col, MIR_LR[x])
        bot[i], bot[j] = (col, MIR_TB[x]), (col, MIR_TB[MIR_LR[x]])
    return [top, bot]


def check_pattern(P):
    used = [x for row in P for x in row]
    assert sorted(used) == sorted(BACK.values()), "every tile back exactly once"
    for c in range(6):
        col, corner = P[0][c]
        assert P[1][c] == (col, MIR_TB[corner]), "top-bottom symmetric"


def pattern_library():
    """Distinct, symmetric patterns in a fixed order (first entries look the nicest)."""
    lib = [
        block_pattern([("R", "M"), ("G", "M"), ("B", "M")]),
        block_pattern([("B", "HG"), ("R", "HG"), ("G", "HG")]),
        nested_pattern([("G", "BL"), ("B", "TR"), ("R", "BR")]),
        block_pattern([("G", "K"), ("R", "HG"), ("B", "GT")]),
        nested_pattern([("R", "TL"), ("G", "BL"), ("B", "TR")]),
        block_pattern([("B", "M"), ("G", "HG"), ("R", "M")]),
        nested_pattern([("B", "BR"), ("R", "TL"), ("G", "BL")]),
        block_pattern([("R", "GT"), ("B", "M"), ("G", "K")]),
        nested_pattern([("G", "TR"), ("R", "BL"), ("B", "TL")]),
        block_pattern([("G", "HG"), ("B", "K"), ("R", "HG")]),
        nested_pattern([("R", "BR"), ("B", "BL"), ("G", "TR")]),
        block_pattern([("B", "GT"), ("R", "M"), ("G", "GT")]),
    ]
    for P in lib:
        check_pattern(P)
    return lib


def validate():
    """Internal consistency: the tile-back table is a bijection onto 3 colours x 4 corners,
    placement and pattern invert each other, and every library pattern is complete and symmetric."""
    assert len(set(BACK.values())) == 12
    assert {c for c, _ in BACK.values()} == {"B", "R", "G"}
    assert {k for _, k in BACK.values()} == {"BL", "BR", "TL", "TR"}
    for P in pattern_library():
        L = placement_of(P)
        assert sorted(t for row in L for t in row) == list(range(1, 13))
        assert pattern_of(L) == P
    return True


if __name__ == "__main__":
    validate()
    print("tile model consistent;", len(pattern_library()), "patterns")
