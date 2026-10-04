"""Export missing, real KH2 item pictures from a local OpenKH extraction."""
import ast
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from PIL import Image

root=Path(__file__).resolve().parents[1]
pack=root/'kh2-ap-poptracker'
openkh=Path(sys.argv[1]).resolve()
data=openkh/'data/kh2'
tool=openkh/'Apps/OpenKh.Command.ImgTool.exe'
raw=(data/'03system.bin').read_bytes()
assert raw[:3]==b'BAR', 'Expected KH2 BAR container'
count=struct.unpack_from('<I',raw,4)[0]
item_table=None
for i in range(count):
    kind,index,name,offset,size=struct.unpack_from('<HH4sII',raw,16+i*16)
    if name.rstrip(b'\0')==b'item': item_table=raw[offset:offset+size]
assert item_table is not None
version,count=struct.unpack_from('<II',item_table)
assert version==6
game_items={}
for i in range(count):
    v=struct.unpack_from('<HBBBBHHHHHHHhBB',item_table,8+i*24)
    game_items[v[0]]={'type':v[1],'name_message_id':v[6]&0x7fff,'picture':v[12]}

names={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse((root/'sources/kh2/Names/ItemName.py').read_text(encoding='utf-8')).body if isinstance(n,ast.Assign)}
catalog=json.loads((pack/'data/catalog.json').read_text(encoding='utf-8'))
tracker=json.loads((pack/'data/tracker-assets.json').read_text(encoding='utf-8'))['items']
# AP repurposes map slots for these rewards. Use original game IDs, not AP's
# delivery/memory IDs. Stat-ups and custom/dummy rewards have no unique picture.
overrides={'Potion':1,'Hi-Potion':2,'Ether':3,'Elixir':4,'Megalixir':7,'Tent':131,'Drive Recovery':274,'High Drive Recovery':275,'Power Boost':276,'Magic Boost':277,'Defense Boost':278,'AP Boost':279}
exclude={'Disney Castle Key','Unknown Disk','Lucky Emblem','Bounty','Max HP Up','Max MP Up','Drive Gauge Up','Armor Slot Up','Accessory Slot Up','Item Slot Up'}
records={}; skipped={}
for node in ast.parse((root/'sources/kh2/Items.py').read_text(encoding='utf-8')).body:
    if not isinstance(node,ast.Assign) or not isinstance(node.targets[0],ast.Name) or not isinstance(node.value,ast.Dict): continue
    table=node.targets[0].id
    if not table.endswith('_Table') or table=='Events_Table': continue
    for key,call in zip(node.value.keys,node.value.values):
        if not isinstance(key,ast.Attribute) or not isinstance(call,ast.Call): continue
        name=names[key.attr]
        if name not in catalog['items'] or name in tracker or name in records: continue
        kwargs={k.arg:ast.literal_eval(k.value) for k in call.keywords}
        if kwargs.get('ability') or 'Ability_Table' in table or table=='Movement_Table':
            skipped[name]='Ability namespace: no separate itempic graphic'; continue
        if name in exclude:
            skipped[name]='AP custom reward or repurposed/dummy slot: no matching original item picture'; continue
        gameid=overrides.get(name,ast.literal_eval(call.args[1]) if len(call.args)>1 else kwargs.get('kh2id'))
        record=game_items.get(gameid)
        if not record or record['picture']<=0 or record['type']==22:
            skipped[name]='No usable individual item picture'; continue
        image_source=data/'itempic'/f"item-{record['picture']:03d}.imd"
        if not image_source.exists():
            skipped[name]='Referenced IMD not present'; continue
        dest=pack/'images/kh2game'/f"item-{record['picture']:03d}.png"
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():
            result=subprocess.run([str(tool),'unimd',str(image_source),'-o',str(dest)],capture_output=True,text=True)
            assert result.returncode==0 and dest.exists(), result.stdout+result.stderr
        with Image.open(dest) as image:
            image.verify()
        records[name]={'img':dest.relative_to(pack).as_posix(),'game_item_id':gameid,'game_item_type':record['type'],'picture_id':record['picture'],'name_message_id':record['name_message_id'],'source_path':image_source.relative_to(data).as_posix(),'source_sha256':hashlib.sha256(image_source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'mapping':'Original game ID override' if name in overrides else 'AP item ID -> original KH2 item table -> Picture'}
assert not set(records)&set(exclude)
payload={'source':'User-provided OpenKH extraction of KH2 Final Mix','openkh_release':(openkh/'openkh-release').read_text().strip(),'format':'Original IMD exported by OpenKh.Command.ImgTool unimd, preserving alpha','system_table_sha256':hashlib.sha256(raw).hexdigest(),'items':records,'unresolved_reasons':skipped}
(pack/'data/game-assets.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Exported and mapped {len(records)} additional item pictures; {len(skipped)} unresolved')
