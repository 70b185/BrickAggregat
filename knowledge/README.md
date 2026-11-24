# Developing for the TrimUI Brick

What people building apps, instruments and firmwares for the Brick family have found out, collected from
their public repositories. Everything here is second-hand: each fact names where it comes from (a key in braces, resolved
in [SOURCES.md](SOURCES.md)) and how sure it is. Read the original before you rely on a detail.

**Ask a question** in [Discussions → Q&A](https://github.com/70b185/trimui-music-apps/discussions/categories/q-a).
When the answer is settled, it moves into these pages with its source.

## Pages

| You need | Read |
| --- | --- |
| The devices: SoC, screen, RAM, USB ports, buttons, LEDs, sysfs paths | [devices.md](devices.md) |
| Which firmware does what: platform names, SDL, audio server, glibc, packaging | [firmwares.md](firmwares.md) |
| Toolchains, SDKs, cross-compiling, deploying, testing without a device | [building.md](building.md) |
| NextUI / MinUI paks: folder layout, `launch.sh`, environment, Pak Store | [paks.md](paks.md) |
| Sound and MIDI: audio path, latency, USB audio, USB MIDI, real-time threads | [audio-midi.md](audio-midi.md) |
| What nobody has settled yet | [open-questions.md](open-questions.md) |

## Evidence tags

- `[hw]` reported working (or failing) on a real device by the project cited
- `[src]` read from a firmware's or project's source code or config, not tested by us
- `[doc]` stated in documentation or a spec sheet, without a test result
- `[?]` sources disagree, or inferred; see [open-questions.md](open-questions.md)

## The Brick family in one paragraph

The Brick (TG3040), Brick Hammer and Brick Pro (TG4040) share TrimUI's Allwinner A133P platform with the Smart
Pro (TG5040): four Cortex-A53 cores, a PowerVR GE8300 GPU, 1 GB of RAM, an aarch64 glibc userland on a 4.9 vendor
kernel, and a 1024×768 screen {tbr-hw} {handkit-platforms}. NextUI calls this platform `tg5040` and ships one
build for all of them {nextui-paks}. The Smart Pro S (TG5050) is a different chip and needs its own builds.

## Contributing knowledge

Open a pull request against the page, with a source for each fact (a repo file, a release note, an issue, or
your own test with device, firmware version and date). Tag it. A failure on a real device is as useful as a
success.
