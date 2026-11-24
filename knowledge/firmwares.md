# Firmwares, as a developer sees them

What a program meets on each firmware. Full project entries (versions, activity) are on the website's
Firmware tab and in [`catalog/os.md`](../catalog/os.md).

| Firmware | Base | Platform / app folder | Audio | glibc | How an app is packaged | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Stock TrimUI OS | Tina Linux | `Apps/<name>/` with `config.json` | ALSA directly | (stock) | stock app folder | {tbr-audio} {handkit-platforms} |
| NextUI | MinUI fork, runs on the stock system | `Tools/tg5040/<Name>.pak/`, `Emus/tg5040/<TAG>.pak/` | as stock | as stock | `.pak` folder with `launch.sh` | {nextui-paks} |
| MinUI | the stock system | as NextUI (`.pak`) | as stock | as stock | `.pak` folder | {nextui-paks} |
| NX Redux | NextUI fork | `.pak`, as NextUI | as stock | as stock | `.pak` folder | {nxredux} |
| CrossMix-OS | stock interface, extended | `Apps/` | as stock | as stock | stock app folder | {handkit-platforms} |
| spruce | SD-card layer on the stock system | spruce app folders | as stock | as stock | spruce app | {handkit-platforms} |
| KNULLI | Batocera | Ports (PortMaster) | (Batocera) | 2.40 `[src]` | PortMaster port or a script in Ports | {handkit-platforms} |
| muOS (MustardOS) | own system on the vendor kernel | `.muxapp` | PipeWire + WirePlumber | 2.38 or newer `[src]` | `.muxapp` | {tbr-audio} {handkit-platforms} {tbr-muos} |
| TortOS | plastron (own minimal Linux) | own | own | own | see project | {tortos} |

Notes:

- **Same kernel and GPU driver everywhere** that keeps the vendor kernel: 4.9.191 with the PowerVR fbdev driver
  (`libpvrNULL_WSEGL`) on stock, NextUI and KNULLI `[src]` {handkit-platforms}.
- **SDL2 comes with the firmware**: on the stock system in `/usr/trimui/lib`, on muOS in `/opt/muos/frontend/lib`.
  The sydilaxe apps link against a stub and use the firmware's library `[hw]` {tbr-hw}. Handkit instead links SDL3
  statically and needs only glibc and the GPU driver from the firmware {handkit}.
- **One binary for several firmwares**: building against glibc 2.28 runs on both the stock system and muOS `[hw]`
  {tbr-hw}; Handkit targets 2.33 {handkit}.
- **NextUI switches the CPU governor to `performance`** before any pak and resets it after; tools that do not need
  it should call `governor.sh powersave` or `auto` {nextui-paks}.
- **Root everywhere**: apps can write sysfs, use `SCHED_FIFO` and `mlockall` `[hw]` {tbr-hw}.
