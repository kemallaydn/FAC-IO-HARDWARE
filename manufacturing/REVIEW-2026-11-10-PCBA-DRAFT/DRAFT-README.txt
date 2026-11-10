FAC-IO-Mini V1 — PCBA review draft, not approved for ordering

This package carries the current-source 4-layer Gerber/Excellon set plus the
Robotistan BOM and Pick & Place draft so the assembler can assess feasibility.
Do not submit this as an approved assembly order yet. release/NOT-APPROVED.txt
is intentional; no independent review or supplier acceptance is recorded.
For the assembly form that accepts XLSX, use bom/FAC-IO-Mini-V1.xlsx. It uses
the user's supplied default BOM template, groups exact manufacturer MPNs, and
lists quantity per board. EXT1 WIZ850io is listed for factory installation;
the 56 PCB placements remain in the separate Pick & Place file.

CAD validation: KiCad 10.0.8 ERC has 0 errors/warnings; refilled DRC/parity has
0 violations, 0 unconnected pads and 0 parity issues. The 56-entry PCBA BOM
matches current schematic values, footprints and MPNs; Pick & Place matches
56/56 unique references, positions, rotations and top-side placement.

Open PCBA items: supplier codes for C1, C2, L1, SW1 and SW2 are blank. Do not
substitute components without engineering review and CAD/BOM synchronization.
Robotistan's component-sourcing quotation must resolve these exact MPNs or return
engineering-approved equivalents before order. WIZnet WIZ850io is item EXT1,
catalog code C134462. The PCBA supplier must source it and plug it into the
factory-installed J6/J7 sockets before shipment; the customer must not need to
install the module. Robotistan acceptance of this manual final assembly step is
not yet confirmed. Firmware flashing/key provisioning and first-article tests
are also outside PCB assembly.

The board is four-layer, 110 x 77 mm nominal, 1.6 mm thick. Confirm the exact
stackup, HASL lead-free finish, drill/slot capability, component sourcing and
assembly process with Robotistan before a production order. This package is for
review/quotation only. The separate bare-board package is
manufacturing/REVIEW-2026-11-10-DRAFT/.
