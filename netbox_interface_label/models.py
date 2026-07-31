from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet

TOKEN_CHOICES = [
    ('', _('— none —')),
    ('device_name', _('Device Name')),
    ('port_name', _('Port Name')),
    ('device_role', _('Device Role')),
    ('site', _('Site')),
    ('location', _('Location')),
    ('free_text', _('Free text')),
]


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


class LabelScheme(NetBoxModel):
    """
    Configurable label composition for one endpoint type (Interface, PowerPort or
    PowerOutlet), keyed by content_type. Up to 5 ordered slots, each resolving to a
    token value on the far-end target; joined by the separator following each slot
    (skipping slots that resolve empty, so no leading/duplicate separators appear).
    """
    content_type = models.OneToOneField(
        to=ContentType,
        on_delete=models.CASCADE,
        editable=False,
        related_name='+',
    )

    slot_1 = models.CharField(max_length=20, choices=TOKEN_CHOICES, blank=True, default='device_name')
    slot_1_text = models.CharField(max_length=50, blank=True, verbose_name=_('Free text value'))
    separator_1 = models.CharField(max_length=10, blank=True, default='_')

    slot_2 = models.CharField(max_length=20, choices=TOKEN_CHOICES, blank=True, default='port_name')
    slot_2_text = models.CharField(max_length=50, blank=True, verbose_name=_('Free text value'))
    separator_2 = models.CharField(max_length=10, blank=True, default='_')

    slot_3 = models.CharField(max_length=20, choices=TOKEN_CHOICES, blank=True)
    slot_3_text = models.CharField(max_length=50, blank=True, verbose_name=_('Free text value'))
    separator_3 = models.CharField(max_length=10, blank=True, default='_')

    slot_4 = models.CharField(max_length=20, choices=TOKEN_CHOICES, blank=True)
    slot_4_text = models.CharField(max_length=50, blank=True, verbose_name=_('Free text value'))
    separator_4 = models.CharField(max_length=10, blank=True, default='_')

    slot_5 = models.CharField(max_length=20, choices=TOKEN_CHOICES, blank=True)
    slot_5_text = models.CharField(max_length=50, blank=True, verbose_name=_('Free text value'))

    class Meta:
        verbose_name = _('Label Scheme')
        verbose_name_plural = _('Label Schemes')

    def __str__(self):
        if self.content_type_id:
            return _('%(type)s label scheme') % {'type': self.content_type.model_class()._meta.verbose_name}
        return str(_('Label Scheme'))

    def get_absolute_url(self):
        return reverse('plugins:netbox_interface_label:settings')

    @property
    def slots(self):
        return (
            (self.slot_1, self.slot_1_text, self.separator_1),
            (self.slot_2, self.slot_2_text, self.separator_2),
            (self.slot_3, self.slot_3_text, self.separator_3),
            (self.slot_4, self.slot_4_text, self.separator_4),
            (self.slot_5, self.slot_5_text, ''),
        )


class LabelFormatSettings(NetBoxModel):
    """
    Singleton holding the two automatic-label prefixes. Enforced as a singleton via
    clean() (no DB constraint), matching NamierungsKonfiguration in netbox_name_generator.
    """
    temp_prefix = models.CharField(
        max_length=20, blank=True, default='TEMP_',
        verbose_name=_('Incomplete connection prefix'),
        help_text=_('Prefix used when the cable path only reaches a patch panel port, not a real target yet.'),
    )
    disconnect_prefix = models.CharField(
        max_length=20, blank=True, default='GETRENNT_',
        verbose_name=_('Disconnected prefix'),
        help_text=_('Prefix automatically added to an existing label when its cable is removed.'),
    )

    class Meta:
        verbose_name = _('Label Format Settings')
        verbose_name_plural = _('Label Format Settings')

    def __str__(self):
        return str(_('Label Format Settings'))

    def clean(self):
        super().clean()
        if LabelFormatSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError(_('Only one Label Format Settings instance is allowed. Edit the existing one.'))

    def get_absolute_url(self):
        return reverse('plugins:netbox_interface_label:settings')
