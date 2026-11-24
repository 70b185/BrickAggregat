# Building, deploying, testing

## Toolchains

| Toolchain | What it is | Use it for | Source |
| --- | --- | --- | --- |
| TrimUI SDK (TG5040) | TrimUI's own SDK and cross toolchain for the platform | the vendor baseline | {trimui-sdk} |
| NextUI `tg5040-toolchain` | Docker image; `make shell` drops into a container with the toolchain in `/opt/` and your `./workspace` mounted | building NextUI and paks the NextUI way | {nextui-toolchain} |
| MinUI `union-tg5040-toolchain` | MinUI's Docker image, based on TrimUI's | MinUI-style builds | {minui-toolchain} |
| Handkit | pinned Zig/Clang 19 toolchain for aarch64 glibc 2.33, SDL3 with PowerVR/Mali backends, helper library, `.pak` packaging; no Docker | native SDL3 apps | {handkit} |
| zig + SDL2 stub | cross-compile with zig, link against a stub of SDL2 and use the firmware's SDL2 at run time | apps for stock and muOS from one binary | {tbr-build} |
| `minui-toolchain-images` | builds MinUI toolchain images | MinUI devices in general | {josegonzalez-toolchains} |

Building NextUI itself: Docker for device builds, a native `desktop` platform for fast UI work on the host.
arm64 hosts (Apple Silicon) are the least trouble; x86_64 hosts have hit missing arm64 libraries in Docker {nextui-build}.

## UI libraries for paks

- **Apostrophe**: header-only C UI toolkit for NextUI paks {apostrophe}
- **Gabagool**: Go UI library for paks (used by the Pak Store) {nextui-paks}
- **Dot**: the C + SDL2 UI shared by the Kino, Musicdisk, Tuner and Speed paks {dotui}
- **minui-list / minui-keyboard / minui-presenter / minui-progress / minui-detail**: ready-made screens for
  shell-script paks {minui-shell-tools}

## Getting it onto the device

- **USB + adb**: Handkit's `tools/handkit deploy` installs a pak over USB with adb enabled on the handheld {handkit}.
  If adb stops answering, the Restart ADB pak brings it back without a reboot (needs BaseOS).
- **SSH**: the stock firmware 1.1.1 added SSH {trimui-fw-brick}; on NextUI the Toggle Native SSH pak or the
  Dropbear pak start a server.
- **SD card**: copy the `.pak` folder to `Tools/tg5040/` (not into `.system/`, which updates replace) {nextui-paks}.

## Testing without a device

- **trimui-brick-emu** runs the Brick's stock system on a Linux PC {brick-emu}.
- **NextUI's `desktop` platform** runs NextUI on the host for UI work {nextui-build}.
- **Handkit's device test** pak runs an input self-test and a rendering demo and writes a report you can attach
  to an issue {handkit}.
