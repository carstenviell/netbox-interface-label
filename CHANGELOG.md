**English** | [Deutsch](CHANGELOG.de.md)

# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - 2026-11-22

### Changed
- **The prefix for disconnected cables is now English and shorter: `OLD_` instead of `GETRENNT_`** (e.g. `OLD_SW01_Gi1/0/1`). Migration `0003` only switches the setting if it still holds the old default `GETRENNT_` – a custom prefix is kept. Existing labels are not changed.
- Documentation in two languages: `README.md` (English) / `README.de.md` (German), `CHANGELOG.md` / `CHANGELOG.de.md`; added `LICENSE` (Apache-2.0, as declared in `pyproject.toml`).

## [1.0.2] - 2026-11-22

### Fixed
- Installation guide: installation from the GitHub release archive instead of `git+https://…` (the netbox-docker image has no `git`); variants for source installation (incl. `local_requirements.txt`) and netbox-docker, restart of web and worker, upgrade.
- The German translation is now shipped compiled (`django.mo`) – before only the `.po`; without `gettext` on the target system the UI stayed English. Added a test against outdated/guessed translations.

## [1.0.1] - 2026-08-01

### Security
- `ApplySuggestionView`/`DismissSuggestionView`/`LabelSettingsView` so far only checked `LoginRequiredMixin` (login), no NetBox permission — every logged-in account could set arbitrary interface/power port/power outlet labels and change the global naming scheme. `ApplySuggestionView`/`DismissSuggestionView` now check `change_<model>` on the actual target endpoint (respecting existing ObjectPermission constraints); `LabelSettingsView` requires `change_labelformatsettings`/`change_labelscheme`
- `BulkApplySuggestionsView` processed suggestions without permission filtering (also with `_all=1`); it now additionally filters with `.restrict(user, 'change')` and checks the permission on the target endpoint per suggestion
- Fixed an open redirect via the unvalidated `return_url` form field in `BulkApplySuggestionsView` (`safe_for_redirect()` check, following the pattern established in NetBox core)

## [1.0.0] - 2026-08-01

First stable release. Sums up the entire development so far (0.1.0–0.3.1): suggestion calculation along the complete cable path incl. patch panels, confirmation banners in several places (interface/power port/power outlet, cable detail page), overview page with bulk apply, badge icon, configurable naming scheme including prefixes via a settings page, full i18n (German/English). No functional changes compared to 0.3.1 – a pure version milestone.

## [0.3.1] - 2026-08-01

### Fixed
- Existing open label suggestions were not recalculated when the naming scheme or the prefixes were changed on the settings page and kept showing the value calculated with the old configuration until the next cabling event. Saving the settings now immediately recalculates all open suggestions

## [0.3.0] - 2026-07-31

### Added
- Configurable naming scheme on a new settings page: per device component type (interface/power port/power outlet) up to 5 building blocks (device name, port name, device role, site, location, free text) can be combined in any order with an individual separator between them (`LabelScheme`)
- The `TEMP_` and `GETRENNT_` prefixes are now configurable as text (`LabelFormatSettings`) instead of being hard-coded
- Full i18n support: all UI texts (banners, buttons, settings page, messages) are now translatable; a German translation is included. Automatically follows the language set in NetBox, no separate language switch needed

### Changed
- Existing installations keep the previous behaviour without any configuration (default scheme: devicename_portname, default prefixes TEMP_/GETRENNT_)

## [0.2.1] - 2026-07-31

### Fixed
- The badge column had no name in the column configuration (missing `verbose_name`)
- The checkbox column for multiple selection was missing on the overview page, because NetBox only shows bulk checkboxes if at least one registered multi action exists – "Apply selected" is now registered as a real `ObjectAction` instead of a standalone button

## [0.2.0] - 2026-07-31

### Added
- Badge icon in the device interface list for an open label suggestion (the column has to be enabled once via the column gear)
- Banner also on the cable detail page (`/dcim/cables/<pk>/`), showing suggestions for both sides of the connection
- New overview page `/plugins/interface-label/suggestions/` with all open suggestions (interface/power port/power outlet), filterable by type, with checkbox multiple selection and bulk apply (each selected object gets its individual suggestion value)
- Menu entry "Label Suggestions" in the NetBox main menu

### Changed
- A suggestion that already equals the current label is no longer kept as an open `LabelSuggestion` (affects e.g. interfaces that were already named correctly by hand, or a repeated backfill)

## [0.1.0] - 2026-07-31

### Added
- Automatic label suggestion calculation when cabling interfaces and power ports (power port/power outlet), based on the actual cable path – also through patch panels (FrontPort/RearPort)
- `TEMP_` placeholder suggestion as long as the cabling only reaches a patch panel port; updated automatically as soon as the chain is completed to a real target interface
- Symmetric suggestions on both sides of a connection
- Confirmation banner on the interface/power port/power outlet detail page ("Apply"/"Dismiss") – no automatic write to the label field
- Special case cable removal: automatic `GETRENNT_` prefix on an existing label, without confirmation
- `backfill_interface_labels` management command for existing cabling
