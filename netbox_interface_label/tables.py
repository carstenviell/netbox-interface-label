import django_tables2 as tables
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from dcim.tables import DeviceInterfaceTable, InterfaceTable
from netbox.tables import NetBoxTable, columns
from utilities.tables import register_table_column

from .models import LabelSuggestion


class SuggestionBadgeColumn(tables.Column):
    """
    Marks rows with an open, non-dismissed label suggestion. Loads the set of
    matching object_ids once per table render (cached on this column instance,
    which register_table_column deep-copies per table instantiation) instead
    of querying per row.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', _('Label suggestion'))
        kwargs.setdefault('orderable', False)
        kwargs.setdefault('empty_values', ())
        super().__init__(*args, **kwargs)
        self._pending_ids = None

    def _pending_ids_for(self, model):
        if self._pending_ids is None:
            content_type = ContentType.objects.get_for_model(model)
            self._pending_ids = set(
                LabelSuggestion.objects.filter(content_type=content_type, dismissed=False)
                .values_list('object_id', flat=True)
            )
        return self._pending_ids

    def render(self, record):
        if record.pk in self._pending_ids_for(type(record)):
            return format_html(
                '<i class="mdi mdi-tag-outline text-warning" title="{}"></i>',
                _('Label suggestion pending'),
            )
        return ''


def register_badge_columns():
    register_table_column(SuggestionBadgeColumn(), 'label_suggestion', InterfaceTable, DeviceInterfaceTable)


class LabelSuggestionTable(NetBoxTable):
    # LabelSuggestion has no registered edit/delete/changelog views (bulk-apply
    # is the only action) - an empty actions tuple skips the URL reversal that
    # ActionsColumn otherwise always attempts.
    actions = columns.ActionsColumn(actions=())

    endpoint = tables.Column(orderable=False, empty_values=())
    endpoint_type = tables.Column(accessor='content_type', orderable=False, verbose_name=_('Type'))
    current_label = tables.Column(orderable=False, empty_values=(), verbose_name=_('Current label'))
    suggested_label = tables.Column(verbose_name=_('Suggested label'))
    dismissed = columns.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = LabelSuggestion
        fields = ('pk', 'endpoint', 'endpoint_type', 'current_label', 'suggested_label', 'dismissed', 'created')
        default_columns = ('pk', 'endpoint', 'endpoint_type', 'current_label', 'suggested_label', 'dismissed')

    def render_endpoint(self, record):
        endpoint = record.endpoint
        return format_html('<a href="{}">{}</a>', endpoint.get_absolute_url(), endpoint)

    def render_endpoint_type(self, record):
        return record.content_type.model_class()._meta.verbose_name

    def render_current_label(self, record):
        return record.endpoint.label or '—'
