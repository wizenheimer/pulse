# Generated by Django 4.2 on 2023-05-02 16:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("monitor", "0009_alter_credentials_managers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="monitor",
            name="tags",
            field=models.ManyToManyField(
                blank=True, null=True, related_name="monitors", to="monitor.tags"
            ),
        ),
    ]