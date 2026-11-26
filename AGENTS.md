# AGENTS.md

Instructions for coding agents. Two kinds of agent read this: **users**, who build something for the TrimUI Brick
and want the knowledge here, and **maintainers**, who change this repository.

## If you are developing for the TrimUI Brick

1. Read [`knowledge/README.md`](knowledge/README.md), then the page you need: devices, firmwares, building, paks,
   audio-midi. Facts cite sources in braces (resolved in `knowledge/SOURCES.md`) and carry `[hw]` / `[src]` / `[doc]`
   / `[?]` tags. Prefer `[hw]`. Everything is second-hand: check the cited source before relying on a path or a number.
2. Before building something, check what exists: `export/projects.json` (filter on `category`, `runs_on`,
   `devices`, `open`) or the Markdown lists in `catalog/`.
3. Open questions are in `knowledge/open-questions.md`. If your project settles one, say so in a Discussion or a pull
   request with your device, firmware version and date.
4. Ask humans in [Discussions → Q&A](https://github.com/70b185/BrickAggregat/discussions/categories/q-a).

## If you are changing this repository

- **Edit sources, never generated files.** Sources: `data/*.yml`, `knowledge/*.md`, `scripts/`, `index.html`,
  `assets/`. Generated: `catalog/`, `export/`, `kb/`, `state/`, `feed.xml`, `llms.txt`, `sitemap.xml`, the counts
  block in `README.md`.
- After a data change: `python3 scripts/validate.py && python3 scripts/build.py`. For a new entry also
  `python3 scripts/check_updates.py --only <id>` so its licence and version are read.
- Notes (`note:`) are in our own words, one or two sentences: what it is, which firmware, notable hardware support.
  Never copy README paragraphs.
- The review procedure (what to do with `state/CHANGES.md` and `state/NEW.md`) is in
  [`docs/UPDATING.md`](docs/UPDATING.md).
- No binaries, firmware images or other projects' code in this repo.
