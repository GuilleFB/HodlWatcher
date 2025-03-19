from django.db import models


class Configuracion(models.Model):
    rate_fee = models.DecimalField("Rate Fee (%)", max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Rate Fee: {self.rate_fee}%"
