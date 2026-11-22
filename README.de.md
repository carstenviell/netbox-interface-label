[English](README.md) | **Deutsch**

# NetBox Interface Label

[NetBox](https://github.com/netbox-community/netbox)-Plugin, das beim Verkabeln von Interfaces und Power-Ports (PowerPort/PowerOutlet) automatisch einen Label-Vorschlag berechnet – basierend auf dem tatsächlichen Kabelpfad, auch durch Patch-Panels (FrontPort/RearPort) hindurch.

## Funktionen

- Führt das Kabel zu einem echten Ziel-Interface/-Power-Port, setzt sich der Vorschlag aus dem konfigurierten Namensaufbau des fernen Endes zusammen (Standard: `{Devicename}_{Portname}`).
- Führt das Kabel (noch) nur zu einem Patch-Panel-Port, wird ein konfigurierbares Präfix vorangestellt (Standard: `TEMP_`) – wird automatisch aktualisiert, sobald die Verkabelung vervollständigt wird.
- Verbindungen entstehen **symmetrisch**: beide Enden bekommen einen Vorschlag.
- Vorschläge werden nie automatisch übernommen – der Nutzer bestätigt sie explizit (Banner auf der Detailseite, oder gesammelt auf der Übersichtsseite mit Massenübernahme).
- Wird ein Kabel direkt getrennt, bekommt ein vorhandenes Label automatisch ein konfigurierbares Präfix (Standard: `GETRENNT_`, einzige automatische Ausnahme).

## Konfiguration

Unter **Plugins → Settings** lässt sich pro Gerätekomponententyp (Interface/PowerPort/PowerOutlet) der Namensaufbau frei zusammenstellen: bis zu 5 Bausteine (Gerätename, Portname, Geräterolle, Standort, Lokation, Freitext) in beliebiger Reihenfolge, mit individuellem Trennzeichen zwischen den Bausteinen. Die `TEMP_`/`GETRENNT_`-Präfixe sind dort ebenfalls als Text änderbar.

## Voraussetzungen

- NetBox **4.5** oder neuer (getestet mit 4.7)
- Python ≥ 3.10

## Installation

Das Plugin liegt nicht auf PyPI. Installiert wird aus dem GitHub-Release-Archiv – das funktioniert ohne `git`,
auch im netbox-docker-Image. `v1.0.2` ggf. durch das gewünschte [Release](https://github.com/carstenviell/netbox-interface-label/releases) ersetzen.

**NetBox aus dem Quellcode (systemd):**

```bash
sudo /opt/netbox/venv/bin/pip install https://github.com/carstenviell/netbox-interface-label/archive/refs/tags/v1.0.2.tar.gz

# bleibt bei NetBox-Upgrades erhalten (upgrade.sh installiert local_requirements.txt neu)
echo "https://github.com/carstenviell/netbox-interface-label/archive/refs/tags/v1.0.2.tar.gz" | sudo tee -a /opt/netbox/local_requirements.txt
```

**netbox-docker:** in `plugin_requirements.txt`

```text
https://github.com/carstenviell/netbox-interface-label/archive/refs/tags/v1.0.2.tar.gz
```

und in `Dockerfile-Plugins` (aus dem `netbox`, `netbox-worker` und `netbox-housekeeping` per `docker-compose.override.yml` gebaut werden):

```dockerfile
FROM netboxcommunity/netbox:v4.7
COPY ./plugin_requirements.txt /opt/netbox/
RUN /usr/local/bin/uv pip install -r /opt/netbox/plugin_requirements.txt
```

Plugin aktivieren in der `configuration.py` (Docker: `configuration/plugins.py`):

```python
PLUGINS = [
    # ...
    'netbox_interface_label',
]
```

Migrationen anwenden und **beide** Dienste neu starten:

```bash
cd /opt/netbox/netbox
sudo /opt/netbox/venv/bin/python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

Docker: `docker compose build --no-cache && docker compose up -d` – die Migrationen laufen beim Start automatisch.

Optional – Label-Vorschläge für bereits bestehende Verkabelung erzeugen:

```bash
sudo /opt/netbox/venv/bin/python manage.py backfill_interface_labels
```

### Upgrade

Neues Release-Archiv installieren (auch in `local_requirements.txt` bzw. `plugin_requirements.txt`
anpassen), danach `migrate` und Neustart (Docker: neu bauen).

## Sprache

Die Oberfläche ist englisch, eine deutsche Übersetzung wird mitgeliefert. Angezeigt wird die Sprache,
die der Benutzer in NetBox gewählt hat (*Profil → Einstellungen → Sprache*); für Sprachen ohne Übersetzung erscheint Englisch.

## Lizenz

[Apache License 2.0](LICENSE)
