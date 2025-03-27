from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from .models import Configuracion, ContactMessage


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
