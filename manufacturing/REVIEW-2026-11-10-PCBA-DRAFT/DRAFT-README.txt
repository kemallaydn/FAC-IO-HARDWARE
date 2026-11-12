FAC-IO-Mini V1 — PCBA review draft, not approved for ordering

This package carries the current-source 4-layer Gerber/Excellon set plus the
Robotistan BOM and Pick & Place draft so the assembler can assess feasibility.
Do not submit this as an approved assembly order yet. release/NOT-APPROVED.txt
is intentional; no independent review or supplier acceptance is recorded.
Robotistan upload files are bom/Robotistan-BOM.xlsx and
position/Robotistan-PickAndPlace.xlsx. The BOM follows Robotistan's supplied
template, groups the 56 PCB references by part, and includes the EXT1 WIZ850io
manual installation item. Pick & Place contains the 56 CAD placements only;
EXT1 is off-board in this CAD and has no verified main-board centroid.

CAD validation: KiCad 10.0.8 ERC has 0 errors/warnings; refilled DRC/parity has
0 violations, 0 unconnected pads and 0 parity issues. The 56-entry PCBA BOM
matches current schematic values, footprints and MPNs; Pick & Place matches
56/56 unique references, positions, rotations and top-side placement.

Open PCBA items: supplier codes for C1, C2, L1, SW1 and SW2 are blank. The
blocked passive codes were replaced consistently in schematic, PCB, BOM and upload
workbooks: C3/C8/C30=C91183, C9=C23631, C28/C29=C141125. LCSC catalog pages list
these equivalent-value/package parts in stock; Robotistan sourcing and assembly
acceptance remain unconfirmed. Do not substitute any further parts without engineering
review and CAD/BOM synchronization. Robotistan must resolve the five blank source
lines before order. WIZnet WIZ850io is item EXT1,
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
