"""Rebuild KH2 pack from pinned AP 0.6.7 data without importing the AP runtime."""
import ast
import collections
import hashlib
import json
from pathlib import Path
import types
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'sources/kh2'
PACK = ROOT / 'kh2-ap-poptracker'
ENV = {}

def evaluate(node):
    if isinstance(node, ast.Constant): return node.value
    if isinstance(node, ast.Name): return ENV[node.id]
    if isinstance(node, ast.Attribute): return getattr(evaluate(node.value), node.attr)
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return [evaluate(x) for x in node.elts]
    if isinstance(node, ast.Dict):
        result = {}
        for k,v in zip(node.keys,node.values):
            if k is None: result.update(evaluate(v))
            else: result[evaluate(k)] = evaluate(v)
        return result
    if isinstance(node, ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('ItemData','LocationData'):
        return [evaluate(x) for x in node.args]
    raise ValueError(ast.dump(node)[:100])

def load_assignments(path):
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if isinstance(node, (ast.Assign,ast.AnnAssign)):
            name = node.targets[0].id if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) else node.target.id if isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Name) else None
            if name and node.value is not None:
                try: ENV[name] = evaluate(node.value)
                except (ValueError,KeyError,AttributeError): pass

for module in ('ItemName','LocationName','RegionName'):
    values = {}
    for node in ast.parse((SRC/'Names'/(module+'.py')).read_text(encoding='utf-8')).body:
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name):
            values[node.targets[0].id] = ast.literal_eval(node.value)
    ENV[module] = types.SimpleNamespace(**values)
load_assignments(SRC/'Items.py')
load_assignments(SRC/'Regions.py')
load_assignments(SRC/'Locations.py')
items = ENV['item_dictionary_table']
locations = ENV['all_locations']
regions = ENV['KH2REGIONS']
for directory in ('items','locations','maps','layouts','scripts','images/items','images/maps','data'):
    (PACK/directory).mkdir(parents=True,exist_ok=True)

def write(path,value):
    (PACK/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def lua(value):
    if isinstance(value,dict): return '{'+','.join('['+lua(k)+']='+lua(v) for k,v in value.items())+'}'
    if isinstance(value,list): return '{'+','.join(lua(x) for x in value)+'}'
    if isinstance(value,bool): return 'true' if value else 'false'
    if isinstance(value,(int,float)): return str(value)
    return json.dumps(value,ensure_ascii=False)

FONT = Path('C:/Windows/Fonts/segoeui.ttf')
def font(size): return ImageFont.truetype(str(FONT),size)
PALETTE = ['#71d4ef','#e7b866','#ad94ef','#79d7b1','#e590ad','#a4c7ee']

item_codes = {name:'i_'+str(i) for i,name in enumerate(items)}
item_ids = {0x130000+i:item_codes[name] for i,name in enumerate(items)}
categories = collections.OrderedDict()
item_json=[]
for name, data in items.items():
    table = next(k for k,v in ENV.items() if k.endswith('_Table') and isinstance(v,dict) and name in v and k!='Events_Table')
    categories.setdefault(table,[]).append(item_codes[name])
    color=PALETTE[list(categories).index(table)%len(PALETTE)]
    image=Image.new('RGBA',(64,64),'#111a2b'); d=ImageDraw.Draw(image)
    d.rounded_rectangle((3,3,60,60),radius=12,fill='#1e2d43',outline=color,width=2)
    # Original category symbols; never copied game artwork.
    cx,cy=32,22
    if table in ('Keyblade_Table','Staffs_Table','Shields_Table','Progression_Table'):
        d.line((17,36,43,10),fill=color,width=5); d.ellipse((36,5,51,20),outline=color,width=3); d.line((18,26,26,34),fill=color,width=4)
    elif table in ('Magic_Table','Forms_Table','Summon_Table','Movement_Table'):
        d.polygon([(32,5),(38,17),(52,22),(38,27),(32,39),(26,27),(12,22),(26,17)],fill=color)
    elif table=='Reports_Table':
        d.rectangle((20,8,44,37),outline=color,width=3)
        for y in (16,23,30): d.line((25,y,39,y),fill=color,width=2)
    else:
        d.polygon([(32,7),(48,22),(32,37),(16,22)],outline=color,width=3)
    label=''.join(x[0] for x in name.replace("'",'').split())[:5].upper()
    d.text((32,48),label,font=font(11),anchor='mm',fill='white')
    image.save(PACK/'images/items'/f'{item_codes[name]}.png')
    item_json.append({'name':name,'type':'consumable','codes':item_codes[name],'img':f'images/items/{item_codes[name]}.png','min_quantity':0,'max_quantity':0,'initial_quantity':0})
asset_file=PACK/'data/tracker-assets.json'
assets=json.loads(asset_file.read_text(encoding='utf-8')) if asset_file.exists() else {'items':{}}
game_asset_file=PACK/'data/game-assets.json'
game_assets=json.loads(game_asset_file.read_text(encoding='utf-8')) if game_asset_file.exists() else {'items':{}}
combined_assets={**assets['items'],**game_assets['items']}
menu_asset_file=PACK/'data/menu-assets.json'
menu_assets=json.loads(menu_asset_file.read_text(encoding='utf-8')) if menu_asset_file.exists() else {'items':{}}
text_assets={}
for name,label in {'Max HP Up':'HP ↑','Max MP Up':'MP ↑'}.items():
    image=Image.new('RGBA',(64,64),(0,0,0,0))
    draw=ImageDraw.Draw(image)
    draw.text((32,32),label,font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',24),anchor='mm',fill='white',stroke_width=1,stroke_fill='#101010')
    path='images/items/'+item_codes[name]+'.png'
    image.save(PACK/path)
    text_assets[name]={'img':path,'label':label,'kind':'recreated_text','sha256':hashlib.sha256((PACK/path).read_bytes()).hexdigest(),'source':'User-confirmed in-game HP/MP up text convention; newly rendered typography, not extracted artwork'}
write('data/text-assets.json',{'items':text_assets})
display_assets={**text_assets,**menu_assets['items'],**combined_assets}
for item in item_json:
    if item['name'] in display_assets:
        item['img']=display_assets[item['name']]['img']
write('items/items.json',item_json)
missing=[item['name'] for item in item_json if item['name'] not in combined_assets]
write('data/missing-item-assets.json',missing)
report=['# Fehlende individuelle Item-Assets','',f"{len(combined_assets)} von {len(items)} Itemtypen besitzen ein zugeordnetes Icon: {len(assets['items'])} aus Red-Buddha/KH2Tracker, {len(game_assets['items'])} zusätzlich aus der lokalen KH2-Extraktion.",f"{len(menu_assets['items'])} weitere Itemtypen verwenden originale, gemeinsam genutzte KH2-Menü-/Kategorie-Icons. Max HP Up und Max MP Up verwenden neu gerenderte Textsymbole HP ↑ und MP ↑. Es verbleiben keine generischen Platzhalter.",f'{len(missing)} Itemtypen besitzen kein individuelles Originalbild; sie sind unten vollständig aufgeführt. Kategorie- und Textsymbole werden separat gekennzeichnet.','',
        'Es wurden nur inhaltlich passende Icons zugeordnet. Welt-, Boss- und generische Kategorie-Icons zählen nicht als eigene Itemgrafik.','']
report += ['Die verbliebenen Fähigkeiten besitzen keine eigene Item-Bildzuordnung. Anti Form und Pureblood verweisen in der Spieltabelle auf Bild 0. Disney Castle Key, Unknown Disk, Lucky Emblem, Bounty sowie sechs Stat-/Slot-Upgrades verwenden AP- bzw. Dummy-Slots; deren ursprüngliche Grafiken wären irreführend.','']
for category,codes in categories.items():
    names=[name for name in missing if item_codes[name] in codes]
    if names:
        report += ['## '+category.replace('_Table','')+f' ({len(names)})','']
        report += ['- '+name+(' — Kategorie: '+menu_assets['items'][name]['category']+f" (Icon {menu_assets['items'][name]['icon_id']})" if name in menu_assets['items'] else ' — Textsymbol: '+text_assets[name]['label']) for name in names]
        report += ['']
(PACK/'MISSING-ASSETS.md').write_text('\n'.join(report),encoding='utf-8')

# Group regions by their dominant original location table, retaining exact AP names.
labels={'LoD_Checks':'Land of Dragons','AG_Checks':'Agrabah','DC_Checks':'Disney Castle & Timeless River','HundredAcre_Checks':'100 Acre Wood','Oc_Checks':'Olympus Coliseum','BC_Checks':"Beast's Castle",'SP_Checks':'Space Paranoids','PR_Checks':'Port Royal','HT_Checks':'Halloween Town','HB_Checks':'Hollow Bastion & CoR','PL_Checks':'Pride Lands','STT_Checks':'Simulated Twilight Town','TT_Checks':'Twilight Town','TWTNW_Checks':'The World That Never Was','SoraLevels':'Sora Levels','Form_Checks':'Drive Forms','GoA_Checks':'Garden of Assemblage','Keyblade_Slots':'Weapon Slots','Donald_Checks':'Donald','Goofy_Checks':'Goofy','Atlantica_Checks':'Atlantica','Summon_Checks':'Summons'}
owner={}
for table in labels:
    for name in ENV[table]: owner.setdefault(name,table)
groups=collections.OrderedDict((k,[]) for k in labels)
covered=set()
for region,names in regions.items():
    valid=[n for n in names if n in locations and n not in covered]
    if not valid: continue
    category=collections.Counter(owner[n] for n in valid).most_common(1)[0][0]
    groups[category].append((region,valid)); covered.update(valid)
for table in labels:
    rest=[n for n in locations if n not in covered and owner[n]==table]
    if rest: groups[table].append((labels[table]+' / Other',rest)); covered.update(rest)
assert covered==set(locations)
groups={k:v for k,v in groups.items() if v}

maps=[]; nodes=[]; mapping={}; lookup={}; tabs=[]; region_meta={}
world_image=Image.new('RGB',(1200,900),'#0d1524'); wd=ImageDraw.Draw(world_image)
wd.text((42,24),'KINGDOM HEARTS II',font=font(34),fill='#eff5ff')
wd.text((44,74),'ARCHIPELAGO  /  WORLD ATLAS',font=font(17),fill='#71d4ef')
wd.text((44,855),'Schematic check atlas  |  Blue: access requires manual verification  |  Select a world tab for details',font=font(15),fill='#a7b6ce')
for gi,(category,entries) in enumerate(groups.items()):
    mapname='map_'+category.lower(); title=labels[category]; color=PALETTE[gi%len(PALETTE)]
    ox=55+(gi%4)*290; oy=150+(gi//4)*115
    wd.rounded_rectangle((ox-12,oy-20,ox+260,oy+77),radius=14,fill='#1b293d',outline=color,width=2)
    wd.text((ox+25,oy),title,font=font(15),fill='white')
    wd.text((ox+25,oy+34),f'{sum(len(n) for _,n in entries)} checks / {len(entries)} regions',font=font(12),fill='#a7b6ce')
    h=max(620,160+((len(entries)+2)//3)*145)
    image=Image.new('RGB',(1200,h),'#0d1524'); d=ImageDraw.Draw(image)
    d.text((42,24),title.upper(),font=font(30),fill='white')
    d.text((44,72),'CHECK ATLAS  /  ORIGINAL AP REGION GROUPS',font=font(16),fill=color)
    world_node={'name':title,'map_locations':[{'map':'worlds','x':ox+7,'y':oy+8}],'children':[]}
    for ri,(region,names) in enumerate(entries):
        x=50+(ri%3)*390; y=150+(ri//3)*145
        d.rounded_rectangle((x-10,y-20,x+365,y+102),radius=14,fill='#1b293d',outline=color,width=2)
        # wrap long original region names
        words=region.split(); lines=['']
        for word in words:
            if len(lines[-1]+' '+word)>31: lines.append('')
            lines[-1]=(lines[-1]+' '+word).strip()
        for li,line in enumerate(lines): d.text((x+32,y+li*21),line,font=font(16),fill='white')
        d.text((x+32,y+67),f'{len(names)} checks  /  click marker',font=font(13),fill='#a7b6ce')
        rid=len(region_meta); region_meta[rid]={'name':region}
        sections=[]
        for name in names:
            lid=0x130000+list(locations).index(name)
            path='@'+title+'/'+region+'/'+name
            mapping[lid]=path; lookup[name]=path
            sections.append({'name':name,'item_count':1,'clear_as_group':False,'visibility_rules':[f'$enabled|{lid}'],'access_rules':[f'^$access|{rid}']})
        world_node['children'].append({'name':region,'map_locations':[{'map':mapname,'x':x+8,'y':y+9}],'sections':sections})
    nodes.append(world_node)
    image.save(PACK/'images/maps'/f'{mapname}.png')
    maps.append({'name':mapname,'img':f'images/maps/{mapname}.png','location_size':18,'location_border_thickness':2})
    tabs.append({'title':title,'content':{'type':'map','maps':[mapname]}})
world_image.save(PACK/'images/maps/worlds.png')
maps.insert(0,{'name':'worlds','img':'images/maps/worlds.png','location_size':18,'location_border_thickness':2})
write('maps/maps.json',maps); write('locations/locations.json',nodes)
tabs.insert(0,{'title':'Worlds','content':{'type':'map','maps':['worlds']}})
item_tabs=[]
for cat,codes in categories.items():
    item_tabs.append({'title':cat.replace('_Table','').replace('Usefull','Stats'),'content':{'type':'itemgrid','item_size':40,'rows':[codes[i:i+10] for i in range(0,len(codes),10)]}})
layout={'type':'dock','content':[{'type':'tabbed','dock':'left','width':435,'tabs':item_tabs},{'type':'tabbed','tabs':tabs}]}
write('layouts/tracker.json',{'tracker_default':layout,'tracker_broadcast':layout})
write('manifest.json',{'name':'Kingdom Hearts II — Archipelago Check Atlas','game_name':'Kingdom Hearts 2','package_uid':'dsatool-kh2-ap-atlas','package_version':'0.1.4','author':'DSATool / Codex','platform':'pc','min_poptracker_version':'0.32.0','variants':{'standard':{'display_name':'World Atlas + AP Auto-Tracking','flags':['ap']}}})
write('settings.json',{'smooth_scaling':True,'smooth_map_scaling':True})
write('data/catalog.json',{'source':'Archipelago 0.6.7 / KH2 World 2.0.0','items':{n:0x130000+i for i,n in enumerate(items)},'locations':{n:0x130000+i for i,n in enumerate(locations)},'regions':region_meta})
script='ITEM_IDS='+lua(item_ids)+'\nITEM_NAMES='+lua(item_codes)+'\nLOCATION_IDS='+lua(mapping)+'\nLOCATION_NAMES='+lua(lookup)+'\nREGIONS='+lua(region_meta)+'\n'
(PACK/'scripts/catalog.lua').write_text(script,encoding='utf-8')
write('data/source-lock.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SRC.rglob('*.py'))})
print(f'Generated {len(items)} items, {len(locations)} locations, {len(region_meta)} regions, {len(maps)} maps')
