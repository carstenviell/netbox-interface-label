# Changelog

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.

Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [0.2.0] - 2026-07-31

### Neu
- Badge-Icon in der Geräte-Interface-Liste bei offenem Label-Vorschlag (Spalte muss einmalig über das Spalten-Zahnrad aktiviert werden)
- Banner auch auf der Kabel-Detailseite (`/dcim/cables/<pk>/`), zeigt Vorschläge für beide Seiten der Verbindung
- Neue Übersichtsseite `/plugins/interface-label/suggestions/` mit allen offenen Vorschlägen (Interface/PowerPort/PowerOutlet), filterbar nach Typ, mit Checkbox-Mehrfachauswahl und Massenübernahme (jedes ausgewählte Objekt erhält seinen individuellen Vorschlagswert)
- Menüeintrag "Label Suggestions" im NetBox-Hauptmenü

### Geändert
- Ein Vorschlag, der bereits dem aktuellen Label entspricht, wird nicht mehr als offene `LabelSuggestion` geführt (betrifft z. B. manuell schon korrekt benannte Interfaces oder erneutes Backfill)

## [0.1.0] - 2026-07-31

### Neu
- Automatische Label-Vorschlagsberechnung beim Verkabeln von Interfaces und Power-Ports (PowerPort/PowerOutlet), basierend auf dem tatsächlichen Kabelpfad – auch durch Patch-Panels (FrontPort/RearPort) hindurch
- `TEMP_`-Platzhalter-Vorschlag, solange die Verkabelung nur bis zu einem Patch-Panel-Port reicht; automatische Aktualisierung, sobald die Kette bis zu einem echten Ziel-Interface komplettiert wird
- Symmetrische Vorschläge auf beiden Seiten einer Verbindung
- Bestätigungs-Banner auf der Interface-/PowerPort-/PowerOutlet-Detailseite ("Übernehmen"/"Verwerfen") – kein automatisches Schreiben ins Label-Feld
- Sonderfall Kabel trennen: automatische `GETRENNT_`-Präfixierung eines vorhandenen Labels, ohne Bestätigung
- `backfill_interface_labels`-Management-Command für bereits bestehende Verkabelung
