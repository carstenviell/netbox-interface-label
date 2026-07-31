from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from netbox.views import generic

from .filtersets import LabelSuggestionFilterSet
from .forms import LabelSuggestionFilterForm
from .label_logic import apply_suggestion
from .models import LabelSuggestion
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
    template_name = 'netbox_interface_label/labelsuggestion_list.html'
    actions = ()


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

        messages.success(request, f'{count} Label(s) übernommen.')

        return_url = request.POST.get('return_url') or reverse('plugins:netbox_interface_label:labelsuggestion_list')
        return redirect(return_url)
