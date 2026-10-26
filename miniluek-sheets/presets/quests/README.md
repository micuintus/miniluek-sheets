# Quest lanes: circus, sea post, ice palace

Three story lanes that revisit the courses' operations in the same miniLÜK box: a day at the
unicorn circus (numbers, 13 sheets), the mermaid's sea post (letters, 7) and the ice palace
(logic, 4). Each lane ships in English and German and builds like a course:

```bash
python3 scripts/miniluek.py build presets/quests/circus-numbers.json -o circus.pdf --key
```

| Lane | English | German |
|---|---|---|
| Numbers | `circus-numbers.json` | `zirkus-zahlen.json` |
| Letters | `sea-letters.json` | `meer-buchstaben.json` |
| Logic | `palace-logic.json` | `eispalast-logik.json` |

The course picture twins (S1b to S13b, A1b to A6b) tell their own stories inside the courses;
these lanes come on top of them.

## How a quest sheet works

A quest sheet is a picture sheet of the generator: the scene on top, then title, worked
examples and control pattern, then the answer grid, all in the courses' geometry. The scene
draws each station from its task, and the sheet's rule derives the answer from the same task,
so a station cannot show something other than what its answer counts, names or continues. The
scenes live in `scripts/quest_scenes.py`. The sheet id (C4, M2, P1) prints small at the lower
left of every page, so a goal line that says "after S1" can be found in the course PDF.

Pink stations 1–6 sit in the left half, blue 7–12 in the right. One half is one sitting of six
tiles, and the adult checks only the placed tiles against the pattern. The title tells the
story beat and the task; the grey goal line names the stop and, for C1 to C12 and M1 to M7,
the course sheet it revisits. Half a sheet per sitting is a design choice, untested.

C1 to C12 and M1 to M7 come after their course sheet as a revisit, never as the teaching.
C13 and P1 to P4 have no course sheet. Each is the first sheet for its operation and comes
after the same idea with objects:

- C13: three cookies on a plate, eat one, "how many are left?"
- P1: an ABAB bead string, "which comes next?"
- P2: shape blocks in other colours and sizes.
- P3: three toy animals of one kind and one of another.
- P4: a toy placed on a 3 by 3 grid drawn on paper.

A story picture as the first sheet is untested.

## Coverage

C1 to C12 revisit all thirteen counting sheets (C5 revisits two), M1 to M7 the reading sheets;
C13 and P1 to P4 have no course sheet.

| Sheet | Scene (`picture`) | Operation | After | Evidence |
|---|---|---|---|---|
| C1 | jugglers (`juggling`) | same number in a new arrangement, 1–3 | S1 | Frye et al. 2013 [G]; the rearrangement itself is untested |
| C2 | breakfast (`breakfast`) | count, then match one to one, 1–6 | S2 | Frye et al. 2013 [G] |
| C3 | giant dice (`dice_meadow`) | dice patterns, checked by counting | S3 | Starkey & McCandliss 2014 [E] |
| C4 | finger theatre (`finger_theatre`) | finger patterns to dice, full hand = 5, counted from the thumb (German) or index finger (English) as in the course | S4 | Poletti et al. 2025 [R]; Kullberg et al. 2020 [R] |
| C5 | balloon contest (`contest`) | comparing sets | S5, S10 | Frye et al. 2013 [G]; Halberda & Feigenson 2008 [E] |
| C6 | circus trains (`trains`) | counting to the numeral | S6 | Krajewski & Schneider 2009 [C] |
| C7 | ticket booth (`ticket_booth`) | numeral to quantity | S7 | Mundy & Gilmore 2009 [E] |
| C8 | spotlights (`spotlights`) | counting a scattered set, each one once | S8 | Fuson 1988 [E] |
| C9 | tightrope (`tightrope`) | position on a path, 1–6 | S9 | Siegler & Booth 2004 [C]; Siegler & Ramani 2008, 2009 [R] |
| C10 | ring toss (`ring_toss`) | comparing written numbers, distances 2 to 4 | S11 | Schneider et al. 2017 [M]; Jacobson et al. 2011 [C] |
| C11 | magic chests (`magic_show`) | five and some more in a ten-frame, 3–8 | S12 | Krajewski & Schneider 2009 [C]; Kullberg et al. 2020 [R] |
| C12 | seal towers (`seal_show`) | one more, up to 7 | S13 | Schneider et al. 2021 [C]; Spaepen et al. 2018 [C] |
| C13 | party (`party`) | take-away: one is gone, count the rest | S13, no course sheet | the guide's basic problems add and remove items (Frye et al. 2013 [G]) |
| M1 | twin shells (`twin_shells`) | the same letter | A1 | NELP 2008 [M] |
| M2 | big and little fish (`fish_school`) | uppercase to lowercase | A2 | NELP 2008 [M] |
| M3 | bottle post (`bottle_post`) | letter to first-sound picture | A3 | NELP 2008 [M] |
| M4 | bubbles (`sea_finds`) | picture to first letter | A4 | NELP 2008 [M]; the reverse direction is untested |
| M5 | syllable fish (`syllable_bubbles`) | first syllable to picture | A5 | NELP 2008 [M] |
| M6 | post boats (`post_boats`) | printed word to picture | A6 | NELP 2008 [M] |
| M7 | parcels (`beach_post`) | picture to printed word, every first letter at least twice | A6b | NELP 2008 [M]; the shared-letter design is untested |
| P1 | necklaces (`necklaces`) | AB pattern, the gap always last; P1 practises extending, the trials also taught copying, translating and naming the unit of repeat | | patterning at 4 predicted fifth-grade math (Rittle-Johnson et al. 2017 [C], 517 children) |
| P2 | palace windows (`palace_windows`) | the same shape in another colour and size; P2 varies colour and size, not orientation | | children of 3 to 6 tell shapes apart mainly by visual matching (Clements et al. 1999 [E], 97 interviews) |
| P3 | winter party (`winter_party`) | odd one out: three alike, one of another kind | | oddity and seriation lessons improved those skills more than letter, number or art lessons, and the children identified letters better than the number and art groups (Kidd et al. 2012 [R], 72 Head Start children) |
| P4 | castle maps (`castle_hills`) | the same place in a 3 by 3 grid; P4 matches a place between two visible 3 by 3 layouts on paper | | spatial training works (Uttal et al. 2013 [M], g = 0.47) and moves math a little, less at preschool age (Hawes et al. 2022 [M], g = 0.28); spatial span and spatial recognition memory predicted math in 56 children aged 7 to 12, 29 of them heavily alcohol-exposed, alike in both groups, with IQ controlled only spatial recognition memory did (Crocker, Riley & Mattson 2015 [C]) |

Evidence types as in the course research: [M] meta-analysis or systematic review,
[R] randomised or controlled trial (Wijns et al. 2021 is quasi-experimental),
[C] correlational or cohort study, [G] guideline or practice guidance,
[E] experiment, descriptive or single-case study, book or narrative review.

Full references for the C and M rows are in the course research files
(`presets/counting_and_numbers/research.md`, `presets/reading/research.md`).

## Scenes and task kinds

The `picture` value in each preset is the scene name in `scripts/quest_scenes.py`. Task kinds
that only a scene draws, with their fields:

| Scene | Task kind | Fields |
|---|---|---|
| `juggling` | juggled tokens | `kind`, `n` 1–3, hearts or stars (pink) and moons or strawberries (blue) |
| `breakfast` | `seal`, `puppy` | `n` 1–6 |
| `dice_meadow` | `dice` | `n` 1–6 |
| `finger_theatre` | `fingers` | `n` 1–6, counted from the course habit |
| `contest`, `ring_toss` | `compare` | `a`, `na`, `b`, `nb`; every animal wins once and loses once |
| `trains` | `gift`, `star` | `n` 1–6 |
| `ticket_booth` | `ticket` | `n` 1–6 |
| `spotlights` | `heart`, `star` | `n` 1–6, scattered |
| `tightrope` | `rope` | `n` 1–6, counted from the flag |
| `magic_show` | `chest` | `n` 3–8 |
| `seal_show` | `balls` | `n` 1–6; the answer kind `balls` stacks them on one floor line |
| `party` | `plate` | `n` 1–6 left after one is eaten |
| `twin_shells`, `fish_school` | `letter` | `n` 0–25 |
| `bottle_post` | `card` | a course word |
| `sea_finds` | `pict` | a picture and its first letter |
| `syllable_bubbles` | `syll` | `text` and `word` from the course list |
| `post_boats` | `wcard` | `word` from the course list |
| `beach_post` | `pict` | a picture bound to its `word` |
| `necklaces` | `necklace` | `pic` (the next charm) and a different `other` |
| `palace_windows` | `shape` | `n` 0–5 (circle, square, triangle, rectangle, star, heart); the answer kind `shape` is the same shape in gold |
| `winter_party` | `odd` | `same`, a different `pic`, `at` 0–3 |
| `castle_hills` | `castle` | `n` 0–8, the window the princess looks out of; the answer kind `map` marks it with a star |

## Design rules

The rules follow the course picture sheets and are untested on these sheets; evidence in
[research](../counting_and_numbers/research.md#picture-sheets).

- One operation per sheet, and every item asks it the same way: the gap is always last, the
  odd guest always differs in kind, the acrobat is always counted from the flag.
- Nothing that is counted appears loose in the picture. The take-away plates show crumbs where
  the eaten cookie was, never a second cookie.
- Counted things are plain tokens; C2 counts seals and puppies as S2 counts princesses and
  frogs. Nothing else countable decorates a station.
- Pink and blue mark the two families. Charms, tokens and props avoid both colours.
- Two things the child must tell apart differ in colour and outline (each necklace's two
  charms, the odd guest and the three others).
- Comparing sheets use twelve animals, each wins once and loses once, so every loser is also a
  right answer elsewhere on the grid.
- Letters use only the course word lists.

## Limits

No study tested miniLÜK, story pictures or these sheets; every row borrows evidence from
studies of the skill. The finger studies tested typically developing children, the patterning,
oddity and shape studies unselected, partly low-income preschoolers. Patterning
trials improved patterning but not number skills (Wijns et al. 2021 [R], quasi-experimental,
147 children; Zippert et al. 2021 [R], randomised, 211 children), and the practice guide rates its geometry and patterns
recommendation as minimal evidence (Frye et al. 2013 [G]), so the logic lane practises its own
skills. Kidd et al. 2012 taught oddity together with seriation, with toy animals over most of
a school year, and comes from one research group. The take-away
sheet shows what is left, so it practises the take-away story with counting; naming the number
just before lags naming the number just after until about 5 1/2 (Fuson, Richards & Briars 1982
[E], spoken questions to samples of 24).

## Sources added for the quest lanes

- [C] **Crocker, Riley & Mattson 2015.** Visual-spatial abilities relate to mathematics
  achievement in children with heavy prenatal alcohol exposure. *Neuropsychology* 29(1), 108–116.
  doi:10.1037/neu0000094
- [E] **Clements, Swaminathan, Hannibal & Sarama 1999.** Young children's concepts of shape.
  *JRME* 30(2), 192–212. doi:10.2307/749610
- [E] **Fuson, Richards & Briars 1982.** The acquisition and elaboration of the number word
  sequence. In C. J. Brainerd (Ed.), *Children's Logical and Mathematical Cognition*, 33–92. Springer.
  doi:10.1007/978-1-4613-9466-2_2
- [M] **Hawes, Gilligan-Lee & Mix 2022.** Effects of spatial training on mathematics
  performance: a meta-analysis. *Dev Psychol* 58(1), 112–137. doi:10.1037/dev0001281
- [R] **Kidd et al. 2012.** Benefits of an intervention focused on oddity and seriation.
  *Early Educ Dev* 23(6), 900–918. doi:10.1080/10409289.2011.621877
- [C] **Rittle-Johnson, Fyfe, Hofer & Farran 2017.** Early math trajectories: low-income
  children's mathematics knowledge from ages 4 to 11. *Child Dev* 88(5), 1727–1742.
  doi:10.1111/cdev.12662
- [C] **Schneider, Sullivan, Guo & Barner 2021.** What counts? Sources of knowledge in
  children's acquisition of the successor function. *Child Dev* 92(4), e476–e492.
  doi:10.1111/cdev.13524
- [M] **Uttal et al. 2013.** The malleability of spatial skills: a meta-analysis of training
  studies. *Psychol Bull* 139(2), 352–402. doi:10.1037/a0028446
- [R] **Wijns, Verschaffel, De Smedt, De Keyser & Torbeyns 2021.** Stimulating preschoolers'
  focus on structure in repeating and growing patterns. *Learn Instr* 74, 101444.
  doi:10.1016/j.learninstruc.2021.101444
- [R] **Zippert, Douglas, Tian & Rittle-Johnson 2021.** Helping preschoolers learn math: the
  impact of emphasizing the patterns in objects and numbers. *J Educ Psychol* 113(7), 1370–1386.
  doi:10.1037/edu0000656
