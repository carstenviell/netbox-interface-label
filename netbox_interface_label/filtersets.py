import django_filters
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from .label_logic import LABEL_CAPABLE_MODELS
from .models import LabelSuggestion


class LabelSuggestionFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(method='search', label=_('Search'))
    content_type = django_filters.ModelChoiceFilter(
        queryset=ContentType.objects.filter(
            app_label='dcim',
            model__in=[m._meta.model_name for m in LABEL_CAPABLE_MODELS],
        ),
        label=_('Type'),
    )
    dismissed = django_filters.BooleanFilter()

    class Meta:
        model = LabelSuggestion
        fields = ('content_type', 'dismissed')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(suggested_label__icontains=value)
