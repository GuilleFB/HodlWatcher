from django import forms

from .models import Configuracion


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ["rate_fee"]
