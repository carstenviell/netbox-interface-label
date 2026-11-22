**English** | [Deutsch](README.de.md)

# NetBox Interface Label

[NetBox](https://github.com/netbox-community/netbox) plugin that automatically calculates a label suggestion when
interfaces and power ports (PowerPort/PowerOutlet) are cabled – based on the actual cable path, also through patch
panels (FrontPort/RearPort).

## Features

- If the cable leads to a real target interface/power port, the suggestion is built from the configured naming scheme
  of the far end (default: `{Devicename}_{Portname}`).
- If the cable (so far) only leads to a patch panel port, a configurable prefix is added (default: `TEMP_`) – updated
  automatically as soon as the cabling is completed.
- Connections are **symmetric**: both ends get a suggestion.
- Suggestions are never applied automatically – the user confirms them explicitly (banner on the detail page, or
  collected on the overview page with bulk apply).
- If a cable is removed, an existing label automatically gets a configurable prefix (default: `OLD_`, the only
  automatic change).

## Configuration

Under **Plugins → Settings** the naming scheme can be composed per device component type (Interface/PowerPort/
PowerOutlet): up to 5 building blocks (device name, port name, device role, site, location, free text) in any order,
with an individual separator between them. The `TEMP_`/`OLD_` prefixes can be changed there as text as well.

## Requirements

- NetBox **4.5** or later (tested with 4.7)
- Python ≥ 3.10

## Installation

The plugin is not published on PyPI. Install it from the GitHub release archive – this works without `git`,
also in the netbox-docker image. Replace `v1.1.0` with the [release](https://github.com/carstenviell/netbox-interface-label/releases) you want.

**NetBox installed from source (systemd):**

```bash
sudo /opt/netbox/venv/bin/pip install https://github.com/carstenviell/netbox-interface-label/archive/refs/tags/v1.1.0.tar.gz

# keep the plugin when NetBox is upgraded (upgrade.sh reinstalls local_requirements.txt)
echo "https://github.com/carstenviell/netbox-interface-label/archive/refs/tags/v1.1.0.tar.gz" | sudo tee -a /opt/netbox/local_requirements.txt
```

**netbox-docker:** add to `plugin_requirements.txt`

```text
https://github.com/carstenviell/netbox-interface-label/archive/refs/tags/v1.1.0.tar.gz
```

and to `Dockerfile-Plugins` (build `netbox`, `netbox-worker` and `netbox-housekeeping` from it via `docker-compose.override.yml`):

```dockerfile
FROM netboxcommunity/netbox:v4.7
COPY ./plugin_requirements.txt /opt/netbox/
RUN /usr/local/bin/uv pip install -r /opt/netbox/plugin_requirements.txt
```

Enable the plugin in `configuration.py` (Docker: `configuration/plugins.py`):

```python
PLUGINS = [
    # ...
    'netbox_interface_label',
]
```

Apply the migrations and restart **both** services:

```bash
cd /opt/netbox/netbox
sudo /opt/netbox/venv/bin/python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

Docker: `docker compose build --no-cache && docker compose up -d` – migrations run automatically at start.

Optional – create label suggestions for existing cabling:

```bash
sudo /opt/netbox/venv/bin/python manage.py backfill_interface_labels
```

### Upgrade

Install the new release archive (also update `local_requirements.txt` / `plugin_requirements.txt`),
then `migrate` and restart (Docker: rebuild).

## Language

The user interface is English and ships with a German translation. It follows the language the user
selected in NetBox (*Profile → Preferences → Language*); languages without a translation fall back to English.

## License

[Apache License 2.0](LICENSE)
