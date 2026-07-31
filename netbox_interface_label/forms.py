from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from .label_logic import LABEL_CAPABLE_MODELS


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
