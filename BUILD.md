# KH2 PopTracker-Pack bauen

Das fertige Pack liegt in `kh2-ap-poptracker`, das installierbare ZIP in `dist`.

Mit Python 3 und den Paketen Pillow, jsonschema, lupa:

```powershell
python tools/build_pack.py
python tools/validate_pack.py
python tools/package_pack.py
```

`sources/kh2` enthält die gepinnten Archipelago-0.6.7-Daten.
Der Generator liest Daten mit einem eingeschränkten AST-Auswerter; er importiert
und startet nicht den Archipelago-Server. Die Asset-Erstellung nutzt Segoe UI aus
dem Windows-Fonts-Ordner. Für andere Systeme muss der Fontpfad angepasst werden.
Die Validierung nutzt die mitgelieferten offiziellen Schemas in `tools/schema`.

Die README im Pack beschreibt Funktionsumfang und ausstehende Live-Validierung.
Das ALBW-Pack diente als Entwicklungsreferenz; Code und Assets daraus sind nicht enthalten.

Originale Itembilder erneut aus einer vorhandenen OpenKH-Extraktion exportieren:

```powershell
python tools/import_game_assets.py C:\Archipelago\openkh
python tools/import_menu_icons.py C:\Archipelago\openkh
python tools/build_pack.py
python tools/validate_pack.py
python tools/package_pack.py
```

Der Import liest `data/kh2/03system.bin` und `data/kh2/itempic` und verwendet das
vorhandene `Apps/OpenKh.Command.ImgTool.exe`. Es werden nur ausgewählte Itembilder
exportiert. Die Quelldateien der Installation werden nicht verändert.
Der Menü-Import liest msg/us/fontimage.bar direkt und dekodiert das 256×160-
Icon-Atlas nach OpenKH: 8-Bit-Palette, PS2-CLUT und Alpha, 24×24-Icons mit
zehn Spalten. Die Zuordnung trennt individuelle Bilder und gemeinsame Symbole.
