# Generated by Django 4.2.20 on 2025-03-28 14:46

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="Your Name")),
                ("email", models.EmailField(max_length=254, verbose_name="Email Address")),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=17,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Phone number must be entered in the format: '+99999999999'. Up to 15 digits allowed.",
                                regex="^\\+?1?\\d{9,17}$",
                            )
                        ],
                        verbose_name="Phone Number",
                    ),
                ),
                ("subject", models.CharField(max_length=200, verbose_name="Subject")),
                ("message", models.TextField(verbose_name="Your Message")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Contact Message",
                "verbose_name_plural": "Contact Messages",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="UsuarioTelegram",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chat_id", models.BigIntegerField(unique=True)),
                ("username", models.CharField(blank=True, max_length=255)),
                (
                    "rate_fee",
                    models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name="Rate Fee (%)"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Configuracion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(default="default.jpg", upload_to="profile_pics/")),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "user_telegram",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="alertas_bot.usuariotelegram",
                    ),
                ),
            ],
        ),
    ]
