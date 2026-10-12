#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create an original TI-85 keypad skin. Regeneration needs Cairo and Pango.
The generated SVG is editable; the .skn embeds the same drawing as PNG.
"""
import ctypes as C
import ctypes.util
import json
from pathlib import Path
import struct
import tempfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
# Skin rectangle indices follow TilEm's existing hardware scan map.
CODES = [53,52,51,50,49,54,55,56,2,3,4,1,48,40,32,47,39,31,23,15,
         46,38,30,22,14,45,37,29,21,13,44,36,28,20,12,43,35,27,19,11,
         42,34,26,18,10,41,33,25,17,9]
NAMES = ['F1','F2','F3','F4','F5','2nd','Exit','More','Left','Right',
         'Up','Down','Alpha','XVar','Del','Graph','Stat','Prgm','Custom','Clear',
         'Log','Sin','Cos','Tan','Power','Ln','EE','LParen','RParen','Div',
         'Square','7','8','9','Mul','Comma','4','5','6','Sub','Store','1','2','3','Add',
         'On','0','DecPnt','Chs','Enter']
# Drawing order is independent of the fixed skin-file key order above.
VISUAL_NAMES = NAMES[:5] + ['2nd','Exit','More','Left','Up',
                           'Alpha','XVar','Del','Down','Right'] + NAMES[15:]
ARROW_RECTS = {
    'Up': (294,310,338,342), 'Down': (294,370,338,402),
    'Left': (243,336,283,376), 'Right': (342,336,382,376),
}
LEGENDS = json.loads((ROOT/'server/ti85-keypad.json').read_text())
libname = ctypes.util.find_library('cairo') or '/opt/homebrew/lib/libcairo.2.dylib'
lib = C.CDLL(libname)
pango = C.CDLL(ctypes.util.find_library('pango-1.0') or '/opt/homebrew/lib/libpango-1.0.dylib')
pangocairo = C.CDLL(ctypes.util.find_library('pangocairo-1.0') or '/opt/homebrew/lib/libpangocairo-1.0.dylib')
gobject = C.CDLL(ctypes.util.find_library('gobject-2.0') or '/opt/homebrew/lib/libgobject-2.0.dylib')
def external(library, name, args, result=None):
    fn = getattr(library, name)
    fn.argtypes, fn.restype = args, result
    return fn
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
move = function('move_to',[p,d,d])
class Extents(C.Structure):
    _fields_ = [(name,i) for name in ('x','y','width','height')]
layout = external(pangocairo,'pango_cairo_create_layout',[p],p)(ctx)
font_description = external(pango,'pango_font_description_from_string',[C.c_char_p],p)(b'Sans Bold')
font_size = external(pango,'pango_font_description_set_absolute_size',[p,d])
layout_font = external(pango,'pango_layout_set_font_description',[p,p])
layout_text = external(pango,'pango_layout_set_text',[p,C.c_char_p,i])
measure = external(pango,'pango_layout_get_pixel_extents',[p,p,C.POINTER(Extents)])
baseline = external(pango,'pango_layout_get_baseline',[p],i)
show = external(pangocairo,'pango_cairo_show_layout',[p,p])
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="400" height="800" viewBox="0 0 400 800">', '<!-- SPDX-License-Identifier: GPL-3.0-or-later; original TilEm Portable drawing -->']
def box(x,y,w,h,hexcolor):
    rgb = tuple(int(hexcolor[j:j+2],16)/255 for j in (1,3,5))
    color(ctx,*rgb); rect(ctx,x,y,w,h); fill(ctx)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hexcolor}"/>')
def text(x,y,value,points,hexcolor='#ffffff',anchor='middle'):
    rgb = tuple(int(hexcolor[j:j+2],16)/255 for j in (1,3,5))
    font_size(font_description,points*1024); layout_font(layout,font_description)
    layout_text(layout,value.encode(),-1); ext=Extents()
    measure(layout,None,C.byref(ext)); color(ctx,*rgb)
    offset = {'start':0, 'middle':ext.width/2, 'end':ext.width}[anchor]
    move(ctx,x-offset-ext.x,y-baseline(layout)/1024); show(ctx,layout)
    svg.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="sans-serif" font-weight="bold" font-size="{points}" fill="{hexcolor}">{escape(value)}</text>')
box(0,0,400,800,'#232b36')
text(200,35,'TilEm · TI-85',22)
box(48,52,304,160,'#151c24')
box(72,68,256,128,'#cad5a7')
text(200,237,'GOLD: 2nd  ·  BLUE: ALPHA  ·  ␣: SPACE',10,'#a3afbf')
rectangles={}
for index,name in enumerate(VISUAL_NAMES):
    row,col=divmod(index,5)
    x,y=18+col*75,258+row*52
    bounds = ARROW_RECTS.get(name, (x,y,x+64,y+40))
    rectangles[name] = bounds
    x,y,right,bottom = bounds
    width,height = right-x,bottom-y
    legend = LEGENDS[name]
    primary = legend['primary']
    box(x,y,width,height,'#996b26' if name == '2nd' else '#365b88' if index < 5 or name == 'Alpha' else '#495260')
    text(x+width/2,y+height/2+6,primary,12 if len(primary)>4 else 16)
    if legend.get('second'):
        text(x,y-3,legend['second'],10.5,'#f4d47b',anchor='start')
    if legend.get('alpha'):
        text(x+width,y-3,legend['alpha'],12,'#87d7ed',anchor='end')
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
            +b''.join(struct.pack('<4I',*r) for r in (rectangles[key] for key in NAMES)))
    header=header[:20]+u32(len(header))+header[24:]
    (folder/'ti85.skn').write_bytes(header+png.read_bytes())
external(pango,'pango_font_description_free',[p])(font_description)
external(gobject,'g_object_unref',[p])(layout)
function('destroy',[p])(ctx); function('surface_destroy',[p])(surface)
print(folder/'ti85.skn')
