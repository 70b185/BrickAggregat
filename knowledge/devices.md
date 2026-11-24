# The devices

| | Brick / Brick Hammer | Brick Pro |
| --- | --- | --- |
| Model | TG3040 {trimui-fw-brick} | TG4040 {trimui-fw-brickpro} |
| SoC | Allwinner A133P, 4× Cortex-A53, PowerVR GE8300 `[doc]` {tbr-hw} | same `[doc]` {tbr-hw} |
| Clock | sold as 1.8 GHz; muOS configures 408 MHz–2.0 GHz `[src]` {tbr-hw} | same |
| RAM / storage | 1 GB, 8 GB eMMC + microSD `[doc]` {tbr-hw} | same `[doc]` {tbr-hw} |
| Screen | 3.2" IPS, 1024×768, 60 Hz `[doc]` | 3.95" IPS, 1024×768, 60 Hz `[doc]` {tbr-hw} |
| Battery | 3000 mAh `[src]` {tbr-hw} | 5000 mAh `[src]` {tbr-hw} |
| Sticks | none | two Hall-effect sticks, clickable `[doc]` |
| Extra buttons | F1, F2, side switch, MENU | as Brick, plus HOME, L3, R3 `[src]` {tbr-hw} |
| Addressable LEDs | 14 RGB (measured on a Brick) `[hw]` {ledoh} | 22 used `[hw]` {tbr-hw} |
| Speaker | mono `[src]` {tbr-hw} | mono `[src]` {tbr-hw} |
| Audio out | 3.5 mm headphone jack | 3.5 mm headphone jack |
| USB | two USB-C: top = host, bottom = charging and USB device (gadget) `[hw]` {tbr-hw} | which port is the host: [open](open-questions.md) |
| Kernel | Linux 4.9.191, Allwinner BSP `[src]` {tbr-hw} {handkit-platforms} | same |

The Brick Hammer is a Brick variant: muOS treats it as the same board (`tui-brick`) and the sydilaxe apps ship one
build for both `[src]` {tbr-hw}. Its LED layout is not yet confirmed to match.

## Telling them apart at run time

| Check | Brick / Hammer | Brick Pro | Source |
| --- | --- | --- | --- |
| `$DEVICE` on the stock system | `brick` | `brickpro` | {tbr-hw} |
| `/opt/muos/device/config/board/name` on muOS | `tui-brick` | `tui-brick-pro` | {tbr-hw} |
| `$PLATFORM` in a NextUI pak | `tg5040` | `tg5040` | {nextui-paks} |

## Useful paths (all `[src]` or `[hw]` as noted in the source)

| Path | What |
| --- | --- |
| `/sys/class/led_anim/` | RGB LEDs (zones, effects, per-LED frames); details in {tbr-leds} |
| `/sys/class/gpio/gpio227/value` | rumble motor |
| `/sys/class/power_supply/axp2202-battery/capacity` | battery percent |
| `/sys/class/thermal/thermal_zone0/temp` | SoC temperature (milli-°C) |
| `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor` | CPU governor |
| `/sys/class/graphics/fb0/blank` | screen blank (4 off, 0 on) |
| `/dev/snd/midiC*D*` | USB MIDI ports (ALSA raw MIDI) |
| `/proc/asound/cards` | sound cards; USB ones say `USB-Audio` |

All from {tbr-hw}, which lists more (Wi-Fi, charger, colour temperature) with a source per line.

## Controller

On the stock system the built-in controller ("TRIMUI Player1") reports as an Xbox 360 pad (USB `045e:028e`), so
SDL maps it without a custom mapping; F1, F2 and HOME need extra handling `[src]` {handkit-platforms}. muOS uses its
own input daemon with different button numbers ("muOS-Keys") `[src]` {handkit-platforms}. A user-space input daemon
for the TrimUI family is in {trimui-inputd}. Per-firmware button numbers: {tbr-input}.

## Graphics

The GPU is driven through the vendor fbdev driver with no window system; EGL takes native window `0` `[src]`.
OpenGL ES and Vulkan (`VK_KHR_display`) both ran on a Brick Pro under NextUI `[hw]` {handkit-platforms}.
