from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelForm

from .label_logic import LABEL_CAPABLE_MODELS
from .models import LabelFormatSettings, LabelScheme


class LabelSuggestionFilterForm(forms.Form):
    model = None

    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            app_label='dcim',
            model__in=[m._meta.model_name for m in LABEL_CAPABLE_MODELS],
        ),
        required=False,
        label=_('Type'),
    )


class LabelSchemeForm(NetBoxModelForm):
    class Meta:
        model = LabelScheme
        fields = (
            'slot_1', 'slot_1_text', 'separator_1',
            'slot_2', 'slot_2_text', 'separator_2',
            'slot_3', 'slot_3_text', 'separator_3',
            'slot_4', 'slot_4_text', 'separator_4',
            'slot_5', 'slot_5_text',
            'tags',
        )


class LabelFormatSettingsForm(NetBoxModelForm):
    class Meta:
        model = LabelFormatSettings
        fields = ('temp_prefix', 'disconnect_prefix', 'tags')
