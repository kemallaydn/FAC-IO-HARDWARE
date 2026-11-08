# Manufacturing — NOT RELEASED

This directory is reserved for output generated from a completed and independently reviewed KiCad board.

## Robotistan submission (checked 2026-11-08)

Robotistan's [PCB service](https://www.robotistan.com/pcb-servisi) requests a ZIP/RAR containing production Gerber layers (copper, solder mask, silkscreen, outline) and drill data for PCB fabrication. Its assembly flow additionally requests a BOM and Pick & Place file with matching references and positions. The current service page lists five boards as the standard minimum PCB order, so the earlier two-assembled-prototype target is a bring-up quantity, not an assumed order quantity. Confirm the final quantity and THT population with the supplier before ordering.

**Release gate:** Export all fabrication and assembly files from the same reviewed KiCad revision only after schematic ERC, PCB DRC, schematic/PCB parity, exact part/footprint verification and independent Gerber inspection pass. Do not upload the current draft board or its Gerbers for quotation or manufacture.

Required:
- Gerber layers: F/B copper, solder mask, silkscreen, edge cuts (and paste for assembly).
- Excellon plated and non-plated drill files as appropriate.
- BOM with exact manufacturer part numbers, quantity and designators.
- Pick-and-place/centroid file with rotation, side and designators.
- Assembly drawing, polarity/connector notes, and THT assembly confirmation.
- ERC/DRC reports, fabrication drawing, board thickness/stackup and design revision.

**No production Gerber is currently available. Do not upload any earlier test Gerber as FAC-IO.**
