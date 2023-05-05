import arrow
from django.db import models
from users.models import Team, User
from util.calendar_util import get_on_call


# TODO: Figure out how to optimally store graphs and nodes


class OnCallCalendar(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    timezone = models.CharField(max_length=255)

    def currently_on_call(self):
        return get_on_call(
            url=self.url,
            timezone=self.timezone,
        )

    def __str__(self):
        return self.name


class Incident(models.Model):
    title = models.CharField(max_length=255, default="untitled")
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=[("P1", "P1"), ("P2", "P2"), ("P3", "P3"), ("P4", "P4")],
        default="",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("Open", "Open"),
            ("Acknowledged", "Acknowledged"),
            ("Resolved", "Resolved"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status


class EscalationLevel(models.Model):
    level_number = models.IntegerField()
    time_interval = models.PositiveIntegerField(
        help_text="Time interval (in minutes) for this escalation level"
    )
    users = models.ManyToManyField(
        User, help_text="Users to be notified for this escalation level"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Escalation Level {self.level_number}"


class EscalationPolicy(models.Model):
    name = models.CharField(max_length=255)
    escalation_levels = models.ManyToManyField(EscalationLevel)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
