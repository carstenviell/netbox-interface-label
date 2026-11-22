# Changelog

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.

Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [1.0.2] - 2026-11-22

### Behoben
- Installationsanleitung: Installation aus dem GitHub-Release-Archiv statt `git+https://…` (im netbox-docker-Image gibt es kein `git`); Varianten für Source-Installation (inkl. `local_requirements.txt`) und netbox-docker, Neustart von Web und Worker, Upgrade.
- Deutsche Übersetzung wird jetzt kompiliert mitgeliefert (`django.mo`) – vorher nur `.po`, ohne `gettext` auf dem Zielsystem blieb die Oberfläche englisch. Test gegen veraltete/geratene Übersetzungen ergänzt.

## [1.0.1] - 2026-08-01

### Sicherheit
- `ApplySuggestionView`/`DismissSuggestionView`/`LabelSettingsView` prüften bisher nur `LoginRequiredMixin` (Login), keine NetBox-Berechtigung — jeder eingeloggte Account konnte beliebige Interface-/PowerPort-/PowerOutlet-Labels setzen und den globalen Namensaufbau ändern. `ApplySuggestionView`/`DismissSuggestionView` prüfen jetzt objektbezogen `change_<model>` auf dem tatsächlichen Zielendpunkt (respektiert bestehende ObjectPermission-Constraints); `LabelSettingsView` erfordert `change_labelformatsettings`/`change_labelscheme`
- `BulkApplySuggestionsView` verarbeitete Vorschläge ungefiltert nach Berechtigung (auch bei `_all=1`); filtert jetzt zusätzlich per `.restrict(user, 'change')` und prüft je Vorschlag die Berechtigung auf den Zielendpunkt
- Offener Redirect über unvalidiertes `return_url`-Formularfeld in `BulkApplySuggestionsView` behoben (`safe_for_redirect()`-Check, analog zum in NetBox-Core etablierten Muster)

## [1.0.0] - 2026-08-01

Erstes stabiles Release. Fasst die gesamte bisherige Entwicklung (0.1.0–0.3.1) zusammen: Vorschlagsberechnung über den vollständigen Kabelpfad inkl. Patch-Panels, Bestätigungs-Banner an mehreren Stellen (Interface/PowerPort/PowerOutlet, Kabel-Detailseite), Übersichtsseite mit Massenübernahme, Badge-Icon, konfigurierbarer Namensaufbau samt Präfixen über eine Settings-Seite, vollständige i18n (Deutsch/Englisch). Keine inhaltlichen Änderungen gegenüber 0.3.1 – reiner Versions-Meilenstein.

## [0.3.1] - 2026-08-01

### Behoben
- Bestehende, noch offene Label-Vorschläge wurden beim Ändern des Namensaufbaus bzw. der Präfixe über die Settings-Seite nicht neu berechnet und zeigten weiterhin den nach der alten Konfiguration berechneten Wert an, bis das nächste Verkabelungsereignis eintrat. Das Speichern der Settings löst jetzt sofort eine Neuberechnung aller offenen Vorschläge aus

## [0.3.0] - 2026-07-31

### Neu
- Konfigurierbarer Namensaufbau über eine neue Settings-Seite: pro Gerätekomponententyp (Interface/PowerPort/PowerOutlet) lassen sich bis zu 5 Bausteine (Gerätename, Portname, Geräterolle, Standort, Lokation, Freitext) in beliebiger Reihenfolge mit individuellem Trennzeichen zwischen den Bausteinen zusammenstellen (`LabelScheme`)
- `TEMP_`- und `GETRENNT_`-Präfixe sind jetzt als Text konfigurierbar (`LabelFormatSettings`), statt fest im Code zu stehen
- Vollständige i18n-Unterstützung: alle UI-Texte (Banner, Buttons, Settings-Seite, Meldungen) sind jetzt übersetzbar; deutsche Übersetzung liegt bei. Folgt automatisch der in NetBox eingestellten Sprache, kein eigener Sprachumschalter nötig

### Geändert
- Bestehende Installationen behalten ohne Konfigurationsaufwand das bisherige Verhalten (Default-Schema: Gerätename_Portname, Standard-Präfixe TEMP_/GETRENNT_)

## [0.2.1] - 2026-07-31

### Behoben
- Badge-Spalte hatte keinen Namen in der Spalten-Konfiguration (fehlender `verbose_name`)
- Checkbox-Spalte zur Mehrfachauswahl fehlte auf der Übersichtsseite, da NetBox Bulk-Checkboxen nur anzeigt, wenn mindestens eine registrierte Mehrfach-Aktion existiert – "Ausgewählte übernehmen" ist jetzt als echte `ObjectAction` registriert statt als eigenständiger Button

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
