from netbox.plugins import PluginConfig


class InterfaceLabelConfig(PluginConfig):
    name = 'netbox_interface_label'
    verbose_name = 'Interface Label'
    description = 'Suggests interface/power-port labels based on the connected cable path.'
    version = '1.1.0'
    author = 'Carsten Viell'
    base_url = 'interface-label'

    def ready(self):
        super().ready()
        from . import signals  # noqa: F401
        from .tables import register_badge_columns
        register_badge_columns()


config = InterfaceLabelConfig
