# Sound and MIDI

For instruments, trackers, samplers and players. The most detailed public source is {tbr-audio}
(sydilaxe's notes from their muOS apps, with a shared C library, {brickio}); this page summarises it and adds what
other projects report. Read the sources for code.

## The audio path per firmware

| | Stock, NextUI, MinUI, CrossMix | muOS |
| --- | --- | --- |
| Server | ALSA directly `[src]` | PipeWire + WirePlumber `[src]` |
| Built-in card | `audiocodec` (card 0) | same card, as a PipeWire sink |
| Speaker | mono | mono |
| Headphones | 3.5 mm stereo | 3.5 mm stereo |
| USB audio | an ALSA card | a PipeWire sink |

Source: {tbr-audio}. On muOS, log `SDL_GetCurrentAudioDriver()` at start to know whether SDL went through PipeWire
or ALSA's PipeWire plugin.

**USB audio on NextUI**: one project found that the stock audio library pins ALSA's `default` device to the internal
codec (and rewrites `hw:0,0` to `hw:1,0`), so SDL never reaches a USB card. Their fix: find the USB card in
`/proc/asound/cards` in `launch.sh`, then point SDL straight at it with `SDL_AUDIODRIVER=alsa` `[hw]` {trimui-fixes}.
**USB audio on the Brick Pro stock OS**: the stock ALSA config defines `sysdefault` without a `CARD` argument, so
SDL3 cannot open `sysdefault:N` to list cards and misses USB audio; an `.asoundrc` that overrides
`ctl.sysdefault`/`pcm.sysdefault` for the app process alone fixed it `[hw]` {m8c-brickpro-stock}. The stock kernel
has `cdc_acm` built in, so USB serial devices appear as `/dev/ttyACM0` `[hw]` {m8c-brickpro-stock}.

**USB audio on the Brick Pro with NextUI 6.15.0**: the volume buttons act on the first non-internal card, which can be
a USB source (an M8) rather than the USB headphone adapter; one port therefore picks its output card in `launch.sh`
and bridges audio with `arecord`/`aplay`. The built-in headphone output had audible noise and clicks even with
nothing playing, cause unknown `[hw]` {m8c-brickpro-nextui}.

SideB prefers a USB DAC whenever the system exposes it as an ALSA card `[hw]` {sideb}.

## Latency and buffers

- Opening a USB interface **directly through `plughw:CARD=<id>`** (skipping `dmix`/`dsnoop` and PipeWire) took
  latency from about 90 ms to about 25 ms in the sydilaxe apps `[hw]` {tbr-audio}; full duplex at 64 frames gave
  about 4 ms round trip `[hw]` {brickio}.
- Buffers that worked: 512 frames at 48 kHz (~10.7 ms) for synths, 1024 for stream decoding; brickio starts at
  256 and grows only after dropouts `[hw]` {tbr-audio}.
- Engines pick one rate and resample on load: brickrack and TimeATronics' player run at **48 kHz** {brickrack}
  {tm-player}; Ambience converts everything to 44.1 kHz stereo {ambience}.

## Real-time habits that paid off

All `[hw]` in {tbr-audio}:

- Render on your own thread into a ring buffer; let the SDL callback only copy (its timing is uneven on PipeWire).
- `SCHED_FIFO` for the render thread (they use 45; MIDI 40), switchable by an environment variable.
- Pin threads with `pthread_setaffinity_np` (voices on core 2, effects on core 3, leave 0–1 to UI and system).
- `mlockall(MCL_CURRENT | MCL_FUTURE)` so audio never waits on a page fault.
- Flush denormals to zero on every audio thread (set FZ in AArch64's FPCR); reverb tails otherwise cost many times
  the CPU.
- Set the governor to `performance` with all four cores online while the instrument runs; restore it on exit.
- Watch the callback rate; if a driver gets stuck feeding at half speed, reopen the device.

## USB ports

- On the Brick the **top USB-C port is the host** (MIDI controllers, audio interfaces, hubs); it supplies about
  500 mA, so use a powered hub for hungry devices `[hw]` {tbr-hw}.
- On the Brick Pro the **top port** is the host too: an M8 Headless (Teensy) is found there and not on the bottom
  port (stock OS, November 2026) `[hw]` {m8c-brickpro-stock}.
- The **bottom port** charges and can be a USB device (gadget). The kernel has no USB audio or USB MIDI gadget
  function; a FunctionFS probe bound one isochronous endpoint in one direction but not one each way `[hw]` {tbr-hw}.
  OZMA's README nevertheless describes the bottom port as "sound card + MIDI port" for an iPad `[doc]` {ozma}.
  How is listed in [open-questions.md](open-questions.md).

## USB MIDI

- ALSA raw MIDI: scan `/dev/snd/midiC*D*`, open `O_RDWR | O_NONBLOCK`, rescan every second or two for hot-plug,
  read on a thread of its own `[hw]` {tbr-audio}.
- The ALSA sequencer works too (pocketpads uses it through ctypes, untested with real hardware at the time) {pocketpads}.
- Clock out: 24 pulses per quarter note plus START/STOP, timed to when the sound is heard (add about one buffer of
  output latency) `[hw]` {tbr-audio}.
- mgba-midisync turns the Game Boy link port into USB MIDI clock for LSDj and FMS `[hw]` {mgba-midisync}.
- PolyTracker (KNULLI) supports class-compliant USB MIDI and USB audio out on the host port; PolyBrik (NextUI) does
  not yet `[doc]` {polytracker} {polybrik}.
- Little Piggy Tracker's MIDI depends on kernel support per firmware `[doc]` {lgpt}.

## Syncing without USB

HI5 and Columbia Street put the mix in mono on one side of the headphone jack and clock pulses on the other, to
drive a Pocket Operator or Volca `[hw]` {tbr-audio}.

## Recording

- M8Tape captures the Dirtywave M8's 24-channel USB audio with `arecord` (24-bit, 44.1 kHz) and splits each take
  into 12 stereo files `[hw]` {m8tape}.
- On the Smart Pro, the built-in microphone records mono 16-bit 44.1 kHz; the default "Line In" source is noisy
  on the right channel `[hw]` {picotracker-trimui}. Whether the same holds on the Brick: not reported.
