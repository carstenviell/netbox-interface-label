from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.object_actions import ObjectAction


class ApplySelectedSuggestions(ObjectAction):
    """
    Bulk action button for the suggestions list: posts the selected pks to
    BulkApplySuggestionsView. Registering this (multi=True) is also what makes
    NetBoxTable show its row-selection checkboxes - ObjectListView only turns
    those on if at least one permitted action has multi=True.
    """
    name = 'bulk_apply'
    label = _('Apply Selected')
    multi = True
    permissions_required = {'change'}
    template_name = 'buttons/bulk_apply.html'

    @classmethod
    def get_url(cls, obj):
        return reverse('plugins:netbox_interface_label:labelsuggestion_bulk_apply')
