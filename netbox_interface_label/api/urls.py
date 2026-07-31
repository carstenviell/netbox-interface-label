from netbox.api.routers import NetBoxRouter

from . import views

router = NetBoxRouter()
router.register('label-schemes', views.LabelSchemeViewSet)
router.register('label-format-settings', views.LabelFormatSettingsViewSet)

urlpatterns = router.urls
