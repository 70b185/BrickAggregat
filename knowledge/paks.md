# NextUI and MinUI paks

A pak is a folder ending in `.pak` with a `launch.sh` in it {nextui-paks}.

| Kind | Where | Example |
| --- | --- | --- |
| Tool | `Tools/tg5040/<Name>.pak/launch.sh` | `Tools/tg5040/Grampus.pak/` |
| Emulator | `Emus/tg5040/<TAG>.pak/launch.sh` | ROMs in `Roms/Game Boy (GB)/` start `GB.pak` |

`tg5040` covers the Brick, Brick Hammer, Brick Pro and Smart Pro; `tg5050` is the Smart Pro S; `h700` the Anbernic
RG XX devices {nextui-paks}. Never put community paks in `.system/`: updates replace it.

## What `launch.sh` gets

NextUI passes `$PLATFORM`, `$DEVICE`, `$SDCARD_PATH`, `$SYSTEM_PATH`, `$LOGS_PATH`, `$USERDATA_PATH`, and for
emulators `$EMU_TAG`, `$ROM`, `$BIOS_PATH`, `$SAVES_PATH`, `$CHEATS_PATH`, `$CORES_PATH` {nextui-paks}.
Write logs to `$LOGS_PATH/<TAG>.txt` (users find them under `.userdata/<platform>/logs/`).

## Behaviour worth knowing

- **CPU governor**: NextUI sets `performance` before a pak and resets it after. A music player or menu should
  switch to `auto` or `powersave` through `$SYSTEM_PATH/bin/governor.sh`; an instrument that needs steady
  timing may want to stay on `performance` {nextui-paks}.
- **Brightness and volume**: some standalone programs reset them; `syncsettings.elf` restores the global
  settings around a launched binary {nextui-paks}.
- **Standalone programs** do not get resume, quicksave or NextUI's in-game menu; say so in your README {nextui-paks}.

## Getting into the Pak Store

The Pak Store (bundled with NextUI) lists paks from its storefront file. To be listed {pak-store}:

1. Put a `pak.json` in the repo root with `name`, `version`, `type`, `description`, `author`, `repo_url`,
   `release_filename` and `platforms` (e.g. `["tg5040"]`).
2. Zip the pak's contents (not the folder) and attach it to a GitHub release.
3. Tag the release `vX.Y.Z` matching `version` in `pak.json`; the asset name must match `release_filename`.
4. Ask for the pak to be added to the storefront (see the Pak Store README).

This index reads the storefront too: a pak listed there shows a "Pak Store" chip here.

## Further reading

- Jose Diaz-Gonzalez's guide to writing a pak, linked from the NextUI docs {nextui-paks}
- Handkit's `hk_add_pak()` builds a pak folder from CMake {handkit}
