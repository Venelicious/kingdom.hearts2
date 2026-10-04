"""Validate official schemas, resources, AP IDs and real Lua callback behavior."""
import json
import hashlib
from pathlib import Path
import jsonschema
from lupa import LuaRuntime
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'kh2-ap-poptracker'
for kind,path in [('manifest','manifest.json'),('settings','settings.json'),('items','items/items.json'),('locations','locations/locations.json'),('maps','maps/maps.json'),('layouts','layouts/tracker.json')]:
    schema_dir=ROOT/'tools/schema/packs'
    if not schema_dir.exists(): schema_dir=ROOT/'reference-poptracker/schema/packs'
    schema=json.loads((schema_dir/f'{kind}.json').read_text())
    jsonschema.validate(json.loads((PACK/path).read_text(encoding='utf-8')),schema)
    print('Schema OK:',kind)
items=json.loads((PACK/'items/items.json').read_text(encoding='utf-8'))
maps=json.loads((PACK/'maps/maps.json').read_text(encoding='utf-8'))
nodes=json.loads((PACK/'locations/locations.json').read_text(encoding='utf-8'))
catalog=json.loads((PACK/'data/catalog.json').read_text(encoding='utf-8'))
assets=json.loads((PACK/'data/tracker-assets.json').read_text(encoding='utf-8')) if (PACK/'data/tracker-assets.json').exists() else {'items':{}}
game_assets=json.loads((PACK/'data/game-assets.json').read_text(encoding='utf-8')) if (PACK/'data/game-assets.json').exists() else {'items':{}}
combined_assets={**assets['items'],**game_assets['items']}
menu_assets=json.loads((PACK/'data/menu-assets.json').read_text(encoding='utf-8')) if (PACK/'data/menu-assets.json').exists() else {'items':{}}
display_assets={**menu_assets['items'],**combined_assets}
assert not set(menu_assets['items'])&set(combined_assets)
for name,record in display_assets.items():
    assert hashlib.sha256((PACK/record['img']).read_bytes()).hexdigest()==record['sha256']
    assert next(item for item in items if item['name']==name)['img']==record['img']
missing=json.loads((PACK/'data/missing-item-assets.json').read_text(encoding='utf-8'))
assert set(missing)==set(catalog['items'])-set(combined_assets)
for name,record in game_assets['items'].items():
    assert record['game_item_type']!=22 and record['picture_id']>0
    with Image.open(PACK/record['img']) as im:
        alpha=im.convert('RGBA').getchannel('A')
        assert alpha.getbbox() is not None and alpha.getextrema()[0]==0
if game_assets['items']:
    for name,game_id in {'Potion':1,'Hi-Potion':2,'Ether':3,'Power Boost':276,'Magic Boost':277,'Defense Boost':278,'AP Boost':279}.items():
        assert game_assets['items'][name]['game_item_id']==game_id
print(f"Assets OK: {len(combined_assets)} mapped icons, {len(missing)} explicit missing entries; original-ID overrides and alpha checked")
if menu_assets['items']:
    assert len(menu_assets['items'])==115
    assert set(catalog['items'])-set(display_assets)=={'Max HP Up','Max MP Up'}
    for name,record in menu_assets['items'].items():
        assert record['kind']=='shared_category'
        with Image.open(PACK/record['img']) as im:
            assert im.size==(24,24) and im.mode=='RGBA' and im.getchannel('A').getbbox() is not None
    assert menu_assets['items']['Scan']['icon_id']==3
    assert menu_assets['items']['Anti Form']['icon_id']==25
    assert menu_assets['items']['Pureblood']['icon_id']==4
    assert menu_assets['items']['Armor Slot Up']['icon_id']==7
    assert menu_assets['items']['Accessory Slot Up']['icon_id']==17
    print('Menu icons OK: 7 original 24x24 symbols, 115 category fallbacks, 2 placeholders; individual images preserved')
for obj in items+maps:
    with Image.open(PACK/obj['img']) as im: im.verify()
dimensions={m['name']:Image.open(PACK/m['img']).size for m in maps}
paths=set()
for world in nodes:
    for region in world['children']:
        for marker in region['map_locations']:
            w,h=dimensions[marker['map']]; assert 0<=marker['x']<w and 0<=marker['y']<h
        for section in region['sections']:
            path='@'+world['name']+'/'+region['name']+'/'+section['name']
            assert path not in paths; paths.add(path)
assert len(paths)==len(catalog['locations'])==724
assert len(items)==len(catalog['items'])==293
runtime=LuaRuntime(unpack_returned_tuples=True)
runtime.execute('''
objects = {}; handlers = {}
Tracker = {BulkUpdate=false}
function Tracker:FindObjectForCode(code) return objects[code] end
Archipelago = {MissingLocations={},CheckedLocations={}}
function Archipelago:AddClearHandler(name,fn) handlers.clear=fn end
function Archipelago:AddItemHandler(name,fn) handlers.item=fn end
function Archipelago:AddLocationHandler(name,fn) handlers.location=fn end
AccessibilityLevel={Normal=5,Inspect=3}
''')
for name in ('catalog','logic'):
    runtime.execute((PACK/'scripts'/f'{name}.lua').read_text(encoding='utf-8'))
runtime.execute('''
for _,code in pairs(ITEM_IDS) do objects[code]={AcquiredCount=17} end
for _,path in pairs(LOCATION_IDS) do objects[path]={ChestCount=1,AvailableChestCount=0} end
''')
runtime.execute((PACK/'scripts/archipelago.lua').read_text(encoding='utf-8'))
runtime.execute('''
local first=0x130000
Archipelago.MissingLocations={first+1}
Archipelago.CheckedLocations={first}
handlers.clear({})
assert(not Tracker.BulkUpdate)
assert(objects[ITEM_IDS[first]].AcquiredCount==0)
assert(objects[LOCATION_IDS[first]].AvailableChestCount==0)
assert(objects[LOCATION_IDS[first+1]].AvailableChestCount==1)
assert(enabled(tostring(first)))
assert(enabled(tostring(first+1)))
assert(not enabled(tostring(first+2)))
handlers.item(0,first,'',2)
handlers.item(0,first,'',2)
handlers.item(1,first,'',2)
assert(objects[ITEM_IDS[first]].AcquiredCount==2)
handlers.item(2,9999999,'unknown',2)
handlers.location(first+1,'')
handlers.location(first+1,'')
assert(objects[LOCATION_IDS[first+1]].AvailableChestCount==0)
handlers.location(9999999,'unknown')
handlers.clear({})
handlers.item(0,first,'',2)
assert(objects[ITEM_IDS[first]].AcquiredCount==1)
Archipelago.MissingLocations=nil; Archipelago.CheckedLocations=nil
handlers.clear({})
assert(enabled(tostring(first+2)))
for id,data in pairs(REGIONS) do
  assert(access(tostring(id)) == (data.name=='Garden Of Assemblage' and AccessibilityLevel.Normal or AccessibilityLevel.Inspect))
end
''')
print('PASS: all schemas, PNGs, paths, coverage, seed filtering, duplicate packets, reconnect replay, unknown IDs, offline fallback and access states')
