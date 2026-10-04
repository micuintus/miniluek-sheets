# Format, geometry and the tile-back model

## Preschool mode

Preschool booklets (26.0 × 14.0 cm) are used turned sideways: the upper page holds 12 numbered
tasks, the open box's clear lid lies on the lower page. The child places tile *n* in the
compartment that shows the answer to task *n*, closes the box, turns it over, opens it and
compares the tile backs with the printed pattern. School booklets (23.5 × 15.5 cm) work
differently: the box lies next to the booklet and the answers carry field numbers. This skill
only makes preschool-mode sheets.

## Geometry used

| | |
|---|---|
| Page | A4 landscape, 300 dpi raster PDF |
| Answer grid | 2 rows × 6 columns, pitch 4.10 cm, frames 3.5 cm, centred horizontally |
| Rows | centres 3.05 cm and 7.15 cm above the lower paper edge (= hinge) |
| Tasks | 3.4 cm cells at the same column positions, rows at 18.7 cm and 15.15 cm |
| Box | sold as "26 × 13 cm" closed by dealers; tiles 4 × 4 cm |

The pitch was measured from published booklet pages and confirmed on a physical box.

## Tile backs

Each tile back is blue, red or green with a cream right triangle in one corner (full vertical
side, horizontal leg half the tile width). Seen in the base after closing, turning over and
reopening (base towards the child):

| Tile | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Colour | G | B | R | G | R | B | G | B | R | G | R | B |
| Cream corner | BL | BL | BR | BR | TR | BR | TR | TL | BL | TL | TL | TR |

A tile placed in the lid row far from the hinge lands in the base row away from the hinge,
same column. The patterns in the library are top-bottom symmetric, so the result does not
depend on how the closed box is turned over. Each pattern uses every tile back exactly once,
which fixes the placement: `placement_of(pattern)` in `scripts/luek_model.py`.
