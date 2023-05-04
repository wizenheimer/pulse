# Generated by Django 4.2 on 2023-05-04 10:44

from django.db import migrations, models
import django.db.models.deletion
import logger.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RequestHandler",
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
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("GET", "GET"),
                            ("POST", "POST"),
                            ("PUT", "PUT"),
                            ("PATCH", "PATCH"),
                        ],
                        max_length=5,
                    ),
                ),
                ("headers", models.JSONField(blank=True, null=True)),
                ("body", models.TextField(blank=True, null=True)),
                ("auth_username", models.CharField(max_length=255)),
                ("auth_password", models.CharField(max_length=255)),
                ("remember_cookies", models.BooleanField(default=False)),
                ("log_response", models.BooleanField(default=False)),
                ("log_screen", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Endpoint",
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
                (
                    "logger_type",
                    models.CharField(
                        choices=[
                            ("status", "Status Monitor"),
                            ("keyword", "Keyword Monitor"),
                            ("ping", "Ping Monitor"),
                            ("tcp", "TCP Monitor"),
                            ("udp", "UDP Monitor"),
                            ("smtp", "SMTP Monitor"),
                            ("pop", "POP Monitor"),
                            ("imap", "IMAP Monitor"),
                        ],
                        max_length=255,
                    ),
                ),
                ("url", models.URLField()),
                ("name", models.CharField(default="Logger", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("port", models.CharField(blank=True, max_length=255, null=True)),
                ("push_email", models.BooleanField(default=True)),
                ("push_sms", models.BooleanField(default=False)),
                ("push_call", models.BooleanField(default=False)),
                ("push_notif", models.BooleanField(default=False)),
                ("check_frequency", models.PositiveIntegerField()),
                ("timeout", models.PositiveIntegerField(default=5)),
                ("confirmation_period", models.PositiveIntegerField(default=5)),
                ("recovery_period", models.PositiveIntegerField(default=5)),
                ("escalation_period", models.PositiveIntegerField(default=5)),
                ("regex", models.CharField(max_length=255)),
                (
                    "domain_expiration",
                    models.PositiveIntegerField(
                        choices=[
                            (1, 1),
                            (2, 2),
                            (3, 3),
                            (7, 7),
                            (14, 14),
                            (30, 30),
                            (60, 60),
                        ],
                        default=1,
                    ),
                ),
                (
                    "ssl_expiration",
                    models.PositiveIntegerField(
                        choices=[
                            (1, 1),
                            (2, 2),
                            (3, 3),
                            (7, 7),
                            (14, 14),
                            (30, 30),
                            (60, 60),
                        ],
                        default=1,
                    ),
                ),
                ("follow_requests", models.BooleanField(default=True)),
                ("regions", logger.models.SeparatedValuesField()),
                ("verify_ssl", models.BooleanField(default=False)),
                ("is_public", models.BooleanField(default=False)),
                (
                    "request_handler",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="logger.requesthandler",
                    ),
                ),
            ],
        ),
    ]
