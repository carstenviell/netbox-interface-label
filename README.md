# netbox-interface-label

NetBox-Plugin, das beim Verkabeln von Interfaces und Power-Ports (PowerPort/PowerOutlet) automatisch einen Label-Vorschlag berechnet – basierend auf dem tatsächlichen Kabelpfad, auch durch Patch-Panels (FrontPort/RearPort) hindurch.

## Verhalten

- Führt das Kabel zu einem echten Ziel-Interface/-Power-Port, setzt sich der Vorschlag aus dem konfigurierten Namensaufbau des fernen Endes zusammen (Standard: `{Devicename}_{Portname}`).
- Führt das Kabel (noch) nur zu einem Patch-Panel-Port, wird ein konfigurierbares Präfix vorangestellt (Standard: `TEMP_`) – wird automatisch aktualisiert, sobald die Verkabelung vervollständigt wird.
- Verbindungen entstehen **symmetrisch**: beide Enden bekommen einen Vorschlag.
- Vorschläge werden nie automatisch übernommen – der Nutzer bestätigt sie explizit (Banner auf der Detailseite, oder gesammelt auf der Übersichtsseite mit Massenübernahme).
- Wird ein Kabel direkt getrennt, bekommt ein vorhandenes Label automatisch ein konfigurierbares Präfix (Standard: `GETRENNT_`, einzige automatische Ausnahme).

## Einstellungen

Unter **Plugins → Settings** lässt sich pro Gerätekomponententyp (Interface/PowerPort/PowerOutlet) der Namensaufbau frei zusammenstellen: bis zu 5 Bausteine (Gerätename, Portname, Geräterolle, Standort, Lokation, Freitext) in beliebiger Reihenfolge, mit individuellem Trennzeichen zwischen den Bausteinen. Die `TEMP_`/`GETRENNT_`-Präfixe sind dort ebenfalls als Text änderbar.

Die Plugin-Oberfläche ist mehrsprachig (Englisch/Deutsch) und folgt automatisch der in NetBox eingestellten Sprache.

## Voraussetzungen

- NetBox ≥ 4.5
- Python ≥ 3.10

## Installation

```bash
pip install git+https://github.com/carstenviell/netbox-interface-label.git
```

In der `configuration.py`:
```python
PLUGINS = [
    # ...
    'netbox_interface_label',
]
```

Danach Migrationen anwenden und NetBox neu starten:
```bash
python manage.py migrate
python manage.py backfill_interface_labels   # optional: Vorschläge für bereits bestehende Verkabelung erzeugen
```
