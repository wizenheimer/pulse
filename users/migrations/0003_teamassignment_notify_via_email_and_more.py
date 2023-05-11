# Generated by Django 4.2.1 on 2023-05-11 14:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="teamassignment",
            name="notify_via_email",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="teamassignment",
            name="notify_via_phone",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="teamassignment",
            name="notify_via_webhooks",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="teamassignment",
            name="webhook_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
