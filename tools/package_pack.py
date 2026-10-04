from pathlib import Path
import json
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parents[1]
pack=root/'kh2-ap-poptracker'
(root/'dist').mkdir(exist_ok=True)
version=json.loads((pack/'manifest.json').read_text(encoding='utf-8'))['package_version']
target=root/'dist'/f'kh2-ap-poptracker-{version}.zip'
with ZipFile(target,'w',ZIP_DEFLATED) as archive:
    for file in sorted(pack.rglob('*')):
        if file.is_file(): archive.write(file,file.relative_to(pack).as_posix())
print(target)
