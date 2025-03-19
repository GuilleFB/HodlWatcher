from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import Configuracion
from .forms import ConfiguracionForm


class ConfiguracionUpdateView(UpdateView):
    model = Configuracion
    form_class = ConfiguracionForm
    template_name = "configuracion.html"
    success_url = reverse_lazy("modificar_rate_fee")

    def get_object(self, queryset=None):
        # Siempre retornamos el primer objeto de Configuracion
        return Configuracion.objects.first()
