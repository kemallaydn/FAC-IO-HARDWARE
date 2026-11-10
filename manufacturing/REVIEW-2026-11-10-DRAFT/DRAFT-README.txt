FAC-IO Mini V1 — DRAFT PCB review candidate
Generated: 2026-11-10
Source CAD: hardware/FAC-IO-Mini-V1.kicad_pcb and current project design files
CAD tool: KiCad 10.0.8

This folder contains a current bare-board Gerber/Excellon package and current ERC/DRC evidence for independent review. It is not approved for fabrication. Do not upload/order this package until a named reviewer records approval and the fabricator accepts layer mapping, stackup, drill/slot interpretation, and manufacturing rules. The project remains NOT production-ready.

Validation: current schematic ERC has 0 violations; refilled PCB DRC and schematic parity have 0 violations, 0 unconnected items, and 0 parity issues. Current Gerber and decimal-format Excellon exports were compared with DRAFT-1.2 after normalizing only export timestamps; all 11 Gerbers and both drill files match. ZIP contains the current KiCad export outputs.

Unclosed checks: independent electrical/safety review; fabricator CAM/stackup and drill/slot acceptance; Robotistan board-specific price and material acceptance; assembly/component sourcing if PCBA is desired; first-article electrical, Ethernet, reset/brownout, and relay timing/fail-safe tests. The Gerbonara G90 warning is explained in `review/gerber-parse.txt` and `review/excellon-structure.txt`; this is not Robotistan CAM acceptance. Use only the isolated low-voltage barrier command contacts, never motor or mains.

The authoritative project CAD remains in hardware/. This review bundle is a copy. Any source or package change requires re-running CAD checks and review.
