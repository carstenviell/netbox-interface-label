from django.core.management.base import BaseCommand

from dcim.models import Interface, PowerOutlet, PowerPort

from netbox_interface_label.label_logic import compute_suggested_label_for_endpoint, upsert_or_clear_suggestion


class Command(BaseCommand):
    help = (
        'Creates pending LabelSuggestion entries for all already-cabled interfaces and power ports. '
        'Never writes to the label field itself - suggestions still require confirmation in the UI. '
        'Idempotent, safe to re-run.'
    )

    def handle(self, *args, **options):
        total = 0
        for model in (Interface, PowerPort, PowerOutlet):
            queryset = model.objects.exclude(_path__isnull=True).select_related('device')
            count = 0
            for endpoint in queryset.iterator():
                new_label = compute_suggested_label_for_endpoint(endpoint)
                upsert_or_clear_suggestion(endpoint, new_label)
                count += 1
            self.stdout.write(f'{model._meta.verbose_name}: {count} geprueft')
            total += count

        self.stdout.write(self.style.SUCCESS(f'{total} Endpunkte insgesamt geprueft.'))
