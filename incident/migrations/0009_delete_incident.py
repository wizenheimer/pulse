# Generated by Django 4.2.1 on 2023-05-10 14:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("incident", "0008_rename_delay_for_escalationlevel_delay_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Incident",
        ),
    ]
