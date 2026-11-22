from django.db import migrations, models

OLD_DEFAULT = 'GETRENNT_'
NEW_DEFAULT = 'OLD_'


def switch_default(apps, schema_editor):
    """Switch only settings that still carry the old (German) default; custom prefixes are kept.
    Existing labels are not touched."""
    apps.get_model('netbox_interface_label', 'LabelFormatSettings').objects.filter(
        disconnect_prefix=OLD_DEFAULT).update(disconnect_prefix=NEW_DEFAULT)


def switch_back(apps, schema_editor):
    apps.get_model('netbox_interface_label', 'LabelFormatSettings').objects.filter(
        disconnect_prefix=NEW_DEFAULT).update(disconnect_prefix=OLD_DEFAULT)


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_interface_label', '0002_labelformatsettings_labelscheme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labelformatsettings',
            name='disconnect_prefix',
            field=models.CharField(blank=True, default=NEW_DEFAULT, max_length=20,
                                   verbose_name='Disconnected prefix',
                                   help_text='Prefix automatically added to an existing label when its cable is removed.'),
        ),
        migrations.RunPython(switch_default, switch_back),
    ]
