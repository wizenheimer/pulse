# Generated by Django 4.2.1 on 2023-05-16 16:45

from django.db import migrations, models
import django.db.models.deletion
import incident.validators


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("incident", "0010_escalationpolicy_max_level_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Webhook",
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
                ("url", models.URLField()),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name="escalationaction",
            name="context",
        ),
        migrations.RemoveField(
            model_name="escalationaction",
            name="entity",
        ),
        migrations.RemoveField(
            model_name="escalationlevel",
            name="days",
        ),
        migrations.RemoveField(
            model_name="escalationlevel",
            name="delay",
        ),
        migrations.RemoveField(
            model_name="escalationlevel",
            name="end_time",
        ),
        migrations.RemoveField(
            model_name="escalationlevel",
            name="repeat",
        ),
        migrations.RemoveField(
            model_name="escalationlevel",
            name="start_time",
        ),
        migrations.RemoveField(
            model_name="escalationlevel",
            name="timezone",
        ),
        migrations.RemoveField(
            model_name="escalationlevel",
            name="urgency",
        ),
        migrations.RemoveField(
            model_name="escalationpolicy",
            name="delay",
        ),
        migrations.RemoveField(
            model_name="escalationpolicy",
            name="impact",
        ),
        migrations.RemoveField(
            model_name="escalationpolicy",
            name="repeat",
        ),
        migrations.RemoveField(
            model_name="escalationpolicy",
            name="urgency",
        ),
        migrations.AddField(
            model_name="escalationaction",
            name="entity_id",
            field=models.PositiveIntegerField(default=True, null=True),
        ),
        migrations.AddField(
            model_name="escalationpolicy",
            name="source",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="media/policy",
                validators=[incident.validators.validate_file_extension],
            ),
        ),
        migrations.AlterField(
            model_name="escalationaction",
            name="entity_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="escalationpolicy",
            name="name",
            field=models.CharField(default="My Escalation Policy", max_length=255),
        ),
    ]
