from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models

from bot.models import UsuarioTelegram


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Your Name")
    email = models.EmailField(verbose_name="Email Address")
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,17}$",
        message="Phone number must be entered in the format: '+99999999999'. Up to 15 digits allowed.",
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name="Phone Number")
    subject = models.CharField(max_length=200, verbose_name="Subject")
    message = models.TextField(verbose_name="Your Message")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


class Configuracion(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_telegram = models.ForeignKey(UsuarioTelegram, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to="profile_pics/", default="default.jpg")

    def __str__(self):
        return f"Config for {self.user.username}"
