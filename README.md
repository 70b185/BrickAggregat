# Brick Aggregat

**Every open-source project for the TrimUI Brick in one place, and what their developers found out.** Music apps,
firmwares, emulators and tools for the Brick, Brick Hammer and Brick Pro are spread over hundreds of repos, the
NextUI Pak Store, itch.io pages and Discord servers. This index lists them with their licence, latest version and
how recently they moved, and keeps a knowledge base and a Q&A for people who build for the Brick. Links and short
notes only; every entry points to the original project.

**[Open the website](https://70b185.github.io/trimui-music-apps/)**

<!-- counts -->
**475 projects** (324 with a licence and source, 359 with commits in the last 90 days), checked 2026-11-25:

[Make music](https://70b185.github.io/trimui-music-apps/?c=music-make) 57 · [Listen](https://70b185.github.io/trimui-music-apps/?c=music-play) 29 · [Firmware](https://70b185.github.io/trimui-music-apps/?c=os) 47 · [Apps & tools](https://70b185.github.io/trimui-music-apps/?c=app) 130 · [Emulators](https://70b185.github.io/trimui-music-apps/?c=emulator) 60 · [Games & ports](https://70b185.github.io/trimui-music-apps/?c=port) 33 · [Video & reading](https://70b185.github.io/trimui-music-apps/?c=media) 22 · [Look](https://70b185.github.io/trimui-music-apps/?c=theme) 20 · [Developer](https://70b185.github.io/trimui-music-apps/?c=dev) 52 · [Guides & companions](https://70b185.github.io/trimui-music-apps/?c=guide) 25
<!-- /counts -->

## Looking for software

Pick a list: [make music](https://70b185.github.io/trimui-music-apps/?c=music-make) (instruments, trackers,
samplers, M8 clients) · [listen](https://70b185.github.io/trimui-music-apps/?c=music-play) ·
[firmware](https://70b185.github.io/trimui-music-apps/?c=os) · [emulators](https://70b185.github.io/trimui-music-apps/?c=emulator) ·
[games & ports](https://70b185.github.io/trimui-music-apps/?c=port) · [apps & tools](https://70b185.github.io/trimui-music-apps/?c=app).
Filter by firmware (NextUI, KNULLI, muOS, …) and device. The same lists as Markdown are in [`catalog/`](catalog/README.md).

Each entry says whether it is open source: "no licence", "no source" (releases only) or "no repo" (itch.io,
Gumroad or a website only) mark the rest. Tick "open source only" to hide them; dormant projects show on request.

## Building for the Brick

- **Knowledge base:** [`knowledge/`](knowledge/README.md), also [on the website](https://70b185.github.io/trimui-music-apps/kb/):
  devices, firmwares, toolchains, paks, and sound and MIDI for music apps, each fact with a source.
- **Ask:** [Discussions → Q&A](https://github.com/70b185/trimui-music-apps/discussions/categories/q-a). Settled answers
  move into the knowledge base.
- **What exists already:** the [developer list](https://70b185.github.io/trimui-music-apps/?c=dev) (toolchains, UI
  libraries, input daemons, kernels).

## Data

- [`data/projects.yml`](data/projects.yml): the catalogue (edit this). Category, firmwares, devices, our note.
- [`state/meta.json`](state/meta.json): read from each repo every three days (licence, last commit, tags, `pak.json`, stars).
- [`export/projects.json`](export/projects.json): both merged, for scripts and the website.
- [`data/ignore.yml`](data/ignore.yml): repos the search found that are out of scope, each with a reason.

## How it stays current

Every three days the [update workflow](.github/workflows/update.yml) reads every repo (one `git ls-remote` each,
a small clone only when something moved), refreshes stars and descriptions, searches GitHub and the NextUI Pak Store
for new projects and rebuilds the site. A review run then sorts new finds in and writes notes. Details:
[docs/UPDATING.md](docs/UPDATING.md).

## Contributing

Add or correct a project with the [issue forms](https://github.com/70b185/trimui-music-apps/issues/new/choose) or a
pull request against `data/projects.yml`; add knowledge with a pull request against `knowledge/` (one source per
fact). `python3 scripts/validate.py` checks your change. See [CONTRIBUTING.md](CONTRIBUTING.md).

Licence: [CC0](LICENSE) for this index's own text, data and scripts. The listed projects keep their own licences.
