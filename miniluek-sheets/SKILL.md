---
name: miniluek-sheets
description: |
  Generate printable A4 worksheets for the miniLÜK control box in preschool mode (the open box
  lies on the sheet), each with a working control pattern. Use when someone wants their own
  miniLÜK exercises: counting, dice, fingers, comparing, numerals, number path, ten-frame,
  one more, or any picture matching, themed with princesses, animals or other pictures.
---

# miniLÜK sheets

Each sheet is one A4 landscape page: 12 numbered tasks on top, the answer grid at the bottom
under the clear lid (box hinge on the lower paper edge), the control pattern in between. The
child puts tile *n* on the picture that answers task *n*, closes the box, turns it over, opens
it and compares the tile backs with the printed pattern.

## Commands

Requires Python 3.9+ and Pillow (`pip install pillow`). Run from this skill directory.

```bash
python3 scripts/miniluek.py check presets/princess-counting.json     # validate a set
python3 scripts/miniluek.py build presets/princess-counting.json -o sheets.pdf --previews previews/
python3 scripts/miniluek.py fit-test -o fit.pdf                      # does the box line up?
python3 scripts/miniluek.py kinds                                    # available pictures
```

`build` options: `--only S2,S5` (subset), `--key` (append an answer key), `--fit` (prepend the
fit test), `--fingers index|thumb` (finger habit). Tell the user to print at **100 % / actual size**, landscape, ideally in colour.
Always look at the preview PNGs before handing over a PDF.

## Writing a sheet set

A set is JSON (see `presets/princess-counting.json`, German: `presets/prinzessinnen-zaehlen.json`;
every field in `references/spec.md`).
Per sheet: `title`, optional `goal` (small grey line for adults) and `prompt`, `theme`,
`rule`, and exactly **12 tasks**. Run `check` after every edit.

- **Matching** (`{"type": "pair", "pairs": [["princess", "cupcake"], ["frog", "crown"]]}`):
  pairs run left to right only, tasks are written `"kind:n"` and the answer is the right-hand
  picture with the same count. With counts 1–6 use two pairs: tasks 1–6 and their answers get
  pink frames, tasks 7–12 and theirs blue, so the only other answer with the right number has
  the other colour. When both pairs start with the same kind, mark the second `"numeral:3@1"`.
- **Same thing** (`{"type": "same"}`): the answer is the same picture and count in the
  answer layout. **One more** (`{"type": "plus_one"}`): the equal set is the intended lure.
- **Comparing** (`{"type": "more"}`): tasks written `"dog:4|cat:1"`; the answer is the
  character with more. Use 12 different characters, each wins once and loses once, so every
  loser is a lure elsewhere; start with differences of at least 2 : 1. `"show": "numeral"`
  draws numbers instead of dots.
- All 12 answers must differ, and no answer may repeat a task picture (that copy would be the
  easiest wrong match); `check` and `build` stop otherwise.
- Kinds: any picture from `kinds`, plus `princess` (drawn full-body figures), `dice`,
  `numeral`, `fingers` (left hand first; `"fingers": "index"` counts index = 1 to thumb = 5,
  `"thumb"` thumb = 1; 6–10 with the second hand), `jewelbox`
  (ten-frame with gems, stars in the blue family), `path` (princess, or frog in the blue
  family, on square *n* of a 6-square path).
- Layout: `task_style` / `answer_style` = `row`, `col`, `up`, `down`, `dice`, `scatter`. Use
  different styles for task and answer so the child counts instead of matching shapes.
  `size` is the picture size in cm (0.9 for up to 6, 1.25 for up to 3).

Each sheet gets its own control pattern from a library of symmetric patterns (`"pattern": k`
picks one). The tile-back model is in `references/format.md`.

## Order and use

The preset follows the early-math progression in `references/teaching-order.md` (sources per
design choice: `references/research.md`): small sets,
counting, dice and finger patterns, comparing, numerals both ways, scattered sets, number path,
comparing by counting and comparing numbers, then ten-frame and one more. Each idea first with real objects, then the sheet; say what to look
for, touch-count and place, then turn the box and fix the wrong tiles together.

## Fit

Compartment pitch 4.10 cm, rows 3.05 cm and 7.15 cm above the hinge, frames 3.5 cm. If a
user's box does not line up, run `fit-test`, ask for the distance from the centre of the
first to the centre of the sixth compartment (expected 20.5 cm) and adjust `PITCH` in
`scripts/miniluek.py`.
