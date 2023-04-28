from django.db import models
from users.models import Team


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
