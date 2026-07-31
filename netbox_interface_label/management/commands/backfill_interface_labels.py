from django.core.management.base import BaseCommand

from netbox_interface_label.label_logic import recompute_all_suggestions


class Command(BaseCommand):
    help = (
        'Creates pending LabelSuggestion entries for all already-cabled interfaces and power ports. '
        'Never writes to the label field itself - suggestions still require confirmation in the UI. '
        'Idempotent, safe to re-run.'
    )

    def handle(self, *args, **options):
        total = recompute_all_suggestions()
        self.stdout.write(self.style.SUCCESS(f'{total} Endpunkte insgesamt geprueft.'))
