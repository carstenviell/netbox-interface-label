from django.utils.translation import gettext_lazy as _

from netbox.plugins.navigation import PluginMenuItem

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_interface_label:labelsuggestion_list',
        link_text=_('Label Suggestions'),
    ),
    PluginMenuItem(
        link='plugins:netbox_interface_label:settings',
        link_text=_('Settings'),
    ),
)
