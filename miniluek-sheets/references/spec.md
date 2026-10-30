# Sheet-set JSON

```json
{
  "title": "Numbers",
  "language": "en",
  "sheets": [
    {
      "id": "S3",
      "theme": "peach",
      "title": ["Pink dice get hearts,", "blue dice get stars."],
      "goal": "Dice patterns, checked by counting, 1–6",
      "prompt": "Count the dots!",
      "rule": {"type": "pair", "pairs": [["dice", "heart"], ["dice", "star"]]},
      "answer_style": "row",
      "size": 0.88,
      "pattern": 3,
      "mascot": true,
      "tasks": ["dice:4@0", "dice:1@0", "dice:6@0", "dice:2@0", "dice:5@0", "dice:3@0",
                "dice:3@1", "dice:5@1", "dice:2@1", "dice:6@1", "dice:1@1", "dice:4@1"]
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `id` | short sheet id, printed small at the lower left; goal lines and `build --only` use it |
| `language` | `en` or `de` (labels at the bottom and in the fit test) |
| `fingers` | set level or per sheet: `index` (index finger = 1, thumb = 5, the default) or `thumb` (thumb = 1); `build --fingers` overrides it |
| `title` | one or two lines, read aloud by the adult |
| `goal` | optional grey line for adults |
| `prompt` | optional coloured line next to the example |
| `theme` | `pink`, `lavender`, `peach`, `mint`, `gold`, `sky`, `rose`, `violet`, `coral`, `teal` |
| `rule` | `pair` with one or two `pairs` (left to right), `plus_one`, `same`, or `more` (comparing) |
| `show` | `numeral` on comparing sheets: numbers instead of dots |
| `task_style`, `answer_style` | `row`, `col`, `up`, `down`, `dice`, `scatter` (pictures only) |
| `size` | picture size in cm |
| `answer_size` | size of the single characters on comparing sheets (default 1.9) |
| `pattern` | index into the 47-pattern library (default: sheet index); index 33 was retired with M1 and no sheet uses it |
| `mascot` | decorative princess next to the title: `true` (default, varies with the page position), `false`, or a number that picks one princess, so a sheet keeps her when sheets are inserted before it |
| `picture` | one full illustration with 12 numbered badges set into a story; the scene names and what each draws are listed under [picture scenes](#picture-scenes). `spots` moves the 12 stations (cm in the 28.3 × 7.6 cm panel, origin top left, y down). Answer grid, pattern and geometry are untouched. Review after the plain sheet of the same skill; a picture sheet without one comes after the same idea with objects |
| `tasks` | exactly 12 entries `"kind:n"` (`"kind:n@1"` for the second pair when both pairs start with the same kind) or objects `{"kind": …, "n": …, "fam": …, "style": …, "size": …, "seed": …}` |

Special kinds: `princess` (n figures; `princess_size` overrides the height), `dice` (1–6),
`numeral`, `fingers` (1–10), `jewelbox` (0–10 in a ten-frame), `path` (1–6), picture-sheet
tokens `pearl` (in shells), `snowflake` (in snow globes),
`tower` (linking cubes, one cube size on one floor line), the scene answer kinds `balls`, `shape`
and `map` (below), and comparing
tasks written `"dog:4|cat:1"` (two characters with 1–6 dots each, for the rule `more`). `yarn`
and `bone` are plain pictures; the `castle` scene lays them on rugs.

Letter kinds: `letter` (`n` 0–25, A to Z), `lower` (its lowercase, as an answer), `card` (a
letter card, `card:C`, or bound to a course word, `card:CAT`, which captions the word), `pict`
(one picture, `pict:cat`, whose first letter is `n`), `wcard` (a printed word as books print it: German nouns capitalised, `Hund`; English lowercase, `cat`) and `syll` (the
start of a course word, `syll:CA`). `card:WORD`, `syll:XX` and word-to-picture pairs resolve
through the 47-word list (`WORD_PIC` in `scripts/miniluek.py`): 12 course words and 12 sea-post words per language, German PANDA sharing the English entry; a task written as an
object can bind any picture to its `word`.

With two pairs, the first pair's tasks and answers get pink frames, the second pair's blue.

`check` (and `build`) verify: 12 tasks, all tasks distinct, all answers distinct, no answer
repeating a task picture (except on `plus_one` sheets), pairs used left to right, every picture
known, every control pattern uses each tile back once and is symmetric; on comparing sheets a
warning appears when a losing character never shows up among the answers.

## Picture scenes

The lane scenes live in `scripts/lane_scenes.py`, the older ones in `scripts/scenes.py`. Each
draws its twelve stations from the tasks; `check` refuses a task the scene cannot draw.

| Scene | Lane sheet | Task kind | Fields |
|---|---|---|---|
| `juggling` | C1 | juggled tokens | `kind`, `n` 1–3: `heart` or `star` (pink), `moon` or `strawberry` (blue) |
| `breakfast` | C2 | `seal`, `puppy` | `n` 1–6 |
| `dice_meadow` | C3 | `dice` | `n` 1–6 |
| `finger_theatre` | C4 | `dice` | `n` 1–6; answers are `fingers` in the set's habit |
| `contest`, `bubble_act` | C5, C10 | `compare` | `a`, `na`, `b`, `nb` 1–6: balloons or bubbles above each animal |
| `trains` | C6 | `gift`, `star` | `n` 1–6 |
| `ticket_booth` | C7 | `ticket` | `n` 1–6 |
| `spotlights` | C8 | `balloon` (pink), `moon` (blue) | `n` 1–6, scattered |
| `tightrope` | C9 | `rope` | `n` 1–6, counted from the flag |
| `ring_toss` | C11 | `compare` | numerals on signs |
| `magic_show` | C12 | `chest` | `n` 3–8 in a ten-frame |
| `seal_show` | C13 | `balls` | `n` 1–6; the answer kind `balls` stacks them on one floor line |
| `party` | C14 | `plate` | `n` 1–6 left after one is eaten |
| `fish_school` | M2 | `lower` | `n` 0–25; answers are the capitals |
| `bottle_post` | M3 | `card` | a sea-post word |
| `sea_finds` | M4 | `pict` | a new picture and its first letter `n` |
| `word_start_bubbles` | M5 | `syll` | the start of a sea-post word: `text` and `word` from the extended list |
| `post_boats` | M6 | `wcard` | `word` from the extended list |
| `beach_post` | M7 | `pict` | a picture bound to its `word` |
| `necklaces` | P1 | `necklace` | `pic` (the next charm) and a different `other` |
| `palace_windows` | P2 | `shape` | `n` 0–5 (circle, square, triangle, rectangle, star, heart); the answer kind `shape` is the same shape in gold |
| `winter_party` | P3 | `odd` | `same`, a different `pic`, `at` 0–3 |
| `castle_hills` | P4 | `castle` | `n` 0–8, the window the princess looks out of; the answer kind `map` marks it with a star |
| `meadow` | | `ladybug`, `bee`, `snail`, `butterfly` | `n` 1–3, rule `same` |
| `train` | | `cat`, `dog` | `n` 1–6, faces at windows |
| `lagoon` | | `pearl` | `n` 1–6 in shells |
| `ice_gate` | | `snowflake` | `n` 1–6 in snow globes |
| `castle` | | `yarn`, `bone` | `n` 1–6 scattered on blankets |
| `towers` | | `tower` | `n` 1–6 cubes, rule `plus_one` |
| `blocks` | | `letter` | on toy blocks |
| `balloons` | | `card` | on balloons |
| `garden` | | `pict` | to its first letter |
| `village` | | `pict` with its `word` | answered by `wcard` |
