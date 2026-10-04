"""Decode the original KH2 font icon atlas and apply explicit category fallbacks."""
from pathlib import Path
import hashlib
import json
import struct
import sys
from PIL import Image

root=Path(__file__).resolve().parents[1]
pack=root/'kh2-ap-poptracker'
openkh=Path(sys.argv[1]).resolve()
source=openkh/'data/kh2/msg/us/fontimage.bar'
raw=source.read_bytes()
assert raw[:3]==b'BAR'
payload=None
for i in range(struct.unpack_from('<I',raw,4)[0]):
    kind,index,name,offset,size=struct.unpack_from('<HH4sII',raw,16+i*16)
    if name.rstrip(b'\0')==b'icon': payload=raw[offset:offset+size]
assert payload is not None and len(payload)==256*160+256*4
pixels=payload[:256*160]; palette=payload[256*160:]
colors=[]
for i in range(256):
    # PS2 CLUT swaps bits 3 and 4; native alpha range is 0..128.
    j=(i&0xe7)|((i&8)<<1)|((i&16)>>1)
    r,g,b,a=palette[j*4:j*4+4]
    colors.append(bytes((r,g,b,min(a*2,255))))
atlas=Image.frombytes('RGBA',(256,160),b''.join(colors[i] for i in pixels))
directory=pack/'images/kh2menu'; directory.mkdir(parents=True,exist_ok=True)
labels={0:'Consumable (Equippable)',2:'Document / Key item',3:'Ability',4:'Keyblade',7:'Armor',17:'Accessory',25:'Form'}
icons={}
for icon_id,label in labels.items():
    x=(icon_id%10)*24; y=(icon_id//10)*24
    image=atlas.crop((x,y,x+24,y+24))
    assert image.getchannel('A').getbbox() is not None
    dest=directory/f'icon-{icon_id:02d}.png'; image.save(dest)
    icons[icon_id]={'img':dest.relative_to(pack).as_posix(),'label':label,'crop':[x,y,24,24],'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
missing=json.loads((pack/'data/missing-item-assets.json').read_text(encoding='utf-8'))
game=json.loads((pack/'data/game-assets.json').read_text(encoding='utf-8'))
mapping={}
explicit={'Disney Castle Key':2,'Unknown Disk':2,'Lucky Emblem':2,'Bounty':2,'Anti Form':25,'Pureblood':4,'Drive Gauge Up':25,'Armor Slot Up':7,'Accessory Slot Up':17,'Item Slot Up':0}
for name in missing:
    icon_id=explicit.get(name)
    if 'Ability namespace' in game['unresolved_reasons'].get(name,''): icon_id=3
    if icon_id is not None:
        mapping[name]={'icon_id':icon_id,'category':labels[icon_id],'img':icons[icon_id]['img'],'sha256':icons[icon_id]['sha256'],'kind':'shared_category','reason':'Original KH2 menu symbol used as category fallback; not an individual picture for this reward'}
assert len(mapping)==115
metadata={'source_path':'msg/us/fontimage.bar','source_sha256':hashlib.sha256(raw).hexdigest(),'dictionary':'https://openkh.dev/kh2/dictionary/icons.html','format_reference':'OpenKH FontContext (256x160 Indexed8), RawBitmap (PS2 CLUT/alpha), Constants (24x24), Kh2MessageRenderer (10 icons per row)','icons':icons,'items':mapping,'unmapped':['Max HP Up','Max MP Up']}
(pack/'data/menu-assets.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Extracted {len(icons)} original menu icons; applied to {len(mapping)} itemtypes; 2 remain without suitable category')
