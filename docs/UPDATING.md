# Keeping Brick Aggregat current

Goal: find out what changed without reading every repo again. Most runs end with "Nothing to do".

## Scope

- **In:** software with public source for the TrimUI Brick, Brick Hammer and Brick Pro (TG3040/TG4040), and NextUI
  `tg5040` paks (that platform covers the Brick). Smart Pro projects only when they are music apps on the same platform.
- **Also listed, marked:** apps without a licence, without source, or without any repo (itch.io, Gumroad, a website):
  many Brick music apps are published that way. They carry a mark; "open source only" on the website hides them.
  Dormant entries (no commit for a year) show on request.
- **Out:** other devices, the Smart Pro S (TG5050) on its own, ROM downloaders for third-party sites, firmware images
  or binaries in this repo (links only).

## Every three days, automatically (`.github/workflows/update.yml`)

1. `scripts/check_updates.py`: one `git ls-remote` per repo; only when HEAD or tags moved, a blobless depth-1 clone
   reads the last commit date, licence, `pak.json`, file counts (source or not). Writes `state/meta.json`, logs
   releases, licence changes and repos that went offline or came back to `state/changes.json`, and lists everything
   since the last review in `state/CHANGES.md`.
2. `scripts/repo_meta.py`: description, stars, archived flag, creation date (batched GitHub search).
3. `scripts/find_new.py`: GitHub (names, descriptions, README text, forks, topics), the NextUI Pak Store, itch.io tag
   feeds and, with a `YOUTUBE_API_KEY` secret, YouTube (video titles and the links in their descriptions), all
   configured in `data/sources.yml`; finds in none of
   `data/projects.yml`, `data/candidates.yml`, `data/ignore.yml` go to `state/NEW.md`.
4. `scripts/discussions.py`: the latest Discussions for the Ask tab.
5. `scripts/rebuild.py`: `validate.py`, then `build.py` (website data, catalogue pages, knowledge pages, feed).

The workflow only touches generated files. It never edits `data/`.

## Review run (scheduled agent session, every three days, or by hand)

1. `git pull`. Run `python3 scripts/check_updates.py` and `python3 scripts/find_new.py` yourself if the workflow has
   not run since the last review (cheap; `find_new.py` needs `gh`).
2. Read only `state/CHANGES.md` and `state/NEW.md`.
3. `state/CHANGES.md`:
   - `release`: nothing to do unless the project's `note` names a version or feature that is now wrong; then fix the note.
   - `licence`: check the repo's LICENSE; nothing else to do (it is read automatically).
   - `unreachable`: try the URL; if the project moved, fix `repo`; if it is gone, leave it (the website marks it).
   - `back online`: nothing to do.
4. `state/NEW.md`: read the README start of each repo (`git clone --depth 1 --filter=blob:none --no-checkout URL d &&
   git -C d show HEAD:README.md | head -60`), then
   - itch.io and YouTube finds: open the page; a video usually links the download (itch.io, Gumroad, GitHub). Entries
     without a GitHub repo get `url:` (download page) instead of `repo:`; a video that links nothing goes to
     `data/candidates.yml` with its URL until a download page shows up.
   - add an entry to `data/projects.yml` (id, name, author, category, repo, runs_on, devices, `added: <today>`;
     a `note` in your own words for music apps, firmwares and developer resources), or
   - add it to `data/ignore.yml` with a one-line reason (other device, no description, copy of a listed repo, out of
     scope), or
   - put it in `data/candidates.yml` when the README does not settle it.
5. Music apps get extra care: they are this index's focus. Check `runs_on` and `devices` against the README and
   write the note (what it is, which firmware, notable hardware support such as USB MIDI or USB audio).
6. New facts for developers (latency, USB, firmware quirks) found in a README or answered in Discussions go into
   `knowledge/` with a source key in `knowledge/SOURCES.md`.
7. `python3 scripts/check_updates.py --only <new ids>` (stores their baseline), `python3 scripts/check_updates.py --ack`,
   set `checked:` in `data/projects.yml` to today, `python3 scripts/rebuild.py`, commit and push.

## Adding a project by hand

Add it to `data/projects.yml` with a `repo:` URL and `added:` date and run `python3 scripts/check_updates.py --only
<id>` and `python3 scripts/rebuild.py`. Everything else (licence, version, activity) is read from the repo.
