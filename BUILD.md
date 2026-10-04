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
