# Kingdom Hearts II – Archipelago Check Atlas v0.1.0

PopTracker-Pack für **Kingdom Hearts 2 / KH2 Final Mix**, passend zu der auf
ap.dsatool.org dokumentierten **Archipelago Core 0.6.7 / World 2.0.0**.

## Installation

1. ZIP in das PopTracker-Fenster ziehen oder in einen PopTracker-`packs`-Ordner legen.
2. Pack laden und „World Atlas + AP Auto-Tracking“ auswählen.
3. Für manuelles Tracking Items anklicken; Rechtsklick reduziert den Zähler.
   Kartenmarker öffnen die einzelnen Checks der ursprünglichen AP-Bereiche.
4. Für Auto-Tracking über die AP-Schaltfläche mit Server und KH2-Slot verbinden.
   Die Serveradresse aus der aktuellen Raumansicht verwenden. Das DSATool-Portal
   verlangt WSS/TLS; die verwendete PopTracker-Version muss mit der Adresse und
   TLS-Verbindung kompatibel sein. Die Verbindung zum Portal wurde hier nicht live getestet.

## Enthalten

- 293 AP-Itemtypen mit eigenen PNG-Symbolen und unbegrenzten Zählern.
- Alle 724 adressierbaren AP-Locations der gepinnten World.
- 102 Bereiche aus den ursprünglichen AP-Regionsdaten, ergänzt um nicht dort
  zugeordnete adressierbare Checks.
- 21 PNG-Karten: Weltübersicht und 20 Bereichsübersichten.
- AP-Inventar- und Check-Synchronisierung, Seed-Filter für nicht aktivierte Checks,
  Reset und Wiederaufbau nach Reconnect, Schutz vor doppelten Itemnachrichten.
- Offline-Tracking. Änderungen im Tracker senden keine Checks an den Server.

## Grenzen dieser Version

Dies ist ein **Check-Atlas mit Auto-Tracking**, keine vollständige Umsetzung der
KH2-Zugangslogik. Kampfanforderungen, Visit Locks, Form-/Summon-Level, LevelDepth,
Goal und Keyblade-Abilities werden nicht als Erreichbarkeitslogik ausgewertet.
Ungeprüfte Bereiche erscheinen deshalb blau (`Inspect`); die Startchecks im
Garden of Assemblage erscheinen grün. Blau ist hier eine Aufforderung zur manuellen
Prüfung und keine Aussage, dass der Bereich bereits im Spiel erreichbar ist.
Bei AP-Verbindung bestimmt die tatsächliche Checked-/Missing-Locations-Liste,
welche Checks angezeigt werden. Offline ist der vollständige Katalog sichtbar.

Die Karten sind **schematische Bereichsübersichten**, keine maßstabsgetreuen
Raumpläne. Die Symbole sind eigene Kategorie-Icons mit Namenskürzeln;
Original-Spielgrafiken und Screenshots sind nicht enthalten.

## Quellen und Rechte

- https://github.com/black-sliver/PopTracker – Packformat, Lua-API, JSON-Schemas.
- https://github.com/guigui0246/albw-ap-poptracker – Referenz für die Organisation
  eines AP-Packs. Kein Code oder Artwork daraus kopiert.
- https://github.com/ArchipelagoMW/Archipelago/tree/0.6.7/worlds/kh2 – Itemnamen,
  Locationnamen, Datenreihenfolge und Regionsgruppen (MIT; siehe LICENSE-AP.txt).
- https://ap.dsatool.org/games/Kingdom%20Hearts%202 – Portal-Version und Einrichtung.

Die AP-IDs stammen ausdrücklich aus der Dictionary-Reihenfolge der World und
sind keine Spielspeicheradressen. `data/source-lock.json` enthält SHA-256-Werte
der verwendeten Quelldateien. Andere World-Versionen müssen separat geprüft werden.
Eigener Lua-Code, Generator und eigene Grafiken: MIT; siehe LICENSE.txt.

## Validierung

Offizielle PopTracker-JSON-Schemas, PNG-Dateien, Map-Koordinaten und eindeutige
Checkpfade wurden geprüft. Lua-Callbacks wurden mit einem simulierten Tracker
auf Reset, Replay nach Reconnect, Duplikate, unbekannte IDs und Seed-Filter getestet.
Ein echter Multiworld-Spieltest ist damit noch nicht belegt.
