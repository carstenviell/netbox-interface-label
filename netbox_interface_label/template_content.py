from django.contrib.contenttypes.models import ContentType
from netbox.plugins import PluginTemplateExtension

from .label_logic import LABEL_CAPABLE_MODELS
from .models import LabelSuggestion


class LabelSuggestionAlert(PluginTemplateExtension):
    models = ['dcim.interface', 'dcim.powerport', 'dcim.poweroutlet']

    def alerts(self):
        obj = self.context['object']
        content_type = ContentType.objects.get_for_model(obj)
        suggestion = LabelSuggestion.objects.filter(
            content_type=content_type, object_id=obj.pk, dismissed=False,
        ).first()
        if suggestion is None:
            return ''
        return self.render('netbox_interface_label/suggestion_alert.html', extra_context={
            'suggestions': [suggestion],
        })


class CableLabelSuggestionAlert(PluginTemplateExtension):
    models = ['dcim.cable']

    def alerts(self):
        cable = self.context['object']
        terminations = [*cable.a_terminations, *cable.b_terminations]

        suggestions = []
        for termination in terminations:
            if not isinstance(termination, LABEL_CAPABLE_MODELS):
                continue
            content_type = ContentType.objects.get_for_model(termination)
            suggestion = LabelSuggestion.objects.filter(
                content_type=content_type, object_id=termination.pk, dismissed=False,
            ).first()
            if suggestion is not None:
                suggestions.append(suggestion)

        if not suggestions:
            return ''
        return self.render('netbox_interface_label/suggestion_alert.html', extra_context={
            'suggestions': suggestions,
        })


template_extensions = [LabelSuggestionAlert, CableLabelSuggestionAlert]
