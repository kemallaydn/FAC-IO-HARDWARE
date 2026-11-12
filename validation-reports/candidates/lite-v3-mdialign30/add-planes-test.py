import sys
sys.path.append('/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew
from pathlib import Path
root=Path(__file__).resolve().parent
src=root/'routed.kicad_pcb';out=root/'routed-planes.kicad_pcb'
b=pcbnew.LoadBoard(str(src))
box=b.GetBoardEdgesBoundingBox(); left=box.GetLeft()+pcbnew.FromMM(1);right=box.GetRight()-pcbnew.FromMM(1);top=box.GetTop()+pcbnew.FromMM(1);bottom=box.GetBottom()-pcbnew.FromMM(1)
keep=(pcbnew.FromMM(189),pcbnew.FromMM(104),pcbnew.FromMM(208),pcbnew.FromMM(123))
def add_zone(netname,layer,name):
 z=pcbnew.ZONE(b);z.SetNet(b.FindNet(netname));z.SetLayer(layer);z.SetZoneName(name);z.SetLocalClearance(pcbnew.FromMM(.2));z.SetThermalReliefGap(pcbnew.FromMM(.25));z.SetThermalReliefSpokeWidth(pcbnew.FromMM(.25));z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if netname=='/3V3' else pcbnew.ZONE_CONNECTION_THERMAL)
 poly=z.Outline();poly.NewOutline()
 for x,y in [(left,top),(right,top),(right,bottom),(left,bottom)]:poly.Append(x,y)
 poly.NewHole(0)
 for x,y in [(keep[0],keep[1]),(keep[2],keep[1]),(keep[2],keep[3]),(keep[0],keep[3])]:poly.Append(x,y,0,0)
 b.Add(z);return z
add_zone('/3V3',pcbnew.F_Cu,'3V3_TOP')
add_zone('/GND',pcbnew.B_Cu,'GND_BOTTOM')
pcbnew.SaveBoard(str(out),b);print('created F.Cu 3V3 and B.Cu GND planes, with no-plane hole under J7 magnetics')
