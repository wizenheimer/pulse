# Generated by Django 4.2.1 on 2023-05-04 20:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EscalationLevel",
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
                ("level_number", models.IntegerField()),
                (
                    "time_interval",
                    models.PositiveIntegerField(
                        help_text="Time interval (in minutes) for this escalation level"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "users",
                    models.ManyToManyField(
                        help_text="Users to be notified for this escalation level",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Incident",
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
                ("title", models.CharField(default="untitled", max_length=255)),
                ("description", models.TextField()),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("P1", "P1"),
                            ("P2", "P2"),
                            ("P3", "P3"),
                            ("P4", "P4"),
                        ],
                        default="",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Open", "Open"),
                            ("Acknowledged", "Acknowledged"),
                            ("Resolved", "Resolved"),
                        ],
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="EscalationPolicy",
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
                ("name", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "escalation_levels",
                    models.ManyToManyField(to="incident.escalationlevel"),
                ),
            ],
        ),
    ]
