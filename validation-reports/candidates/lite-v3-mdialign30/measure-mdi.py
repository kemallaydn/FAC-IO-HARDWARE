import sys,math
sys.path.append('/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew
from pathlib import Path
b=pcbnew.LoadBoard(str(Path(__file__).resolve().parent/'routed.kicad_pcb'))
for name in ['ETH_TXP','ETH_TXN','ETH_RXP_PHY','ETH_RXN_PHY','ETH_RXP_CABLE','ETH_RXN_CABLE']:
 n=b.FindNet('/'+name);ln=0;vias=0
 for t in b.GetTracks():
  if t.GetNetCode()==n.GetNetCode():
   if t.Type()==pcbnew.PCB_VIA_T:vias+=1
   else:ln+=math.hypot(pcbnew.ToMM(t.GetEndX()-t.GetStartX()),pcbnew.ToMM(t.GetEndY()-t.GetStartY()))
 print(name,f'{ln:.2f} mm',f'{vias} vias')
