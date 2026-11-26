# Contributing

Thanks for helping. Three kinds of contribution, smallest first:

1. **Report a project or a mistake**: the [issue forms](https://github.com/70b185/BrickAggregat/issues/new/choose).
2. **Edit the data**: `data/projects.yml` (fields explained at the top of the file). Do not edit generated files
   (`catalog/`, `export/`, `kb/`, `feed.xml`, `state/`); the update workflow rebuilds them.
3. **Add knowledge**: a pull request against `knowledge/`. Every fact needs a source: add a key to
   `knowledge/SOURCES.md` and cite it in braces. Tag how sure it is: `[hw]` seen on a device, `[src]` read in source
   code, `[doc]` stated without a test, `[?]` unclear. Settled questions leave `open-questions.md`.

Before you open the pull request:

```sh
pip install pyyaml markdown
python3 scripts/validate.py     # fields, vocabularies, duplicates, source keys
python3 scripts/build.py        # optional: see the result in export/ and kb/
```

Ground rules: links and short notes in our own words, no binaries, firmware images or copied code. Development
questions belong in [Discussions → Q&A](https://github.com/70b185/BrickAggregat/discussions/categories/q-a).
