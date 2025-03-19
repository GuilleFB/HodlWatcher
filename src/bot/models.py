from django.db import models


class UsuarioTelegram(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username or f"ID: {self.chat_id}"
