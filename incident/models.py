from django.db import models
from users.models import Team, User


class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Incident(models.Model):
    title = models.CharField(max_length=255, default="untitled")
    description = models.TextField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
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