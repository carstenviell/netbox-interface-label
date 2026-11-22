import logging

from django.contrib.contenttypes.models import ContentType

from dcim.models import FrontPort, Interface, PowerFeed, PowerOutlet, PowerPort, RearPort

from .models import LabelFormatSettings, LabelScheme, LabelSuggestion

logger = logging.getLogger('netbox.plugins.netbox_interface_label')

# Endpoint types that can hold a `label` field and therefore a LabelSuggestion.
LABEL_CAPABLE_MODELS = (Interface, PowerPort, PowerOutlet)

# ComponentModel.label has max_length=64; a long composed name plus a
# TEMP_/OLD_-style prefix can exceed it. Truncate rather than let full_clean()
# raise, since the value is already a best-effort suggestion.
LABEL_MAX_LENGTH = 64


def get_format_settings():
    settings, _ = LabelFormatSettings.objects.get_or_create(pk=1)
    return settings


def _get_scheme(origin_type):
    if origin_type not in LABEL_CAPABLE_MODELS:
        return None
    content_type = ContentType.objects.get_for_model(origin_type)
    scheme, _ = LabelScheme.objects.get_or_create(content_type=content_type)
    return scheme


def _resolve_token(token, target, free_text):
    """
    Resolve one LabelScheme slot's token to text, given the far-end `target`
    object. Tokens that don't apply to `target` (e.g. device_role/location for
    a PowerFeed, which has no device) resolve to '' and are skipped when
    composing the final label.
    """
    if not token:
        return ''
    if token == 'free_text':
        return free_text
    if token == 'port_name':
        return target.name
    if token == 'device_name':
        if hasattr(target, 'device'):
            return target.device.name
        if hasattr(target, 'power_panel'):
            return target.power_panel.name
        return ''
    if token == 'device_role':
        if hasattr(target, 'device') and target.device.role:
            return target.device.role.name
        return ''
    if token == 'site':
        if hasattr(target, 'device') and target.device.site:
            return target.device.site.name
        if hasattr(target, 'power_panel') and target.power_panel.site:
            return target.power_panel.site.name
        return ''
    if token == 'location':
        if hasattr(target, 'device') and target.device.location:
            return target.device.location.name
        return ''
    return ''


def _compose(origin, target):
    """
    Build a label from `origin`'s configured LabelScheme, resolving each slot
    against `target`. Slots that resolve empty are skipped entirely (no
    leading/duplicate separators); the separator following each *used* slot is
    inserted only between two present values.
    """
    scheme = _get_scheme(type(origin))
    if scheme is None:
        return None

    values = [
        (value, separator)
        for slot, slot_text, separator in scheme.slots
        for value in [_resolve_token(slot, target, slot_text)]
        if value
    ]
    if not values:
        return None

    parts, separators = [v for v, _ in values], [s for _, s in values[:-1]]
    label = parts[0]
    for part, sep in zip(parts[1:], separators):
        label += sep + part
    return label


def _label_from_last_segment(nodes, origin):
    """
    Determine the suggested label text from the last segment of a cable path
    (a list of objects occupying the final hop) and the interface/power-port
    whose suggestion is being computed (determines which LabelScheme applies).
    Multi-termination segments (breakout cables) are intentionally unsupported.
    """
    if len(nodes) != 1:
        return None

    target = nodes[0]

    if isinstance(target, (Interface, PowerPort, PowerOutlet, PowerFeed)):
        return _compose(origin, target)

    if isinstance(target, (FrontPort, RearPort)):
        # Path doesn't reach a real endpoint yet - only as far as a patch panel port.
        composed = _compose(origin, target)
        if composed is None:
            return None
        return f'{get_format_settings().temp_prefix}{composed}'

    return None


def compute_suggested_label_from_cablepath(cablepath):
    """
    Compute the suggested label directly from a CablePath instance. Must be used
    (rather than `endpoint._path`) inside signal handlers, since CablePath.save()
    only sets the origin's `_path` FK *after* firing post_save.
    """
    origins = cablepath.origins
    if len(origins) != 1:
        return None
    last_segment = cablepath.path_objects[-1] if cablepath.path else []
    return _label_from_last_segment(last_segment, origins[0])


def compute_suggested_label_for_endpoint(endpoint):
    """
    Compute the suggested label for an already-saved endpoint by reading its
    cached CablePath. Safe to use outside of signal handlers (e.g. backfill),
    where there's no in-flight CablePath.save() to race against.
    """
    cablepath = endpoint._path
    if cablepath is None:
        return None
    return compute_suggested_label_from_cablepath(cablepath)


def upsert_or_clear_suggestion(endpoint, new_label):
    """
    Create/update/delete the LabelSuggestion row for `endpoint`. Endpoints that
    can't hold a `label` themselves (e.g. PowerFeed) are silently skipped.
    No suggestion is kept if it would be a no-op (already matches the current
    label) - nothing left for the user to apply.
    """
    if not isinstance(endpoint, LABEL_CAPABLE_MODELS):
        return

    content_type = ContentType.objects.get_for_model(endpoint)

    if new_label is None or new_label == endpoint.label:
        LabelSuggestion.objects.filter(content_type=content_type, object_id=endpoint.pk).delete()
        return

    suggestion, created = LabelSuggestion.objects.get_or_create(
        content_type=content_type,
        object_id=endpoint.pk,
        defaults={'suggested_label': new_label},
    )
    if not created and suggestion.suggested_label != new_label:
        suggestion.suggested_label = new_label
        suggestion.dismissed = False
        suggestion.save(update_fields=['suggested_label', 'dismissed', 'last_updated'])


def apply_suggestion(suggestion):
    """
    Write a suggestion's value to its endpoint's label and remove the
    suggestion. Shared by the single-object and bulk apply views.
    """
    endpoint = suggestion.endpoint
    label = suggestion.suggested_label
    if len(label) > LABEL_MAX_LENGTH:
        logger.warning('Truncating suggested label %r to %d characters for %r', label, LABEL_MAX_LENGTH, endpoint)
        label = label[:LABEL_MAX_LENGTH]

    endpoint.label = label
    endpoint.save()
    suggestion.delete()
    return endpoint


def recompute_all_suggestions():
    """
    Recompute (and upsert/clear) the LabelSuggestion for every already-cabled
    endpoint. Used by the backfill command and whenever the label scheme /
    format settings are changed via the Settings page - existing pending
    suggestions are otherwise only ever recomputed by a *cabling* event and
    would keep showing stale values computed under the old configuration.
    """
    count = 0
    for model in LABEL_CAPABLE_MODELS:
        for endpoint in model.objects.exclude(_path__isnull=True).select_related('device').iterator():
            new_label = compute_suggested_label_for_endpoint(endpoint)
            upsert_or_clear_suggestion(endpoint, new_label)
            count += 1
    return count
