import sys
sys.path.append('/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew
from pathlib import Path
root=Path(__file__).resolve().parent
source=Path('/Users/furkan/Projeler/FAC-IO-HARDWARE/hardware/FAC-IO-Lite-V3.kicad_pcb')
b=pcbnew.LoadBoard(str(source))
placements={'U6':(182.5,111.0,180),'J7':(194.0,109.0,0),'C32':(193.0,140.0,0),'C33':(199.0,140.0,0),'R28':(190.0,146.5,0)}
for ref,(x,y,angle) in placements.items():
 fp=next(fp for fp in b.GetFootprints() if fp.GetReference()==ref)
 fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)))
 fp.SetOrientationDegrees(angle)
removed=0
for item in list(b.GetTracks()):
 b.Remove(item);removed+=1
stem='FAC-IO-Lite-V3'
for ext in ['kicad_sch','kicad_pro','kicad_dru']:
 (root/f'{stem}.{ext}').write_bytes((source.parent/f'{stem}.{ext}').read_bytes())
pcbnew.SaveBoard(str(root/f'{stem}.kicad_pcb'),b)
print(f'created trackless candidate; moved {len(placements)} footprints; removed {removed} tracks/vias')
