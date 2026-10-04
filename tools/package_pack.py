from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parents[1]
pack=root/'kh2-ap-poptracker'
(root/'dist').mkdir(exist_ok=True)
target=root/'dist/kh2-ap-poptracker-0.1.0.zip'
with ZipFile(target,'w',ZIP_DEFLATED) as archive:
    for file in sorted(pack.rglob('*')):
        if file.is_file(): archive.write(file,file.relative_to(pack).as_posix())
print(target)
