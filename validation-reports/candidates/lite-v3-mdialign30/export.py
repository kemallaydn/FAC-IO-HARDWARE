import sys
sys.path.append('/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew
from pathlib import Path
root=Path(__file__).resolve().parent
board=pcbnew.LoadBoard(str(root/'FAC-IO-Lite-V3.kicad_pcb'))
print('DSN export:',pcbnew.ExportSpecctraDSN(board,str(root/'FAC-IO-Lite-V3.dsn')))
