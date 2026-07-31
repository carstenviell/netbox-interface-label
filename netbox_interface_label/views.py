from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from netbox.views import generic

from .filtersets import LabelSuggestionFilterSet
from .forms import LabelFormatSettingsForm, LabelSchemeForm, LabelSuggestionFilterForm
from .label_logic import LABEL_CAPABLE_MODELS, apply_suggestion
from .models import LabelFormatSettings, LabelScheme, LabelSuggestion
from .object_actions import ApplySelectedSuggestions
from .tables import LabelSuggestionTable


class ApplySuggestionView(LoginRequiredMixin, View):

    def post(self, request, pk):
        suggestion = get_object_or_404(LabelSuggestion, pk=pk)
        endpoint = apply_suggestion(suggestion)
        return redirect(endpoint.get_absolute_url())


class DismissSuggestionView(LoginRequiredMixin, View):

    def post(self, request, pk):
        suggestion = get_object_or_404(LabelSuggestion, pk=pk)
        endpoint = suggestion.endpoint
        suggestion.dismissed = True
        suggestion.save(update_fields=['dismissed', 'last_updated'])

        return redirect(endpoint.get_absolute_url())


class LabelSuggestionListView(generic.ObjectListView):
    queryset = LabelSuggestion.objects.select_related('content_type')
    table = LabelSuggestionTable
    filterset = LabelSuggestionFilterSet
    filterset_form = LabelSuggestionFilterForm
    actions = (ApplySelectedSuggestions,)


class BulkApplySuggestionsView(LoginRequiredMixin, View):

    def post(self, request):
        pk_list = request.POST.getlist('pk')
        if request.POST.get('_all'):
            queryset = LabelSuggestionFilterSet(request.GET, queryset=LabelSuggestion.objects.all()).qs
        else:
            queryset = LabelSuggestion.objects.filter(pk__in=pk_list)

        with transaction.atomic():
            count = 0
            for suggestion in queryset:
                apply_suggestion(suggestion)
                count += 1

        messages.success(request, _('%(count)d label(s) applied.') % {'count': count})

        return_url = request.POST.get('return_url') or reverse('plugins:netbox_interface_label:labelsuggestion_list')
        return redirect(return_url)


class LabelSettingsView(LoginRequiredMixin, View):
    template_name = 'netbox_interface_label/settings.html'

    def _instances(self):
        format_settings, _created = LabelFormatSettings.objects.get_or_create(pk=1)
        schemes = [
            (model, LabelScheme.objects.get_or_create(content_type=ContentType.objects.get_for_model(model))[0])
            for model in LABEL_CAPABLE_MODELS
        ]
        return format_settings, schemes

    def _forms(self, data=None):
        format_settings, schemes = self._instances()
        format_form = LabelFormatSettingsForm(data, instance=format_settings, prefix='format')
        scheme_forms = [
            (model._meta.verbose_name, LabelSchemeForm(data, instance=scheme, prefix=model._meta.model_name))
            for model, scheme in schemes
        ]
        return format_form, scheme_forms

    def get(self, request):
        format_form, scheme_forms = self._forms()
        return render(request, self.template_name, {'format_form': format_form, 'scheme_forms': scheme_forms})

    def post(self, request):
        format_form, scheme_forms = self._forms(request.POST)
        all_forms = [format_form] + [form for _label, form in scheme_forms]
        valid = [form.is_valid() for form in all_forms]

        if all(valid):
            for form in all_forms:
                form.save()
            messages.success(request, _('Settings saved.'))
            return redirect('plugins:netbox_interface_label:settings')

        return render(request, self.template_name, {'format_form': format_form, 'scheme_forms': scheme_forms})
