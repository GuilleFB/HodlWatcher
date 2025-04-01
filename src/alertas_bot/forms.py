from django import forms
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from .models import Configuracion, ContactMessage, InvestmentWatchdog


class ContactForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3)
    privacy_policy = forms.BooleanField(label="I have read and agree to the Privacy Policy", required=True)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message", "captcha", "privacy_policy"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }
        labels = {
            "name": "Your Name",
            "email": "Your Email Address",
            "phone": "Your Phone Number (optional)",
            "subject": "Subject",
            "message": "Your Message",
        }


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ["image"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }


class InvestmentWatchdogForm(forms.ModelForm):
    # Definir los campos explícitamente para poder asignarles choices
    currency = forms.ChoiceField(label="Moneda", widget=forms.Select(attrs={"class": "form-select"}))

    payment_method_id = forms.ChoiceField(label="Método de pago", widget=forms.Select(attrs={"class": "form-select"}))

    asset_code = forms.ChoiceField(label="Activo", widget=forms.Select(attrs={"class": "form-select"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtener payment_methods de la caché
        cache_key = "payment_methods"
        cached_payment_methods = cache.get(cache_key) or []

        # Crear las opciones para payment_method_id
        payment_method_choices = [
            (method["id"], f"{method['name']} ({method['type']})") for method in cached_payment_methods
        ]
        self.fields["payment_method_id"].choices = payment_method_choices

        # Definir currencies
        currency_choices = [
            ("EUR", "Euros"),
            ("USD", "American Dolar"),
        ]
        self.fields["currency"].choices = currency_choices

        # Definir assets
        asset_choices = [
            ("BTC", "Bitcoin"),
        ]
        self.fields["asset_code"].choices = asset_choices

    class Meta:
        model = InvestmentWatchdog
        fields = ["side", "asset_code", "currency", "payment_method_id", "amount", "rate_fee"]
        widgets = {
            "side": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Introduce la cantidad"}),
            "rate_fee": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
        }
        labels = {
            "side": "Tipo de operación",
            "amount": "Cantidad",
            "rate_fee": "Tasa de fee (%)",
        }

    def clean(self):
        cleaned_data = super().clean()
        user = self.instance.user if hasattr(self.instance, "user") else None

        if user and user.watchdogs.filter(active=True).count() >= 5:
            raise ValidationError(
                "Ya tienes el máximo de 5 watchdogs activos. Por favor desactiva uno antes de crear otro."
            )

        return cleaned_data
