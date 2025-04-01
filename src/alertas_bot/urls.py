from django.urls import path

from .views import (
    BuscadorView,
    ConfiguracionUpdateView,
    ContactView,
    DeleteWatchdogView,
    ProfileUpdateView,
    WatchdogActivateView,
    WatchdogCreateView,
    WatchdogDeactivateView,
    WatchdogListView,
    delete_account,
)

urlpatterns = [
    path("configurar-rate-fee/", ConfiguracionUpdateView.as_view(), name="modificar_rate_fee"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("delete-account/", delete_account, name="delete_account"),
    path("finder/", BuscadorView.as_view(), name="finder"),
    path("watchdogs/list/", WatchdogListView.as_view(), name="watchdogs_list"),
    path("watchdog/new/", WatchdogCreateView.as_view(), name="create_watchdog"),
    path("watchdog/<uuid:pk>/deactivate/", WatchdogDeactivateView.as_view(), name="deactivate_watchdog"),
    path("watchdog/<uuid:pk>/activate/", WatchdogActivateView.as_view(), name="activate_watchdog"),
    path("watchdog/<uuid:pk>/delete/", DeleteWatchdogView.as_view(), name="delete_watchdog"),
]
