# Generated by Django 4.2.20 on 2025-04-03 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alertas_bot", "0007_alter_configuracion_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configuracion",
            name="image",
            field=models.ImageField(default="profile.png", upload_to="profile_pics/"),
        ),
    ]
