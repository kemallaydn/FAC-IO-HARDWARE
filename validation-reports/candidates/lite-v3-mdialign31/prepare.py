import sys
sys.path.append('/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew
from pathlib import Path
root=Path(__file__).resolve().parent
source=Path('/Users/furkan/Projeler/FAC-IO-HARDWARE/hardware/FAC-IO-Lite-V3.kicad_pcb')
b=pcbnew.LoadBoard(str(source))
placements={'U6':(182.5,111.0,180),'J7':(195.5,109.0,0),'C32':(188.4,107.0,90),'C33':(188.4,111.0,90),'R28':(190.0,146.5,0),'R34':(191.5,114.0,0),'R35':(191.5,117.0,0),'C34':(193.5,120.5,0)}
for ref,(x,y,angle) in placements.items():
 fp=next(fp for fp in b.GetFootprints() if fp.GetReference()==ref);fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)));fp.SetOrientationDegrees(angle)
for item in list(b.GetTracks()):b.Remove(item)
stem='FAC-IO-Lite-V3'
for ext in ['kicad_sch','kicad_pro','kicad_dru']:(root/f'{stem}.{ext}').write_bytes((source.parent/f'{stem}.{ext}').read_bytes())
pcbnew.SaveBoard(str(root/f'{stem}.kicad_pcb'),b)
print(f'candidate placed; removed all source tracks ({len(b.GetTracks())} remaining)')
