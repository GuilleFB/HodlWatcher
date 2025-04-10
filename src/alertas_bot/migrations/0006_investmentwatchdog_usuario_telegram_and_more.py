# Generated by Django 4.2.20 on 2025-04-02 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("alertas_bot", "0005_alter_investmentwatchdog_payment_method_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="investmentwatchdog",
            name="usuario_telegram",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="watchdogs",
                to="alertas_bot.usuariotelegram",
            ),
        ),
        migrations.AddField(
            model_name="usuariotelegram",
            name="rate_fee",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="usuariotelegram",
            name="recibir_alertas_watchdog",
            field=models.BooleanField(default=False),
        ),
    ]
