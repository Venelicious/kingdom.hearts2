"""Copy exact item matches, unchanged, from a local Red-Buddha/KH2Tracker clone."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]).resolve()
pack=root/'kh2-ap-poptracker'
mapping={f"Secret Ansem's Report {i}":f'Old/ansem_report{i}.png' for i in range(1,14)}
for name,filename in {'Proof of Connection':'proof_of_connection','Proof of Nonexistence':'proof_of_nonexistence','Proof of Peace':'proof_of_peace','Promise Charm':'promise_charm','Torn Page':'torn_page','Valor Form':'valor','Wisdom Form':'wisdom','Limit Form':'limit','Master Form':'master','Final Form':'final','Genie':'genie','Peter Pan':'peter_pan','Stitch':'stitch','Chicken Little':'chicken_little',**{n+' Element':n.lower() for n in ['Fire','Blizzard','Thunder','Cure','Magnet','Reflect']}}.items():
    mapping[name]=f'Old/{filename}.png'
for name,filename in {'High Jump':'jump','Quick Run':'quick','Aerial Dodge':'aerial','Glide':'glide','Dodge Roll':'dodge'}.items():
    mapping[name]=f'GrowthAbilities/{filename}.png'
mapping.update({'Once More':'Simple/once_more.png','Second Chance':'Simple/second_chance.png'})
catalog=json.loads((pack/'data/catalog.json').read_text(encoding='utf-8'))
assert set(mapping)<=set(catalog['items'])
commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD']).decode().strip()
records={}
for name,path in mapping.items():
    sourcefile=source/'KhTracker/Images'/path
    dest=pack/'images/kh2tracker'/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(sourcefile,dest)
    records[name]={'img':dest.relative_to(pack).as_posix(),'source_path':'KhTracker/Images/'+path,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
shutil.copyfile(source/'LICENSE',pack/'LICENSE-KH2Tracker.txt')
(pack/'data/tracker-assets.json').write_text(json.dumps({'source':'https://github.com/Red-Buddha/KH2Tracker','commit':commit,'credits':'README credits Televo for icons not taken directly from the game; per-file authorship is unspecified.','items':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Copied {len(records)} unchanged icons at source commit {commit}')
