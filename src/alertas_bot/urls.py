from django.urls import path
from .views import ConfiguracionUpdateView

urlpatterns = [
    path("configurar-rate-fee/", ConfiguracionUpdateView.as_view(), name="modificar_rate_fee"),
]
