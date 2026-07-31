from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from utilities.querysets import RestrictedQuerySet


class LabelSuggestion(models.Model):
    """
    Pending label suggestion for a cable-terminating endpoint (Interface, PowerPort, PowerOutlet).
    One row per endpoint; re-computed whenever the underlying CablePath changes.
    """
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveBigIntegerField()
    endpoint = GenericForeignKey('content_type', 'object_id')

    suggested_label = models.CharField(max_length=100)
    dismissed = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Required by generic.ObjectListView, which calls queryset.restrict(user, action)
    # for permission filtering - a lightweight NetBox queryset feature, unrelated to
    # NetBoxModel (no changelog/custom-fields/API-serializer requirement pulled in).
    objects = RestrictedQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['content_type', 'object_id'], name='unique_endpoint_suggestion'),
        ]

    def __str__(self):
        return f'{self.endpoint}: {self.suggested_label}'
