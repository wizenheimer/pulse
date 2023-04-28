# Generated by Django 4.2 on 2023-04-28 22:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0004_guest_remove_subscriber_monitors_and_more"),
        ("monitor", "0005_remove_monitorresult_log_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubscriberAssignment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateTimeField(auto_now_add=True)),
                (
                    "monitor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="monitor.monitor",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GuestAssignment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateTimeField(auto_now_add=True)),
                (
                    "guest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="users.guest"
                    ),
                ),
                (
                    "monitor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="monitor.monitor",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="monitor",
            name="guests",
            field=models.ManyToManyField(
                related_name="monitors",
                through="monitor.GuestAssignment",
                to="users.guest",
            ),
        ),
        migrations.AddField(
            model_name="monitor",
            name="subscribers",
            field=models.ManyToManyField(
                related_name="monitors",
                through="monitor.SubscriberAssignment",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]