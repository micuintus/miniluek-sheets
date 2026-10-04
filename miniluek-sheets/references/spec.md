# Sheet-set JSON

```json
{
  "title": "Princess counting",
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
| `language` | `en` or `de` (labels at the bottom and in the fit test) |
| `title` | one or two lines, read aloud by the adult |
| `goal` | optional grey line for adults |
| `prompt` | optional coloured line next to the example |
| `theme` | `pink`, `lavender`, `peach`, `mint`, `gold`, `sky`, `rose`, `violet`, `coral`, `teal` |
| `rule` | `pair` with one or two `pairs` (left to right), `plus_one`, `same`, or `more` (comparing) |
| `show` | `numeral` on comparing sheets: numbers instead of dots |
| `task_style`, `answer_style` | `row`, `col`, `up`, `down`, `dice`, `scatter` (pictures only) |
| `size` | picture size in cm |
| `answer_size` | size of the single characters on comparing sheets (default 1.9) |
| `pattern` | index into the pattern library (default: sheet index) |
| `mascot` | decorative princess next to the title (default true) |
| `tasks` | exactly 12 entries `"kind:n"` (`"kind:n@1"` for the second pair when both pairs start with the same kind) or objects `{"kind": …, "n": …, "fam": …, "style": …, "size": …, "seed": …}` |

Special kinds: `princess` (n figures; `princess_size` overrides the height), `dice` (1–6),
`numeral`, `fingers` (1–10), `jewelbox` (0–10 in a ten-frame), `path` (1–6), and comparing
tasks written `"dog:4|cat:1"` (two characters with 1–6 dots each, for the rule `more`).

With two pairs, the first pair's tasks and answers get pink frames, the second pair's blue.

`check` (and `build`) verify: 12 tasks, all tasks distinct, all answers distinct, no answer
repeating a task picture (except on `plus_one` sheets), pairs used left to right, every picture
known, every control pattern uses each tile back once and is symmetric; on comparing sheets a
warning appears when a losing character never shows up among the answers.
