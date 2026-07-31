from netbox.api.serializers import NetBoxModelSerializer

from netbox_interface_label.models import LabelFormatSettings, LabelScheme

LABEL_SCHEME_FIELDS = (
    'id', 'url', 'display', 'content_type',
    'slot_1', 'slot_1_text', 'separator_1',
    'slot_2', 'slot_2_text', 'separator_2',
    'slot_3', 'slot_3_text', 'separator_3',
    'slot_4', 'slot_4_text', 'separator_4',
    'slot_5', 'slot_5_text',
    'created', 'last_updated',
)


class LabelSchemeSerializer(NetBoxModelSerializer):
    class Meta:
        model = LabelScheme
        fields = LABEL_SCHEME_FIELDS


class LabelFormatSettingsSerializer(NetBoxModelSerializer):
    class Meta:
        model = LabelFormatSettings
        fields = ('id', 'url', 'display', 'temp_prefix', 'disconnect_prefix', 'created', 'last_updated')
