from django.urls import path

from . import views

app_name = 'netbox_interface_label'

urlpatterns = (
    path('suggestions/', views.LabelSuggestionListView.as_view(), name='labelsuggestion_list'),
    path('suggestions/bulk-apply/', views.BulkApplySuggestionsView.as_view(), name='labelsuggestion_bulk_apply'),
    path('suggestions/<int:pk>/apply/', views.ApplySuggestionView.as_view(), name='suggestion_apply'),
    path('suggestions/<int:pk>/dismiss/', views.DismissSuggestionView.as_view(), name='suggestion_dismiss'),
)
