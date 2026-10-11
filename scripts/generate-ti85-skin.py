#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create an original TI-85 keypad skin. Regeneration needs the Cairo library.
The generated SVG is editable; the .skn embeds the same drawing as PNG.
"""
import ctypes as C
import ctypes.util
from pathlib import Path
import struct
import tempfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
# Skin rectangle indices follow TilEm's existing hardware scan map.
CODES = [53,52,51,50,49,54,55,56,2,3,4,1,48,40,32,47,39,31,23,15,
         46,38,30,22,14,45,37,29,21,13,44,36,28,20,12,43,35,27,19,11,
         42,34,26,18,10,41,33,25,17,9]
NAMES = ['F1','F2','F3','F4','F5','2nd','EXIT','MORE','LEFT','RIGHT',
         'UP','DOWN','ALPHA','x-VAR','DEL','GRAPH','STAT','PRGM','CUSTOM','CLEAR',
         'LOG','SIN','COS','TAN','^','LN','EE','(',')','/',
         'x²','7','8','9','×',',','4','5','6','−','STO','1','2','3','+',
         'ON','0','.','(−)','ENTER']
libname = ctypes.util.find_library('cairo') or '/opt/homebrew/lib/libcairo.2.dylib'
lib = C.CDLL(libname)
def function(name, args, result=None):
    fn = getattr(lib, 'cairo_' + name)
    fn.argtypes, fn.restype = args, result
    return fn
p, d, i = C.c_void_p, C.c_double, C.c_int
surface = function('image_surface_create', [i,i,i], p)(0,400,800)
ctx = function('create', [p], p)(surface)
color = function('set_source_rgb',[p,d,d,d])
rect = function('rectangle',[p,d,d,d,d])
fill = function('fill',[p])
font = function('select_font_face',[p,C.c_char_p,i,i])
size = function('set_font_size',[p,d])
move = function('move_to',[p,d,d])
show = function('show_text',[p,C.c_char_p])
class Extents(C.Structure):
    _fields_ = [(name,d) for name in ('x_bearing','y_bearing','width','height','x_advance','y_advance')]
measure = function('text_extents',[p,C.c_char_p,C.POINTER(Extents)])
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="400" height="800" viewBox="0 0 400 800">', '<!-- SPDX-License-Identifier: GPL-3.0-or-later; original TilEm Portable drawing -->']
def box(x,y,w,h,hexcolor):
    rgb = tuple(int(hexcolor[j:j+2],16)/255 for j in (1,3,5))
    color(ctx,*rgb); rect(ctx,x,y,w,h); fill(ctx)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hexcolor}"/>')
def text(x,y,value,points,hexcolor='#ffffff'):
    rgb = tuple(int(hexcolor[j:j+2],16)/255 for j in (1,3,5))
    font(ctx,b'Sans',0,1); size(ctx,points); ext=Extents()
    measure(ctx,value.encode(),C.byref(ext)); color(ctx,*rgb)
    move(ctx,x-ext.width/2-ext.x_bearing,y); show(ctx,value.encode())
    svg.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="{points}" fill="{hexcolor}">{escape(value)}</text>')
box(0,0,400,800,'#232b36')
text(200,35,'TilEm · TI-85',22)
box(48,52,304,160,'#151c24')
box(72,68,256,128,'#cad5a7')
text(200,237,'SCIENTIFIC GRAPHING CALCULATOR',10,'#a3afbf')
rectangles=[]
for index,name in enumerate(NAMES):
    row,col=divmod(index,5)
    x,y=18+col*75,258+row*52
    rectangles.append((x,y,x+64,y+40))
    box(x,y,64,40,'#365b88' if index < 5 or name in ('2nd','ALPHA') else '#495260')
    text(x+32,y+26,name,12 if len(name)>4 else 16)
text(200,791,'Right-click for files, settings and debugger',10,'#a3afbf')
svg.append('</svg>')
folder=ROOT/'data/skins'
(folder/'ti85.svg').write_text('\n'.join(svg)+'\n')
write_png=function('surface_write_to_png',[p,C.c_char_p],i)
with tempfile.TemporaryDirectory() as temporary:
    png=Path(temporary)/'ti85.png'
    if write_png(surface,str(png).encode()): raise RuntimeError('Cairo PNG generation failed')
    u32=lambda n:struct.pack('<I',n)
    string=lambda v:u32(len(v))+v
    name=b'TilEm Portable TI-85'; author=b'TilEm Portable contributors'
    header=(b'TilEm v2.00'.ljust(16,b'\0')+u32(0xfeedbabe)+u32(0)
            +string(name)+string(author)+u32(2)+u32(0xcad5a7)+u32(0x152115)
            +b'TI-85'.ljust(8,b'\0')+struct.pack('<4I',72,68,328,196)+u32(50)
            +b''.join(struct.pack('<4I',*r) for r in rectangles))
    header=header[:20]+u32(len(header))+header[24:]
    (folder/'ti85.skn').write_bytes(header+png.read_bytes())
function('destroy',[p])(ctx); function('surface_destroy',[p])(surface)
print(folder/'ti85.skn')
