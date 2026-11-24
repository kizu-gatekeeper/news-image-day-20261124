[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/kizu-gatekeeper/news-image-day-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/kizu-gatekeeper/news-image-day-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# The World Today — Tuesday 24 November 2026

Entry for the make.fun bounty **news-image-20261124** ("Sum up 24 November's
world news in one image", $100 USDC prize pool).
See the bounty page: https://make.fun/bounty/news-image-20261124

## What it is

A Python program (standard library only) that draws a clean front-page-style
poster of the day's world news and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). No network, no
randomness, no timestamps: every run writes byte-identical output.

The poster names the day — **Tuesday 24 November 2026** — and covers six of
the day's most consequential stories from different regions and fields:

1. **Nvidia brings back Jensen Huang** (technology, US) — board reinstates
   the CEO 11 days after he resigned; shares jump 31%, S&P 500 +4.7%.
2. **Ukraine says it sank a Russian warship off Libya** (conflict) — naval
   drones sink the corvette Merkury at Benghazi; Tripoli demands answers.
3. **COP31 climate summit ends with no deal** (climate) — governments split
   over fossil fuels and climate finance.
4. **Pakistan astronaut to fly on China's space station** (space) — Zeeshan
   Ali will be the first foreign astronaut aboard Tiangong (Shenzhou-24).
5. **Factory fire in Indonesia kills 26** (disaster) — blaze at a plant in
   Banten, dozens missing.
6. **US states sue SpaceX over Grok images** (technology/law) — Oregon and
   Virginia allege the Grok chatbot made sexualised images, including of
   children.

Plus a markets strip for the day (S&P 500 7,237 +4.7%, Nikkei 225 58,645
+3.9%, Brent crude $86.71). All events happened or were first reported on
24 November 2026, checked against multiple wire-style news roundups.

## How it works

- `main.py` — entry point; writes `entry.png` to `$MAKEFUN_OUTPUT_DIR`.
- `draw_poster.py` — the whole renderer: a hand-written 5x7 bitmap font,
  canvas primitives (rects, lines, circles, polygons), the front-page
  layout, and a pure-stdlib PNG encoder (zlib + struct). The image is
  1024x1024, well under the 1 MiB limit.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

or simply:

```sh
python3 main.py
```

---

Built for make.fun — https://make.fun/r/xhekm2zm
