import logging

from django.contrib.contenttypes.models import ContentType

from dcim.models import FrontPort, Interface, PowerFeed, PowerOutlet, PowerPort, RearPort

from .models import LabelSuggestion

logger = logging.getLogger('netbox.plugins.netbox_interface_label')

# Endpoint types that can hold a `label` field and therefore a LabelSuggestion.
LABEL_CAPABLE_MODELS = (Interface, PowerPort, PowerOutlet)

TEMP_PREFIX = 'TEMP_'
DISCONNECT_PREFIX = 'GETRENNT_'

# ComponentModel.label has max_length=64; a long device/port name plus a
# TEMP_/GETRENNT_ prefix can exceed it. Truncate rather than let full_clean()
# raise, since the value is already a best-effort suggestion.
LABEL_MAX_LENGTH = 64


def _label_from_last_segment(nodes):
    """
    Determine the suggested label text from the last segment of a cable path
    (a list of objects occupying the final hop). Multi-termination segments
    (breakout cables) are intentionally unsupported.
    """
    if len(nodes) != 1:
        return None

    target = nodes[0]

    if isinstance(target, (Interface, PowerPort, PowerOutlet)):
        return f'{target.device.name}_{target.name}'

    if isinstance(target, PowerFeed):
        return f'{target.power_panel.name}_{target.name}'

    if isinstance(target, (FrontPort, RearPort)):
        # Path doesn't reach a real endpoint yet - only as far as a patch panel port.
        return f'{TEMP_PREFIX}{target.device.name}_{target.name}'

    return None


def compute_suggested_label_from_cablepath(cablepath):
    """
    Compute the suggested label directly from a CablePath instance. Must be used
    (rather than `endpoint._path`) inside signal handlers, since CablePath.save()
    only sets the origin's `_path` FK *after* firing post_save.
    """
    last_segment = cablepath.path_objects[-1] if cablepath.path else []
    return _label_from_last_segment(last_segment)


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
