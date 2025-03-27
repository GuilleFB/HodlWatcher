from django.db import models


class UsuarioTelegram(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True)
    rate_fee = models.DecimalField("Rate Fee (%)", max_digits=3, decimal_places=2, default=0)

    def __str__(self):
        return self.username or f"ID: {self.chat_id}"
