# netbox-interface-label

NetBox-Plugin, das beim Verkabeln von Interfaces und Power-Ports (PowerPort/PowerOutlet) automatisch einen Label-Vorschlag berechnet – basierend auf dem tatsächlichen Kabelpfad, auch durch Patch-Panels (FrontPort/RearPort) hindurch.

## Verhalten

- Führt das Kabel zu einem echten Ziel-Interface/-Power-Port, lautet der Vorschlag `{Devicename}_{Portname}` des fernen Endes.
- Führt das Kabel (noch) nur zu einem Patch-Panel-Port, lautet der Vorschlag `TEMP_{Devicename}_{Portname}` – wird automatisch aktualisiert, sobald die Verkabelung vervollständigt wird.
- Verbindungen entstehen **symmetrisch**: beide Enden bekommen einen Vorschlag.
- Vorschläge werden nie automatisch übernommen – der Nutzer bestätigt sie explizit auf der Detailseite des Interfaces/Power-Ports.
- Wird ein Kabel direkt getrennt, bekommt ein vorhandenes Label automatisch das Präfix `GETRENNT_` (einzige automatische Ausnahme).

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
