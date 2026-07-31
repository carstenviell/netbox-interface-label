from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from dcim.models import Cable, CablePath, Interface, PortMapping, PowerOutlet, PowerPort
from dcim.models.cables import trace_paths

from .label_logic import DISCONNECT_PREFIX, LABEL_CAPABLE_MODELS, compute_suggested_label_for_endpoint
from .label_logic import upsert_or_clear_suggestion as _upsert_or_clear_suggestion
from .models import LabelSuggestion

# NetBox's own cable-path retracing (dcim/signals.py, dcim/utils.py) can fire
# several intermediate post_save/post_delete(CablePath) events for the *same*
# origin while a multi-hop patch-panel chain is being retraced, some carrying
# transient/stale data - and the order in which they fire isn't guaranteed
# deterministic (it depends on the order Django's cascade collector happens to
# process cascaded CableTermination rows in). Hooking CablePath directly is
# therefore unreliable. Instead, this module hooks the *outer* events (Cable's
# own `trace_paths` signal, sent as the final step of Cable.save(); Cable's
# pre_delete/post_delete; PortMapping's post_save/post_delete) and always
# recomputes from each endpoint's `_path` FK - which is only reliably settled
# *after* NetBox's own receivers for these same signals have already run. That
# is guaranteed here because dcim's signal receivers are registered during
# Django app startup before any plugin's (NetBox always loads PLUGINS after
# the core apps), so our receivers - registered on the same signals - always
# run after Core's for a given dispatch.


def _affected_origins(*nodes):
    """
    Find every LABEL_CAPABLE_MODELS endpoint whose CablePath passes through
    any of the given nodes (an interface/power-port itself, or an
    intermediate front/rear port it's patched through).
    """
    query = Q()
    for node in nodes:
        query |= Q(_nodes__contains=node)

    origins = {}
    for cablepath in CablePath.objects.filter(query):
        for origin in cablepath.origins:
            if isinstance(origin, LABEL_CAPABLE_MODELS):
                origins[(type(origin), origin.pk)] = origin
    return list(origins.values())


def _recompute_and_upsert(endpoint):
    endpoint.refresh_from_db()
    new_label = compute_suggested_label_for_endpoint(endpoint)
    _upsert_or_clear_suggestion(endpoint, new_label)


@receiver(trace_paths, sender=Cable)
def handle_cable_traced(instance, **kwargs):
    nodes = [*instance.a_terminations, *instance.b_terminations]
    for endpoint in _affected_origins(*nodes):
        _recompute_and_upsert(endpoint)


@receiver(pre_delete, sender=Cable)
def handle_cable_pre_delete(instance, **kwargs):
    """
    Capture which endpoints will be affected (terminations are still intact
    here) for handle_cable_post_delete, and apply the GETRENNT_ prefix
    immediately - the only label write that happens without user confirmation.
    """
    nodes = [*instance.a_terminations, *instance.b_terminations]
    instance._label_affected_origins = _affected_origins(*nodes)

    for termination in nodes:
        if not isinstance(termination, LABEL_CAPABLE_MODELS):
            continue
        if not termination.label or termination.label.startswith(DISCONNECT_PREFIX):
            continue
        # ComponentModel.label has max_length=64; truncate rather than let a
        # long existing label + prefix silently overflow the column.
        new_label = f'{DISCONNECT_PREFIX}{termination.label}'[:64]
        type(termination).objects.filter(pk=termination.pk).update(label=new_label)


@receiver(post_delete, sender=Cable)
def handle_cable_post_delete(instance, **kwargs):
    for endpoint in getattr(instance, '_label_affected_origins', []):
        _recompute_and_upsert(endpoint)


@receiver(post_save, sender=PortMapping)
@receiver(post_delete, sender=PortMapping)
def handle_portmapping_change(instance, **kwargs):
    """
    Re-patching a panel (front/rear port mapping) can complete or break a
    path without touching any Cable directly.
    """
    for endpoint in _affected_origins(instance.front_port, instance.rear_port):
        _recompute_and_upsert(endpoint)


@receiver(post_delete, sender=Interface)
@receiver(post_delete, sender=PowerPort)
@receiver(post_delete, sender=PowerOutlet)
def handle_endpoint_delete(instance, **kwargs):
    """
    Clean up an orphaned LabelSuggestion when its endpoint is deleted outright
    (GenericForeignKey has no DB-level cascade).
    """
    content_type = ContentType.objects.get_for_model(instance)
    LabelSuggestion.objects.filter(content_type=content_type, object_id=instance.pk).delete()
