---
name: miniluek-sheets
description: |
  Generate printable A4 worksheets for the miniLÜK control box in preschool mode (the open box
  lies on the sheet), each with a working control pattern. Use when someone wants their own
  miniLÜK exercises: counting, dice, fingers, comparing, numerals, number path, ten-frame,
  one more, letters, first sounds, syllables, short words, shapes or odd one out, or any
  picture matching, themed with princesses, animals or other pictures.
---

# miniLÜK sheets

Each sheet is one A4 landscape page: 12 numbered tasks on top, the answer grid at the bottom
under the clear lid (box hinge on the lower paper edge), the control pattern in between. The
child puts tile *n* on the picture that answers task *n*, closes the box, turns it over, opens
it and compares the tile backs with the printed pattern.

## Commands

Requires Python 3.9+ and Pillow (`pip install pillow`). Run from this skill directory.

```bash
python3 scripts/miniluek.py check presets/counting_and_numbers/princess-counting.json     # validate a set
python3 scripts/miniluek.py build presets/counting_and_numbers/princess-counting.json -o sheets.pdf --previews previews/
python3 scripts/miniluek.py fit-test -o fit.pdf                      # does the box line up?
python3 scripts/miniluek.py kinds                                    # available pictures
```

`build` options: `--only S2,S5` (subset), `--key` (append an answer key), `--fit` (prepend the
fit test), `--fingers index|thumb` (finger habit). Tell the user to print at **100 % / actual size**, landscape, ideally in colour.
Always look at the preview PNGs before handing over a PDF.

## Writing a sheet set

The counting course is the flagship: 19 sheets (13 plain sheets and 6 picture twins) in `presets/counting_and_numbers/princess-counting.json`
(German: `presets/counting_and_numbers/prinzessinnen-zaehlen.json`), ordered along the early-math
progression in `presets/counting_and_numbers/teaching-order.md` (sources per design choice:
`presets/counting_and_numbers/research.md`).

A smaller experimental reading course ships as `presets/reading/reading-readiness.json`
(German: `presets/reading/lese-vorbereitung.json`); its order is in
`presets/reading/teaching-order.md`.
Evidence: `presets/counting_and_numbers/research.md` for counting, `presets/reading/research.md` for reading.

A set is JSON (see the preset for its course; every field in `references/spec.md`).
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
- All 12 answers must differ, and no answer may repeat another task's picture (that copy would
  be the easiest wrong match); `check` and `build` stop otherwise. `plus_one` sheets are exempt:
  there the equal set is the intended lure.
- Kinds: any picture from `kinds`, plus `princess` (drawn full-body figures), `dice`,
  `numeral`, `fingers` (left hand first; `"fingers": "index"` counts index = 1 to thumb = 5,
  `"thumb"` thumb = 1; 6–10 with the second hand), `jewelbox`
  (ten-frame with gems, stars in the blue family), `path` (princess, or frog in the blue
  family, on square *n* of a 6-square path), and picture-sheet tokens: `pearl` (in shells),
  `yarn` and `bone` (scattered on rugs), `snowflake` (in snow globes), `tower` (linking cubes).
- Layout: `task_style` / `answer_style` = `row`, `col`, `up`, `down`, `dice`, `scatter`. Use
  different styles for task and answer when the answer repeats the task's kind, so the child
  counts instead of matching shapes.
  `size` is the picture size in cm (0.9 for up to 6, 1.25 for up to 3).
- **Picture sheets** (`"picture": "lagoon"`): one full illustration with 12 numbered badges set
  into the story along a trail in number order, answer grid and pattern unchanged. Counting:
  `meadow` (1–3 bugs on flowers, rule `same`), `train` (kittens `cat` and puppies `dog` at the
  windows), `lagoon` (`pearl`), `ice_gate` (`snowflake` in snow globes on locked doors), `castle` (`yarn` and `bone`
  on blankets), `towers` (`tower` of cubes, rule `plus_one`). Reading: `blocks` (`letter`),
  `balloons` (`card`), `garden` (`pict` to letter), `village` (`pict` to `wcard` word). `"spots"` moves the stations (cm in the panel). Each
  comes after the plain sheet of the same skill as review, never as the teaching. Twins are
  quest chapters: the title tells the story beat in one or two lines, the goal names the quest
  number and the plain sheet it revisits.
- **Quest lanes** (`presets/quests/`): three story lanes revisit the courses, one sheet per
  course step: the unicorn circus (numbers, 12), the mermaid's sea post (letters, 7) and the
  ice palace (logic: AB patterns, shapes, odd one out, places in a 3 × 3 grid). Their scenes
  and kinds are registered by `scripts/quest_scenes.py`; operations, scenes and evidence are
  in `presets/quests/README.md`.
- Picture sheets: counted sets and letter guests are plain and uniform in their own
  containers; decoration stays out of the way. Grid sheets stay plain, the picture is the
  review, not the teaching.

Each sheet gets a control pattern from a library of symmetric patterns (`"pattern": k` picks
one; a set with more sheets than the library repeats one). The tile-back model is in `references/format.md`.

## Order and use

The counting preset follows the early-math progression in
`presets/counting_and_numbers/teaching-order.md` (sources per design choice:
`presets/counting_and_numbers/research.md`): small sets,
counting, dice and finger patterns, comparing, numerals both ways, scattered sets, number path,
comparing by counting and comparing numbers, then ten-frame and one more. Each idea first with real objects, then the sheet; say what to look
for, touch-count and place, then turn the box and fix the wrong tiles together.

## Fit

Compartment pitch 4.10 cm, rows 3.05 cm and 7.15 cm above the hinge, frames 3.5 cm. If a
user's box does not line up, run `fit-test`, ask for the distance from the centre of the
first to the centre of the sixth compartment (expected 20.5 cm) and adjust `PITCH` in
`scripts/miniluek.py`.
