from netbox.api.viewsets import NetBoxModelViewSet

from netbox_interface_label.models import LabelFormatSettings, LabelScheme

from .serializers import LabelFormatSettingsSerializer, LabelSchemeSerializer


class LabelSchemeViewSet(NetBoxModelViewSet):
    queryset = LabelScheme.objects.all()
    serializer_class = LabelSchemeSerializer


class LabelFormatSettingsViewSet(NetBoxModelViewSet):
    queryset = LabelFormatSettings.objects.all()
    serializer_class = LabelFormatSettingsSerializer
