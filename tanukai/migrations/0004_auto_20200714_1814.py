# Generated by Django 2.2.10 on 2020-07-14 18:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tanukai", "0003_userpartition_userrating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userrating",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
