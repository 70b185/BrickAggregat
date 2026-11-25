# Open questions

Things sources disagree on or nobody has tested. Discuss them in
[Discussions → Q&A](https://github.com/70b185/trimui-music-apps/discussions/categories/q-a); when one is settled on
a device, write the answer into the right page with device, firmware version and date, and remove it here.

| # | Question | Why it matters | Sources |
| --- | --- | --- | --- |
| Q1 | **Can the Brick's bottom USB-C port be a sound card and MIDI device for a computer or iPad?** A FunctionFS probe found no USB audio/MIDI gadget in the kernel and could not bind isochronous endpoints both ways; OZMA's README says its Brick plays into an iPad over USB as sound card and MIDI port. Is OZMA using bulk endpoints with its own protocol, a one-way isochronous stream, or something else? | Recording a Brick straight into a DAW | {tbr-hw} {ozma} |
| Q3 | **Does the Brick Hammer have the Brick's 14-LED layout?** | LED meters and feedback | {tbr-hw} {ledoh} |
| Q4 | **Brick Pro L2/R2: analog or digital?** Spec sheets disagree | expressive control in instruments | {tbr-hw} |
| Q5 | **Audio input on the Brick**: PolyBrik's sample recorder records silence on NextUI; BrickTape (KNULLI) records from the mic and USB, GrainBrick (KNULLI) processes live input, Conduit (muOS) records from the mic or a USB interface. Is input a firmware question (mixer setup) rather than hardware? | sampling on the device | {polybrik} {bricktape} {conduit} |
| Q6 | **Lowest usable latency on NextUI** with the internal codec (no USB interface): has anyone measured it? | live playing | |
| Q7 | **USB MIDI on NextUI**: which projects get class-compliant MIDI working there, and is anything missing in NextUI's kernel/modules compared with KNULLI? | controllers for NextUI paks | {lgpt} {polybrik} {polytracker} |
